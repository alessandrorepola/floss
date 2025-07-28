"""
Test suite for fault localizer integration and end-to-end scenarios.

This module focuses on integration testing of the complete fault localization workflow,
testing the interaction between all components.
"""

import pytest
import tempfile
import shutil
import numpy as np
import random
from pathlib import Path

from src.pyfault.core.fault_localizer import FaultLocalizer
from src.pyfault.core.models import (
    CodeElement, TestOutcome, CoverageMatrix,
    SuspiciousnessScore, FaultLocalizationResult
)
from src.pyfault.formulas import OchiaiFormula, TarantulaFormula


class TestFaultLocalizerIntegration:
    """Integration tests for the complete fault localization workflow."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.source_dir = self.temp_dir / "src"
        self.test_dir = self.temp_dir / "tests"
        self.output_dir = self.temp_dir / "output"
        
        self.source_dir.mkdir()
        self.test_dir.mkdir()
        self.output_dir.mkdir()
        
        # Create sample source files
        self.create_sample_source_files()
        self.create_sample_test_files()
    
    def teardown_method(self):
        """Cleanup."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_sample_source_files(self):
        """Create sample source files with potential bugs."""
        (self.source_dir / "calculator.py").write_text("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b  # This line is correct

def multiply(a, b):
    if a == 0:
        return 0  # Correct behavior
    return a * b

def divide(a, b):
    if b == 0:
        return 0  # BUG: Should raise exception
    return a / b

def complex_function(x):
    if x < 0:
        return -1  # BUG: Should return abs(x)
    elif x == 0:
        return 0
    else:
        return x * 2
""")
    
    def create_sample_test_files(self):
        """Create test files that will expose the bugs."""
        (self.test_dir / "test_calculator.py").write_text(f"""
import sys
sys.path.insert(0, r"{self.source_dir}")
from calculator import add, subtract, multiply, divide, complex_function

def test_add_positive():
    assert add(2, 3) == 5  # PASS

def test_add_negative():
    assert add(-1, 1) == 0  # PASS

def test_subtract_basic():
    assert subtract(5, 3) == 2  # PASS

def test_multiply_basic():
    assert multiply(4, 3) == 12  # PASS

def test_multiply_zero():
    assert multiply(0, 5) == 0  # PASS

def test_divide_basic():
    assert divide(10, 2) == 5  # PASS

def test_divide_by_zero():
    try:
        result = divide(10, 0)
        assert False, "Should have raised exception"  # FAIL - exposes bug
    except ZeroDivisionError:
        pass

def test_complex_positive():
    assert complex_function(5) == 10  # PASS

def test_complex_zero():
    assert complex_function(0) == 0  # PASS

def test_complex_negative():
    assert complex_function(-3) == 3  # FAIL - exposes bug
""")
    
    def test_end_to_end_fault_localization(self):
        """Test complete end-to-end fault localization workflow."""
        localizer = FaultLocalizer(
            source_dirs=[self.source_dir],
            test_dirs=[self.test_dir],
            formulas=[OchiaiFormula(), TarantulaFormula()],
            output_dir=self.output_dir
        )
        
        result = localizer.run()
        
        # Verify result structure
        assert isinstance(result, FaultLocalizationResult)
        assert len(result.scores) > 0
        
        # Get first formula name and check its scores
        formula_names = list(result.scores.keys())
        assert len(formula_names) > 0
        first_formula = formula_names[0]
        assert len(result.scores[first_formula]) > 0  # At least one score for first formula
        
        # Check that we have coverage data
        assert result.coverage_matrix is not None
        assert len(result.coverage_matrix.test_names) > 0
        assert len(result.coverage_matrix.code_elements) > 0
        
        # Verify test outcomes
        outcomes = result.coverage_matrix.test_outcomes
        assert TestOutcome.PASSED in outcomes
        assert TestOutcome.FAILED in outcomes
        
        # Check suspiciousness scores
        for formula_name, formula_scores in result.scores.items():
            assert len(formula_scores) == len(result.coverage_matrix.code_elements)
            for score in formula_scores:
                assert isinstance(score, SuspiciousnessScore)
                assert 0 <= score.score <= 1
    
    def test_analyze_from_existing_data(self):
        """Test fault localization from pre-existing coverage matrix."""
        # Create a simple coverage matrix manually
        elements = [
            CodeElement(Path("file1.py"), 1, "line"),
            CodeElement(Path("file1.py"), 2, "line"),
            CodeElement(Path("file2.py"), 1, "line"),
        ]
        
        test_names = ["test_pass_1", "test_pass_2", "test_fail_1"]
        test_outcomes = [TestOutcome.PASSED, TestOutcome.PASSED, TestOutcome.FAILED]
        
        # Coverage matrix: tests as rows, elements as columns
        matrix = np.array([
            [1, 0, 1],  # test_pass_1 covers elements 0 and 2
            [0, 1, 1],  # test_pass_2 covers elements 1 and 2
            [1, 1, 0],  # test_fail_1 covers elements 0 and 1
        ], dtype=np.int8)
        
        coverage_matrix = CoverageMatrix(
            test_names=test_names,
            code_elements=elements,
            matrix=matrix,
            test_outcomes=test_outcomes
        )
        
        localizer = FaultLocalizer(
            source_dirs=[],
            test_dirs=[],
            formulas=[OchiaiFormula()],
            output_dir=self.output_dir
        )
        
        result = localizer.analyze_from_data(coverage_matrix)
        
        # Verify analysis results
        assert isinstance(result, FaultLocalizationResult)
        assert result.coverage_matrix is coverage_matrix
        
        # Get Ochiai scores
        ochiai_scores = result.scores[OchiaiFormula().name]
        assert len(ochiai_scores) == 3  # Three elements
        
        # Element 1 (file1.py:2) should have highest suspiciousness
        # It's covered by failed test but not by both passing tests
        element_1_score = ochiai_scores[1].score
        assert element_1_score > 0
    
    def test_multiple_formulas_consistency(self):
        """Test that multiple formulas produce consistent results."""
        # Create test data with clear fault pattern
        elements = [
            CodeElement(Path("buggy.py"), 10, "line"),  # Buggy line
            CodeElement(Path("good.py"), 5, "line"),    # Good line
        ]
        
        test_names = ["test_pass", "test_fail"]
        test_outcomes = [TestOutcome.PASSED, TestOutcome.FAILED]
        
        # Failed test covers buggy line, passed test covers good line
        matrix = np.array([
            [0, 1],  # test_pass covers only good line
            [1, 0],  # test_fail covers only buggy line
        ], dtype=np.int8)
        
        coverage_matrix = CoverageMatrix(
            test_names=test_names,
            code_elements=elements,
            matrix=matrix,
            test_outcomes=test_outcomes
        )
        
        localizer = FaultLocalizer(
            source_dirs=[],
            test_dirs=[],
            formulas=[OchiaiFormula(), TarantulaFormula()],
            output_dir=self.output_dir
        )
        
        result = localizer.analyze_from_data(coverage_matrix)
        
        # Both formulas should rank buggy line higher than good line
        ochiai_scores = result.scores[OchiaiFormula().name]
        tarantula_scores = result.scores[TarantulaFormula().name]
        
        # Buggy line (element 0) should have higher score than good line (element 1)
        assert ochiai_scores[0].score > ochiai_scores[1].score
        assert tarantula_scores[0].score > tarantula_scores[1].score
        
        # Buggy line should have maximum suspiciousness (perfect fault localization)
        assert ochiai_scores[0].score == 1.0
        assert tarantula_scores[0].score == 1.0
    
    def test_no_failing_tests_scenario(self):
        """Test behavior when all tests pass."""
        elements = [
            CodeElement(Path("file.py"), 1, "line"),
            CodeElement(Path("file.py"), 2, "line"),
        ]
        
        test_names = ["test_1", "test_2"]
        test_outcomes = [TestOutcome.PASSED, TestOutcome.PASSED]
        
        matrix = np.array([
            [1, 0],  # test_1 covers element 0
            [0, 1],  # test_2 covers element 1
        ], dtype=np.int8)
        
        coverage_matrix = CoverageMatrix(
            test_names=test_names,
            code_elements=elements,
            matrix=matrix,
            test_outcomes=test_outcomes
        )
        
        localizer = FaultLocalizer(
            source_dirs=[],
            test_dirs=[],
            formulas=[OchiaiFormula()],
            output_dir=self.output_dir
        )
        
        result = localizer.analyze_from_data(coverage_matrix)
        
        # All scores should be 0 when no tests fail
        ochiai_scores = result.scores[OchiaiFormula().name]
        for score in ochiai_scores:
            assert score.score == 0.0
    
    def test_no_passing_tests_scenario(self):
        """Test behavior when all tests fail."""
        elements = [
            CodeElement(Path("file.py"), 1, "line"),
            CodeElement(Path("file.py"), 2, "line"),
        ]
        
        test_names = ["test_1", "test_2"]
        test_outcomes = [TestOutcome.FAILED, TestOutcome.FAILED]
        
        matrix = np.array([
            [1, 1],  # test_1 covers both elements
            [1, 0],  # test_2 covers only element 0
        ], dtype=np.int8)
        
        coverage_matrix = CoverageMatrix(
            test_names=test_names,
            code_elements=elements,
            matrix=matrix,
            test_outcomes=test_outcomes
        )
        
        localizer = FaultLocalizer(
            source_dirs=[],
            test_dirs=[],
            formulas=[OchiaiFormula()],
            output_dir=self.output_dir
        )
        
        result = localizer.analyze_from_data(coverage_matrix)
        
        # Verify scores are calculated correctly
        ochiai_scores = result.scores[OchiaiFormula().name]
        
        # Element 1: covered by 1 failed, 0 passed = 1/sqrt(1*1) = 1.0
        assert ochiai_scores[0].score == 1.0
        assert ochiai_scores[1].score < 1.0
    
    def test_mixed_test_outcomes(self):
        """Test with mixed test outcomes including skipped and error."""
        elements = [CodeElement(Path("file.py"), i, "line") for i in range(1, 4)]
        
        test_names = ["test_pass", "test_fail", "test_skip", "test_error"]
        test_outcomes = [
            TestOutcome.PASSED,
            TestOutcome.FAILED,
            TestOutcome.SKIPPED,
            TestOutcome.ERROR
        ]
        
        matrix = np.array([
            [1, 0, 1],  # test_pass
            [1, 1, 0],  # test_fail
            [0, 1, 1],  # test_skip
            [1, 0, 0],  # test_error
        ], dtype=np.int8)
        
        coverage_matrix = CoverageMatrix(
            test_names=test_names,
            code_elements=elements,
            matrix=matrix,
            test_outcomes=test_outcomes
        )
        
        localizer = FaultLocalizer(
            source_dirs=[],
            test_dirs=[],
            formulas=[OchiaiFormula()],
            output_dir=self.output_dir
        )
        
        result = localizer.analyze_from_data(coverage_matrix)
        
        # Should handle mixed outcomes gracefully
        ochiai_scores = result.scores[OchiaiFormula().name]
        assert len(ochiai_scores) == 3
        for score in ochiai_scores:
            assert 0 <= score.score <= 1
    
    def test_large_scale_integration(self):
        """Test with larger number of tests and elements."""
        # Create 100 elements and 50 tests
        num_elements = 100
        num_tests = 50
        
        elements = [
            CodeElement(Path(f"file_{i//10}.py"), i % 10 + 1, "line")
            for i in range(num_elements)
        ]
        
        test_names = [f"test_{i}" for i in range(num_tests)]
        
        # Generate random but controlled test outcomes and coverage
        random.seed(42)  # For reproducible results
        
        # 80% passed, 20% failed
        outcomes = (
            [TestOutcome.PASSED] * int(num_tests * 0.8) +
            [TestOutcome.FAILED] * int(num_tests * 0.2)
        )
        random.shuffle(outcomes)
        
        # Generate coverage matrix with ~30% coverage density
        np.random.seed(42)
        matrix = np.random.choice([0, 1], size=(num_tests, num_elements), p=[0.7, 0.3])
        
        coverage_matrix = CoverageMatrix(
            test_names=test_names,
            code_elements=elements,
            matrix=matrix.astype(np.int8),
            test_outcomes=outcomes
        )
        
        localizer = FaultLocalizer(
            source_dirs=[],
            test_dirs=[],
            formulas=[OchiaiFormula(), TarantulaFormula()],
            output_dir=self.output_dir
        )
        
        result = localizer.analyze_from_data(coverage_matrix)
        
        # Verify large-scale processing
        assert len(result.scores) == 2  # Two formulas
        
        ochiai_scores = result.scores[OchiaiFormula().name]
        tarantula_scores = result.scores[TarantulaFormula().name]
        
        assert len(ochiai_scores) == num_elements
        assert len(tarantula_scores) == num_elements
        
        # All scores should be valid
        for formula_name, formula_scores in result.scores.items():
            for score in formula_scores:
                assert 0 <= score.score <= 1
                assert isinstance(score.element, CodeElement)
                assert isinstance(score.formula_name, str)
    
    # @patch('src.pyfault.test_runner.pytest_runner.PytestRunner')
    # def test_fault_localizer_error_handling(self, mock_runner_class):
    #     """Test error handling in fault localizer."""
    #     # Mock runner that raises exception
    #     mock_runner = Mock()
    #     mock_runner.run_tests.side_effect = RuntimeError("Test execution failed")
    #     mock_runner_class.return_value = mock_runner
        
    #     localizer = FaultLocalizer(
    #         source_dirs=[self.source_dir],
    #         test_dirs=[self.test_dir],
    #         formulas=[OchiaiFormula()],
    #         output_dir=self.output_dir
    #     )
        
    #     with pytest.raises(RuntimeError, match="Test execution failed"):
    #         localizer.run()
    
    def test_fault_localizer_with_branch_coverage(self):
        """Test fault localizer with branch coverage mode."""
        # This test verifies that branch coverage mode is properly integrated
        localizer = FaultLocalizer(
            source_dirs=[self.source_dir],
            test_dirs=[self.test_dir],
            formulas=[OchiaiFormula()],
            output_dir=self.output_dir,
            branch_coverage=True
        )
        
        # Create manual test data to simulate branch coverage
        elements = [
            CodeElement(Path("file.py"), 5, "branch", "if_branch_5->6"),
            CodeElement(Path("file.py"), 5, "branch", "if_branch_5->8"),
            CodeElement(Path("file.py"), 10, "line"),
        ]
        
        test_names = ["test_1", "test_2"]
        test_outcomes = [TestOutcome.PASSED, TestOutcome.FAILED]
        
        matrix = np.array([
            [1, 0, 1],  # test_1 covers first branch and line
            [0, 1, 1],  # test_2 covers second branch and line
        ], dtype=np.int8)
        
        coverage_matrix = CoverageMatrix(
            test_names=test_names,
            code_elements=elements,
            matrix=matrix,
            test_outcomes=test_outcomes
        )
        
        result = localizer.analyze_from_data(coverage_matrix)
        
        # Should handle branch elements correctly
        ochiai_scores = result.scores[OchiaiFormula().name]
        assert len(ochiai_scores) == 3
        # Branch covered by failed test should have higher suspiciousness
        branch_1_score = ochiai_scores[0].score  # Second branch
        branch_0_score = ochiai_scores[1].score  # First branch
        assert branch_1_score > branch_0_score


class TestFaultLocalizerConfiguration:
    """Test different configurations of FaultLocalizer."""
    
    def test_custom_formula_configuration(self):
        """Test fault localizer with custom formula configuration."""
        from src.pyfault.formulas import JaccardFormula, DStarFormula
        
        formulas = [JaccardFormula(), DStarFormula()]
        
        localizer = FaultLocalizer(
            source_dirs=[Path("/tmp")],
            test_dirs=[Path("/tmp")],
            formulas=formulas,
            output_dir=Path("/tmp")
        )
        
        assert len(localizer.formulas) == 2
        assert any(isinstance(f, JaccardFormula) for f in localizer.formulas)
        assert any(isinstance(f, DStarFormula) for f in localizer.formulas)
    
    def test_output_directory_creation(self):
        """Test that output directory is created if it doesn't exist."""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            output_dir = temp_dir / "new_output_dir"
            assert not output_dir.exists()
            
            localizer = FaultLocalizer(
                source_dirs=[temp_dir],
                test_dirs=[temp_dir],
                formulas=[OchiaiFormula()],
                output_dir=output_dir
            )
            
            # Output directory should be created during initialization
            assert output_dir.exists()
            assert output_dir.is_dir()
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_default_parameters(self):
        """Test fault localizer with default parameters."""
        localizer = FaultLocalizer(
            source_dirs=[Path("/tmp")],
            test_dirs=[Path("/tmp")]
        )
        
        # Should have default formulas
        assert len(localizer.formulas) > 0
        
        # Should have default output directory
        assert localizer.output_dir is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

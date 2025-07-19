"""
Test cases for core PyFault functionality.
"""

import pytest
import numpy as np
from pathlib import Path
from src.pyfault.core.models import (
    CodeElement, TestResult, TestOutcome, CoverageMatrix,
    SuspiciousnessScore, FaultLocalizationResult
)


class TestCoreModels:
    """Test cases for core data models."""
    
    def test_code_element_creation(self):
        """Test CodeElement creation and properties."""
        element = CodeElement(
            file_path=Path("test.py"),
            line_number=10,
            element_type="line",
            element_name="test_function"
        )
        
        assert element.file_path.resolve() == Path("test.py").resolve()
        assert element.line_number == 10
        assert element.element_type == "line"
        assert element.element_name == "test_function"
        
        # Test string representation
        assert "test.py:10:test_function" in f"{element.file_path}:{element.line_number}:{element.element_name}"
    
    def test_test_result_creation(self):
        """Test TestResult creation and properties."""
        elements = {
            CodeElement(Path("file1.py"), 5),
            CodeElement(Path("file2.py"), 10)
        }
        
        result = TestResult(
            test_name="test_example",
            outcome=TestOutcome.FAILED,
            execution_time=0.5,
            error_message="AssertionError",
            covered_elements=elements
        )
        
        assert result.test_name == "test_example"
        assert result.outcome == TestOutcome.FAILED
        assert result.execution_time == 0.5
        assert result.error_message == "AssertionError"
        assert len(result.covered_elements) == 2
        assert result.is_failed is True
        
        # Test passed test
        passed_result = TestResult("test_pass", TestOutcome.PASSED)
        assert passed_result.is_failed is False
    
    def test_coverage_matrix_creation(self):
        """Test CoverageMatrix creation from test results."""
        # Create test data
        elements = [
            CodeElement(Path("file1.py"), 1),
            CodeElement(Path("file1.py"), 2),
            CodeElement(Path("file2.py"), 5)
        ]
        
        test_results = [
            TestResult(
                "test1", TestOutcome.PASSED, covered_elements={elements[0], elements[1]}
            ),
            TestResult(
                "test2", TestOutcome.FAILED, covered_elements={elements[1], elements[2]}
            ),
            TestResult(
                "test3", TestOutcome.PASSED, covered_elements={elements[0], elements[2]}
            )
        ]
        
        matrix = CoverageMatrix.from_test_results(test_results)
        
        # Verify structure
        assert len(matrix.test_names) == 3
        assert len(matrix.code_elements) == 3
        assert len(matrix.test_outcomes) == 3
        assert matrix.matrix.shape == (3, 3)
        
        # Verify test names
        assert matrix.test_names == ["test1", "test2", "test3"]
        
        # Verify outcomes
        assert matrix.test_outcomes[0] == TestOutcome.PASSED
        assert matrix.test_outcomes[1] == TestOutcome.FAILED
        assert matrix.test_outcomes[2] == TestOutcome.PASSED
        
        # Verify coverage matrix content
        # test1 covers elements[0] and elements[1]
        # test2 covers elements[1] and elements[2]  
        # test3 covers elements[0] and elements[2]
        
        # Find element indices
        elem0_idx = matrix.code_elements.index(elements[0])
        elem1_idx = matrix.code_elements.index(elements[1])
        elem2_idx = matrix.code_elements.index(elements[2])
        
        # Check coverage
        assert matrix.matrix[0, elem0_idx] == 1  # test1 covers elem0
        assert matrix.matrix[0, elem1_idx] == 1  # test1 covers elem1
        assert matrix.matrix[0, elem2_idx] == 0  # test1 doesn't cover elem2
        
        assert matrix.matrix[1, elem0_idx] == 0  # test2 doesn't cover elem0
        assert matrix.matrix[1, elem1_idx] == 1  # test2 covers elem1
        assert matrix.matrix[1, elem2_idx] == 1  # test2 covers elem2
    
    def test_coverage_matrix_statistics(self):
        """Test coverage matrix statistics calculation."""
        # Create a simple coverage matrix
        test_names = ["test1", "test2", "test3"]
        elements = [
            CodeElement(Path("file.py"), 1),
            CodeElement(Path("file.py"), 2)
        ]
        
        # Matrix: 3 tests x 2 elements
        matrix_data = np.array([
            [1, 1],  # test1: covers both elements, PASSED
            [0, 1],  # test2: covers element 2 only, FAILED  
            [1, 0],  # test3: covers element 1 only, PASSED
        ])
        
        outcomes = [TestOutcome.PASSED, TestOutcome.FAILED, TestOutcome.PASSED]
        
        matrix = CoverageMatrix(test_names, elements, matrix_data, outcomes)
        
        # Test statistics for element 0 (index 0)
        n_cf, n_nf, n_cp, n_np = matrix.get_element_stats(0)
        
        # Element 0 is covered by test1 (passed) and test3 (passed)
        # Not covered by test2 (failed)
        assert n_cf == 0  # No failed tests cover element 0
        assert n_nf == 1  # 1 failed test doesn't cover element 0 (test2)
        assert n_cp == 2  # 2 passed tests cover element 0 (test1, test3)
        assert n_np == 0  # No passed tests don't cover element 0
        
        # Test statistics for element 1 (index 1)
        n_cf, n_nf, n_cp, n_np = matrix.get_element_stats(1)
        
        # Element 1 is covered by test1 (passed) and test2 (failed)
        # Not covered by test3 (passed)
        assert n_cf == 1  # 1 failed test covers element 1 (test2)
        assert n_nf == 0  # No failed tests don't cover element 1
        assert n_cp == 1  # 1 passed test covers element 1 (test1)
        assert n_np == 1  # 1 passed test doesn't cover element 1 (test3)
    
    def test_suspiciousness_score(self):
        """Test SuspiciousnessScore functionality."""
        element = CodeElement(Path("test.py"), 42)
        score = SuspiciousnessScore(
            element=element,
            score=0.85,
            formula_name="ochiai",
            rank=3
        )
        
        assert score.element == element
        assert score.score == 0.85
        assert score.formula_name == "ochiai"
        assert score.rank == 3
        
        # Test sorting (higher scores first)
        score1 = SuspiciousnessScore(element, 0.9, "test")
        score2 = SuspiciousnessScore(element, 0.7, "test")
        score3 = SuspiciousnessScore(element, 0.8, "test")
        
        scores = [score2, score1, score3]  # 0.7, 0.9, 0.8
        scores.sort(reverse=True)
        
        assert scores[0].score == 0.9  # Highest first
        assert scores[1].score == 0.8
        assert scores[2].score == 0.7  # Lowest last
    
    def test_fault_localization_result(self):
        """Test FaultLocalizationResult functionality."""
        # Create minimal test data
        elements = [CodeElement(Path("test.py"), i) for i in range(3)]
        test_results = [
            TestResult("test1", TestOutcome.PASSED, covered_elements={elements[0]}),
            TestResult("test2", TestOutcome.FAILED, covered_elements={elements[1], elements[2]})
        ]
        
        matrix = CoverageMatrix.from_test_results(test_results)
        
        # Create scores
        ochiai_scores = [
            SuspiciousnessScore(elements[0], 0.2, "ochiai", 3),
            SuspiciousnessScore(elements[1], 0.8, "ochiai", 1),
            SuspiciousnessScore(elements[2], 0.6, "ochiai", 2)
        ]
        
        tarantula_scores = [
            SuspiciousnessScore(elements[0], 0.1, "tarantula", 3),
            SuspiciousnessScore(elements[1], 0.9, "tarantula", 1),
            SuspiciousnessScore(elements[2], 0.7, "tarantula", 2)
        ]
        
        scores = {
            "ochiai": ochiai_scores,
            "tarantula": tarantula_scores
        }
        
        result = FaultLocalizationResult(
            coverage_matrix=matrix,
            scores=scores,
            execution_time=1.5,
            metadata={"test_key": "test_value"}
        )
        
        # Test basic properties
        assert result.execution_time == 1.5
        assert result.metadata["test_key"] == "test_value"
        assert len(result.scores) == 2
        
        # Test get_ranking
        ochiai_ranking = result.get_ranking("ochiai")
        assert len(ochiai_ranking) == 3
        ochiai_ranking.sort(reverse=True)
        assert ochiai_ranking[0].score == 0.8  # Highest score first
        assert ochiai_ranking[1].score == 0.6
        assert ochiai_ranking[2].score == 0.2  # Lowest score last
        
        # Test get_ranking with limit
        limited_ranking = result.get_ranking("ochiai", limit=2)
        assert len(limited_ranking) == 2
        limited_ranking.sort(reverse=True)
        assert limited_ranking[0].score == 0.8
        assert limited_ranking[1].score == 0.6
        
        # Test get_top_suspicious
        top_suspicious = result.get_top_suspicious("ochiai", threshold=0.5)
        assert len(top_suspicious) == 2  # Only elements with score >= 0.5
        assert elements[1] in top_suspicious  # score 0.8
        assert elements[2] in top_suspicious  # score 0.6
        assert elements[0] not in top_suspicious  # score 0.2
        
        # Test error on unknown formula
        with pytest.raises(ValueError):
            result.get_ranking("unknown_formula")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

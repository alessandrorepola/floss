"""
Test suite for reporter modules.

This module tests all reporter classes (CSV, JSON) with focus on
functional correctness and output format validation.
"""

import pytest
import tempfile
import shutil
import json
import pandas as pd
import numpy as np
from pathlib import Path

from src.pyfault.formulas.sbfl_formulas import JaccardFormula, OchiaiFormula, TarantulaFormula
from src.pyfault.reporters.csv_reporter import CSVReporter
from src.pyfault.reporters.json_reporter import JSONReporter
from src.pyfault.core.models import (
    CodeElement, TestOutcome, CoverageMatrix, SuspiciousnessScore,
    FaultLocalizationResult
)

@pytest.fixture
def sample_coverage_matrix() -> CoverageMatrix:
    """Provide a sample coverage matrix for testing."""
    elements = [
        CodeElement(Path("file1.py"), 1, "line"),
        CodeElement(Path("file1.py"), 2, "line"),
        CodeElement(Path("file2.py"), 5, "branch", "if_branch"),
    ]
    
    test_names = ["test_pass_1", "test_fail_1", "test_pass_2"]
    test_outcomes = [TestOutcome.PASSED, TestOutcome.FAILED, TestOutcome.PASSED]
    
    matrix = np.array([
        [1, 0, 1],
        [1, 1, 0],
        [0, 1, 1],
    ], dtype=np.int8)
    
    return CoverageMatrix(
        test_names=test_names,
        code_elements=elements,
        matrix=matrix,
        test_outcomes=test_outcomes
    )

@pytest.fixture
def sample_result(sample_coverage_matrix: CoverageMatrix) -> FaultLocalizationResult:
    """Provide a sample fault localization result."""
    ochiai_scores = [
        SuspiciousnessScore(sample_coverage_matrix.code_elements[0], 0.7, "ochiai", 2),
        SuspiciousnessScore(sample_coverage_matrix.code_elements[1], 0.9, "ochiai", 1),
        SuspiciousnessScore(sample_coverage_matrix.code_elements[2], 0.3, "ochiai", 3),
    ]
    
    tarantula_scores = [
        SuspiciousnessScore(sample_coverage_matrix.code_elements[0], 0.6, "tarantula", 2),
        SuspiciousnessScore(sample_coverage_matrix.code_elements[1], 0.8, "tarantula", 1),
        SuspiciousnessScore(sample_coverage_matrix.code_elements[2], 0.4, "tarantula", 3),
    ]
    
    scores = {
        "ochiai": ochiai_scores,
        "tarantula": tarantula_scores
    }
    
    return FaultLocalizationResult(
        coverage_matrix=sample_coverage_matrix,
        scores=scores,
        execution_time=1.5,
        metadata={"version": "1.0", "total_elements": 3}
    )


class TestCSVReporter:
    """Test cases for CSV reporter functionality."""
    
    @pytest.fixture(autouse=True)
    def setup_reporter(self, tmp_path):
        """Setup test environment."""
        self.temp_dir = tmp_path
        self.reporter = CSVReporter(output_dir=self.temp_dir)

    def test_write_coverage_matrix(self, sample_coverage_matrix: CoverageMatrix):
        """Test writing coverage matrix to CSV."""
        self.reporter.write_coverage_matrix(sample_coverage_matrix)
        
        output_file = self.temp_dir / "coverage_matrix.csv"
        assert output_file.exists()
        
        df = pd.read_csv(output_file)
        
        expected_columns = ['Element', 'File', 'Line', 'ElementType', 'ElementName'] + sample_coverage_matrix.test_names
        assert list(df.columns) == expected_columns
        
        outcome_row = df[df['Element'] == 'OUTCOME']
        assert len(outcome_row) == 1
        
        test_cols = [col for col in df.columns if col.startswith('test_')]
        outcome_values = outcome_row[test_cols].iloc[0].tolist()
        expected_outcomes = [outcome.value for outcome in sample_coverage_matrix.test_outcomes]
        assert outcome_values == expected_outcomes
        
        element_rows = df[df['Element'] != 'OUTCOME']
        assert len(element_rows) == len(sample_coverage_matrix.code_elements)
    
    def test_load_coverage_matrix(self, sample_coverage_matrix: CoverageMatrix):
        """Test loading coverage matrix from CSV."""
        output_file = self.temp_dir / "coverage_matrix.csv"
        self.reporter.write_coverage_matrix(sample_coverage_matrix, output_file=output_file)

        loaded_matrix = self.reporter.load_coverage_matrix(output_file)

        assert loaded_matrix.test_names == sample_coverage_matrix.test_names
        assert loaded_matrix.test_outcomes == sample_coverage_matrix.test_outcomes
        assert len(loaded_matrix.code_elements) == len(sample_coverage_matrix.code_elements)
        
        np.testing.assert_array_equal(loaded_matrix.matrix, sample_coverage_matrix.matrix)
        
        for orig, loaded in zip(sample_coverage_matrix.code_elements, loaded_matrix.code_elements):
            assert orig.line_number == loaded.line_number
            assert orig.element_type == loaded.element_type
            assert orig.element_name == loaded.element_name
    
    def test_write_results(self, sample_result: FaultLocalizationResult):
        """Test writing fault localization results to CSV."""
        self.reporter.generate_report(sample_result)
        
        print(f"temp dir content: {list(self.temp_dir.iterdir())}")
        ochiai_file = self.temp_dir / f"ranking_{OchiaiFormula().name}.csv"
        tarantula_file = self.temp_dir / f"ranking_{TarantulaFormula().name}.csv"

        assert ochiai_file.exists()
        assert tarantula_file.exists()
        
        df_ochiai = pd.read_csv(ochiai_file)
        expected_cols = ['Rank', 'File', 'Line', 'Element', 'Suspiciousness', 'Formula']
        assert list(df_ochiai.columns) == expected_cols

        ranks = df_ochiai['Rank'].tolist()
        ranks.sort()
        assert ranks == [1, 2, 3]
    
    def test_write_test_results(self, sample_result: FaultLocalizationResult):
        """Test writing test results to CSV."""
        self.reporter._write_test_results(sample_result)
        
        test_file = self.temp_dir / "test_results.csv"
        assert test_file.exists()
        
        df = pd.read_csv(test_file)
        expected_cols = ['Test Name', 'Outcome', 'Elements Covered', 'Coverage Percentage']
        assert list(df.columns) == expected_cols
        
        assert len(df) == len(sample_result.coverage_matrix.test_names)
        outcomes = df['Outcome'].tolist()
        expected_outcomes = [outcome.value for outcome in sample_result.coverage_matrix.test_outcomes]
        assert outcomes == expected_outcomes
    
    def test_roundtrip_coverage_matrix(self, sample_coverage_matrix: CoverageMatrix):
        """Test complete roundtrip: write -> load -> verify."""
        original_file = self.temp_dir / "coverage_matrix_1.csv"
        self.reporter.write_coverage_matrix(sample_coverage_matrix, output_file=original_file)
        
        loaded_matrix = self.reporter.load_coverage_matrix(original_file)
        
        roundtrip_file = self.temp_dir / "coverage_matrix_2.csv"
        self.reporter.write_coverage_matrix(loaded_matrix, output_file=roundtrip_file)
        
        df1 = pd.read_csv(original_file)
        df2 = pd.read_csv(roundtrip_file)
        
        pd.testing.assert_frame_equal(df1, df2)
    
    def test_invalid_coverage_file(self):
        """Test loading from invalid coverage file."""
        # Non-existent file
        with pytest.raises(RuntimeError, match="Error loading coverage matrix"):
            self.reporter.load_coverage_matrix("nonexistent.csv")
        
        # Invalid format file
        invalid_file = self.temp_dir / "invalid.csv"
        invalid_file.write_text("Invalid,CSV,Content\n1,2,3")
        
        with pytest.raises(RuntimeError, match="Error loading coverage matrix"):
            self.reporter.load_coverage_matrix(invalid_file)
    
    def test_empty_coverage_matrix(self):
        """Test handling of empty coverage matrix."""
        empty_matrix = CoverageMatrix(
            test_names=[],
            code_elements=[],
            matrix=np.empty((0, 0), dtype=np.int8),
            test_outcomes=[]
        )
        output_file = self.temp_dir / "coverage_matrix.csv"
        
        # Should not raise exception
        self.reporter.write_coverage_matrix(empty_matrix, output_file)
        
        assert output_file.exists()
        
        # Load it back
        with pytest.raises(RuntimeError):
            self.reporter.load_coverage_matrix(output_file)


class TestJSONReporter:
    """Test cases for JSON reporter functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.reporter = JSONReporter(output_dir=self.temp_dir)
        
        # Create sample data
        self.sample_result = self.create_sample_result()
    
    def teardown_method(self):
        """Cleanup."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_sample_result(self) -> FaultLocalizationResult:
        """Create a sample fault localization result."""
        elements = [
            CodeElement(Path("app.py"), 20, "line"),
            CodeElement(Path("app.py"), 25, "branch", "exception_handler"),
            CodeElement(Path("helpers.py"), 10, "line"),
        ]
        
        test_names = ["test_success", "test_error", "test_edge_case"]
        test_outcomes = [TestOutcome.PASSED, TestOutcome.FAILED, TestOutcome.ERROR]
        
        matrix = np.array([
            [1, 0, 1],  # test_success
            [1, 1, 0],  # test_error
            [0, 1, 1],  # test_edge_case
        ], dtype=np.int8)
        
        coverage_matrix = CoverageMatrix(
            test_names=test_names,
            code_elements=elements,
            matrix=matrix,
            test_outcomes=test_outcomes
        )
        
        # Create scores for multiple formulas
        ochiai_scores = [
            SuspiciousnessScore(elements[0], 0.4, "ochiai", 3),
            SuspiciousnessScore(elements[1], 0.8, "ochiai", 1),
            SuspiciousnessScore(elements[2], 0.6, "ochiai", 2),
        ]
        
        tarantula_scores = [
            SuspiciousnessScore(elements[0], 0.3, "tarantula", 3),
            SuspiciousnessScore(elements[1], 0.7, "tarantula", 1),
            SuspiciousnessScore(elements[2], 0.5, "tarantula", 2),
        ]
        
        scores = {
            "ochiai": ochiai_scores,
            "tarantula": tarantula_scores
        }
        
        return FaultLocalizationResult(
            coverage_matrix=coverage_matrix,
            scores=scores,
            execution_time=3.2,
            metadata={
                "version": "1.0", 
                "total_elements": 3,
                "formulas_used": ["ochiai", "tarantula"],
                "test_framework": "pytest"
            }
        )
    
    def test_write_results_creates_file(self):
        """Test that JSON reporter creates output file."""
        self.reporter.generate_report(self.sample_result)

        json_file = self.temp_dir / "summary.json"
        assert json_file.exists()
    
    def test_json_structure_and_content(self):
        """Test JSON structure and content validity."""
        self.reporter.generate_report(self.sample_result)

        json_file = self.temp_dir / "summary.json"
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Check top-level structure
        expected_keys = ['metadata', 'execution_time', 'formulas', 'elements', 'stats']
        assert all(key in data for key in expected_keys)
        
        # Check metadata
        assert data['metadata']['version'] == '1.0'
        assert data['metadata']['total_elements'] == 3
        
        # Check execution time
        assert data['execution_time'] == 3.2
        
        # Check formulas structure
        assert len(data['formulas']) == 2
        assert 'ochiai' in data['formulas']
        assert 'tarantula' in data['formulas']
        
        # Check ranking structure
        ochiai_ranking = data['formulas']['ochiai']
        assert len(ochiai_ranking) == 3

        # Check individual ranking item structure
        first_item = ochiai_ranking[0]
        expected_item_keys = ['rank', 'element', 'score', 'formula_name']
        assert all(key in first_item for key in expected_item_keys)
        
    def test_test_results_serialization(self):
        """Test test results serialization in JSON."""
        self.reporter.generate_report(self.sample_result)

        json_file = self.temp_dir / "summary.json"
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        stats = data['stats']
       
        # Verify counts
        assert stats['total_tests'] == 3
        assert stats['failed_tests'] == 2
            
    def test_json_valid_format(self):
        """Test that output is valid JSON."""
        self.reporter.generate_report(self.sample_result)

        json_file = self.temp_dir / "summary.json"
        
        # Should not raise exception
        with open(json_file, 'r', encoding='utf-8') as f:
            json.load(f)
    
    def test_unicode_handling(self):
        """Test handling of unicode characters in file names."""

        file1 = self.temp_dir / "测试文件.py"
        file2 = self.temp_dir / "файл.py"
        # Create result with unicode file names
        elements = [
            CodeElement(file1, 1, "line"),
            CodeElement(file2, 2, "line"),
        ]
        
        test_names = ["test_üñíçødé"]
        test_outcomes = [TestOutcome.PASSED]
        
        matrix = np.array([[1, 0]], dtype=np.int8)
        
        coverage_matrix = CoverageMatrix(
            test_names=test_names,
            code_elements=elements,
            matrix=matrix,
            test_outcomes=test_outcomes
        )
        
        scores = {
            "ochiai": [
                SuspiciousnessScore(elements[0], 0.5, "ochiai", 1),
                SuspiciousnessScore(elements[1], 0.3, "ochiai", 2),
            ]
        }
        
        unicode_result = FaultLocalizationResult(
            coverage_matrix=coverage_matrix,
            scores=scores,
            execution_time=1.0
        )
        
        # Should handle unicode without error
        self.reporter.generate_report(unicode_result)

        json_file = self.temp_dir / "summary.json"
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Verify unicode content is preserved

        assert file1.resolve() == Path(data['elements'][0]['file']).resolve()
        assert file2.resolve() == Path(data['elements'][1]['file']).resolve()

    def test_large_data_handling(self):
        """Test handling of large datasets."""
        # Create a large coverage matrix
        num_elements = 10000
        num_tests = 500
        
        elements = [
            CodeElement(Path(f"file_{i}.py"), i % 100 + 1, "line")
            for i in range(num_elements)
        ]
        
        test_names = [f"test_{i}" for i in range(num_tests)]
        test_outcomes = [TestOutcome.PASSED] * num_tests
        
        # Create sparse matrix
        matrix = np.random.choice([0, 1], size=(num_tests, num_elements), p=[0.9, 0.1])
        
        coverage_matrix = CoverageMatrix(
            test_names=test_names,
            code_elements=elements,
            matrix=matrix.astype(np.int8),
            test_outcomes=test_outcomes
        )
        
        # Create scores (simplified)
        ochiai_scores = [
            SuspiciousnessScore(elements[i], float(i) / num_elements, "ochiai", i)
            for i in range(num_elements)
        ]
        
        large_result = FaultLocalizationResult(
            coverage_matrix=coverage_matrix,
            scores={"ochiai": ochiai_scores},
            execution_time=10.0
        )
        
        # Should handle large data without error
        self.reporter.generate_report(large_result)

        json_file = self.temp_dir / "summary.json"
        assert json_file.exists()
        
        # Verify file is readable
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        assert len(data['formulas']['ochiai']) == num_elements


class TestReporterIntegration:
    """Integration tests for multiple reporters working together."""
    
    def setup_method(self):
        """Setup test environment."""
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create sample result
        self.sample_result = self.create_comprehensive_result()
    
    def teardown_method(self):
        """Cleanup."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_comprehensive_result(self) -> FaultLocalizationResult:
        """Create a comprehensive result for integration testing."""
        elements = [
            CodeElement(Path("src/calculator.py"), 15, "line"),
            CodeElement(Path("src/calculator.py"), 20, "branch", "division_check"),
            CodeElement(Path("src/utils.py"), 5, "line"),
            CodeElement(Path("tests/test_helper.py"), 10, "line"),
        ]
        
        test_names = ["test_add", "test_divide", "test_multiply", "test_edge_cases"]
        test_outcomes = [TestOutcome.PASSED, TestOutcome.FAILED, TestOutcome.PASSED, TestOutcome.ERROR]
        
        matrix = np.array([
            [1, 0, 1, 0],  # test_add
            [1, 1, 0, 1],  # test_divide
            [1, 0, 1, 0],  # test_multiply
            [0, 1, 1, 1],  # test_edge_cases
        ], dtype=np.int8)
        
        coverage_matrix = CoverageMatrix(
            test_names=test_names,
            code_elements=elements,
            matrix=matrix,
            test_outcomes=test_outcomes
        )
        
        # Create scores for multiple formulas
        formulas = ["ochiai", "tarantula", "jaccard"]
        scores = {}
        
        for formula in formulas:
            formula_scores = []
            for i, element in enumerate(elements):
                score_value = 1.0 - (i * 0.2)  # Decreasing scores
                formula_scores.append(SuspiciousnessScore(element, score_value, formula, i + 1))
            scores[formula] = formula_scores
        
        return FaultLocalizationResult(
            coverage_matrix=coverage_matrix,
            scores=scores,
            execution_time=5.5,
            metadata={
                "version": "1.0",
                "total_elements": len(elements),
                "formulas_used": formulas,
                "branch_coverage": True
            }
        )
    
    def test_all_reporters_generate_output(self):
        """Test that all reporters generate their expected outputs."""
        # Initialize all reporters
        csv_reporter = CSVReporter(output_dir=self.temp_dir / "csv")
        json_reporter = JSONReporter(output_dir=self.temp_dir / "json")

        # Generate reports
        csv_reporter.generate_report(self.sample_result)
        json_reporter.generate_report(self.sample_result)

        # Verify CSV outputs
        csv_dir = self.temp_dir / "csv"
        assert (csv_dir / f"ranking_{OchiaiFormula().name}.csv").exists()
        assert (csv_dir / f"ranking_{TarantulaFormula().name}.csv").exists()
        assert (csv_dir / f"ranking_{JaccardFormula().name}.csv").exists()
        assert (csv_dir / "test_results.csv").exists()

        # Verify JSON output
        json_dir = self.temp_dir / "json"
        assert (json_dir / "summary.json").exists()
    
    def test_consistent_data_across_reporters(self):
        """Test that all reporters produce consistent data."""
        # Generate all reports
        csv_reporter = CSVReporter(output_dir=self.temp_dir / "csv")
        json_reporter = JSONReporter(output_dir=self.temp_dir / "json")

        csv_reporter.generate_report(self.sample_result)
        json_reporter.generate_report(self.sample_result)

        # Load CSV data
        csv_ochiai = pd.read_csv(self.temp_dir / "csv" / f"ranking_{OchiaiFormula().name}.csv")

        # Load JSON data
        with open(self.temp_dir / "json" / "summary.json", 'r') as f:
            json_data = json.load(f)
        
        json_ochiai = json_data['formulas']['ochiai']
        
        # Compare rankings
        assert len(csv_ochiai) == len(json_ochiai)

        # Check that top-ranked elements match (file and line)
        csv_top_file = csv_ochiai.iloc[0]['File']
        csv_top_line = int(csv_ochiai.iloc[0]['Line'])
        json_top_element = json_ochiai[0]['element']
        json_top_file = json_top_element['file']
        json_top_line = int(json_top_element['line'])

        # Normalize file paths for comparison
        import os
        csv_file_name = os.path.basename(str(csv_top_file))
        json_file_name = os.path.basename(str(json_top_file))
        assert csv_file_name == json_file_name
        assert csv_top_line == json_top_line


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

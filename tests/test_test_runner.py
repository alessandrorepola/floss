"""
Test suite for test runner modules.

This module provides comprehensive testing for both PytestRunner and SimpleTestRunner,
focusing on integration testing with pytest and functional correctness.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
import sys
import os

from src.pyfault.test_runner.pytest_runner import (
    PytestRunner, SimpleTestRunner, PytestResultCollector
)
from src.pyfault.core.models import TestResult, TestOutcome
from src.pyfault.coverage.collector import CoverageCollector


class TestSimpleTestRunner:
    """Test cases for SimpleTestRunner (functional approach)."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.runner = SimpleTestRunner()
    
    def test_empty_runner_initialization(self):
        """Test that runner initializes with empty state."""
        assert len(self.runner.test_results) == 0
    
    def test_add_single_passing_test(self):
        """Test adding a single passing test result."""
        self.runner.add_test_result("test_example", passed=True, execution_time=0.5)
        
        results = self.runner.run_tests()
        assert len(results) == 1
        
        result = results[0]
        assert result.test_name == "test_example"
        assert result.outcome == TestOutcome.PASSED
        assert result.execution_time == 0.5
        assert result.error_message is None
        assert isinstance(result.covered_elements, set)
    
    def test_add_single_failing_test(self):
        """Test adding a single failing test result."""
        error_msg = "AssertionError: Expected 5, got 3"
        self.runner.add_test_result(
            "test_failure", 
            passed=False, 
            execution_time=1.2,
            error_message=error_msg
        )
        
        results = self.runner.run_tests()
        assert len(results) == 1
        
        result = results[0]
        assert result.test_name == "test_failure"
        assert result.outcome == TestOutcome.FAILED
        assert result.execution_time == 1.2
        assert result.error_message == error_msg
    
    def test_add_multiple_tests(self):
        """Test adding multiple test results."""
        self.runner.add_test_result("test_pass_1", passed=True)
        self.runner.add_test_result("test_fail_1", passed=False)
        self.runner.add_test_result("test_pass_2", passed=True)
        
        results = self.runner.run_tests()
        assert len(results) == 3
        
        # Check outcomes
        outcomes = [r.outcome for r in results]
        assert TestOutcome.PASSED in outcomes
        assert TestOutcome.FAILED in outcomes
        assert outcomes.count(TestOutcome.PASSED) == 2
        assert outcomes.count(TestOutcome.FAILED) == 1
    
    def test_filter_tests_by_name(self):
        """Test filtering tests by name pattern."""
        self.runner.add_test_result("test_math_add", passed=True)
        self.runner.add_test_result("test_math_subtract", passed=True)
        self.runner.add_test_result("test_string_concat", passed=False)
        
        # Filter for math tests
        math_results = self.runner.run_tests(test_filter="math")
        assert len(math_results) == 2
        for result in math_results:
            assert "math" in result.test_name
        
        # Filter for string tests
        string_results = self.runner.run_tests(test_filter="string")
        assert len(string_results) == 1
        assert "string" in string_results[0].test_name
        
        # Filter with no matches
        no_match = self.runner.run_tests(test_filter="nonexistent")
        assert len(no_match) == 0
    
    def test_clear_results(self):
        """Test clearing all test results."""
        self.runner.add_test_result("test_1", passed=True)
        self.runner.add_test_result("test_2", passed=False)
        
        assert len(self.runner.run_tests()) == 2
        
        self.runner.clear_results()
        assert len(self.runner.run_tests()) == 0
    
    def test_multiple_runs_same_results(self):
        """Test that multiple calls to run_tests return the same results."""
        self.runner.add_test_result("test_example", passed=True)
        
        results1 = self.runner.run_tests()
        results2 = self.runner.run_tests()
        
        assert len(results1) == len(results2) == 1
        assert results1[0].test_name == results2[0].test_name
        assert results1[0].outcome == results2[0].outcome


class TestPytestRunner:
    """Test cases for PytestRunner (integration approach)."""

    def setup_method(self):
        """Setup test environment with temporary test files."""
        self.original_cwd = os.getcwd()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Cambia la directory di lavoro nella directory temporanea
        os.chdir(self.temp_dir)
        # Aggiungi la CWD a sys.path per la scoperta dei moduli da parte di pytest
        sys.path.insert(0, "")

        self.test_dir = self.temp_dir / "tests"
        self.test_dir.mkdir()
        (self.test_dir / "__init__.py").write_text("")
        
        self._create_sample_test_files()

    def teardown_method(self):
        """Cleanup temporary files."""
        # Rimuovi la CWD da sys.path
        if "" in sys.path:
            sys.path.remove("")
        
        # Ripristina la directory di lavoro originale
        os.chdir(self.original_cwd)

        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)

    def _create_sample_test_files(self):
        """Create sample test files for testing."""
        # Basic passing test
        (self.test_dir / "test_basic.py").write_text("""
def test_addition():
    assert 2 + 2 == 4

def test_subtraction():
    assert 5 - 3 == 2
""")
        
        # Test with failure
        (self.test_dir / "test_with_failure.py").write_text("""
def test_pass():
    assert True

def test_fail():
    assert 1 == 2, "This should fail"
""")
        
        # Test with different patterns
        (self.test_dir / "test_math_operations.py").write_text("""
def test_math_multiply():
    assert 3 * 4 == 12

def test_math_divide():
    assert 10 / 2 == 5
""")
    
    def test_runner_initialization(self):
        """Test PytestRunner initialization."""
        runner = PytestRunner([Path("tests")])
        assert Path("tests") in runner.test_dirs
        assert len(runner.test_results) == 0
        assert runner.coverage_collector is None
        
        # With coverage collector
        mock_collector = Mock()
        runner_with_cov = PytestRunner([Path("tests")], mock_collector)
        assert runner_with_cov.coverage_collector is mock_collector
    
    def test_run_all_tests(self):
        """Test running all tests in the test directory."""
        runner = PytestRunner([Path("tests")])
        results = runner.run_tests()
        
        # Should find all test functions
        assert len(results) >= 5  # At least 5 test functions
        
        # Check test names
        test_names = [r.test_name for r in results]
        assert any("test_addition" in name for name in test_names)
        assert any("test_fail" in name for name in test_names)
        
        # Check outcomes
        outcomes = [r.outcome for r in results]
        assert TestOutcome.PASSED in outcomes
        assert TestOutcome.FAILED in outcomes
    
    
    def test_test_result_conversion(self):
        """Test conversion of pytest results to our format."""
        runner = PytestRunner([Path("tests")])
        results = runner.run_tests()
        
        for result in results:
            assert isinstance(result, TestResult)
            assert isinstance(result.test_name, str)
            assert isinstance(result.outcome, TestOutcome)
            assert isinstance(result.execution_time, (int, float))
            assert result.execution_time >= 0
            assert isinstance(result.covered_elements, set)
            
            # Error message should be present for failed tests
            if result.outcome == TestOutcome.FAILED:
                assert result.error_message is not None
    
    def test_nonexistent_test_directory(self):
        """Test behavior with non-existent test directory."""
        nonexistent_dir = Path("/this/path/does/not/exist")
        runner = PytestRunner([nonexistent_dir])
        
        with pytest.raises(RuntimeError, match="No valid test directories found"):
            runner.run_tests()
    
    def test_empty_test_directory(self):
        """Test behavior with empty test directory."""
        empty_dir = self.temp_dir / "empty_tests"
        empty_dir.mkdir()
        
        runner = PytestRunner([empty_dir])
        results = runner.run_tests()
        
        # Should run without error but return no results
        assert len(results) == 0
    
    @patch('src.pyfault.test_runner.pytest_runner.pytest.main')
    def test_pytest_execution_error(self, mock_pytest):
        """Test handling of pytest execution errors."""
        mock_pytest.side_effect = ImportError("Pytest not available")
        
        runner = PytestRunner([self.test_dir])
        
        with pytest.raises(RuntimeError, match="Pytest or a plugin could not be imported"):
            runner.run_tests()
    


class TestPytestResultCollector:
    """Test cases for PytestResultCollector plugin."""
    
    def test_collector_initialization(self):
        """Test collector initialization."""
        collector = PytestResultCollector()
        assert len(collector.test_reports) == 0
        assert collector.coverage_collector is None
        
        # With coverage collector
        mock_cov = Mock()
        collector_with_cov = PytestResultCollector(mock_cov)
        assert collector_with_cov.coverage_collector is mock_cov
    
    def test_report_collection(self):
        """Test collection of test reports."""
        collector = PytestResultCollector()
        
        # Mock test report
        mock_report = Mock()
        mock_report.when = "call"
        mock_report.outcome = "passed"
        mock_report.nodeid = "test_file.py::test_func"
        
        collector.pytest_runtest_logreport(mock_report)
        
        assert len(collector.test_reports) == 1
        assert collector.test_reports[0] is mock_report
    
    def test_coverage_integration_hooks(self):
        """Test integration hooks with coverage collector."""
        mock_coverage = Mock()
        collector = PytestResultCollector(mock_coverage)
        
        # Mock pytest item
        mock_item = Mock()
        mock_item.nodeid = "test_file.py::test_func"
        
        # Test setup hook
        collector.pytest_runtest_setup(mock_item)
        mock_coverage.start_test.assert_called_once_with("test_file.py::test_func")
        
        # Test teardown hook
        collector.pytest_runtest_teardown(mock_item, None)
        mock_coverage.end_test.assert_called_once_with("test_file.py::test_func")
    
    def test_report_filtering(self):
        """Test that only 'call' phase reports are collected."""
        collector = PytestResultCollector()
        
        # Create reports for different phases
        setup_report = Mock()
        setup_report.when = "setup"
        
        call_report = Mock()
        call_report.when = "call"
        
        teardown_report = Mock()
        teardown_report.when = "teardown"
        
        # Add all reports
        collector.pytest_runtest_logreport(setup_report)
        collector.pytest_runtest_logreport(call_report)
        collector.pytest_runtest_logreport(teardown_report)
        
        # Only call report should be collected
        assert len(collector.test_reports) == 1
        assert collector.test_reports[0] is call_report


class TestTestRunnersEdgeCases:
    """Test edge cases and error conditions for test runners."""
    
    def test_pytest_runner_with_multiple_directories(self):
        """Test PytestRunner with multiple test directories."""
        temp_dir = Path(tempfile.mkdtemp())
        try:
            # Create multiple test directories
            test_dir1 = temp_dir / "tests1"
            test_dir2 = temp_dir / "tests2"
            test_dir1.mkdir()
            test_dir2.mkdir()
            
            # Add tests to each directory
            (test_dir1 / "test_a.py").write_text("def test_a(): assert True")
            (test_dir2 / "test_b.py").write_text("def test_b(): assert True")
            
            runner = PytestRunner([test_dir1, test_dir2])
            results = runner.run_tests()
            
            # Should find tests from both directories
            test_names = [r.test_name for r in results]
            assert any("test_a" in name for name in test_names)
            assert any("test_b" in name for name in test_names)
            
        finally:
            shutil.rmtree(temp_dir)
    
    def test_simple_runner_edge_cases(self):
        """Test edge cases for SimpleTestRunner."""
        runner = SimpleTestRunner()
        
        # Test with empty test name
        runner.add_test_result("", passed=True)
        results = runner.run_tests()
        assert len(results) == 1
        assert results[0].test_name == ""
        
        # Test with very long execution time
        runner.add_test_result("slow_test", passed=True, execution_time=999.99)
        results = runner.run_tests()
        slow_test = next(r for r in results if r.test_name == "slow_test")
        assert slow_test.execution_time == 999.99
        
        # Test filter with empty string
        all_results = runner.run_tests(test_filter="")
        assert len(all_results) == 2  # Both tests should match empty filter
    
    def test_pytest_runner_test_name_extraction(self):
        """Test extraction of test names from pytest reports."""
        runner = PytestRunner([Path("/tmp")])
        
        # Mock report with nodeid
        report1 = Mock()
        report1.nodeid = "tests/test_module.py::TestClass::test_method"
        report1.outcome = "passed"
        report1.longrepr = None
        
        # Mock report without nodeid but with fspath and location
        report2 = Mock()
        report2.nodeid = None
        report2.fspath = Path("tests/test_other.py")
        report2.location = ("tests/test_other.py", 10, "test_function")
        report2.outcome = "failed"
        report2.longrepr = "Error message"
        
        # Mock report with minimal info
        report3 = Mock()
        report3.nodeid = None
        report3.fspath = Path("tests/test_minimal.py")
        report3.location = None
        report3.outcome = "passed"
        report3.longrepr = None
        
        results = runner._convert_results([report1, report2, report3])
        
        assert len(results) == 3
        for result in results:
            if result.test_name:
                result.test_name = result.test_name.replace("\\", "/")       
        
        # Check test name extraction
        assert results[0].test_name == "tests/test_module.py::TestClass::test_method"
        assert results[1].test_name == "tests/test_other.py::test_function"
        assert "test_minimal.py" in results[2].test_name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

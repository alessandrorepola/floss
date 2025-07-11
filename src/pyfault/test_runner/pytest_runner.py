"""
Pytest test runner integration.

This module provides integration with pytest for executing tests and collecting results,
similar to GZoltar's integration with JUnit/TestNG.
"""

import subprocess
import json
import tempfile
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any
import pytest
from _pytest.python import Function
from _pytest.reports import TestReport

from ..core.models import TestResult, TestOutcome


class PytestRunner:
    """
    Test runner that integrates with pytest to execute tests and collect results.
    
    This class provides similar functionality to GZoltar's JUnit integration,
    allowing automated test execution and result collection.
    
    Example:
        >>> runner = PytestRunner(['tests'])
        >>> results = runner.run_tests()
        >>> for result in results:
        ...     print(f"{result.test_name}: {result.outcome}")
    """
    
    def __init__(self, test_dirs: List[Path]):
        """
        Initialize the pytest runner.
        
        Args:
            test_dirs: Directories containing test files
        """
        self.test_dirs = test_dirs
        self.test_results: List[TestResult] = []
    
    def run_tests(self, test_filter: Optional[str] = None) -> List[TestResult]:
        """
        Run tests and collect results.
        
        Args:
            test_filter: Optional filter for test selection (pytest -k pattern)
            
        Returns:
            List of test results
        """
        self.test_results.clear()
        
        # Build pytest arguments
        args = []
        
        # Add test directories
        for test_dir in self.test_dirs:
            if test_dir.exists():
                args.append(str(test_dir))
        
        if not args:
            raise RuntimeError("No valid test directories found")
        
        # Add test filter if specified
        if test_filter:
            args.extend(['-k', test_filter])
        
        # Add options for detailed output
        args.extend([
            '-v',  # Verbose output
            '--tb=short',  # Short traceback format
            '--no-header',  # No header
            '--no-summary',  # No summary
        ])
        
        # Run tests using pytest's programmatic API
        result_plugin = PytestResultCollector()
        
        try:
            # Run pytest with our custom plugin
            exit_code = pytest.main(args + ['-p', 'no:cacheprovider'], plugins=[result_plugin])
            
            # Convert collected results to our format
            self.test_results = self._convert_results(result_plugin.test_reports)
            
        except Exception as e:
            raise RuntimeError(f"Error running tests: {e}")
        
        return self.test_results
    
    def _convert_results(self, pytest_reports: List[TestReport]) -> List[TestResult]:
        """Convert pytest reports to our TestResult format."""
        results = []
        
        for report in pytest_reports:
            # Extract test name
            test_name = self._get_test_name(report)
            
            # Convert outcome
            if report.outcome == 'passed':
                outcome = TestOutcome.PASSED
            elif report.outcome == 'failed':
                outcome = TestOutcome.FAILED
            elif report.outcome == 'skipped':
                outcome = TestOutcome.SKIPPED
            else:
                outcome = TestOutcome.ERROR
            
            # Extract error message if any
            error_message = None
            if report.longrepr:
                error_message = str(report.longrepr)
            
            # Create test result
            result = TestResult(
                test_name=test_name,
                outcome=outcome,
                execution_time=getattr(report, 'duration', 0.0),
                error_message=error_message,
                covered_elements=set()  # Will be populated by coverage collector
            )
            
            results.append(result)
        
        return results
    
    def _get_test_name(self, report: TestReport) -> str:
        """Extract a meaningful test name from pytest report."""
        # Use nodeid which includes the full path and test name
        if hasattr(report, 'nodeid'):
            return report.nodeid
        
        # Fallback to basic name
        return f"{report.fspath}::{report.head_line}" if hasattr(report, 'head_line') else str(report.fspath)


class PytestResultCollector:
    """
    Pytest plugin to collect test results.
    
    This class implements the pytest plugin interface to collect detailed
    test execution information.
    """
    
    def __init__(self):
        """Initialize the result collector."""
        self.test_reports: List[TestReport] = []
    
    def pytest_runtest_logreport(self, report: TestReport) -> None:
        """Collect test reports from pytest."""
        # Only collect call phase reports (not setup/teardown)
        if report.when == 'call':
            self.test_reports.append(report)


class SimpleTestRunner:
    """
    A simplified test runner for testing purposes.
    
    This runner allows manual creation of test results without actually
    running tests, useful for testing the SBFL algorithms.
    """
    
    def __init__(self):
        """Initialize the simple runner."""
        self.test_results: List[TestResult] = []
    
    def add_test_result(
        self,
        test_name: str,
        passed: bool,
        execution_time: float = 0.0,
        error_message: Optional[str] = None
    ) -> None:
        """
        Manually add a test result.
        
        Args:
            test_name: Name of the test
            passed: Whether the test passed
            execution_time: Test execution time
            error_message: Optional error message
        """
        outcome = TestOutcome.PASSED if passed else TestOutcome.FAILED
        
        result = TestResult(
            test_name=test_name,
            outcome=outcome,
            execution_time=execution_time,
            error_message=error_message,
            covered_elements=set()
        )
        
        self.test_results.append(result)
    
    def run_tests(self, test_filter: Optional[str] = None) -> List[TestResult]:
        """Return the manually created test results."""
        if test_filter:
            # Simple filtering by test name
            return [r for r in self.test_results if test_filter in r.test_name]
        return self.test_results.copy()
    
    def clear_results(self) -> None:
        """Clear all test results."""
        self.test_results.clear()

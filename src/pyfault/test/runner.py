"""Test runner for PyFault using pytest with coverage context."""

import subprocess
import json
import uuid
import xml.etree.ElementTree as ET
import tempfile
import os
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from .config import TestConfig


@dataclass
class TestResult:
    """Result of test execution."""
    
    coverage_data: Dict[str, Any]
    failed_tests: List[str]
    passed_tests: List[str]
    skipped_tests: List[str]


class TestRunner:
    """Executes tests with pytest and coverage collection."""
    
    def __init__(self, config: TestConfig):
        self.config = config
    
    def run_tests(self, test_filter: Optional[str] = None) -> TestResult:
        """Run tests and collect coverage with context information."""
        
        # Create temporary files for results
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as xml_file:
            xml_path = xml_file.name
        
        try:
            # Write coverage configuration with unique name
            coveragerc_file = f".coveragerc_{uuid.uuid4().hex}"
            self.config.write_coveragerc(coveragerc_file)
            
            # Build pytest command
            cmd = self._build_pytest_command(xml_path, test_filter)
            
            # Execute pytest
            result = subprocess.run(cmd, capture_output=True, text=True, cwd=".")
            
            if result.returncode != 0 and result.returncode != 1:
                # Return code 1 is normal when tests fail, anything else is an error
                raise RuntimeError(f"pytest execution failed: {result.stderr}")
            
            # Parse results
            coverage_data = self._load_coverage_data()
            test_outcomes = self._parse_junit_xml(xml_path)
            
            # Merge test outcomes into coverage data
            coverage_data = self._merge_test_outcomes(coverage_data, test_outcomes)

            return TestResult(
                coverage_data=coverage_data,
                failed_tests=test_outcomes["failed"],
                passed_tests=test_outcomes["passed"],
                skipped_tests=test_outcomes["skipped"]
            )
            
        finally:
            # Cleanup temporary files
            if os.path.exists(xml_path):
                os.unlink(xml_path)
            if os.path.exists(coveragerc_file):
                os.unlink(coveragerc_file)

    def _build_pytest_command(self, xml_path: str, test_filter: Optional[str] = None) -> List[str]:
        """Build the pytest command with all required options."""
        cmd = ["pytest"]
        
        # Add test directory if specified
        if self.config.test_dir:
            cmd.append(self.config.test_dir)
        
        # Required coverage options
        cmd.extend([
            f"--cov={self.config.source_dir}",
            "--cov-context=test",
            f"--cov-report=json:{self.config.output_file}",
            "--cov-branch",
            "-v"
        ])
        
        # Add ignore patterns
        for pattern in (self.config.ignore_patterns or []):
            cmd.extend(["--ignore-glob", pattern])
        
        # Add junit XML output
        cmd.extend(["--junitxml", xml_path])
        
        # Add test filter if provided
        if test_filter:
            cmd.extend(["-k", test_filter])
        
        return cmd
    
    def _load_coverage_data(self) -> Dict[str, Any]:
        """Load coverage data from JSON file."""
        try:
            with open(self.config.output_file, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            raise RuntimeError(f"Coverage file {self.config.output_file} not found")
        except json.JSONDecodeError:
            raise RuntimeError(f"Invalid JSON in coverage file {self.config.output_file}")
    
    def _parse_junit_xml(self, xml_path: str) -> Dict[str, List[str]]:
        """Parse JUnit XML to extract test outcomes."""
        outcomes = {
            "failed": [],
            "passed": [],
            "skipped": []
        }
        
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()
            
            for testcase in root.iter('testcase'):
                classname = testcase.get('classname', '')
                name = testcase.get('name', '')
                
                # Convert to pytest context format (e.g., "tests/test_file.py::test_function")
                test_name = self._convert_to_pytest_format(classname, name)
                
                # Check test outcome
                if testcase.find('failure') is not None:
                    outcomes["failed"].append(test_name)
                elif testcase.find('skipped') is not None:
                    outcomes["skipped"].append(test_name)
                elif testcase.find('error') is not None:
                    outcomes["error"].append(test_name)
                else:
                    outcomes["passed"].append(test_name)
            
            return outcomes
            
        except ET.ParseError:
            raise RuntimeError(f"Failed to parse JUnit XML file {xml_path}")
    
    def _convert_to_pytest_format(self, classname: str, name: str) -> str:
        """Convert JUnit format to pytest context format."""
        # JUnit classname is like "tests.test_file" or "tests.test_file.ClassName"
        # pytest context format is like "tests/test_file.py::test_function"
        
        # Handle ruff and other non-test cases
        if name in ["ruff", "format"] or "ruff" in classname:
            return f"{classname}::{name}"
        
        # Convert dots to slashes and add .py extension
        parts = classname.split('.')
        if len(parts) >= 2:
            # Assume first part is directory, second is file
            file_path = '/'.join(parts[:-1]) + '/' + parts[-1] + '.py'
            return f"{file_path}::{name}"
        else:
            # Fallback format
            return f"{classname}::{name}"
    
    def _merge_test_outcomes(self, coverage_data: Dict[str, Any], test_outcomes: Dict[str, List[str]]) -> Dict[str, Any]:
        """Merge test outcome information into coverage data."""
        # Add tests section to coverage data
        coverage_data["tests"] = {
            "failed": test_outcomes["failed"],
            "passed": test_outcomes["passed"],
            "skipped": test_outcomes["skipped"]
        }
        
        return coverage_data

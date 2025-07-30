"""
Test suite for the new CLI implementation.

This module tests the simplified CLI with only the 'test' command.
"""

import pytest
import tempfile
import shutil
import json
import os
from pathlib import Path
from unittest.mock import Mock, patch
from click.testing import CliRunner

from src.pyfault.cli.main import main
from src.pyfault.test.runner import TestResult


class TestCLITestCommand:
    """Test cases for the 'pyfault test' command."""
    
    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test directory structure
        self.source_dir = self.temp_dir / "src"
        self.test_dir = self.temp_dir / "tests"
        self.source_dir.mkdir()
        self.test_dir.mkdir()
        
        # Create sample files
        self.create_sample_files()
    
    def teardown_method(self):
        """Cleanup."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_sample_files(self):
        """Create sample source and test files."""
        # Sample source file
        (self.source_dir / "calculator.py").write_text("""
def add(a, b):
    return a + b

def subtract(a, b):
    return a - b
""")
        
        # Sample test file
        (self.test_dir / "test_calculator.py").write_text("""
import sys
sys.path.insert(0, 'src')
from calculator import add, subtract

def test_add():
    assert add(2, 3) == 5

def test_subtract():
    assert subtract(5, 3) == 2
""")
        
        # Sample config file
        (self.temp_dir / "pyfault.conf").write_text("""[test]
source_dir = src
output_file = test_coverage.json
""")
    
    def test_help_command(self):
        """Test that help command works."""
        result = self.runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "PyFault: Spectrum-Based Fault Localization" in result.output
    
    def test_test_command_help(self):
        """Test that test command help works."""
        result = self.runner.invoke(main, ['test', '--help'])
        assert result.exit_code == 0
        assert "Run tests with coverage collection" in result.output
        assert "--source-dir" in result.output
        assert "--output" in result.output
    
    @patch('src.pyfault.test.runner.TestRunner.run_tests')
    def test_test_command_basic(self, mock_run_tests):
        """Test basic test command execution."""
        # Mock the test runner
        mock_result = TestResult(
            coverage_data={"meta": {}, "files": {}, "tests": {"failed": [], "passed": ["test1"], "skipped": []}},
            failed_tests=[],
            passed_tests=["test1"],
            skipped_tests=[]
        )
        mock_run_tests.return_value = mock_result
        
        with self.runner.isolated_filesystem():
            # Create minimal structure
            os.makedirs("src")
            result = self.runner.invoke(main, ['test', '--source-dir', 'src'])
            
            assert result.exit_code == 0
            assert "Running tests with coverage collection" in result.output
            assert "Test execution completed" in result.output
            assert "Total tests: 1" in result.output
            assert "Passed: 1" in result.output
    
    @patch('src.pyfault.test.runner.TestRunner.run_tests')
    def test_test_command_with_failures(self, mock_run_tests):
        """Test test command with failed tests."""
        # Mock the test runner with failures
        mock_result = TestResult(
            coverage_data={"meta": {}, "files": {}, "tests": {"failed": ["test_fail"], "passed": ["test_pass"], "skipped": []}},
            failed_tests=["tests/test_calc.py::test_fail"],
            passed_tests=["tests/test_calc.py::test_pass"],
            skipped_tests=[]
        )
        mock_run_tests.return_value = mock_result
        
        with self.runner.isolated_filesystem():
            os.makedirs("src")
            result = self.runner.invoke(main, ['test', '--source-dir', 'src'])
            
            assert result.exit_code == 0
            assert "Failed: 1" in result.output
            assert "Failed tests:" in result.output
            assert "tests/test_calc.py::test_fail" in result.output
    
    def test_test_command_with_custom_output(self):
        """Test test command with custom output file."""
        with patch('src.pyfault.test.runner.TestRunner.run_tests') as mock_run_tests:
            mock_result = TestResult(
                coverage_data={"tests": {"failed": [], "passed": [], "skipped": []}},
                failed_tests=[],
                passed_tests=[],
                skipped_tests=[]
            )
            mock_run_tests.return_value = mock_result
            
            with self.runner.isolated_filesystem():
                os.makedirs("src")
                result = self.runner.invoke(main, ['test', '--source-dir', 'src', '--output', 'custom.json'])
                
                assert result.exit_code == 0
                assert "Output file: custom.json" in result.output
    
    def test_test_command_with_test_filter(self):
        """Test test command with test filter."""
        with patch('src.pyfault.test.runner.TestRunner.run_tests') as mock_run_tests:
            mock_result = TestResult(
                coverage_data={"tests": {"failed": [], "passed": [], "skipped": []}},
                failed_tests=[],
                passed_tests=[],
                skipped_tests=[]
            )
            mock_run_tests.return_value = mock_result
            
            with self.runner.isolated_filesystem():
                os.makedirs("src")
                result = self.runner.invoke(main, ['test', '--source-dir', 'src', '--test-filter', 'test_add'])
                
                assert result.exit_code == 0
                # Verify that test filter was passed to runner
                mock_run_tests.assert_called_once_with('test_add')
    
    def test_test_command_with_ignore_patterns(self):
        """Test test command with additional ignore patterns."""
        with patch('src.pyfault.test.runner.TestRunner.run_tests') as mock_run_tests:
            mock_result = TestResult(
                coverage_data={"tests": {"failed": [], "passed": [], "skipped": []}},
                failed_tests=[],
                passed_tests=[],
                skipped_tests=[]
            )
            mock_run_tests.return_value = mock_result
            
            with self.runner.isolated_filesystem():
                os.makedirs("src")
                result = self.runner.invoke(main, [
                    'test', 
                    '--source-dir', 'src',
                    '--ignore', '*/migrations/*',
                    '--ignore', '*/temp/*'
                ])
                
                assert result.exit_code == 0
    
    def test_test_command_with_omit_patterns(self):
        """Test test command with additional omit patterns."""
        with patch('src.pyfault.test.runner.TestRunner.run_tests') as mock_run_tests:
            mock_result = TestResult(
                coverage_data={"tests": {"failed": [], "passed": [], "skipped": []}},
                failed_tests=[],
                passed_tests=[],
                skipped_tests=[]
            )
            mock_run_tests.return_value = mock_result
            
            with self.runner.isolated_filesystem():
                os.makedirs("src")
                result = self.runner.invoke(main, [
                    'test', 
                    '--source-dir', 'src',
                    '--omit', '*/test_utils.py',
                    '--omit', '*/conftest.py'
                ])
                
                assert result.exit_code == 0
    
    @patch('src.pyfault.test.runner.TestRunner.run_tests')
    def test_test_command_error_handling(self, mock_run_tests):
        """Test test command error handling."""
        # Mock an exception
        mock_run_tests.side_effect = RuntimeError("Test execution failed")
        
        with self.runner.isolated_filesystem():
            os.makedirs("src")
            result = self.runner.invoke(main, ['test', '--source-dir', 'src'])
            
            assert result.exit_code == 1
            assert "Error:" in result.output
            assert "Test execution failed" in result.output
    
    @patch('src.pyfault.test.runner.TestRunner.run_tests')
    def test_test_command_verbose_error(self, mock_run_tests):
        """Test test command error handling with verbose mode."""
        # Mock an exception
        mock_run_tests.side_effect = RuntimeError("Test execution failed")
        
        with self.runner.isolated_filesystem():
            os.makedirs("src")
            result = self.runner.invoke(main, ['--verbose', 'test', '--source-dir', 'src'])
            
            assert result.exit_code == 1
            assert "Error:" in result.output
    
    def test_configuration_file_loading(self):
        """Test that configuration file is loaded correctly."""
        with patch('src.pyfault.test.runner.TestRunner.run_tests') as mock_run_tests:
            mock_result = TestResult(
                coverage_data={"tests": {"failed": [], "passed": [], "skipped": []}},
                failed_tests=[],
                passed_tests=[],
                skipped_tests=[]
            )
            mock_run_tests.return_value = mock_result
            
            with self.runner.isolated_filesystem():
                os.makedirs("app")  # Different from default "src"
                
                # Create config file
                with open("custom.conf", "w") as f:
                    f.write("""[test]
source_dir = app
output_file = app_coverage.json
""")
                
                result = self.runner.invoke(main, ['test', '--config', 'custom.conf'])
                
                assert result.exit_code == 0
                assert "Source dir: app" in result.output
                assert "Output file: app_coverage.json" in result.output
    
    def test_command_line_override_config_file(self):
        """Test that command line arguments override config file."""
        with patch('src.pyfault.test.runner.TestRunner.run_tests') as mock_run_tests:
            mock_result = TestResult(
                coverage_data={"tests": {"failed": [], "passed": [], "skipped": []}},
                failed_tests=[],
                passed_tests=[],
                skipped_tests=[]
            )
            mock_run_tests.return_value = mock_result
            
            with self.runner.isolated_filesystem():
                os.makedirs("src")
                os.makedirs("custom_src")
                
                # Create config file with different values
                with open("test.conf", "w") as f:
                    f.write("""[test]
source_dir = src
output_file = config_coverage.json
""")
                
                # Override with command line
                result = self.runner.invoke(main, [
                    'test', 
                    '--config', 'test.conf',
                    '--source-dir', 'custom_src',
                    '--output', 'cli_coverage.json'
                ])
                
                assert result.exit_code == 0
                assert "Source dir: custom_src" in result.output
                assert "Output file: cli_coverage.json" in result.output


class TestCLIMainGroup:
    """Test cases for the main CLI group."""
    
    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
    
    def test_main_group_help(self):
        """Test main group help output."""
        result = self.runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "PyFault: Spectrum-Based Fault Localization" in result.output
        assert "Commands:" in result.output
        assert "test" in result.output
    
    def test_verbose_flag(self):
        """Test verbose flag functionality."""
        result = self.runner.invoke(main, ['--verbose', '--help'])
        assert result.exit_code == 0
    
    def test_unknown_command(self):
        """Test handling of unknown commands."""
        result = self.runner.invoke(main, ['unknown-command'])
        assert result.exit_code != 0
        assert "No such command" in result.output
    
    def test_no_command(self):
        """Test behavior when no command is provided."""
        result = self.runner.invoke(main, [])
        # Click returns exit code 2 when no command is provided and shows help
        assert result.exit_code == 2 or "Commands:" in result.output


class TestCLIIntegration:
    """Integration tests for CLI functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
    
    @patch('src.pyfault.test.runner.TestRunner.run_tests')
    @patch('builtins.open', create=True)
    def test_full_workflow_mock(self, mock_open, mock_run_tests):
        """Test full workflow with mocked file operations."""
        # Mock the test result
        mock_coverage_data = {
            "meta": {"version": "7.9.2"},
            "files": {"src/calculator.py": {"executed_lines": [1, 2, 3]}},
            "totals": {"covered_lines": 3},
            "tests": {
                "failed": ["tests/test_calc.py::test_fail"],
                "passed": ["tests/test_calc.py::test_pass1", "tests/test_calc.py::test_pass2"],
                "skipped": []
            }
        }
        
        mock_result = TestResult(
            coverage_data=mock_coverage_data,
            failed_tests=["tests/test_calc.py::test_fail"],
            passed_tests=["tests/test_calc.py::test_pass1", "tests/test_calc.py::test_pass2"],
            skipped_tests=[]
        )
        mock_run_tests.return_value = mock_result
        
        # Mock file writing
        mock_file = Mock()
        mock_open.return_value.__enter__.return_value = mock_file
        
        with self.runner.isolated_filesystem():
            os.makedirs("src")
            result = self.runner.invoke(main, ['test', '--source-dir', 'src'])
            
            assert result.exit_code == 0
            assert "Test execution completed" in result.output
            assert "Total tests: 3" in result.output
            assert "Passed: 2" in result.output
            assert "Failed: 1" in result.output
            
            # Verify that JSON was written
            mock_open.assert_called_with('coverage.json', 'w')
    
    def test_config_file_precedence(self):
        """Test configuration file precedence and merging."""
        with patch('src.pyfault.test.runner.TestRunner.run_tests') as mock_run_tests:
            mock_result = TestResult(
                coverage_data={"tests": {"failed": [], "passed": [], "skipped": []}},
                failed_tests=[],
                passed_tests=[],
                skipped_tests=[]
            )
            mock_run_tests.return_value = mock_result
            
            with self.runner.isolated_filesystem():
                os.makedirs("config_src")
                os.makedirs("cli_src")
                
                # Create config file
                with open("pyfault.conf", "w") as f:
                    f.write("""[test]
source_dir = config_src
test_dir = config_tests
output_file = config.json
ignore = */__init__.py, */config_ignore/*
omit = */__init__.py, */config_omit/*
""")
                
                # Test with partial CLI override
                result = self.runner.invoke(main, [
                    'test',
                    '--source-dir', 'cli_src',  # Override source dir
                    '--ignore', '*/cli_ignore/*',  # Add to ignore patterns
                    '--omit', '*/cli_omit/*'  # Add to omit patterns
                ])
                
                assert result.exit_code == 0
                assert "Source dir: cli_src" in result.output  # CLI override
                assert "Output file: config.json" in result.output  # From config file

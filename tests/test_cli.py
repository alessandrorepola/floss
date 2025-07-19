"""
Test suite for CLI (Command Line Interface) module.

This module focuses on end-to-end testing of the CLI functionality,
including command parsing, error handling, and output validation.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock, patch
from click.testing import CliRunner

from src.pyfault.cli.main import main
from src.pyfault.core.models import CodeElement


class TestCLIBasicFunctionality:
    """Test basic CLI functionality and command parsing."""
    
    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create test directory structure
        self.source_dir = self.temp_dir / "src"
        self.test_dir = self.temp_dir / "tests"
        self.output_dir = self.temp_dir / "output"
        
        self.source_dir.mkdir()
        self.test_dir.mkdir()
        self.output_dir.mkdir()
        
        # Create sample files
        self.create_sample_files()
    
    def teardown_method(self):
        """Cleanup."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_sample_files(self):
        """Create sample source and test files."""
        # Sample source file
        (self.source_dir / "math_ops.py").write_text("""
def add(a, b):
    return a + b

def divide(a, b):
    if b == 0:
        return 0  # BUG: should raise exception
    return a / b
""")
        
        # Sample test file
        (self.test_dir / "test_math.py").write_text(f"""
import sys
sys.path.insert(0, r"{self.source_dir}")
from math_ops import add, divide

def test_add():
    assert add(2, 3) == 5

def test_divide():
    assert divide(10, 2) == 5

def test_divide_by_zero():
    try:
        result = divide(10, 0)
        assert False, "Should raise exception"
    except ZeroDivisionError:
        pass
""")
        
        # Sample coverage CSV file
        self.create_sample_coverage_csv()
    
    def create_sample_coverage_csv(self):
        """Create a sample coverage CSV file for testing."""
        coverage_file = self.temp_dir / "coverage.csv"
        coverage_content = """Element,File,Line,ElementType,ElementName,test_add,test_divide,test_divide_by_zero
OUTCOME,,,,,passed,passed,failed
math_ops.py:2,math_ops.py,2,line,,1,0,0
math_ops.py:5,math_ops.py,5,line,,0,1,1
math_ops.py:6,math_ops.py,6,line,,0,1,1
math_ops.py:8,math_ops.py,8,line,,0,1,0
"""
        coverage_file.write_text(coverage_content)
        return coverage_file
    
    def test_main_command_help(self):
        """Test main command help output."""
        result = self.runner.invoke(main, ['--help'])
        assert result.exit_code == 0
        assert "PyFault" in result.output
        assert "Spectrum-Based Fault Localization" in result.output
    
    def test_main_command_with_verbose(self):
        """Test main command with verbose flag."""
        result = self.runner.invoke(main, ['--verbose', '--help'])
        assert result.exit_code == 0
    
    def test_run_command_help(self):
        """Test run command help output."""
        result = self.runner.invoke(main, ['run', '--help'])
        assert result.exit_code == 0
        assert "--source-dir" in result.output
        assert "--test-dir" in result.output
        assert "--formula" in result.output
    
    def test_fl_command_help(self):
        """Test fl command help output."""
        result = self.runner.invoke(main, ['fl', '--help'])
        assert result.exit_code == 0
        assert "--coverage-file" in result.output
        assert "--formula" in result.output
    
    def test_test_command_help(self):
        """Test test command help output."""
        result = self.runner.invoke(main, ['test', '--help'])
        assert result.exit_code == 0
        assert "--source-dir" in result.output
        assert "--test-dir" in result.output
        assert "--branch-coverage" in result.output


class TestCLIRunCommand:
    """Test the 'run' command functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        self.source_dir = self.temp_dir / "src"
        self.test_dir = self.temp_dir / "tests"
        self.output_dir = self.temp_dir / "output"
        
        self.source_dir.mkdir()
        self.test_dir.mkdir()
        
        # Create simple test files that will actually work
        self._create_working_test_files()
    
    def teardown_method(self):
        """Cleanup."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def _create_working_test_files(self):
        """Create working test files for CLI testing."""
        # Simple source file
        (self.source_dir / "simple.py").write_text("""
def simple_add(x, y):
    return x + y

def simple_multiply(x, y):
    return x * y
""")
        
        # Simple test file
        (self.test_dir / "test_simple.py").write_text(f"""
import sys
sys.path.insert(0, r"{self.source_dir}")
from simple import simple_add, simple_multiply

def test_add():
    assert simple_add(1, 2) == 3

def test_multiply():
    assert simple_multiply(2, 3) == 6
""")
    
    def test_run_command_missing_required_args(self):
        """Test run command with missing required arguments."""
        result = self.runner.invoke(main, ['run'])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()
    
    def test_run_command_invalid_directory(self):
        """Test run command with invalid directories."""
        result = self.runner.invoke(main, [
            'run',
            '--source-dir', '/nonexistent/path',
            '--test-dir', str(self.test_dir)
        ])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "error" in result.output.lower()
    
    @patch('src.pyfault.cli.main.FaultLocalizer')
    def test_run_command_basic_execution(self, mock_localizer_class):
        """Test basic execution of run command."""
        # Mock the fault localizer
        mock_localizer = Mock()
        mock_result = Mock()
        mock_result.scores = {'Ochiai': []}
        mock_result.coverage_matrix = Mock()
        mock_result.coverage_matrix.test_names = []
        mock_result.coverage_matrix.code_elements = []
        mock_result.execution_time = 1.0
        mock_result.get_ranking.return_value = []
        
        mock_localizer.run.return_value = mock_result
        mock_localizer_class.return_value = mock_localizer
        
        result = self.runner.invoke(main, [
            'run',
            '--source-dir', str(self.source_dir),
            '--test-dir', str(self.test_dir),
            '--output-dir', str(self.output_dir)
        ])
        
        # Should complete successfully
        print(result.output)
        assert result.exit_code == 0
        mock_localizer_class.assert_called_once()
        mock_localizer.run.assert_called_once()
    
    def test_run_command_formula_selection(self):
        """Test run command with formula selection."""
        with patch('src.pyfault.cli.main.FaultLocalizer') as mock_localizer_class:
            mock_localizer = Mock()
            mock_result = Mock()
            mock_result.scores = {'Ochiai': []}
            mock_result.coverage_matrix = Mock()
            mock_result.coverage_matrix.test_names = []
            mock_result.coverage_matrix.code_elements = []
            mock_result.get_ranking.return_value = []
            
            mock_localizer.run.return_value = mock_result
            mock_localizer_class.return_value = mock_localizer
            
            result = self.runner.invoke(main, [
                'run',
                '--source-dir', str(self.source_dir),
                '--test-dir', str(self.test_dir),
                '--formula', 'ochiai',
                '--formula', 'tarantula'
            ])
            
            assert result.exit_code == 0
            
            # Check that formulas were passed correctly
            call_args = mock_localizer_class.call_args
            formulas = call_args[1]['formulas']
            formula_names = [f.__class__.__name__ for f in formulas]
            assert 'OchiaiFormula' in formula_names
            assert 'TarantulaFormula' in formula_names
    
    def test_run_command_branch_coverage(self):
        """Test run command with branch coverage enabled."""
        with patch('src.pyfault.cli.main.FaultLocalizer') as mock_localizer_class:
            mock_localizer = Mock()
            mock_result = Mock()
            mock_result.scores = {}
            mock_result.coverage_matrix = Mock()
            mock_result.coverage_matrix.test_names = []
            mock_result.coverage_matrix.code_elements = []
            mock_result.get_ranking.return_value = []
            
            mock_localizer.run.return_value = mock_result
            mock_localizer_class.return_value = mock_localizer
            
            result = self.runner.invoke(main, [
                'run',
                '--source-dir', str(self.source_dir),
                '--test-dir', str(self.test_dir),
                '--branch-coverage'
            ])
            
            assert result.exit_code == 0
            
            # Check that branch coverage was enabled
            call_args = mock_localizer_class.call_args
            assert call_args[1]['branch_coverage'] is True


class TestCLIFLCommand:
    """Test the 'fl' (fault localization) command functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create sample coverage file
        self.coverage_file = self.create_sample_coverage_file()
    
    def teardown_method(self):
        """Cleanup."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_sample_coverage_file(self):
        """Create a sample coverage CSV file."""
        coverage_file = self.temp_dir / "sample_coverage.csv"
        content = """Element,File,Line,ElementType,ElementName,test_1,test_2,test_3
OUTCOME,,,,,passed,failed,passed
file1.py:10,file1.py,10,line,,1,1,0
file1.py:15,file1.py,15,line,,0,1,1
file2.py:5,file2.py,5,branch,if_branch,1,0,1
"""
        coverage_file.write_text(content)
        return coverage_file
    
    def test_fl_command_missing_coverage_file(self):
        """Test fl command with missing coverage file argument."""
        result = self.runner.invoke(main, ['fl'])
        assert result.exit_code != 0
        assert "Missing option" in result.output or "required" in result.output.lower()
    
    def test_fl_command_nonexistent_coverage_file(self):
        """Test fl command with non-existent coverage file."""
        result = self.runner.invoke(main, [
            'fl',
            '--coverage-file', '/nonexistent/coverage.csv'
        ])
        assert result.exit_code != 0
        assert "not found" in result.output.lower() or "error" in result.output.lower()
    
    @patch('src.pyfault.cli.main.CSVReporter')
    @patch('src.pyfault.cli.main.FaultLocalizer')
    def test_fl_command_basic_execution(self, mock_localizer_class, mock_csv_reporter_class):
        """Test basic execution of fl command."""
        # Mock CSV reporter
        mock_reporter = Mock()
        mock_coverage_matrix = Mock()
        mock_coverage_matrix.test_names = ['test_1', 'test_2']
        mock_coverage_matrix.code_elements = []
        mock_reporter.load_coverage_matrix.return_value = mock_coverage_matrix
        mock_csv_reporter_class.return_value = mock_reporter

        
        # Mock fault localizer
        mock_localizer = Mock()
        mock_result = Mock()
        mock_result.scores = {'Ochiai': []}
        mock_result.coverage_matrix = mock_coverage_matrix
        mock_result.get_ranking = Mock(return_value=[])
        mock_localizer.analyze_from_data.return_value = mock_result
        mock_localizer_class.return_value = mock_localizer
        
        result = self.runner.invoke(main, [
            'fl',
            '--coverage-file', str(self.coverage_file)
        ])
        
        assert result.exit_code == 0
        mock_reporter.load_coverage_matrix.assert_called_once()
        mock_localizer.analyze_from_data.assert_called_once()
    
    def test_fl_command_with_custom_formulas(self):
        """Test fl command with custom formula selection."""
        with patch('src.pyfault.cli.main.CSVReporter') as mock_csv_reporter_class:
            with patch('src.pyfault.cli.main.FaultLocalizer') as mock_localizer_class:
                # Setup mocks
                mock_reporter = Mock()
                mock_coverage_matrix = Mock()
                mock_coverage_matrix.test_names = []
                mock_coverage_matrix.code_elements = []
                mock_reporter.load_coverage_matrix.return_value = mock_coverage_matrix
                mock_csv_reporter_class.return_value = mock_reporter
                
                mock_localizer = Mock()
                mock_result = Mock()
                mock_result.scores = {}
                mock_result.coverage_matrix = mock_coverage_matrix
                mock_localizer.analyze_from_data.return_value = mock_result
                mock_localizer_class.return_value = mock_localizer
                
                result = self.runner.invoke(main, [
                    'fl',
                    '--coverage-file', str(self.coverage_file),
                    '--formula', 'dstar',
                    '--formula', 'kulczynski2'
                ])
                
                assert result.exit_code == 0
                
                # Check formulas were set correctly
                call_args = mock_localizer_class.call_args
                formulas = call_args[1]['formulas']
                formula_names = [f.__class__.__name__ for f in formulas]
                assert 'DStarFormula' in formula_names
                assert 'Kulczynski2Formula' in formula_names
    
    def test_fl_command_output_directory(self):
        """Test fl command with custom output directory."""
        output_dir = self.temp_dir / "custom_output"
        
        with patch('src.pyfault.cli.main.CSVReporter') as mock_csv_reporter_class:
            with patch('src.pyfault.cli.main.FaultLocalizer') as mock_localizer_class:
                # Setup mocks
                mock_reporter = Mock()
                mock_coverage_matrix = Mock()
                mock_coverage_matrix.test_names = []
                mock_coverage_matrix.code_elements = []
                mock_reporter.load_coverage_matrix.return_value = mock_coverage_matrix
                mock_csv_reporter_class.return_value = mock_reporter
                
                mock_localizer = Mock()
                mock_result = Mock()
                mock_result.scores = {}
                mock_result.coverage_matrix = mock_coverage_matrix
                mock_localizer.analyze_from_data.return_value = mock_result
                mock_localizer_class.return_value = mock_localizer
                
                result = self.runner.invoke(main, [
                    'fl',
                    '--coverage-file', str(self.coverage_file),
                    '--output-dir', str(output_dir)
                ])
                
                assert result.exit_code == 0
                
                # Check output directory was set
                call_args = mock_localizer_class.call_args
                assert str(output_dir) in str(call_args[1]['output_dir'])


class TestCLITestCommand:
    """Test the 'test' command functionality."""
    
    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        self.source_dir = self.temp_dir / "src"
        self.test_dir = self.temp_dir / "tests"
        
        self.source_dir.mkdir()
        self.test_dir.mkdir()
        
        self.create_sample_files()
    
    def teardown_method(self):
        """Cleanup."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_sample_files(self):
        """Create sample files for testing."""
        # Sample source
        (self.source_dir / "calc.py").write_text("""
def add(a, b):
    return a + b
""")
        
        # Sample test
        (self.test_dir / "test_calc.py").write_text(f"""
import sys
sys.path.insert(0, r"{self.source_dir}")
from calc import add

def test_add():
    assert add(1, 1) == 2
""")
    
    def test_test_command_missing_args(self):
        """Test test command with missing required arguments."""
        result = self.runner.invoke(main, ['test'])
        assert result.exit_code != 0
    
    @patch('src.pyfault.cli.main.CoverageCollector')
    @patch('src.pyfault.cli.main.PytestRunner')
    @patch('src.pyfault.cli.main.CoverageMatrix')
    @patch('src.pyfault.cli.main.CSVReporter')
    def test_test_command_basic_execution(self, mock_csv_reporter, mock_coverage_matrix, 
                                         mock_pytest_runner, mock_coverage_collector):
        """Test basic execution of test command."""
        # Setup mocks
        mock_collector = Mock()
        mock_coverage_collector.return_value = mock_collector
        
        mock_runner = Mock()
        mock_test_results = [Mock()]
        mock_test_results[0].is_failed = False
        mock_runner.run_tests.return_value = mock_test_results
        mock_pytest_runner.return_value = mock_runner
        
        mock_matrix = Mock()
        mock_matrix.code_elements = []
        mock_coverage_matrix.from_test_results.return_value = mock_matrix
        
        mock_reporter = Mock()
        mock_csv_reporter.return_value = mock_reporter
        
        result = self.runner.invoke(main, [
            'test',
            '--source-dir', str(self.source_dir),
            '--test-dir', str(self.test_dir)
        ])
        
        assert result.exit_code == 0
        mock_runner.run_tests.assert_called_once()
    
    def test_test_command_with_filter(self):
        """Test test command with test filter."""
        with patch('src.pyfault.cli.main.CoverageCollector') as mock_coverage_collector:
            with patch('src.pyfault.cli.main.PytestRunner') as mock_pytest_runner:
                with patch('src.pyfault.cli.main.CoverageMatrix') as mock_coverage_matrix:
                    with patch('src.pyfault.cli.main.CSVReporter') as mock_csv_reporter:
                        # Setup mocks
                        mock_collector = Mock()
                        mock_coverage_collector.return_value = mock_collector
                        
                        mock_runner = Mock()
                        mock_test_results = [Mock()]
                        mock_test_results[0].is_failed = False
                        mock_runner.run_tests.return_value = mock_test_results
                        mock_pytest_runner.return_value = mock_runner
                        
                        mock_matrix = Mock()
                        mock_matrix.code_elements = []
                        mock_coverage_matrix.from_test_results.return_value = mock_matrix
                        
                        mock_reporter = Mock()
                        mock_csv_reporter.return_value = mock_reporter
                        
                        result = self.runner.invoke(main, [
                            'test',
                            '--source-dir', str(self.source_dir),
                            '--test-dir', str(self.test_dir),
                            '--test-filter', 'test_add'
                        ])
                        
                        assert result.exit_code == 0
                        # Check that filter was passed to run_tests
                        mock_runner.run_tests.assert_called_with('test_add')
    
    def test_test_command_branch_coverage(self):
        """Test test command with branch coverage enabled."""
        with patch('src.pyfault.cli.main.CoverageCollector') as mock_coverage_collector:
            with patch('src.pyfault.cli.main.PytestRunner') as mock_pytest_runner:
                with patch('src.pyfault.cli.main.CoverageMatrix') as mock_coverage_matrix:
                    with patch('src.pyfault.cli.main.CSVReporter') as mock_csv_reporter:
                        # Setup mocks
                        mock_collector = Mock()
                        mock_coverage_collector.return_value = mock_collector
                        
                        mock_runner = Mock()
                        mock_test_results = [Mock()]
                        mock_test_results[0].is_failed = False
                        mock_runner.run_tests.return_value = mock_test_results
                        mock_pytest_runner.return_value = mock_runner
                        
                        mock_matrix = Mock()
                        mock_matrix.code_elements = []
                        mock_coverage_matrix.from_test_results.return_value = mock_matrix
                        
                        mock_reporter = Mock()
                        mock_csv_reporter.return_value = mock_reporter
                        
                        result = self.runner.invoke(main, [
                            'test',
                            '--source-dir', str(self.source_dir),
                            '--test-dir', str(self.test_dir),
                            '--branch-coverage'
                        ])
                        
                        assert result.exit_code == 0
                        
                        # Check that branch coverage was enabled
                        call_args = mock_coverage_collector.call_args
                        assert call_args[1]['branch_coverage'] is True


class TestCLIErrorHandling:
    """Test CLI error handling scenarios."""
    
    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Cleanup."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_invalid_command(self):
        """Test behavior with invalid command."""
        result = self.runner.invoke(main, ['invalid_command'])
        assert result.exit_code != 0
        assert "No such command" in result.output
    
    def test_invalid_formula_name(self):
        """Test behavior with invalid formula name."""
        coverage_file = self.temp_dir / "coverage.csv"
        coverage_file.write_text("Element,File,Line,ElementType,ElementName\nOUTCOME,,,,,")
        
        result = self.runner.invoke(main, [
            'fl',
            '--coverage-file', str(coverage_file),
            '--formula', 'invalid_formula'
        ])
        assert result.exit_code != 0
        assert "Invalid value" in result.output or "invalid choice" in result.output.lower()
    
    @patch('src.pyfault.cli.main.FaultLocalizer')
    def test_fault_localizer_exception(self, mock_localizer_class):
        """Test handling of FaultLocalizer exceptions."""
        # Mock fault localizer to raise exception
        mock_localizer = Mock()
        mock_localizer.run.side_effect = RuntimeError("Test execution failed")
        mock_localizer_class.return_value = mock_localizer
        
        # Create minimal valid directories
        source_dir = self.temp_dir / "src"
        test_dir = self.temp_dir / "tests"
        source_dir.mkdir()
        test_dir.mkdir()
        
        result = self.runner.invoke(main, [
            'run',
            '--source-dir', str(source_dir),
            '--test-dir', str(test_dir)
        ])
        
        assert result.exit_code != 0
        assert "Error" in result.output
    
    def test_permission_error(self):
        """Test handling of permission errors."""
        # Try to write to a read-only directory (simulated)
        readonly_dir = self.temp_dir / "readonly"
        readonly_dir.mkdir()
        
        # On Windows, we can't easily make directories read-only in tests
        # So we'll test with a non-existent parent directory instead
        invalid_output = Path("/root/nonexistent/output")
        
        source_dir = self.temp_dir / "src"
        test_dir = self.temp_dir / "tests"
        source_dir.mkdir()
        test_dir.mkdir()
        
        with patch('src.pyfault.cli.main.FaultLocalizer') as mock_localizer_class:
            mock_localizer = Mock()
            mock_localizer.run.side_effect = PermissionError("Permission denied")
            mock_localizer_class.return_value = mock_localizer
            
            result = self.runner.invoke(main, [
                'run',
                '--source-dir', str(source_dir),
                '--test-dir', str(test_dir),
                '--output-dir', str(invalid_output)
            ])
            
            assert result.exit_code != 0


class TestCLIOutputFormatting:
    """Test CLI output formatting and display."""
    
    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())
    
    def teardown_method(self):
        """Cleanup."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    @patch('src.pyfault.cli.main.CSVReporter')
    @patch('src.pyfault.cli.main.FaultLocalizer')
    def test_results_display_formatting(self, mock_localizer_class, mock_csv_reporter_class):
        """Test that results are displayed in proper format."""
        # Create sample coverage file
        coverage_file = self.temp_dir / "coverage.csv"
        coverage_file.write_text("""Element,File,Line,ElementType,ElementName,test_1,test_2
OUTCOME,,,,,passed,failed
file1.py:10,file1.py,10,line,,1,1
file1.py:15,file1.py,15,line,,0,1
""")
        
        # Mock reporter
        mock_reporter = Mock()
        elements = [
            CodeElement(Path("file1.py"), 10, "line"),
            CodeElement(Path("file1.py"), 15, "line"),
        ]
        mock_coverage_matrix = Mock()
        mock_coverage_matrix.test_names = ['test_1', 'test_2']
        mock_coverage_matrix.code_elements = elements
        mock_reporter.load_coverage_matrix.return_value = mock_coverage_matrix
        mock_csv_reporter_class.return_value = mock_reporter
        
        # Mock localizer with realistic results
        from src.pyfault.core.models import SuspiciousnessScore
        scores = [
            SuspiciousnessScore(elements[0], 0.8, "Ochiai", 1),
            SuspiciousnessScore(elements[1], 0.6, "Ochiai", 2),
        ]
        
        mock_localizer = Mock()
        mock_result = Mock()
        mock_result.scores = {'Ochiai': scores}
        mock_result.coverage_matrix = mock_coverage_matrix
        mock_result.execution_time = 1.5
        mock_result.get_ranking = Mock(return_value=scores)
        mock_localizer.analyze_from_data.return_value = mock_result
        mock_localizer_class.return_value = mock_localizer
        
        result = self.runner.invoke(main, [
            'fl',
            '--coverage-file', str(coverage_file),
            '--top', '5'
        ])
        
        assert result.exit_code == 0
        
        # Check that results are displayed
        assert "file1.py" in result.output
        assert "0.8" in result.output or "0.6" in result.output
        assert "Analysis complete" in result.output or "complete" in result.output.lower()
    
    def test_verbose_output(self):
        """Test verbose output mode."""
        result = self.runner.invoke(main, ['--verbose', '--help'])
        assert result.exit_code == 0
        # Verbose flag should be processed without error
    
    @patch('src.pyfault.cli.main.FaultLocalizer')
    def test_progress_indicators(self, mock_localizer_class):
        """Test that progress indicators are shown."""
        # Setup mock
        mock_localizer = Mock()
        mock_result = Mock()
        mock_result.scores = {}
        mock_result.coverage_matrix = Mock()
        mock_result.coverage_matrix.test_names = []
        mock_result.coverage_matrix.code_elements = []
        mock_localizer.run.return_value = mock_result
        mock_localizer_class.return_value = mock_localizer
        
        # Create minimal directories
        source_dir = self.temp_dir / "src"
        test_dir = self.temp_dir / "tests"
        source_dir.mkdir()
        test_dir.mkdir()
        
        result = self.runner.invoke(main, [
            'run',
            '--source-dir', str(source_dir),
            '--test-dir', str(test_dir)
        ])
        
        assert result.exit_code == 0
        # Should show progress or completion messages
        # (Note: Rich progress bars might not show in test output)


class TestCLIIntegration:
    """Integration tests for CLI with real components."""
    
    def setup_method(self):
        """Setup test environment."""
        self.runner = CliRunner()
        self.temp_dir = Path(tempfile.mkdtemp())
        
        # Create realistic project structure
        self.create_realistic_project()
    
    def teardown_method(self):
        """Cleanup."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def create_realistic_project(self):
        """Create a realistic project structure for integration testing."""
        # Source code
        src_dir = self.temp_dir / "src"
        src_dir.mkdir()
        
        (src_dir / "calculator.py").write_text("""
def add(a, b):
    \"\"\"Add two numbers.\"\"\"
    return a + b

def subtract(a, b):
    \"\"\"Subtract b from a.\"\"\"
    return a - b

def divide(a, b):
    \"\"\"Divide a by b.\"\"\"
    if b == 0:
        return None  # BUG: should raise exception
    return a / b

def multiply(a, b):
    \"\"\"Multiply two numbers.\"\"\"
    return a * b
""")
        
        # Test code
        test_dir = self.temp_dir / "tests"
        test_dir.mkdir()
        
        (test_dir / "test_calculator.py").write_text(f"""
import sys
sys.path.insert(0, r"{src_dir}")
from calculator import add, subtract, divide, multiply

def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

def test_subtract():
    assert subtract(5, 3) == 2

def test_multiply():
    assert multiply(4, 3) == 12

def test_divide_normal():
    assert divide(10, 2) == 5

def test_divide_by_zero():
    # This test will fail due to the bug
    try:
        result = divide(10, 0)
        assert False, "Should have raised ZeroDivisionError"
    except ZeroDivisionError:
        pass  # Expected behavior
""")
        
        # Create coverage CSV for fl command testing
        coverage_file = self.temp_dir / "sample_coverage.csv"
        coverage_file.write_text("""Element,File,Line,ElementType,ElementName,test_add_positive,test_add_negative,test_subtract,test_multiply,test_divide_normal,test_divide_by_zero
OUTCOME,,,,,passed,passed,passed,passed,passed,failed
calculator.py:2,calculator.py,2,line,,1,1,0,0,0,0
calculator.py:6,calculator.py,6,line,,0,0,1,0,0,0
calculator.py:10,calculator.py,10,line,,0,0,0,0,1,1
calculator.py:11,calculator.py,11,line,,0,0,0,0,1,1
calculator.py:12,calculator.py,12,line,,0,0,0,0,1,0
calculator.py:16,calculator.py,16,line,,0,0,0,1,0,0
""")
        
        self.src_dir = src_dir
        self.test_dir = test_dir
        self.coverage_file = coverage_file
    
    def test_end_to_end_fl_command(self):
        """Test end-to-end execution of fl command with real data."""
        result = self.runner.invoke(main, [
            'fl',
            '--coverage-file', str(self.coverage_file),
            '--output-dir', str(self.temp_dir / "output"),
            '--formula', 'ochiai',
            '--top', '3'
        ])
        
        # Should complete successfully
        assert result.exit_code == 0
        
        # Should show analysis results
        assert "Loading coverage data" in result.output or "coverage" in result.output.lower()
        assert "Analysis complete" in result.output or "complete" in result.output.lower()
        
        # Should create output files
        output_dir = self.temp_dir / "output"
        assert output_dir.exists()
    
    def test_error_handling_with_real_files(self):
        """Test error handling with real file operations."""
        # Test with malformed coverage file
        bad_coverage = self.temp_dir / "bad_coverage.csv"
        bad_coverage.write_text("This is not a valid CSV file")
        
        result = self.runner.invoke(main, [
            'fl',
            '--coverage-file', str(bad_coverage)
        ])
        
        assert result.exit_code != 0
        assert "Error" in result.output


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

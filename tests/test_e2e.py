"""
End-to-end integration tests for PyFault workflow.
"""

import json
import os
import tempfile
import shutil
from click.testing import CliRunner

from pyfault.cli.main import main


class TestE2EWorkflow:
    """End-to-end tests for complete PyFault workflow."""
    
    def test_complete_workflow(self):
        """Test complete test -> FL workflow."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create a mini project structure
            os.makedirs('src')
            os.makedirs('tests')
            
            # Create source file with a bug
            with open('src/calculator.py', 'w') as f:
                f.write('''
def add(a, b):
    return a + b

def subtract(a, b):
    if a < 0:  # Buggy condition
        return 0  # Wrong!
    return a - b

def divide(a, b):
    if b == 0:
        raise ValueError("Division by zero")
    return a / b
''')
            
            # Create test file
            with open('tests/test_calculator.py', 'w') as f:
                f.write('''
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from calculator import add, subtract, divide

def test_add_positive():
    assert add(2, 3) == 5

def test_add_negative():
    assert add(-1, 1) == 0

def test_subtract_positive():
    assert subtract(5, 3) == 2

def test_subtract_negative():
    # This test will fail due to the bug
    assert subtract(-1, 1) == -2

def test_divide_normal():
    assert divide(6, 2) == 3

def test_divide_by_zero():
    try:
        divide(1, 0)
        assert False, "Should raise exception"
    except ValueError:
        pass
''')
            
            # Create config file
            with open('pyfault.conf', 'w') as f:
                f.write('''
[test]
source_dir = src

[fl]
formulas = ochiai, tarantula, dstar2
''')
            
            # Step 1: Run tests with coverage (simulate - we'll create the coverage manually)
            # In real scenario this would be: result = runner.invoke(main, ['test'])
            
            # Create realistic coverage data manually (simulating test command output)
            coverage_data = {
                "meta": {
                    "format": 3,
                    "version": "7.9.2",
                    "timestamp": "2025-01-01T12:00:00.000000",
                    "branch_coverage": True,
                    "show_contexts": True
                },
                "files": {
                    "src\\calculator.py": {
                        "executed_lines": [2, 3, 5, 6, 7, 8, 10, 11, 12, 13],
                        "contexts": {
                            "2": ["tests/test_calculator.py::test_add_positive|run", 
                                  "tests/test_calculator.py::test_add_negative|run"],
                            "3": ["tests/test_calculator.py::test_add_positive|run", 
                                  "tests/test_calculator.py::test_add_negative|run"],
                            "5": ["tests/test_calculator.py::test_subtract_positive|run",
                                  "tests/test_calculator.py::test_subtract_negative|run"],
                            "6": ["tests/test_calculator.py::test_subtract_negative|run"],  # Bug line!
                            "7": ["tests/test_calculator.py::test_subtract_negative|run"],  # Bug line!
                            "8": ["tests/test_calculator.py::test_subtract_positive|run"],
                            "10": ["tests/test_calculator.py::test_divide_normal|run",
                                   "tests/test_calculator.py::test_divide_by_zero|run"],
                            "11": ["tests/test_calculator.py::test_divide_by_zero|run"],
                            "12": ["tests/test_calculator.py::test_divide_by_zero|run"],
                            "13": ["tests/test_calculator.py::test_divide_normal|run"]
                        },
                        "summary": {
                            "covered_lines": 10,
                            "num_statements": 10,
                            "percent_covered": 100.0
                        }
                    }
                },
                "tests": {
                    "passed": [
                        "tests/test_calculator.py::test_add_positive",
                        "tests/test_calculator.py::test_add_negative", 
                        "tests/test_calculator.py::test_subtract_positive",
                        "tests/test_calculator.py::test_divide_normal",
                        "tests/test_calculator.py::test_divide_by_zero"
                    ],
                    "failed": [
                        "tests/test_calculator.py::test_subtract_negative"
                    ],
                    "skipped": []
                },
                "totals": {
                    "covered_lines": 10,
                    "num_statements": 10,
                    "percent_covered": 100.0
                }
            }
            
            with open('coverage.json', 'w') as f:
                json.dump(coverage_data, f, indent=2)
            
            # Step 2: Run fault localization
            result = runner.invoke(main, ['fl'])
            
            assert result.exit_code == 0
            assert "Fault localization completed" in result.output
            assert os.path.exists('report.json')
            
            # Step 3: Analyze results
            with open('report.json', 'r') as f:
                report = json.load(f)
            
            # Verify structure
            assert 'fl_metadata' in report
            assert 'formulas_used' in report['fl_metadata']
            assert set(report['fl_metadata']['formulas_used']) == {'ochiai', 'tarantula', 'dstar2'}
            
            # Get suspiciousness scores
            file_data = report['files']['src\\calculator.py']
            assert 'suspiciousness' in file_data
            susp = file_data['suspiciousness']
            
            # Lines 6,7 should have highest suspiciousness (only covered by failing test)
            assert '6' in susp
            assert '7' in susp
            
            # These lines should have higher suspiciousness than others
            line6_ochiai = susp['6']['ochiai']
            line7_ochiai = susp['7']['ochiai']
            
            # Compare with lines covered by both passing and failing tests
            if '5' in susp:  # Line covered by both pass/fail
                line5_ochiai = susp['5']['ochiai']
                assert line6_ochiai > line5_ochiai
                assert line7_ochiai > line5_ochiai
            
            # Lines only covered by passing tests should have 0 suspiciousness
            if '13' in susp:  # Only covered by passing test
                assert susp['13']['ochiai'] == 0.0
                assert susp['13']['tarantula'] == 0.0
    
    def test_workflow_with_custom_parameters(self):
        """Test workflow with custom parameters and configuration."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create minimal coverage data
            coverage_data = {
                "tests": {
                    "passed": ["test_pass"],
                    "failed": ["test_fail"]
                },
                "files": {
                    "buggy.py": {
                        "contexts": {
                            "1": ["test_pass|run", "test_fail|run"],
                            "2": ["test_fail|run"]
                        }
                    }
                }
            }
            
            with open('my_coverage.json', 'w') as f:
                json.dump(coverage_data, f)
            
            # Test FL with custom parameters
            result = runner.invoke(main, [
                'fl',
                '--input', 'my_coverage.json',
                '--output', 'my_report.json', 
                '--formulas', 'ochiai',
                '--formulas', 'jaccard'
            ])
            
            assert result.exit_code == 0
            assert 'Input file: my_coverage.json' in result.output
            assert 'Output file: my_report.json' in result.output
            assert 'Formulas: ochiai, jaccard' in result.output
            
            # Verify output
            assert os.path.exists('my_report.json')
            with open('my_report.json', 'r') as f:
                report = json.load(f)
            
            assert set(report['fl_metadata']['formulas_used']) == {'ochiai', 'jaccard'}
            
            # Line 2 should have higher suspiciousness (only failing test covers it)
            susp = report['files']['buggy.py']['suspiciousness']
            assert susp['2']['ochiai'] > susp['1']['ochiai']
            assert susp['2']['jaccard'] > susp['1']['jaccard']
    
    def test_error_handling_workflow(self):
        """Test error handling in workflow scenarios."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Test 1: Missing input file
            result = runner.invoke(main, ['fl'])
            assert result.exit_code == 1
            assert 'Error:' in result.output
            
            # Test 2: Invalid JSON
            with open('coverage.json', 'w') as f:
                f.write('invalid json content')
            
            result = runner.invoke(main, ['fl'])
            assert result.exit_code == 1
            assert 'Error:' in result.output
            
            # Test 3: Empty but valid JSON
            with open('coverage.json', 'w') as f:
                json.dump({}, f)
            
            result = runner.invoke(main, ['fl'])
            assert result.exit_code == 0  # Should handle gracefully
            
            with open('report.json', 'r') as f:
                report = json.load(f)
            assert report['fl_metadata']['total_lines_analyzed'] == 0
    
    def test_workflow_preserves_all_original_data(self):
        """Test that FL workflow preserves all original coverage data."""
        runner = CliRunner()
        
        with runner.isolated_filesystem():
            # Create complex coverage data with many fields
            original_data = {
                "meta": {
                    "format": 3,
                    "version": "7.9.2",
                    "timestamp": "2025-01-01T12:00:00.000000",
                    "branch_coverage": True,
                    "show_contexts": True
                },
                "files": {
                    "complex_file.py": {
                        "executed_lines": [1, 2, 3],
                        "missing_lines": [4, 5],
                        "excluded_lines": [6],
                        "contexts": {
                            "1": ["test1|run"],
                            "2": ["test2|run"],
                            "3": ["test1|run", "test2|run"]
                        },
                        "summary": {
                            "covered_lines": 3,
                            "num_statements": 5,
                            "percent_covered": 60.0,
                            "missing_lines": 2,
                            "excluded_lines": 1
                        },
                        "executed_branches": [[1, 2], [2, 3]],
                        "missing_branches": [[3, 4]],
                        "functions": {
                            "func1": {
                                "executed_lines": [1, 2],
                                "summary": {"covered_lines": 2}
                            }
                        },
                        "classes": {
                            "Class1": {
                                "executed_lines": [3],
                                "summary": {"covered_lines": 1}
                            }
                        }
                    }
                },
                "tests": {
                    "passed": ["test1"],
                    "failed": ["test2"],
                    "skipped": ["test3"]
                },
                "totals": {
                    "covered_lines": 3,
                    "num_statements": 5,
                    "percent_covered": 60.0,
                    "missing_lines": 2
                }
            }
            
            with open('coverage.json', 'w') as f:
                json.dump(original_data, f, indent=2)
            
            # Run FL
            result = runner.invoke(main, ['fl'])
            assert result.exit_code == 0
            
            # Load result and verify all original data is preserved
            with open('report.json', 'r') as f:
                report = json.load(f)
            
            # Check meta preservation
            assert report['meta'] == original_data['meta']
            
            # Check totals preservation  
            assert report['totals'] == original_data['totals']
            
            # Check test outcomes preservation
            assert report['tests'] == original_data['tests']
            
            # Check file-level data preservation
            file_data = report['files']['complex_file.py']
            orig_file_data = original_data['files']['complex_file.py']
            
            assert file_data['executed_lines'] == orig_file_data['executed_lines']
            assert file_data['missing_lines'] == orig_file_data['missing_lines']
            assert file_data['excluded_lines'] == orig_file_data['excluded_lines']
            assert file_data['summary'] == orig_file_data['summary']
            assert file_data['executed_branches'] == orig_file_data['executed_branches']
            assert file_data['missing_branches'] == orig_file_data['missing_branches']
            assert file_data['functions'] == orig_file_data['functions']
            assert file_data['classes'] == orig_file_data['classes']
            
            # Check that FL data was added
            assert 'suspiciousness' in file_data
            assert 'fl_metadata' in report
            
            # Verify suspiciousness data
            susp = file_data['suspiciousness']
            assert '1' in susp  # Line covered by passing test only
            assert '2' in susp  # Line covered by failing test only  
            assert '3' in susp  # Line covered by both
            
            # Line 2 should have highest suspiciousness (only failing test)
            assert susp['2']['ochiai'] > susp['1']['ochiai']
            assert susp['2']['ochiai'] > susp['3']['ochiai']
            
            # Line 1 should have 0 suspiciousness (only passing test)
            assert susp['1']['ochiai'] == 0.0

"""
CSV reporter for fault localization results.

This module generates CSV reports containing suspiciousness rankings,
similar to GZoltar's CSV output functionality.
"""

import csv
from pathlib import Path
from typing import List, Dict, Any

from ..core.models import FaultLocalizationResult, SuspiciousnessScore


class CSVReporter:
    """
    Generates CSV reports for fault localization results.
    
    Similar to GZoltar's CSV export functionality, this reporter creates
    structured CSV files containing suspiciousness rankings and statistics.
    
    Example:
        >>> reporter = CSVReporter(Path('output'))
        >>> reporter.generate_report(results)
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize the CSV reporter.
        
        Args:
            output_dir: Directory where CSV files will be written
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def generate_report(self, result: FaultLocalizationResult) -> None:
        """
        Generate CSV reports for the fault localization results.
        
        Args:
            result: Fault localization results to report
        """
        # Generate individual formula rankings
        for formula_name, scores in result.scores.items():
            self._write_formula_ranking(formula_name, scores)
        
        # Generate summary report
        self._write_summary_report(result)
        
        # Generate coverage matrix
        self._write_coverage_matrix(result)
        
        # Generate test results
        self._write_test_results(result)
    
    def _write_formula_ranking(self, formula_name: str, scores: List[SuspiciousnessScore]) -> None:
        """Write ranking for a specific formula."""
        filename = self.output_dir / f"ranking_{formula_name}.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'Rank',
                'File',
                'Line',
                'Element',
                'Suspiciousness',
                'Formula'
            ])
            
            # Write rankings
            for score in scores:
                writer.writerow([
                    score.rank,
                    str(score.element.file_path),
                    score.element.line_number,
                    score.element.element_name or '',
                    f"{score.score:.6f}",
                    score.formula_name
                ])
    
    def _write_summary_report(self, result: FaultLocalizationResult) -> None:
        """Write summary report with statistics."""
        filename = self.output_dir / "summary.csv"
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write metadata
            writer.writerow(['Metric', 'Value'])
            writer.writerow(['Total Tests', result.metadata.get('total_tests', 0)])
            writer.writerow(['Failed Tests', result.metadata.get('failed_tests', 0)])
            writer.writerow(['Total Elements', result.metadata.get('total_elements', 0)])
            writer.writerow(['Execution Time (s)', f"{result.execution_time:.3f}"])
            formulas_used = result.metadata.get('formulas_used', [])
            if isinstance(formulas_used, list):
                formulas_str = ', '.join(str(f) for f in formulas_used)
            else:
                formulas_str = str(formulas_used)
            writer.writerow(['Formulas Used', formulas_str])
            
            # Write empty row
            writer.writerow([])
            
            # Write top elements for each formula
            writer.writerow(['Formula', 'Top Element', 'File', 'Line', 'Score'])
            
            for formula_name in result.scores:
                if result.scores[formula_name]:
                    top_score = result.scores[formula_name][0]
                    writer.writerow([
                        formula_name,
                        str(top_score.element),
                        str(top_score.element.file_path),
                        top_score.element.line_number,
                        f"{top_score.score:.6f}"
                    ])
    
    def _write_coverage_matrix(self, result: FaultLocalizationResult) -> None:
        """Write the coverage matrix to CSV."""
        filename = self.output_dir / "coverage_matrix.csv"
        matrix = result.coverage_matrix
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header with test names
            header = ['Element', 'File', 'Line'] + matrix.test_names
            writer.writerow(header)
            
            # Write coverage data
            for idx, element in enumerate(matrix.code_elements):
                row = [
                    str(element),
                    str(element.file_path),
                    element.line_number
                ]
                
                # Add coverage values for each test
                for test_idx in range(len(matrix.test_names)):
                    coverage_value = matrix.matrix[test_idx, idx]
                    row.append(coverage_value)
                
                writer.writerow(row)
    
    def _write_test_results(self, result: FaultLocalizationResult) -> None:
        """Write test results to CSV."""
        filename = self.output_dir / "test_results.csv"
        matrix = result.coverage_matrix
        
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            
            # Write header
            writer.writerow([
                'Test Name',
                'Outcome',
                'Elements Covered',
                'Coverage Percentage'
            ])
            
            # Write test data
            total_elements = len(matrix.code_elements)
            
            for idx, test_name in enumerate(matrix.test_names):
                outcome = matrix.test_outcomes[idx].value
                elements_covered = sum(matrix.matrix[idx, :].astype(int))
                coverage_pct = (elements_covered / total_elements * 100) if total_elements > 0 else 0
                
                writer.writerow([
                    test_name,
                    outcome,
                    elements_covered,
                    f"{coverage_pct:.2f}%"
                ])

"""
CSV reporter for fault localization results.

This module generates CSV reports containing suspiciousness rankings,
similar to GZoltar's CSV output functionality.
"""

import csv
from pathlib import Path
from typing import List

import numpy as np
import pandas as pd

from rich.console import Console

from ..core.models import CodeElement, CoverageMatrix, FaultLocalizationResult, SuspiciousnessScore, TestOutcome


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
        self.console = Console()
    
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
        self.write_coverage_matrix(result.coverage_matrix)
        
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
            self.console.print(f"Summary report saved to: [blue]{filename}[/blue]")
    
    def write_coverage_matrix(self, matrix: CoverageMatrix, output_file: Path | None = None) -> None:
        """
        Save coverage matrix to CSV file.
        
        Args:
            coverage_matrix: The coverage matrix to save
            output_file: Path where to save the CSV file
            
        Raises:
            RuntimeError: If there's an error saving the file
        """
        try:
            if output_file is None:
                output_file = self.output_dir / "coverage_matrix.csv"

            # Prepare data for CSV
            data = []
            
            # Create header
            header = ['Element', 'File', 'Line', 'ElementType', 'ElementName'] + matrix.test_names
            
            # Add a special row for test outcomes
            outcome_row = ['OUTCOME', '', '', '', ''] + [o.value for o in matrix.test_outcomes]
            data.append(outcome_row)

            # Add rows for each code element
            for i, element in enumerate(matrix.code_elements):
                row = [
                    str(element),
                    str(element.file_path),
                    element.line_number,
                    element.element_type,
                    element.element_name or ''
                ]
                # Add coverage data for each test (transpose matrix to get element rows)
                coverage_for_element = matrix.matrix[:, i].tolist()
                row.extend(coverage_for_element)
                data.append(row)
            
            # Create DataFrame and save
            df = pd.DataFrame(data, columns=header)
            df.to_csv(output_file, index=False)

            self.console.print(f"Coverage data saved to: [blue]{output_file}[/blue]")
            self.console.print(f"Use '[cyan]pyfault fl -c {output_file}[/cyan]' to perform fault localization")

        except Exception as e:
            raise RuntimeError(f"Error saving coverage matrix to {output_file}: {e}")

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

        self.console.print(f"Test results saved to: [blue]{filename}[/blue]")


    def load_coverage_matrix(self, coverage_file: str) -> CoverageMatrix:
        """
        Load coverage matrix from CSV file.
        
        Expected CSV format (as generated by write_coverage_matrix):
        Element,File,Line,ElementType,ElementName,test1,test2,test3,...
        OUTCOME,,,,,PASSED,FAILED,PASSED,...
        file.py:1,file.py,1,line,,1,0,1,...
        file.py:2,file.py,2,line,,0,1,1,...
        
        Args:
            coverage_file: Path to the CSV file containing coverage matrix
            
        Returns:
            CoverageMatrix object
        """
        try:
            # Read CSV file
            df = pd.read_csv(coverage_file)
            
            # Validate required columns
            required_columns = ['Element', 'File', 'Line', 'ElementType', 'ElementName']
            if not all(col in df.columns for col in required_columns):
                raise ValueError(f"CSV file must contain columns: {required_columns}")

            # Extract test names (columns after ElementName)
            metadata_columns = ['Element', 'File', 'Line', 'ElementType', 'ElementName']
            test_columns = [col for col in df.columns if col not in metadata_columns]
            test_names = test_columns
            
            if not test_names:
                raise ValueError("Empty or malformed Coverage Matrix CSV file")

            # Extract test outcomes from the special 'OUTCOME' row
            outcome_row = df[df['Element'] == 'OUTCOME']
            if outcome_row.empty:
                raise ValueError("CSV file must contain an 'OUTCOME' row for test results.")
            
            test_outcomes_str = outcome_row[test_columns].iloc[0].tolist()
            test_outcomes = [TestOutcome(outcome.lower()) for outcome in test_outcomes_str]

            # Filter out the outcome row to process code elements
            df_elements = df[df['Element'] != 'OUTCOME'].reset_index(drop=True)
            
            # Extract code elements
            code_elements = []
            for _, row in df_elements.iterrows():
                element_name = row['ElementName'] if pd.notna(row['ElementName']) and row['ElementName'] != '' else None
                element = CodeElement(
                    file_path=Path(row['File']),
                    line_number=int(row['Line']),
                    element_type=row['ElementType'],
                    element_name=element_name
                )
                code_elements.append(element)
            
            # Extract coverage matrix
            coverage_data = df_elements[test_columns].values.astype(np.int8)
            
            # Transpose to get tests as rows, elements as columns
            matrix = coverage_data.T
            
            return CoverageMatrix(
                test_names=test_names,
                code_elements=code_elements,
                matrix=matrix,
                test_outcomes=test_outcomes
            )
            
        except Exception as e:
            raise RuntimeError(f"Error loading coverage matrix from {coverage_file}: {e}")

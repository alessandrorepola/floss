"""
JSON reporter for fault localization results.

This module generates JSON reports that are compatible with the PyFault dashboard,
bridging the gap between the backend analysis and frontend visualization.
"""

import json
from pathlib import Path
from typing import Any, Dict
from dataclasses import asdict, is_dataclass

from rich.console import Console

from ..core.models import FaultLocalizationResult, CodeElement, SuspiciousnessScore


class CustomEncoder(json.JSONEncoder):
    """Custom JSON encoder to handle dataclasses and Path objects."""
    
    def default(self, obj):
        """Convert non-serializable objects to JSON-compatible formats."""
        if isinstance(obj, Path):
            return str(obj.as_posix())  # Convert Path to standardized string format
        if is_dataclass(obj) and not isinstance(obj, type):
            return asdict(obj)
        return super().default(obj)


class JSONReporter:
    """
    Generates JSON reports for fault localization results.
    
    This reporter creates a JSON file structure that's compatible with 
    the PyFault dashboard, enabling seamless visualization of results.
    
    Example:
        >>> reporter = JSONReporter(Path('output'))
        >>> reporter.generate_report(results)
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize the JSON reporter.
        
        Args:
            output_dir: Directory where JSON files will be written
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.console = Console()
    
    def generate_report(self, result: FaultLocalizationResult) -> Path:
        """
        Generate JSON report for the fault localization results.
        
        Args:
            result: Fault localization results to report
            
        Returns:
            Path to the generated JSON file
        """
        output_path = self.output_dir / "summary.json"
        self.save_as_json(result, output_path)
        return output_path
    
    def save_as_json(self, result: FaultLocalizationResult, output_path: Path) -> None:
        """
        Serialize the fault localization result to a JSON file.
        
        Args:
            result: The FaultLocalizationResult to serialize
            output_path: Path where to save the JSON file
        """
        try:
            # Convert formulas data to dashboard-compatible format
            formulas_data = {}
            for formula_name, scores in result.scores.items():
                formulas_data[formula_name] = [
                    self._convert_score_to_dict(score) for score in scores
                ]
            
            # Extract all unique elements for the elements list
            all_elements = []
            seen_elements = set()
            for scores in result.scores.values():
                for score in scores:
                    element_key = (str(score.element.file_path), score.element.line_number)
                    if element_key not in seen_elements:
                        all_elements.append(self._convert_element_to_dict(score.element))
                        seen_elements.add(element_key)
            
            # Calculate additional statistics
            failed_tests = sum(1 for outcome in result.coverage_matrix.test_outcomes 
                             if outcome.value in ['failed', 'error'])
            total_tests = len(result.coverage_matrix.test_names)
            coverage_percentage = self._calculate_coverage_percentage(result.coverage_matrix)
            
            # Create dashboard-compatible structure
            output_dict = {
                'stats': {
                    'total_tests': total_tests,
                    'failed_tests': failed_tests,
                    'total_elements': len(result.coverage_matrix.code_elements),
                    'coverage_percentage': coverage_percentage,
                    'execution_time': result.execution_time,
                    'formulas_used': result.metadata.get('formulas_used', [])
                },
                'formulas': formulas_data,
                'elements': all_elements,
                'execution_time': result.execution_time,
                'metadata': result.metadata
            }
            
            # Save to JSON file
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(output_dict, f, cls=CustomEncoder, indent=2, ensure_ascii=False)
            
            self.console.print(f"JSON report saved to: [blue]{output_path}[/blue]")
            self.console.print(f"Use the dashboard to visualize: [cyan]pyfault ui --data {output_path}[/cyan]")
            
        except Exception as e:
            raise RuntimeError(f"Error saving JSON report to {output_path}: {e}")
    
    def _convert_score_to_dict(self, score: SuspiciousnessScore) -> Dict[str, Any]:
        """Convert a SuspiciousnessScore to dashboard-compatible dictionary."""
        return {
            'element': self._convert_element_to_dict(score.element),
            'score': score.score,
            'rank': score.rank,
            'formula_name': score.formula_name
        }
    
    def _convert_element_to_dict(self, element: CodeElement) -> Dict[str, Any]:
        """Convert a CodeElement to dashboard-compatible dictionary."""
        return {
            'file': str(element.file_path.as_posix()),
            'line': element.line_number,
            'element_type': element.element_type,
            'element_name': element.element_name
        }
    
    def _calculate_coverage_percentage(self, coverage_matrix) -> float:
        """Calculate overall coverage percentage."""
        if coverage_matrix.matrix.size == 0:
            return 0.0
        
        # Calculate percentage of elements covered by at least one test
        elements_covered = (coverage_matrix.matrix.sum(axis=0) > 0).sum()
        total_elements = len(coverage_matrix.code_elements)
        
        if total_elements == 0:
            return 0.0
        
        return (elements_covered / total_elements) * 100.0
    
    @classmethod
    def load_from_json(cls, json_path: Path) -> Dict[str, Any]:
        """
        Load fault localization results from a JSON file.
        
        Args:
            json_path: Path to the JSON file
            
        Returns:
            Dictionary containing the loaded data
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            raise RuntimeError(f"Error loading JSON from {json_path}: {e}")

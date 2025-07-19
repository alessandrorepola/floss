"""
Core data models for PyFault.

Defines the fundamental data structures used throughout the fault localization process.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple, Any
from enum import Enum
import numpy as np
from pathlib import Path


class TestOutcome(Enum):
    __test__ = False  # Prevent pytest from collecting this as a test case
    """Test execution outcome."""
    PASSED = "passed"
    FAILED = "failed"
    SKIPPED = "skipped"
    ERROR = "error"


@dataclass
class CodeElement:
    """Represents a code element that can be covered (line, branch, etc.)."""
    file_path: Path
    line_number: int
    element_type: str = "line"  # line, branch, function, class, etc.
    element_name: Optional[str] = None
    
    def __post_init__(self):
        """Normalize file path to ensure consistency."""
        try:
            self.file_path = self.file_path.resolve(strict=True)
        except FileNotFoundError:
            import logging
            logging.warning(
                f"CodeElement: FileNotFoundError for path '{self.file_path}'. "
                "Resolved as absolute path, but this may indicate a misconfiguration (e.g., wrong source_dir)."
            )
            self.file_path = self.file_path.absolute()
    def __str__(self) -> str:
        # String representation for easy debugging and logging.
        # Improves representation for branches    
        if self.element_name:
            return f"{self.file_path.name}:{self.line_number} ({self.element_name})"
        return f"{self.file_path.name}:{self.line_number}"
    
    def __hash__(self) -> int:
        """Hash based on file path, line number, element type, and name."""
        # Use element_name to differentiate branches
        return hash((str(self.file_path), self.line_number, self.element_type, self.element_name))


@dataclass
class TestResult:
    __test__ = False  # Prevent pytest from collecting this as a test case
    """Represents the result of a single test execution."""
    test_name: str
    outcome: TestOutcome
    execution_time: float = 0.0
    error_message: Optional[str] = None
    covered_elements: Set[CodeElement] = field(default_factory=set)
    
    @property
    def is_failed(self) -> bool:
        """Returns True if the test failed or had an error."""
        return self.outcome in (TestOutcome.FAILED, TestOutcome.ERROR)


@dataclass
class CoverageMatrix:
    """
    Represents the N×M coverage matrix where:
    - N = number of tests
    - M = number of code elements
    - Each cell indicates if a code element was covered by a test
    """
    test_names: List[str]
    code_elements: List[CodeElement]
    matrix: np.ndarray  # Binary matrix (N×M)
    test_outcomes: List[TestOutcome]
    
    def __post_init__(self):
        """Validate matrix dimensions."""
        n_tests = len(self.test_names)
        n_elements = len(self.code_elements)
        
        if self.matrix.shape != (n_tests, n_elements):
            raise ValueError(
                f"Matrix shape {self.matrix.shape} does not match "
                f"expected ({n_tests}, {n_elements})"
            )
        
        if len(self.test_outcomes) != n_tests:
            raise ValueError(
                f"Number of test outcomes ({len(self.test_outcomes)}) "
                f"does not match number of tests ({n_tests})"
            )
    
    @classmethod
    def from_test_results(cls, test_results: List[TestResult]) -> "CoverageMatrix":
        """Create a coverage matrix from a list of test results."""
        # Collect all unique code elements
        all_elements = set()
        for result in test_results:
            all_elements.update(result.covered_elements)
        
        code_elements = sorted(all_elements, key=lambda x: (str(x.file_path), x.line_number))
        element_to_idx = {elem: idx for idx, elem in enumerate(code_elements)}
        
        # Build matrix
        test_names = [result.test_name for result in test_results]
        test_outcomes = [result.outcome for result in test_results]
        
        n_tests = len(test_results)
        n_elements = len(code_elements)
        matrix = np.zeros((n_tests, n_elements), dtype=np.int8)
        
        for test_idx, result in enumerate(test_results):
            for element in result.covered_elements:
                element_idx = element_to_idx[element]
                matrix[test_idx, element_idx] = 1
        
        return cls(
            test_names=test_names,
            code_elements=code_elements,
            matrix=matrix,
            test_outcomes=test_outcomes
        )
    
    def get_element_stats(self, element_idx: int) -> Tuple[int, int, int, int]:
        """
        Get statistics for a code element:
        Returns (n_cf, n_nf, n_cp, n_np) where:
        - n_cf: number of failed tests that cover the element
        - n_nf: number of failed tests that do NOT cover the element  
        - n_cp: number of passed tests that cover the element
        - n_np: number of passed tests that do NOT cover the element
        """
        coverage_col = self.matrix[:, element_idx]
        
        failed_mask = np.array([outcome in (TestOutcome.FAILED, TestOutcome.ERROR) 
                               for outcome in self.test_outcomes])
        passed_mask = np.array([outcome == TestOutcome.PASSED 
                               for outcome in self.test_outcomes])
        
        n_cf = np.sum(failed_mask & (coverage_col == 1))
        n_nf = np.sum(failed_mask & (coverage_col == 0))
        n_cp = np.sum(passed_mask & (coverage_col == 1))
        n_np = np.sum(passed_mask & (coverage_col == 0))
        
        return int(n_cf), int(n_nf), int(n_cp), int(n_np)


@dataclass
class SuspiciousnessScore:
    """Represents a suspiciousness score for a code element."""
    element: CodeElement
    score: float
    formula_name: str
    rank: Optional[int] = None
    
    def __lt__(self, other: "SuspiciousnessScore") -> bool:
        """Enable sorting by score."""
        return self.score < other.score


@dataclass 
class FaultLocalizationResult:
    """Results of fault localization analysis."""
    coverage_matrix: CoverageMatrix
    scores: Dict[str, List[SuspiciousnessScore]]  # formula_name -> scores
    execution_time: float = 0.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_ranking(self, formula_name: str, limit: Optional[int] = None) -> List[SuspiciousnessScore]:
        """Get ranked list of SuspiciousnessScore objects for a specific formula."""
        if formula_name not in self.scores:
            raise ValueError(f"Formula '{formula_name}' not found in results")
        
        scores = self.scores[formula_name] # Scores are already sorted by score
        
        if limit:
            scores = scores[:limit]
        
        return scores
    
    def get_top_suspicious(self, formula_name: str, threshold: float = 0.5) -> List[CodeElement]:
        """Get code elements with suspiciousness above threshold."""
        ranking = self.get_ranking(formula_name)
        return [score.element for score in ranking if score.score >= threshold]

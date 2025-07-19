"""
Main fault localizer class that orchestrates the SBFL process.

This module provides the main API for performing fault localization,
similar to GZoltar's core functionality.
"""

import time
import logging
from pathlib import Path
from typing import List, Optional, Sequence, Union

import numpy as np

from ..coverage.collector import CoverageCollector
from ..test_runner.pytest_runner import PytestRunner
from ..formulas.base import SBFLFormula
from ..reporters.html_reporter import HTMLReporter
from ..reporters.csv_reporter import CSVReporter
from ..reporters.json_reporter import JSONReporter
from ..formulas import (
    OchiaiFormula,
    TarantulaFormula,
    JaccardFormula,
    DStarFormula,
    Kulczynski2Formula
)
from .models import (
    FaultLocalizationResult, 
    CoverageMatrix,
    SuspiciousnessScore
)

# Define a base type for test runners for better type hinting
TestRunner = Union[PytestRunner]

logger = logging.getLogger(__name__)


class FaultLocalizer:
    """
    Main fault localizer class that coordinates the SBFL process.
    
    Inspired by GZoltar's architecture, this class orchestrates:
    1. Code instrumentation and coverage collection
    2. Test execution
    3. SBFL formula application
    4. Report generation
    
    Example:
        >>> from pyfault import FaultLocalizer
        >>> from pyfault.formulas import OchiaiFormula
        >>> 
        >>> localizer = FaultLocalizer(
        ...     source_dirs=['src'],
        ...     test_dirs=['tests'],
        ...     formulas=[OchiaiFormula()],
        ...     branch_coverage=True
        ... )
        >>> results = localizer.run()
        >>> ranking = results.get_ranking('ochiai')
    """
    
    def __init__(
        self,
        source_dirs: Sequence[str | Path],
        test_dirs: Sequence[str | Path],
        formulas: Optional[List[SBFLFormula]] = None,
        test_runner: Optional[TestRunner] = None,
        coverage_collector: Optional[CoverageCollector] = None,
        output_dir: Optional[str | Path] = None,
        branch_coverage: bool = False
    ):
        """
        Initialize the fault localizer.
        
        Args:
            source_dirs: Directories containing source code to analyze
            test_dirs: Directories containing test files
            formulas: SBFL formulas to use (default: Ochiai, Tarantula, Jaccard)
            test_runner: An instance of a test runner (e.g., PytestRunner).
            coverage_collector: Custom coverage collector (uses default if None)
            output_dir: Directory for output files (default: './pyfault_output')
            branch_coverage: Use branch coverage instead of line coverage (default: False)
        """
        self.source_dirs = [Path(d) for d in source_dirs]
        self.test_dirs = [Path(d) for d in test_dirs]
        self.output_dir = Path(output_dir or './pyfault_output')
        self.branch_coverage = branch_coverage
        
        # Default formulas if none specified
        if formulas is None:
            self.formulas = [
                OchiaiFormula(),
                TarantulaFormula(), 
                JaccardFormula(),
                DStarFormula(star=2, name='DStar2'),
                Kulczynski2Formula()
            ]
        else:
            self.formulas = formulas
        
        # Initialize components with coverage type configuration
        self.coverage_collector = coverage_collector or CoverageCollector(
            self.source_dirs, branch_coverage=branch_coverage
        )
        
        if test_runner is None:
            self.test_runner: TestRunner = PytestRunner(self.test_dirs, self.coverage_collector)
        else:
            self.test_runner = test_runner    
            
        # Ensure output directory exists
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        coverage_type = "branch" if branch_coverage else "line"
        logger.info(f"Initialized FaultLocalizer with {len(self.formulas)} formulas, {coverage_type} coverage")
    
    def run(self, test_filter: Optional[str] = None) -> FaultLocalizationResult:
        """
        Run the complete fault localization process.
        
        Args:
            test_filter: Optional filter for test selection
            
        Returns:
            FaultLocalizationResult containing all analysis results
        """
        start_time = time.time()
        
        logger.info("Starting fault localization process")
        
        # Step 1: Collect coverage and run tests
        logger.info("Collecting coverage and executing tests")
        test_results = self.test_runner.run_tests(test_filter)        
        
        if not test_results:
            logger.warning("No tests were found or executed. Aborting analysis.")
            # Create an empty result object with a (0, 0) matrix
            return FaultLocalizationResult(
                coverage_matrix=CoverageMatrix([], [], np.empty((0, 0), dtype=np.int8), []),
                scores={},
                execution_time=time.time() - start_time,
                metadata={'message': 'No tests found or executed.'}
            )
        
        # Step 2: Build coverage matrix  
        logger.info(f"Building coverage matrix from {len(test_results)} test results")
        coverage_matrix = CoverageMatrix.from_test_results(test_results)
        
        # Step 3: Apply SBFL formulas
        logger.info(f"Applying {len(self.formulas)} SBFL formulas")
        all_scores = {}
        
        for formula in self.formulas:
            logger.info(f"Computing suspiciousness scores using {formula.name}")
            scores = self._compute_suspiciousness(coverage_matrix, formula)
            all_scores[formula.name] = scores
        
        # Step 4: Create result object
        execution_time = time.time() - start_time
        
        result = FaultLocalizationResult(
            coverage_matrix=coverage_matrix,
            scores=all_scores,
            execution_time=execution_time,
            metadata={
                'total_tests': len(test_results),
                'failed_tests': sum(1 for r in test_results if r.is_failed),
                'total_elements': len(coverage_matrix.code_elements),
                'formulas_used': [f.name for f in self.formulas]
            }
        )
        
        logger.info(f"Fault localization completed in {execution_time:.2f}s")
        
        # Step 5: Generate reports
        self._generate_reports(result)
        
        return result
    
    def _compute_suspiciousness(
        self, 
        coverage_matrix: CoverageMatrix, 
        formula: SBFLFormula
    ) -> List[SuspiciousnessScore]:
        """Compute suspiciousness scores for all code elements using the given formula."""
        scores = []
        
        for idx, element in enumerate(coverage_matrix.code_elements):
            # Get statistics for this element
            n_cf, n_nf, n_cp, n_np = coverage_matrix.get_element_stats(idx)
            
            # Calculate suspiciousness score
            score = formula.calculate(n_cf, n_nf, n_cp, n_np)
            
            scores.append(SuspiciousnessScore(
                element=element,
                score=score,
                formula_name=formula.name
            ))
        
        # Sort by score (descending) and assign ranks
        scores.sort(reverse=True)
        for rank, score in enumerate(scores, 1):
            score.rank = rank
        
        return scores
    
    def _generate_reports(self, result: FaultLocalizationResult) -> None:
        """Generate output reports."""
        logger.info("Generating reports")
        
        # CSV reports
        csv_reporter = CSVReporter(self.output_dir)
        csv_reporter.generate_report(result)
        
        # JSON reports (for dashboard compatibility)
        json_reporter = JSONReporter(self.output_dir)
        json_reporter.generate_report(result)
        
        # HTML reports  
        html_reporter = HTMLReporter(self.output_dir)
        html_reporter.generate_report(result)
        
        logger.info(f"Reports generated in {self.output_dir}")
    
    def analyze_from_data(
        self, 
        coverage_matrix: CoverageMatrix
    ) -> FaultLocalizationResult:
        """
        Perform fault localization analysis on existing coverage data.
        
        Useful when you already have coverage data and want to skip test execution.
        
        Args:
            coverage_matrix: Pre-built coverage matrix
            
        Returns:
            FaultLocalizationResult containing analysis results
        """
        start_time = time.time()
        
        logger.info("Analyzing existing coverage data")
        
        # Apply SBFL formulas
        all_scores = {}
        for formula in self.formulas:
            scores = self._compute_suspiciousness(coverage_matrix, formula)
            all_scores[formula.name] = scores
        
        execution_time = time.time() - start_time
        
        result = FaultLocalizationResult(
            coverage_matrix=coverage_matrix,
            scores=all_scores,
            execution_time=execution_time,
            metadata={
                'total_tests': len(coverage_matrix.test_names),
                'total_elements': len(coverage_matrix.code_elements),
                'formulas_used': [f.name for f in self.formulas]
            }
        )
        
        # Generate reports
        self._generate_reports(result)
        
        return result

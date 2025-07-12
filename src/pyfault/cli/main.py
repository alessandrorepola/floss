"""
Command-line interface for PyFault.

This module provides a CLI similar to GZoltar's command-line interface,
allowing batch execution of fault localization tasks.
"""

import sys
import logging
from pathlib import Path
from typing import List, Optional

import click
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.logging import RichHandler
import pandas as pd
import numpy as np

from ..core.fault_localizer import FaultLocalizer
from ..core.models import CodeElement, CoverageMatrix, TestOutcome
from ..formulas import (
    OchiaiFormula, TarantulaFormula, JaccardFormula,
    DStarFormula, Kulczynski2Formula
)

console = Console()


def setup_logging(verbose: bool = False) -> None:
    """Setup logging configuration."""
    level = logging.DEBUG if verbose else logging.INFO
    
    logging.basicConfig(
        level=level,
        format="%(message)s",
        datefmt="[%X]",
        handlers=[RichHandler(console=console, rich_tracebacks=True)]
    )


@click.group()
@click.option('--verbose', '-v', is_flag=True, help='Enable verbose output')
@click.pass_context
def main(ctx: click.Context, verbose: bool) -> None:
    """
    PyFault: Spectrum-Based Fault Localization for Python
    
    A tool for automated fault localization using SBFL techniques,
    inspired by GZoltar.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    setup_logging(verbose)


@main.command()
@click.option('--source-dir', '-s', multiple=True, required=True,
              help='Source code directories to analyze')
@click.option('--test-dir', '-t', multiple=True, required=True,
              help='Test directories')
@click.option('--output-dir', '-o', default='./pyfault_output',
              help='Output directory for results')
@click.option('--formula', '-f', multiple=True,
              type=click.Choice(['ochiai', 'tarantula', 'jaccard', 'dstar', 'kulczynski2']),
              help='SBFL formulas to use (default: ochiai, tarantula, jaccard)')
@click.option('--test-filter', '-k',
              help='Filter tests using pytest -k pattern')
@click.option('--top', '-n', type=int, default=20,
              help='Number of top suspicious elements to display')
@click.pass_context
def run(ctx: click.Context, source_dir: List[str], test_dir: List[str], 
        output_dir: str, formula: List[str], test_filter: Optional[str], top: int) -> None:
    """
    Run complete fault localization analysis.
    
    This command performs the full SBFL pipeline:
    1. Instrument source code
    2. Execute tests with coverage collection
    3. Apply SBFL formulas
    4. Generate reports
    """
    try:
        # Convert to Path objects
        source_dirs = [Path(d) for d in source_dir]
        test_dirs = [Path(d) for d in test_dir]
        output_path = Path(output_dir)
        
        # Validate directories
        for d in source_dirs + test_dirs:
            if not d.exists():
                raise click.ClickException(f"Directory not found: {d}")
        
        # Setup formulas
        if not formula:
            formulas = [OchiaiFormula(), TarantulaFormula(), JaccardFormula()]
        else:
            formula_map = {
                'ochiai': OchiaiFormula(),
                'tarantula': TarantulaFormula(),
                'jaccard': JaccardFormula(),
                'dstar': DStarFormula(),
                'kulczynski2': Kulczynski2Formula()
            }
            formulas = [formula_map[f] for f in formula]
        
        console.print(f"[bold green]Starting PyFault Analysis[/bold green]")
        console.print(f"Source dirs: {[str(d) for d in source_dirs]}")
        console.print(f"Test dirs: {[str(d) for d in test_dirs]}")
        console.print(f"Output dir: {output_path}")
        console.print(f"Formulas: {[f.name for f in formulas]}")
        
        # Initialize fault localizer
        localizer = FaultLocalizer(
            source_dirs=source_dirs,
            test_dirs=test_dirs,
            formulas=formulas,
            output_dir=output_path
        )
        
        # Run analysis with progress indicator
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Running fault localization...", total=None)
            result = localizer.run(test_filter=test_filter)
        
        # Display results
        _display_results(result, top)
        
        console.print(f"\n[bold green]✓[/bold green] Analysis complete!")
        console.print(f"Reports generated in: [blue]{output_path}[/blue]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


def _load_coverage_matrix_from_csv(coverage_file: str) -> CoverageMatrix:
    """
    Load coverage matrix from CSV file.
    
    Expected CSV format:
    Element,File,Line,test1,test2,test3,...
    file.py:1,file.py,1,1,0,1,...
    file.py:2,file.py,2,0,1,1,...
    
    Args:
        coverage_file: Path to the CSV file containing coverage matrix
        
    Returns:
        CoverageMatrix object
    """
    try:
        # Read CSV file
        df = pd.read_csv(coverage_file)
        
        # Validate required columns
        if not all(col in df.columns for col in ['Element', 'File', 'Line']):
            raise ValueError("CSV file must contain 'Element', 'File', and 'Line' columns")
        
        # Extract code elements
        code_elements = []
        for _, row in df.iterrows():
            element = CodeElement(
                file_path=Path(row['File']),
                line_number=int(row['Line']),
                element_type="line"
            )
            code_elements.append(element)
        
        # Extract test names (columns after 'Line')
        test_columns = [col for col in df.columns if col not in ['Element', 'File', 'Line']]
        test_names = test_columns
        
        if not test_names:
            raise ValueError("No test columns found in CSV file")
        
        # Extract coverage matrix
        coverage_data = df[test_columns].values.astype(np.int8)
        
        # Transpose to get tests as rows, elements as columns
        matrix = coverage_data.T
        
        # For now, assume all tests passed (since we don't have outcome info in CSV)
        # This could be enhanced to load test outcomes from a separate file
        test_outcomes = [TestOutcome.PASSED] * len(test_names)
        
        return CoverageMatrix(
            test_names=test_names,
            code_elements=code_elements,
            matrix=matrix,
            test_outcomes=test_outcomes
        )
        
    except Exception as e:
        raise RuntimeError(f"Error loading coverage matrix from {coverage_file}: {e}")


@main.command()
@click.option('--coverage-file', '-c', required=True,
              help='Coverage matrix file (CSV format)')
@click.option('--output-dir', '-o', default='./pyfault_output',
              help='Output directory for results')
@click.option('--formula', '-f', multiple=True,
              type=click.Choice(['ochiai', 'tarantula', 'jaccard', 'dstar', 'kulczynski2']),
              help='SBFL formulas to use')
@click.option('--top', '-n', type=int, default=20,
              help='Number of top suspicious elements to display')
@click.pass_context
def fl(ctx: click.Context, coverage_file: str, output_dir: str, 
       formula: List[str], top: int) -> None:
    """
    Perform fault localization on existing coverage data.
    
    This command applies SBFL formulas to pre-collected coverage data,
    useful when you want to skip test execution.
    """
    try:
        # Validate input file
        coverage_path = Path(coverage_file)
        if not coverage_path.exists():
            raise click.ClickException(f"Coverage file not found: {coverage_file}")
        
        # Setup formulas
        if not formula:
            formulas = [OchiaiFormula(), TarantulaFormula(), JaccardFormula()]
        else:
            formula_map = {
                'ochiai': OchiaiFormula(),
                'tarantula': TarantulaFormula(),
                'jaccard': JaccardFormula(),
                'dstar': DStarFormula(),
                'kulczynski2': Kulczynski2Formula()
            }
            formulas = [formula_map[f] for f in formula]
        
        console.print(f"[bold green]Loading coverage data from:[/bold green] {coverage_file}")
        
        # Load coverage matrix from CSV
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Loading coverage data...", total=None)
            coverage_matrix = _load_coverage_matrix_from_csv(coverage_file)
        
        console.print(f"Loaded {len(coverage_matrix.test_names)} tests and {len(coverage_matrix.code_elements)} elements")
        
        # Initialize fault localizer for analysis only
        output_path = Path(output_dir)
        localizer = FaultLocalizer(
            source_dirs=[Path(".")],  # Dummy source dir
            test_dirs=[Path(".")],    # Dummy test dir
            formulas=formulas,
            output_dir=output_path
        )
        
        console.print(f"[bold green]Running fault localization analysis...[/bold green]")
        console.print(f"Formulas: {[f.name for f in formulas]}")
        
        # Run analysis on loaded data
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Analyzing coverage data...", total=None)
            result = localizer.analyze_from_data(coverage_matrix)
        
        # Display results
        _display_results(result, top)
        
        console.print(f"\n[bold green]✓[/bold green] Analysis complete!")
        console.print(f"Reports generated in: [blue]{output_path}[/blue]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@main.command()
@click.option('--source-dir', '-s', multiple=True, required=True,
              help='Source code directories')
@click.option('--test-dir', '-t', multiple=True, required=True,
              help='Test directories')
@click.option('--test-filter', '-k',
              help='Filter tests using pytest -k pattern')
def test(source_dir: List[str], test_dir: List[str], test_filter: Optional[str]) -> None:
    """
    Run tests with coverage collection only.
    
    This command executes tests and collects coverage data without
    performing fault localization analysis.
    """
    try:
        source_dirs = [Path(d) for d in source_dir]
        test_dirs = [Path(d) for d in test_dir]
        
        # Just use a simple localizer to run tests
        localizer = FaultLocalizer(
            source_dirs=source_dirs,
            test_dirs=test_dirs,
            formulas=[OchiaiFormula()]  # Minimal formula for testing
        )
        
        console.print("[bold green]Running tests with coverage...[/bold green]")
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Executing tests...", total=None)
            result = localizer.run(test_filter=test_filter)
        
        # Display test statistics
        matrix = result.coverage_matrix
        passed = sum(1 for outcome in matrix.test_outcomes if outcome.value == 'passed')
        failed = sum(1 for outcome in matrix.test_outcomes if outcome.value in ('failed', 'error'))
        
        console.print(f"\n[bold green]✓[/bold green] Tests completed!")
        console.print(f"Total tests: {len(matrix.test_outcomes)}")
        console.print(f"Passed: [green]{passed}[/green]")
        console.print(f"Failed: [red]{failed}[/red]")
        console.print(f"Coverage: {len(matrix.code_elements)} elements")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        sys.exit(1)


def _display_results(result, top: int) -> None:
    """Display fault localization results in a nice table."""
    console.print(f"\n[bold]Top {top} Suspicious Elements[/bold]")
    
    for formula_name in result.scores:
        ranking = result.get_ranking(formula_name, limit=top)
        
        if not ranking:
            continue
        
        table = Table(title=f"{formula_name.title()} Formula")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("File", style="magenta")
        table.add_column("Line", style="green", width=8)
        table.add_column("Score", style="yellow", width=10)
        
        for idx, (element, score) in enumerate(ranking, 1):
            table.add_row(
                str(idx),
                str(element.file_path.name),
                str(element.line_number),
                f"{score:.4f}"
            )
        
        console.print(table)
        console.print()


if __name__ == '__main__':
    main()

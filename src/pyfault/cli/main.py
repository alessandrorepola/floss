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

from pyfault.reporters.csv_reporter import CSVReporter

from ..core.fault_localizer import FaultLocalizer
from ..core.models import FaultLocalizationResult
from ..coverage.collector import CoverageCollector
from ..test_runner.pytest_runner import PytestRunner
from ..core.models import CoverageMatrix
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
@click.option('--branch-coverage', '-b', is_flag=True, default=False,
              help='Use branch coverage instead of line coverage')
@click.pass_context
def run(ctx: click.Context, source_dir: List[str], test_dir: List[str], 
        output_dir: str, formula: List[str], test_filter: Optional[str], 
        top: int, branch_coverage: bool) -> None:
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
            formulas = [OchiaiFormula(), TarantulaFormula(), JaccardFormula(), DStarFormula(), Kulczynski2Formula()]
        else:
            formula_map = {
                'ochiai': OchiaiFormula(),
                'tarantula': TarantulaFormula(),
                'jaccard': JaccardFormula(),
                'dstar': DStarFormula(),
                'kulczynski2': Kulczynski2Formula()
            }
            formulas = [formula_map[f] for f in formula]
        
        coverage_type = "branch" if branch_coverage else "line"
        console.print(f"[bold green]Starting PyFault Analysis[/bold green]")
        console.print(f"Source dirs: {[str(d) for d in source_dirs]}")
        console.print(f"Test dirs: {[str(d) for d in test_dirs]}")
        console.print(f"Output dir: {output_path}")
        console.print(f"Coverage type: [cyan]{coverage_type}[/cyan]")
        console.print(f"Formulas: {[f.name for f in formulas]}")
        
        # Initialize fault localizer with coverage type
        localizer = FaultLocalizer(
            source_dirs=source_dirs,
            test_dirs=test_dirs,
            formulas=formulas,
            output_dir=output_path,
            branch_coverage=branch_coverage
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
            formulas = [OchiaiFormula(), TarantulaFormula(), JaccardFormula(), DStarFormula(), Kulczynski2Formula()]
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
            coverage_matrix = CSVReporter(Path()).load_coverage_matrix(coverage_file)
        
        console.print(f"Loaded {len(coverage_matrix.test_names)} tests and {len(coverage_matrix.code_elements)} elements")
        
        # Initialize fault localizer for analysis only
        output_path = Path(output_dir)
        localizer = FaultLocalizer(
            source_dirs=[],  # Not needed when analyzing from data
            test_dirs=[],    # Not needed when analyzing from data
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
@click.option('--output-dir', '-o', default='./pyfault_output',
              help='Output directory for coverage data')
@click.option('--test-filter', '-k',
              help='Filter tests using pytest -k pattern')
@click.option('--save-coverage', is_flag=True, default=True,
              help='Save coverage matrix to CSV file')
@click.option('--branch-coverage', '-b', is_flag=True, default=False,
              help='Use branch coverage instead of line coverage')
@click.pass_context
def test(ctx: click.Context, source_dir: List[str], test_dir: List[str], 
         output_dir: str, test_filter: Optional[str], save_coverage: bool,
         branch_coverage: bool) -> None:
    """
    Run tests with coverage collection only.
    
    This command executes tests and collects coverage data without
    performing fault localization analysis. The coverage data can be
    saved for later analysis using the 'fl' command.
    """
    try:
        source_dirs = [Path(d) for d in source_dir]
        test_dirs = [Path(d) for d in test_dir]
        output_path = Path(output_dir)
        
        # Validate directories
        for d in source_dirs + test_dirs:
            if not d.exists():
                raise click.ClickException(f"Directory not found: {d}")
        
        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)
        
        coverage_type = "branch" if branch_coverage else "line"
        console.print("[bold green]Running tests with coverage collection...[/bold green]")
        console.print(f"Source dirs: {[str(d) for d in source_dirs]}")
        console.print(f"Test dirs: {[str(d) for d in test_dirs]}")
        console.print(f"Output dir: {output_path}")
        console.print(f"Coverage type: [cyan]{coverage_type}[/cyan]")
        
        # Initialize components with coverage type
        coverage_collector = CoverageCollector(source_dirs, branch_coverage=branch_coverage)
        test_runner = PytestRunner(test_dirs, coverage_collector)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console
        ) as progress:
            task = progress.add_task("Executing tests and collecting coverage...", total=None)
            
            # Run tests and get results
            test_results = test_runner.run_tests(test_filter)
        
        if not test_results:
            raise RuntimeError("No test results collected")
        
        # Build coverage matrix
        coverage_matrix = CoverageMatrix.from_test_results(test_results)
        
        # Display test statistics
        failed_count = sum(1 for r in test_results if r.is_failed)
        passed_count = len(test_results) - failed_count
        
        console.print(f"\n[bold green]✓[/bold green] Test execution completed!")
        console.print(f"Total tests: {len(test_results)}")
        console.print(f"Passed: [green]{passed_count}[/green]")
        console.print(f"Failed: [red]{failed_count}[/red]")
        console.print(f"Coverage collected for: {len(coverage_matrix.code_elements)} code elements")
        
        # Save coverage data if requested
        if save_coverage:            
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console
            ) as progress:
                task = progress.add_task("Saving coverage data...", total=None)
                reporter = CSVReporter(output_dir=output_path)
                reporter.write_coverage_matrix(coverage_matrix)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@main.command()
@click.option('--data-file', '-d', 
              help='Load existing results (JSON/CSV)')
@click.option('--port', '-p', default=8501,
              help='Port for web interface')
@click.option('--auto-open', is_flag=True,
              help='Automatically open browser')
@click.pass_context
def ui(ctx: click.Context, data_file: Optional[str], port: int, auto_open: bool) -> None:
    """
    Launch interactive web UI for fault localization results.
    
    Opens a Streamlit-based dashboard for visualizing and analyzing
    fault localization results. Can load existing data or allow upload.
    """
    try:
        # Validate data file if provided
        if data_file:
            data_path = Path(data_file)
            if not data_path.exists():
                raise click.ClickException(f"Data file not found: {data_file}")
            
            console.print(f"[bold green]Loading data from:[/bold green] {data_file}")
        
        console.print(f"[bold green]Starting PyFault Dashboard...[/bold green]")
        console.print(f"Port: [blue]{port}[/blue]")
        console.print(f"Auto-open browser: [blue]{auto_open}[/blue]")
        
        # Import and launch dashboard
        from ..ui.dashboard import launch_dashboard
        
        launch_dashboard(data_file, port, auto_open)
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


def _display_results(result: FaultLocalizationResult, top: int) -> None:
    """Display fault localization results in a nice table."""
    console.print(f"\n[bold]Top {top} Suspicious Elements[/bold]")
    
    for formula_name in result.scores:
        ranking = result.get_ranking(formula_name, limit=top)
        
        if not ranking:
            continue
        
        table = Table(title=f"{formula_name.title()} Formula")
        table.add_column("Rank", style="cyan", width=6)
        table.add_column("File", style="magenta")
        table.add_column("Element", style="green", max_width=50)
        table.add_column("Score", style="yellow", width=10)
        
        for score in ranking: # ranking is a list of SuspiciousnessScore
            element = score.element
            table.add_row(
                str(score.rank),
                str(element.file_path.name),
                f"L{element.line_number} ({element.element_type}: {element.element_name or 'line'})",
                f"{score.score:.4f}"
            )
        
        console.print(table)
        console.print()


if __name__ == '__main__':
    main()

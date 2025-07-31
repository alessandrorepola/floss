"""
Command-line interface for PyFault.

This module provides a CLI for fault localization tasks.
"""

import sys
import logging
import json
from typing import List, Optional

import click
from rich.console import Console
from rich.logging import RichHandler

from ..test.runner import TestRunner
from ..test.config import TestConfig
from ..fl.engine import FLEngine
from ..fl.config import FLConfig

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
    
    A tool for automated fault localization using SBFL techniques.
    """
    ctx.ensure_object(dict)
    ctx.obj['verbose'] = verbose
    setup_logging(verbose)


@main.command()
@click.option('--source-dir', '-s', default='.',
              help='Source code directory to analyze (default: .)')
@click.option('--test-dir', '-t', 
              help='Test directory (default: auto-detected by pytest)')
@click.option('--output', '-o', default='coverage.json',
              help='Output file for coverage data (default: coverage.json)')
@click.option('--test-filter', '-k',
              help='Filter tests using pytest -k pattern')
@click.option('--ignore', multiple=True,
              help='Additional file patterns to ignore for test discovery (besides */__init__.py)')
@click.option('--omit', multiple=True,
              help='Additional file patterns to omit from coverage (besides */__init__.py)')
@click.option('--config', '-c', default='pyfault.conf',
              help='Configuration file (default: pyfault.conf)')
@click.pass_context
def test(ctx: click.Context, source_dir: str, test_dir: Optional[str], 
         output: str, test_filter: Optional[str], ignore: List[str],
         omit: List[str], config: str) -> None:
    """
    Run tests with coverage collection.
    
    Executes tests using pytest with coverage context collection and produces
    an enhanced coverage JSON file with test outcome information.
    """
    try:
        # Load configuration
        test_config = TestConfig.from_file(config)
        
        # Override with command line arguments
        if source_dir != '.':  # Only override if different from default
            test_config.source_dir = source_dir
        if test_dir:
            test_config.test_dir = test_dir
        if output != 'coverage.json':
            test_config.output_file = output
        
        # Merge ignore patterns
        if ignore:
            test_config.ignore_patterns = (test_config.ignore_patterns or []) + list(ignore)

        # Merge omit patterns
        if omit:
            test_config.omit_patterns = (test_config.omit_patterns or []) + list(omit)

        console.print("[bold green]Running tests with coverage collection...[/bold green]")
        console.print(f"Source dir: [cyan]{test_config.source_dir}[/cyan]")
        if test_config.test_dir:
            console.print(f"Test dir: [cyan]{test_config.test_dir}[/cyan]")
        console.print(f"Output file: [cyan]{test_config.output_file}[/cyan]")
        
        # Execute tests
        runner = TestRunner(test_config)
        result = runner.run_tests(test_filter)
        
        # Write coverage matrix code_lines-tests
        with open(test_config.output_file, 'w') as f:
            json.dump(result.coverage_data, f, indent=2)
        
        # Display results
        total_tests = len(result.passed_tests) + len(result.failed_tests) + len(result.skipped_tests)
        console.print(f"\n[bold green]✓[/bold green] Test execution completed!")
        console.print(f"Total tests: {total_tests}")
        console.print(f"Passed: [green]{len(result.passed_tests)}[/green]")
        console.print(f"Failed: [red]{len(result.failed_tests)}[/red]")
        console.print(f"Skipped: [yellow]{len(result.skipped_tests)}[/yellow]")

        if result.failed_tests:
            console.print(f"\n[bold red]Failed tests:[/bold red]")
            for test in result.failed_tests:
                console.print(f"  - {test}")
        
        console.print(f"\n[bold green]Coverage data saved to:[/bold green] {test_config.output_file}")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


@main.command()
@click.option('--input', '-i', default='coverage.json',
              help='Input coverage file (default: coverage.json)')
@click.option('--output', '-o', default='report.json',
              help='Output report file (default: report.json)')
@click.option('--formulas', '-f', multiple=True,
              help='SBFL formulas to use (default: all available)')
@click.option('--config', '-c', default='pyfault.conf',
              help='Configuration file (default: pyfault.conf)')
@click.pass_context
def fl(ctx: click.Context, input: str, output: str, formulas: List[str], config: str) -> None:
    """
    Calculate fault localization suspiciousness scores.
    
    Takes a coverage.json file as input and produces a report.json file
    with suspiciousness scores calculated using SBFL formulas.
    """
    try:
        # Load configuration
        fl_config = FLConfig.from_file(config)
        
        # Override with command line arguments
        if input != 'coverage.json':
            fl_config.input_file = input
        if output != 'report.json':
            fl_config.output_file = output
        if formulas:
            fl_config.formulas = list(formulas)
        
        console.print("[bold green]Calculating fault localization scores...[/bold green]")
        console.print(f"Input file: [cyan]{fl_config.input_file}[/cyan]")
        console.print(f"Output file: [cyan]{fl_config.output_file}[/cyan]")
        console.print(f"Formulas: [cyan]{', '.join(fl_config.formulas or [])}[/cyan]")
        
        # Create FL engine and calculate
        engine = FLEngine(fl_config)
        engine.calculate_suspiciousness(fl_config.input_file, fl_config.output_file)
        
        console.print(f"\n[bold green]✓[/bold green] Fault localization completed!")
        console.print(f"Report saved to: [cyan]{fl_config.output_file}[/cyan]")
        
    except Exception as e:
        console.print(f"[bold red]Error:[/bold red] {e}")
        if ctx.obj.get('verbose'):
            console.print_exception()
        sys.exit(1)


if __name__ == '__main__':
    main()

"""
Clean and minimal PyFault dashboard for fault localization visualization.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import numpy as np
from pathlib import Path
from typing import Dict, List, Any, Optional, NamedTuple
import os
import sys
import subprocess
import tkinter as tk
from tkinter import filedialog

# Data structures for cached computations
class FormulaStats(NamedTuple):
    """Statistics for a specific formula."""
    min_score: float
    max_score: float
    range_score: float
    all_scores: List[float]


class FileStats(NamedTuple):
    """Statistics for a file's suspiciousness."""
    file_path: str
    max_score: float
    avg_score: float
    suspicious_statements: int
    suspicious_statements_pct: float
    suspicious_branches: int
    suspicious_branches_pct: float
    total_statements_with_coverage: int
    total_branches_with_coverage: int


def select_directory_with_dialog() -> Optional[str]:
    """Open native file dialog to select directory."""
    try:
        # Create a root window but hide it
        root = tk.Tk()
        root.withdraw()
        root.attributes('-topmost', True)  # Bring dialog to front
        
        # Open directory selection dialog
        directory = filedialog.askdirectory(
            title="Select Project Root Directory",
            mustexist=True
        )
        
        # Clean up
        root.destroy()
        
        return directory if directory else None
    except Exception as e:
        st.error(f"Error opening file dialog: {str(e)}")
        return None


@st.cache_data
def calculate_formula_statistics(data: Dict[str, Any], formula: str) -> FormulaStats:
    """Calculate and cache min/max/range statistics for a specific formula.
    
    This is the core optimization - all normalization calculations depend on these values.
    """
    files_data = data.get('files', {})
    all_scores = []
    
    for _, file_data in files_data.items():
        suspiciousness = file_data.get('suspiciousness', {})
        for line_scores in suspiciousness.values():
            if formula in line_scores:
                all_scores.append(float(line_scores[formula]))
    
    if not all_scores:
        return FormulaStats(0.0, 0.0, 1.0, [])
    
    min_score = min(all_scores)
    max_score = max(all_scores)
    range_score = max_score - min_score if max_score > min_score else 1.0
    
    return FormulaStats(min_score, max_score, range_score, all_scores)


@st.cache_data
def calculate_file_suspiciousness_stats(data: Dict[str, Any], formula: str, 
                                       formula_stats: FormulaStats) -> List[FileStats]:
    """Calculate and cache file-level suspiciousness statistics.
    
    Uses pre-calculated formula statistics to avoid redundant computations.
    """
    files_data = data.get('files', {})
    file_suspiciousness = []
    
    for file_path, file_data in files_data.items():
        file_scores = []
        normalized_scores = []
        suspicious_statements_count = 0
        total_statements_with_test_coverage = 0
        suspicious_branches_count = 0
        total_branches_with_test_coverage = 0
        
        # Get executed lines (actual statements)
        executed_lines = file_data.get('executed_lines', [])
        contexts = file_data.get('contexts', {})
        suspiciousness = file_data.get('suspiciousness', {})
        
        # Get executed branches
        executed_branches = file_data.get('executed_branches', [])
        
        # Process only executed statements that have test coverage
        for line_num in executed_lines:
            line_str = str(line_num)
            
            # Check if this line has test coverage (non-empty contexts)
            line_contexts = contexts.get(line_str, [])
            has_test_coverage = any(context.strip() for context in line_contexts)
            
            # Check if this line has suspiciousness score
            if line_str in suspiciousness and formula in suspiciousness[line_str] and has_test_coverage:
                score = float(suspiciousness[line_str][formula])
                # Normalize score to 0-1 range using cached stats
                normalized_score = (score - formula_stats.min_score) / formula_stats.range_score
                file_scores.append(score)
                normalized_scores.append(normalized_score)
                total_statements_with_test_coverage += 1
        
        # Process executed branches that have test coverage
        for branch in executed_branches:
            if len(branch) >= 2:
                source_line = branch[0]
                source_line_str = str(source_line)
                
                # Check if the source line of the branch has test coverage
                line_contexts = contexts.get(source_line_str, [])
                has_test_coverage = any(context.strip() for context in line_contexts)
                
                # Check if the source line has suspiciousness score
                if source_line_str in suspiciousness and formula in suspiciousness[source_line_str] and has_test_coverage:
                    total_branches_with_test_coverage += 1
        
        if file_scores:
            avg_score = sum(normalized_scores) / len(normalized_scores)
            max_score = max(normalized_scores)
            
            # Only include files with max suspiciousness > 0 (normalized)
            if max_score > 0:
                file_suspiciousness.append(FileStats(
                    file_path=file_path,
                    max_score=max_score,
                    avg_score=avg_score,
                    suspicious_statements=suspicious_statements_count,
                    suspicious_statements_pct=0.0,  # Will be calculated later when threshold is known
                    suspicious_branches=suspicious_branches_count,
                    suspicious_branches_pct=0.0,  # Will be calculated later when threshold is known
                    total_statements_with_coverage=total_statements_with_test_coverage,
                    total_branches_with_coverage=total_branches_with_test_coverage
                ))
    
    return file_suspiciousness


@st.cache_data
def get_most_suspicious_file_cached(data: Dict[str, Any], formula: str, 
                                   formula_stats: FormulaStats) -> Optional[str]:
    """Get the most suspicious file using cached statistics."""
    file_stats = calculate_file_suspiciousness_stats(data, formula, formula_stats)
    
    if not file_stats:
        return None
    
    # Sort by max score (priority), then by number of statements with coverage
    sorted_files = sorted(file_stats, 
                         key=lambda x: (x.max_score, x.total_statements_with_coverage), 
                         reverse=True)
    return sorted_files[0].file_path


@st.cache_data
def build_hierarchical_data_cached(data: Dict[str, Any], formula: str, 
                                  formula_stats: FormulaStats, 
                                  min_score: float = 0.0) -> Dict[str, List]:
    """Build hierarchical data structure using cached formula statistics."""
    files_data = data.get('files', {})
    
    if not formula_stats.all_scores:
        return {'labels': [], 'parents': [], 'values': [], 'colors': [], 'hover_info': []}
    
    # Convert normalized min_score to actual threshold using cached stats
    actual_min_score = formula_stats.min_score + (min_score * formula_stats.range_score)
    
    labels = []
    parents = []
    values = []
    colors = []
    hover_info = []
    
    # Root node
    labels.append("Project")
    parents.append("")
    values.append(1)
    colors.append(0.0)
    
    # Get overall project coverage from totals
    totals = data.get('totals', {})
    project_coverage = totals.get('percent_covered', 0.0)
    total_files = totals.get('analysis_statistics', {}).get('files_analyzed', 0)
    hover_info.append(f"Project<br>Coverage: {project_coverage:.1f}%<br>Files: {total_files}")
    
    # Process files with cached normalization
    for file_path, file_data in files_data.items():
        file_suspiciousness = file_data.get('suspiciousness', {})
        if not file_suspiciousness:
            continue
            
        # Check if file has any scores above threshold (using actual threshold)
        file_scores = []
        for line_scores in file_suspiciousness.values():
            if formula in line_scores:
                raw_score = float(line_scores[formula])
                if raw_score >= actual_min_score:
                    # Normalize score to 0-1 range using cached stats
                    normalized_score = (raw_score - formula_stats.min_score) / formula_stats.range_score
                    file_scores.append(normalized_score)
        
        if not file_scores:
            continue  # Skip files with no significant scores
        
        # Get just the filename for display (ensure it's unique)
        file_name = file_path
        
        # Make file name unique if necessary
        counter = 1
        original_file_name = file_name
        while file_name in labels:
            file_name = f"{original_file_name} ({counter})"
            counter += 1
        
        # Get file coverage summary
        file_summary = file_data.get('summary', {})
        file_coverage = file_summary.get('percent_covered', 0.0)
        file_statements = file_summary.get('num_statements', 0)
        file_covered_lines = file_summary.get('covered_lines', 0)
        
        # Add file
        avg_file_score = sum(file_scores) / len(file_scores)
        file_lines_count = len(file_scores)
        
        labels.append(file_name)
        parents.append("Project")  # All files directly under project
        values.append(max(file_lines_count, 1))
        colors.append(avg_file_score)
        hover_info.append(f"File: {file_name}<br>Coverage: {file_coverage:.1f}%<br>Lines: {file_covered_lines}/{file_statements}")
        
        # Add classes and functions within the file (only if they have significant scores)
        classes_data = file_data.get('classes', {})
        functions_data = file_data.get('functions', {})
        
        # Process classes
        for class_name, class_info in classes_data.items():
            if class_name == "" or len(class_name) == 0:
                continue  # Skip global code
            
            # Get class suspiciousness from executed lines
            executed_lines = class_info.get('executed_lines', [])
            class_scores = []
            for line_num in executed_lines:
                line_str = str(line_num)
                if line_str in file_suspiciousness:
                    raw_score = float(file_suspiciousness[line_str].get(formula, 0.0))
                    if raw_score >= actual_min_score:
                        # Normalize score to 0-1 range using cached stats
                        normalized_score = (raw_score - formula_stats.min_score) / formula_stats.range_score
                        class_scores.append(normalized_score)
            
            if not class_scores:
                continue  # Skip classes with no significant scores
            
            avg_class_score = sum(class_scores) / len(class_scores)
            class_lines_count = len(class_scores)
            
            # Make class label unique
            class_label = f"class {class_name}"
            counter = 1
            original_class_label = class_label
            while class_label in labels:
                class_label = f"{original_class_label} ({counter})"
                counter += 1
            
            labels.append(class_label)
            parents.append(file_name)  # Class parent is the file
            values.append(max(class_lines_count, 1))
            colors.append(avg_class_score)
            hover_info.append(f"Class: {class_name}<br>Lines with data: {class_lines_count}<br>Avg Score: {avg_class_score:.3f}")
            
            # Add methods for this class (only with significant scores)
            for func_name, func_info in functions_data.items():
                if func_name.startswith(f"{class_name}."):
                    method_name = func_name.split('.')[-1]
                    
                    method_executed_lines = func_info.get('executed_lines', [])
                    method_scores = []
                    for line_num in method_executed_lines:
                        line_str = str(line_num)
                        if line_str in file_suspiciousness:
                            raw_score = float(file_suspiciousness[line_str].get(formula, 0.0))
                            if raw_score >= actual_min_score:
                                # Normalize score to 0-1 range using cached stats
                                normalized_score = (raw_score - formula_stats.min_score) / formula_stats.range_score
                                method_scores.append(normalized_score)
                    
                    if not method_scores:
                        continue  # Skip methods with no significant scores
                    
                    # Get method coverage summary
                    method_summary = func_info.get('summary', {})
                    method_coverage = method_summary.get('percent_covered', 0.0)
                    method_statements = method_summary.get('num_statements', 0)
                    
                    avg_method_score = sum(method_scores) / len(method_scores)
                    method_lines_count = len(method_scores)
                    
                    # Make method label unique
                    method_label = f"def {method_name}()"
                    counter = 1
                    original_method_label = method_label
                    while method_label in labels:
                        method_label = f"{original_method_label} ({counter})"
                        counter += 1
                    
                    labels.append(method_label)
                    parents.append(class_label)  # Method parent is the class
                    values.append(max(method_lines_count, 1))
                    colors.append(avg_method_score)
                    hover_info.append(f"Method: {method_name}<br>Coverage: {method_coverage:.1f}%<br>Statements: {method_statements}")
        
        # Process standalone functions (not methods, only with significant scores)
        for func_name, func_info in functions_data.items():
            if '.' in func_name or func_name == "" or len(func_name) == 0:
                continue  # Skip methods and global code
            
            func_executed_lines = func_info.get('executed_lines', [])
            func_scores = []
            for line_num in func_executed_lines:
                line_str = str(line_num)
                if line_str in file_suspiciousness:
                    raw_score = float(file_suspiciousness[line_str].get(formula, 0.0))
                    if raw_score >= actual_min_score:
                        # Normalize score to 0-1 range using cached stats
                        normalized_score = (raw_score - formula_stats.min_score) / formula_stats.range_score
                        func_scores.append(normalized_score)
            
            if not func_scores:
                continue  # Skip functions with no significant scores
            
            # Get function coverage summary
            func_summary = func_info.get('summary', {})
            func_coverage = func_summary.get('percent_covered', 0.0)
            func_statements = func_summary.get('num_statements', 0)
            
            avg_func_score = sum(func_scores) / len(func_scores)
            func_lines_count = len(func_scores)
            
            # Make function label unique
            func_label = f"def {func_name}()"
            counter = 1
            original_func_label = func_label
            while func_label in labels:
                func_label = f"{original_func_label} ({counter})"
                counter += 1
            
            labels.append(func_label)
            parents.append(file_name)  # Function parent is the file
            values.append(max(func_lines_count, 1))
            colors.append(avg_func_score)
            hover_info.append(f"Function: {func_name}<br>Coverage: {func_coverage:.1f}%<br>Statements: {func_statements}")
    
    return {
        'labels': labels,
        'parents': parents,
        'values': values,
        'colors': colors,
        'hover_info': hover_info
    }


def calculate_file_suspiciousness_with_threshold(data: Dict[str, Any], formula: str, 
                                               formula_stats: FormulaStats, 
                                               actual_threshold: float) -> List[FileStats]:
    """Calculate file suspiciousness statistics with a specific threshold."""
    files_data = data.get('files', {})
    file_suspiciousness = []
    
    for file_path, file_data in files_data.items():
        file_scores = []
        normalized_scores = []
        suspicious_statements_count = 0
        total_statements_with_test_coverage = 0
        suspicious_branches_count = 0
        total_branches_with_test_coverage = 0
        
        # Get executed lines (actual statements)
        executed_lines = file_data.get('executed_lines', [])
        contexts = file_data.get('contexts', {})
        suspiciousness = file_data.get('suspiciousness', {})
        
        # Get executed branches
        executed_branches = file_data.get('executed_branches', [])
        
        # Process only executed statements that have test coverage
        for line_num in executed_lines:
            line_str = str(line_num)
            
            # Check if this line has test coverage (non-empty contexts)
            line_contexts = contexts.get(line_str, [])
            has_test_coverage = any(context.strip() for context in line_contexts)
            
            # Check if this line has suspiciousness score
            if line_str in suspiciousness and formula in suspiciousness[line_str] and has_test_coverage:
                score = float(suspiciousness[line_str][formula])
                # Normalize score to 0-1 range using cached stats
                normalized_score = (score - formula_stats.min_score) / formula_stats.range_score
                file_scores.append(score)
                normalized_scores.append(normalized_score)
                total_statements_with_test_coverage += 1
                if score >= actual_threshold:
                    suspicious_statements_count += 1
        
        # Process executed branches that have test coverage
        for branch in executed_branches:
            if len(branch) >= 2:
                source_line = branch[0]
                source_line_str = str(source_line)
                
                # Check if the source line of the branch has test coverage
                line_contexts = contexts.get(source_line_str, [])
                has_test_coverage = any(context.strip() for context in line_contexts)
                
                # Check if the source line has suspiciousness score
                if source_line_str in suspiciousness and formula in suspiciousness[source_line_str] and has_test_coverage:
                    score = float(suspiciousness[source_line_str][formula])
                    total_branches_with_test_coverage += 1
                    if score >= actual_threshold:
                        suspicious_branches_count += 1
        
        if file_scores:
            avg_score = sum(normalized_scores) / len(normalized_scores)
            max_score = max(normalized_scores)
            
            # Calculate percentage of suspicious statements
            suspicious_statements_percentage = (suspicious_statements_count / total_statements_with_test_coverage * 100) if total_statements_with_test_coverage > 0 else 0
            
            # Calculate percentage of suspicious branches
            suspicious_branches_percentage = (suspicious_branches_count / total_branches_with_test_coverage * 100) if total_branches_with_test_coverage > 0 else 0
            
            # Only include files with max suspiciousness > 0 (normalized)
            if max_score > 0:
                file_suspiciousness.append(FileStats(
                    file_path=file_path,
                    max_score=round(max_score, 3),
                    avg_score=round(avg_score, 3),
                    suspicious_statements=suspicious_statements_count,
                    suspicious_statements_pct=round(suspicious_statements_percentage, 1),
                    suspicious_branches=suspicious_branches_count,
                    suspicious_branches_pct=round(suspicious_branches_percentage, 1),
                    total_statements_with_coverage=total_statements_with_test_coverage,
                    total_branches_with_coverage=total_branches_with_test_coverage
                ))
    
    return file_suspiciousness


def launch_dashboard(report_file: str = "report.json", 
                    port: int = 8501, 
                    auto_open: bool = True) -> None:
    """Launch the dashboard."""
    import subprocess
    import sys
    
    # Set environment variable for the report file
    os.environ['PYFAULT_REPORT_FILE'] = report_file
    
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(Path(__file__)),
        "--server.port", str(port)
    ]
    
    if not auto_open:
        cmd.extend(["--server.headless", "true"])
    
    print(f"Starting PyFault Dashboard on port {port}")
    print(f"Report file: {report_file}")
    
    subprocess.run(cmd)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="PyFault Dashboard",
        page_icon="🔍",
        layout="wide"
    )
    
    st.title("PyFault Dashboard")
    st.markdown("Fault Localization Results Visualization")
    
    # Initialize session state
    if 'data' not in st.session_state:
        st.session_state.data = None
    if 'project_root' not in st.session_state:
        st.session_state.project_root = None
    
    # Auto-load report file
    if st.session_state.data is None:
        # Try environment variable first (from CLI)
        report_file = os.environ.get('PYFAULT_REPORT_FILE', 'report.json')
        
        try:
            with open(report_file) as f:
                st.session_state.data = json.load(f)
        except FileNotFoundError:
            st.error(f"Report file not found: {report_file}")
            st.info("Please ensure report.json exists in the current directory or specify the correct path via CLI")
            return
        except Exception as e:
            st.error(f"Error loading report file: {e}")
            return
    
    # Data is loaded, show main dashboard
    data = st.session_state.data
    
    # Formula selection
    formulas = data.get('totals', {}).get('sbfl_formulas', [])
    if not formulas:
        st.error("No formulas found in report")
        return
    
    selected_formula = st.selectbox("SBFL Formula", formulas)
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Overview", "Source Code", "Coverage Matrix", "Treemap", "Sunburst"
    ])
    
    with tab1:
        show_overview(data, selected_formula)
    
    with tab2:
        show_source_code(data, selected_formula)
    
    with tab3:
        show_coverage_matrix(data)
    
    with tab4:
        show_treemap_tab(data, selected_formula)
    
    with tab5:
        show_sunburst(data, selected_formula)


def show_overview(data: Dict[str, Any], formula: str):
    """Show comprehensive overview with key metrics for fault localization."""
    st.header("Fault Localization Overview")
    
    # Calculate formula statistics once (cached)
    formula_stats = calculate_formula_statistics(data, formula)
    
    # Extract main sections from report
    meta = data.get('meta', {})
    totals = data.get('totals', {})
    test_stats = totals.get('test_statistics', {})
    analysis_stats = totals.get('analysis_statistics', {})
    files_data = data.get('files', {})
    
    # === TEST EXECUTION SUMMARY ===
    st.subheader("Test Execution Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_tests = test_stats.get('total_tests', 0)
        st.metric(
            "Total Tests", 
            total_tests,
            help="Total number of tests in the test suite"
        )
    
    with col2:
        passed_tests = test_stats.get('passed_tests', 0)
        pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
        st.metric(
            "Passed Tests", 
            passed_tests,
            delta=f"{pass_rate:.1f}%",
            help="Number and percentage of passing tests"
        )
    
    with col3:
        failed_tests = test_stats.get('failed_tests', 0)
        fail_rate = (failed_tests / total_tests * 100) if total_tests > 0 else 0
        st.metric(
            "Failed Tests", 
            failed_tests,
            delta=f"{fail_rate:.1f}%",
            delta_color="inverse",
            help="Number and percentage of failing tests (key for FL)"
        )
    
    with col4:
        skipped_tests = test_stats.get('skipped_tests', 0)
        skip_rate = (skipped_tests / total_tests * 100) if total_tests > 0 else 0
        st.metric(
            "Skipped Tests", 
            skipped_tests,
            delta=f"{skip_rate:.1f}%",
            help="Number and percentage of skipped tests"
        )
    
    # Test quality indicators
    if failed_tests > 0:
        if failed_tests >= 5:
            st.success("✅ Good test failure count for fault localization")
        elif failed_tests >= 2:
            st.warning("⚠️ Moderate test failure count - FL may be less precise")
        else:
            st.warning("⚠️ Low test failure count - FL effectiveness may be limited")
    else:
        st.error("❌ No failing tests - fault localization cannot be performed")
    
    st.divider()
    
    # === CODE COVERAGE ANALYSIS ===
    st.subheader("Code Coverage Analysis")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Statement coverage
        covered_lines = totals.get('covered_lines', 0)
        total_statements = totals.get('num_statements', 0)
        coverage_percent = totals.get('percent_covered', 0.0)
        
        st.metric(
            "Statement Coverage", 
            f"{coverage_percent:.1f}%",
            delta=f"{covered_lines}/{total_statements} lines",
            help="Percentage of code lines executed by tests"
        )
        
        # Coverage quality assessment
        if coverage_percent >= 70:
            st.success("✅ High coverage - good for fault localization")
        elif coverage_percent >= 50:
            st.warning("⚠️ Moderate coverage - FL may miss some faults")
        else:
            st.error("❌ Low coverage - fault localization effectiveness limited")
    
    with col2:
        # Branch coverage
        covered_branches = totals.get('covered_branches', 0)
        total_branches = totals.get('num_branches', 0)
        branch_coverage = (covered_branches / total_branches * 100) if total_branches > 0 else 0
        
        st.metric(
            "Branch Coverage", 
            f"{branch_coverage:.1f}%",
            delta=f"{covered_branches}/{total_branches} branches",
            help="Percentage of code branches executed by tests"
        )
        
        partial_branches = totals.get('num_partial_branches', 0)
        if partial_branches > 0:
            st.info(f"ℹ️ {partial_branches} partially covered branches")
    
    # === FILE-BY-FILE COVERAGE TABLE ===
    st.subheader("File-by-File Coverage Details")
    
    # Build coverage data for each file
    file_coverage_data = []
    for file_path, file_data in files_data.items():
        summary = file_data.get('summary', {})
        covered_branches = summary.get('covered_branches', 0)
        total_branches = summary.get('num_branches', 0)
        branch_coverage = (covered_branches / total_branches * 100) if total_branches > 0 else 0
        file_coverage_data.append({
            'File': file_path,
            'Line Coverage': round(summary.get('percent_covered', 0.0), 1),
            'Covered Lines': summary.get('covered_lines', 0),
            'Total Statements': summary.get('num_statements', 0),
            'Branch Coverage': round(branch_coverage, 1),
            'Covered Branches': covered_branches,
            'Total Branches': total_branches,
            'Partial Branches': summary.get('num_partial_branches', 0)
        })
    
    if file_coverage_data:
        import pandas as pd
        coverage_df = pd.DataFrame(file_coverage_data)
        
        # Sort by coverage percentage descending
        coverage_df = coverage_df.sort_values('Line Coverage', ascending=False)

        # Display coverage table
        st.dataframe(
            coverage_df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "File": st.column_config.TextColumn("File"),
                "Line Coverage": st.column_config.ProgressColumn(
                    "Line Coverage",
                    help="Percentage of statements covered by tests",
                    min_value=0,
                    max_value=100,
                    format="%.1f%%"
                ),
                "Covered Lines": st.column_config.NumberColumn(
                    "Covered Lines",
                    help="Number of lines covered by tests"
                ),
                "Total Statements": st.column_config.NumberColumn(
                    "Total Statements",
                    help="Total number of executable statements"
                ),
                "Branch Coverage": st.column_config.ProgressColumn(
                    "Branch Coverage",
                    help="Percentage of branches covered by tests",
                    min_value=0,
                    max_value=100,
                    format="%.1f%%"
                ),
                "Covered Branches": st.column_config.NumberColumn(
                    "Covered Branches",
                    help="Number of branches covered by tests"
                ),
                "Total Branches": st.column_config.NumberColumn(
                    "Total Branches",
                    help="Total number of conditional branches"
                ),
                "Partial Branches": st.column_config.NumberColumn(
                    "Partial Branches",
                    help="Number of partially covered branches"
                )
            }
        )
        
        # Coverage summary statistics
        col1, col2, col3 = st.columns(3)
        with col1:
            avg_coverage = coverage_df['Line Coverage'].mean()
            st.metric("Average Line Coverage", f"{avg_coverage:.1f}%")
        with col2:
            high_coverage_files = len(coverage_df[coverage_df['Line Coverage'] >= 80])
            st.metric("Files with High Line Coverage (≥80%)", high_coverage_files)
        with col3:
            low_coverage_files = len(coverage_df[coverage_df['Line Coverage'] < 50])
            st.metric("Files with Low Line Coverage (<50%)", low_coverage_files)

    st.divider()
    
    # === FAULT LOCALIZATION READINESS ===
    st.subheader("Fault Localization Analysis")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        files_analyzed = analysis_stats.get('files_analyzed', 0)
        st.metric(
            "Files Analyzed", 
            files_analyzed,
            help="Number of source files included in analysis"
        )
    
    with col2:
        lines_with_scores = analysis_stats.get('total_lines_with_scores', 0)
        st.metric(
            "Lines with FL Scores", 
            lines_with_scores,
            help="Number of code lines with suspiciousness scores"
        )
    
    with col3:
        formulas_available = len(totals.get('sbfl_formulas', []))
        st.metric(
            "SBFL Formulas", 
            formulas_available,
            help="Number of available suspiciousness formulas"
        )
    
    # Show available formulas
    formulas = totals.get('sbfl_formulas', [])
    if formulas:
        st.write("**Available Formulas:**", ", ".join(f"`{f}`" for f in formulas))
    
    # Calculate and show top suspicious files preview using cached data
    st.divider()
    st.subheader("Most Suspicious Files")
    
    if not formula_stats.all_scores:
        st.warning("No suspiciousness data available for this formula")
        return
    
    # Add threshold control for suspicious lines (normalized)
    col1, col2 = st.columns([1, 3])
    with col1:
        st.write(f"**{formula.title()} Range:**")
        st.write(f"Min: {formula_stats.min_score:.3f}")
        st.write(f"Max: {formula_stats.max_score:.3f}")
        
        suspicious_threshold = st.slider(
            "Suspiciousness Threshold",
            min_value=0.0,
            max_value=1.0,
            value=0.5,
            step=0.1,
            key="suspicious_threshold",
            help="Normalized threshold (0=min, 1=max) for considering lines suspicious"
        )
        
        # Convert normalized threshold to actual value using cached stats
        actual_threshold = formula_stats.min_score + (suspicious_threshold * formula_stats.range_score)
        st.write(f"**Actual threshold:** {actual_threshold:.3f}")
    
    # Calculate suspicious files with the specific threshold using cached data
    file_suspiciousness = calculate_file_suspiciousness_with_threshold(
        data, formula, formula_stats, actual_threshold
    )
    
    # Create sortable dataframe
    if file_suspiciousness:
        df = pd.DataFrame([f._asdict() for f in file_suspiciousness])
        
        # Sort by Max Score (priority), then by Suspicious Statements count
        df = df.sort_values(['max_score', 'suspicious_statements'], ascending=[False, False])
        
        # Calculate maximums for progress bars
        max_max_score = df['max_score'].max()
        max_avg_score = df['avg_score'].max()
        
        # Display as interactive table with progress bars
        st.dataframe(
            df[['file_path', 'max_score', 'avg_score', 'suspicious_statements', 
                'suspicious_statements_pct', 'suspicious_branches', 'suspicious_branches_pct']],
            use_container_width=True,
            hide_index=True,
            column_config={
                "file_path": st.column_config.TextColumn("File"),
                "max_score": st.column_config.ProgressColumn(
                    "Max Score",
                    help="Maximum suspiciousness score in the file",
                    min_value=0,
                    max_value=max_max_score,
                    format="%.3f"
                ),
                "avg_score": st.column_config.ProgressColumn(
                    "Avg Score", 
                    help="Average suspiciousness score in the file",
                    min_value=0,
                    max_value=max_avg_score,
                    format="%.3f"
                ),
                "suspicious_statements": st.column_config.NumberColumn(
                    "Suspicious Statements",
                    help="Count of suspicious statements",
                    min_value=0
                ),
                "suspicious_statements_pct": st.column_config.ProgressColumn(
                    "Suspicious Statements (%)",
                    help="Percentage of suspicious statements (Suspicious Statements / Covered Statements)",
                    min_value=0,
                    max_value=100,
                    format="%.1f%%"
                ),
                "suspicious_branches": st.column_config.NumberColumn(
                    "Suspicious Branches",
                    help="Count of suspicious branches",
                    min_value=0
                ),
                "suspicious_branches_pct": st.column_config.ProgressColumn(
                    "Suspicious Branches (%)",
                    help="Percentage of suspicious branches (Suspicious Branches / Covered Branches)",
                    min_value=0,
                    max_value=100,
                    format="%.1f%%"
                )
            }
        )
        
        with col2:
            st.caption(f"Scores normalized to 0-1 range. Files sorted by Max Score, then by Suspicious Statements (≥{actual_threshold:.3f}). Click column headers to re-sort.")
            if len(df) > 0:
                st.info(f"Top priority: **{df.iloc[0]['file_path']}** (Normalized Max Score: {df.iloc[0]['max_score']}, {df.iloc[0]['suspicious_statements']} suspicious statements)")
    
    
    # Recommendations
    st.divider()
    st.subheader("Recommendations")
    
    recommendations = []
    
    if failed_tests < 2:
        recommendations.append("**Critical**: Add more failing tests to improve fault localization precision")
    
    if coverage_percent < 50:
        recommendations.append("**Important**: Increase test coverage to improve fault detection")
    
    if lines_with_scores < 100:
        recommendations.append("**Suggestion**: More code execution needed for better analysis")
    
    if file_suspiciousness:
        # Use same prioritization as table: sort by Max Score, then by Suspicious Statements Count
        sorted_files = sorted(file_suspiciousness, key=lambda x: (x.max_score, x.suspicious_statements), reverse=True)
        top_file = sorted_files[0]
        recommendations.append(f"**Priority**: Focus on `{top_file.file_path}` (Max Score: {top_file.max_score:.3f}, {top_file.suspicious_statements} suspicious statements)")
    
    if not recommendations:
        recommendations.append("**Good**: Project setup looks optimal for fault localization")
    
    for i, rec in enumerate(recommendations, 1):
        st.write(f"{i}. {rec}")


def show_treemap_tab(data: Dict[str, Any], formula: str):
    """Show dedicated treemap tab with detailed hierarchical view."""
    st.header("Hierarchical Treemap")
    
    # Calculate formula statistics once (cached)
    formula_stats = calculate_formula_statistics(data, formula)
    
    # Add threshold control
    col1, col2 = st.columns([1, 3])
    with col1:
        min_score = st.slider(
            "Minimum Suspiciousness Score",
            min_value=0.0,
            max_value=1.0,
            value=0.0,
            step=0.05,
            help="Filter out elements with suspiciousness score below this threshold"
        )
    
    hierarchy_data = build_hierarchical_data_cached(data, formula, formula_stats, min_score)
    
    if not hierarchy_data or len(hierarchy_data['labels']) <= 1:
        st.warning(f"No hierarchical data available with minimum score {min_score:.2f}")
        return
    
    # Create treemap with hierarchical structure
    fig = go.Figure(go.Treemap(
        labels=hierarchy_data['labels'],
        parents=hierarchy_data['parents'],
        values=hierarchy_data['values'],
        textinfo="label+value",
        marker=dict(
            colors=hierarchy_data['colors'],
            colorscale='Reds',  # Scala da bianco a rosso
            colorbar=dict(title="Suspiciousness Score"),
            line=dict(width=1),
            cmid=0.5
        ),
        hovertemplate="<b>%{label}</b><br>%{customdata}<br>Score: %{color:.3f}<extra></extra>",
        customdata=hierarchy_data['hover_info'],
        maxdepth=5  # Allow deeper nesting in dedicated view
    ))
    
    fig.update_layout(
        height=700,
        title=f"Project Structure - Hierarchical Treemap ({formula.title()})",
        margin=dict(t=50, l=0, r=0, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Add statistics
    with col2:
        st.markdown(f"""
        **Statistics:**
        - Total elements shown: {len(hierarchy_data['labels']) - 1}
        - Average suspiciousness: {np.mean(hierarchy_data['colors']):.3f}
        - Max suspiciousness: {max(hierarchy_data['colors']):.3f}
        """)
    
    # Add explanation
    st.markdown("""
    **Hierarchical Structure:**
    - **Packages/Directories**: Top-level containers organizing related files
    - **Python Files (.py)**: Individual source code files
    - **Classes**: Object-oriented code structures within files
    - **Functions/Methods**: Individual code functions and class methods
    
    **Visualization:**
    - **Size**: Proportional to number of lines with coverage data
    - **Color**: Suspiciousness score (blue = low, red = high)
    - **Nesting**: Shows the containment relationship (package → file → class → method)
    
    **Interaction**: Click on any section to drill down into that part of the hierarchy.
    """)


def show_treemap(data: Dict[str, Any], formula: str):
    """Create hierarchical treemap visualization based on Python project structure."""
    # Calculate formula statistics once (cached)
    formula_stats = calculate_formula_statistics(data, formula)
    
    hierarchy_data = build_hierarchical_data_cached(data, formula, formula_stats, min_score=0.05)  # Small threshold for overview
    
    if not hierarchy_data or len(hierarchy_data['labels']) <= 1:
        st.warning("No hierarchical data available")
        return
    
    # Create treemap with hierarchical structure
    fig = go.Figure(go.Treemap(
        labels=hierarchy_data['labels'],
        parents=hierarchy_data['parents'],
        values=hierarchy_data['values'],
        textinfo="label+value",
        marker=dict(
            colors=hierarchy_data['colors'],
            colorscale='Reds',  # Scala da bianco a rosso
            colorbar=dict(title="Suspiciousness Score"),
            line=dict(width=1),
            cmid=0.5
        ),
        hovertemplate="<b>%{label}</b><br>%{customdata}<br>Score: %{color:.3f}<extra></extra>",
        customdata=hierarchy_data['hover_info'],
        maxdepth=4  # Package -> File -> Class -> Function/Method
    ))
    
    fig.update_layout(
        height=600,
        title="Project Structure - Hierarchical View",
        margin=dict(t=50, l=0, r=0, b=0)
    )
    
    st.plotly_chart(fig, use_container_width=True)


def show_ranking_table(susp_data: List[Dict]):
    """Show ranking table of suspicious lines."""
    if not susp_data:
        return
    
    df_data = []
    for i, item in enumerate(susp_data, 1):
        df_data.append({
            'Rank': i,
            'File': item['file'],
            'Line': item['line'],
            'Score': item['score']
        })
    
    df = pd.DataFrame(df_data)
    
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Score": st.column_config.ProgressColumn(
                "Score",
                min_value=0.0,
                max_value=1.0,
                format="%.3f"
            )
        }
    )


def get_most_suspicious_file(data: Dict[str, Any], formula: str) -> Optional[str]:
    """Get the file with the highest suspiciousness score for the given formula."""
    # Use cached version for performance
    formula_stats = calculate_formula_statistics(data, formula)
    return get_most_suspicious_file_cached(data, formula, formula_stats)


def show_source_code(data: Dict[str, Any], formula: str):
    """Show source code with suspiciousness highlighting."""
    st.header("Source Code")

    files_data = data.get('files', {})
    if not files_data:
        st.warning("No file data available")
        return
    
    # Project root selection
    col1, col2 = st.columns([3, 1])
    
    with col1:
        # Display current project root
        st.info(f"📁 Project root: `{st.session_state.project_root or os.getcwd()}`")
    with col2:
        # Browse button for project root
        if st.button("📁 Browse Project Root", help="Select the root directory of your project"):
            # Open native file dialog
            selected_directory = select_directory_with_dialog()
            if selected_directory:
                st.session_state.project_root = selected_directory
                st.rerun()
    
    st.divider()
    
    # File selection with most suspicious file as default
    file_paths = list(files_data.keys())
    most_suspicious_file = get_most_suspicious_file(data, formula)
    
    # Set default index to the most suspicious file if found
    default_index = 0
    if most_suspicious_file and most_suspicious_file in file_paths:
        default_index = file_paths.index(most_suspicious_file)
    
    selected_file = st.selectbox("Select File", file_paths, index=default_index)
    
    if selected_file:
        show_file_with_highlighting(files_data[selected_file], selected_file, formula)


def show_file_with_highlighting(file_data: Dict, file_path: str, formula: str):
    """Show file content with line highlighting based on suspiciousness."""
    suspiciousness = file_data.get('suspiciousness', {})

    if not suspiciousness:
        st.warning("No suspiciousness data for this file")
        return

    # Determine the actual file path to read
    actual_file_path = file_path
    
    # If project root is set, try to construct the full path
    if st.session_state.project_root:
        # Try different combinations to find the file
        potential_paths = [
            os.path.join(st.session_state.project_root, file_path),  # Direct join
            os.path.join(st.session_state.project_root, file_path.lstrip('./')),  # Remove leading ./
            os.path.join(st.session_state.project_root, file_path.lstrip('/\\')),  # Remove leading slashes
        ]
        
        # If file_path is already absolute, also try it as-is
        if os.path.isabs(file_path):
            potential_paths.insert(0, file_path)
        
        # Find the first path that exists
        for path in potential_paths:
            if os.path.exists(path):
                actual_file_path = path
                break
    
    # Try to read the actual file content
    try:
        with open(actual_file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            
    except FileNotFoundError:
        st.error(f"❌ Could not find file: `{file_path}`")
        if st.session_state.project_root:
            st.error(f"🔍 Searched in project root: `{st.session_state.project_root}`")
            # Show tried paths for debugging
            with st.expander("Show attempted paths"):
                potential_paths = [
                    os.path.join(st.session_state.project_root, file_path),
                    os.path.join(st.session_state.project_root, file_path.lstrip('./')),
                    os.path.join(st.session_state.project_root, file_path.lstrip('/\\')),
                ]
                for i, path in enumerate(potential_paths, 1):
                    st.code(f"{i}. {path}")
        else:
            st.info("💡 Try setting a project root directory using the 'Browse Project Root' button above.")
        return
    except Exception as e:
        st.error(f"❌ Error reading file: {str(e)}")
        return

    st.subheader(f"File: {file_path}")

    # Create highlighted code display with preserved indentation
    highlighted_lines = []
    for line_num, line_content in enumerate(lines, 1):
        line_str = str(line_num)
        # Escape HTML special characters and preserve indentation
        safe_content = line_content.rstrip('\n').replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        # Replace leading spaces/tabs with &nbsp; for indentation
        leading_spaces = len(line_content) - len(line_content.lstrip(' '))
        leading_tabs = len(line_content) - len(line_content.lstrip('\t'))
        indent = '&nbsp;' * leading_spaces + ('&nbsp;&nbsp;&nbsp;&nbsp;' * leading_tabs)
        stripped_content = safe_content.lstrip(' \t')
        code_html = f"{indent}{stripped_content}"
        if line_str in suspiciousness:
            score = suspiciousness[line_str].get(formula, 0)
            # Color intensity based on suspiciousness
            if score > 0.8:
                color = "#ff4444"
            elif score > 0.5:
                color = "#ff8844"
            elif score > 0.2:
                color = "#ffbb44"
            else:
                color = "#ffffff"

            highlighted_lines.append(
                f'<div style="background-color: {color}; padding: 2px; margin: 1px;">'
                f'<span style="color: #666; width: 40px; display: inline-block;">{line_num:3d}</span> '
                f'<span style="color: #000;">{code_html}</span> '
                f'<span style="color: #999; float: right;">({score:.3f})</span>'
                f'</div>'
            )
        else:
            highlighted_lines.append(
                f'<div style="padding: 2px; margin: 1px;">'
                f'<span style="color: #666; width: 40px; display: inline-block;">{line_num:3d}</span> '
                f'<span style="color: #000;">{code_html}</span>'
                f'</div>'
            )

    st.markdown(
        f'<div style="font-family: monospace; font-size: 12px; background-color: rgba(240, 242, 246, 0.5); padding: 15px; border-radius: 8px; border: 1px solid rgba(49, 51, 63, 0.2);">'
        + ''.join(highlighted_lines) +
        '</div>',
        unsafe_allow_html=True
    )


def show_coverage_matrix(data: Dict[str, Any]):
    """Show enhanced coverage matrix visualization with interactive controls."""
    st.header("Coverage Matrix")
    
    # Extract test and coverage information
    tests_info = data.get('tests', {})
    files_data = data.get('files', {})
    
    if not tests_info or not files_data:
        st.warning("No test or coverage data available")
        return
    
    # Controls row
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        view_mode = st.selectbox(
            "View Mode",
            ["Detailed Lines", "File Summary", "Test Clustering"],
            help="Choose how to display the coverage data"
        )
    
    with col2:
        test_filter = st.selectbox(
            "Test Filter",
            ["All Tests", "Failed Tests Only", "Passed Tests Only"],
            help="Filter tests by their execution result"
        )
    
    with col3:
        max_rows = st.slider("Max Rows", 10, 100, 50, help="Maximum number of rows to display")
    
    with col4:
        max_cols = st.slider("Max Columns", 5, 50, 20, help="Maximum number of columns to display")
    
    # Build enhanced coverage matrix with test status and suspiciousness
    passed_tests = set(tests_info.get('passed', []))
    failed_tests = set(tests_info.get('failed', []))
    all_lines = []
    
    for file_path, file_data in files_data.items():
        contexts = file_data.get('contexts', {})
        suspiciousness = file_data.get('suspiciousness', {})
        
        for line_num, test_contexts in contexts.items():
            for context in test_contexts:
                if '::' in context:  # It's a test context
                    test_name = context.split('|')[0]  # Remove |run suffix
                    
                    # Determine test status
                    test_status = "unknown"
                    if test_name in passed_tests:
                        test_status = "passed"
                    elif test_name in failed_tests:
                        test_status = "failed"
                    
                    # Get suspiciousness score (use first available formula)
                    susp_score = 0.0
                    if line_num in suspiciousness:
                        scores = suspiciousness[line_num]
                        if scores:
                            susp_score = float(list(scores.values())[0])
                    
                    all_lines.append({
                        'file': file_path,
                        'line': int(line_num),
                        'test': test_name,
                        'test_status': test_status,
                        'covered': 1,
                        'suspiciousness': susp_score,
                        'file_line': f"{file_path}:{line_num}"
                    })
    
    if not all_lines:
        st.warning("No coverage data found")
        return
    
    # Apply test filter
    df = pd.DataFrame(all_lines)
    if test_filter == "Failed Tests Only":
        df = df[df['test_status'] == 'failed']
    elif test_filter == "Passed Tests Only":
        df = df[df['test_status'] == 'passed']
    
    if df.empty:
        st.warning("No coverage data to display with current filters")
        return
    
    # Show different views based on mode
    if view_mode == "Detailed Lines":
        show_detailed_coverage_heatmap(df, max_rows, max_cols)
    elif view_mode == "File Summary":
        show_file_summary_heatmap(df, max_rows, max_cols)
    elif view_mode == "Test Clustering":
        show_test_clustering_heatmap(df, max_rows, max_cols)
    
    # Show coverage statistics
    show_coverage_statistics(df, tests_info)


def show_detailed_coverage_heatmap(df: pd.DataFrame, max_rows: int, max_cols: int):
    """Show detailed line-by-line coverage heatmap with enhanced features."""
    st.subheader("Detailed Coverage Heatmap")
    
    # Create pivot table with suspiciousness as values for coloring
    pivot_coverage = df.pivot_table(
        index=['file', 'line'], 
        columns='test', 
        values='covered', 
        fill_value=0
    )
    
    pivot_suspiciousness = df.pivot_table(
        index=['file', 'line'], 
        columns='test', 
        values='suspiciousness', 
        fill_value=0,
        aggfunc='mean'  # Average if multiple entries
    )
    
    if pivot_coverage.empty:
        st.warning("No pivot data to display")
        return
    
    # Sort by suspiciousness (lines with highest average suspiciousness first)
    avg_susp_per_line = pivot_suspiciousness.mean(axis=1).sort_values(ascending=False)
    sorted_indices = avg_susp_per_line.index
    
    # Limit and sort data
    display_coverage = pivot_coverage.loc[sorted_indices].iloc[:max_rows, :max_cols]
    display_suspiciousness = pivot_suspiciousness.loc[sorted_indices].iloc[:max_rows, :max_cols]
    
    # Create enhanced heatmap
    hover_text = []
    for i in range(len(display_coverage)):
        hover_row = []
        for j in range(len(display_coverage.columns)):
            line_info = display_coverage.index[i]
            test_name = display_coverage.columns[j]
            covered = display_coverage.iloc[i, j]
            susp = display_suspiciousness.iloc[i, j]
            
            hover_row.append(
                f"File: {line_info[0]}<br>"
                f"Line: {line_info[1]}<br>"
                f"Test: {test_name}<br>"
                f"Covered: {'Yes' if covered else 'No'}<br>"
                f"Suspiciousness: {susp:.3f}"
            )
        hover_text.append(hover_row)
    
    # Use suspiciousness for coloring, but show coverage in hover
    fig = go.Figure(data=go.Heatmap(
        z=display_suspiciousness.values,
        x=display_coverage.columns,
        y=[f"{idx[0]}:{idx[1]}" for idx in display_coverage.index],
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_text,
        colorscale='RdYlBu_r',  # Red for high suspiciousness, blue for low
        colorbar=dict(title="Suspiciousness Score")
    ))
    
    fig.update_layout(
        height=max(400, len(display_coverage) * 25),
        xaxis_title="Tests",
        yaxis_title="File:Line",
        title="Coverage Matrix (colored by Suspiciousness, sorted by priority)"
    )
    
    fig.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig, use_container_width=True)
    
    if len(pivot_coverage) > max_rows or len(pivot_coverage.columns) > max_cols:
        st.info(f"Showing top {max_rows} most suspicious lines and {max_cols} tests. Total: {len(pivot_coverage)} lines, {len(pivot_coverage.columns)} tests")


def show_file_summary_heatmap(df: pd.DataFrame, max_rows: int, max_cols: int):
    """Show file-level aggregated coverage heatmap."""
    st.subheader("File-Level Coverage Summary")
    
    # Aggregate by file
    file_summary = df.groupby(['file', 'test']).agg({
        'covered': 'sum',  # Number of lines covered
        'suspiciousness': 'mean',  # Average suspiciousness
        'test_status': 'first'  # Test status
    }).reset_index()
    
    # Create pivot for coverage counts
    pivot_coverage = file_summary.pivot_table(
        index='file',
        columns='test',
        values='covered',
        fill_value=0
    )
    
    pivot_suspiciousness = file_summary.pivot_table(
        index='file',
        columns='test',
        values='suspiciousness',
        fill_value=0
    )
    
    # Sort files by total suspiciousness
    file_priority = pivot_suspiciousness.sum(axis=1).sort_values(ascending=False)
    sorted_files = file_priority.index
    
    display_coverage = pivot_coverage.loc[sorted_files].iloc[:max_rows, :max_cols]
    display_suspiciousness = pivot_suspiciousness.loc[sorted_files].iloc[:max_rows, :max_cols]
    
    # Create hover information
    hover_text = []
    for i in range(len(display_coverage)):
        hover_row = []
        for j in range(len(display_coverage.columns)):
            file_name = display_coverage.index[i]
            test_name = display_coverage.columns[j]
            lines_covered = display_coverage.iloc[i, j]
            avg_susp = display_suspiciousness.iloc[i, j]
            
            hover_row.append(
                f"File: {file_name}<br>"
                f"Test: {test_name}<br>"
                f"Lines Covered: {lines_covered}<br>"
                f"Avg Suspiciousness: {avg_susp:.3f}"
            )
        hover_text.append(hover_row)
    
    fig = go.Figure(data=go.Heatmap(
        z=display_coverage.values,
        x=display_coverage.columns,
        y=display_coverage.index,
        hovertemplate='%{customdata}<extra></extra>',
        customdata=hover_text,
        colorscale='Blues',
        colorbar=dict(title="Lines Covered")
    ))
    
    fig.update_layout(
        height=max(300, len(display_coverage) * 30),
        xaxis_title="Tests",
        yaxis_title="Files",
        title="File-Level Coverage (number of lines covered per test)"
    )
    
    fig.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show file statistics
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Top Files by Coverage:**")
        file_total_coverage = display_coverage.sum(axis=1).sort_values(ascending=False)
        for i, (file, coverage) in enumerate(file_total_coverage.head(5).items(), 1):
            st.write(f"{i}. `{file}`: {coverage} lines")
    
    with col2:
        st.write("**Top Files by Suspiciousness:**")
        file_total_susp = display_suspiciousness.sum(axis=1).sort_values(ascending=False)
        for i, (file, susp) in enumerate(file_total_susp.head(5).items(), 1):
            st.write(f"{i}. `{file}`: {susp:.3f} avg score")


def show_test_clustering_heatmap(df: pd.DataFrame, max_rows: int, max_cols: int):
    """Show test clustering based on coverage patterns."""
    st.subheader("Test Clustering by Coverage Patterns")
    
    # Create test-line matrix
    test_line_matrix = df.pivot_table(
        index='test',
        columns='file_line',
        values='covered',
        fill_value=0
    )
    
    if test_line_matrix.empty:
        st.warning("No data for clustering")
        return
    
    # Simple clustering by test status and coverage similarity
    passed_tests = df[df['test_status'] == 'passed']['test'].unique()
    failed_tests = df[df['test_status'] == 'failed']['test'].unique()
    
    # Separate and sort tests
    passed_matrix = test_line_matrix.loc[test_line_matrix.index.isin(passed_tests)]
    failed_matrix = test_line_matrix.loc[test_line_matrix.index.isin(failed_tests)]
    
    # Combine with failed tests first (more important for FL)
    if not failed_matrix.empty and not passed_matrix.empty:
        ordered_matrix = pd.concat([failed_matrix, passed_matrix])
    elif not failed_matrix.empty:
        ordered_matrix = failed_matrix
    else:
        ordered_matrix = passed_matrix
    
    # Limit size
    display_matrix = ordered_matrix.iloc[:max_cols, :max_rows]  # Swap for tests as rows
    
    # Create test status colors
    test_colors = []
    for test in display_matrix.index:
        if test in failed_tests:
            test_colors.append("Failed")
        else:
            test_colors.append("Passed")
    
    fig = go.Figure(data=go.Heatmap(
        z=display_matrix.values,
        x=display_matrix.columns,
        y=[f"{test} ({status})" for test, status in zip(display_matrix.index, test_colors)],
        colorscale='RdBu_r',
        colorbar=dict(title="Coverage")
    ))
    
    fig.update_layout(
        height=max(400, len(display_matrix) * 20),
        xaxis_title="File:Line",
        yaxis_title="Tests (grouped by status)",
        title="Test Coverage Patterns (Failed tests first)"
    )
    
    fig.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Show clustering insights
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Failed Tests Coverage:**")
        if not failed_matrix.empty:
            failed_coverage = failed_matrix.sum(axis=1).sort_values(ascending=False)
            for i, (test, coverage) in enumerate(failed_coverage.head(5).items(), 1):
                st.write(f"{i}. `{test}`: {coverage} lines")
        else:
            st.write("No failed tests found")
    
    with col2:
        st.write("**Passed Tests Coverage:**")
        if not passed_matrix.empty:
            passed_coverage = passed_matrix.sum(axis=1).sort_values(ascending=False)
            for i, (test, coverage) in enumerate(passed_coverage.head(5).items(), 1):
                st.write(f"{i}. `{test}`: {coverage} lines")
        else:
            st.write("No passed tests found")


def show_coverage_statistics(df: pd.DataFrame, tests_info: Dict[str, Any]):
    """Show comprehensive coverage statistics."""
    st.divider()
    st.subheader("Coverage Statistics")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        total_lines = len(df['file_line'].unique())
        st.metric("Total Lines Covered", total_lines)
    
    with col2:
        total_tests = len(df['test'].unique())
        st.metric("Total Tests", total_tests)
    
    with col3:
        avg_coverage_per_test = df.groupby('test')['line'].count().mean()
        st.metric("Avg Lines per Test", f"{avg_coverage_per_test:.1f}")
    
    with col4:
        avg_tests_per_line = df.groupby('file_line')['test'].count().mean()
        st.metric("Avg Tests per Line", f"{avg_tests_per_line:.1f}")
    
    # Coverage distribution chart
    col1, col2 = st.columns(2)
    
    with col1:
        # Test coverage distribution
        test_coverage = df.groupby('test')['line'].count()
        fig1 = px.histogram(
            x=test_coverage.values,
            nbins=20,
            title="Distribution of Lines Covered per Test",
            labels={'x': 'Lines Covered', 'y': 'Number of Tests'}
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with col2:
        # Line coverage distribution
        line_coverage = df.groupby('file_line')['test'].count()
        fig2 = px.histogram(
            x=line_coverage.values,
            nbins=20,
            title="Distribution of Tests per Line",
            labels={'x': 'Tests Covering Line', 'y': 'Number of Lines'}
        )
        st.plotly_chart(fig2, use_container_width=True)


def show_sunburst(data: Dict[str, Any], formula: str):
    """Show sunburst visualization with hierarchical Python project structure."""
    st.header("Sunburst View")
    
    # Calculate formula statistics once (cached)
    formula_stats = calculate_formula_statistics(data, formula)
    
    # Add threshold control
    col1, col2 = st.columns([1, 3])
    with col1:
        min_score = st.slider(
            "Min Suspiciousness Score",
            min_value=0.0,
            max_value=1.0,
            value=0.05,
            step=0.05,
            key="sunburst_threshold",
            help="Filter out elements with suspiciousness score below this threshold"
        )
    
    hierarchy_data = build_hierarchical_data_cached(data, formula, formula_stats, min_score)
    
    if not hierarchy_data or len(hierarchy_data['labels']) <= 1:
        st.warning(f"No hierarchical data available with minimum score {min_score:.2f}")
        st.info("Try lowering the minimum score threshold")
        
        # Show fallback with very low threshold
        fallback_data = build_hierarchical_data_cached(data, formula, formula_stats, 0.0)
        if fallback_data and len(fallback_data['labels']) > 1:
            st.info(f"Available elements with threshold 0.0: {len(fallback_data['labels'])}")
        return
    
    # Fix small values that cause rendering issues
    fixed_values = [max(v, 5) for v in hierarchy_data['values']]
    
    # Create hierarchical sunburst
    try:
        fig = go.Figure(go.Sunburst(
            labels=hierarchy_data['labels'],
            parents=hierarchy_data['parents'],
            values=fixed_values,
            marker=dict(
                colors=hierarchy_data['colors'],
                colorscale='Reds',  # Scala da bianco a rosso
                colorbar=dict(title="Suspiciousness Score"),
                line=dict(width=2, color="white")
            ),
            hovertemplate="<b>%{label}</b><br>%{customdata}<br>Score: %{color:.3f}<extra></extra>",
            customdata=hierarchy_data['hover_info']
        ))
        
        fig.update_layout(
            height=700,
            title=f"Code Hierarchy - {formula.title()}",
            font_size=11,
            margin=dict(t=50, l=0, r=0, b=0)
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Add statistics
        with col2:
            if hierarchy_data['colors']:
                st.markdown(f"""
                **Statistics:**
                - Total elements shown: {len(hierarchy_data['labels']) - 1}
                - Average suspiciousness: {np.mean(hierarchy_data['colors']):.3f}
                - Max suspiciousness: {max(hierarchy_data['colors']):.3f}
                - Min suspiciousness: {min(hierarchy_data['colors']):.3f}
                """)
        
        # Add explanation
        st.markdown("""
        **Hierarchy Levels:**
        - **Center**: Project root
        - **Level 1**: Python files (.py)
        - **Level 2**: Classes within files
        - **Level 3**: Functions/Methods within classes
        
        **Color**: Indicates suspiciousness score (red = more suspicious)  
        **Size**: Proportional to number of lines with coverage data
        
        **Tip**: If the sunburst appears empty, try lowering the minimum score threshold.
        """)
        
    except Exception as e:
        st.error(f"Error creating sunburst: {e}")
        
        # Fallback to simple visualization
        st.subheader("Alternative View")
        susp_data = extract_suspiciousness_data(data, formula)
        
        df_data = []
        for item in susp_data[:15]:  # Top 15
            df_data.append({
                'Element': f"{item['file']}:{item['line']}",
                'Score': item['score']
            })
        
        if df_data:
            df = pd.DataFrame(df_data)
            fig_bar = px.bar(
                df, 
                x='Score', 
                y='Element', 
                orientation='h',
                title=f"Top Suspicious Elements - {formula.title()}",
                color='Score',
                color_continuous_scale='Reds'
            )
            fig_bar.update_layout(height=500)
            st.plotly_chart(fig_bar, use_container_width=True)


def extract_suspiciousness_data(data: Dict[str, Any], formula: str) -> List[Dict]:
    """Extract and sort suspiciousness data for given formula."""
    files_data = data.get('files', {})
    susp_data = []
    
    for file_path, file_data in files_data.items():
        suspiciousness = file_data.get('suspiciousness', {})
        for line_num, scores in suspiciousness.items():
            if formula in scores:
                susp_data.append({
                    'file': file_path,
                    'line': int(line_num),
                    'score': float(scores[formula])  # Ensure float
                })
    
    # Sort by score descending
    susp_data.sort(key=lambda x: x['score'], reverse=True)
    return susp_data


if __name__ == "__main__":
    main()

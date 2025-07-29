"""
Streamlit-based dashboard for PyFault results visualization.
"""

import os
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import numpy as np
from pathlib import Path
from typing import Optional, Dict, List, Any

from pyfault.core.fault_localizer import FaultLocalizer
from pyfault.reporters.csv_reporter import CSVReporter
from pyfault.reporters.json_reporter import JSONReporter
from pyfault.formulas import OchiaiFormula, TarantulaFormula, JaccardFormula, DStarFormula, Kulczynski2Formula


def launch_dashboard(data_source: Optional[str] = None, 
                    port: int = 8501, 
                    auto_open: bool = False) -> None:
    """Launch the Streamlit dashboard."""
    import subprocess
    import sys
    import os
    
    # Set environment variable for data source
    if data_source:
        os.environ['PYFAULT_DATA_SOURCE'] = str(data_source)
    
    # Prepare streamlit command
    cmd = [
        sys.executable, "-m", "streamlit", "run",
        str(Path(__file__)),
        "--server.port", str(port),
        "--server.headless", "true" if not auto_open else "false"
    ]
    
    if auto_open:
        cmd.extend(["--browser.serverAddress", "localhost"])
    
    print(f"🚀 Starting PyFault Dashboard on port {port}")
    print(f"📂 Data source: {data_source or 'None (upload required)'}")
    
    subprocess.run(cmd)


def main():
    """Main Streamlit application."""
    st.set_page_config(
        page_title="PyFault Dashboard",
        page_icon="🔍",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    st.title("🔍 PyFault - Fault Localization Dashboard")
    st.markdown("**Spectrum-Based Fault Localization Results Visualization**")
    
    # Check for pre-loaded data source
    preloaded_source = os.environ.get('PYFAULT_DATA_SOURCE')
    
    # Initialize session state for data persistence
    if 'loaded_data' not in st.session_state:
        st.session_state.loaded_data = None
    if 'data_source' not in st.session_state:
        st.session_state.data_source = None
    if 'csv_data' not in st.session_state:
        st.session_state.csv_data = None
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # File upload or use preloaded
        if preloaded_source and st.session_state.data_source != preloaded_source:
            source_path = Path(preloaded_source)
            if source_path.is_file():
                st.success(f"📁 Loaded file: {source_path.name}")
            else:
                st.success(f"📁 Loaded directory: {source_path.name}")
            st.session_state.data_source = preloaded_source
            # Load data
            try:
                st.session_state.loaded_data, st.session_state.csv_data = load_data(preloaded_source)
            except Exception as e:
                st.error(f"❌ Error loading preloaded data: {str(e)}")
                st.session_state.loaded_data = None
                st.session_state.csv_data = None
        else:
            uploaded_files = st.file_uploader(
                "Upload Results", 
                type=['json', 'csv'],
                accept_multiple_files=True,
                help="Upload PyFault JSON results or multiple CSV files"
            )
            
            if uploaded_files:
                # Check if it's a new set of files
                file_names = [f.name for f in uploaded_files]
                if st.session_state.data_source != str(file_names):
                    st.session_state.data_source = str(file_names)
                    
                    # Load data with progress indicator
                    with st.spinner("Loading and processing data..."):
                        try:
                            st.session_state.loaded_data, st.session_state.csv_data = load_data(uploaded_files)
                        except Exception as e:
                            st.error(f"❌ Error loading data: {str(e)}")
                            st.session_state.loaded_data = None
                            st.session_state.csv_data = None
        
        # Configuration controls (only show if data is loaded)
        if st.session_state.loaded_data is not None:
            data = st.session_state.loaded_data
            csv_data = st.session_state.csv_data
            
            # Validate data structure
            if not validate_dashboard_data(data):
                st.error("❌ Invalid data structure. Please check your input file.")
                st.session_state.loaded_data = None
                st.session_state.csv_data = None
                return
            
            st.success("✅ Data loaded successfully!")
            st.divider()
            
            # Formula selection
            available_formulas = list(data.get('formulas', {}).keys())
            selected_formula = st.selectbox(
                "🔬 SBFL Formula",
                available_formulas,
                help="Select the suspiciousness formula to visualize"
            )
            
            # Top N elements
            formula_scores = data.get('formulas', {}).get(selected_formula, [])
            max_elements = min(100, len(formula_scores))
            top_n = st.slider(
                "📊 Top N Elements", 
                5, max_elements, 
                min(20, max_elements),
                help="Number of top suspicious elements to display"
            )
            
            # Filtering options
            st.divider()
            st.subheader("🎯 Filters")
            
            min_score = st.slider(
                "Minimum Score", 
                0.0, 1.0, 0.0, 0.01,
                help="Show only elements with score above this threshold"
            )
            
            exclude_zero_scores = st.checkbox(
                "Exclude Zero Scores from Histogram", 
                value=False,
                help="Hide elements with score = 0 from the histogram (they will still appear in other views)"
            )
            
            # Store config in session state for main area
            st.session_state.config = {
                'selected_formula': selected_formula,
                'top_n': top_n,
                'min_score': min_score,
                'exclude_zero_scores': exclude_zero_scores
            }
            
            # Show CSV data info if available
            if csv_data:
                st.divider()
                st.subheader("📊 Additional Data")
                available_csv = list(csv_data.keys())
                st.write(f"Available CSV files: {', '.join(available_csv)}")
    
    # Main content area
    if st.session_state.loaded_data is None:
        display_welcome()
    else:
        # Display results in main area using session state config
        config = st.session_state.get('config', {})
        if config:
            display_results(
                st.session_state.loaded_data,
                st.session_state.csv_data,
                config['selected_formula'],
                config['top_n'],
                config['min_score'],
                config.get('exclude_zero_scores', False)
            )
        else:
            st.info("⚙️ Please configure the settings in the sidebar.")


@st.cache_data
def load_data_cached(data_source_info: str) -> Optional[Dict[str, Any]]:
    """Cached version of load_data to improve performance."""
    # This would need to be implemented based on the data source type
    # For now, redirect to the original function
    pass


def display_error_details(error: Exception):
    """Display detailed error information for debugging."""
    with st.expander("🔍 Error Details"):
        st.code(str(error))
        st.text("Stack trace:")
        import traceback
        st.code(traceback.format_exc())


def load_data(data_source) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Load data from file, directory, or uploaded content.
    
    Returns:
        Tuple of (json_data, csv_data) where:
        - json_data: Traditional JSON dashboard data
        - csv_data: Additional CSV data (coverage matrix, test results, etc.)
    """
    try:
        if isinstance(data_source, str):
            # File path or directory path
            path = Path(data_source)
            if path.is_file():
                if path.suffix.lower() == '.json':
                    return JSONReporter.load_from_json(path), None
                elif path.suffix.lower() == '.csv':
                    # For single CSV, perform fault localization analysis on-the-fly
                    return analyze_csv_data(path), None
            elif path.is_dir():
                # Directory with CSV files
                return load_csv_directory(path)
        elif isinstance(data_source, list):
            # Multiple uploaded files
            return load_uploaded_files(data_source)
        else:
            # Single uploaded file
            if data_source.name.endswith('.json'):
                content = data_source.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                data = json.loads(content)
                return data, None
            elif data_source.name.endswith('.csv'):
                df = pd.read_csv(data_source)
                # Save temporarily and analyze
                temp_path = Path.cwd() / "temp_coverage.csv"
                df.to_csv(temp_path, index=False)
                try:
                    result = analyze_csv_data(temp_path)
                    temp_path.unlink()  # Clean up
                    return result, None
                except Exception as e:
                    if temp_path.exists():
                        temp_path.unlink()
                    raise e
        return None, None
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None, None


def load_csv_directory(directory: Path) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Load data from a directory containing CSV files."""
    csv_files = {}
    json_data = None
    
    # Check for summary.json first
    json_file = directory / "summary.json"
    if json_file.exists():
        json_data = JSONReporter.load_from_json(json_file)
    
    # Load CSV files
    for file_pattern in ["coverage_matrix.csv", "test_results.csv", "ranking_*.csv"]:
        if "*" in file_pattern:
            # Handle wildcard patterns
            for csv_file in directory.glob(file_pattern):
                csv_files[csv_file.stem] = pd.read_csv(csv_file)
        else:
            csv_file = directory / file_pattern
            if csv_file.exists():
                csv_files[csv_file.stem] = pd.read_csv(csv_file)
    
    # If no JSON but we have coverage matrix, create JSON data
    if json_data is None and "coverage_matrix" in csv_files:
        json_data = analyze_csv_data(directory / "coverage_matrix.csv")
    
    csv_data = csv_files if csv_files else None
    return json_data, csv_data


def load_uploaded_files(uploaded_files) -> tuple[Optional[Dict[str, Any]], Optional[Dict[str, Any]]]:
    """Load data from multiple uploaded files."""
    csv_files = {}
    json_data = None
    
    for uploaded_file in uploaded_files:
        if uploaded_file.name.endswith('.json'):
            content = uploaded_file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            json_data = json.loads(content)
        elif uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
            file_stem = Path(uploaded_file.name).stem
            csv_files[file_stem] = df
    
    # If no JSON but we have coverage matrix, create JSON data
    if json_data is None and "coverage_matrix" in csv_files:
        # Save coverage matrix temporarily and analyze
        temp_path = Path.cwd() / "temp_coverage.csv"
        csv_files["coverage_matrix"].to_csv(temp_path, index=False)
        try:
            json_data = analyze_csv_data(temp_path)
            temp_path.unlink()
        except Exception as e:
            if temp_path.exists():
                temp_path.unlink()
            raise e
    
    csv_data = csv_files if csv_files else None
    return json_data, csv_data


def analyze_csv_data(csv_path: Path) -> Dict[str, Any]:
    """
    Analyze CSV coverage data and return results in dashboard format.
    
    This function performs fault localization analysis on CSV coverage data
    and returns results compatible with the dashboard.
    """
    try:
        # Load coverage matrix from CSV
        csv_reporter = CSVReporter(Path.cwd())
        coverage_matrix = csv_reporter.load_coverage_matrix(str(csv_path))
        
        # Create fault localizer with available formulas
        formulas = [
            OchiaiFormula(),
            TarantulaFormula(),
            JaccardFormula(),
            DStarFormula(),
            Kulczynski2Formula()
        ]
        
        # Create a temporary output directory for analysis
        temp_output = Path.cwd() / "temp_analysis"
        temp_output.mkdir(exist_ok=True)
        
        localizer = FaultLocalizer(
            source_dirs=[Path.cwd()],  # Dummy source dir
            test_dirs=[Path.cwd()],    # Dummy test dir
            formulas=formulas,
            output_dir=temp_output
        )
        
        # Perform analysis on existing coverage data
        result = localizer.analyze_from_data(coverage_matrix)
        
        # Convert to dashboard format using JSON reporter
        json_reporter = JSONReporter(temp_output)
        json_path = json_reporter.generate_report(result)
        
        # Load the generated JSON
        dashboard_data = JSONReporter.load_from_json(json_path)
        
        # Clean up temporary files
        try:
            import shutil
            shutil.rmtree(temp_output)
        except:
            pass  # Ignore cleanup errors
        
        return dashboard_data
        
    except Exception as e:
        raise RuntimeError(f"Error analyzing CSV data: {e}")


def validate_dashboard_data(data: Dict[str, Any]) -> bool:
    """
    Validate that the loaded data has the correct structure for dashboard display.
    
    Args:
        data: Dictionary containing the loaded data
        
    Returns:
        True if data is valid, False otherwise
    """
    try:
        # Check required top-level keys
        required_keys = ['stats', 'formulas', 'elements']
        missing_keys = [key for key in required_keys if key not in data]
        if missing_keys:
            st.error(f"Missing required keys: {missing_keys}")
            return False
        
        # Validate stats structure
        stats = data['stats']
        if not isinstance(stats, dict):
            st.error("Stats must be a dictionary")
            return False
        
        # Validate formulas structure
        formulas = data['formulas']
        if not isinstance(formulas, dict):
            st.error("Formulas data should be a dictionary")
            return False
        
        if not formulas:
            st.warning("No formula data found")
            return False
        
        # Validate at least one formula has valid structure
        valid_formula_found = False
        for formula_name, scores in formulas.items():
            if not isinstance(scores, list):
                st.warning(f"Formula '{formula_name}' should contain a list of scores")
                continue
            
            if not scores:  # Empty scores list
                st.warning(f"Formula '{formula_name}' has no scores")
                continue
                
            # Validate first score structure
            score = scores[0]
            if not isinstance(score, dict):
                st.warning(f"Invalid score structure in formula '{formula_name}'")
                continue
                
            required_score_keys = ['element', 'score', 'rank']
            if not all(key in score for key in required_score_keys):
                st.warning(f"Incomplete score structure in formula '{formula_name}'. Expected keys: {required_score_keys}")
                continue
            
            # Validate element structure
            element = score['element']
            if not isinstance(element, dict):
                st.warning(f"Invalid element structure in formula '{formula_name}'")
                continue
                
            required_element_keys = ['file', 'line']
            if not all(key in element for key in required_element_keys):
                st.warning(f"Incomplete element structure. Expected keys: {required_element_keys}")
                continue
            
            valid_formula_found = True
            break
        
        if not valid_formula_found:
            st.error("No valid formula data found")
            return False
        
        # Validate elements structure
        elements = data['elements']
        if not isinstance(elements, list):
            st.error("Elements data should be a list")
            return False
        
        return True
        
    except Exception as e:
        st.error(f"Error validating data structure: {e}")
        display_error_details(e)
        return False


def display_welcome():
    """Display welcome screen with instructions."""
    st.info("👋 **Welcome to PyFault Dashboard!**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("""
        ### 🚀 Getting Started
        1. **Upload** your fault localization results
        2. **Select** an SBFL formula  
        3. **Explore** the interactive visualizations
        4. **Filter** and **analyze** suspicious elements
        """)
        
        st.markdown("""
        ### 📋 Features
        - **Interactive rankings** with sorting and filtering
        - **Visualizations** of suspiciousness distributions  
        - **File-level analysis** with treemaps
        - **Source code viewer** with highlighting
        """)
    
    with col2:
        st.markdown("""
        ### 📁 Supported Formats
        - **JSON results** from `pyfault run`
        - **CSV coverage matrices** from `pyfault test`
        - **Direct integration** with PyFault CLI
        """)
        
        st.markdown("""
        ### 🔧 Commands
        ```bash
        # Run and open UI
        pyfault ui
        
        # Load specific results
        pyfault ui --data results.json
        
        # Custom port
        pyfault ui --port 8502
        ```
        """)


def display_results(data: Dict[str, Any], csv_data: Optional[Dict[str, Any]], 
                   formula: str, top_n: int, min_score: float, exclude_zero_scores: bool = False):
    """Display fault localization results with enhanced CSV data support."""
    
    # Extract data
    stats = data.get('stats', {})
    formulas = data.get('formulas', {})
    all_files = list(set(
        score['element']['file']
        for scores_list in formulas.values()
        for score in scores_list
        if 'element' in score and 'file' in score['element']
    ))    
    # Find common root directory for file paths
    common_root = os.path.commonpath(all_files) if all_files else None
    
    if formula not in formulas:
        st.error(f"Formula '{formula}' not found in data")
        return
    
    scores = formulas[formula]
    
    # Filter scores
    filtered_scores = [
        s for s in scores 
        if s['score'] >= min_score
    ]
    
    # Main metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Tests", 
            stats.get('total_tests', 'N/A'),
            delta=None
        )
    with col2:
        st.metric(
            "Failed Tests", 
            stats.get('failed_tests', 'N/A'),
            delta=None
        )
    with col3:
        st.metric(
            "Code Elements", 
            stats.get('total_elements', len(filtered_scores)),
            delta=None
        )
    with col4:
        st.metric(
            "Coverage", 
            f"{stats.get('coverage_percentage', 0):.1f}%",
            delta=None
        )
    
    # Tabs for different visualizations
    if csv_data:
        tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
            "📊 Overview", "🎯 Ranking", "📁 Files", "🔍 Source", 
            "🧪 Test Analysis", "📈 Coverage Matrix", "🏆 Formula Comparison"
        ])
        
        # Standard tabs
        with tab1:
            display_overview_tab(filtered_scores, formula, top_n, common_root, exclude_zero_scores)
        
        with tab2:
            display_ranking_tab(filtered_scores, formula, top_n, common_root)
        
        with tab3:
            display_files_tab(filtered_scores, common_root)
        
        with tab4:
            display_source_tab(filtered_scores, common_root)
        
        # New CSV-based tabs
        with tab5:
            display_test_analysis_tab(csv_data)
        
        with tab6:
            display_coverage_matrix_tab(csv_data)
        
        with tab7:
            display_formula_comparison_tab(csv_data, data)
    else:
        tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🎯 Ranking", "📁 Files", "🔍 Source"])
        
        with tab1:
            display_overview_tab(filtered_scores, formula, top_n, common_root, exclude_zero_scores)
        
        with tab2:
            display_ranking_tab(filtered_scores, formula, top_n, common_root)
        
        with tab3:
            display_files_tab(filtered_scores, common_root)
        
        with tab4:
            display_source_tab(filtered_scores, common_root)


def display_overview_tab(scores: List[Dict], formula: str, top_n: int, common_root: Optional[str], exclude_zero_scores: bool = False):
    """Display overview visualizations."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Suspiciousness Distribution")
        
        # Extract ALL scores for histogram (not limited by top_n for better distribution)
        all_score_values = [s['score'] for s in scores]
        
        # Apply zero score filter if requested for histogram
        if exclude_zero_scores:
            histogram_scores = [s for s in all_score_values if s > 0]
        else:
            histogram_scores = all_score_values
        
        if histogram_scores:
            fig = px.histogram(
                x=histogram_scores,
                nbins=20,
                title=f"Score Distribution ({formula.title()})" + (" - Excluding Zeros" if exclude_zero_scores else ""),
                labels={'x': 'Suspiciousness Score', 'y': 'Count'},
                color_discrete_sequence=['#FF6B6B']
            )
            fig.update_layout(
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Show statistics
            if exclude_zero_scores and len(all_score_values) != len(histogram_scores):
                st.info(f"Showing {len(histogram_scores)} elements (excluded {len(all_score_values) - len(histogram_scores)} zero scores)")
        else:
            if exclude_zero_scores:
                st.info("No non-zero scores available for distribution")
            else:
                st.info("No data available for distribution")
    
    with col2:
        st.subheader("🏆 Top Suspicious Elements")
        
        # Bar chart of top elements
        top_scores = scores[:min(top_n, 10)]  # Limit for readability
        
        if top_scores:
            elements = [
                f"{os.path.relpath(s['element']['file'], common_root) if common_root else Path(s['element']['file']).name}:{s['element']['line']}" 
                for s in top_scores
            ]
            score_values = [s['score'] for s in top_scores]
            colors = ['#FF4444' if s > 0.8 else '#FF8844' if s > 0.5 else '#FFBB44' for s in score_values]
            
            # Reverse the order of elements and scores for inverted bars
            elements = elements[::-1]
            score_values = score_values[::-1]
            colors = colors[::-1]

            fig = go.Figure(data=[
                go.Bar(
                    y=elements,  # Horizontal bar
                    x=score_values,
                    orientation='h',
                    marker_color=colors,
                    text=[f"{s:.2f}" for s in score_values],
                    textposition='inside'
                )
            ])
            
            fig.update_layout(
                title=f"Top Elements by Suspiciousness ({formula.title()})",
                xaxis_title="Suspiciousness Score",
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for ranking")


def display_ranking_tab(scores: List[Dict], formula: str, top_n: int, common_root: Optional[str]):
    """Display detailed ranking table."""
    st.subheader(f"📋 Detailed Ranking - {formula.title()}")
    
    if not scores:
        st.info("No scores available for the selected criteria")
        return
    
    # Prepare data for table
    top_scores = scores[:top_n]
    
    table_data = []
    for score in top_scores:
        element = score['element']
        file_display_path = os.path.relpath(element['file'], common_root) if common_root else Path(element['file']).name
        table_data.append({
            'Rank': score['rank'],
            'File': file_display_path,
            'Line': element['line'],
            'Type': element['element_type'],
            'Element': element.get('element_name', f"line_{element['line']}"),
            'Suspiciousness': score['score']
        })
    
    df = pd.DataFrame(table_data)
    
    # Display interactive table
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Suspiciousness": st.column_config.ProgressColumn(
                "Suspiciousness",
                help="Suspiciousness score (0.0 to 1.0)",
                min_value=0.0,
                max_value=1.0,
                format="%.2f"
            ),
            "Rank": st.column_config.NumberColumn(
                "Rank",
                help="Ranking position",
                format="%d"
            )
        }
    )
    
    # Additional statistics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        avg_score = np.mean([s['score'] for s in top_scores])
        st.metric("Average Score", f"{avg_score:.2f}")
    
    with col2:
        max_score = max(s['score'] for s in top_scores) if top_scores else 0
        st.metric("Max Score", f"{max_score:.2f}")
    
    with col3:
        unique_files = len(set(s['element']['file'] for s in top_scores))
        st.metric("Affected Files", unique_files)


def display_files_tab(scores: List[Dict], common_root: Optional[str]):
    """Display file-level analysis."""
    st.subheader("📁 File-Level Analysis")
    
    if not scores:
        st.info("No data available for file analysis")
        return
    
    # Group by file
    file_stats = {}
    for score in scores:
        file_path = score['element']['file']
        if file_path not in file_stats:
            file_stats[file_path] = {
                'count': 0,
                'total_score': 0,
                'max_score': 0,
                'scores': []
            }
        
        file_stats[file_path]['count'] += 1
        file_stats[file_path]['total_score'] += score['score']
        file_stats[file_path]['max_score'] = max(file_stats[file_path]['max_score'], score['score'])
        file_stats[file_path]['scores'].append(score['score'])
    
    # Prepare data for treemap
    files = []
    counts = []
    avg_scores = []
    
    for file_path, stats in file_stats.items():
        display_path = os.path.relpath(file_path, common_root) if common_root else Path(file_path).name
        files.append(display_path)
        counts.append(stats['count'])
        avg_scores.append(stats['total_score'] / stats['count'])

    if files:
        # Create a DataFrame for Plotly
        df_treemap = pd.DataFrame({
            'file': files,
            'count': counts,
            'avg_score': avg_scores
        })

        # Treemap for file overview
        fig = px.treemap(
            df_treemap,
            path=[px.Constant("all"), 'file'], # Use path for hierarchy
            values='count',
            color='avg_score',
            color_continuous_scale='Reds',
            title="Files by Number of Suspicious Elements (Color = Avg Score)",
            hover_data={'avg_score': ':.3f'} # Custom hover format
        )
        fig.update_traces(textinfo="label+value")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # File statistics table
        st.subheader("📊 File Statistics")
        
        file_table_data = []
        for file_path, stats in sorted(file_stats.items(), key=lambda x: x[1]['max_score'], reverse=True):
            display_path = os.path.relpath(file_path, common_root) if common_root else Path(file_path).name
            file_table_data.append({
                'File': display_path,
                'Elements': stats['count'],
                'Max Score': stats['max_score'],
                'Avg Score': stats['total_score'] / stats['count'],
                'Score Sum': stats['total_score']
            })
        
        df = pd.DataFrame(file_table_data)
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Max Score": st.column_config.ProgressColumn(
                    "Max Score",
                    min_value=0.0,
                    max_value=1.0,
                    format="%.2f"
                ),
                "Avg Score": st.column_config.ProgressColumn(
                    "Avg Score", 
                    min_value=0.0,
                    max_value=1.0,
                    format="%.2f"
                )
            }
        )


def display_source_tab(scores: List[Dict], common_root: Optional[str]):
    """Display source code viewer with highlighting."""
    st.subheader("🔍 Source Code Viewer")
    
    if not scores:
        st.info("No data available for source viewing")
        return
    
    # Show highlighting legend
    st.markdown("### 🎨 Suspiciousness Legend")
    col_legend1, col_legend2, col_legend3, col_legend4 = st.columns(4)
    with col_legend1:
        st.markdown("🔴 **High** (> 0.8)")
    with col_legend2:
        st.markdown("🟡 **Medium** (0.5 - 0.8)")
    with col_legend3:
        st.markdown("🟢 **Low** (0.2 - 0.5)")
    with col_legend4:
        st.markdown("⚪ **Minimal** (< 0.2)")
        
    # File selector
    unique_files = list(set(s['element']['file'] for s in scores))

    def format_path(path):
        if common_root:
            return os.path.relpath(path, common_root)
        return Path(path).name
    
    # Find the file with the highest score (and in case of a tie, the one with more elements)
    file_stats = {}
    for score in scores:
        file_path = score['element']['file']
        if file_path not in file_stats:
            file_stats[file_path] = {
                'max_score': score['score'],
                'count': 1
            }
        else:
            file_stats[file_path]['max_score'] = max(file_stats[file_path]['max_score'], score['score'])
            file_stats[file_path]['count'] += 1

    # Sort files by max score and then by count
    default_file = None
    if file_stats:
        default_file = sorted(
            file_stats.items(),
            key=lambda x: (x[1]['max_score'], x[1]['count']),
            reverse=True
        )[0][0]

    selected_file = st.selectbox(
        "Select File",
        unique_files,
        format_func=format_path,
        index=unique_files.index(default_file) if default_file in unique_files else 0
    )
    
    if selected_file:
        # Get scores for this file, which are already sorted by score
        file_scores_by_score = [s for s in scores if s['element']['file'] == selected_file]
        
        # Create a copy and sort by line number for code view
        file_scores_by_line = sorted(file_scores_by_score, key=lambda x: x['element']['line'])
        
        col1, col2 = st.columns([3, 1])
        
        with col1:
            st.subheader(f"📄 {Path(selected_file).name}")
            
            # Try to read the actual source file
            source_file_path = Path(selected_file)
            code_content = None
            
            # Try multiple ways to locate the file
            possible_paths = [
                source_file_path,  # Absolute path
                Path.cwd() / selected_file,  # Relative to current working directory
                Path.cwd() / source_file_path.name,  # Just filename in current directory
            ]
            
            # Add common source directories
            for src_dir in ['src', 'lib', 'app', '.']:
                possible_paths.append(Path.cwd() / src_dir / source_file_path.name)
                if source_file_path.is_absolute():
                    # Try to make it relative to common source dirs
                    try:
                        rel_path = source_file_path.relative_to(source_file_path.anchor)
                        possible_paths.append(Path.cwd() / src_dir / rel_path)
                    except ValueError:
                        pass
            
            # Try to read the file from possible locations
            for path in possible_paths:
                try:
                    if path.exists() and path.is_file():
                        with open(path, 'r', encoding='utf-8') as f:
                            code_content = f.read()
                        break
                except (PermissionError, UnicodeDecodeError, OSError):
                    continue
            
            if code_content is not None:
                # Create line-by-line highlighting info
                lines = code_content.split('\n')
                score_map = {s['element']['line']: s['score'] for s in file_scores_by_line}
                
                # Display the code with syntax highlighting
                try:
                    from pygments import highlight
                    from pygments.lexers import get_lexer_by_name
                    from pygments.formatters import HtmlFormatter
                    import html

                    lexer = get_lexer_by_name("python", stripall=True)
                    formatter = HtmlFormatter(style='monokai', nobackground=True)
                    
                    css = f"<style>{formatter.get_style_defs('.highlight')}</style>"
                    st.markdown(css, unsafe_allow_html=True)

                    highlighted_code = highlight(code_content, lexer, formatter)
                    
                    cleaned_code = highlighted_code.strip()
                    if cleaned_code.startswith('<div class="highlight"><pre>'):
                        cleaned_code = cleaned_code[len('<div class="highlight"><pre>'):]
                    if cleaned_code.endswith('</pre></div>'):
                        cleaned_code = cleaned_code[:-len('</pre></div>')]
                    
                    highlighted_lines = cleaned_code.strip().split('\n')

                except ImportError:
                    st.warning("Pygments not installed. Falling back to plain text. `pip install Pygments`")
                    highlighted_lines = [html.escape(line) for line in lines]

                
                # Generate custom HTML for code view with highlighting
                html_lines = []
                line_numbers_html = []
                
                # Define a consistent line height
                line_height = "1.3em" 

                for i, line_content in enumerate(highlighted_lines):
                    line_num = i + 1
                    score = score_map.get(line_num)
                    bg_color = "transparent"
                    
                    if score is not None:
                        if score > 0.8:
                            bg_color = "rgba(255, 75, 75, 0.3)" # Red
                        elif score > 0.5:
                            bg_color = "rgba(255, 165, 0, 0.3)" # Orange
                        elif score > 0.2:
                            bg_color = "rgba(255, 255, 0, 0.3)" # Yellow
                
                    # Wrap the already-highlighted HTML line
                    html_lines.append(f'<div style="background-color: {bg_color}; height: {line_height}; white-space: pre;">{line_content if line_content else "&nbsp;"}</div>')
                    line_numbers_html.append(f'<div style="height: {line_height};">{line_num}</div>')

                # Using st.code's line numbering by creating a custom component look-alike
                st.markdown(f"""
                <div class="highlight" style="font-family: monospace; background-color:#272822; border-radius: 0.5rem; overflow: hidden; width: 100%;">
                    <div style="display: flex; width: 100%;">
                        <div style="color: #888; text-align: right; padding: 5px; user-select: none; flex-shrink: 0;">
                            {''.join(line_numbers_html)}
                        </div>
                        <div style="flex-grow: 1; padding: 5px 5px 5px 10px; width: 100%;">
                            {''.join(html_lines)}
                        </div>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            else:
                # File not found - show alternative information
                st.warning(f"⚠️ Could not locate source file: `{selected_file}`")
                st.info("""
                **Possible reasons:**
                - File path in the coverage data is absolute but not accessible
                - File has been moved or renamed
                - Dashboard is running from a different directory
                
                **Suggested solutions:**
                - Run the dashboard from the project root directory
                - Ensure source files are accessible from the current working directory
                - Check if the file path in the data is correct
                """)
                
                # Show attempted paths for debugging
                with st.expander("🔍 Debugging - Attempted file paths"):
                    for i, path in enumerate(possible_paths[:5]):  # Show first 5 attempts
                        exists = "✅" if path.exists() else "❌"
                        st.text(f"{exists} {path}")
                
                # Still show the score information
                st.markdown("### 📊 Line Scores (No Source Preview)")
                for score in file_scores_by_score[:10]:  # Show top 10
                    element = score['element']
                    score_val = score['score']
                    
                    if score_val > 0.8:
                        color = "🔴"
                    elif score_val > 0.5:
                        color = "🟡"
                    else:
                        color = "🟢"
                    
                    st.write(f"{color} **Line {element['line']}**: {score_val:.2f}")
        
        with col2:
            st.subheader("📊 Line Scores")
            
            # Show scores for this file, sorted by score
            for score in file_scores_by_score[:20]:  # Limit to top 20
                element = score['element']
                score_val = score['score']
                
                # Color coding
                if score_val > 0.8:
                    color = "🔴"
                elif score_val > 0.5:
                    color = "🟡"
                else:
                    color = "🟢"
                
                st.write(f"{color} **Line {element['line']}**: {score_val:.2f}")
            
            # Show file statistics
            if file_scores_by_score:
                st.divider()
                st.subheader("📈 File Statistics")
                
                scores_values = [s['score'] for s in file_scores_by_score]
                st.metric("Suspicious Lines", len(file_scores_by_score))
                st.metric("Max Score", f"{max(scores_values):.2f}")
                st.metric("Avg Score", f"{np.mean(scores_values):.2f}")
                st.metric("High Risk Lines", len([s for s in scores_values if s > 0.8]))


def display_test_analysis_tab(csv_data: Dict[str, pd.DataFrame]):
    """Display test analysis from CSV data."""
    st.subheader("🧪 Test Analysis")
    
    if "test_results" not in csv_data:
        st.warning("Test results data not available")
        return
    
    test_df = csv_data["test_results"]
    
    # Test overview metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_tests = len(test_df)
    failed_tests = len(test_df[test_df['Outcome'] == 'failed'])
    passed_tests = len(test_df[test_df['Outcome'] == 'passed'])
    
    with col1:
        st.metric("Total Tests", total_tests)
    with col2:
        st.metric("Failed Tests", failed_tests, delta=f"-{failed_tests}")
    with col3:
        st.metric("Passed Tests", passed_tests, delta=f"+{passed_tests}")
    with col4:
        avg_coverage = test_df['Coverage Percentage'].str.rstrip('%').astype(float).mean()
        st.metric("Avg Coverage", f"{avg_coverage:.1f}%")
    
    # Test results table
    st.subheader("📋 Test Results Details")
    
    # Add outcome filtering
    outcome_filter = st.selectbox("Filter by outcome:", ["All", "failed", "passed"])
    
    if outcome_filter != "All":
        filtered_test_df = test_df[test_df['Outcome'] == outcome_filter]
    else:
        filtered_test_df = test_df
    
    st.dataframe(filtered_test_df, use_container_width=True)
    
    # Coverage vs Outcome analysis
    st.subheader("📊 Coverage vs Test Outcome")
    
    # Box plot of coverage by outcome
    fig = px.box(test_df, x='Outcome', y='Coverage Percentage',
                 title="Coverage Distribution by Test Outcome",
                 labels={'Coverage Percentage': 'Coverage %'})
    st.plotly_chart(fig, use_container_width=True)
    
    # Scatter plot of elements covered vs coverage percentage
    col1, col2 = st.columns(2)
    
    with col1:
        fig2 = px.scatter(test_df, x='Elements Covered', y='Coverage Percentage',
                         color='Outcome', title="Elements Covered vs Coverage %",
                         labels={'Coverage Percentage': 'Coverage %'})
        st.plotly_chart(fig2, use_container_width=True)
    
    with col2:
        # Test outcome distribution
        outcome_counts = test_df['Outcome'].value_counts()
        fig3 = px.pie(values=outcome_counts.values, names=outcome_counts.index,
                     title="Test Outcome Distribution")
        st.plotly_chart(fig3, use_container_width=True)


def display_coverage_matrix_tab(csv_data: Dict[str, pd.DataFrame]):
    """Display coverage matrix visualization."""
    st.subheader("📈 Coverage Matrix Analysis")
    
    if "coverage_matrix" not in csv_data:
        st.warning("Coverage matrix data not available")
        return
    
    coverage_df = csv_data["coverage_matrix"]
    
    # Extract metadata columns and test columns
    metadata_cols = ['Element', 'File', 'Line', 'ElementType', 'ElementName']
    test_cols = [col for col in coverage_df.columns if col not in metadata_cols]
    
    if not test_cols:
        st.error("No test columns found in coverage matrix")
        return
    
    # Get test outcomes from the OUTCOME row
    outcome_row = coverage_df[coverage_df['Element'] == 'OUTCOME']
    if not outcome_row.empty:
        test_outcomes = outcome_row[test_cols].iloc[0].to_dict()
        # Remove OUTCOME row for analysis
        element_df = coverage_df[coverage_df['Element'] != 'OUTCOME'].copy()
    else:
        test_outcomes = {}
        element_df = coverage_df.copy()
    
    # Convert test columns to numeric for analysis
    for col in test_cols:
        element_df[col] = pd.to_numeric(element_df[col], errors='coerce')
    
    # Create coverage matrix for visualization
    coverage_matrix = element_df[test_cols].values
    element_labels = element_df['Element'].tolist()
    
    # Limit to reasonable size for visualization
    max_elements = 50
    if len(element_labels) > max_elements:
        st.info(f"Showing top {max_elements} elements for visualization. Total elements: {len(element_labels)}")
        coverage_matrix = coverage_matrix[:max_elements, :]
        element_labels = element_labels[:max_elements]
    
    # Create heatmap
    fig = go.Figure(data=go.Heatmap(
        z=coverage_matrix,
        x=test_cols,
        y=element_labels,
        colorscale='RdYlBu_r',
        showscale=False,
        hoverongaps=False
    ))
    
    fig.update_layout(
        title="Coverage Matrix: Elements vs Tests",
        xaxis_title="Tests",
        yaxis_title="Code Elements",
        height=1000,
        xaxis_tickangle=-45
    )
    
    st.plotly_chart(fig, use_container_width=True)

    # Add an interactive table view of the matrix
    st.subheader("📄 Coverage Matrix Table")
    st.info("Click on column headers to sort by test coverage.")
    
    # Prepare dataframe for display
    display_df = element_df[['Element', 'File', 'Line'] + test_cols].copy()
    st.dataframe(display_df, use_container_width=True, height=400)
    
    # Coverage statistics
    
    st.subheader("📊 Element Coverage Statistics")
    # Calculate coverage per element
    element_df['Total_Coverage'] = element_df[test_cols].sum(axis=1)
    element_df['Coverage_Percentage'] = (element_df['Total_Coverage'] / len(test_cols)) * 100
    # Coverage distribution
    fig4 = px.histogram(element_df, x='Coverage_Percentage', 
                        title="Element Coverage Distribution",
                        labels={'Coverage_Percentage': 'Coverage %'})
    st.plotly_chart(fig4, use_container_width=True)


def display_formula_comparison_tab(csv_data: Dict[str, pd.DataFrame], json_data: Dict[str, Any]):
    """Display comparison between different SBFL formulas."""
    st.subheader("🏆 Formula Comparison Analysis")
    
    # Get all ranking files
    ranking_files = {k: v for k, v in csv_data.items() if k.startswith('ranking_')}
    
    if not ranking_files:
        st.warning("No ranking data available for comparison")
        return
    
    # Extract formula names
    formula_names = [k.replace('ranking_', '') for k in ranking_files.keys()]
    
    st.write(f"**Available formulas:** {', '.join(formula_names)}")
    
    # Debug: Show the structure of ranking files
    with st.expander("🔍 Debug - Ranking Data Structure"):
        for formula in formula_names:
            ranking_key = f"ranking_{formula}"
            if ranking_key in csv_data:
                df = csv_data[ranking_key]
                st.write(f"**{formula}** - Columns: {list(df.columns)}")
                st.write(f"Shape: {df.shape}")
                if len(df) > 0:
                    st.write("First few rows:")
                    st.dataframe(df.head())
    
    # Top-N comparison
    st.subheader("🎯 Top-N Element Comparison")
    
    top_n = st.slider("Select N for Top-N comparison:", 5, 50, 10)
    
        # Create comparison table with better error handling
    comparison_data = {}
    
    for formula in formula_names:
        ranking_key = f"ranking_{formula}"
        if ranking_key in csv_data:
            df = csv_data[ranking_key]
            
            # Always construct element identifier from File and Line since Element column contains "None"
            if 'File' in df.columns and 'Line' in df.columns:
                # Create a proper element identifier
                df['Element_Display'] = df['File'].astype(str) + ':' + df['Line'].astype(str)
                element_col = 'Element_Display'
            else:
                st.warning(f"Could not find File and Line columns in {ranking_key}")
                continue
            
            # Get top elements, handle empty DataFrames
            if len(df) > 0:
                top_elements = df.head(top_n)[element_col].fillna('Unknown').tolist()
                # Clean up the file paths to show just filename:line
                top_elements = [
                    f"{Path(elem.split(':')[0]).name}:{elem.split(':')[1]}" if ':' in elem 
                    else elem 
                    for elem in top_elements
                ]
            else:
                top_elements = ['No data'] * top_n
                
            comparison_data[formula] = top_elements
    
    # Show top elements side by side
    if comparison_data:
        # Ensure all lists have the same length
        max_len = max(len(v) for v in comparison_data.values())
        for formula in comparison_data:
            while len(comparison_data[formula]) < max_len:
                comparison_data[formula].append('N/A')
        
        comparison_df = pd.DataFrame.from_dict(comparison_data, orient='index').T
        comparison_df.index = pd.Index([f"Rank {i+1}" for i in range(len(comparison_df))])
        
        st.dataframe(comparison_df, use_container_width=True)
        
        # Only calculate agreement if we have valid data
        valid_data = {k: v for k, v in comparison_data.items() 
                     if not all(x in ['No data', 'N/A', 'Unknown'] for x in v)}
        
        if len(valid_data) > 1:
            # Calculate agreement between formulas
            st.subheader("🤝 Formula Agreement Analysis")
            
            # Jaccard similarity between top-N lists
            valid_formulas = list(valid_data.keys())
            jaccard_matrix = np.zeros((len(valid_formulas), len(valid_formulas)))
            
            for i, formula1 in enumerate(valid_formulas):
                for j, formula2 in enumerate(valid_formulas):
                    set1 = set(valid_data[formula1])
                    set2 = set(valid_data[formula2])
                    # Remove placeholder values from sets
                    set1 = {x for x in set1 if x not in ['No data', 'N/A', 'Unknown']}
                    set2 = {x for x in set2 if x not in ['No data', 'N/A', 'Unknown']}
                    
                    jaccard = len(set1 & set2) / len(set1 | set2) if len(set1 | set2) > 0 else 0
                    jaccard_matrix[i, j] = jaccard
            
            # Heatmap of agreement
            fig = go.Figure(data=go.Heatmap(
                z=jaccard_matrix,
                x=valid_formulas,
                y=valid_formulas,
                colorscale='Blues',
                text=np.round(jaccard_matrix, 3),
                texttemplate="%{text}",
                showscale=True
            ))
            
            fig.update_layout(
                title=f"Jaccard Similarity between Formulas (Top-{top_n})",
                xaxis_title="Formula",
                yaxis_title="Formula"
            )
            
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Not enough valid data to calculate formula agreement")
    else:
        st.error("No valid ranking data found for comparison")
    
    # Score distribution comparison with better error handling
    st.subheader("📊 Score Distribution Comparison")
    
    # Combine all ranking data
    all_rankings = []
    for formula in formula_names:
        ranking_key = f"ranking_{formula}"
        if ranking_key in csv_data:
            df = csv_data[ranking_key].copy()
            
            # Check if we have a suspiciousness column
            sus_col = None
            possible_sus_cols = ['Suspiciousness', 'suspiciousness', 'Score', 'score']
            
            for col in possible_sus_cols:
                if col in df.columns:
                    sus_col = col
                    break
            
            if sus_col is not None and len(df) > 0:
                df['Formula'] = formula
                df['Suspiciousness'] = pd.to_numeric(df[sus_col], errors='coerce')
                all_rankings.append(df[['Formula', 'Suspiciousness']].dropna())
    
    if all_rankings:
        combined_df = pd.concat(all_rankings, ignore_index=True)
        
        if len(combined_df) > 0:
            # Box plot of suspiciousness scores by formula
            fig = px.box(combined_df, x='Formula', y='Suspiciousness',
                         title="Suspiciousness Score Distribution by Formula")
            st.plotly_chart(fig, use_container_width=True)
            
            # Violin plot for more detailed distribution
            fig2 = px.violin(combined_df, x='Formula', y='Suspiciousness',
                            title="Detailed Score Distribution by Formula")
            st.plotly_chart(fig2, use_container_width=True)
            
            # Statistical summary
            st.subheader("📈 Statistical Summary")
            
            stats_summary = combined_df.groupby('Formula')['Suspiciousness'].agg([
                'count', 'mean', 'std', 'min', 'max'
            ]).round(4)
            
            st.dataframe(stats_summary)
        else:
            st.warning("No valid suspiciousness scores found for analysis")
    else:
        st.warning("No ranking data available for score distribution analysis")


if __name__ == "__main__":
    main()

"""
Streamlit-based dashboard for PyFault results visualization.
"""

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


def launch_dashboard(data_file: Optional[str] = None, 
                    port: int = 8501, 
                    auto_open: bool = False) -> None:
    """Launch the Streamlit dashboard."""
    import subprocess
    import sys
    import os
    
    # Set environment variable for data file
    if data_file:
        os.environ['PYFAULT_DATA_FILE'] = str(data_file)
    
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
    print(f"📂 Data file: {data_file or 'None (upload required)'}")
    
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
    
    # Check for pre-loaded data file
    import os
    preloaded_file = os.environ.get('PYFAULT_DATA_FILE')
    
    # Sidebar for controls
    with st.sidebar:
        st.header("🔧 Configuration")
        
        # File upload or use preloaded
        if preloaded_file:
            st.success(f"📁 Loaded: {Path(preloaded_file).name}")
            data_source = preloaded_file
        else:
            uploaded_file = st.file_uploader(
                "Upload Results File", 
                type=['json', 'csv'],
                help="Upload PyFault JSON results or coverage CSV"
            )
            data_source = uploaded_file
        
        if data_source is not None:
            # Load data
            try:
                data = load_data(data_source)
                
                if data:
                    # Validate data structure
                    if not validate_dashboard_data(data):
                        st.error("❌ Invalid data structure. Please check your input file.")
                        return
                    
                    st.success(f"✅ Data loaded successfully!")
                    
                    # Configuration options
                    st.divider()
                    
                    # Formula selection
                    available_formulas = list(data.get('formulas', {}).keys()) if isinstance(data, dict) else ['ochiai', 'tarantula', 'jaccard']
                    selected_formula = st.selectbox(
                        "🔬 SBFL Formula",
                        available_formulas,
                        help="Select the suspiciousness formula to visualize"
                    )
                    
                    # Top N elements
                    max_elements = min(100, len(data.get('elements', [])) if isinstance(data, dict) else 50)
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
                    
                    # File type filter
                    file_extensions = st.multiselect(
                        "File Extensions",
                        ['.py', '.js', '.java', '.cpp', '.c'],
                        default=['.py'],
                        help="Filter by file extensions"
                    )
                    
                    # Display main content
                    display_results(data, selected_formula, top_n, min_score, file_extensions)
                else:
                    st.error("❌ Failed to load data")
                    
            except Exception as e:
                st.error(f"❌ Error loading data: {str(e)}")
                st.exception(e)
    
    # Main content area
    if 'data_source' not in locals() or data_source is None:
        display_welcome()


def load_data(data_source) -> Optional[Dict[str, Any]]:
    """Load data from file or uploaded content."""
    try:
        if isinstance(data_source, str):
            # File path
            path = Path(data_source)
            if path.suffix.lower() == '.json':
                return JSONReporter.load_from_json(path)
            elif path.suffix.lower() == '.csv':
                # For CSV, perform fault localization analysis on-the-fly
                return analyze_csv_data(path)
        else:
            # Uploaded file
            if data_source.name.endswith('.json'):
                content = data_source.read()
                if isinstance(content, bytes):
                    content = content.decode('utf-8')
                data = json.loads(content)
                return data
            elif data_source.name.endswith('.csv'):
                df = pd.read_csv(data_source)
                # Save temporarily and analyze
                temp_path = Path.cwd() / "temp_coverage.csv"
                df.to_csv(temp_path, index=False)
                try:
                    result = analyze_csv_data(temp_path)
                    temp_path.unlink()  # Clean up
                    return result
                except Exception as e:
                    if temp_path.exists():
                        temp_path.unlink()
                    raise e
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return None


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
        if not all(key in data for key in required_keys):
            st.error(f"Missing required keys. Expected: {required_keys}, Found: {list(data.keys())}")
            return False
        
        # Validate stats structure
        stats = data['stats']
        required_stats = ['total_tests', 'failed_tests', 'total_elements']
        if not all(key in stats for key in required_stats):
            st.warning(f"Missing stats keys. Expected: {required_stats}, Found: {list(stats.keys())}")
        
        # Validate formulas structure
        formulas = data['formulas']
        if not isinstance(formulas, dict):
            st.error("Formulas data should be a dictionary")
            return False
        
        if not formulas:
            st.warning("No formula data found")
            return False
        
        # Validate individual formula data
        for formula_name, scores in formulas.items():
            if not isinstance(scores, list):
                st.error(f"Formula '{formula_name}' should contain a list of scores")
                return False
            
            if scores:  # If there are scores, validate the first one
                score = scores[0]
                required_score_keys = ['element', 'score', 'rank']
                if not all(key in score for key in required_score_keys):
                    st.error(f"Invalid score structure in formula '{formula_name}'. Expected keys: {required_score_keys}")
                    return False
                
                # Validate element structure
                element = score['element']
                required_element_keys = ['file', 'line']
                if not all(key in element for key in required_element_keys):
                    st.error(f"Invalid element structure. Expected keys: {required_element_keys}")
                    return False
        
        # Validate elements structure
        elements = data['elements']
        if not isinstance(elements, list):
            st.error("Elements data should be a list")
            return False
        
        return True
        
    except Exception as e:
        st.error(f"Error validating data structure: {e}")
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


def display_results(data: Dict[str, Any], formula: str, top_n: int, 
                   min_score: float, file_extensions: List[str]):
    """Display fault localization results."""
    
    # Extract data
    stats = data.get('stats', {})
    formulas = data.get('formulas', {})
    
    if formula not in formulas:
        st.error(f"Formula '{formula}' not found in data")
        return
    
    scores = formulas[formula]
    
    # Filter scores
    filtered_scores = [
        s for s in scores 
        if s['score'] >= min_score and 
        any(s['element']['file'].endswith(ext) for ext in file_extensions)
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
    tab1, tab2, tab3, tab4 = st.tabs(["📊 Overview", "🎯 Ranking", "📁 Files", "🔍 Source"])
    
    with tab1:
        display_overview_tab(filtered_scores, formula, top_n)
    
    with tab2:
        display_ranking_tab(filtered_scores, formula, top_n)
    
    with tab3:
        display_files_tab(filtered_scores)
    
    with tab4:
        display_source_tab(filtered_scores)


def display_overview_tab(scores: List[Dict], formula: str, top_n: int):
    """Display overview visualizations."""
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Suspiciousness Distribution")
        
        # Extract scores for histogram
        score_values = [s['score'] for s in scores[:top_n * 2]]  # More data for better distribution
        
        if score_values:
            fig = px.histogram(
                x=score_values,
                nbins=20,
                title=f"Score Distribution ({formula.title()})",
                labels={'x': 'Suspiciousness Score', 'y': 'Count'},
                color_discrete_sequence=['#FF6B6B']
            )
            fig.update_layout(
                showlegend=False,
                height=400
            )
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("No data available for distribution")
    
    with col2:
        st.subheader("🏆 Top Suspicious Elements")
        
        # Bar chart of top elements
        top_scores = scores[:min(top_n, 10)]  # Limit for readability
        
        if top_scores:
            elements = [f"{Path(s['element']['file']).name}:{s['element']['line']}" for s in top_scores]
            score_values = [s['score'] for s in top_scores]
            colors = ['#FF4444' if s > 0.8 else '#FF8844' if s > 0.5 else '#FFBB44' for s in score_values]
            
            fig = go.Figure(data=[
                go.Bar(
                    y=elements,  # Horizontal bar
                    x=score_values,
                    orientation='h',
                    marker_color=colors,
                    text=[f"{s:.3f}" for s in score_values],
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


def display_ranking_tab(scores: List[Dict], formula: str, top_n: int):
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
        table_data.append({
            'Rank': score['rank'],
            'File': Path(element['file']).name,
            'Line': element['line'],
            'Type': element['element_type'],
            'Element': element.get('element_name', f"line_{element['line']}"),
            'Suspiciousness': score['score'],
            'Full Path': element['file']
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
                format="%.4f"
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
        st.metric("Average Score", f"{avg_score:.4f}")
    
    with col2:
        max_score = max(s['score'] for s in top_scores) if top_scores else 0
        st.metric("Max Score", f"{max_score:.4f}")
    
    with col3:
        unique_files = len(set(s['element']['file'] for s in top_scores))
        st.metric("Affected Files", unique_files)


def display_files_tab(scores: List[Dict]):
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
        files.append(Path(file_path).name)
        counts.append(stats['count'])
        avg_scores.append(stats['total_score'] / stats['count'])
    
    if files:
        # Treemap for file overview
        fig = px.treemap(
            names=files,
            values=counts,
            color=avg_scores,
            color_continuous_scale='Reds',
            title="Files by Number of Suspicious Elements (Color = Avg Score)"
        )
        fig.update_traces(textinfo="label+value")
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)
        
        # File statistics table
        st.subheader("📊 File Statistics")
        
        file_table_data = []
        for file_path, stats in sorted(file_stats.items(), key=lambda x: x[1]['max_score'], reverse=True):
            file_table_data.append({
                'File': Path(file_path).name,
                'Elements': stats['count'],
                'Max Score': stats['max_score'],
                'Avg Score': stats['total_score'] / stats['count'],
                'Score Sum': stats['total_score'],
                'Full Path': file_path
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
                    format="%.4f"
                ),
                "Avg Score": st.column_config.ProgressColumn(
                    "Avg Score", 
                    min_value=0.0,
                    max_value=1.0,
                    format="%.4f"
                )
            }
        )


def display_source_tab(scores: List[Dict]):
    """Display source code viewer with highlighting."""
    st.subheader("🔍 Source Code Viewer")
    
    if not scores:
        st.info("No data available for source viewing")
        return
    
    # File selector
    unique_files = list(set(s['element']['file'] for s in scores))
    selected_file = st.selectbox(
        "Select File",
        unique_files,
        format_func=lambda x: Path(x).name
    )
    
    if selected_file:
        # Get scores for this file
        file_scores = [s for s in scores if s['element']['file'] == selected_file]
        file_scores.sort(key=lambda x: x['element']['line'])
        
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
                score_map = {s['element']['line']: s['score'] for s in file_scores}
                
                # Display the code with syntax highlighting
                st.code(code_content, language='python', line_numbers=True)
                
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
                
                # Display highlighted lines with scores
                if score_map:
                    st.markdown("### 📍 Suspicious Lines")
                    for line_num in sorted(score_map.keys()):
                        if 1 <= line_num <= len(lines):
                            score = score_map[line_num]
                            line_content = lines[line_num - 1].strip()
                            
                            # Color coding
                            if score > 0.8:
                                color = "🔴"
                                bg_color = "#ffe6e6"
                            elif score > 0.5:
                                color = "🟡"
                                bg_color = "#fff8e6"
                            elif score > 0.2:
                                color = "🟢"
                                bg_color = "#e6ffe6"
                            else:
                                color = "⚪"
                                bg_color = "#f5f5f5"
                            
                            # Display highlighted line
                            st.markdown(
                                f"""
                                <div style="background-color: {bg_color}; padding: 8px; border-radius: 4px; margin: 4px 0;">
                                    <strong>Line {line_num}</strong> {color} Score: {score:.4f}<br>
                                    <code>{line_content}</code>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
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
                for score in file_scores[:10]:  # Show top 10
                    element = score['element']
                    score_val = score['score']
                    
                    if score_val > 0.8:
                        color = "🔴"
                    elif score_val > 0.5:
                        color = "🟡"
                    else:
                        color = "🟢"
                    
                    st.write(f"{color} **Line {element['line']}**: {score_val:.4f}")
        
        with col2:
            st.subheader("📊 Line Scores")
            
            # Show scores for this file
            for score in file_scores[:20]:  # Limit to top 20
                element = score['element']
                score_val = score['score']
                
                # Color coding
                if score_val > 0.8:
                    color = "🔴"
                elif score_val > 0.5:
                    color = "🟡"
                else:
                    color = "🟢"
                
                st.write(f"{color} **Line {element['line']}**: {score_val:.4f}")
            
            # Show file statistics
            if file_scores:
                st.divider()
                st.subheader("📈 File Statistics")
                
                scores_values = [s['score'] for s in file_scores]
                st.metric("Suspicious Lines", len(file_scores))
                st.metric("Max Score", f"{max(scores_values):.4f}")
                st.metric("Avg Score", f"{np.mean(scores_values):.4f}")
                st.metric("High Risk Lines", len([s for s in scores_values if s > 0.8]))


if __name__ == "__main__":
    main()

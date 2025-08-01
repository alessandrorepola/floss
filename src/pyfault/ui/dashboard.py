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
from typing import Dict, List, Any, Optional, Tuple
import os


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
    """Show overview with treemap and ranking."""
    st.header("Overview")
    
    # Extract suspiciousness data
    susp_data = extract_suspiciousness_data(data, formula)
    
    if not susp_data:
        st.warning("No suspiciousness data available")
        return
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.subheader("Suspiciousness Treemap")
        show_treemap(data, formula)
    
    with col2:
        st.subheader("Top Suspicious Lines")
        show_ranking_table(susp_data[:20])  # Top 20


def build_hierarchical_data(data: Dict[str, Any], formula: str, min_score: float = 0.0) -> Dict[str, List]:
    """Build hierarchical data structure for treemap and sunburst visualizations."""
    files_data = data.get('files', {})
    
    labels = []
    parents = []
    values = []
    colors = []
    
    # Root node
    labels.append("Project")
    parents.append("")
    values.append(1)
    colors.append(0.0)
    
    # Simplified approach: Project -> Files -> Classes/Functions
    # Use labels as references for parent-child relationships
    
    for file_path, file_data in files_data.items():
        # Skip files without significant suspiciousness data
        file_suspiciousness = file_data.get('suspiciousness', {})
        if not file_suspiciousness:
            continue
            
        # Check if file has any scores above threshold
        file_scores = []
        for line_scores in file_suspiciousness.values():
            if formula in line_scores and line_scores[formula] >= min_score:
                file_scores.append(line_scores[formula])
        
        if not file_scores:
            continue  # Skip files with no significant scores
        
        # Get just the filename for display (ensure it's unique)
        file_name = Path(file_path).name
        
        # Make file name unique if necessary
        counter = 1
        original_file_name = file_name
        while file_name in labels:
            file_name = f"{original_file_name} ({counter})"
            counter += 1
        
        # Add file
        avg_file_score = sum(file_scores) / len(file_scores)
        file_lines_count = len(file_scores)
        
        labels.append(file_name)
        parents.append("Project")  # All files directly under project
        values.append(max(file_lines_count, 1))
        colors.append(avg_file_score)
        
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
                    line_score = file_suspiciousness[line_str].get(formula, 0.0)
                    if line_score >= min_score:
                        class_scores.append(line_score)
            
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
            
            # Add methods for this class (only with significant scores)
            for func_name, func_info in functions_data.items():
                if func_name.startswith(f"{class_name}."):
                    method_name = func_name.split('.')[-1]
                    
                    method_executed_lines = func_info.get('executed_lines', [])
                    method_scores = []
                    for line_num in method_executed_lines:
                        line_str = str(line_num)
                        if line_str in file_suspiciousness:
                            line_score = file_suspiciousness[line_str].get(formula, 0.0)
                            if line_score >= min_score:
                                method_scores.append(line_score)
                    
                    if not method_scores:
                        continue  # Skip methods with no significant scores
                    
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
        
        # Process standalone functions (not methods, only with significant scores)
        for func_name, func_info in functions_data.items():
            if '.' in func_name or func_name == "" or len(func_name) == 0:
                continue  # Skip methods and global code
            
            func_executed_lines = func_info.get('executed_lines', [])
            func_scores = []
            for line_num in func_executed_lines:
                line_str = str(line_num)
                if line_str in file_suspiciousness:
                    line_score = file_suspiciousness[line_str].get(formula, 0.0)
                    if line_score >= min_score:
                        func_scores.append(line_score)
            
            if not func_scores:
                continue  # Skip functions with no significant scores
            
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
    
    return {
        'labels': labels,
        'parents': parents,
        'values': values,
        'colors': colors
    }


def show_treemap_tab(data: Dict[str, Any], formula: str):
    """Show dedicated treemap tab with detailed hierarchical view."""
    st.header("Hierarchical Treemap")
    
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
    
    hierarchy_data = build_hierarchical_data(data, formula, min_score)
    
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
            colorscale='RdYlBu_r',
            colorbar=dict(title="Suspiciousness Score"),
            line=dict(width=1),
            cmid=0.5
        ),
        hovertemplate="<b>%{label}</b><br>Score: %{color:.3f}<br>Lines: %{value}<extra></extra>",
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
    hierarchy_data = build_hierarchical_data(data, formula, min_score=0.05)  # Small threshold for overview
    
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
            colorscale='RdYlBu_r',
            colorbar=dict(title="Suspiciousness Score"),
            line=dict(width=1),
            cmid=0.5
        ),
        hovertemplate="<b>%{label}</b><br>Score: %{color:.3f}<br>Lines: %{value}<extra></extra>",
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
            'File': Path(item['file']).name,
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


def show_source_code(data: Dict[str, Any], formula: str):
    """Show source code with suspiciousness highlighting."""
    st.header("Source Code")
    
    files_data = data.get('files', {})
    if not files_data:
        st.warning("No file data available")
        return
    
    # File selection
    file_paths = list(files_data.keys())
    selected_file = st.selectbox("Select File", file_paths)
    
    if selected_file:
        show_file_with_highlighting(files_data[selected_file], selected_file, formula)


def show_file_with_highlighting(file_data: Dict, file_path: str, formula: str):
    """Show file content with line highlighting based on suspiciousness."""
    suspiciousness = file_data.get('suspiciousness', {})

    if not suspiciousness:
        st.warning("No suspiciousness data for this file")
        return

    # Try to read the actual file content
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except:
        st.error(f"Could not read file: {file_path}")
        return

    st.subheader(f"File: {Path(file_path).name}")

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
        f'<div style="font-family: monospace; font-size: 12px; background-color: #f8f8f8; padding: 10px; border-radius: 5px; height: 500px; overflow-y: scroll;">'
        + ''.join(highlighted_lines) +
        '</div>',
        unsafe_allow_html=True
    )


def show_coverage_matrix(data: Dict[str, Any]):
    """Show coverage matrix visualization."""
    st.header("Coverage Matrix")
    
    # Extract test and coverage information
    tests_info = data.get('tests', {})
    files_data = data.get('files', {})
    
    if not tests_info or not files_data:
        st.warning("No test or coverage data available")
        return
    
    # Build coverage matrix
    all_tests = tests_info.get('passed', []) + tests_info.get('failed', [])
    all_lines = []
    
    for file_path, file_data in files_data.items():
        contexts = file_data.get('contexts', {})
        for line_num, test_contexts in contexts.items():
            for context in test_contexts:
                if '::' in context:  # It's a test context
                    test_name = context.split('|')[0]  # Remove |run suffix
                    all_lines.append({
                        'file': Path(file_path).name,
                        'line': int(line_num),
                        'test': test_name,
                        'covered': 1
                    })
    
    if not all_lines:
        st.warning("No coverage data found")
        return
    
    # Create pivot table
    df = pd.DataFrame(all_lines)
    if df.empty:
        st.warning("No coverage data to display")
        return
    
    # Create a more manageable view
    pivot_df = df.pivot_table(
        index=['file', 'line'], 
        columns='test', 
        values='covered', 
        fill_value=0
    )
    
    if pivot_df.empty:
        st.warning("No pivot data to display")
        return
    
    st.subheader("Coverage Heatmap")
    
    # Limit size for readability
    max_rows = 50
    max_cols = 20
    
    display_df = pivot_df.iloc[:max_rows, :max_cols]
    
    fig = px.imshow(
        display_df.values,
        x=display_df.columns,
        y=[f"{idx[0]}:{idx[1]}" for idx in display_df.index],
        color_continuous_scale='RdYlBu_r',
        aspect='auto'
    )
    
    fig.update_layout(
        height=max(400, len(display_df) * 20),
        xaxis_title="Tests",
        yaxis_title="Lines",
        title="Test Coverage Matrix"
    )
    
    fig.update_xaxes(tickangle=45)
    
    st.plotly_chart(fig, use_container_width=True)
    
    if len(pivot_df) > max_rows or len(pivot_df.columns) > max_cols:
        st.info(f"Showing {max_rows} rows and {max_cols} columns. Total: {len(pivot_df)} rows, {len(pivot_df.columns)} columns")


def show_sunburst(data: Dict[str, Any], formula: str):
    """Show sunburst visualization with hierarchical Python project structure."""
    st.header("Sunburst View")
    
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
    
    hierarchy_data = build_hierarchical_data(data, formula, min_score)
    
    if not hierarchy_data or len(hierarchy_data['labels']) <= 1:
        st.warning(f"No hierarchical data available with minimum score {min_score:.2f}")
        st.info("Try lowering the minimum score threshold")
        
        # Show fallback with very low threshold
        fallback_data = build_hierarchical_data(data, formula, 0.0)
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
                colorscale='RdYlBu_r',
                colorbar=dict(title="Suspiciousness Score"),
                line=dict(width=2, color="white")
            ),
            hovertemplate="<b>%{label}</b><br>Score: %{color:.3f}<br>Size: %{value}<extra></extra>"
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
                'Element': f"{Path(item['file']).name}:{item['line']}",
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

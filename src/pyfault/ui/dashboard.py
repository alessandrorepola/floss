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
    formulas = data.get('fl_metadata', {}).get('formulas_used', [])
    if not formulas:
        st.error("No formulas found in report")
        return
    
    selected_formula = st.selectbox("SBFL Formula", formulas)
    
    # Main dashboard tabs
    tab1, tab2, tab3, tab4 = st.tabs([
        "Overview", "Source Code", "Coverage Matrix", "Sunburst"
    ])
    
    with tab1:
        show_overview(data, selected_formula)
    
    with tab2:
        show_source_code(data, selected_formula)
    
    with tab3:
        show_coverage_matrix(data)
    
    with tab4:
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
        show_treemap(susp_data)
    
    with col2:
        st.subheader("Top Suspicious Lines")
        show_ranking_table(susp_data[:20])  # Top 20


def show_treemap(susp_data: List[Dict]):
    """Create treemap visualization."""
    if not susp_data:
        return
    
    # Prepare data for treemap
    df_data = []
    for item in susp_data:
        file_name = Path(item['file']).name
        df_data.append({
            'file': file_name,
            'line': item['line'],
            'score': item['score'],
            'label': f"{file_name}:{item['line']}",
            'parent': file_name,
            'size': max(item['score'], 0.01)  # Minimum size for visibility
        })
    
    # Add file level entries
    files = set(item['file'] for item in df_data)
    for file_path in files:
        file_name = Path(file_path).name
        file_items = [item for item in df_data if item['file'] == file_name]
        avg_score = np.mean([item['score'] for item in file_items])
        df_data.append({
            'file': file_name,
            'line': None,
            'score': avg_score,
            'label': file_name,
            'parent': '',
            'size': sum(item['size'] for item in file_items)
        })
    
    df = pd.DataFrame(df_data)
    
    # Create treemap with colors based on scores
    fig = go.Figure(go.Treemap(
        labels=df['label'],
        parents=df['parent'],
        values=df['size'],
        textinfo="label+value",
        marker=dict(
            colors=df['score'],
            colorscale='Reds',
            colorbar=dict(title="Suspiciousness"),
            line=dict(width=2),
            cmid=0.5
        ),
        hovertemplate="<b>%{label}</b><br>Score: %{color:.3f}<extra></extra>"
    ))
    
    fig.update_layout(
        height=500,
        margin=dict(t=0, l=0, r=0, b=0)
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
        code_html = f"{indent}{safe_content.lstrip(' \t')}"
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
    """Show sunburst visualization."""
    st.header("Sunburst View")
    
    susp_data = extract_suspiciousness_data(data, formula)
    
    if not susp_data:
        st.warning("No suspiciousness data available")
        return
    
    # Create hierarchical sunburst with files and lines
    try:
        # Group by files first for better hierarchy
        files_dict = {}
        for item in susp_data:
            file_name = Path(item['file']).name
            if file_name not in files_dict:
                files_dict[file_name] = []
            files_dict[file_name].append(item)
        
        labels = []
        parents = []
        values = []
        colors = []
        
        # Root level
        labels.append("Project")
        parents.append("")
        values.append(len(susp_data))
        colors.append(np.mean([item['score'] for item in susp_data]))
        
        # File level
        for file_name, items in files_dict.items():
            labels.append(file_name)
            parents.append("Project")
            values.append(len(items))
            colors.append(np.mean([item['score'] for item in items]))
            
            # Line level
            for item in items:
                line_label = f"Line {item['line']}"
                labels.append(line_label)
                parents.append(file_name)
                values.append(1)
                colors.append(item['score'])
        
        fig = go.Figure(go.Sunburst(
            labels=labels,
            parents=parents,
            values=values,
            branchvalues="total",
            marker=dict(
                colors=colors,
                colorscale='Reds',
                colorbar=dict(title="Suspiciousness"),
                line=dict(width=1)
            ),
            hovertemplate="<b>%{label}</b><br>Score: %{color:.3f}<extra></extra>",
            maxdepth=3
        ))
        
        fig.update_layout(
            height=600,
            title=f"Code Hierarchy - {formula.title()}",
            font_size=11
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error creating sunburst: {e}")
        # Fallback to simple bar chart
        st.subheader("Alternative View")
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

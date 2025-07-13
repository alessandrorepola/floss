"""
Enhanced HTML reporter for fault localization results.

This module generates interactive HTML reports with source code viewing and visualizations,
similar to GZoltar's HTML output functionality.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from jinja2 import Environment, FileSystemLoader

from ..core.models import FaultLocalizationResult, SuspiciousnessScore

logger = logging.getLogger(__name__)


class HTMLReporter:
    """
    Generates enhanced HTML reports for fault localization results.
    
    Creates interactive HTML reports with source code viewing, rankings, visualizations, and
    detailed analysis, similar to GZoltar's HTML output functionality.
    
    Example:
        >>> reporter = HTMLReporter(Path('output'))
        >>> reporter.generate_report(results)
    """
    
    def __init__(self, output_dir: Path):
        """
        Initialize the HTML reporter.
        
        Args:
            output_dir: Directory where HTML files will be written
        """
        self.output_dir = output_dir
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Setup Jinja2 environment
        template_dir = Path(__file__).parent / "templates"
        self.jinja_env = Environment(
            loader=FileSystemLoader(template_dir),
            autoescape=True
        )
    
    def generate_report(self, result: FaultLocalizationResult) -> None:
        """
        Generate enhanced HTML reports for the fault localization results.
        
        Args:
            result: Fault localization results to report
        """
        if not result or not result.scores:
            logger.warning("No fault localization results to report")
            return
            
        logger.info(f"Generating HTML report with {len(result.scores)} formulas")
        
        try:
            # Generate data for interactive visualizations FIRST
            self._write_visualization_data(result)
            
            # Generate source code files
            self._generate_source_files(result)
            
            # Generate main report
            self._write_main_report(result)
            
            # Generate individual formula reports
            for formula_name in result.scores:
                self._write_formula_report(formula_name, result)
            
            # Generate package overview
            self._write_package_overview(result)
            
            # Copy static assets (CSS, JS) - this must be after visualization data generation
            self._write_static_files()
            
            logger.info(f"HTML report generated successfully in {self.output_dir}")
        except Exception as e:
            logger.error(f"Failed to generate HTML report: {e}")
            raise
    
    def _generate_source_files(self, result: FaultLocalizationResult) -> None:
        """Generate HTML files for source code viewing."""
        source_dir = self.output_dir / "source"
        source_dir.mkdir(exist_ok=True)
        
        # Group elements by file
        files_with_elements = {}
        for formula_name, scores in result.scores.items():
            for score in scores:
                file_path = score.element.file_path
                if file_path not in files_with_elements:
                    files_with_elements[file_path] = []
                files_with_elements[file_path].append(score)
        
        # Generate HTML for each source file
        for file_path, element_scores in files_with_elements.items():
            self._write_source_file(file_path, element_scores, source_dir)
    
    def _write_source_file(self, file_path: Path, element_scores: List[SuspiciousnessScore], source_dir: Path) -> None:
        """Write HTML for a single source file with highlighting."""
        try:
            # Read source content
            with open(file_path, 'r', encoding='utf-8') as f:
                source_lines = f.readlines()
        except (FileNotFoundError, UnicodeDecodeError) as e:
            # If we can't read the file, create a placeholder
            logger.warning(f"Could not read source file {file_path}: {e}")
            source_lines = ["# Source file not available\n"]
        except Exception as e:
            logger.error(f"Unexpected error reading file {file_path}: {e}")
            source_lines = ["# Error reading source file\n"]
        
        # Prepare line data with suspiciousness scores
        line_data = []
        line_scores = {}
        
        # Group scores by line
        for score in element_scores:
            line_num = score.element.line_number
            if line_num not in line_scores:
                line_scores[line_num] = []
            line_scores[line_num].append(score)
        
        # Process each line
        for line_num, line_content in enumerate(source_lines, 1):
            scores_for_line = line_scores.get(line_num, [])
            max_score = max((s.score for s in scores_for_line), default=0.0)
            
            line_data.append({
                'number': line_num,
                'content': line_content.rstrip(),
                'scores': scores_for_line,
                'max_score': max_score,
                'suspicion_level': self._get_suspicion_level(max_score)
            })
        
        # Generate HTML filename
        relative_path = file_path.name.replace('.py', '')
        html_filename = f"{relative_path}.html"
        
        # Render template
        try:
            template = self.jinja_env.get_template("source_file.html")
            html_content = template.render(
                title=f"Source: {file_path.name}",
                file_path=str(file_path),
                lines=line_data,
                element_scores=element_scores
            )
            
            # Write file
            with open(source_dir / html_filename, 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            logger.debug(f"Source file HTML written: {html_filename}")
        except Exception as e:
            logger.error(f"Failed to write source file HTML for {file_path}: {e}")
            # Continue with other files rather than crashing
    
    def _get_suspicion_level(self, score: float) -> str:
        """Get CSS class for suspicion level."""
        if score >= 0.8:
            return "very-high"
        elif score >= 0.6:
            return "high"
        elif score >= 0.3:
            return "medium"
        elif score > 0:
            return "low"
        else:
            return "none"
    
    def _write_main_report(self, result: FaultLocalizationResult) -> None:
        """Write the enhanced main HTML report."""
        try:
            template = self.jinja_env.get_template("main_report.html")
        except Exception as e:
            logger.error(f"Failed to load main report template: {e}")
            raise RuntimeError(f"Template loading failed: {e}")
        
        # Prepare data for template
        template_data = {
            'title': 'PyFault Localization Report',
            'execution_time': result.execution_time,
            'formulas': list(result.scores.keys()),
            'top_elements': self._get_top_elements_summary(result),
            'test_stats': self._get_test_statistics(result),
            'coverage_stats': self._get_coverage_statistics(result),
            'package_summary': self._get_package_summary(result)
        }
        
        # Render and write
        try:
            html_content = template.render(**template_data)
            
            with open(self.output_dir / "index.html", 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info("Main HTML report written successfully")
        except Exception as e:
            logger.error(f"Failed to write main HTML report: {e}")
            raise RuntimeError(f"Report generation failed: {e}")
    
    def _write_formula_report(self, formula_name: str, result: FaultLocalizationResult) -> None:
        """Write enhanced detailed report for a specific formula."""
        try:
            template = self.jinja_env.get_template("formula_report.html")
        except Exception as e:
            logger.error(f"Failed to load formula report template: {e}")
            raise RuntimeError(f"Template loading failed: {e}")
        
        scores = result.scores[formula_name]
        
        # Prepare enhanced score data with source links
        enhanced_scores = []
        for score in scores[:100]:  # Top 100 elements
            source_file = score.element.file_path.name.replace('.py', '') + '.html'
            enhanced_scores.append({
                'rank': score.rank,
                'element': score.element,
                'score': score.score,
                'suspicion_level': self._get_suspicion_level(score.score),
                'source_link': f"source/{source_file}#line-{score.element.line_number}"
            })
        
        # Prepare data
        template_data = {
            'title': f'PyFault - {formula_name.title()} Results',
            'formula_name': formula_name,
            'scores': enhanced_scores,
            'total_elements': len(scores),
            'metadata': result.metadata
        }
        
        # Render and write
        try:
            html_content = template.render(**template_data)
            
            with open(self.output_dir / f"{formula_name}_ranking.html", 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            logger.info(f"Formula report for {formula_name} written successfully")
        except Exception as e:
            logger.error(f"Failed to write formula report for {formula_name}: {e}")
            raise RuntimeError(f"Formula report generation failed: {e}")
    
    def _write_package_overview(self, result: FaultLocalizationResult) -> None:
        """Write package overview with file-level statistics."""
        try:
            template = self.jinja_env.get_template("package_overview.html")
        except Exception as e:
            logger.error(f"Failed to load package overview template: {e}")
            raise RuntimeError(f"Template loading failed: {e}")
        
        # Group elements by file and calculate statistics
        file_stats = {}
        for formula_name, scores in result.scores.items():
            for score in scores:
                file_path = score.element.file_path
                if file_path not in file_stats:
                    file_stats[file_path] = {
                        'elements': 0,
                        'max_scores': {},
                        'avg_scores': {},
                        'total_score': {}
                    }
                
                file_stats[file_path]['elements'] += 1
                
                if formula_name not in file_stats[file_path]['max_scores']:
                    file_stats[file_path]['max_scores'][formula_name] = 0
                    file_stats[file_path]['total_score'][formula_name] = 0
                
                file_stats[file_path]['max_scores'][formula_name] = max(
                    file_stats[file_path]['max_scores'][formula_name], 
                    score.score
                )
                file_stats[file_path]['total_score'][formula_name] += score.score
        
        # Calculate averages
        for file_path, stats in file_stats.items():
            for formula_name in stats['total_score']:
                stats['avg_scores'][formula_name] = (
                    stats['total_score'][formula_name] / stats['elements']
                    if stats['elements'] > 0 else 0
                )
        
        template_data = {
            'title': 'Package Overview',
            'file_stats': file_stats,
            'formulas': list(result.scores.keys())
        }
        
        try:
            html_content = template.render(**template_data)
            
            with open(self.output_dir / "package_overview.html", 'w', encoding='utf-8') as f:
                f.write(html_content)
                
            logger.info("Package overview report written successfully")
        except Exception as e:
            logger.error(f"Failed to write package overview report: {e}")
            raise RuntimeError(f"Package overview generation failed: {e}")
    
    def _write_visualization_data(self, result: FaultLocalizationResult) -> None:
        """Generate visualization data for embedding in HTML."""
        try:
            logger.info("Generating visualization data...")
            
            # Generate data
            sunburst_data = self._generate_sunburst_data(result)
            ranking_data = self._generate_ranking_data(result)
            
            logger.info(f"Sunburst data generated: {len(sunburst_data.get('children', []))} directories")
            logger.info(f"Ranking data generated: {len(ranking_data.get('items', []))} items")
            
            # Store data as instance variables for embedding
            self._sunburst_data = sunburst_data
            self._ranking_data = ranking_data
            
            # Debug logging
            if sunburst_data.get('children'):
                logger.debug(f"Sunburst sample: {sunburst_data['children'][0] if sunburst_data['children'] else 'None'}")
            if ranking_data.get('items'):
                logger.debug(f"Ranking sample: {ranking_data['items'][0] if ranking_data['items'] else 'None'}")
            
            logger.info("Visualization data prepared for embedding")
            
        except Exception as e:
            logger.error(f"Error generating visualization data: {e}")
            # Fallback data with some content for testing
            self._sunburst_data = {
                "name": "PyFault", 
                "children": [{
                    "name": "Error",
                    "value": 1,
                    "score": 0,
                    "suspiciousness": 0
                }]
            }
            self._ranking_data = {
                "items": [{
                    "name": "Error generating data",
                    "suspiciousness": 0,
                    "score": 0,
                    "rank": 1
                }]
            }

    def _generate_sunburst_data(self, result: FaultLocalizationResult) -> Dict[str, Any]:
        """Generate data for sunburst visualization."""
        # Use the first formula for the sunburst
        primary_formula = list(result.scores.keys())[0] if result.scores else None
        
        if not primary_formula:
            return {"name": "root", "children": []}
        
        scores = result.scores[primary_formula]
        
        if not scores:
            return {"name": "root", "children": []}
        
        # Group by directory and file
        hierarchy = {}
        
        for score in scores:
            file_path = score.element.file_path
            parent_dir = file_path.parent.name if file_path.parent.name else "src"
            file_name = file_path.name
            
            if parent_dir not in hierarchy:
                hierarchy[parent_dir] = {}
            
            if file_name not in hierarchy[parent_dir]:
                hierarchy[parent_dir][file_name] = {
                    'elements': 0,
                    'total_score': 0,
                    'max_score': 0
                }
            
            hierarchy[parent_dir][file_name]['elements'] += 1
            hierarchy[parent_dir][file_name]['total_score'] += score.score
            hierarchy[parent_dir][file_name]['max_score'] = max(
                hierarchy[parent_dir][file_name]['max_score'], 
                score.score
            )
        
        # Convert to sunburst format
        sunburst = {
            "name": "PyFault",
            "children": []
        }
        
        for dir_name, files in hierarchy.items():
            dir_node = {
                "name": dir_name,
                "children": [],
                "value": sum(stats['elements'] for stats in files.values())
            }
            
            for file_name, stats in files.items():
                avg_score = stats['total_score'] / stats['elements'] if stats['elements'] > 0 else 0
                file_node = {
                    "name": file_name,
                    "value": stats['elements'],
                    "score": avg_score,
                    "max_score": stats['max_score'],
                    "suspiciousness": avg_score
                }
                dir_node["children"].append(file_node)
            
            if dir_node["children"]:  # Only add directories with files
                sunburst["children"].append(dir_node)
        
        # If no valid data, create a simple fallback
        if not sunburst["children"]:
            sunburst["children"] = [{
                "name": "No Data",
                "value": 1,
                "score": 0,
                "suspiciousness": 0
            }]
        
        return sunburst
    
    def _generate_ranking_data(self, result: FaultLocalizationResult) -> Dict[str, Any]:
        """Generate data for ranking charts."""
        # Use the first formula for the main ranking chart
        primary_formula = list(result.scores.keys())[0] if result.scores else None
        
        if not primary_formula:
            return {"items": []}
        
        scores = result.scores[primary_formula]
        top_scores = scores[:20]  # Top 20 for charts
        
        ranking_items = [
            {
                "name": str(score.element),
                "element": str(score.element),
                "suspiciousness": score.score,
                "score": score.score,
                "rank": score.rank,
                "file": score.element.file_path.name,
                "line": score.element.line_number
            }
            for score in top_scores
        ]
        
        return {"items": ranking_items}
    
    def _get_top_elements_summary(self, result: FaultLocalizationResult) -> Dict[str, List[Dict[str, Any]]]:
        """Get top suspicious elements for each formula."""
        summary = {}
        
        for formula_name, scores in result.scores.items():
            top_scores = scores[:10]  # Top 10
            summary[formula_name] = [
                {
                    'element': str(score.element),
                    'file': str(score.element.file_path),
                    'line': score.element.line_number,
                    'score': score.score,
                    'rank': score.rank,
                    'source_link': f"source/{score.element.file_path.name.replace('.py', '')}.html#line-{score.element.line_number}"
                }
                for score in top_scores
            ]
        
        return summary
    
    def _get_test_statistics(self, result: FaultLocalizationResult) -> Dict[str, Any]:
        """Get test execution statistics."""
        matrix = result.coverage_matrix
        
        passed_tests = sum(1 for outcome in matrix.test_outcomes 
                          if outcome.value == 'passed')
        failed_tests = sum(1 for outcome in matrix.test_outcomes 
                          if outcome.value in ('failed', 'error'))
        total_tests = len(matrix.test_outcomes)
        
        return {
            'total': total_tests,
            'passed': passed_tests,
            'failed': failed_tests,
            'pass_rate': (passed_tests / total_tests * 100) if total_tests > 0 else 0
        }
    
    def _get_coverage_statistics(self, result: FaultLocalizationResult) -> Dict[str, Any]:
        """Get coverage statistics."""
        import numpy as np
        matrix = result.coverage_matrix
        total_elements = result.metadata.get('total_elements', len(matrix.code_elements))
        covered_elements_count = int(np.any(matrix.matrix, axis=0).sum())
        coverage_percentage = (covered_elements_count / total_elements * 100) if total_elements > 0 else 0
        return {
            'total_elements': total_elements,
            'covered_elements': covered_elements_count,
            'coverage_percentage': coverage_percentage
        }
    
    def _get_package_summary(self, result: FaultLocalizationResult) -> Dict[str, Any]:
        """Get package-level summary statistics."""
        # Count files and packages
        files = set()
        packages = set()
        
        for scores in result.scores.values():
            for score in scores:
                files.add(score.element.file_path)
                packages.add(score.element.file_path.parent)
        
        return {
            'total_files': len(files),
            'total_packages': len(packages)
        }
    
    def _write_static_files(self) -> None:
        """Copy static assets (CSS, JS) to output directory and write generated files."""
        import shutil
        static_dir = Path(__file__).parent / "static"
        output_static_dir = self.output_dir / "static"
        output_static_dir.mkdir(exist_ok=True)

        for asset in static_dir.glob("**/*"):
            if asset.is_file():
                shutil.copy(asset, output_static_dir / asset.name)

        # Scrivi anche i file generati (style.css, script.js) nella root di output
        css_content = self._get_enhanced_css_content()
        with open(self.output_dir / "style.css", 'w', encoding='utf-8') as f:
            f.write(css_content)

        js_content = self._get_enhanced_js_content()
        with open(self.output_dir / "script.js", 'w', encoding='utf-8') as f:
            f.write(js_content)
    
    def _get_enhanced_css_content(self) -> str:
        """Get enhanced CSS stylesheet content."""
        return '''
/* PyFault Enhanced HTML Report Styles */
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    line-height: 1.6;
    color: #333;
    background-color: #f8f9fa;
}

.container {
    max-width: 1400px;
    margin: 0 auto;
    padding: 20px;
}

header {
    text-align: center;
    margin-bottom: 40px;
    padding: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

header h1 {
    color: #2c3e50;
    margin-bottom: 10px;
}

.subtitle {
    color: #6c757d;
    font-size: 1.1em;
}

nav {
    margin-bottom: 20px;
    padding: 15px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

nav a {
    color: #007bff;
    text-decoration: none;
    font-weight: 500;
    margin-right: 20px;
    padding: 8px 12px;
    border-radius: 4px;
    transition: background-color 0.2s;
}

nav a:hover {
    background-color: #e7f3ff;
    text-decoration: none;
}

.stats-grid, .formula-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.stat-card, .formula-card {
    background: white;
    padding: 25px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
    transition: transform 0.2s, box-shadow 0.2s;
}

.stat-card:hover, .formula-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 8px rgba(0,0,0,0.15);
}

.stat-card h3 {
    font-size: 2.5em;
    color: #007bff;
    margin-bottom: 5px;
}

.formula-card h3 {
    color: #2c3e50;
    margin-bottom: 15px;
}

.btn {
    display: inline-block;
    padding: 10px 20px;
    background: #007bff;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    margin-top: 15px;
    transition: background-color 0.2s;
}

.btn:hover {
    background: #0056b3;
    text-decoration: none;
}

.btn-secondary {
    background: #6c757d;
}

.btn-secondary:hover {
    background: #545b62;
}

section {
    background: white;
    padding: 30px;
    margin-bottom: 30px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

section h2 {
    color: #2c3e50;
    margin-bottom: 20px;
    border-bottom: 2px solid #e9ecef;
    padding-bottom: 10px;
}

.ranking-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
}

.ranking-table th,
.ranking-table td {
    padding: 12px;
    text-align: left;
    border-bottom: 1px solid #e9ecef;
}

.ranking-table th {
    background: #f8f9fa;
    font-weight: 600;
    color: #495057;
    cursor: pointer;
    user-select: none;
}

.ranking-table th:hover {
    background: #e9ecef;
}

.ranking-table tr:hover {
    background: #f8f9fa;
}

/* Suspicion level styles */
.very-high-suspicion {
    background-color: #dc3545;
    color: white;
}

.high-suspicion {
    background-color: #fd7e14;
    color: white;
}

.medium-suspicion {
    background-color: #ffc107;
    color: #212529;
}

.low-suspicion {
    background-color: #28a745;
    color: white;
}

.none-suspicion {
    background-color: #f8f9fa;
}

/* Source code styles */
.source-code {
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 14px;
    line-height: 1.4;
    background: #f8f9fa;
    border-radius: 4px;
    overflow-x: auto;
}

.line-number {
    display: inline-block;
    width: 60px;
    text-align: right;
    padding-right: 15px;
    color: #6c757d;
    border-right: 1px solid #dee2e6;
    margin-right: 15px;
    user-select: none;
}

.source-line {
    padding: 2px 0;
    white-space: pre;
}

.source-line:hover {
    background-color: #e9ecef;
}

.source-line.very-high {
    background-color: #f8d7da;
    border-left: 4px solid #dc3545;
}

.source-line.high {
    background-color: #fdf2e9;
    border-left: 4px solid #fd7e14;
}

.source-line.medium {
    background-color: #fff3cd;
    border-left: 4px solid #ffc107;
}

.source-line.low {
    background-color: #d4edda;
    border-left: 4px solid #28a745;
}

/* Visualization container */
.visualization-container {
    margin: 20px 0;
    padding: 20px;
    background: white;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
}

#sunburst-chart, #ranking-chart {
    width: 100%;
    height: 500px;
}

/* Tooltip styles */
.tooltip {
    position: absolute;
    padding: 10px;
    background: rgba(0, 0, 0, 0.8);
    color: white;
    border-radius: 4px;
    font-size: 12px;
    pointer-events: none;
    z-index: 1000;
}

/* Formula results */
.formula-results {
    margin-bottom: 30px;
}

.formula-results h3 {
    color: #495057;
    margin-bottom: 15px;
}

/* Package overview styles */
.package-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin-top: 20px;
}

.package-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    border-left: 4px solid #007bff;
}

.package-card h4 {
    color: #2c3e50;
    margin-bottom: 10px;
}

.score-badge {
    display: inline-block;
    padding: 2px 8px;
    border-radius: 12px;
    font-size: 0.8em;
    font-weight: bold;
    margin: 2px;
}

.score-badge.very-high {
    background: #dc3545;
    color: white;
}

.score-badge.high {
    background: #fd7e14;
    color: white;
}

.score-badge.medium {
    background: #ffc107;
    color: #212529;
}

.score-badge.low {
    background: #28a745;
    color: white;
}

/* Responsive design */
@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .stats-grid, .formula-grid, .package-grid {
        grid-template-columns: 1fr;
    }
    
    .ranking-table {
        font-size: 0.9em;
    }
    
    .ranking-table th,
    .ranking-table td {
        padding: 8px;
    }
    
    nav a {
        display: block;
        margin: 5px 0;
    }
}

/* Loading animation */
.loading {
    display: inline-block;
    width: 20px;
    height: 20px;
    border: 3px solid #f3f3f3;
    border-top: 3px solid #007bff;
    border-radius: 50%;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    0% { transform: rotate(0deg); }
    100% { transform: rotate(360deg); }
}
        '''
    
    def _get_enhanced_js_content(self) -> str:
        """Get enhanced JavaScript content with embedded data."""
        # Embed data directly in JavaScript to avoid CORS issues
        sunburst_json = json.dumps(getattr(self, '_sunburst_data', {"name": "root", "children": []}))
        ranking_json = json.dumps(getattr(self, '_ranking_data', {"items": []}))
        
        return f'''
// PyFault Enhanced HTML Report JavaScript
// Embedded data to avoid CORS issues
const SUNBURST_DATA = {sunburst_json};
const RANKING_DATA = {ranking_json};

document.addEventListener('DOMContentLoaded', function() {{
    console.log('PyFault enhanced report loaded');
    
    // Initialize interactive features
    initializeSorting();
    initializeTooltips();
    
    // Load visualizations with embedded data
    loadVisualizationsWithEmbeddedData();
    
    // Smooth scrolling for anchor links
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {{
        anchor.addEventListener('click', function (e) {{
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {{
                target.scrollIntoView({{
                    behavior: 'smooth',
                    block: 'start'
                }});
            }}
        }});
    }});
}});

function loadVisualizationsWithEmbeddedData() {{
    // Check if D3.js is available
    if (typeof d3 !== 'undefined') {{
        console.log('D3.js found, loading visualizations with embedded data');
        loadSunburstChartWithData(SUNBURST_DATA);
        loadRankingChartWithData(RANKING_DATA);
    }} else {{
        console.log('D3.js not found, loading from CDN');
        const script = document.createElement('script');
        script.src = 'https://d3js.org/d3.v7.min.js';
        script.crossOrigin = 'anonymous';
        
        script.onload = function() {{
            console.log('D3.js loaded from CDN');
            loadSunburstChartWithData(SUNBURST_DATA);
            loadRankingChartWithData(RANKING_DATA);
        }};
        
        script.onerror = function() {{
            console.warn('Failed to load D3.js from CDN');
            showVisualizationError();
        }};
        
        document.head.appendChild(script);
        
        // Fallback timeout
        setTimeout(() => {{
            if (typeof d3 === 'undefined') {{
                console.warn('D3.js loading timeout');
                showVisualizationError();
            }}
        }}, 10000);
    }}
}}

function showVisualizationError() {{
    const sunburstContainer = document.getElementById('sunburst-chart');
    const rankingContainer = document.getElementById('ranking-chart');
    
    const errorMessage = `
        <div style="text-align: center; padding: 40px; color: #6c757d;">
            <h4>📊 Interactive Visualizations</h4>
            <p>Visualizations require an internet connection to load D3.js library.</p>
            <p>Data is available in the tables below.</p>
        </div>
    `;
    
    if (sunburstContainer) {{
        sunburstContainer.innerHTML = errorMessage;
    }}
    if (rankingContainer) {{
        rankingContainer.innerHTML = errorMessage;
    }}
}}

function loadSunburstChartWithData(data) {{
    const container = document.getElementById('sunburst-chart');
    if (!container) {{
        console.warn('Sunburst container not found');
        return;
    }}
    
    console.log('Creating sunburst chart with embedded data:', data);
    
    try {{
        createSunburstChart(container, data);
    }} catch (error) {{
        console.error('Error creating sunburst chart:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #dc3545;">
                ⚠️ Error creating sunburst visualization
            </div>
        `;
    }}
}}

function loadRankingChartWithData(data) {{
    const container = document.getElementById('ranking-chart');
    if (!container) {{
        console.warn('Ranking container not found');
        return;
    }}
    
    console.log('Creating ranking chart with embedded data:', data);
    
    try {{
        createRankingChart(container, data);
    }} catch (error) {{
        console.error('Error creating ranking chart:', error);
        container.innerHTML = `
            <div style="text-align: center; padding: 20px; color: #dc3545;">
                ⚠️ Error creating ranking visualization
            </div>
        `;
    }}
}}

function createSunburstChart(container, data) {{
    // Clear container
    container.innerHTML = '';
    
    console.log('Sunburst data received:', data);
    
    if (!data || !data.children || data.children.length === 0) {{
        console.warn('No sunburst data available');
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #6c757d;">
                <p>📊 No data available for sunburst visualization</p>
                <p>Debug: data = ${{JSON.stringify(data)}}</p>
            </div>
        `;
        return;
    }}
    
    const width = container.clientWidth || 600;
    const height = 500;
    const radius = Math.min(width, height) / 2 - 10;
    
    // Create SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height)
        .append('g')
        .attr('transform', `translate(${{width / 2}},${{height / 2}})`);
    
    // Create partition layout
    const partition = d3.partition()
        .size([2 * Math.PI, radius]);
    
    // Create hierarchy
    const root = d3.hierarchy(data)
        .sum(d => d.value || 1)
        .sort((a, b) => (b.value || 0) - (a.value || 0));
    
    partition(root);
    
    console.log('Sunburst hierarchy created with', root.descendants().length, 'nodes');
    
    // Color scale
    const color = d3.scaleOrdinal(d3.schemeCategory10);
    
    // Create arc generator
    const arc = d3.arc()
        .startAngle(d => d.x0)
        .endAngle(d => d.x1)
        .innerRadius(d => d.y0)
        .outerRadius(d => d.y1);
    
    // Add arcs
    const paths = svg.selectAll('path')
        .data(root.descendants().filter(d => d.depth > 0))
        .enter().append('path')
        .attr('d', arc)
        .style('fill', d => color(d.depth))
        .style('stroke', '#fff')
        .style('stroke-width', 1)
        .style('opacity', 0.8)
        .on('mouseover', function(event, d) {{
            d3.select(this).style('opacity', 1);
            showTooltip(event, d);
        }})
        .on('mouseout', function(event, d) {{
            d3.select(this).style('opacity', 0.8);
            hideTooltip();
        }});
    
    console.log('Sunburst paths created:', paths.size());
    
    // Add labels for larger segments
    const labels = svg.selectAll('text')
        .data(root.descendants().filter(d => d.depth > 0 && (d.x1 - d.x0) > 0.1))
        .enter().append('text')
        .attr('transform', d => {{
            const angle = (d.x0 + d.x1) / 2;
            const radius = (d.y0 + d.y1) / 2;
            return `rotate(${{angle * 180 / Math.PI - 90}}) translate(${{radius}},0) rotate(${{angle > Math.PI ? 180 : 0}})`;
        }})
        .attr('dy', '0.35em')
        .style('text-anchor', d => (d.x0 + d.x1) / 2 > Math.PI ? 'end' : 'start')
        .style('font-size', '12px')
        .style('fill', '#333')
        .text(d => d.data.name);
    
    console.log('Sunburst labels created:', labels.size());
    
    if (paths.size() === 0) {{
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #dc3545;">
                <p>⚠️ No visual elements created for sunburst</p>
                <p>Debug: ${{root.descendants().length}} total nodes, ${{root.descendants().filter(d => d.depth > 0).length}} visible nodes</p>
            </div>
        `;
    }}
}}

function createRankingChart(container, data) {{
    // Clear container
    container.innerHTML = '';
    
    console.log('Ranking data received:', data);
    
    if (!data || !data.items || data.items.length === 0) {{
        console.warn('No ranking data available');
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #6c757d;">
                <p>📊 No ranking data available</p>
                <p>Debug: data = ${{JSON.stringify(data)}}</p>
            </div>
        `;
        return;
    }}
    
    const width = container.clientWidth || 600;
    const height = 400;
    const margin = {{top: 20, right: 30, bottom: 60, left: 100}};
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;
    
    // Take top 20 items for better visualization
    const topItems = data.items.slice(0, 20);
    console.log('Creating ranking chart with', topItems.length, 'items');
    
    // Create SVG
    const svg = d3.select(container)
        .append('svg')
        .attr('width', width)
        .attr('height', height);
    
    const g = svg.append('g')
        .attr('transform', `translate(${{margin.left}},${{margin.top}})`);
    
    // Scales
    const maxScore = d3.max(topItems, d => d.suspiciousness || 0);
    console.log('Max suspiciousness score:', maxScore);
    
    const x = d3.scaleLinear()
        .domain([0, maxScore || 1])
        .range([0, chartWidth]);
    
    const y = d3.scaleBand()
        .domain(topItems.map((d, i) => i))  // Use index instead of name for better spacing
        .range([0, chartHeight])
        .padding(0.1);
    
    // Color scale based on suspiciousness
    const colorScale = d3.scaleSequential(d3.interpolateReds)
        .domain([0, maxScore || 1]);
    
    // Add bars
    const bars = g.selectAll('.bar')
        .data(topItems)
        .enter().append('rect')
        .attr('class', 'bar')
        .attr('x', 0)
        .attr('y', (d, i) => y(i))
        .attr('width', d => x(d.suspiciousness || 0))
        .attr('height', y.bandwidth())
        .style('fill', d => colorScale(d.suspiciousness || 0))
        .style('stroke', '#333')
        .style('stroke-width', 0.5)
        .on('mouseover', function(event, d) {{
            showTooltip(event, d);
        }})
        .on('mouseout', hideTooltip);
    
    console.log('Ranking bars created:', bars.size());
    
    // Add x-axis
    g.append('g')
        .attr('transform', `translate(0,${{chartHeight}})`)
        .call(d3.axisBottom(x))
        .append('text')
        .attr('x', chartWidth / 2)
        .attr('y', 40)
        .style('text-anchor', 'middle')
        .style('fill', '#333')
        .text('Suspiciousness Score');
    
    // Add y-axis with element names
    g.append('g')
        .call(d3.axisLeft(y).tickFormat(i => {{
            const item = topItems[i];
            return item ? item.name.slice(0, 30) + (item.name.length > 30 ? '...' : '') : '';
        }}))
        .selectAll('text')
        .style('font-size', '10px');
    
    if (bars.size() === 0) {{
        container.innerHTML = `
            <div style="text-align: center; padding: 40px; color: #dc3545;">
                <p>⚠️ No bars created for ranking chart</p>
                <p>Debug: ${{topItems.length}} items processed</p>
            </div>
        `;
    }}
}}

// Tooltip functions
let tooltip;

function showTooltip(event, d) {{
    if (!tooltip) {{
        tooltip = d3.select('body').append('div')
            .style('position', 'absolute')
            .style('padding', '10px')
            .style('background', 'rgba(0, 0, 0, 0.8)')
            .style('color', 'white')
            .style('border-radius', '5px')
            .style('pointer-events', 'none')
            .style('opacity', 0);
    }}
    
    let content = `<strong>${{d.data?.name || d.name}}</strong>`;
    if (d.suspiciousness !== undefined) {{
        content += `<br/>Suspiciousness: ${{d.suspiciousness.toFixed(4)}}`;
    }}
    if (d.value !== undefined) {{
        content += `<br/>Value: ${{d.value}}`;
    }}
    
    tooltip.html(content)
        .style('left', (event.pageX + 10) + 'px')
        .style('top', (event.pageY - 10) + 'px')
        .transition()
        .duration(200)
        .style('opacity', 1);
}}

function hideTooltip() {{
    if (tooltip) {{
        tooltip.transition()
            .duration(200)
            .style('opacity', 0);
    }}
}}

// Initialize sorting and other interactive features
function initializeSorting() {{
    const tables = document.querySelectorAll('.ranking-table');
    tables.forEach(table => {{
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {{
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => sortTable(table, index));
        }});
    }});
}}

function initializeTooltips() {{
    // Tooltip initialization code would go here
    console.log('Tooltips initialized');
}}

function sortTable(table, column) {{
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {{
        const aVal = a.cells[column].textContent.trim();
        const bVal = b.cells[column].textContent.trim();
        
        // Try to parse as numbers
        const aNum = parseFloat(aVal);
        const bNum = parseFloat(bVal);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {{
            return bNum - aNum; // Descending for numbers
        }}
        
        return aVal.localeCompare(bVal);
    }});
    
    rows.forEach(row => tbody.appendChild(row));
}}
        '''

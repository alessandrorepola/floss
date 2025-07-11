"""
HTML reporter for fault localization results.

This module generates interactive HTML reports with visualizations,
similar to GZoltar's HTML output functionality.
"""

from pathlib import Path
from typing import Dict, List, Any
from jinja2 import Template

from ..core.models import FaultLocalizationResult, SuspiciousnessScore


class HTMLReporter:
    """
    Generates HTML reports for fault localization results.
    
    Creates interactive HTML reports with rankings, visualizations, and
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
    
    def generate_report(self, result: FaultLocalizationResult) -> None:
        """
        Generate HTML reports for the fault localization results.
        
        Args:
            result: Fault localization results to report
        """
        # Generate main report
        self._write_main_report(result)
        
        # Generate individual formula reports
        for formula_name in result.scores:
            self._write_formula_report(formula_name, result)
        
        # Copy static assets (CSS, JS)
        self._write_static_files()
    
    def _write_main_report(self, result: FaultLocalizationResult) -> None:
        """Write the main HTML report."""
        template_str = self._get_main_template()
        template = Template(template_str)
        
        # Prepare data for template
        template_data = {
            'title': 'PyFault Localization Report',
            'metadata': result.metadata,
            'execution_time': result.execution_time,
            'formulas': list(result.scores.keys()),
            'top_elements': self._get_top_elements_summary(result),
            'test_stats': self._get_test_statistics(result),
            'coverage_stats': self._get_coverage_statistics(result)
        }
        
        # Render and write
        html_content = template.render(**template_data)
        
        with open(self.output_dir / "index.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _write_formula_report(self, formula_name: str, result: FaultLocalizationResult) -> None:
        """Write detailed report for a specific formula."""
        template_str = self._get_formula_template()
        template = Template(template_str)
        
        scores = result.scores[formula_name]
        
        # Prepare data
        template_data = {
            'title': f'PyFault - {formula_name.title()} Results',
            'formula_name': formula_name,
            'scores': scores[:100],  # Top 100 elements
            'total_elements': len(scores),
            'metadata': result.metadata
        }
        
        # Render and write
        html_content = template.render(**template_data)
        
        with open(self.output_dir / f"{formula_name}_ranking.html", 'w', encoding='utf-8') as f:
            f.write(html_content)
    
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
                    'rank': score.rank
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
        matrix = result.coverage_matrix
        
        # Calculate coverage statistics
        total_elements = len(matrix.code_elements)
        covered_elements = set()
        
        for test_idx in range(len(matrix.test_names)):
            for elem_idx in range(total_elements):
                if matrix.matrix[test_idx, elem_idx] == 1:
                    covered_elements.add(elem_idx)
        
        coverage_percentage = (len(covered_elements) / total_elements * 100) if total_elements > 0 else 0
        
        return {
            'total_elements': total_elements,
            'covered_elements': len(covered_elements),
            'coverage_percentage': coverage_percentage
        }
    
    def _write_static_files(self) -> None:
        """Write CSS and JavaScript files."""
        # Write CSS
        css_content = self._get_css_content()
        with open(self.output_dir / "style.css", 'w', encoding='utf-8') as f:
            f.write(css_content)
        
        # Write JavaScript
        js_content = self._get_js_content()
        with open(self.output_dir / "script.js", 'w', encoding='utf-8') as f:
            f.write(js_content)
    
    def _get_main_template(self) -> str:
        """Get the main HTML template."""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{{ title }}</h1>
            <p class="subtitle">Spectrum-Based Fault Localization Results</p>
        </header>
        
        <section class="summary">
            <h2>Summary</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <h3>{{ test_stats.total }}</h3>
                    <p>Total Tests</p>
                </div>
                <div class="stat-card">
                    <h3>{{ test_stats.failed }}</h3>
                    <p>Failed Tests</p>
                </div>
                <div class="stat-card">
                    <h3>{{ metadata.total_elements }}</h3>
                    <p>Code Elements</p>
                </div>
                <div class="stat-card">
                    <h3>{{ "%.2f"|format(execution_time) }}s</h3>
                    <p>Execution Time</p>
                </div>
            </div>
        </section>
        
        <section class="formulas">
            <h2>SBFL Formulas</h2>
            <div class="formula-grid">
                {% for formula in formulas %}
                <div class="formula-card">
                    <h3>{{ formula.title() }}</h3>
                    <p>Top Element: {{ top_elements[formula][0].element if top_elements[formula] }}</p>
                    <p>Score: {{ "%.4f"|format(top_elements[formula][0].score) if top_elements[formula] }}</p>
                    <a href="{{ formula }}_ranking.html" class="btn">View Ranking</a>
                </div>
                {% endfor %}
            </div>
        </section>
        
        <section class="top-suspects">
            <h2>Top Suspicious Elements</h2>
            {% for formula, elements in top_elements.items() %}
            <div class="formula-results">
                <h3>{{ formula.title() }}</h3>
                <table class="ranking-table">
                    <thead>
                        <tr>
                            <th>Rank</th>
                            <th>File</th>
                            <th>Line</th>
                            <th>Score</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for element in elements[:5] %}
                        <tr>
                            <td>{{ element.rank }}</td>
                            <td>{{ element.file }}</td>
                            <td>{{ element.line }}</td>
                            <td>{{ "%.4f"|format(element.score) }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
            {% endfor %}
        </section>
    </div>
    <script src="script.js"></script>
</body>
</html>
        '''
    
    def _get_formula_template(self) -> str:
        """Get the formula-specific HTML template."""
        return '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ title }}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>{{ formula_name.title() }} Rankings</h1>
            <nav>
                <a href="index.html">← Back to Summary</a>
            </nav>
        </header>
        
        <section class="ranking">
            <h2>Suspiciousness Ranking (Top {{ scores|length }} of {{ total_elements }})</h2>
            <table class="ranking-table">
                <thead>
                    <tr>
                        <th>Rank</th>
                        <th>File</th>
                        <th>Line</th>
                        <th>Element</th>
                        <th>Suspiciousness Score</th>
                    </tr>
                </thead>
                <tbody>
                    {% for score in scores %}
                    <tr class="{% if score.score > 0.7 %}high-suspicion{% elif score.score > 0.3 %}medium-suspicion{% else %}low-suspicion{% endif %}">
                        <td>{{ score.rank }}</td>
                        <td>{{ score.element.file_path }}</td>
                        <td>{{ score.element.line_number }}</td>
                        <td>{{ score.element.element_name or '' }}</td>
                        <td>{{ "%.6f"|format(score.score) }}</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </section>
    </div>
    <script src="script.js"></script>
</body>
</html>
        '''
    
    def _get_css_content(self) -> str:
        """Get CSS stylesheet content."""
        return '''
/* PyFault HTML Report Styles */
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
    max-width: 1200px;
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
}

nav a {
    color: #007bff;
    text-decoration: none;
    font-weight: 500;
}

nav a:hover {
    text-decoration: underline;
}

.stats-grid, .formula-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 20px;
    margin-bottom: 40px;
}

.stat-card, .formula-card {
    background: white;
    padding: 20px;
    border-radius: 8px;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    text-align: center;
}

.stat-card h3 {
    font-size: 2em;
    color: #007bff;
    margin-bottom: 5px;
}

.formula-card h3 {
    color: #2c3e50;
    margin-bottom: 10px;
}

.btn {
    display: inline-block;
    padding: 8px 16px;
    background: #007bff;
    color: white;
    text-decoration: none;
    border-radius: 4px;
    margin-top: 10px;
}

.btn:hover {
    background: #0056b3;
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
}

.ranking-table tr:hover {
    background: #f8f9fa;
}

.high-suspicion {
    background-color: #ffe6e6;
}

.medium-suspicion {
    background-color: #fff3cd;
}

.low-suspicion {
    background-color: #e6ffe6;
}

.formula-results {
    margin-bottom: 30px;
}

.formula-results h3 {
    color: #495057;
    margin-bottom: 15px;
}

@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    .stats-grid, .formula-grid {
        grid-template-columns: 1fr;
    }
    
    .ranking-table {
        font-size: 0.9em;
    }
    
    .ranking-table th,
    .ranking-table td {
        padding: 8px;
    }
}
        '''
    
    def _get_js_content(self) -> str:
        """Get JavaScript content."""
        return '''
// PyFault HTML Report JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Add interactive features
    console.log('PyFault report loaded');
    
    // Add sorting functionality to tables
    const tables = document.querySelectorAll('.ranking-table');
    tables.forEach(table => {
        const headers = table.querySelectorAll('th');
        headers.forEach((header, index) => {
            header.style.cursor = 'pointer';
            header.addEventListener('click', () => sortTable(table, index));
        });
    });
});

function sortTable(table, column) {
    const tbody = table.querySelector('tbody');
    const rows = Array.from(tbody.querySelectorAll('tr'));
    
    rows.sort((a, b) => {
        const aVal = a.cells[column].textContent.trim();
        const bVal = b.cells[column].textContent.trim();
        
        // Try to parse as numbers
        const aNum = parseFloat(aVal);
        const bNum = parseFloat(bVal);
        
        if (!isNaN(aNum) && !isNaN(bNum)) {
            return bNum - aNum; // Descending for numbers
        }
        
        return aVal.localeCompare(bVal);
    });
    
    rows.forEach(row => tbody.appendChild(row));
}
        '''

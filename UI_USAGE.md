# PyFault UI - Usage Examples

## 🚀 Quick Start

### 1. Launch UI without data (upload files manually)
```bash
pyfault ui
```

### 2. Launch UI with existing JSON results
```bash
pyfault ui --data-file results/summary.json
```

### 3. Launch UI with CSV coverage data (real-time analysis)
```bash
pyfault ui --data-file coverage_matrix.csv --port 8502
```

### 4. Launch UI and auto-open browser
```bash
pyfault ui --auto-open
```

## 📊 Complete Workflow Examples

### Example 1: Run analysis and view results
```bash
# 1. Run fault localization (automatically generates JSON + CSV + HTML)
pyfault run -s src -t tests -o results

# 2. Open UI with JSON results (recommended)
pyfault ui --data-file results/summary.json --auto-open
```

### Example 2: Collect coverage and analyze interactively  
```bash
# 1. Collect coverage data only
pyfault test -s src -t tests -o coverage_data

# 2. Open UI with coverage data (performs analysis on-the-fly)
pyfault ui --data-file coverage_data/coverage_matrix.csv
```

### Example 3: Compare multiple formulas
```bash
# 1. Run with multiple formulas
pyfault run -s src -t tests -f ochiai -f tarantula -f jaccard -f dstar

# 2. Open UI to compare results
pyfault ui --data-file pyfault_output/summary.json
```

## 🎯 UI Features

### 📈 Interactive Visualizations
- **Score distributions**: Histogram of suspiciousness scores
- **Top suspicious elements**: Horizontal bar charts with color coding
- **File-level treemaps**: Visual overview of suspicious files

### 🔍 Real Source Code Viewer
- **Actual source code display**: Shows real file contents (not mock data)
- **Intelligent file resolution**: Tries multiple paths to locate source files
- **Syntax highlighting**: Python code with line numbers
- **Suspicious line highlighting**: Visual indicators for high-risk lines
- **Score annotations**: Detailed scores displayed alongside code

### 📁 File Analysis
- **File-level grouping**: Elements grouped by source file
- **File statistics**: Count, max/avg scores per file
- **Interactive filtering**: By file extension and score thresholds

### 🎛️ Dynamic Filtering
- **Score thresholds**: Filter elements by minimum suspiciousness
- **File type filtering**: Focus on specific file extensions
- **Top-N selection**: Limit display to most suspicious elements

### 📊 Multiple Formula Support
- **Side-by-side comparison**: Switch between different SBFL formulas
- **Unified data format**: JSON format supports all implemented formulas
- **Real-time analysis**: CSV data analyzed on-demand with all formulas

## 🛠️ Data Format Support

### JSON Results (Recommended)
- **Complete analysis results**: All formulas, metadata, and statistics
- **Fastest loading**: Pre-computed results for immediate display
- **Generated automatically**: Every `pyfault run` creates `summary.json`

### CSV Coverage Data (Dynamic Analysis)
- **Real-time analysis**: Fault localization performed in the dashboard
- **All formulas applied**: Ochiai, Tarantula, Jaccard, DStar, Kulczynski2
- **Flexible input**: Works with any valid coverage matrix CSV

## 🚨 Troubleshooting

### Source Code Not Displaying
The dashboard tries multiple strategies to locate source files:

1. **Absolute paths**: Uses paths exactly as stored in data
2. **Relative to current directory**: Resolves relative to where UI is launched
3. **Common source directories**: Tries `src/`, `lib/`, `app/` subdirectories
4. **Filename matching**: Searches for files by name in current directory

**Solutions:**
```bash
# Launch from project root directory
cd /path/to/your/project
pyfault ui --data-file results/summary.json

# Ensure source files are accessible from launch directory
ls src/  # Check that source files exist and are accessible
```

### CSV Analysis Errors
```bash
# Verify CSV format
head coverage_matrix.csv

# Check for required columns: Element, File, Line, ElementType, ElementName, test columns
# Ensure OUTCOME row exists with test results (PASSED/FAILED)
```

### Performance with Large Datasets
- **Use JSON format**: Pre-computed results load faster than CSV analysis
- **Enable filtering**: Use score thresholds and file extension filters
- **Limit top-N**: Reduce the number of displayed elements

### Port Already in Use
```bash
pyfault ui --port 8502  # Try different port
pyfault ui --port 9000  # Or another available port
```

## 💡 Best Practices

1. **Use JSON for regular analysis**: Faster loading and consistent results
2. **Use CSV for exploration**: When you want to experiment with different parameters
3. **Launch from project root**: Ensures source code files can be located
4. **Filter for focus**: Use thresholds to focus on most suspicious elements
5. **Compare formulas**: Different formulas may highlight different potential bugs

## 🔧 Advanced Features

### Real-time CSV Analysis
When loading CSV files, the dashboard:
1. Parses the coverage matrix format
2. Applies all available SBFL formulas
3. Generates rankings and statistics
4. Presents results in the same format as JSON data

### Intelligent Source Resolution
The source code viewer:
1. Attempts to resolve file paths from multiple locations
2. Provides debugging information when files can't be found
3. Shows helpful error messages with suggested solutions
4. Falls back to score-only display when source isn't available

### Multi-formula Comparison
- Switch between formulas using the sidebar selector
- Compare how different formulas rank the same code elements
- Understand which formulas work best for your specific codebase

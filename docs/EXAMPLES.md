# PyFault Examples

This directory contains practical examples demonstrating PyFault's capabilities for fault localization in Python projects.

## 📁 Example Projects

### Example 1: Basic Calculator (`ex1/`)

A simple calculator implementation with intentional bugs, perfect for learning PyFault basics.

**Features:**
- Basic arithmetic operations (add, subtract, multiply, divide)
- Input validation and error handling
- Comprehensive test suite with both passing and failing tests
- Pre-configured PyFault settings

**Bugs Included:**
- Division by zero handling issue
- Floating-point precision error
- Edge case in modulo operation

**Usage:**
```bash
cd examples/ex1
pyfault run
pyfault ui
```

### Example 2: E-commerce Cart (Coming Soon)

A more complex example with shopping cart functionality.

### Example 3: Data Processing Pipeline (Coming Soon)

Example demonstrating fault localization in data processing workflows.

## 🚀 Quick Start Guide

### Running Example 1

1. **Navigate to the example**:
   ```bash
   cd examples/ex1
   ```

2. **Inspect the project structure**:
   ```
   ex1/
   ├── pyfault.conf          # PyFault configuration
   ├── src/                  # Source code with bugs
   │   ├── __init__.py
   │   ├── calculator.py     # Main calculator logic
   │   └── utils.py         # Utility functions
   └── tests/               # Test suite
       ├── test_calculator.py
       └── test_utils.py
   ```

3. **Run the complete fault localization pipeline**:
   ```bash
   pyfault run --source-dir src
   ```

4. **Launch the interactive dashboard**:
   ```bash
   pyfault ui
   ```

5. **Explore the results**:
   - Check the Overview tab for summary metrics
   - Use the Source Code tab to see highlighted suspicious lines
   - Compare different SBFL formulas in the Formula Comparison tab

## 📊 Expected Results

### Example 1 Analysis

When you run PyFault on Example 1, you should see:

**Test Results:**
- ~15 total tests
- ~12 passing tests
- ~3 failing tests
- ~80% code coverage

**Top Suspicious Lines** (using Ochiai formula):
1. `calculator.py:42` - Division handling logic (Score: ~0.85)
2. `calculator.py:67` - Modulo operation edge case (Score: ~0.72)
3. `utils.py:15` - Precision validation (Score: ~0.58)

**Formula Comparison:**
- **Ochiai** and **Tarantula** show high correlation (>0.8)
- **D*2** provides good discrimination for this project size
- **Jaccard** tends to be more conservative in scoring

## 🔧 Customizing Examples

### Modifying Configuration

Edit `pyfault.conf` to experiment with different settings:

```ini
[test]
source_dir = src
output_file = coverage.json
ignore = */__init__.py
omit = */__init__.py

[fl]
input_file = coverage.json
output_file = report.json
# Try different formula combinations
formulas = ochiai, tarantula, jaccard, dstar2, dstar3
```

### Adding New Tests

Create additional tests to see how they affect fault localization:

```python
# tests/test_calculator_extended.py
import pytest
from src.calculator import Calculator

class TestCalculatorExtended:
    def test_edge_case_scenario(self):
        calc = Calculator()
        # Add test that exercises the buggy code
        result = calc.divide(1.0, 3.0)
        assert abs(result - 0.333333) < 1e-6  # This might fail due to precision bug
```

### Introducing New Bugs

Modify the source code to introduce new bugs and observe how PyFault ranks them:

```python
# src/calculator.py
def multiply(self, a, b):
    # Introduce a subtle bug
    if a == 0 or b == 0:
        return 1  # Bug: should return 0
    return a * b
```

## 📈 Learning Objectives

### Understanding SBFL Formulas

Use the examples to understand how different formulas behave:

1. **Run with single formula**:
   ```bash
   pyfault run --formulas ochiai
   ```

2. **Compare results with multiple formulas**:
   ```bash
   pyfault run --formulas ochiai,tarantula,jaccard
   ```

3. **Analyze the differences** in the Formula Comparison tab

### Test Quality Impact

Experiment with test quality to see its effect on fault localization:

1. **Remove some tests** and observe how rankings change
2. **Add more comprehensive tests** covering edge cases
3. **Modify test assertions** to make more tests fail

### Coverage Impact

Understand how code coverage affects fault localization effectiveness:

1. **Check current coverage**:
   ```bash
   coverage run -m pytest
   coverage report
   ```

2. **Add tests to increase coverage** and re-run PyFault
3. **Compare fault localization accuracy** with different coverage levels

## 🎯 Best Practices Demonstrated

### Project Structure

The examples demonstrate recommended project organization:

```
project/
├── pyfault.conf          # Configuration at project root
├── src/                  # Source code in dedicated directory
│   └── package/          # Proper package structure
└── tests/                # Tests mirror source structure
    └── test_module.py    # Clear test naming
```

### Configuration Patterns

Examples show common configuration patterns:

```ini
[test]
source_dir = src          # Focus analysis on source code
omit = */__init__.py     # Exclude boilerplate files

[fl]
formulas = ochiai, tarantula, jaccard, dstar2  # Balanced formula selection
```

### Test Design for FL

Examples demonstrate test patterns that work well with fault localization:

```python
# Good: Focused tests that exercise specific functionality
def test_divide_positive_numbers(self):
    calc = Calculator()
    assert calc.divide(10, 2) == 5

# Good: Edge case tests that might reveal bugs
def test_divide_by_very_small_number(self):
    calc = Calculator()
    result = calc.divide(1, 1e-10)
    assert result == 1e10

# Good: Error condition tests
def test_divide_by_zero_raises_exception(self):
    calc = Calculator()
    with pytest.raises(ZeroDivisionError):
        calc.divide(5, 0)
```

## 🔍 Troubleshooting Examples

### Common Issues and Solutions

#### No Failing Tests
If you don't see any failing tests in the examples:

```bash
# Verify test discovery
pytest --collect-only

# Run tests manually to see results
pytest -v
```

#### Low Suspiciousness Scores
If all suspiciousness scores are very low:

1. Check that failing tests actually cover the buggy code
2. Verify that the bugs are in code paths executed by tests
3. Consider adding more targeted tests for the buggy areas

#### Dashboard Not Loading
If the dashboard fails to start:

```bash
# Ensure UI dependencies are installed
pip install pyfault[ui]

# Check that report file exists
ls -la report.json

# Try manual dashboard launch
streamlit run --server.port 8501 dashboard.py
```

## 🚀 Advanced Usage

### Custom Analysis Scripts

Create custom scripts to analyze the examples:

```python
# analyze_example.py
import json
from collections import defaultdict

def analyze_fault_localization(report_file):
    with open(report_file) as f:
        data = json.load(f)
    
    # Extract top suspicious lines across all formulas
    all_scores = defaultdict(list)
    
    for file_path, file_data in data["files"].items():
        for formula, scores in file_data["suspiciousness"].items():
            for line, score in scores.items():
                all_scores[f"{file_path}:{line}"].append((formula, score))
    
    # Find lines with high consensus across formulas
    consensus_lines = []
    for line, formula_scores in all_scores.items():
        if len(formula_scores) >= 3:  # At least 3 formulas
            avg_score = sum(score for _, score in formula_scores) / len(formula_scores)
            if avg_score > 0.5:  # High average suspiciousness
                consensus_lines.append((line, avg_score, formula_scores))
    
    # Sort by average score
    consensus_lines.sort(key=lambda x: x[1], reverse=True)
    
    print("Lines with high consensus suspiciousness:")
    for line, avg_score, formula_scores in consensus_lines[:10]:
        print(f"{line}: {avg_score:.3f}")
        for formula, score in formula_scores:
            print(f"  {formula}: {score:.3f}")

if __name__ == "__main__":
    analyze_fault_localization("report.json")
```

### Batch Analysis

Analyze multiple configurations:

```bash
# Run with different formula combinations
for formulas in "ochiai" "tarantula" "ochiai,tarantula" "ochiai,tarantula,jaccard"
do
    echo "Testing with formulas: $formulas"
    pyfault run --formulas "$formulas" --output "report_${formulas//,/_}.json"
done

# Compare results
python compare_results.py report_*.json
```

### Performance Benchmarking

Measure PyFault performance on the examples:

```python
# benchmark.py
import time
import subprocess
import json

def benchmark_pyfault(source_dir="src", iterations=5):
    times = []
    
    for i in range(iterations):
        start_time = time.time()
        
        # Run PyFault
        result = subprocess.run([
            "pyfault", "run", 
            "--source-dir", source_dir,
            "--output", f"report_bench_{i}.json"
        ], capture_output=True, text=True)
        
        end_time = time.time()
        
        if result.returncode == 0:
            times.append(end_time - start_time)
        else:
            print(f"Error in iteration {i}: {result.stderr}")
    
    if times:
        avg_time = sum(times) / len(times)
        print(f"Average execution time: {avg_time:.2f} seconds")
        print(f"Min: {min(times):.2f}s, Max: {max(times):.2f}s")

if __name__ == "__main__":
    benchmark_pyfault()
```

## 📚 Further Learning

### Next Steps

After working through the examples:

1. **Apply PyFault to your own projects**
2. **Experiment with different SBFL formulas**
3. **Contribute new examples or improvements**
4. **Read the research papers** behind the implemented formulas
5. **Explore the source code** to understand implementation details

### Additional Resources

- **Research Papers**: Look up the original papers for Ochiai, Tarantula, and D* formulas
- **GZoltar Documentation**: Study the Java-based fault localization tool that inspired PyFault
- **Coverage.py Documentation**: Understand the underlying coverage collection mechanism
- **Pytest Documentation**: Learn advanced testing techniques that work well with fault localization

### Contributing Examples

We welcome new examples! See `CONTRIBUTING.md` for guidelines on:
- Creating new example projects
- Adding different types of bugs
- Demonstrating advanced PyFault features
- Writing clear documentation for examples

---

These examples provide a hands-on way to learn fault localization concepts and PyFault's capabilities. Start with Example 1 and gradually work through more complex scenarios as you become comfortable with the tool.

# Dummy Example - Simple Synthetic Bug

This example provides a simple, synthetic demonstration of floss's fault localization capabilities using artificially created bugs in geometric calculation functions.

## Example Description

**Type**: Synthetic/Educational Example
**Category**: Mathematical Computation
**Language**: Python
**Complexity**: Beginner-friendly

### Purpose
This example serves as:
- **Introduction to floss**: Simple scenario for learning floss basics
- **Educational tool**: Clear demonstration of fault localization concepts
- **Testing baseline**: Controlled environment for validating floss functionality
- **Development aid**: Quick example for floss development and debugging

## Project Structure

```
dummy-example/
├── src/
│   ├── __init__.py
│   ├── equilateral.py      # Equilateral triangle area calculation (contains bug)
│   └── isosceles.py        # Isosceles triangle area calculation
├── tests/
│   ├── __init__.py
│   ├── test_equilateral.py # Tests for equilateral triangle (one failing test)
│   └── test_isosceles.py   # Tests for isosceles triangle (all passing)
├── floss.conf           # floss configuration
├── .coverage              # Coverage data (if previously run)
└── .coveragerc           # Coverage configuration
```

## The Bug

### Bug Location
File: `src/equilateral.py`, Line 10

### Bug Description
The calculation of equilateral triangle area contains a mathematical error:

```python
# BUGGY CODE (Line 10)
area = const + term  # Incorrect: addition instead of multiplication

# CORRECT CODE
area = const * term  # Should be multiplication
```

### Mathematical Context
- **Correct formula**: Area = (√3/4) × a²
- **Buggy implementation**: Area = (√3/4) + a²
- **Impact**: Incorrect area calculations for all triangles except edge case where a=1

## Setup Instructions

### Prerequisites
- Python 3.9+ (any recent Python version)
- floss installed

### Quick Setup
```bash
# Navigate to the dummy example directory
cd examples/dummy-example

# Install floss if not already installed
pip install -e ../../

# Ready to run! No additional setup needed
```

## Running floss

### Complete Pipeline
```bash
# Run the complete fault localization pipeline
floss run --source-dir src --test-dir tests
```

### Step-by-Step
```bash
# Step 1: Run tests with coverage collection
floss test --source-dir src --test-dir tests --output coverage.json

# Step 2: Calculate fault localization scores
floss fl --input coverage.json --output report.json --formulas ochiai tarantula dstar2

# Step 3: Launch interactive dashboard
floss ui --report report.json
```

### Using Configuration File
```bash
# The included floss.conf file has pre-configured settings
floss run --config floss.conf
```

## Expected Results

### Test Execution
- **Total tests**: 3 tests across 2 files
- **Passing tests**: 2 tests (test_ea_pass, test_isosceles tests)
- **Failing tests**: 1 test (test_ea_fail)

### Fault Localization Results
floss should identify:
1. **Highest suspiciousness**: Line 10 in `equilateral.py` (the actual bug)
2. **Medium suspiciousness**: Lines around the bug (function definition, variable assignments)
3. **Low suspiciousness**: Lines in `isosceles.py` (not involved in failing tests)

### Dashboard Views
- **Treemap**: Should highlight `equilateral.py` as most suspicious
- **Source code**: Line 10 should have the highest suspiciousness score
- **Coverage matrix**: Shows which tests execute which lines

## Learning Objectives

This example demonstrates:

### Basic SBFL Concepts
- How passing vs failing tests affect suspiciousness scores
- Relationship between code coverage and fault localization
- Different SBFL formula behaviors on simple bugs

### floss Features
- Complete fault localization workflow
- Configuration file usage
- Interactive dashboard capabilities
- Command-line interface options

### Analysis Techniques
- Interpreting suspiciousness scores
- Using coverage information for debugging
- Comparing different SBFL formulas

## Analysis Guide

### What to Look For
1. **High suspiciousness scores** on line 10 of `equilateral.py`
2. **Low scores** for `isosceles.py` (not involved in failing tests)
3. **Medium scores** for other lines in `equilateral_area()` function

### Formula Comparison
Try different SBFL formulas to see how they rank the bug:
- **Ochiai**: Usually performs well on this type of bug
- **Tarantula**: Classic formula, good baseline
- **DStar2**: Often effective for single-bug scenarios

### Interactive Exploration
Use the dashboard to:
- Adjust suspiciousness thresholds
- Compare formula results side by side
- Examine test coverage patterns
- View source code with suspiciousness overlays

## Educational Exercises

### Beginner Exercises
1. **Run floss** and identify the bug location
2. **Compare formulas** - which gives the clearest results?
3. **Fix the bug** and re-run to see results change
4. **Add more tests** and observe the impact on suspiciousness

### Advanced Exercises
1. **Introduce additional bugs** in `isosceles.py`
2. **Create more complex test scenarios** with edge cases
3. **Experiment with different coverage patterns**
4. **Implement custom SBFL formulas** and test them

## Common Issues

### No Failing Tests
If you accidentally fix the bug:
```python
# Make sure line 10 in equilateral.py has the bug:
area = const + term  # This should be addition (incorrect)
```

### All Tests Pass
Check that `test_ea_fail()` is actually testing the problematic case:
```python
# This test should fail with the buggy implementation
def test_ea_fail():
    a = 3  # Using a=3 triggers the bug
    area = equilateral_area(a)
    assert area == pytest.approx(9 * math.sqrt(3) / 4)  # Expects correct result
```

## Next Steps

After completing this example:
1. **Explore real-world examples** like the FastAPI bugs
2. **Try modifying the bug** to see how it affects results
3. **Add complexity** with multiple bugs or more intricate test patterns
4. **Use this as a baseline** for understanding more complex fault localization scenarios

## Contributing

This example can be enhanced by:
- Adding more synthetic bugs with different characteristics
- Creating additional test scenarios
- Implementing more complex mathematical functions
- Adding examples of different bug types (logical, boundary, etc.)

## Troubleshooting

### Import Errors
Ensure you're running from the correct directory:
```bash
cd examples/dummy-example
python -m pytest tests/  # Should work
```

### No Coverage Data
If coverage collection fails:
```bash
# Run tests manually with coverage
coverage run -m pytest tests/
coverage json -o coverage.json
```

### Dashboard Issues
If the dashboard doesn't show expected results:
- Verify `report.json` was generated
- Check that the report contains the expected failing test
- Ensure floss UI dependencies are installed

# Adding New Examples to floss

This guide explains how to contribute new examples to the floss project, helping expand the collection of real-world fault localization demonstrations.

## Example Categories

### 1. Educational Examples
Simple, synthetic bugs designed for learning floss concepts.

**Characteristics:**
- Clear, isolated bugs
- Minimal setup requirements
- Well-documented expected results
- Suitable for beginners

**Example**: `dummy-example`

### 2. Real-World Framework Examples
Actual bugs from popular Python frameworks and libraries.

**Characteristics:**
- Historical bugs from real projects
- Complex codebases demonstrating realistic scenarios
- Specific version requirements
- Automated setup scripts

**Examples**: FastAPI bugs, PyGraphistry

### 3. Domain-Specific Examples
Examples showcasing floss in specific application domains.

**Potential domains:**
- Scientific computing (NumPy, SciPy)
- Machine learning (scikit-learn, TensorFlow)
- Web development (Django, Flask)
- Data processing (Pandas, Dask)
- DevOps tools (Ansible, Docker utilities)

## Creating a New Example

### Step 1: Choose Your Bug Source

#### Option A: Synthetic Bug
Create a controlled bug for educational purposes:
```python
def calculate_area(length, width):
    # Bug: using addition instead of multiplication
    return length + width  # Should be: length * width
```

#### Option B: Historical Bug
Find a real bug from:
- [BugsInPy](https://github.com/soarsmu/BugsInPy) dataset
- GitHub issue trackers of popular projects
- CVE databases for security-related bugs
- Academic bug benchmarks

#### Option C: Reproduced Bug
Reproduce a bug you've encountered in real development.

### Step 2: Set Up Directory Structure

Create the example directory:
```bash
mkdir examples/your-example-name
cd examples/your-example-name
```

Required files:
```
your-example-name/
├── README.md           # Detailed documentation
├── floss.conf       # floss configuration
├── setup.sh           # Automated setup script (if needed)
└── report.json        # Pre-generated results (optional)
```

### Step 3: Write the README.md

Use this template:

```markdown
# Your Example Name - Brief Description

## Bug Description
**Bug ID**: Identifier if applicable
**Category**: Bug type (validation, logic, performance, etc.)
**Severity**: High/Medium/Low
**Language**: Python version requirements

### Problem Summary
Clear description of what the bug does wrong.

### Expected vs Actual Behavior
- **Expected**: What should happen
- **Actual**: What actually happens
- **Impact**: Why this matters

## Files Included
List and explain each file in the example.

## Setup Instructions
### Prerequisites
### Quick Setup
### Manual Setup (if automated setup fails)

## Running floss
Step-by-step instructions for running fault localization.

## Viewing Results
How to interpret the results and what to look for.

## Expected Results
What fault localization should find.

## Learning Objectives
What this example teaches about fault localization.

## Troubleshooting
Common issues and solutions.
```

### Step 4: Create floss.conf

Optimize settings for your specific example:

```ini
[test]
source_dir = path/to/source
test_dir = path/to/tests
output_file = coverage.json
ignore = */__init__.py, */migrations/*
omit = */__init__.py, */tests/*

[fl]
input_file = coverage.json
output_file = report.json
formulas = ochiai, tarantula, jaccard, dstar2

[ui]
port = 8501
auto_open = true
```

### Step 5: Write setup.sh (if needed)

For examples requiring external projects:

```bash
#!/usr/bin/env bash
set -Eeuo pipefail

# Setup script for Your Example
VENV_NAME="your-example-venv"
REQUIRED_PY="3.x.x"  # Specify if needed

# Python version checking
PY=""
if command -v python3 >/dev/null 2>&1; then
  PY="python3"
elif command -v python >/dev/null 2>&1; then
  PY="python"
else
  echo "Python not found. Please install Python and try again." >&2
  exit 1
fi

# Create virtual environment
$PY -m venv "$VENV_NAME"
source "$VENV_NAME/bin/activate"

# Install floss
$PY -m pip install -q -e ../../

# Download/setup the project with the bug
# This varies based on your bug source

echo "Setup completed."
```

Make it executable:
```bash
chmod +x setup.sh
```

### Step 6: Test Your Example

Verify your example works:

```bash
# Test setup script
./setup.sh

# Test floss execution
cd project-directory  # If applicable
floss run

# Test dashboard
floss ui --report report.json
```

### Step 7: Add CI/CD Support

Add your example to `.github/workflows/examples.yml`:

```yaml
test-your-example:
  name: Test Your Example
  runs-on: ubuntu-latest

  steps:
  - name: Checkout repository
    uses: actions/checkout@v4

  - name: Set up Python X.X
    uses: actions/setup-python@v5
    with:
      python-version: "X.X"

  - name: Install floss
    run: |
      python -m pip install --upgrade pip
      pip install -e .

  - name: Setup Your Example
    run: |
      cd examples/your-example-name
      timeout 600 bash setup.sh

  - name: Test floss on Your Example
    run: |
      cd examples/your-example-name/project-dir
      timeout 300 floss run
      # Validate outputs
```

## Quality Guidelines

### Documentation Quality
- ✅ Clear bug description with context
- ✅ Step-by-step setup instructions
- ✅ Expected results and learning objectives
- ✅ Troubleshooting section
- ✅ Proper markdown formatting

### Technical Quality
- ✅ Reproducible setup process
- ✅ Reasonable execution time (< 10 minutes)
- ✅ Clear failing tests (not all tests should pass)
- ✅ Meaningful suspiciousness results
- ✅ Proper floss configuration

### Educational Value
- ✅ Demonstrates specific fault localization concepts
- ✅ Shows realistic debugging scenarios
- ✅ Provides learning progression (beginner → advanced)
- ✅ Includes analysis tips and interpretation guidance

## Example Validation Checklist

Before submitting your example:

### Setup Validation
- [ ] Setup script runs successfully on clean environment
- [ ] All dependencies are properly specified
- [ ] Python version requirements are documented
- [ ] Setup completes within reasonable time (< 10 minutes)

### floss Execution
- [ ] floss test execution succeeds
- [ ] At least one test fails (demonstrating the bug)
- [ ] Coverage data is collected properly
- [ ] Fault localization produces meaningful results
- [ ] Dashboard displays results correctly

### Documentation
- [ ] README.md follows the template structure
- [ ] All sections are complete and informative
- [ ] Code examples are correct and tested
- [ ] Troubleshooting covers common issues
- [ ] Learning objectives are clear

### CI Integration
- [ ] Example is added to GitHub Actions workflow
- [ ] CI tests pass for the example
- [ ] Timeout values are appropriate
- [ ] Error handling works correctly

## Submission Process

1. **Fork the repository**
2. **Create your example** following this guide
3. **Test thoroughly** on multiple environments if possible
4. **Update main documentation**:
   - Add to `examples/README.md`
   - Update main `README.md` examples section
5. **Submit pull request** with:
   - Clear description of the example
   - Explanation of the bug and its significance
   - Screenshots or output samples
   - Testing verification

## Maintenance

### Updating Existing Examples
- Keep dependencies up to date when possible
- Fix broken setup scripts promptly
- Update documentation for clarity
- Monitor CI failures and address issues

### Deprecating Examples
If an example becomes unmaintainable:
1. Mark as deprecated in README
2. Move to `examples/deprecated/` directory
3. Remove from CI workflows
4. Update main documentation

## Tips for Success

### Choosing Good Examples
- **Start simple**: Educational examples are easier to create
- **Focus on clarity**: Clear bugs are more valuable than complex ones
- **Consider diversity**: Different bug types and domains are valuable
- **Think about maintenance**: Avoid examples with fragile dependencies

### Making Examples Robust
- **Pin dependency versions** when possible
- **Handle network failures** gracefully in setup scripts
- **Provide alternative setup methods** for different environments
- **Test on multiple platforms** (Linux, macOS, Windows)

### Educational Impact
- **Include analysis walkthroughs** showing how to interpret results
- **Compare different SBFL formulas** and explain differences
- **Show common pitfalls** and how to avoid them
- **Connect to real-world debugging** practices

## Getting Help

If you need help creating an example:
- Open an issue describing your idea
- Ask questions in discussions
- Look at existing examples for inspiration
- Reach out to maintainers for guidance

Thank you for contributing to floss's educational mission!

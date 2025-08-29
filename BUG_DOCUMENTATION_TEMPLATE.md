# Bug Documentation Template

This template provides a standardized format for creating documentation for individual PyFault bug examples.

## Template Structure

```markdown
# {Project} Bug {Number} - {Bug Title}

This example demonstrates PyFault's fault localization capabilities on {Project} Bug #{Number}, which involves {brief description}.

## Bug Description

**Bug ID**: {Project} Bug #{Number} from {Dataset} dataset  
**Category**: {Category}  
**Severity**: {High/Medium/Low}  
**Language**: Python 3.8.3  

### Problem Summary
The bug occurs in {location/module} where {detailed description of the problem}. This {causes/leads to} {impact description}.

### Expected vs Actual Behavior
- **Expected**: {What should happen}
- **Actual**: {What actually happens}
- **Impact**: {Real-world consequences}

### Technical Details
{Technical explanation of the fix and why it's needed}

## Files Included

- `README.md`: This file with bug-specific documentation
- `bug_patch.txt`: The exact patch that fixes this bug
- `report.json`: Pre-generated fault localization results showing the most suspicious lines

## Setup Instructions

### Prerequisites
- Python 3.8.3 (exact version required)
- Git
- Unix-like environment (Linux/macOS/WSL)

### Quick Setup
```bash
# Navigate to the {project} examples directory
cd examples/{project}

# Run the automated setup for bug {number}
./setup.sh {number}

# The setup creates:
# - Virtual environment: {project}-bug{number}
# - Downloads and sets up {Project} with bug
# - Installs all dependencies
```

### Manual Setup (Alternative)
```bash
# From the {project} directory
cd examples/{project}

# Create and activate virtual environment
python3.8 -m venv {project}-bug{number}
source {project}-bug{number}/bin/activate

# Install PyFault and BugsInPy
pip install pyfault bugsinpy

# Clone BugsInPy framework (for FastAPI bugs)
git clone https://github.com/soarsmu/BugsInPy.git

# Setup BugsInPy environment
cd BugsInPy && source framework/bin/setup

# Checkout {Project} buggy version
bugsinpy-checkout -p {project} -v 0 -i {number} -w "./"

# Install dependencies and {Project}
cd {project} && pip install -r bugsinpy_requirements.txt && pip install -e .
```

## Running PyFault

After setup completion:

```bash
# Ensure you're in the virtual environment
source {project}-bug{number}/bin/activate

# Navigate to the {Project} project directory
cd {project}

# Run PyFault analysis
pyfault run

# View results in web dashboard
pyfault ui --report report.json
```

## Expected Results

The fault localization should identify suspicious lines in:
- `{main_file}` - {description of expected suspicious areas}

Top suspicious areas typically include:
1. {Area 1}
2. {Area 2}
3. {Area 3}

## Understanding the Fix

The `bug_patch.txt` file shows the exact changes needed:

1. **{Change 1}**: {Description}
2. **{Change 2}**: {Description}

The key change is:
```diff
{show key diff lines}
```

{Explanation of what the fix does}

## Learning Objectives

This example demonstrates:
- **{Concept 1}**: {Description}
- **{Concept 2}**: {Description}
- **{Concept 3}**: {Description}
- **{Concept 4}**: {Description}

## Troubleshooting

### Common Issues
1. **Python Version**: Ensure exactly Python 3.8.3 is used
2. **Virtual Environment**: Make sure the {project}-bug{number} environment is activated
3. **{Specific Issue}**: {Description and solution}

### Debug Steps
```bash
# Verify Python version
python --version  # Should show 3.8.3

# Check {Project} installation
python -c "import {project}; print({project}.__version__)"

# Test {specific module}
python -c "from {module} import {function}; print('{Module} loaded')"
```

### Common Symptoms of the Bug
- {Symptom 1}
- {Symptom 2}  
- {Symptom 3}
- {Symptom 4}

### Real-world Impact
This type of bug affects:
- {Impact area 1}
- {Impact area 2}
- {Impact area 3}
```

## Available Bug Categories

### FastAPI Bug Categories
1. **Response Model Handling** (bugs 1, 5) - Model serialization and field handling
2. **Input Validation** (bugs 3, 4, 9) - Request parameter and body validation  
3. **OpenAPI Schema** (bugs 2, 4) - API documentation generation
4. **Routing & Middleware** (bugs 6, 8, 13) - Request routing and middleware execution
5. **Error Handling** (bugs 7, 14) - Exception handling and error responses
6. **Advanced Features** (bugs 10, 12, 15, 16) - File uploads, WebSockets, static files, background tasks

### Cookiecutter Bug Categories
1. **File Handling** (bug 1) - Character encoding and file I/O
2. **Template Processing** (bug 2) - Hook discovery and template variable substitution

## Usage Instructions

1. **Copy this template** for a new bug documentation
2. **Replace all {placeholders}** with bug-specific information
3. **Examine the bug_patch.txt** file to understand the technical details
4. **Test the setup process** to ensure accuracy
5. **Review and refine** the documentation for clarity

## Quality Checklist

- [ ] All placeholders replaced with accurate information
- [ ] Technical details match the actual patch file
- [ ] Setup instructions tested and verified
- [ ] Learning objectives are educational and relevant
- [ ] Troubleshooting section covers common issues
- [ ] Examples and code snippets are correct

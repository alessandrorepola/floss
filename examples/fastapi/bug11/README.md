# FastAPI Bug 11 - Response Model Validation Issue

This example demonstrates PyFault's fault localization capabilities on FastAPI Bug #11, which involves incorrect response model validation and serialization behavior.

## Bug Description

**Bug ID**: FastAPI Bug #11 from BugsInPy dataset  
**Category**: Response Model Validation  
**Severity**: Medium  
**Language**: Python 3.8.3  

### Problem Summary
The bug occurs when FastAPI validates and serializes response data according to declared response models. The validation logic incorrectly handles certain response structures, leading to either validation errors for valid responses or acceptance of invalid response data.

### Expected vs Actual Behavior
- **Expected**: Response data is properly validated against declared response models and correctly serialized
- **Actual**: Response validation fails for valid data or accepts invalid response structures
- **Impact**: API responses become inconsistent, affecting client applications and API contracts

## Files Included

- `README.md`: This file with bug-specific documentation
- `report.json`: Pre-generated fault localization results showing the most suspicious lines

## Setup Instructions

### Prerequisites
- Python 3.8.3 (exact version required)
- Git
- Unix-like environment (Linux/macOS/WSL)

### Quick Setup
```bash
# Navigate to the fastapi examples directory
cd examples/fastapi

# Run the centralized setup script for bug 11
./setup.sh 11

# The script will:
# 1. Create a Python 3.8.3 virtual environment (fastapi-bug11)
# 2. Install PyFault
# 3. Clone BugsInPy framework
# 4. Download FastAPI v0.11 with the bug
# 5. Install dependencies
# 6. Copy configuration files
```

### Manual Setup
### Manual Setup (Alternative)

If the automated setup fails, you can set up manually:

```bash
# From the fastapi directory
cd examples/fastapi

# Create virtual environment with Python 3.8.3
python3.8 -m venv fastapi-bug11
source fastapi-bug11/bin/activate

# Install PyFault
pip install -e ../../

# Clone BugsInPy
git clone https://github.com/soarsmu/BugsInPy.git
export PATH="$PATH:$(pwd)/BugsInPy/framework/bin"

# Checkout FastAPI buggy version
bugsinpy-checkout -p fastapi -v 0 -i 11 -w "./"

# Install dependencies
cd fastapi && pip install -r bugsinpy_requirements.txt && pip install -e .
```

## Running PyFault

After setup completes:

```bash
# Activate environment (if not already active)
source fastapi-bug11/bin/activate

# Navigate to the FastAPI project directory
cd fastapi

# Run fault localization
pyfault run
```

## Expected Results

The fault localization should identify suspicious code in:

| Priority | Component | Expected Files |
|----------|-----------|----------------|
| **High** | Response validation logic | `fastapi/utils.py`, `fastapi/routing.py` |
| **Medium** | Response serialization | `fastapi/encoders.py`, `fastapi/responses.py` |
| **Low** | Model field validation | `pydantic` model files |

## Bug Analysis

**Nature of the Bug**: Incorrect response model validation and serialization behavior

**What to Look For**:
- Response data validation failures for valid responses
- Acceptance of invalid response structures
- Issues in type conversion and serialization

**Key Concepts**:
- **Response Models**: Pydantic models defining expected response structure
- **Serialization**: Converting Python objects to JSON
- **Field Validation**: Per-field validation rules and constraints

## Viewing Results

Launch the interactive dashboard:
```bash
pyfault ui --report report.json
```

The dashboard provides:
- **Treemap view**: Visual file suspiciousness
- **Source code view**: Line-by-line analysis
- **Coverage matrix**: Test execution patterns
- **Formula comparison**: Multiple SBFL formula results

# FastAPI Bug 6 - Dependency Injection Error

This example demonstrates PyFault's fault localization capabilities on FastAPI Bug #6, which involves incorrect behavior in the dependency injection system.

## Bug Description

**Bug ID**: FastAPI Bug #6 from BugsInPy dataset  
**Category**: Dependency Injection  
**Severity**: High  
**Language**: Python 3.8.3  

### Problem Summary
The bug occurs in FastAPI's dependency injection mechanism where dependencies are not properly resolved or injected in certain scenarios. This leads to runtime errors or incorrect behavior when endpoints rely on injected dependencies.

### Expected vs Actual Behavior
- **Expected**: Dependencies are properly resolved and injected into endpoint functions
- **Actual**: Dependency injection fails or injects incorrect/incomplete dependencies
- **Impact**: API endpoints fail at runtime, affecting application functionality and reliability

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

# Run the centralized setup script for bug 6
./setup.sh 6
```

### Manual Setup (Alternative)
If the automated setup fails:

```bash
# From the fastapi directory
cd examples/fastapi

# Create virtual environment with Python 3.8.3
python3.8 -m venv fastapi-bug6
source fastapi-bug6/bin/activate

# Install PyFault
pip install -e ../../

# Clone BugsInPy
git clone https://github.com/soarsmu/BugsInPy.git
export PATH="$PATH:$(pwd)/BugsInPy/framework/bin"

# Checkout FastAPI buggy version
bugsinpy-checkout -p fastapi -v 0 -i 6 -w "./"

# Install dependencies
cd fastapi && pip install -r bugsinpy_requirements.txt && pip install -e .
```

## Running PyFault

After setup completes:

```bash
# Activate environment (if not already active)
source fastapi-bug6/bin/activate

# Navigate to the FastAPI project directory
cd fastapi

# Run fault localization
pyfault run
```

## Expected Results

The fault localization should identify suspicious code in:

| Priority | Component | Expected Files |
|----------|-----------|----------------|
| **High** | Dependency resolution | `fastapi/dependencies/`, `fastapi/routing.py` |
| **Medium** | Dependency injection | `fastapi/utils.py`, DI container code |
| **Low** | Dependency caching | Memoization and lifecycle management |

## Bug Analysis

**Nature of the Bug**: Incorrect dependency injection behavior

**What to Look For**:
- Dependency resolution failures
- Incorrect dependency lifecycle management
- Issues with dependency scoping and caching

**Key Concepts**:
- **Dependency Injection**: Automatic provision of dependencies to functions
- **Dependency Graph**: Relationships and dependencies between components
- **Dependency Scoping**: Request-level vs application-level dependencies

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

## Analysis Tips

When analyzing the results:
1. **Focus on dependency resolution code** - examine how dependencies are discovered and instantiated
2. **Look for injection points** - understand where and how dependencies are injected
3. **Examine dependency graphs** - trace complex dependency relationships
4. **Check lifecycle management** - understand how dependencies are created, cached, and cleaned up

### Quick Setup
```bash
# Navigate to the fastapi examples directory
cd examples/fastapi

# Run the centralized setup script for bug 6
./setup.sh 6
```
cd examples/fastapi/bug6

# Run setup script (this will take a few minutes)
./setup.sh

# The script will:
# 1. Create a Python 3.8.3 virtual environment
# 2. Install PyFault
# 3. Clone BugsInPy framework
# 4. Download FastAPI v0.6 with the bug
# 5. Install dependencies
# 6. Copy configuration files
```

### Manual Setup
If the automated setup fails, you can set up manually:

```bash
# Create virtual environment with Python 3.8.3
python3.8 -m venv fastapi-bug6
source fastapi-bug6/bin/activate

# Install PyFault
pip install -e ../../../

# Clone BugsInPy
git clone https://github.com/soarsmu/BugsInPy.git
export PATH="$PATH:$(pwd)/BugsInPy/framework/bin"

# Checkout FastAPI buggy version
bugsinpy-checkout -p fastapi -v 0 -i 6 -w "./"

# Install dependencies
cd fastapi
pip install -r bugsinpy_requirements.txt
pip install -e .
```

## Running PyFault

After setup completes, run fault localization:

```bash
# Navigate to the FastAPI project directory
cd fastapi

# Run complete fault localization pipeline
pyfault run

# Or run step by step:
pyfault test --source-dir fastapi --test-dir tests
pyfault fl --input coverage.json --output report.json --formulas ochiai tarantula dstar2 jaccard op2
```

## Viewing Results

Launch the interactive dashboard:
```bash
pyfault ui --report report.json
```

The dashboard will show:
- **Treemap view**: Visual representation of file suspiciousness
- **Source code view**: Line-by-line suspiciousness scores with dependency injection focus
- **Coverage matrix**: Test execution patterns for dependency scenarios
- **Formula comparison**: Different SBFL formula results

## Expected Results

The fault localization should identify suspicious code in:
1. **Dependency resolution logic** (highest suspiciousness)
2. **Dependency injection mechanisms** (high suspiciousness)  
3. **Dependency caching/lifecycle management** (medium suspiciousness)
4. **Route parameter binding** (medium suspiciousness)

Key files to examine:
- `fastapi/dependencies/utils.py`: Core dependency injection logic
- `fastapi/dependencies/models.py`: Dependency model definitions
- `fastapi/routing.py`: Route-level dependency handling
- `fastapi/utils.py`: Utility functions for dependency resolution

## Analysis Tips

When analyzing the results:

1. **Focus on dependency resolution paths** - trace how dependencies are discovered and resolved
2. **Examine dependency lifecycles** - understand when dependencies are created/destroyed
3. **Check for circular dependencies** - common source of injection issues
4. **Look at dependency caching** - issues might arise from incorrect caching behavior
5. **Analyze sub-dependency handling** - bugs often occur in nested dependency scenarios

## Learning Objectives

This example demonstrates:
- How SBFL performs on dependency injection bugs
- Complexity of modern framework dependency systems
- Impact of dependency testing on fault localization accuracy
- Relationship between component coupling and bug localization

## Dependency Injection Concepts

Understanding key concepts helps with analysis:

- **Dependency Graph**: How dependencies relate to each other
- **Injection Scopes**: Singleton, request-scoped, transient dependencies
- **Dependency Providers**: Functions or classes that create dependencies
- **Sub-dependencies**: Dependencies that themselves have dependencies
- **Dependency Overrides**: Test-time dependency replacements

## Common Dependency Bug Patterns

This bug type typically involves:
- **Resolution order issues**: Dependencies resolved in wrong order
- **Scope violations**: Incorrect dependency lifecycle management
- **Circular dependency**: Dependencies that reference each other
- **Missing dependency**: Required dependency not properly registered
- **Type annotation issues**: Incorrect type hints affecting injection

## Troubleshooting

### Setup Issues
- **Python version**: Ensure exactly Python 3.8.3 is used
- **BugsInPy errors**: Check internet connection and git configuration
- **Permission errors**: Run `chmod +x setup.sh`

### Runtime Issues
- **Import errors**: Ensure virtual environment is activated
- **Dependency errors**: Some dependency injection failures are expected (this is the bug!)
- **Test isolation**: Dependency state might affect test execution order

## Deep Dive Analysis

For advanced analysis:

1. **Dependency graph visualization**: Map out the dependency relationships
2. **Injection timing analysis**: Understand when dependencies are resolved
3. **Mock dependency testing**: Replace dependencies to isolate the bug
4. **Performance impact**: Analyze how the bug affects application performance

## Real-World Impact

Dependency injection bugs can cause:
- **Runtime failures**: Endpoints crash when dependencies aren't available
- **Data corruption**: Incorrect dependencies might lead to wrong business logic
- **Security issues**: Authentication/authorization dependencies might fail
- **Performance problems**: Inefficient dependency resolution

## Next Steps

After exploring this example:
1. Compare with validation bugs (bug2, bug3) to understand different bug categories
2. Examine how dependency complexity affects fault localization effectiveness
3. Try creating custom dependency scenarios to test PyFault's capabilities
4. Analyze the relationship between test coverage of dependencies and localization accuracy

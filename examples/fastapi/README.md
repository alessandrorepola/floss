# FastAPI Bug Examples

This directory contains examples for testing PyFault with different FastAPI bugs from the BugsInPy dataset.

## Quick Start

Use the centralized setup script to prepare the environment for any bug:

```bash
./setup.sh <bug_number>
```

**Available bugs:** 2, 3, 6, 11

### Examples

```bash
# Setup environment for bug 11
./setup.sh 11

# Setup environment for bug 2  
./setup.sh 2

# Run PyFault analysis (after setup)
cd fastapi && pyfault run
```

## Structure

```
fastapi/
├── setup.sh           # Centralized, parametrized setup script
├── pyfault.conf       # Shared configuration for all bugs
├── README.md          # This documentation
├── bug2/              # Bug-specific directories
│   ├── README.md      # Bug description and details
│   └── report.json    # Expected PyFault output
├── bug3/
├── bug6/
└── bug11/
```

## How It Works

1. **Centralized Setup**: One script (`setup.sh`) handles all bugs, eliminating code duplication
2. **Shared Configuration**: All bugs use the same `pyfault.conf` file
3. **Isolated Environments**: Each bug gets its own virtual environment (`fastapi-bug<N>`)
4. **Bug-Specific Data**: Individual directories contain only bug-specific documentation and expected results

## Environment Details

- **Python Version**: 3.8.3 (required by BugsInPy)
- **Virtual Environments**: `fastapi-bug2`, `fastapi-bug3`, `fastapi-bug6`, `fastapi-bug11`
- **Dependencies**: FastAPI, PyTest, Pydantic (installed automatically)

## CI/CD Integration

The setup is integrated with the project's CI pipeline (`.github/workflows/examples.yml`). The workflow:

1. Sets up Python 3.8
2. Installs PyFault 
3. Runs the centralized setup for each bug
4. Executes PyFault analysis
5. Validates the output structure

## Bug Details

| Bug | Description | Category |
|-----|-------------|----------|
| [2](bug2/README.md) | OpenAPI Schema Generation Issue | Schema Generation |
| [3](bug3/README.md) | Request Validation Error | Input Validation |
| [6](bug6/README.md) | Dependency Injection Problem | Dependency Management |
| [11](bug11/README.md) | Response Model Validation Issue | Response Validation |

## Troubleshooting

### Common Issues

1. **Python Version**: Ensure you have Python 3.8.x installed
2. **Permissions**: Make sure `setup.sh` is executable (`chmod +x setup.sh`)
3. **Git Access**: The script clones BugsInPy, ensure Git is available
4. **Environment Conflicts**: Each bug uses separate virtual environments to avoid conflicts

### Cleanup

To remove all virtual environments:

```bash
rm -rf fastapi-bug2 fastapi-bug3 fastapi-bug6 fastapi-bug11 BugsInPy fastapi
```

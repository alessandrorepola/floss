# FastAPI Bug Examples

This directory contains examples for testing floss with different FastAPI bugs from the BugsInPy dataset.

## Quick Start

Use the centralized setup script to prepare the environment for any bug:

```bash
./setup.sh <bug_number>
```

**Available bugs:** 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, multi-bugs

### Examples

```bash
# Setup environment for bug 11
./setup.sh 11

# Setup environment for bug 2
./setup.sh 2

# Setup environment for bug 7
./setup.sh 7

# Setup environment for multiple bugs
./setup.sh multi-bugs

# Run floss analysis (after setup)
cd fastapi && floss run
```

## Structure

```
fastapi/
├── setup.sh           # Centralized, parametrized setup script
├── floss.conf       # Shared configuration for all bugs
├── README.md          # This documentation
├── bug1/              # Bug-specific directories
│   ├── README.md      # Bug description and details (if available)
│   ├── bug_patch.txt  # Actual patch that fixes the bug
│   └── report.json    # Expected floss output
├── bug2/
│   ├── bug_patch.txt
│   └── report.json
├── ... (bug3 through bug16)
└── multi-bugs/        # Multiple bugs combined scenario
    ├── bug_patch.txt
    └── report.json
```

## How It Works

1. **Centralized Setup**: One script (`setup.sh`) handles all bugs, eliminating code duplication
2. **Shared Configuration**: All bugs use the same `floss.conf` file
3. **Isolated Environments**: Each bug gets its own virtual environment (`fastapi-bug<N>`)
4. **Bug-Specific Data**: Individual directories contain bug-specific documentation, expected results, and patch files
5. **Patch Files**: Each bug includes a `bug_patch.txt` file with the exact fix for comparison with floss results

## Environment Details

- **Python Version**: 3.8.3 (required by BugsInPy)
- **Virtual Environments**: `fastapi-bug1` through `fastapi-bug16`, `fastapi-multi-bugs`
- **Dependencies**: FastAPI, PyTest, Pydantic (installed automatically)

## CI/CD Integration

The setup is integrated with the project's CI pipeline (`.github/workflows/examples.yml`). The workflow:

1. Sets up Python 3.8
2. Installs floss
3. Runs the centralized setup for each bug
4. Executes floss analysis
5. Validates the output structure

## Bug Details

| Bug | Description | Category | Patch Available |
|-----|-------------|----------|-----------------|
| [1](bug1/) | Response model handling issue | Response Model | ✓ |
| [2](bug2/) | OpenAPI Schema Generation Issue | Schema Generation | ✓ |
| [3](bug3/) | Request Validation Error | Input Validation | ✓ |
| [4](bug4/) | Request body validation error | Input Validation | ✓ |
| [5](bug5/) | Path parameter handling issue | Parameter Handling | ✓ |
| [6](bug6/) | Dependency Injection Problem | Dependency Management | ✓ |
| [7](bug7/) | Response serialization problem | Response Handling | ✓ |
| [8](bug8/) | Authentication middleware issue | Middleware | ✓ |
| [9](bug9/) | Query parameter validation error | Parameter Validation | ✓ |
| [10](bug10/) | File upload handling issue | File Handling | ✓ |
| [11](bug11/) | Response Model Validation Issue | Response Validation | ✓ |
| [12](bug12/) | WebSocket connection error | WebSocket | ✓ |
| [13](bug13/) | Middleware execution order issue | Middleware | ✓ |
| [14](bug14/) | Exception handling problem | Error Handling | ✓ |
| [15](bug15/) | Static file serving issue | Static Files | ✓ |
| [16](bug16/) | Background task execution error | Background Tasks | ✓ |
| [multi-bugs](multi-bugs/) | Multiple bugs combined | Advanced Testing | ✓ |

## Troubleshooting

### Common Issues

1. **Python Version**: Ensure you have Python 3.8.x installed
2. **Permissions**: Make sure `setup.sh` is executable (`chmod +x setup.sh`)
3. **Git Access**: The script clones BugsInPy, ensure Git is available
4. **Environment Conflicts**: Each bug uses separate virtual environments to avoid conflicts

### Cleanup

To remove all virtual environments:

```bash
rm -rf fastapi-bug* BugsInPy fastapi
```

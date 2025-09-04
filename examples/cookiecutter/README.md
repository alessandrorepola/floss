# Cookiecutter Bug Examples

This directory contains examples for testing floss with different Cookiecutter bugs. Cookiecutter is a command-line utility that creates projects from project templates.

## Quick Start

Use the centralized setup script to prepare the environment for any bug:

```bash
./setup.sh <bug_number>
```

**Available bugs:** 1, 2

### Examples

```bash
# Setup environment for bug 1
./setup.sh 1

# Setup environment for bug 2
./setup.sh 2

# Run floss analysis (after setup)
cd cookiecutter && floss run
```

## Structure

```
cookiecutter/
├── setup.sh           # Centralized, parametrized setup script
├── floss.conf       # Shared configuration for all bugs
├── README.md          # This documentation
├── bug1/              # Bug-specific directories
│   ├── bug_patch.txt  # Actual patch that fixes the bug
│   └── report.json    # Expected floss output
└── bug2/
    ├── bug_patch.txt
    └── report.json
```

## How It Works

1. **Centralized Setup**: One script (`setup.sh`) handles all bugs, eliminating code duplication
2. **Shared Configuration**: All bugs use the same `floss.conf` file
3. **Isolated Environments**: Each bug gets its own virtual environment (`cookiecutter-bug<N>`)
4. **Bug-Specific Data**: Individual directories contain bug-specific expected results and patch files
5. **Patch Files**: Each bug includes a `bug_patch.txt` file with the exact fix for comparison with floss results

## Environment Details

- **Python Version**: 3.8+ (compatible with Cookiecutter requirements)
- **Virtual Environments**: `cookiecutter-bug1`, `cookiecutter-bug2`
- **Dependencies**: Cookiecutter, PyTest (installed automatically)

## Bug Details

| Bug | Description | Category | Patch Available |
|-----|-------------|----------|-----------------|
| [1](bug1/) | File encoding issue in context parsing | File Handling | ✓ |
| [2](bug2/) | Template variable substitution error | Template Processing | ✓ |

## Troubleshooting

### Common Issues

1. **Python Version**: Ensure you have Python 3.8+ installed
2. **Permissions**: Make sure `setup.sh` is executable (`chmod +x setup.sh`)
3. **Git Access**: The script clones Cookiecutter repository, ensure Git is available
4. **Environment Conflicts**: Each bug uses separate virtual environments to avoid conflicts

### Cleanup

To remove all virtual environments:

```bash
rm -rf cookiecutter-bug* cookiecutter
```

## Understanding the Bugs

### Bug 1: File Encoding Issue
- **Problem**: File opened without explicit encoding specification
- **Fix**: Add `encoding='utf-8'` parameter to file open operations
- **Impact**: Causes issues when processing files with non-ASCII characters

### Bug 2: Template Variable Substitution
- **Problem**: Template variables not properly substituted in certain contexts
- **Fix**: Improve variable substitution logic
- **Impact**: Generates incorrect project files from templates

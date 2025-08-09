# PyFault Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Comprehensive documentation suite
- Architecture documentation with system overview
- API reference with detailed examples
- User guide with best practices
- Contributing guidelines for developers

### Changed
- Improved project structure documentation
- Enhanced README with feature overview

## [0.1.0] - 2025-01-09

### Added
- Initial release of PyFault framework
- Core SBFL formula implementations (Ochiai, Tarantula, Jaccard, D*)
- Comprehensive CLI interface with four main commands
- Interactive Streamlit dashboard for visualization
- Test execution with enhanced coverage collection
- Complete fault localization pipeline
- Configuration file support
- Multi-tab dashboard interface:
  - Overview tab with summary metrics
  - Source code viewer with suspiciousness highlighting
  - Test-to-fault analysis with coverage matrix
  - Treemap visualization for hierarchical project view
  - Sunburst chart for circular hierarchy representation
  - Formula comparison for side-by-side analysis
  - Formula performance metrics and benchmarking

### Features

#### CLI Commands
- `pyfault test`: Execute tests with coverage collection
- `pyfault fl`: Calculate fault localization scores
- `pyfault run`: Complete pipeline execution in one command
- `pyfault ui`: Launch interactive dashboard

#### SBFL Formulas
- **Ochiai**: Most effective general-purpose formula
- **Tarantula**: Classic baseline formula for comparison
- **Jaccard**: Similarity-based approach
- **D* (D-Star)**: Optimized binary formula with configurable exponent

#### Dashboard Features
- Interactive source code browser with syntax highlighting
- Real-time suspiciousness score visualization
- Coverage matrix heatmaps
- Hierarchical project structure views
- Multi-formula comparison and correlation analysis
- Performance metrics and effectiveness analysis
- Export capabilities for reports and data

#### Technical Features
- Integration with pytest for test execution
- Enhanced coverage collection using coverage.py
- JSON-based data formats for interoperability
- Configurable file patterns for ignore/omit
- Comprehensive error handling and debugging support
- Rich terminal output with progress indicators
- Memory-efficient processing for large codebases

#### Configuration
- INI-style configuration files (`pyfault.conf`)
- Command-line argument overrides
- Flexible source and test directory specification
- Customizable formula selection
- Pattern-based file filtering

### Technical Implementation
- Built on Python 3.9+ with modern type hints
- Modular architecture with clear separation of concerns
- Comprehensive test suite with unit, integration, and E2E tests
- Performance optimizations for large projects
- Extensible formula system for research and development

### Dependencies
- **Core**: rich, click, pytest, numpy, coverage
- **UI**: streamlit, plotly, pandas (optional)
- **Development**: mypy, black, flake8, pre-commit (optional)

### Supported Platforms
- Python 3.9, 3.10, 3.11, 3.12
- Cross-platform support (Windows, macOS, Linux)
- Integration with popular development environments

---

## Release Notes Format

### Types of Changes
- **Added** for new features
- **Changed** for changes in existing functionality
- **Deprecated** for soon-to-be removed features
- **Removed** for now removed features
- **Fixed** for any bug fixes
- **Security** for vulnerability fixes

### Version History

This is the initial release of PyFault. Future releases will maintain backward compatibility within major versions and provide clear migration paths for breaking changes.

### Future Roadmap

Planned features for upcoming releases:
- Additional SBFL formulas and algorithms
- Real-time fault localization during development
- IDE plugins and integrations
- Machine learning-enhanced suspiciousness calculation
- Multi-language support beyond Python
- Distributed processing for large-scale analysis
- Advanced visualization options (3D, VR)
- Collaborative fault localization workflows
- Historical trend analysis
- REST API for programmatic access

### Migration Guide

As this is the initial release, no migration is required. Future releases will include migration guides for any breaking changes.

### Known Issues

- Large projects (>10,000 lines) may experience slower processing
- Dashboard performance may degrade with very large coverage matrices
- Memory usage increases linearly with number of test-line combinations

### Performance Characteristics

- **Small projects** (<1,000 lines): Sub-second analysis
- **Medium projects** (1,000-10,000 lines): 1-10 second analysis
- **Large projects** (>10,000 lines): 10+ second analysis
- **Memory usage**: ~100MB base + ~1MB per 1,000 lines analyzed

### Acknowledgments

PyFault 0.1.0 incorporates research and techniques from the software engineering and fault localization community. Special thanks to:

- The GZoltar project for inspiration and reference implementations
- The Python testing and coverage ecosystem (pytest, coverage.py)
- The Streamlit and Plotly communities for visualization tools
- Academic researchers in spectrum-based fault localization

---

*For detailed technical changes and implementation notes, see the git commit history and pull request discussions.*

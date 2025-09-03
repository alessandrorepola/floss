# Complete Analysis of PyFault and SBFL Formula Effectiveness

NOTE: The results reported are approximate and have no statistical or demonstrative validity. Their use is to be understood exclusively for informational purposes to support understanding of the PyFault tool's ability to identify lines of code containing bugs. Therefore, these results should not be considered as definitive or conclusive.

## Executive Summary

This document presents a comprehensive analysis of PyFault's effectiveness in identifying lines of code containing bugs, with particular attention to comparing the different Spectrum-Based Fault Localization (SBFL) formulas implemented in the tool.

## General Effectiveness Metrics

### Analyzed Dataset
- **Total bugs**: 30
- **Analyzable bugs** (with patch): 24 (80%)
- **Projects**: 4 (Black, Cookiecutter, FastAPI, PyGraphistry)

### Overall Effectiveness (Reference Formula: Ochiai)
- **Top-1 hit rate**: 25.0% (6/24 bugs identified in first position)
- **Top-3 hit rate**: 37.5% (9/24 bugs identified in top 3 positions)
- **Top-5 hit rate**: 45.8% (11/24 bugs identified in top 5 positions)
- **Top-10 hit rate**: 54.2% (13/24 bugs identified in top 10 positions)
- **Best average rank**: 162.5

### Effectiveness by Project
- **Cookiecutter**: 100% success rate (2/2 bugs in top-10)
- **PyGraphistry**: 100% success rate (1/1 bug in top-10)
- **Black**: 55.6% success rate (5/9 bugs in top-10)
- **FastAPI**: 41.7% success rate (5/12 bugs in top-10)

## Detailed Comparison of SBFL Formulas

### 1. Ranking Effectiveness (Top-N Analysis)

| Formula     | Bugs | Top-1 | Top-3 | Top-5 | Top-10 | Avg Rank | Med Rank | Best | P25 | P75 |
|-------------|------|-------|-------|-------|--------|----------|----------|------|-----|-----|
| **Ochiai**  | 24   | 25.0% | 37.5% | 45.8% | 54.2%  | 162.5    | 10       | 1    | 2   | 174 |
| **Tarantula**| 24  | 25.0% | 41.7% | 45.8% | 54.2%  | 160.3    | 10       | 1    | 2   | 194 |
| **Jaccard** | 24   | 25.0% | 37.5% | 41.7% | 54.2%  | 160.3    | 10       | 1    | 2   | 187 |
| **Dstar2**  | 24   | 25.0% | 33.3% | 41.7% | 50.0%  | 179.3    | 11       | 1    | 2   | 283 |

#### Rank Distribution
- **Ochiai**: 1-5: 11, 6-10: 2, 11-20: 2, 21-50: 2, 51+: 7
- **Tarantula**: 1-5: 11, 6-10: 2, 11-20: 3, 21-50: 2, 51+: 6
- **Jaccard**: 1-5: 10, 6-10: 3, 11-20: 3, 21-50: 2, 51+: 6
- **Dstar2**: 1-5: 10, 6-10: 2, 11-20: 2, 21-50: 2, 51+: 8

### 2. Discriminatory Capability

Discriminatory capability measures how effectively each formula distinguishes lines with bugs from lines without bugs.

| Formula     | AUC-ROC | Score Separation | Overlap | Perfect Separations |
|-------------|---------|------------------|---------|---------------------|
| **Jaccard** | 0.628   | 0.117           | 0.550   | 4.2%               |
| **Ochiai**  | 0.627   | 0.192           | 0.554   | 4.2%               |
| **Tarantula**| 0.625  | 0.426           | 0.556   | 4.2%               |
| **Dstar2**  | 0.578   | 0.170           | 0.591   | 4.2%               |

#### Detailed Discrimination Metrics

**Ochiai:**
- Average buggy line scores: 0.247 ± 0.238
- Average non-buggy line scores: 0.055 ± 0.075
- High overlap cases (>50%): 13/24 (54%)

**Tarantula:**
- Average buggy line scores: 0.699 ± 0.288
- Average non-buggy line scores: 0.273 ± 0.240
- High overlap cases (>50%): 13/24 (54%)

**Jaccard:**
- Average buggy line scores: 0.186 ± 0.159
- Average non-buggy line scores: 0.069 ± 0.084
- High overlap cases (>50%): 13/24 (54%)

**Dstar2:**
- Average buggy line scores: 0.264 ± 0.315
- Average non-buggy line scores: 0.094 ± 0.158
- High overlap cases (>50%): 14/24 (58%)

## Comparative Analysis

### Best Formulas by Specific Metric

1. **Top-1 Accuracy**: All formulas perform equally (25.0%)
2. **Top-3 Accuracy**: **Tarantula** (41.7%)
3. **Top-10 Accuracy**: **Ochiai, Tarantula, Jaccard** (54.2%)
4. **Average Rank**: **Tarantula and Jaccard** (160.3)
5. **AUC-ROC**: **Jaccard** (0.628)
6. **Score Separation**: **Tarantula** (0.426)
7. **Least Overlap**: **Jaccard** (0.550)

### Recommendations

1. **Primary Recommended Formula: Tarantula**
   - Best performance in Top-3
   - Excellent average rank
   - Superior score separation
   - Good discriminatory capability

2. **Secondary Recommended Formula: Jaccard**
   - Best AUC-ROC
   - Lowest overlap between distributions
   - Competitive ranking performance

3. **Formula to Avoid: Dstar2**
   - Inferior performance in all metrics
   - Higher overlap between distributions
   - Worst average rank

## Limitations and Considerations

### Dataset Size
- The dataset is relatively small (24 analyzable bugs)
- Some projects have few bugs (Cookiecutter: 2, PyGraphistry: 1)
- Result variability may be influenced by limited size

### Bug Types
- The analyzed bugs vary significantly in complexity
- Multi-bugs present additional challenges in identification
- Bugs in different projects may have different characteristics

### Evaluation Metrics
- Effectiveness is primarily measured on top-N ranks
- Discriminatory capability provides a complementary view
- AUC-ROC may be influenced by data distribution

## Conclusions

1. **PyFault shows moderate effectiveness** with 54% of bugs identifiable in the top 10 positions
2. **Tarantula emerges as the most performant formula** for general use
3. **Jaccard offers the best discriminatory capability** for distinguishing buggy from non-buggy lines
4. **Dstar2 presents inferior performance** compared to other formulas
5. **Effectiveness varies significantly between projects**, suggesting that project-specific factors influence performance

## Recommendations for Future Development

1. **Implement an ensemble approach** that combines multiple formulas
2. **Develop project-specific heuristics** to improve accuracy
3. **Integrate additional information** beyond test coverage (e.g., code complexity, change history)
4. **Expand the evaluation dataset** with more projects and bug types
5. **Investigate machine learning techniques** for fault localization

---

*Analysis automatically generated by PyFault Effectiveness Analyzer*
*Date: September 3, 2025*

## Project Performance Summary
1. **Cookiecutter**: 100.0% (2/2) - Excellent
2. **PyGraphistry**: 100.0% (1/1) - Perfect on single bug
3. **Black**: 55.6% (5/9) - Good performance
4. **FastAPI**: 41.7% (5/12) - Moderate performance

## Detailed Analysis by Project

### Black Project
- **9 analyzable bugs** out of 10 total
- **5 bugs found** in top-10 (55.6%)
- **Best performers**: bug15, bug18 (rank 1)
- **Multi-bug performance**: Significant degradation
  - bugs_17-18-19-20: rank 81
  - bugs_19-22-23: rank 174

### Cookiecutter Project  
- **2 analyzable bugs** out of 2 total
- **100% success rate** in top-10
- **Consistent performance**: bug1 (rank 4), bug2 (rank 1)

### FastAPI Project
- **12 analyzable bugs** out of 17 total
- **5 bugs found** in top-10 (41.7%)
- **Best performers**: bug12, bug16, multi-1-9-12-13-15-16 (rank 1)
- **Multi-bug included**: The multi-bug has excellent performance (rank 1)

### PyGraphistry Project
- **1 analyzable bug** out of 1 total
- **100% success rate** (rank 2)

## SBFL Formula Comparison

### Performance Ranking (average ranks)
1. **Tarantula**: 160.3
2. **Jaccard**: 160.3  
3. **Ochiai**: 162.5
4. **DStar2**: 179.3

### Observations
- **Tarantula and Jaccard** show slightly better performance
- **DStar2** has more variable performance
- Differences between formulas are relatively modest

## Multi-Bug Analysis

### Impact on Rankings
Multi-bug scenarios generally show **degraded performance** compared to individual bugs:

- **Black bugs_17-18-19-20**: rank 81 vs individual ranks 1-12
- **Black bugs_19-22-23**: rank 174 vs individual ranks 10-400  
- **FastAPI multi-1-9-12-13-15-16**: rank 1 (positive exception)

### Interpretation
Interference between multiple bugs can:
- **Confuse SBFL formulas** with contradictory signals
- **Reduce precision** of suspiciousness ranking
- **Require specialized techniques** for multi-fault scenarios

## Limits and Considerations

### Dataset Limitations
- **Limited size**: 24 analyzable bugs
- **Project diversity**: Variety in size and complexity
- **Artificial vs real bugs**: Mix of bug types

### Methodological Limitations  
- **Classic SBFL formulas**: Not optimized for multi-bug
- **Static coverage**: Based only on test execution
- **Missing baseline**: Lack of comparison with other tools

## Conclusions and Recommendations

### Main Conclusions
1. **Moderate effectiveness**: 54.2% top-10 hit rate is competitive
2. **Project variability**: Large difference between projects (41.7% - 100%)
3. **Multi-bug impact**: Multi-bugs significantly reduce effectiveness
4. **Formula consistency**: Similar performance between SBFL formulas

### Recommendations
1. **Multi-bug improvement**: Develop specific techniques for multi-fault scenarios
2. **Project customization**: Adapt approach based on project characteristics
3. **Dataset extension**: Validate on larger and more diversified datasets
4. **Hybrid approaches**: Combine SBFL with other techniques (ML, static analysis)

### Future Directions
- **Machine Learning**: Integration with ML approaches to improve ranking
- **Context-aware FL**: Consider semantic and structural information
- **Multi-bug strategies**: Fault decomposition and isolation techniques
- **Evaluation metrics**: More sophisticated metrics to evaluate effectiveness

---

**Analysis Date**: September 3, 2025
**Tool Versions**: PyFault v0.1.0, Python 3.12  
**Dataset**: 30 bugs, 4 projects, 3 multi-bug scenarios

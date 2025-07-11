"""
Core module for PyFault.
"""

from .fault_localizer import FaultLocalizer
from .models import (
    CoverageMatrix, 
    TestResult, 
    SuspiciousnessScore,
    FaultLocalizationResult,
    CodeElement,
    TestOutcome
)

__all__ = [
    "FaultLocalizer",
    "CoverageMatrix",
    "TestResult", 
    "SuspiciousnessScore",
    "FaultLocalizationResult",
    "CodeElement",
    "TestOutcome"
]

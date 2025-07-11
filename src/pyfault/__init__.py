"""
PyFault: Spectrum-Based Fault Localization for Python

A Python framework for automated fault localization using SBFL techniques,
inspired by GZoltar.
"""

__version__ = "0.1.0"
__author__ = "PyFault Contributors"

from .core.fault_localizer import FaultLocalizer
from .core.models import CoverageMatrix, TestResult, SuspiciousnessScore
from .formulas import OchiaiFormula, TarantulaFormula, JaccardFormula

__all__ = [
    "FaultLocalizer",
    "CoverageMatrix", 
    "TestResult",
    "SuspiciousnessScore",
    "OchiaiFormula",
    "TarantulaFormula", 
    "JaccardFormula",
]

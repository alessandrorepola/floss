"""
PyFault: Spectrum-Based Fault Localization for Python

A Python framework for automated fault localization using SBFL techniques.
"""

__version__ = "0.1.0"
__author__ = "PyFault Contributors"

from pyfault.core.fl import FLConfig, FLEngine
from pyfault.core.test import TestConfig, TestRunner

__all__ = [
    "TestRunner",
    "TestConfig",
    "FLEngine",
    "FLConfig",
]

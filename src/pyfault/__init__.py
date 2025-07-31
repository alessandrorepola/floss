"""
PyFault: Spectrum-Based Fault Localization for Python

A Python framework for automated fault localization using SBFL techniques.
"""

__version__ = "0.1.0"
__author__ = "PyFault Contributors"

from .test import TestRunner, TestConfig
from .fl import FLEngine, FLConfig

__all__ = [
    "TestRunner",
    "TestConfig",
    "FLEngine", 
    "FLConfig",
]

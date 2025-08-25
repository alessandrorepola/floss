"""
PyFault: Spectrum-Based Fault Localization for Python

A Python framework for automated fault localization using SBFL techniques.
"""

__version__ = "0.1.0"
__author__ = "PyFault Contributors"

from .core.test import TestRunner, TestConfig
from .core.fl import FLEngine, FLConfig

__all__ = [
    "TestRunner",
    "TestConfig",
    "FLEngine", 
    "FLConfig",
]

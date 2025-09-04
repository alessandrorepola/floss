"""
FLOSS: Fault Localization with Spectrum-based Scoring

A Python framework for automated fault localization using SBFL techniques.
"""

__version__ = "0.1.0"
__author__ = "FLOSS Contributors"

from floss.core.fl import FLConfig, FLEngine
from floss.core.test import TestConfig, TestRunner

__all__ = [
    "TestRunner",
    "TestConfig",
    "FLEngine",
    "FLConfig",
]

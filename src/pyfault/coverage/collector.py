"""
Coverage collection module.

This module provides functionality for collecting code coverage information
during test execution, similar to GZoltar's instrumentation capabilities.
"""

import sys
import coverage
import threading
from pathlib import Path
from typing import Set, List, Dict, Optional, Union
from collections import defaultdict

from ..core.models import CodeElement


class CoverageCollector:
    """
    Collects code coverage information during test execution.
    
    This class uses Python's coverage.py library to instrument code and
    collect coverage data, similar to how GZoltar uses JaCoCo for Java.
    
    Example:
        >>> collector = CoverageCollector(['src'])
        >>> collector.start()
        >>> # Run tests here
        >>> coverage_data = collector.get_coverage_for_test('test_example')
        >>> collector.stop()
    """
    
    def __init__(self, source_dirs: List[Path], include_patterns: Optional[List[str]] = None):
        """
        Initialize the coverage collector.
        
        Args:
            source_dirs: Directories containing source code to track
            include_patterns: Optional patterns for files to include
        """
        self.source_dirs = source_dirs
        self.include_patterns = include_patterns or ['*.py']
        self.coverage_data: Dict[str, Set[CodeElement]] = defaultdict(set)
        self.current_test: Optional[str] = None
        self._coverage_instance: Optional[coverage.Coverage] = None
        self._is_collecting = False
        self._lock = threading.Lock()
    
    def start(self) -> None:
        """Start coverage collection."""
        if self._is_collecting:
            return
        
        with self._lock:
            # Configure coverage to track our source directories
            source_paths = [str(d) for d in self.source_dirs]
            
            self._coverage_instance = coverage.Coverage(
                source=source_paths,
                include=self.include_patterns,
                branch=True,  # Track branch coverage
                auto_data=False,  # We'll handle data manually
            )
            
            self._coverage_instance.start()
            self._is_collecting = True
    
    def stop(self) -> None:
        """Stop coverage collection."""
        if not self._is_collecting:
            return
        
        with self._lock:
            if self._coverage_instance:
                self._coverage_instance.stop()
            self._is_collecting = False
    
    def start_test(self, test_name: str) -> None:
        """Start tracking coverage for a specific test."""
        with self._lock:
            self.current_test = test_name
            if self._coverage_instance:
                # Clear any previous data for this test
                self._coverage_instance.erase()
                # Restart to get fresh data for this test
                if self._is_collecting:
                    self._coverage_instance.stop()
                self._coverage_instance.start()
    
    def end_test(self, test_name: str) -> None:
        """End tracking for the current test and store coverage data."""
        if not self._is_collecting or not self._coverage_instance:
            return
        
        with self._lock:
            # Stop collection temporarily to get data
            self._coverage_instance.stop()
            
            # Extract coverage data
            covered_elements = self._extract_coverage_data()
            self.coverage_data[test_name] = covered_elements
            
            # Restart collection if needed
            if self._is_collecting:
                self._coverage_instance.start()
    
    def get_coverage_for_test(self, test_name: str) -> Set[CodeElement]:
        """
        Get coverage data for a specific test.
        
        Args:
            test_name: Name of the test
            
        Returns:
            Set of code elements covered by the test
        """
        return self.coverage_data.get(test_name, set())
    
    def _extract_coverage_data(self) -> Set[CodeElement]:
        """Extract coverage data from the current coverage instance."""
        if not self._coverage_instance:
            return set()
        
        covered_elements = set()
        
        try:
            # Get the coverage data
            data = self._coverage_instance.get_data()
            
            # Process each file
            for filename in data.measured_files():
                file_path = Path(filename)
                
                # Skip files not in our source directories
                if not any(self._is_file_in_dir(file_path, source_dir) 
                          for source_dir in self.source_dirs):
                    continue
                
                # Get line coverage for this file
                lines = data.lines(filename) or []
                
                for line_number in lines:
                    element = CodeElement(
                        file_path=file_path,
                        line_number=line_number,
                        element_type="line"
                    )
                    covered_elements.add(element)
        
        except Exception as e:
            # Log error but don't break the flow
            print(f"Warning: Error extracting coverage data: {e}")
        
        return covered_elements
    
    def _is_file_in_dir(self, file_path: Path, directory: Path) -> bool:
        """Check if a file is within a directory."""
        try:
            file_path.resolve().relative_to(directory.resolve())
            return True
        except ValueError:
            return False
    
    def get_all_coverage_data(self) -> Dict[str, Set[CodeElement]]:
        """Get all collected coverage data."""
        return dict(self.coverage_data)
    
    def clear_data(self) -> None:
        """Clear all collected coverage data."""
        with self._lock:
            self.coverage_data.clear()


class SimpleCoverageCollector:
    """
    A simplified coverage collector for testing purposes.
    
    This collector doesn't use real instrumentation but allows manual
    registration of coverage data.
    """
    
    def __init__(self):
        """Initialize the simple collector."""
        self.coverage_data: Dict[str, Set[CodeElement]] = defaultdict(set)
    
    def add_coverage(self, test_name: str, elements: Set[CodeElement]) -> None:
        """Manually add coverage data for a test."""
        self.coverage_data[test_name] = elements
    
    def get_coverage_for_test(self, test_name: str) -> Set[CodeElement]:
        """Get coverage data for a test."""
        return self.coverage_data.get(test_name, set())
    
    def start(self) -> None:
        """No-op for compatibility."""
        pass
    
    def stop(self) -> None:
        """No-op for compatibility.""" 
        pass

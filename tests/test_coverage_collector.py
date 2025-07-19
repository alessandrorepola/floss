"""
Test suite for Coverage Collector module.

This module tests both the real CoverageCollector and SimpleCoverageCollector
with a focus on functional correctness and integration scenarios.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Set
from unittest.mock import Mock, patch, MagicMock

from src.pyfault.coverage.collector import CoverageCollector, SimpleCoverageCollector
from src.pyfault.core.models import CodeElement


class TestSimpleCoverageCollector:
    """Test cases for SimpleCoverageCollector (black-box approach)."""
    
    def setup_method(self):
        """Setup for each test method."""
        self.collector = SimpleCoverageCollector()
    
    def test_empty_collector_initialization(self):
        """Test that collector initializes with empty state."""
        assert len(self.collector.coverage_data) == 0
        assert self.collector.get_coverage_for_test("nonexistent") == set()
    
    def test_add_single_coverage_entry(self):
        """Test adding coverage for a single test."""
        element = CodeElement(Path("test.py"), 10, "line")
        test_elements = {element}
        
        self.collector.add_coverage("test_func", test_elements)
        
        retrieved = self.collector.get_coverage_for_test("test_func")
        assert retrieved == test_elements
        assert element in retrieved
    
    def test_add_multiple_coverage_entries(self):
        """Test adding coverage for multiple tests."""
        element1 = CodeElement(Path("file1.py"), 5, "line")
        element2 = CodeElement(Path("file2.py"), 15, "line")
        element3 = CodeElement(Path("file1.py"), 20, "branch", "if_branch")
        
        self.collector.add_coverage("test_a", {element1, element2})
        self.collector.add_coverage("test_b", {element1, element3})
        self.collector.add_coverage("test_c", {element3})
        
        # Verify each test's coverage
        assert self.collector.get_coverage_for_test("test_a") == {element1, element2}
        assert self.collector.get_coverage_for_test("test_b") == {element1, element3}
        assert self.collector.get_coverage_for_test("test_c") == {element3}
    
    def test_overwrite_coverage_entry(self):
        """Test that adding coverage for the same test overwrites previous data."""
        element1 = CodeElement(Path("test.py"), 10, "line")
        element2 = CodeElement(Path("test.py"), 20, "line")
        
        # First entry
        self.collector.add_coverage("test_func", {element1})
        assert self.collector.get_coverage_for_test("test_func") == {element1}
        
        # Overwrite
        self.collector.add_coverage("test_func", {element2})
        assert self.collector.get_coverage_for_test("test_func") == {element2}
        assert element1 not in self.collector.get_coverage_for_test("test_func")
    
    def test_start_stop_compatibility(self):
        """Test that start/stop methods work for compatibility."""
        # These should not raise exceptions
        self.collector.start()
        self.collector.stop()
        
        # Should still be able to add coverage after start/stop
        element = CodeElement(Path("test.py"), 5, "line")
        self.collector.add_coverage("test", {element})
        assert self.collector.get_coverage_for_test("test") == {element}


class TestCoverageCollector:
    """Test cases for CoverageCollector (functional + integration)."""
    
    def setup_method(self):
        """Setup test environment with temporary directories."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.source_dir = self.temp_dir / "src"
        self.source_dir.mkdir()
        
        # Create a simple Python file to track
        self.test_file = self.source_dir / "example.py"
        self.test_file.write_text("""
def add(a, b):
    if a > 0:
        return a + b
    else:
        return b - a

def multiply(a, b):
    return a * b
""")
    
    def teardown_method(self):
        """Cleanup temporary files."""
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_collector_initialization(self):
        """Test CoverageCollector initialization with various parameters."""
        # Basic initialization
        collector = CoverageCollector([self.source_dir])
        assert self.source_dir in collector.source_dirs
        assert collector.include_patterns == ['*.py']
        assert collector.branch_coverage is False
        assert not collector._is_collecting
        
        # Initialization with custom parameters
        collector = CoverageCollector(
            [self.source_dir], 
            include_patterns=['*.py', '*.pyx'],
            branch_coverage=True
        )
        assert collector.include_patterns == ['*.py', '*.pyx']
        assert collector.branch_coverage is True
    
    def test_start_stop_collection(self):
        """Test starting and stopping coverage collection."""
        collector = CoverageCollector([self.source_dir])
        
        # Test start
        collector.start()
        assert collector._is_collecting is True
        assert collector._coverage_instance is not None
        
        # Test stop
        collector.stop()
        assert collector._is_collecting is False
    
    def test_multiple_start_stop_cycles(self):
        """Test multiple start/stop cycles don't break the collector."""
        collector = CoverageCollector([self.source_dir])
        
        # Multiple cycles should work
        for _ in range(3):
            collector.start()
            assert collector._is_collecting is True
            collector.stop()
            assert collector._is_collecting is False
    
    def test_test_tracking_lifecycle(self):
        """Test the complete lifecycle of test tracking."""
        collector = CoverageCollector([self.source_dir])
        collector.start()
        
        # Start tracking a test
        collector.start_test("test_example")
        assert collector.current_test == "test_example"
        
        # End tracking
        collector.end_test("test_example")
        # Coverage data should be stored
        assert "test_example" in collector.coverage_data
        
        collector.stop()
    
    @patch('src.pyfault.coverage.collector.coverage.Coverage')
    def test_coverage_data_extraction_line_mode(self, mock_coverage_class):
        """Test coverage data extraction in line coverage mode."""
        # Setup mock
        mock_coverage = MagicMock()
        mock_coverage_class.return_value = mock_coverage
        
        mock_data = MagicMock()
        mock_coverage.get_data.return_value = mock_data
        mock_data.measured_files.return_value = [str(self.test_file)]
        mock_data.lines.return_value = [2, 3, 4, 7, 8]
        mock_data.arcs.return_value = None
        
        collector = CoverageCollector([self.source_dir], branch_coverage=False)
        collector._coverage_instance = mock_coverage
        
        # Extract coverage data
        elements = collector._extract_coverage_data()
        
        # Verify line elements were created
        assert len(elements) == 5
        line_numbers = {elem.line_number for elem in elements}
        assert line_numbers == {2, 3, 4, 7, 8}
        
        # All should be line type
        for elem in elements:
            assert elem.element_type == "line"
            assert elem.file_path.name == "example.py"
    
    @patch('src.pyfault.coverage.collector.coverage.Coverage')
    def test_coverage_data_extraction_branch_mode(self, mock_coverage_class):
        """Test coverage data extraction in branch coverage mode."""
        # Setup mock
        mock_coverage = MagicMock()
        mock_coverage_class.return_value = mock_coverage
        
        mock_data = MagicMock()
        mock_coverage.get_data.return_value = mock_data
        mock_data.measured_files.return_value = [str(self.test_file)]
        mock_data.arcs.return_value = [(2, 3), (3, 4), (3, 5), (5, 7)]
        mock_data.lines.return_value = None
        
        collector = CoverageCollector([self.source_dir], branch_coverage=True)
        collector._coverage_instance = mock_coverage
        
        # Extract coverage data
        elements = collector._extract_coverage_data()
        
        # Verify branch elements were created
        assert len(elements) == 4
        
        # All should be branch type
        for elem in elements:
            assert elem.element_type == "branch"
            assert elem.element_name is not None
            assert elem.element_name.startswith("branch:")
    
    def test_file_filtering(self):
        """Test that files outside source directories are filtered out."""
        # Create file outside source directory
        outside_file = self.temp_dir / "outside.py"
        outside_file.write_text("print('hello')")
        
        collector = CoverageCollector([self.source_dir])
        
        # Test the _is_file_in_dir method
        assert collector._is_file_in_dir(self.test_file, self.source_dir) is True
        assert collector._is_file_in_dir(outside_file, self.source_dir) is False
    
    def test_clear_data(self):
        """Test clearing coverage data."""
        collector = CoverageCollector([self.source_dir])
        
        # Add some test data
        element = CodeElement(self.test_file, 10, "line")
        collector.coverage_data["test1"] = {element}
        collector.coverage_data["test2"] = {element}
        
        assert len(collector.coverage_data) == 2
        
        # Clear data
        collector.clear_data()
        assert len(collector.coverage_data) == 0
    
    def test_get_all_coverage_data(self):
        """Test retrieving all coverage data."""
        collector = CoverageCollector([self.source_dir])
        
        # Add test data
        element1 = CodeElement(self.test_file, 10, "line")
        element2 = CodeElement(self.test_file, 20, "line")
        
        collector.coverage_data["test1"] = {element1}
        collector.coverage_data["test2"] = {element2}
        
        all_data = collector.get_all_coverage_data()
        
        # Should return a copy of the data
        assert all_data == collector.coverage_data
        assert all_data is not collector.coverage_data  # Should be a copy
    
    def test_concurrent_access_safety(self):
        """Test thread safety of collector operations."""
        import threading
        import time
        
        collector = CoverageCollector([self.source_dir])
        results = []
        
        def worker(test_name):
            """Worker function for threading test."""
            collector.start_test(f"test_{test_name}")
            time.sleep(0.01)  # Simulate some work
            collector.end_test(f"test_{test_name}")
            results.append(f"test_{test_name}")
        
        # Start multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=worker, args=(i,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads
        for thread in threads:
            thread.join()
        
        # All tests should have completed
        assert len(results) == 5
        assert all(f"test_{i}" in results for i in range(5))


class TestCoverageCollectorEdgeCases:
    """Test edge cases and error conditions (white-box approach)."""
    
    def test_stop_without_start(self):
        """Test stopping collector that was never started."""
        collector = CoverageCollector([Path("/tmp")])
        # Should not raise exception
        collector.stop()
    
    def test_end_test_without_collection(self):
        """Test ending test when collection is not active."""
        collector = CoverageCollector([Path("/tmp")])
        # Should not raise exception
        collector.end_test("test_name")
        assert "test_name" not in collector.coverage_data
    
    def test_nonexistent_source_directory(self):
        """Test behavior with non-existent source directories."""
        nonexistent_dir = Path("/this/path/does/not/exist")
        collector = CoverageCollector([nonexistent_dir])
        
        # Should initialize without error
        assert nonexistent_dir in collector.source_dirs
        
        # Should handle gracefully during collection
        collector.start()
        collector.stop()
    
    @patch('src.pyfault.coverage.collector.coverage.Coverage')
    def test_coverage_extraction_with_errors(self, mock_coverage_class):
        """Test error handling during coverage data extraction."""
        # Setup mock that raises exception
        mock_coverage = MagicMock()
        mock_coverage_class.return_value = mock_coverage
        mock_coverage.get_data.side_effect = Exception("Coverage error")
        
        collector = CoverageCollector([Path("/tmp")])
        collector._coverage_instance = mock_coverage
        
        # Should handle exception gracefully and return empty set
        elements = collector._extract_coverage_data()
        assert isinstance(elements, set)
        assert len(elements) == 0
    
    def test_coverage_with_negative_line_numbers(self):
        """Test handling of negative line numbers from coverage.py."""
        collector = CoverageCollector([Path("/tmp")], branch_coverage=True)
        
        # Mock coverage data with negative line numbers (exit points)
        with patch.object(collector, '_coverage_instance') as mock_cov:
            mock_data = MagicMock()
            mock_cov.get_data.return_value = mock_data
            mock_data.measured_files.return_value = ["/tmp/test.py"]
            mock_data.arcs.return_value = [(2, 3), (-1, 0), (5, -1)]  # Include negative numbers
            
            elements = collector._extract_coverage_data()
            
            # Should filter out arcs with negative line numbers
            assert len(elements) == 1  # Only (2, 3) should be included
            element = list(elements)[0]
            assert element.line_number == 2
            assert element.element_name is not None
            assert "2->3" in element.element_name


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

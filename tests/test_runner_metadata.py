"""
Tests that validate TestRunner augments coverage JSON with expected
meta and totals fields, including reordering.
"""

from pyfault.test.config import TestConfig
from pyfault.test.runner import TestRunner


def test_add_pyfault_metadata_and_summary_reorg():
    config = TestConfig()
    config.source_dir = "src"
    runner = TestRunner(config)

    coverage_data = {
        "meta": {"format": 3},
        "files": {"f.py": {"contexts": {}}},
        "totals": {},
    }
    test_outcomes = {"failed": ["t_fail"], "passed": ["t_pass"], "skipped": []}

    updated = runner._add_pyfault_metadata(coverage_data, test_outcomes)
    assert updated["meta"]["tool"] == "PyFault"
    assert updated["meta"]["phase"] == "test_execution"
    assert updated["meta"]["source_dir"] == "src"

    reorganized = runner._add_test_summary_info(updated, test_outcomes)
    assert list(reorganized.keys())[:2] == ["meta", "totals"]  # promoted order
    ts = reorganized["totals"]["test_statistics"]
    assert ts["total_tests"] == 2
    assert ts["failed_tests"] == 1
    assert ts["passed_tests"] == 1
    assert ts["skipped_tests"] == 0

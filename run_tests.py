#!/usr/bin/env python3
"""Testes unitários (matriz agent_action) — corre na raiz do clone, sem PYTHONPATH."""
from __future__ import annotations

import sys
import unittest
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
if str(_ROOT / "runtime") not in sys.path:
    sys.path.insert(0, str(_ROOT / "runtime"))
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))


if __name__ == "__main__":
    loader = unittest.defaultTestLoader
    suite = unittest.TestSuite()
    suite.addTests(loader.loadTestsFromName("tests.test_matrix_example"))
    suite.addTests(loader.loadTestsFromName("tests.test_validator"))
    suite.addTests(loader.loadTestsFromName("tests.test_pii"))
    suite.addTests(loader.loadTestsFromName("tests.test_exams_catalog"))
    suite.addTests(loader.loadTestsFromName("tests.test_mcp_ocr_engine"))
    suite.addTests(loader.loadTestsFromName("tests.test_mcp_rag_matcher"))
    suite.addTests(loader.loadTestsFromName("tests.test_api_appointments"))
    suite.addTests(loader.loadTestsFromName("tests.test_tools_unit"))
    suite.addTests(loader.loadTestsFromName("tests.test_lab_runtime"))
    suite.addTests(loader.loadTestsFromName("tests.test_cli_flow"))
    suite.addTests(loader.loadTestsFromName("tests.test_e2e_offline_full"))
    suite.addTests(loader.loadTestsFromName("tests.test_generator"))
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    sys.exit(0 if result.wasSuccessful() else 1)

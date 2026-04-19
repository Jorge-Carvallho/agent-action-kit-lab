"""Runtime laboratorial (`lab_runtime`)."""
from __future__ import annotations

import os
import unittest
from unittest.mock import patch


class TestLabRuntime(unittest.TestCase):
    def test_get_lab_extra_tools_empty_when_disabled(self) -> None:
        with patch.dict(os.environ, {"LAB_AGENT_TOOLS": "0"}, clear=False):
            from agent_action.lab_runtime import get_lab_extra_tools, lab_adk_tools_enabled

            self.assertFalse(lab_adk_tools_enabled())
            self.assertEqual(get_lab_extra_tools(), [])


if __name__ == "__main__":
    unittest.main()

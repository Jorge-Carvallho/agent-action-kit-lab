"""
Espelha a ideia de tests/test_agent_context_matrix.py: trocar AGENT_ACTION e reimportar.

Importante: chamar get_agent_profile() / get_agent_prompt() **dentro** do mesmo
`patch.dict(os.environ, ...)` usado no import, senão o ambiente restaura antes
das asserções.
"""
from __future__ import annotations

import importlib
import os
import sys
import unittest
from unittest.mock import patch


def _clear_agent_action_modules() -> None:
    for name in list(sys.modules.keys()):
        if name == "agent_action" or name.startswith("agent_action."):
            sys.modules.pop(name, None)


class TestAgentActionMatrix(unittest.TestCase):
    def test_lab_context(self):
        _clear_agent_action_modules()
        with patch.dict(os.environ, {"AGENT_ACTION": "lab"}, clear=False):
            pr = importlib.import_module("agent_action.profile_runtime")
            profile = pr.get_agent_profile()
            self.assertEqual(profile.action, "lab")
            self.assertEqual(profile.app_name, "lab_exam_scheduler_kit")
            self.assertEqual(profile.domain, "laboratory_scheduling")
            self.assertEqual(profile.instruction_key, "lab_example")
            pl = importlib.import_module("agent_action.prompt_loader")
            text = pl.get_agent_prompt()
            self.assertIn("laboratoriais", text)
            self.assertIn("OCR", text)

    def test_generic_context(self):
        _clear_agent_action_modules()
        with patch.dict(os.environ, {"AGENT_ACTION": "generic"}, clear=False):
            pr = importlib.import_module("agent_action.profile_runtime")
            profile = pr.get_agent_profile()
            self.assertEqual(profile.action, "generic")
            self.assertEqual(profile.domain, "generic_assistant")
            pl = importlib.import_module("agent_action.prompt_loader")
            text = pl.get_agent_prompt()
            self.assertIn("assistente", text.lower())

    def test_invalid_agent_action(self):
        _clear_agent_action_modules()
        with patch.dict(os.environ, {"AGENT_ACTION": "invalid"}, clear=False):
            pr = importlib.import_module("agent_action.profile_runtime")
            with self.assertRaises(ValueError):
                pr.get_agent_profile()


if __name__ == "__main__":
    unittest.main()

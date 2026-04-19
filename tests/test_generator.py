"""
Testes do transpilador — geração de código (AI-005).
"""
from __future__ import annotations

import json
import subprocess
import sys
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO))

from transpiler.generator import generate_source, write_generated_agent
from transpiler.validator import validate


class TestGenerateSource(unittest.TestCase):
    def setUp(self) -> None:
        with (_REPO / "examples" / "agent_spec.json").open(encoding="utf-8") as f:
            self.spec = json.load(f)
        validate(self.spec, raise_on_error=True)

    def test_contains_adk_imports(self) -> None:
        src = generate_source(self.spec, output_path=_REPO / "examples" / "generated_agent.py")
        self.assertIn("from google.adk.agents import Agent", src)
        self.assertIn("from google.adk.runners import InMemoryRunner", src)
        self.assertIn("InMemoryRunner(agent=root_agent", src)

    def test_contains_agent_and_model_from_spec(self) -> None:
        src = generate_source(self.spec, output_path=_REPO / "examples" / "generated_agent.py")
        self.assertIn("lab_scheduler", src)
        self.assertIn("gemini-2.5-flash", src)

    def test_generates_real_tools_not_empty_list(self) -> None:
        src = generate_source(self.spec, output_path=_REPO / "examples" / "generated_agent.py")
        self.assertNotIn("tools=[]", src)
        self.assertIn("FunctionTool(", src)
        self.assertIn("from tools.ocr_tool import ocr_extract_exams", src)
        self.assertIn("from tools.rag_tool import rag_lookup_exam_codes", src)
        self.assertIn("from tools.scheduling_tool import submit_appointment_request", src)
        self.assertIn("ocr_exams", src)
        self.assertIn("rag_exam_codes", src)
        self.assertIn("schedule_appointment", src)

    def test_write_and_run_smoke(self) -> None:
        out = _REPO / "examples" / "generated_agent.py"
        path = write_generated_agent(_REPO / "examples" / "agent_spec.json", out)
        proc = subprocess.run(
            [sys.executable, str(path)],
            cwd=str(_REPO),
            capture_output=True,
            text=True,
            timeout=60,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr + proc.stdout)
        self.assertIn("OK — ADK", proc.stdout)
        self.assertIn("lab_exam_scheduler_kit", proc.stdout)


if __name__ == "__main__":
    unittest.main()

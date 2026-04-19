"""
Testes de validação do input do transpilador (AI-004).

Cobre:
  - Spec válida (exemplo oficial)
  - Campos obrigatórios ausentes
  - spec_version desconhecida
  - agent.name inválido (não é identificador Python)
  - agent: instruction + instruction_key em simultâneo
  - tools: mcp_sse sem mcp_role
  - tools: id duplicado
  - tools: id inválido
  - mcp_servers: sse_url inválida (sem http)
  - scheduling_api: base_url inválida
  - scheduling_api: create_path sem '/'
  - security.pii: enabled=True mas apply_before_llm=False e apply_before_persist=False
  - JSON não é dict (é lista)
  - JSON malformado (string inválida)
"""
from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO))

from transpiler.validator import ValidationError, validate, validate_file

# ---------------------------------------------------------------------------
# Spec válida base (construída a partir do exemplo oficial)
# ---------------------------------------------------------------------------
with (_REPO / "examples" / "agent_spec.json").open(encoding="utf-8") as _f:
    _VALID: dict = json.load(_f)


def _copy(**overrides) -> dict:
    """Copia profunda da spec e aplica overrides (dict-merge de 1 nível)."""
    spec = copy.deepcopy(_VALID)
    spec.update(overrides)
    return spec


class TestValidatorHappyPath(unittest.TestCase):
    def test_valid_example(self):
        result = validate(_VALID, raise_on_error=False)
        self.assertTrue(result.ok, result.user_message())

    def test_valid_example_file(self):
        result = validate_file(_REPO / "examples" / "agent_spec.json", raise_on_error=False)
        self.assertTrue(result.ok, result.user_message())

    def test_raises_on_invalid_when_raise_on_error(self):
        bad = _copy()
        del bad["agent"]
        with self.assertRaises(ValidationError):
            validate(bad)


class TestMissingRequiredFields(unittest.TestCase):
    def _missing(self, field: str):
        spec = copy.deepcopy(_VALID)
        del spec[field]
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any(field in e for e in result.errors), result.errors)

    def test_missing_agent(self):
        self._missing("agent")

    def test_missing_mcp_servers(self):
        self._missing("mcp_servers")

    def test_missing_scheduling_api(self):
        self._missing("scheduling_api")

    def test_missing_security(self):
        self._missing("security")

    def test_missing_cli(self):
        self._missing("cli")

    def test_missing_spec_version(self):
        self._missing("spec_version")


class TestSpecVersion(unittest.TestCase):
    def test_unknown_version(self):
        spec = _copy(spec_version="9.9")
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("spec_version" in e for e in result.errors))

    def test_empty_version_schema_fails(self):
        spec = _copy(spec_version="")
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)


class TestAgentFields(unittest.TestCase):
    def _agent(self, **kwargs) -> dict:
        spec = copy.deepcopy(_VALID)
        spec["agent"].update(kwargs)
        return spec

    def test_invalid_name_with_dash(self):
        spec = self._agent(name="my-agent")
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("agent.name" in e for e in result.errors))

    def test_invalid_name_starts_digit(self):
        spec = self._agent(name="1agent")
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)

    def test_invalid_app_name(self):
        spec = self._agent(app_name="my app")
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("app_name" in e for e in result.errors))

    def test_both_instruction_and_key_error(self):
        spec = self._agent(instruction="inline", instruction_key="some_key")
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("instruction" in e for e in result.errors))

    def test_missing_profile_schema_error(self):
        spec = copy.deepcopy(_VALID)
        del spec["agent"]["profile"]
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)


class TestToolsValidation(unittest.TestCase):
    def test_mcp_sse_without_mcp_role(self):
        spec = copy.deepcopy(_VALID)
        spec["tools"] = [{"id": "ocr_tool", "kind": "mcp_sse"}]
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("mcp_role" in e for e in result.errors))

    def test_duplicate_tool_id(self):
        spec = copy.deepcopy(_VALID)
        spec["tools"] = [
            {"id": "same", "kind": "http_json"},
            {"id": "same", "kind": "http_json"},
        ]
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("duplicado" in e for e in result.errors))

    def test_invalid_tool_id(self):
        spec = copy.deepcopy(_VALID)
        spec["tools"] = [{"id": "bad-id!", "kind": "http_json"}]
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("id" in e for e in result.errors))

    def test_mcp_role_without_matching_server_errors(self):
        spec = copy.deepcopy(_VALID)
        spec["tools"] = [{"id": "extra", "kind": "mcp_sse", "mcp_role": "ocr"}]
        del spec["mcp_servers"]["ocr"]
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("ocr" in e for e in result.errors))


class TestMcpServersValidation(unittest.TestCase):
    def test_invalid_sse_url_no_http(self):
        spec = copy.deepcopy(_VALID)
        spec["mcp_servers"]["ocr"]["sse_url"] = "ftp://bad:3100/sse"
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("sse_url" in e for e in result.errors))

    def test_missing_rag_server(self):
        spec = copy.deepcopy(_VALID)
        del spec["mcp_servers"]["rag"]
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)


class TestSchedulingApiValidation(unittest.TestCase):
    def test_invalid_base_url(self):
        spec = copy.deepcopy(_VALID)
        spec["scheduling_api"]["base_url"] = "not-a-url"
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("base_url" in e for e in result.errors))

    def test_create_path_without_slash(self):
        spec = copy.deepcopy(_VALID)
        spec["scheduling_api"]["create_path"] = "api/v1/appointments"
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("create_path" in e for e in result.errors))


class TestSecurityPiiValidation(unittest.TestCase):
    def test_pii_enabled_but_both_flags_false(self):
        spec = copy.deepcopy(_VALID)
        spec["security"]["pii"]["apply_before_llm"] = False
        spec["security"]["pii"]["apply_before_persist"] = False
        result = validate(spec, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("PII" in e or "pii" in e.lower() for e in result.errors))

    def test_pii_disabled_generates_warning(self):
        spec = copy.deepcopy(_VALID)
        spec["security"]["pii"]["enabled"] = False
        result = validate(spec, raise_on_error=False)
        self.assertTrue(result.ok)
        self.assertTrue(result.warnings)


class TestFileValidation(unittest.TestCase):
    def test_file_not_found(self):
        result = validate_file("/tmp/does_not_exist_abc123.json", raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("não encontrado" in e or "inexistente" in e.lower() for e in result.errors))

    def test_malformed_json(self):
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            f.write("{invalid json")
            path = f.name
        result = validate_file(path, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("JSON" in e for e in result.errors))

    def test_json_is_list_not_dict(self):
        with tempfile.NamedTemporaryFile(suffix=".json", mode="w", delete=False) as f:
            json.dump([1, 2, 3], f)
            path = f.name
        result = validate_file(path, raise_on_error=False)
        self.assertFalse(result.ok)
        self.assertTrue(any("objecto" in e or "dict" in e.lower() for e in result.errors))


if __name__ == "__main__":
    unittest.main()

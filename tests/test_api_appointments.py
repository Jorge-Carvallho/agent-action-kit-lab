"""Testes da API FastAPI de agendamento (AI-010)."""
from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from api.main import app


class TestSchedulingApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.client = TestClient(app)

    def test_health(self) -> None:
        r = self.client.get("/health")
        self.assertEqual(r.status_code, 200)
        data = r.json()
        self.assertEqual(data.get("status"), "ok")
        self.assertIn("service", data)

    def test_openapi_docs_available(self) -> None:
        r = self.client.get("/openapi.json")
        self.assertEqual(r.status_code, 200)
        spec = r.json()
        paths = spec.get("paths", {})
        self.assertIn("/api/v1/appointments", paths)
        self.assertIn("/health", paths)

    def test_favicon_returns_empty_204(self) -> None:
        r = self.client.get("/favicon.ico")
        self.assertEqual(r.status_code, 204)
        self.assertEqual(r.content, b"")

    def test_create_appointment_success(self) -> None:
        r = self.client.post(
            "/api/v1/appointments",
            json={
                "exam_items": [
                    {"code": "LAB-F0001", "name": "Hemograma completo"},
                    {"code": "LAB-F0003", "name": "Glicemia em jejum"},
                ],
                "patient_reference": "REF-FICT-001",
                "notes": "Demonstração",
            },
        )
        self.assertEqual(r.status_code, 201)
        data = r.json()
        self.assertIn("appointment_id", data)
        self.assertEqual(data.get("status"), "confirmed")
        self.assertEqual(data.get("exam_count"), 2)
        self.assertIn("received_at", data)

    def test_create_appointment_validation_empty_exams(self) -> None:
        r = self.client.post(
            "/api/v1/appointments",
            json={"exam_items": []},
        )
        self.assertEqual(r.status_code, 422)


if __name__ == "__main__":
    unittest.main()

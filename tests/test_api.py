"""
test_api.py - Unit tests for Flask REST API endpoints.
"""

import unittest
import json
from backend.app import app


class TestAPI(unittest.TestCase):

    def setUp(self):
        self.client = app.test_client()

    def test_health_endpoint(self):
        resp = self.client.get("/api/health")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertEqual(data["status"], "healthy")

    def test_examples_endpoint(self):
        resp = self.client.get("/api/examples")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertGreaterEqual(len(data["examples"]), 10)

    def test_grammar_endpoint(self):
        resp = self.client.get("/api/grammar")
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIn("formal_definition", data["grammar"])

    def test_automata_test_endpoint(self):
        payload = {"dfa_id": "identifier", "input_string": "valid_var"}
        resp = self.client.post("/api/automata/test", json=payload)
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertTrue(data["result"]["accepted"])
        self.assertEqual(data["result"]["final_state"], "q1")

    def test_compile_endpoint_success(self):
        code = """START
LET a = 15
LET b = 30
LET sum = a + b
PRINT sum
STOP"""
        resp = self.client.post("/api/compile", json={"source_code": code})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertIsNotNone(data["ast"])
        self.assertGreater(len(data["tokens"]), 0)
        self.assertEqual(len(data["errors"]), 0)

    def test_run_endpoint_success(self):
        code = """START
LET x = 5
LET y = 6
PRINT x * y
STOP"""
        resp = self.client.post("/api/run", json={"source_code": code})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertTrue(data["success"])
        self.assertEqual(data["output"], ["30"])

    def test_run_endpoint_with_error(self):
        code = """START
LET x = 10
PRINT undeclared_var
STOP"""
        resp = self.client.post("/api/run", json={"source_code": code})
        self.assertEqual(resp.status_code, 200)
        data = resp.get_json()
        self.assertFalse(data["success"])
        self.assertEqual(data["phase_failed"], "Semantic Analysis")
        self.assertEqual(len(data["errors"]), 1)


if __name__ == "__main__":
    unittest.main()

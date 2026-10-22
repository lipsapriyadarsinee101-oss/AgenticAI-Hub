import json
import io
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from agentic_hub.adapters import langflow_run
from agentic_hub.observability import Recorder
from agentic_hub.tools import calculate, search_knowledge
from agentic_hub.workflow import quality_check, run, validate_question


class ToolsTests(unittest.TestCase):
    def test_arithmetic(self):
        self.assertEqual(calculate("(12 + 8) / 4"), "5.0")
        self.assertEqual(calculate("-3 * 2"), "-6")

    def test_reject_code_and_expensive_operators(self):
        for expression in ["__import__('os')", "2 ** 100000", "True + 1", "[1]", "1 / 0", "1e309"]:
            with self.subTest(expression=expression), self.assertRaises(ValueError):
                calculate(expression)

    def test_search_sources_and_missing_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "a.md").write_text("LangGraph orchestrates agents.", encoding="utf-8")
            (root / "ignored.txt").write_text("secret", encoding="utf-8")
            self.assertIn("[a.md]", search_knowledge("LangGraph", root))
            self.assertEqual(search_knowledge("unknownterm", root), "No matching evidence found.")

    def test_oversize_document_skipped(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "big.md").write_text("agents " * 40000, encoding="utf-8")
            self.assertEqual(search_knowledge("agents", root), "No matching evidence found.")


class WorkflowTests(unittest.TestCase):
    def test_question_validation(self):
        self.assertEqual(validate_question("  agents  "), "agents")
        for question in [" ", "x" * 4001]:
            with self.assertRaises(ValueError):
                validate_question(question)

    def test_demo_artifacts_and_unique_runs(self):
        with tempfile.TemporaryDirectory() as directory:
            first = run("AI agents tools", output=Path(directory))
            second = run("AI agents tools", output=Path(directory))
            self.assertNotEqual(first, second)
            report = (first / "report.md").read_text(encoding="utf-8")
            self.assertIn("Offline demonstration", report)
            result = json.loads((first / "result.json").read_text(encoding="utf-8"))
            self.assertEqual(result["status"], "completed")
            self.assertTrue(result["checks"]["has_local_citation"])
            events = [json.loads(line) for line in (first / "events.jsonl").read_text().splitlines()]
            self.assertEqual(events[-1]["stage"], "workflow")
            self.assertTrue(all(event["status"] == "ok" for event in events))

    def test_missing_evidence_is_explicit(self):
        with tempfile.TemporaryDirectory() as directory:
            folder = run("zzzzunknown", output=Path(directory))
            result = json.loads((folder / "result.json").read_text())
            self.assertIn("No matching evidence", result["state"]["report"])
            self.assertFalse(result["checks"]["has_local_citation"])

    def test_failure_recorded_and_propagated(self):
        with tempfile.TemporaryDirectory() as directory:
            with patch("agentic_hub.adapters.crew_review", side_effect=RuntimeError("test failure")):
                with self.assertRaises(RuntimeError):
                    run("agents", mode="crew", output=Path(directory))
            folder = next(Path(directory).iterdir())
            self.assertEqual(json.loads((folder / "failure.json").read_text())["error_type"], "RuntimeError")
            events = [json.loads(line) for line in (folder / "events.jsonl").read_text().splitlines()]
            self.assertEqual(events[-1]["status"], "error")
            self.assertFalse((folder / "report.md").exists())

    def test_unknown_citations_flagged(self):
        with tempfile.TemporaryDirectory() as directory:
            result = quality_check("A claim [invented.md]", Path(directory))
            self.assertFalse(result["has_local_citation"])
            self.assertEqual(result["unknown_citations"], ["invented.md"])

    def test_invalid_modes(self):
        for mode, flow in [("invalid", False), ("demo", True)]:
            with self.assertRaises(ValueError):
                run("agents", mode=mode, with_langflow=flow)

    def test_metadata_logs_exclude_content(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "events.jsonl"
            recorder = Recorder(path)
            with recorder.stage("research"):
                pass
            self.assertEqual(set(json.loads(path.read_text())), {"time", "stage", "status", "elapsed_seconds"})


class LangflowTests(unittest.TestCase):
    def test_requires_flow_id(self):
        with patch.dict(os.environ, {"LANGFLOW_FLOW_ID": ""}):
            with self.assertRaises(ValueError):
                langflow_run("hello")

    def test_http_request_contract(self):
        captured = {}

        def transport(request, timeout):
            captured["url"] = request.full_url
            captured["key"] = request.get_header("X-api-key")
            captured["body"] = json.loads(request.data)
            captured["timeout"] = timeout
            return io.BytesIO(b'{"outputs": [{"text": "test response"}]}')

        with patch("agentic_hub.adapters.urlopen", side_effect=transport):
            with patch.dict(os.environ, {
                "LANGFLOW_URL": "http://localhost:7860",
                "LANGFLOW_FLOW_ID": "flow-test",
                "LANGFLOW_API_KEY": "test-key",
            }):
                result = json.loads(langflow_run("hello"))
            self.assertEqual(captured["url"], "http://localhost:7860/api/v1/run/flow-test")
            self.assertEqual(captured["key"], "test-key")
            self.assertEqual(captured["body"]["input_value"], "hello")
            self.assertEqual(result["outputs"][0]["text"], "test response")
            self.assertEqual(captured["timeout"], 120)


if __name__ == "__main__":
    unittest.main()


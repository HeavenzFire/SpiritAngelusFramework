import copy
import importlib.util
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("validate_handoff", ROOT / "tools" / "validate_handoff.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)

VALID = {
    "schema_version": "1.0.0",
    "project_id": "heavenzfire-unified-field",
    "source_platform": "ChatGPT",
    "conversation_reference": "https://example.com/shared/conversation",
    "objective": "Test portable AI context exchange.",
    "decisions": ["Use a versioned JSON envelope."],
    "task_status": "in_progress",
    "artifacts": [{"name": "design", "reference": "docs/design.md", "sha256": "a" * 64}],
    "test_results": [{"name": "validator", "status": "passed", "evidence": "Unit tests"}],
    "next_actions": ["Implement provider-specific adapters."],
    "permissions": {"sharing": "private", "external_fetch": False, "execution": "none"},
    "timestamp": "2026-10-21T20:00:00-05:00",
}

class HandoffValidationTests(unittest.TestCase):
    def test_valid_envelope(self):
        self.assertEqual(module.validate(VALID), [])

    def test_missing_required_field(self):
        data = copy.deepcopy(VALID)
        del data["objective"]
        self.assertTrue(any("objective" in e for e in module.validate(data)))

    def test_rejects_unknown_top_level_field(self):
        data = copy.deepcopy(VALID)
        data["secret_token"] = "should-not-be-here"
        self.assertTrue(any("unknown top-level" in e for e in module.validate(data)))

    def test_rejects_bad_hash(self):
        data = copy.deepcopy(VALID)
        data["artifacts"][0]["sha256"] = "not-a-hash"
        self.assertTrue(any("sha256" in e for e in module.validate(data)))

    def test_rejects_timezone_free_timestamp(self):
        data = copy.deepcopy(VALID)
        data["timestamp"] = "2026-10-21T20:00:00"
        self.assertTrue(any("timezone" in e for e in module.validate(data)))

    def test_rejects_privilege_like_execution_mode(self):
        data = copy.deepcopy(VALID)
        data["permissions"]["execution"] = "unrestricted"
        self.assertTrue(any("execution" in e for e in module.validate(data)))

    def test_rejects_bad_test_status(self):
        data = copy.deepcopy(VALID)
        data["test_results"][0]["status"] = "probably"
        self.assertTrue(any("test_results[0]" in e for e in module.validate(data)))

    def test_non_object_root(self):
        self.assertTrue(module.validate(["not", "an", "object"]))

if __name__ == "__main__":
    unittest.main()

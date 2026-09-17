import tempfile
import unittest
from pathlib import Path

from openai_migration_check import scan


class MigrationCheckTests(unittest.TestCase):
    def test_detects_advanced_paths_without_uploading(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "app.py").write_text(
                "client.responses.create(input=[{'type':'input_image'}], "
                "tools=[{'type':'function'}], response_format={'type':'json_schema'}, stream=True, "
                "base_url='https://gateway.example/v1')",
                encoding="utf-8",
            )
            report = scan(root)
            self.assertFalse(report["source_uploaded"])
            self.assertEqual(report["files_scanned"], 1)
            self.assertTrue(all(report["risk_paths"][name] for name in report["risk_paths"]))
            self.assertEqual(report["possible_hardcoded_keys"], [])

    def test_reports_location_without_echoing_possible_key(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            fake_key = "sk-" + "1234567890abcdefghijklmnop"
            (root / "bad.py").write_text(f"token = '{fake_key}'\n", encoding="utf-8")
            report = scan(root)
            self.assertEqual(report["possible_hardcoded_keys"], [{"file": "bad.py", "line": 1}])
            self.assertNotIn("1234567890abcdefghijklmnop", str(report))

    def test_ignores_dependency_directories(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "node_modules").mkdir()
            (root / "node_modules" / "vendor.js").write_text("stream: true", encoding="utf-8")
            report = scan(root)
            self.assertEqual(report["files_scanned"], 0)


if __name__ == "__main__":
    unittest.main()

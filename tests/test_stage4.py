import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import progress  # noqa: E402
import check_format  # noqa: E402


class Stage4Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = progress.generate()

    def test_progress_json_is_canonical_and_current(self):
        stored = json.loads((ROOT / "progress.json").read_text(encoding="utf-8"))
        self.assertEqual(self.report, stored)
        self.assertEqual(1, stored["functions"]["matched"])
        self.assertEqual(36, stored["code"]["matched_bytes"])
        self.assertEqual(596152, stored["assembly"]["function_bytes_remaining"])

    def test_metrics_are_separate_and_accounted(self):
        report = self.report
        self.assertEqual(
            report["code"]["total_function_bytes"],
            report["code"]["matched_bytes"]
            + report["assembly"]["function_bytes_remaining"],
        )
        self.assertEqual(22852, report["data"]["matched_bytes"])
        self.assertEqual(1855, report["symbols"]["total"])
        self.assertIn("championship_grid", report["subsystems"])
        self.assertIn("unclassified", report["subsystems"])

    def test_progress_baseline_detects_regression(self):
        with tempfile.TemporaryDirectory() as directory:
            baseline = Path(directory) / "baseline.json"
            baseline.write_text(
                json.dumps(
                    {
                        "minimum": {
                            "code_matched_bytes": 37,
                            "functions_matched": 1,
                            "data_matched_bytes": 22852,
                            "symbols_total": 1855,
                        },
                        "maximum": {"asm_function_bytes_remaining": 596152},
                    }
                ),
                encoding="utf-8",
            )
            with self.assertRaisesRegex(ValueError, "code_matched_bytes regressed"):
                progress.check_baseline(self.report, baseline)

    def test_public_ci_checks_are_executable(self):
        for script in ("lint_config.py", "check_format.py"):
            result = subprocess.run(
                [sys.executable, str(ROOT / "scripts" / script)],
                cwd=ROOT,
                text=True,
                capture_output=True,
            )
            self.assertEqual(0, result.returncode, result.stdout + result.stderr)

    def test_format_scope_excludes_downloaded_tool_sources(self):
        vendor_header = ROOT / "tools" / "psyq_sdk" / "include" / "stdio.h"
        project_source = ROOT / "tools" / "compiler_probe" / "probe.py"
        self.assertTrue(check_format.is_excluded(vendor_header))
        self.assertFalse(check_format.is_excluded(project_source))

if __name__ == "__main__":
    unittest.main()

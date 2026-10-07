import csv
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import function_tool  # noqa: E402


class Stage3Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        if os.environ.get("RUMBLE_PUBLIC_CI"):
            raise unittest.SkipTest("proprietary reference is intentionally absent from public CI")
        cls.exe = function_tool.Executable.read()
        cls.functions = function_tool.read_functions(cls.exe)

    def test_backlog_schema_and_coverage(self):
        with (ROOT / "config/function_backlog.csv").open(newline="", encoding="utf-8") as stream:
            reader = csv.DictReader(stream)
            rows = list(reader)
        self.assertEqual(function_tool.BACKLOG_FIELDS, reader.fieldnames)
        self.assertEqual(1855, len(rows))
        self.assertEqual(1855, len({row["name"] for row in rows}))

    def test_call_graph_for_pilot(self):
        callers, callees = function_tool.call_graph(self.exe, self.functions)
        self.assertEqual(["FUN_800524b4", "FUN_80056c6c"], callers["FUN_80078c24"])
        self.assertEqual(["FUN_800352f8"], callees["FUN_80078c24"])

    def test_first_c_match_is_registered(self):
        objects = json.loads((ROOT / "config/decomp_objects.json").read_text())["objects"]
        pilot = objects["game/FUN_80078c24"]
        self.assertEqual("matched", pilot["status"])
        self.assertEqual(36, pilot["size"])
        self.assertTrue((ROOT / pilot["source"]).is_file())
        config = (ROOT / "config/splat.yaml").read_text()
        self.assertIn("[0x69424, c, game/FUN_80078c24]", config)

    def test_context_does_not_require_local_ghidra_export(self):
        pilot = function_tool.resolve_function("FUN_80078c24", self.functions)
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(
            function_tool, "DECOMP_PATH", Path(temporary) / "missing.c"
        ):
            text = function_tool.extract_decompilation(pilot)
        self.assertIn("No local Ghidra export", text)

    def test_progress_has_leaf_candidates_in_target_range(self):
        rows = function_tool.build_backlog(self.exe, self.functions)
        candidates = [
            row
            for row in rows
            if row["status"] == "asm"
            and 20 <= int(row["instructions"]) <= 150
            and not row["callees"]
        ]
        self.assertTrue(candidates)
        self.assertTrue(all(20 <= int(row["instructions"]) <= 150 for row in candidates))


if __name__ == "__main__":
    unittest.main()

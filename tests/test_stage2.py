import csv
import hashlib
import json
import os
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class Stage2Tests(unittest.TestCase):
    def test_all_executable_ghidra_functions_are_imported(self):
        with (ROOT / "ghidra_out/functions.csv").open(newline="", encoding="utf-8") as source:
            expected = {
                row["name"]
                for row in csv.DictReader(source)
                if 0x80010000 <= int(row["address"], 16) < 0x800AF800
            }
        pattern = re.compile(r"^([A-Za-z_][A-Za-z0-9_]*) = 0x[0-9A-F]{8}; // type:func")
        actual = {
            match.group(1)
            for line in (ROOT / "config/symbol_addrs.txt").read_text().splitlines()
            if (match := pattern.match(line))
        }
        self.assertEqual(expected, actual)
        self.assertEqual(1855, len(actual))

    def test_split_records_observed_runtime_boundaries(self):
        config = (ROOT / "config/splat.yaml").read_text()
        self.assertIn("gp_value: 0x800AF0E4", config)
        self.assertIn("[0x9A3F4, rodata", config)
        self.assertIn("[0x9F8E4, sdata", config)
        self.assertIn("[0x9FD20, data", config)
        self.assertIn("start: 0x9FD38, type: bss, vram: 0x800AF538", config)
        self.assertIn("bss_size: 0xD9B0", config)

    def test_rebuild_matches_when_present(self):
        if os.environ.get("RUMBLE_PUBLIC_CI"):
            self.skipTest("byte-identical rebuild runs only in matching CI")
        reference = ROOT / "extracted/SLUS_010.68"
        rebuild = ROOT / "build/SLUS_010.68"
        if not rebuild.exists():
            self.skipTest("run make extract && make build for the byte-match integration test")
        self.assertEqual(reference.read_bytes(), rebuild.read_bytes())
        self.assertEqual(
            "e90e3c7e4cf286a7a0a5e827b3a404bfe8407b15f8b2fd54536d426682b20f75",
            hashlib.sha256(rebuild.read_bytes()).hexdigest(),
        )

    def test_gp_usage_inventory_is_conservative_and_complete(self):
        inventory = json.loads((ROOT / "config/gp_usage.json").read_text())
        classification = inventory["classification"]
        self.assertEqual(1855, classification["total_functions"])
        self.assertEqual(
            1855,
            classification["uses_gp_relative"] + classification["unclassified"],
        )
        self.assertEqual(classification["uses_gp_relative"], len(inventory["functions"]))
        self.assertIn("remain unclassified", inventory["policy"])


if __name__ == "__main__":
    unittest.main()

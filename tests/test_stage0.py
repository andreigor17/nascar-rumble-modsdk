import hashlib
import json
import os
import tempfile
import unittest
from pathlib import Path

from scripts.verify_grid_capture import decode_grid, verify as verify_grid
from scripts.verify_reference import file_hashes, parse_psx_exe, verify as verify_reference


REPO = Path(__file__).resolve().parents[1]


class ReferenceTests(unittest.TestCase):
    def test_file_hashes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "sample.bin"
            path.write_bytes(b"nascar-rumble")
            sha1, sha256 = file_hashes(path, chunk_size=3)
        self.assertEqual(sha1, hashlib.sha1(b"nascar-rumble").hexdigest())
        self.assertEqual(sha256, hashlib.sha256(b"nascar-rumble").hexdigest())

    def test_parse_psx_exe_rejects_invalid_header(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "bad.exe"
            path.write_bytes(bytes(0x800))
            with self.assertRaisesRegex(ValueError, "PS-X EXE"):
                parse_psx_exe(path)

    def test_checked_in_reference(self):
        if os.environ.get("RUMBLE_PUBLIC_CI"):
            self.skipTest("proprietary reference is intentionally absent from public CI")
        errors = verify_reference(REPO, REPO / "config" / "reference_hashes.json")
        self.assertEqual(errors, [])


class GridCaptureTests(unittest.TestCase):
    def test_rejects_truncated_capture(self):
        with self.assertRaisesRegex(ValueError, "truncada"):
            decode_grid(b"\x02" + bytes(7), 2)

    def test_checked_in_capture(self):
        self.assertEqual(verify_grid(), [])

    def test_capture_is_json_without_binary_assets(self):
        capture = json.loads(
            (REPO / "experiments" / "grid" / "championship_gold_rush.json").read_text()
        )
        self.assertEqual(capture["schema_version"], 1)
        self.assertEqual(capture["grid_address"], "0x800b0e40")


class CompilerCorpusTests(unittest.TestCase):
    def test_corpus_has_required_breadth(self):
        corpus = json.loads((REPO / "config" / "compiler_corpus.json").read_text())
        functions = corpus["functions"]
        self.assertGreaterEqual(len(functions), 15)
        self.assertLessEqual(len(functions), 30)
        self.assertGreaterEqual(sum(item["status"] == "matched" for item in functions), 5)
        self.assertEqual(len({item["address"] for item in functions}), len(functions))

    def test_candidate_tools_have_checksums(self):
        candidates = json.loads((REPO / "config" / "psyq_candidates.json").read_text())
        self.assertRegex(candidates["runner"]["sha256"], r"^[0-9a-f]{64}$")
        for candidate in candidates["candidates"]:
            self.assertRegex(candidate["cc1psx_sha256"], r"^[0-9a-f]{64}$")
            self.assertRegex(candidate["aspsx_sha256"], r"^[0-9a-f]{64}$")

    def test_locked_toolchain_records_completed_gate(self):
        lock = json.loads((REPO / "config" / "toolchain.lock.json").read_text())
        self.assertEqual(lock["status"], "validated-baseline")
        self.assertEqual(lock["compiler"]["identity"], "GNU C 2.7.2.SN32.3.7 Build 0001")
        self.assertEqual(lock["compiler"]["validated_flags"], ["-O2", "-G0", "-g0"])
        self.assertRegex(lock["linker"]["deterministic_probe_cpe_sha256"], r"^[0-9a-f]{64}$")


if __name__ == "__main__":
    unittest.main()

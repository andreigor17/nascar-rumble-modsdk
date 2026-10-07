import json
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import augment_recompone_funcmap  # noqa: E402


class NativeBuildTests(unittest.TestCase):
    def test_auxiliary_dispatch_targets_are_generated_deterministically(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            map_path = root / "funcmap.json"
            generated = root / "main.cs"
            map_path.write_text(
                json.dumps(
                    {
                        "functions": [
                            {"address": "80001000", "name": "owner", "size": 32},
                            {"address": "80001040", "name": "next", "size": 16},
                        ],
                        "labels": [],
                    }
                ),
                encoding="utf-8",
            )
            generated.write_text(
                "Dispatcher.Call(c, m, 0x80001010u);\n"
                "Dispatcher.Call(c, m, 0x80001030u);\n",
                encoding="utf-8",
            )
            additions = augment_recompone_funcmap.augment(map_path, generated)
            self.assertEqual([16, 16], [entry["size"] for entry in additions])
            self.assertEqual([], augment_recompone_funcmap.augment(map_path, generated))

    def test_native_toolchain_is_pinned_and_patch_is_versioned(self):
        lock = json.loads(
            (ROOT / "config" / "recompone.lock.json").read_text(encoding="utf-8")
        )
        self.assertEqual(40, len(lock["commit"]))
        patch = ROOT / lock["local_patch"]
        self.assertTrue(patch.is_file())
        text = patch.read_text(encoding="utf-8")
        self.assertIn("new APIVersion(4, 1)", text)
        self.assertIn("WaitForValidDisc(cuePath)", text)
        self.assertIn("RUMBLE_ENABLE_MODS", text)

    def test_native_host_handles_managed_failures(self):
        host = (ROOT / "recompone" / "host" / "Program.cs").read_text(
            encoding="utf-8"
        )
        self.assertIn("catch (Exception error)", host)
        self.assertIn("Environment.ExitCode = 1", host)
        self.assertIn("Runtime.Shutdown()", host)


if __name__ == "__main__":
    unittest.main()

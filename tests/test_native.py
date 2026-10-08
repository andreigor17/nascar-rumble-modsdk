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
        self.assertIn("HostWindow.UseDiscPath(cuePath)", text)
        self.assertIn("RUMBLE_ENABLE_MODS", text)
        self.assertIn("bool _deferredIrq", text)
        self.assertIn("psMemory.TickDma()", text)

    def test_native_host_handles_managed_failures(self):
        host = (ROOT / "recompone" / "host" / "Program.cs").read_text(
            encoding="utf-8"
        )
        self.assertIn("catch (Exception error)", host)
        self.assertIn("Environment.ExitCode = 1", host)
        self.assertIn("Runtime.Shutdown()", host)

    def test_cd_callbacks_are_mapped_for_the_native_runtime(self):
        function_map = json.loads(
            (ROOT / "recompone" / "nascar_funcmap.json").read_text(encoding="utf-8")
        )
        functions = {
            entry["address"]: entry["name"] for entry in function_map["functions"]
        }
        self.assertEqual("cd_read_sync_callback", functions["8001af58"])
        self.assertEqual("cd_read_ready_callback", functions["8001b14c"])
        self.assertEqual("cd_file_completion_callback", functions["8001c934"])
        self.assertEqual("mdec_output_callback", functions["80094dd0"])
        self.assertEqual("memory_card_event_callback_4", functions["8001e864"])
        self.assertEqual("memory_card_event_callback_8", functions["8001edd0"])
        self.assertEqual("vblank_tick_callback", functions["8001dcd4"])
        self.assertEqual("vblank_audio_callback", functions["80022308"])
        self.assertEqual("intro_cd_sync_callback", functions["800983a0"])
        self.assertEqual("intro_cd_ready_callback", functions["80098048"])
        self.assertEqual("intro_spu_dma_callback", functions["8009638c"])
        self.assertEqual("intro_vblank_callback", functions["800967b0"])
        self.assertEqual("CdSyncCallback", functions["8009f900"])
        self.assertEqual("CdReadyCallback", functions["8009f920"])

    def test_memory_card_poll_yields_to_the_native_scheduler(self):
        config = json.loads((ROOT / "recompone" / "nascar.json").read_text(encoding="utf-8"))
        patches = {
            (entry["function"], entry["mode"]): entry["target"]
            for entry in config["patches"]
        }
        self.assertEqual(
            "NascarRumble.Host.NativeHooks.MemoryCardPoll",
            patches[("FUN_8001f560", "post")],
        )
        self.assertEqual(
            "RecompOne.Runtime.Sdk.LibCd.CdSync",
            patches[("CD_sync", "replace")],
        )
        self.assertEqual(
            "NascarRumble.Host.NativeHooks.CdReady",
            patches[("CD_ready", "replace")],
        )
        self.assertEqual(
            "NascarRumble.Host.NativeHooks.IntroAudioPoll",
            patches[("FUN_80096e90", "pre")],
        )
        hook = (ROOT / "recompone" / "host" / "NativeHooks.cs").read_text(
            encoding="utf-8"
        )
        self.assertIn("Runtime.PresentFrame()", hook)
        self.assertIn("Runtime.PumpCd()", hook)


if __name__ == "__main__":
    unittest.main()

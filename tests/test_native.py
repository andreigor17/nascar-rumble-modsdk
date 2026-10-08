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
        self.assertIn("channel == 2 || _raisingIrq", text)
        self.assertIn("int _irqPending", text)
        self.assertIn("public bool ConsumeIrq()", text)
        self.assertIn("public void TickSpuIrq()", text)
        self.assertIn("psMemory.TickDma()", text)
        self.assertIn("public static void PumpSpu()", text)

    def test_gte_outer_product_latches_ir_operands(self):
        # OP (cop2 0x0C) must use the IR values from before the command. Without this the
        # terrain height interpolation (FUN_80064998) returns garbage and cars float/fly.
        text = (ROOT / "recompone" / "patches" / "recompone-macos.patch").read_text(
            encoding="utf-8"
        )
        self.assertIn("long ir1 = IR1, ir2 = IR2, ir3 = IR3;", text)
        self.assertIn("(long)RT[8] * ir1 - (long)RT[0] * ir3", text)

    def test_vertex_upload_does_not_stall_the_macos_driver(self):
        # Updating the VBO in place forced a GL-on-Metal flush per batch (~60% of a race frame).
        text = (ROOT / "recompone" / "patches" / "recompone-macos.patch").read_text(
            encoding="utf-8"
        )
        self.assertIn("-        _gl.BufferSubData<GlVertex>(BufferTargetARB.ArrayBuffer, 0", text)
        self.assertIn("BufferUsageARB.StreamDraw);", text)

    def test_race_exit_and_frame_pacing(self):
        hooks = (ROOT / "recompone" / "host" / "NativeHooks.cs").read_text(encoding="utf-8")
        # Quit/restart/finish leave FUN_800299a8 spinning on the swap flag; it needs VBlanks.
        self.assertIn("FinishRaceTiming(m);", hooks)
        self.assertIn("SwapPendingFlag = 0x800AF720u", hooks)
        # Console cadence (30 fps) is the default; 60 fps changes the launch and is opt-in.
        self.assertIn('GetEnvironmentVariable("RUMBLE_RACE_FPS")', hooks)
        self.assertIn("? 1000.0 / fps : 1000.0 / 30.0;", hooks)

    def test_shadow_checker_is_opt_in(self):
        hooks = json.loads((ROOT / "recompone" / "nascar.json").read_text(encoding="utf-8"))
        targets = {patch["target"] for patch in hooks["patches"]}
        self.assertIn("NascarRumble.Host.NativeHooks.ShadowPre80064acc", targets)
        shadow = (ROOT / "recompone" / "host" / "ShadowCpu.cs").read_text(encoding="utf-8")
        self.assertIn('GetEnvironmentVariable("RUMBLE_SHADOW") == "1"', shadow)

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
        self.assertEqual("audio_bank_read_callback", functions["800224f4"])
        self.assertEqual("spu_stream_transfer_callback", functions["80020160"])
        self.assertEqual("spu_upload_completion_callback", functions["80020658"])
        self.assertEqual("spu_irq_callback", functions["80021f9c"])
        self.assertEqual("spu_stream_buffer_callback", functions["800221f8"])
        self.assertEqual("audio_upload_completion_callback", functions["80022e40"])
        self.assertEqual("audio_stream_status_callback", functions["80023b34"])
        self.assertEqual("intro_cd_sync_callback", functions["800983a0"])
        self.assertEqual("intro_cd_ready_callback", functions["80098048"])
        self.assertEqual("intro_spu_dma_callback", functions["8009638c"])
        self.assertEqual("intro_vblank_callback", functions["800967b0"])
        self.assertEqual("frontend_track_read_callback", functions["80029f7c"])
        object_callbacks = {
            "80030f84": "object_type_17_callback",
            "8003203c": "object_type_22_callback",
            "80033274": "object_type_8_callback",
            "80033468": "object_type_13_callback",
            "80034198": "object_type_6_callback",
            "800343dc": "object_type_11_callback",
            "80034894": "object_type_14_callback",
            "80034e6c": "object_type_5_callback",
            "80060190": "object_type_1_callback",
        }
        for address, name in object_callbacks.items():
            self.assertEqual(name, functions[address])
        entity_callbacks = {
            "8003be84": "frontend_entity_callback_3be84",
            "800481bc": "entity_callback_481bc",
            "8006a214": "entity_callback_6a214",
            "8006e074": "entity_callback_6e074",
            "8006fa04": "entity_callback_6fa04",
            "80074fd0": "entity_callback_74fd0",
        }
        for address, name in entity_callbacks.items():
            self.assertEqual(name, functions[address])
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
            "NascarRumble.Host.NativeHooks.FrameSubmitted",
            patches[("FUN_8001a24c", "post")],
        )
        self.assertEqual(
            "NascarRumble.Host.NativeHooks.FrontendFrameWait",
            patches[("FUN_800285e4", "pre")],
        )
        self.assertEqual(
            "NascarRumble.Host.NativeHooks.FrontendUpdateEnter",
            patches[("FUN_8007a994", "pre")],
        )
        self.assertEqual(
            "NascarRumble.Host.NativeHooks.FrontendUpdateExit",
            patches[("FUN_8007a994", "post")],
        )
        self.assertEqual(
            "NascarRumble.Host.NativeHooks.IntroAudioPoll",
            patches[("FUN_80096e90", "pre")],
        )
        hook = (ROOT / "recompone" / "host" / "NativeHooks.cs").read_text(
            encoding="utf-8"
        )
        self.assertIn("Runtime.PresentFrame()", hook)
        self.assertIn("Runtime.PumpSpu()", hook)
        self.assertIn("currentTick - consumedTick", hook)


if __name__ == "__main__":
    unittest.main()

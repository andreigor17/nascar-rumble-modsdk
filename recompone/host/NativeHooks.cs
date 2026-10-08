using RecompOne.Runtime.Context;
using RecompOne.Runtime.Memory;

namespace NascarRumble.Host;

/// <summary>
/// Cooperative scheduling points needed by the statically recompiled game.
/// </summary>
public static class NativeHooks
{
    [ThreadStatic]
    private static (uint S0, uint S1, uint S2, uint SP) _frontendUpdateContext;

    [ThreadStatic]
    private static uint _raceTimingTraceCounter;

    [ThreadStatic]
    private static bool _raceTimingActive;

    [ThreadStatic]
    private static uint _vehicleTraceCounter;

    /// <summary>
    /// The original hardware keeps delivering VBlank and memory-card events while the game
    /// polls the asynchronous card status. The recompiled call graph runs on one host thread,
    /// so yield to the runtime after each status read. Runtime callbacks preserve the emulated
    /// CPU context, including the status value left in V0 by the original function.
    /// </summary>
    public static void MemoryCardPoll(CpuContext c, IMemory m)
    {
        RecompOne.Runtime.Runtime.PresentFrame();
    }

    /// <summary>
    /// Low-level CD_ready reports whether a fresh controller interrupt is pending. RecompOne's
    /// public CdReady implementation exposes the last completed high-level command instead,
    /// which makes the game's pre-command idle loop wait forever.
    /// </summary>
    public static void CdReady(CpuContext c, IMemory m)
    {
        c.V0 = 0;
    }

    /// <summary>
    /// GPU DMA and VBlank are asynchronous on the console. A race frame can submit many draw
    /// lists, so only advance the runtime when the game has consumed the preceding VBlank.
    /// Advancing once per submission makes the simulation delta hit its safety cap and causes
    /// vehicles to be launched by collision/physics impulses.
    /// </summary>
    public static void FrameSubmitted(CpuContext c, IMemory m)
    {
        if (!_raceTimingActive)
        {
            RecompOne.Runtime.Runtime.PresentFrame();
            return;
        }

        uint currentTick = m.ReadU32(c.GP + 0x654u);
        uint consumedTick = m.ReadU32(c.GP + 0x634u);
        if (unchecked((int)(currentTick - consumedTick)) < 1)
        {
            RecompOne.Runtime.Runtime.PresentFrame();
            DeliverElapsedVBlanks();
        }
    }

    private const double VBlankMs = 1000.0 / 60.0;

    [ThreadStatic]
    private static System.Diagnostics.Stopwatch? _raceClock;

    [ThreadStatic]
    private static double _raceVBlankDebtMs;

    /// <summary>
    /// On the console VBlank fires every 1/60 s regardless of how long a race frame takes, so a
    /// frame that spans two VBlanks advances the race clock by 10 instead of 5. PresentFrame
    /// delivers one VBlank; deliver the ones that elapsed in wall time beyond it, capped at the
    /// game's own delta limit (25 = five VBlanks), so slow host frames do not slow the race down.
    /// </summary>
    private static void DeliverElapsedVBlanks()
    {
        _raceClock ??= System.Diagnostics.Stopwatch.StartNew();
        _raceVBlankDebtMs += _raceClock.Elapsed.TotalMilliseconds;
        _raceClock.Restart();
        int due = (int)(_raceVBlankDebtMs / VBlankMs);
        _raceVBlankDebtMs -= due * VBlankMs;
        for (int extra = Math.Min(due, 5) - 1; extra > 0; extra--)
            RecompOne.Runtime.Runtime.DispatchIrq(0);
        if (due > 5) _raceVBlankDebtMs = 0;
    }

    /// <summary>
    /// The frontend resets its timing counters and waits for the first VBlank before it can
    /// submit a frame. Give that bootstrap wait one cooperative runtime tick; subsequent frame
    /// submissions keep the normal VBlank cadence moving through FrameSubmitted.
    /// </summary>
    public static void FrontendFrameWait(CpuContext c, IMemory m)
    {
        _raceTimingActive = false;
        uint currentTick = m.ReadU32(c.GP + 0x654u);
        uint consumedTick = m.ReadU32(c.GP + 0x634u);
        if (unchecked((int)(currentTick - consumedTick)) < 1)
        {
            RecompOne.Runtime.Runtime.PresentFrame();
        }
    }

    /// <summary>
    /// FUN_8007a994 is a large frontend dispatcher. One of its indirectly reached paths
    /// overwrites the caller's saved S0 slot in the recompiled stack, even though S0-S2 and SP
    /// are callee-saved in the original MIPS ABI. Preserve that boundary explicitly.
    /// </summary>
    public static void FrontendUpdateEnter(CpuContext c, IMemory m)
    {
        _frontendUpdateContext = (c.S0, c.S1, c.S2, c.SP);
    }

    public static void FrontendUpdateExit(CpuContext c, IMemory m)
    {
        (c.S0, c.S1, c.S2, c.SP) = _frontendUpdateContext;
    }

    /// <summary>
    /// Marks the transition from frontend/loading cadence to the race timing loop. Ensure the
    /// loop has one pending VBlank before it enters its original busy wait.
    /// </summary>
    public static void RaceTimingEnter(CpuContext c, IMemory m)
    {
        if (!_raceTimingActive)
        {
            _raceClock = System.Diagnostics.Stopwatch.StartNew();
            _raceVBlankDebtMs = 0;
        }
        _raceTimingActive = true;
        uint currentTick = m.ReadU32(c.GP + 0x654u);
        uint consumedTick = m.ReadU32(c.GP + 0x634u);
        if (unchecked((int)(currentTick - consumedTick)) < 1)
        {
            RecompOne.Runtime.Runtime.PresentFrame();
        }
    }

    /// <summary>
    /// Periodic timing diagnostics for the race loop. This is inert unless tracing is enabled
    /// and helps distinguish a stalled countdown from a simulation/physics defect.
    /// </summary>
    public static void RaceTimingTrace(CpuContext c, IMemory m)
    {
        string? trace = Environment.GetEnvironmentVariable("RUMBLE_NATIVE_TRACE");
        if (trace != "1" && trace != "2") return;
        uint traceFrame = ++_raceTimingTraceCounter;
        if (trace == "1" && traceFrame > 10u && traceFrame % 60u != 0u) return;

        Console.Error.WriteLine(
            $"[host] race timing: frame={traceFrame} raw={m.ReadU32(c.GP + 0x654u)} "
            + $"consumed={m.ReadU32(c.GP + 0x634u)} "
            + $"snapshot={m.ReadU32(c.GP + 0x664u)} "
            + $"delta={m.ReadU32(c.GP + 0x5FCu)} "
            + $"state={m.ReadU32(c.GP + 0x600u)} "
            + $"localPlayers={m.ReadU32(c.GP + 0x604u)} "
            + $"vehicles={m.ReadU32(c.GP + 0x6E8u)}");
    }

    [ThreadStatic]
    private static bool _ramDumped;

    /// <summary>Writes main RAM once, during the first race frame, to RUMBLE_RAM_DUMP.</summary>
    private static void DumpRamOnce(IMemory m)
    {
        string? path = Environment.GetEnvironmentVariable("RUMBLE_RAM_DUMP");
        if (_ramDumped || string.IsNullOrEmpty(path) || m is not PSMemory psm) return;
        _ramDumped = true;
        File.WriteAllBytes(path, psm.Ram[..0x200000].ToArray());
        Console.Error.WriteLine($"[host] RAM dumped to {path}");
    }

    /// <summary>Trace the first vehicle immediately after the main vehicle simulation pass.</summary>
    public static void VehicleStateTrace(CpuContext c, IMemory m)
    {
        ShadowCpu.Post(0x80056C6Cu, c, m);
        DumpRamOnce(m);
        if (Environment.GetEnvironmentVariable("RUMBLE_NATIVE_TRACE") != "1") return;
        uint traceFrame = ++_vehicleTraceCounter;
        if (traceFrame > 20u && traceFrame % 60u != 0u) return;

        uint vehicleCount = m.ReadU32(c.GP + 0x6E8u);
        uint vehicle = m.ReadU32(0x800B12C0u);
        if (vehicleCount == 0u || vehicle < 0x80010000u || vehicle >= 0x80200000u) return;
        uint entity = m.ReadU32(vehicle);
        if (entity < 0x80010000u || entity >= 0x80200000u) return;

        static int I32(IMemory memory, uint address) => unchecked((int)memory.ReadU32(address));
        if (traceFrame <= 5u)
        {
            var positions = new List<string>();
            for (uint index = 0; index < vehicleCount; index++)
            {
                uint item = m.ReadU32(0x800B12C0u + index * 4u);
                if (item < 0x80010000u || item >= 0x80200000u) continue;
                uint itemEntity = m.ReadU32(item);
                if (itemEntity < 0x80010000u || itemEntity >= 0x80200000u) continue;
                positions.Add(
                    $"{index}=({I32(m, itemEntity + 0x58u)},{I32(m, itemEntity + 0x5Cu)},"
                    + $"{I32(m, itemEntity + 0x60u)})");
            }
            Console.Error.WriteLine($"[host] vehicle grid: frame={traceFrame} {string.Join(' ', positions)}");
        }

        Console.Error.WriteLine(
            $"[host] vehicle: frame={traceFrame} count={vehicleCount} "
            + $"pos=({I32(m, entity + 0x58u)},{I32(m, entity + 0x5Cu)},{I32(m, entity + 0x60u)}) "
            + $"entityV=({I32(m, entity + 0x148u)},{I32(m, entity + 0x14Cu)},{I32(m, entity + 0x150u)}) "
            + $"vehicleV=({I32(m, vehicle + 0x154u)},{I32(m, vehicle + 0x158u)},{I32(m, vehicle + 0x15Cu)})");
    }

    [ThreadStatic]
    private static Stack<(uint HintPtr, uint Hint, int X, int Y, int Z, uint Mode)>? _groundQueries;

    [ThreadStatic]
    private static uint _groundTraceCounter;

    // Differential checks of recompiled terrain/physics code against the original MIPS code.
    public static void ShadowPre80064acc(CpuContext c, IMemory m) => ShadowCpu.Pre(0x80064ACCu, c, m);
    public static void ShadowPost80064acc(CpuContext c, IMemory m) => ShadowCpu.Post(0x80064ACCu, c, m);
    public static void ShadowPre80056c6c(CpuContext c, IMemory m) => ShadowCpu.Pre(0x80056C6Cu, c, m);

    /// <summary>Ground-height query FUN_80065488(hint, pos, mode): records inputs for tracing.</summary>
    public static void ShadowPre80065488(CpuContext c, IMemory m)
    {
        ShadowCpu.Pre(0x80065488u, c, m);
        if (Environment.GetEnvironmentVariable("RUMBLE_NATIVE_TRACE") != "1") return;
        _groundQueries ??= new();
        _groundQueries.Push((c.A0, c.A0 == 0 ? 0u : m.ReadU32(c.A0), unchecked((int)m.ReadU32(c.A1)),
            unchecked((int)m.ReadU32(c.A1 + 4u)), unchecked((int)m.ReadU32(c.A1 + 8u)), c.A2));
    }

    public static void ShadowPost80065488(CpuContext c, IMemory m)
    {
        ShadowCpu.Post(0x80065488u, c, m);
        if (Environment.GetEnvironmentVariable("RUMBLE_NATIVE_TRACE") != "1") return;
        if (_groundQueries == null || _groundQueries.Count == 0) return;
        var q = _groundQueries.Pop();
        if (++_groundTraceCounter > 400u) return;
        Console.Error.WriteLine(
            $"[host] ground: n={_groundTraceCounter} ra={c.RA:x8} mode={unchecked((int)q.Mode)} "
            + $"pos=({q.X},{q.Y},{q.Z}) hintIn={q.Hint:x8} -> y={unchecked((int)c.V0)} "
            + $"hintOut={(q.HintPtr == 0 ? 0u : m.ReadU32(q.HintPtr)):x8}");
    }

    /// <summary>
    /// SPU playback consumes the intro's audio ring buffer concurrently on the console. Deliver
    /// pending SPU and DMA interrupts before entering the recompiled routine's blocking wait.
    /// </summary>
    public static void IntroAudioPoll(CpuContext c, IMemory m)
    {
        uint packetSize = m.ReadU32(c.A0 + 4u);
        packetSize = ((packetSize & 0x000000FFu) << 24)
            | ((packetSize & 0x0000FF00u) << 8)
            | ((packetSize & 0x00FF0000u) >> 8)
            | ((packetSize & 0xFF000000u) >> 24);
        uint samples = ((packetSize - 16u) >> 1) / 15u;
        uint required = samples * 16u;
        uint state = m.ReadU32(c.GP + 0x408u);

        for (int guard = 0; guard < 64; guard++)
        {
            uint produced = m.ReadU32(state + 4u);
            uint free = m.ReadU32(state) - (produced - 0x3C00u);
            if (free >= required) return;
            RecompOne.Runtime.Runtime.PumpSpu();
        }

        if (Environment.GetEnvironmentVariable("RUMBLE_NATIVE_TRACE") == "1")
        {
            uint produced = m.ReadU32(state + 4u);
            uint consumed = m.ReadU32(state);
            Console.Error.WriteLine(
                $"[host] intro audio wait stalled: produced={produced} consumed={consumed} "
                + $"free={consumed - (produced - 0x3C00u)} required={required}");
        }
    }
}

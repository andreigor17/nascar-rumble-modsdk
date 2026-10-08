using RecompOne.Runtime.Context;
using RecompOne.Runtime.Memory;

namespace NascarRumble.Host;

/// <summary>
/// Cooperative scheduling points needed by the statically recompiled game.
/// </summary>
public static class NativeHooks
{
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
    /// CD callbacks fill the intro's audio ring buffer concurrently on the console. Pump the
    /// emulated CD reader before entering the recompiled routine's blocking buffer wait.
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
            uint read = m.ReadU32(state + 4u);
            uint available = m.ReadU32(state) - (read - 0x3C00u);
            if (available >= required) return;
            RecompOne.Runtime.Runtime.PumpCd();
        }

        if (Environment.GetEnvironmentVariable("RUMBLE_NATIVE_TRACE") == "1")
        {
            uint read = m.ReadU32(state + 4u);
            uint write = m.ReadU32(state);
            Console.Error.WriteLine(
                $"[host] intro audio underflow: read={read} write={write} "
                + $"available={write - (read - 0x3C00u)} required={required}");
        }
    }
}

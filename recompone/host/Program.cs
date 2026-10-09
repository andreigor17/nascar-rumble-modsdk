using RecompOne.Runtime.Memory;

if (args.Length >= 4 && args[0] == "--decode-lsc")
{
    // Diagnostic: --decode-lsc <cue> <disc path> <out.ppm>
    using var disc = RecompOne.Runtime.Cdrom.CueFs.Open(args[1]);
    var (rgba, width, height) = NascarRumble.Host.LscImage.Decode(disc.ReadFile(args[2]));
    using var ppm = File.Create(args[3]);
    ppm.Write(System.Text.Encoding.ASCII.GetBytes($"P6\n{width} {height}\n255\n"));
    for (int i = 0; i < rgba.Length; i += 4) ppm.Write(rgba, i, 3);
    Console.WriteLine($"{width}x{height} -> {args[3]}");
    return;
}

var mem = new PSMemory();
string cue = args.Length > 0 ? args[0]
    : "/opt/Projetos/rumble/NASCAR Rumble (USA)/NASCAR Rumble (USA).cue";
if (Environment.GetEnvironmentVariable("RUMBLE_NATIVE_TRACE") == "1")
{
    RecompOne.Runtime.Log.BiosOn = true;
    RecompOne.Runtime.Log.CdOn = true;
    RecompOne.Runtime.Log.DmaOn = true;
    RecompOne.Runtime.Log.GpuOn = true;
    RecompOne.Runtime.Log.MdecOn = true;
    RecompOne.Runtime.Log.SdkOn = true;
    RecompOne.Runtime.Log.SpuOn = true;
}
Console.WriteLine("[host] iniciando NASCAR Rumble nativo...");
if (Environment.GetEnvironmentVariable("RUMBLE_LAUNCHER") == "0")
{
    NascarRumble.Host.Launcher.LoadAndApply();
}
else
{
    NascarRumble.Host.Launcher.PrepareStartupDisplay();
    NascarRumble.Host.Launcher.RequestFonts();
    RecompOne.Runtime.Runtime.PreBoot = NascarRumble.Host.Launcher.Run;
}
try
{
    Recompiled.Entry.Run(mem, cue);
}
catch (Exception error)
{
    Console.Error.WriteLine("[host] o port nativo encontrou um erro e foi encerrado com segurança.");
    Console.Error.WriteLine(error);
    Environment.ExitCode = 1;
}
finally
{
    try
    {
        RecompOne.Runtime.Runtime.Shutdown();
    }
    catch (Exception error)
    {
        Console.Error.WriteLine($"[host] aviso ao fechar o runtime: {error.Message}");
    }
}

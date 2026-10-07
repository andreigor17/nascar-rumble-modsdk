using RecompOne.Runtime.Memory;

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

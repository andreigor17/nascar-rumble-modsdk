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
Recompiled.Entry.Run(mem, cue);

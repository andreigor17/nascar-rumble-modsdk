using RecompOne.Runtime.Memory;
var mem = new PSMemory();
string cue = args.Length > 0 ? args[0]
    : "/opt/Projetos/rumble/NASCAR Rumble (USA)/NASCAR Rumble (USA).cue";
Console.WriteLine("[host] iniciando NASCAR Rumble nativo...");
Recompiled.Entry.Run(mem, cue);

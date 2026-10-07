typedef unsigned int u32;

extern u32 probe_global_g0;

void probe_global_boolean(int value)
{
    probe_global_g0 = value != 0;
}

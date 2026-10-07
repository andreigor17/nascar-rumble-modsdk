typedef unsigned int u32;

extern void probe_target(u32 value, int mode);

void probe_call_with_loaded_argument(u32 *value)
{
    probe_target(*value, 1);
}

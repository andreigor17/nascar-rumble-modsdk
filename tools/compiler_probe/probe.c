typedef unsigned char u8;
typedef unsigned int u32;

void probe_empty(void)
{
}

void probe_store_zero(u32 *value)
{
    *value = 0;
}

int probe_return_7096(void)
{
    return 7096;
}

int probe_return_one(void)
{
    return 1;
}

void probe_clear_byte_1(u8 *object)
{
    object[1] = 0;
}

void probe_clear_byte_1012(u8 *object)
{
    object[1012] = 0;
}

void probe_set_byte_26_to_3(u8 *object)
{
    object[26] = 3;
}

void probe_set_byte_26_to_9(u8 *object)
{
    object[26] = 9;
}

void probe_init_fields(u8 *object)
{
    *(u32 *)(object + 4) = 3;
    *(unsigned short *)(object + 8) = 0;
}

int probe_scaled_byte(u8 *object, int index)
{
    u8 *entry = object + index;
    return *(int *)(object + 0x10) + entry[0x20] * 11;
}

int probe_clamp_between(int lower, int upper, int value)
{
    int result = upper;
    if (lower <= value && (result = value, upper <= lower)) {
        result = lower;
    }
    return result;
}

int probe_min(int first, int second)
{
    int result = first;
    if (second <= result) {
        result = second;
    }
    return result;
}

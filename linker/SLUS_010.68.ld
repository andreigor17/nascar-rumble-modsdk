SECTIONS
{
    HIDDEN(__romPos = 0);
    _gp = 0x800AF0E4;
    header_ROM_START = __romPos;
    header_VRAM = ADDR(.header);
    .header : AT(header_ROM_START) SUBALIGN(4)
    {
        FILL(0x00000000);
        header_DATA_START = .;
        build/asm/header.o(.data);
        header_DATA_END = .;
        header_DATA_SIZE = ABSOLUTE(header_DATA_END - header_DATA_START);
    }
    __romPos += SIZEOF(.header);
    header_ROM_END = __romPos;
    header_VRAM_END = .;

    payload_prefix_ROM_START = __romPos;
    payload_prefix_VRAM = ADDR(.payload_prefix);
    .payload_prefix : AT(payload_prefix_ROM_START) SUBALIGN(4)
    {
        FILL(0x00000000);
        payload_prefix_DATA_START = .;
        build/assets/payload_prefix.o(.data);
        payload_prefix_DATA_END = .;
        payload_prefix_DATA_SIZE = ABSOLUTE(payload_prefix_DATA_END - payload_prefix_DATA_START);
    }
    __romPos += SIZEOF(.payload_prefix);
    payload_prefix_ROM_END = __romPos;
    payload_prefix_VRAM_END = .;

    main_ROM_START = __romPos;
    main_VRAM = ADDR(.main);
    .main 0x80010030 : AT(main_ROM_START) SUBALIGN(4)
    {
        FILL(0x00000000);
        main_TEXT_START = .;
        build/asm/main_0.o(.text);
        build/src/game/FUN_80078c24.o(.text);
        build/asm/main_1.o(.text);
        main_TEXT_END = .;
        main_TEXT_SIZE = ABSOLUTE(main_TEXT_END - main_TEXT_START);
        main_RODATA_START = .;
        build/asm/main_0.o(.rodata);
        build/src/game/FUN_80078c24.o(.rodata);
        build/asm/main_1.o(.rodata);
        build/asm/data/main.rodata.o(.rodata);
        main_RODATA_END = .;
        main_RODATA_SIZE = ABSOLUTE(main_RODATA_END - main_RODATA_START);
        main_SDATA_START = .;
        build/asm/data/main.sdata.o(.sdata);
        main_SDATA_END = .;
        main_SDATA_SIZE = ABSOLUTE(main_SDATA_END - main_SDATA_START);
        main_DATA_START = .;
        build/asm/main_0.o(.data);
        build/src/game/FUN_80078c24.o(.data);
        build/asm/main_1.o(.data);
        build/asm/data/main.data.o(.data);
        main_DATA_END = .;
        main_DATA_SIZE = ABSOLUTE(main_DATA_END - main_DATA_START);
        main_BSS_START = .;
        build/asm/main_0.o(.bss);
        build/src/game/FUN_80078c24.o(.bss);
        build/asm/main_1.o(.bss);
        build/asm/data/main.bss.o(.bss);
        main_BSS_END = .;
        main_BSS_SIZE = ABSOLUTE(main_BSS_END - main_BSS_START);
    }
    __romPos += SIZEOF(.main);
    __romPos = ALIGN(__romPos, 4);
    main_ROM_END = __romPos;
    main_VRAM_END = .;

    payload_padding_ROM_START = __romPos;
    payload_padding_VRAM = ADDR(.payload_padding);
    .payload_padding 0x800AF538 : AT(payload_padding_ROM_START) SUBALIGN(4)
    {
        FILL(0x00000000);
        payload_padding_DATA_START = .;
        build/assets/payload_padding.o(.data);
        payload_padding_DATA_END = .;
        payload_padding_DATA_SIZE = ABSOLUTE(payload_padding_DATA_END - payload_padding_DATA_START);
    }
    __romPos += SIZEOF(.payload_padding);
    payload_padding_ROM_END = __romPos;
    payload_padding_VRAM_END = .;

    /DISCARD/ :
    {
        *(*);
    }
}

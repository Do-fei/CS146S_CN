from tools.asm65816 import lorom_offset
from tools.build_rom import ROM_SIZE, build_rom
from tools.mini_snes import CPU


def test_rom_header_and_checksum() -> None:
    rom = build_rom()
    assert len(rom) == ROM_SIZE
    title = bytes(rom[lorom_offset(0x80, 0xFFC0) : lorom_offset(0x80, 0xFFC0) + 21])
    assert title.startswith(b"CITY11")
    assert rom[lorom_offset(0x80, 0xFFD5)] == 0x20
    assert rom[lorom_offset(0x80, 0xFFD8)] == 0x03
    complement = rom[lorom_offset(0x80, 0xFFDC)] | (rom[lorom_offset(0x80, 0xFFDD)] << 8)
    checksum = rom[lorom_offset(0x80, 0xFFDE)] | (rom[lorom_offset(0x80, 0xFFDF)] << 8)
    assert (checksum ^ 0xFFFF) == complement
    assert (sum(rom) & 0xFFFF) == checksum


def test_rom_reaches_title_display() -> None:
    rom = build_rom()
    cpu = CPU(rom)
    cpu.reset()
    cpu.run(80_000)
    assert cpu.unknown is None
    assert (cpu.inidisp & 0x80) == 0
    assert cpu.tm & 3 == 3
    assert cpu.nmi_enabled
    assert any(cpu.vram[i] for i in range(0, 256))

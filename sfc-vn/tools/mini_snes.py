"""足以跑本游戏引擎的 65816 + Mode 1 PPU 子集。"""

from __future__ import annotations

from dataclasses import dataclass, field

from tools.asm65816 import lorom_offset
from tools.snes_gfx import decode_tile_4bpp


def bgr15_to_rgb(value: int) -> tuple[int, int, int]:
    r = (value & 0x1F) << 3
    g = ((value >> 5) & 0x1F) << 3
    b = ((value >> 10) & 0x1F) << 3
    return r, g, b


@dataclass
class CPU:
    rom: bytes
    wram: bytearray = field(default_factory=lambda: bytearray(0x20000))
    vram: bytearray = field(default_factory=lambda: bytearray(0x10000))
    cgram: bytearray = field(default_factory=lambda: bytearray(512))
    a: int = 0
    x: int = 0
    y: int = 0
    sp: int = 0x01FF
    d: int = 0
    dbr: int = 0
    pbr: int = 0
    pc: int = 0
    n: int = 0
    z: int = 0
    c: int = 0
    v: int = 0
    i: int = 1
    m: int = 1
    xflag: int = 1
    e: int = 1
    halted: bool = False
    nmi_enabled: bool = False
    joy: int = 0
    vmadd: int = 0
    vmain: int = 0x80
    cgadd: int = 0
    cg_latch: int | None = None
    inidisp: int = 0x8F
    bgmode: int = 0
    bg1sc: int = 0
    bg2sc: int = 0
    bg12nba: int = 0
    tm: int = 0
    dma: list[dict] = field(default_factory=lambda: [dict(ctrl=0, dest=0, src=0, size=0) for _ in range(8)])
    steps: int = 0
    last_opcode: int = 0
    unknown: int | None = None

    def reset(self) -> None:
        self.e = 1
        self.m = 1
        self.xflag = 1
        self.i = 1
        self.sp = 0x01FF
        self.d = 0
        self.dbr = 0
        self.pbr = 0x80
        self.pc = self.read16(0x80, 0xFFFC)

    def _sys_bank(self, bank: int) -> bool:
        return bank < 0x40 or 0x80 <= bank <= 0xBF

    def read8(self, bank: int, addr: int) -> int:
        addr &= 0xFFFF
        bank &= 0xFF
        if addr < 0x2000 and (self._sys_bank(bank) or bank == 0x7E):
            return self.wram[addr]
        if 0x2100 <= addr <= 0x21FF and self._sys_bank(bank):
            return 0
        if 0x4200 <= addr <= 0x421F and self._sys_bank(bank):
            if addr == 0x4212:
                return 0
            if addr == 0x4218:
                return self.joy & 0xFF
            if addr == 0x4219:
                return (self.joy >> 8) & 0xFF
            return 0
        if addr >= 0x8000:
            off = lorom_offset(bank, addr)
            if off < len(self.rom):
                return self.rom[off]
            return 0
        if bank == 0x7E:
            return self.wram[addr]
        if 0x70 <= bank <= 0x7D and addr < 0x8000:
            return self.wram[0x10000 + ((bank - 0x70) * 0x8000 + addr) & 0x1FFFF]
        return 0

    def write8(self, bank: int, addr: int, value: int) -> None:
        addr &= 0xFFFF
        value &= 0xFF
        if addr < 0x2000 and (self._sys_bank(bank) or bank == 0x7E):
            self.wram[addr] = value
            return
        if bank == 0x7E:
            self.wram[addr] = value
            return
        if 0x70 <= bank <= 0x7D and addr < 0x8000:
            self.wram[0x10000 + ((bank - 0x70) * 0x8000 + addr) & 0x1FFFF] = value
            return
        if 0x2100 <= addr <= 0x21FF and self._sys_bank(bank):
            self.write_ppu(addr, value)
            return
        if addr == 0x4200 and self._sys_bank(bank):
            self.nmi_enabled = bool(value & 0x80)
            return
        if addr == 0x420B and self._sys_bank(bank):
            self.run_dma(value)
            return
        if 0x4300 <= addr <= 0x437F and self._sys_bank(bank):
            ch = (addr >> 4) & 7
            which = addr & 0xF
            if which == 0:
                self.dma[ch]["ctrl"] = value
            elif which == 1:
                self.dma[ch]["dest"] = value
            elif which == 2:
                self.dma[ch]["src"] = (self.dma[ch]["src"] & 0xFFFF00) | value
            elif which == 3:
                self.dma[ch]["src"] = (self.dma[ch]["src"] & 0xFF00FF) | (value << 8)
            elif which == 4:
                self.dma[ch]["src"] = (self.dma[ch]["src"] & 0x00FFFF) | (value << 16)
            elif which == 5:
                self.dma[ch]["size"] = (self.dma[ch]["size"] & 0xFF00) | value
            elif which == 6:
                self.dma[ch]["size"] = (self.dma[ch]["size"] & 0x00FF) | (value << 8)

    def write16(self, bank: int, addr: int, value: int) -> None:
        self.write8(bank, addr, value & 0xFF)
        self.write8(bank, (addr + 1) & 0xFFFF, (value >> 8) & 0xFF)

    def read16(self, bank: int, addr: int) -> int:
        return self.read8(bank, addr) | (self.read8(bank, (addr + 1) & 0xFFFF) << 8)

    def write_ppu(self, addr: int, value: int) -> None:
        if addr == 0x2100:
            self.inidisp = value
        elif addr == 0x2105:
            self.bgmode = value
        elif addr == 0x2107:
            self.bg1sc = value
        elif addr == 0x2108:
            self.bg2sc = value
        elif addr == 0x210B:
            self.bg12nba = value
        elif addr == 0x2115:
            self.vmain = value
        elif addr == 0x2116:
            self.vmadd = (self.vmadd & 0xFF00) | value
        elif addr == 0x2117:
            self.vmadd = (self.vmadd & 0x00FF) | (value << 8)
        elif addr in (0x2118, 0x2119):
            off = (self.vmadd * 2) & 0xFFFE
            if addr == 0x2118:
                self.vram[off] = value
            else:
                self.vram[off + 1] = value
            if ((self.vmain & 0x80) and addr == 0x2119) or (
                (self.vmain & 0x80) == 0 and addr == 0x2118
            ):
                step = (1, 32, 128, 128)[self.vmain & 3]
                self.vmadd = (self.vmadd + step) & 0x7FFF
        elif addr == 0x2121:
            self.cgadd = value
            self.cg_latch = None
        elif addr == 0x2122:
            if self.cg_latch is None:
                self.cg_latch = value
            else:
                off = (self.cgadd * 2) & 0x1FF
                self.cgram[off] = self.cg_latch
                self.cgram[off + 1] = value
                self.cgadd = (self.cgadd + 1) & 0xFF
                self.cg_latch = None
        elif addr == 0x212C:
            self.tm = value

    def run_dma(self, mask: int) -> None:
        for ch in range(8):
            if not (mask & (1 << ch)):
                continue
            info = self.dma[ch]
            src = info["src"]
            size = info["size"] or 0x10000
            dest = 0x2100 | info["dest"]
            mode = info["ctrl"] & 7
            i = 0
            while i < size:
                if mode == 0:
                    self.write8(0, dest, self.read8(src >> 16, src & 0xFFFF))
                    src = (src & 0xFF0000) | ((src + 1) & 0xFFFF)
                    i += 1
                else:
                    self.write8(0, dest, self.read8(src >> 16, src & 0xFFFF))
                    src = (src & 0xFF0000) | ((src + 1) & 0xFFFF)
                    self.write8(0, dest + 1, self.read8(src >> 16, src & 0xFFFF))
                    src = (src & 0xFF0000) | ((src + 1) & 0xFFFF)
                    i += 2
            info["src"] = src

    def fetch8(self) -> int:
        value = self.read8(self.pbr, self.pc)
        self.pc = (self.pc + 1) & 0xFFFF
        return value

    def fetch16(self) -> int:
        lo = self.fetch8()
        hi = self.fetch8()
        return lo | (hi << 8)

    def set_nz8(self, value: int) -> int:
        value &= 0xFF
        self.n = (value >> 7) & 1
        self.z = int(value == 0)
        return value

    def set_nz16(self, value: int) -> int:
        value &= 0xFFFF
        self.n = (value >> 15) & 1
        self.z = int(value == 0)
        return value

    def set_a(self, value: int) -> None:
        if self.m:
            self.a = (self.a & 0xFF00) | self.set_nz8(value)
        else:
            self.a = self.set_nz16(value)

    def get_a(self) -> int:
        return self.a & 0xFF if self.m else self.a & 0xFFFF

    def push8(self, value: int) -> None:
        self.write8(0, self.sp, value & 0xFF)
        self.sp = (self.sp - 1) & (0xFF if self.e else 0xFFFF)
        if self.e:
            self.sp = 0x0100 | (self.sp & 0xFF)

    def pull8(self) -> int:
        self.sp = (self.sp + 1) & (0xFF if self.e else 0xFFFF)
        if self.e:
            self.sp = 0x0100 | (self.sp & 0xFF)
        return self.read8(0, self.sp)

    def push16(self, value: int) -> None:
        self.push8((value >> 8) & 0xFF)
        self.push8(value & 0xFF)

    def pull16(self) -> int:
        lo = self.pull8()
        hi = self.pull8()
        return lo | (hi << 8)

    def get_p(self) -> int:
        return (
            (self.n << 7)
            | (self.v << 6)
            | ((0 if self.e else self.m) << 5)
            | ((1 if self.e else self.xflag) << 4)
            | (self.i << 2)
            | (self.z << 1)
            | self.c
        )

    def set_p(self, value: int) -> None:
        self.n = (value >> 7) & 1
        self.v = (value >> 6) & 1
        if not self.e:
            self.m = (value >> 5) & 1
            self.xflag = (value >> 4) & 1
            if self.xflag:
                self.x &= 0xFF
                self.y &= 0xFF
        self.i = (value >> 2) & 1
        self.z = (value >> 1) & 1
        self.c = value & 1

    def adc(self, value: int) -> None:
        if self.m:
            total = (self.a & 0xFF) + value + self.c
            self.c = int(total > 0xFF)
            self.set_a(total)
        else:
            total = (self.a & 0xFFFF) + value + self.c
            self.c = int(total > 0xFFFF)
            self.set_a(total)

    def cmp(self, left: int, right: int, bits8: bool) -> None:
        diff = left - right
        self.c = int(left >= right)
        if bits8:
            self.set_nz8(diff)
        else:
            self.set_nz16(diff)

    def fire_nmi(self) -> None:
        if not self.nmi_enabled:
            return
        if self.e:
            self.push16(self.pc)
            self.push8(self.get_p())
            self.i = 1
            self.pc = self.read16(0x80, 0xFFFA)
        else:
            self.push8(self.pbr)
            self.push16(self.pc)
            self.push8(self.get_p())
            self.i = 1
            self.pbr = 0x80
            self.pc = self.read16(0x80, 0xFFEA)

    def step(self) -> None:
        op = self.fetch8()
        self.last_opcode = op
        self.steps += 1
        match op:
            case 0x18:
                self.c = 0
            case 0x38:
                self.c = 1
            case 0x58:
                self.i = 0
            case 0x78:
                self.i = 1
            case 0xFB:
                self.e, self.c = self.c, self.e
                if self.e:
                    self.m = 1
                    self.xflag = 1
                    self.x &= 0xFF
                    self.y &= 0xFF
                    self.sp = 0x0100 | (self.sp & 0xFF)
            case 0xC2:
                value = self.fetch8()
                self.set_p(self.get_p() & ~value)
            case 0xE2:
                value = self.fetch8()
                self.set_p(self.get_p() | value)
                if self.xflag:
                    self.x &= 0xFF
                    self.y &= 0xFF
            case 0xEA:
                pass
            case 0x40:
                self.set_p(self.pull8())
                self.pc = self.pull16()
                if not self.e:
                    self.pbr = self.pull8()
            case 0x60:
                self.pc = (self.pull16() + 1) & 0xFFFF
            case 0x20:
                dest = self.fetch16()
                self.push16((self.pc - 1) & 0xFFFF)
                self.pc = dest
            case 0x4C:
                self.pc = self.fetch16()
            case 0x80:
                off = self.fetch8()
                if off >= 0x80:
                    off -= 0x100
                self.pc = (self.pc + off) & 0xFFFF
            case 0xF0:
                self._branch(self.z)
            case 0xD0:
                self._branch(not self.z)
            case 0x90:
                self._branch(not self.c)
            case 0xB0:
                self._branch(self.c)
            case 0x10:
                self._branch(not self.n)
            case 0x30:
                self._branch(self.n)
            case 0xA9:
                self.set_a(self._imm())
            case 0xA2:
                self.x = self.set_nz8(self.fetch8()) if self.xflag else self.set_nz16(self.fetch16())
            case 0xA0:
                self.y = self.set_nz8(self.fetch8()) if self.xflag else self.set_nz16(self.fetch16())
            case 0xA5:
                self.set_a(self._read_dp(self.fetch8()))
            case 0x85:
                self._write_dp(self.fetch8(), self.get_a())
            case 0x64:
                self._write_dp(self.fetch8(), 0)
            case 0xAF:
                lo = self.fetch16()
                bank = self.fetch8()
                self.set_a(self.read8(bank, lo) if self.m else self.read16(bank, lo))
            case 0x8F:
                lo = self.fetch16()
                bank = self.fetch8()
                self._write_abs_bank(bank, lo, self.get_a())
            case 0xAD:
                self.set_a(self._read_abs(self.fetch16()))
            case 0x8D:
                self._write_abs(self.fetch16(), self.get_a())
            case 0x9C:
                self._write_abs(self.fetch16(), 0)
            case 0xBD:
                self.set_a(self._read_abs((self.fetch16() + self.x) & 0xFFFF))
            case 0x9D:
                self._write_abs((self.fetch16() + self.x) & 0xFFFF, self.get_a())
            case 0x99:
                self._write_abs((self.fetch16() + self.y) & 0xFFFF, self.get_a())
            case 0xA7:
                dp = self.fetch8()
                ptr = (
                    self.read8(0, (self.d + dp) & 0xFFFF)
                    | (self.read8(0, (self.d + dp + 1) & 0xFFFF) << 8)
                    | (self.read8(0, (self.d + dp + 2) & 0xFFFF) << 16)
                )
                self.set_a(self.read8(ptr >> 16, ptr & 0xFFFF))
            case 0x29:
                self.set_a(self.get_a() & self._imm())
            case 0x09:
                self.set_a(self.get_a() | self._imm())
            case 0x49:
                self.set_a(self.get_a() ^ self._imm())
            case 0x25:
                self.set_a(self.get_a() & self._read_dp(self.fetch8()))
            case 0x45:
                self.set_a(self.get_a() ^ self._read_dp(self.fetch8()))
            case 0xC9:
                self.cmp(self.get_a(), self._imm(), self.m == 1)
            case 0xC5:
                self.cmp(self.get_a(), self._read_dp(self.fetch8()), self.m == 1)
            case 0x69:
                self.adc(self._imm())
            case 0x65:
                self.adc(self._read_dp(self.fetch8()))
            case 0x0A:
                val = self.get_a()
                self.c = 1 if val & (0x80 if self.m else 0x8000) else 0
                self.set_a((val << 1) & (0xFF if self.m else 0xFFFF))
            case 0x4A:
                val = self.get_a()
                self.c = val & 1
                self.set_a(val >> 1)
            case 0x1A:
                self.set_a(self.get_a() + 1)
            case 0x3A:
                self.set_a(self.get_a() - 1)
            case 0xE6:
                self._inc_mem(False)
            case 0xC6:
                self._inc_mem(True)
            case 0xE8:
                self.x = self.set_nz8(self.x + 1) if self.xflag else self.set_nz16(self.x + 1)
            case 0xCA:
                self.x = self.set_nz8(self.x - 1) if self.xflag else self.set_nz16(self.x - 1)
            case 0xC8:
                self.y = self.set_nz8(self.y + 1) if self.xflag else self.set_nz16(self.y + 1)
            case 0x88:
                self.y = self.set_nz8(self.y - 1) if self.xflag else self.set_nz16(self.y - 1)
            case 0xAA:
                self.x = self.set_nz8(self.get_a()) if self.xflag else self.set_nz16(self.get_a())
            case 0x8A:
                self.set_a(self.x)
            case 0xA8:
                self.y = self.set_nz8(self.get_a()) if self.xflag else self.set_nz16(self.get_a())
            case 0x98:
                self.set_a(self.y)
            case 0x9A:
                self.sp = self.x if not self.e else (0x0100 | (self.x & 0xFF))
            case 0x5B:
                self.d = self.a & 0xFFFF
            case 0x7B:
                self.set_a(self.d)
            case 0x4B:
                self.push8(self.pbr)
            case 0xAB:
                self.dbr = self.pull8()
            case 0x48:
                if self.m:
                    self.push8(self.a)
                else:
                    self.push16(self.a)
            case 0x68:
                self.set_a(self.pull8() if self.m else self.pull16())
            case 0xDA:
                if self.xflag:
                    self.push8(self.x)
                else:
                    self.push16(self.x)
            case 0xFA:
                self.x = self.set_nz8(self.pull8()) if self.xflag else self.set_nz16(self.pull16())
            case 0x5A:
                if self.xflag:
                    self.push8(self.y)
                else:
                    self.push16(self.y)
            case 0x7A:
                self.y = self.set_nz8(self.pull8()) if self.xflag else self.set_nz16(self.pull16())
            case 0x8E:
                addr = self.fetch16()
                self.write8(self.dbr, addr, self.x & 0xFF)
                if not self.xflag:
                    self.write8(self.dbr, (addr + 1) & 0xFFFF, (self.x >> 8) & 0xFF)
            case 0x8C:
                addr = self.fetch16()
                self.write8(self.dbr, addr, self.y & 0xFF)
                if not self.xflag:
                    self.write8(self.dbr, (addr + 1) & 0xFFFF, (self.y >> 8) & 0xFF)
            case 0xAC:
                addr = self.fetch16()
                if self.xflag:
                    self.y = self.set_nz8(self.read8(self.dbr, addr))
                else:
                    self.y = self.set_nz16(self.read16(self.dbr, addr))
            case 0xAE:
                addr = self.fetch16()
                if self.xflag:
                    self.x = self.set_nz8(self.read8(self.dbr, addr))
                else:
                    self.x = self.set_nz16(self.read16(self.dbr, addr))
            case 0xEB:
                self.a = ((self.a & 0xFF) << 8) | ((self.a >> 8) & 0xFF)
                self.set_nz8(self.a & 0xFF)
            case _:
                self.unknown = op
                self.halted = True

    def _branch(self, cond: bool) -> None:
        off = self.fetch8()
        if off >= 0x80:
            off -= 0x100
        if cond:
            self.pc = (self.pc + off) & 0xFFFF

    def _imm(self) -> int:
        return self.fetch8() if self.m else self.fetch16()

    def _read_dp(self, dp: int) -> int:
        addr = (self.d + dp) & 0xFFFF
        if self.m:
            return self.read8(0, addr)
        return self.read16(0, addr)

    def _write_dp(self, dp: int, value: int) -> None:
        addr = (self.d + dp) & 0xFFFF
        self.write8(0, addr, value & 0xFF)
        if not self.m:
            self.write8(0, (addr + 1) & 0xFFFF, (value >> 8) & 0xFF)

    def _read_abs(self, addr: int) -> int:
        if self.m:
            return self.read8(self.dbr, addr)
        return self.read16(self.dbr, addr)

    def _write_abs(self, addr: int, value: int) -> None:
        self._write_abs_bank(self.dbr, addr, value)

    def _write_abs_bank(self, bank: int, addr: int, value: int) -> None:
        self.write8(bank, addr, value & 0xFF)
        if not self.m:
            self.write8(bank, (addr + 1) & 0xFFFF, (value >> 8) & 0xFF)

    def _inc_mem(self, dec: bool) -> None:
        dp = self.fetch8()
        addr = (self.d + dp) & 0xFFFF
        value = self.read8(0, addr)
        value = (value - 1) & 0xFF if dec else (value + 1) & 0xFF
        self.write8(0, addr, value)
        self.set_nz8(value)

    def run(self, max_steps: int, nmi_every: int = 800) -> None:
        start = self.steps
        while self.steps - start < max_steps and not self.halted:
            if self.nmi_enabled and self.steps and self.steps % nmi_every == 0:
                self.fire_nmi()
            self.step()


def render_frame(cpu: CPU) -> list[tuple[int, int, int]]:
    def pal(index: int) -> tuple[int, int, int]:
        off = (index * 2) & 0x1FE
        return bgr15_to_rgb(cpu.cgram[off] | (cpu.cgram[off + 1] << 8))

    def tile_pixels(chr_word_base: int, tile: int) -> list[int]:
        off = (chr_word_base * 2 + tile * 32) & 0xFFFE
        return decode_tile_4bpp(bytes(cpu.vram[off : off + 32]))

    def map_word(sc: int, tx: int, ty: int) -> int:
        base = (sc & 0xFC) << 8
        off = (base + ty * 32 + tx) * 2
        return cpu.vram[off] | (cpu.vram[off + 1] << 8)

    bg1_chr = (cpu.bg12nba & 0x0F) << 12
    bg2_chr = (cpu.bg12nba & 0xF0) << 8
    pixels: list[tuple[int, int, int]] = [pal(0)] * (256 * 224)
    if cpu.inidisp & 0x80:
        return [(0, 0, 0)] * (256 * 224)

    def draw_bg(sc: int, chr_base: int, enabled: bool) -> None:
        if not enabled:
            return
        for ty in range(28):
            for tx in range(32):
                word = map_word(sc, tx, ty)
                tile = word & 0x3FF
                pal_idx = (word >> 10) & 7
                pix = tile_pixels(chr_base, tile)
                for y in range(8):
                    for x in range(8):
                        color = pix[y * 8 + x]
                        if color == 0:
                            continue
                        px, py = tx * 8 + x, ty * 8 + y
                        if py >= 224:
                            continue
                        pixels[py * 256 + px] = pal(pal_idx * 16 + color)

    draw_bg(cpu.bg1sc, bg1_chr, cpu.tm & 1)
    draw_bg(cpu.bg2sc, bg2_chr, cpu.tm & 2)
    return pixels


def pixels_to_ppm(pixels: list[tuple[int, int, int]], path: str) -> None:
    from pathlib import Path

    Path(path).write_bytes(
        b"P6\n256 224\n255\n"
        + bytes(c for pix in pixels for c in pix)
    )

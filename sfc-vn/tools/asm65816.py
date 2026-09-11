"""小型 65816 汇编器，专为本游戏的 LoROM 引擎服务。"""

from __future__ import annotations

from dataclasses import dataclass, field


class AsmError(RuntimeError):
    pass


@dataclass
class _Fixup:
    offset: int
    kind: str
    label: str
    pc_after: int
    bank: int
    addr: int


@dataclass
class Asm:
    rom: bytearray
    labels: dict[str, tuple[int, int]] = field(default_factory=dict)
    fixups: list[_Fixup] = field(default_factory=list)
    bank: int = 0x80
    addr: int = 0x8000
    m16: bool = False
    x16: bool = False

    def offset(self) -> int:
        return lorom_offset(self.bank, self.addr)

    def org(self, bank: int, addr: int) -> None:
        if addr < 0x8000 or addr > 0xFFFF:
            raise AsmError(f"LoROM org must be in $8000-$FFFF: {addr:04X}")
        self.bank = bank
        self.addr = addr

    def here(self) -> tuple[int, int]:
        return self.bank, self.addr

    def label(self, name: str) -> None:
        self.labels[name] = (self.bank, self.addr)

    def emit(self, *values: int) -> None:
        for value in values:
            if not 0 <= value <= 0xFF:
                raise AsmError(f"byte out of range: {value}")
            self.rom[lorom_offset(self.bank, self.addr)] = value
            self.addr += 1
            if self.addr > 0xFFFF:
                self.bank += 1
                self.addr = 0x8000

    def db(self, *values: int) -> None:
        self.emit(*values)

    def dw(self, *values: int) -> None:
        for value in values:
            self.emit(value & 0xFF, (value >> 8) & 0xFF)

    def dl(self, *values: int) -> None:
        for value in values:
            self.emit(value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF)

    def place_bytes(self, data: bytes) -> tuple[int, int]:
        loc = self.here()
        for byte in data:
            self.emit(byte)
        return loc

    def resolve(self) -> None:
        for fix in self.fixups:
            if fix.label not in self.labels:
                raise AsmError(f"undefined label: {fix.label}")
            bank, addr = self.labels[fix.label]
            if fix.kind == "rel8":
                delta = addr - fix.pc_after
                if bank != fix.bank or delta < -128 or delta > 127:
                    raise AsmError(f"branch out of range: {fix.label} ({delta})")
                self.rom[fix.offset] = delta & 0xFF
            elif fix.kind == "abs16":
                self.rom[fix.offset] = addr & 0xFF
                self.rom[fix.offset + 1] = (addr >> 8) & 0xFF
            elif fix.kind == "abs24":
                self.rom[fix.offset] = addr & 0xFF
                self.rom[fix.offset + 1] = (addr >> 8) & 0xFF
                self.rom[fix.offset + 2] = bank & 0xFF
            else:
                raise AsmError(f"unknown fixup {fix.kind}")
        self.fixups.clear()

    def _rel(self, opcode: int, label: str) -> None:
        self.emit(opcode)
        self.fixups.append(
            _Fixup(self.offset(), "rel8", label, self.addr + 1, self.bank, self.addr)
        )
        self.emit(0)

    def _abs(self, opcode: int, label: str) -> None:
        self.emit(opcode)
        self.fixups.append(
            _Fixup(self.offset(), "abs16", label, self.addr + 2, self.bank, self.addr)
        )
        self.emit(0, 0)

    def _long(self, opcode: int, label: str) -> None:
        self.emit(opcode)
        self.fixups.append(
            _Fixup(self.offset(), "abs24", label, self.addr + 3, self.bank, self.addr)
        )
        self.emit(0, 0, 0)

    def sei(self) -> None:
        self.emit(0x78)

    def cli(self) -> None:
        self.emit(0x58)

    def clc(self) -> None:
        self.emit(0x18)

    def sec(self) -> None:
        self.emit(0x38)

    def cld(self) -> None:
        self.emit(0xD8)

    def xce(self) -> None:
        self.emit(0xFB)

    def nop(self) -> None:
        self.emit(0xEA)

    def rts(self) -> None:
        self.emit(0x60)

    def rti(self) -> None:
        self.emit(0x40)

    def rtl(self) -> None:
        self.emit(0x6B)

    def wai(self) -> None:
        self.emit(0xCB)

    def xba(self) -> None:
        self.emit(0xEB)

    def phk(self) -> None:
        self.emit(0x4B)

    def plb(self) -> None:
        self.emit(0xAB)

    def pha(self) -> None:
        self.emit(0x48)

    def pla(self) -> None:
        self.emit(0x68)

    def phx(self) -> None:
        self.emit(0xDA)

    def plx(self) -> None:
        self.emit(0xFA)

    def phy(self) -> None:
        self.emit(0x5A)

    def ply(self) -> None:
        self.emit(0x7A)

    def php(self) -> None:
        self.emit(0x08)

    def plp(self) -> None:
        self.emit(0x28)

    def tax(self) -> None:
        self.emit(0xAA)

    def txa(self) -> None:
        self.emit(0x8A)

    def tay(self) -> None:
        self.emit(0xA8)

    def tya(self) -> None:
        self.emit(0x98)

    def txs(self) -> None:
        self.emit(0x9A)

    def tcd(self) -> None:
        self.emit(0x5B)

    def tdc(self) -> None:
        self.emit(0x7B)

    def inx(self) -> None:
        self.emit(0xE8)

    def dex(self) -> None:
        self.emit(0xCA)

    def iny(self) -> None:
        self.emit(0xC8)

    def dey(self) -> None:
        self.emit(0x88)

    def asl_a(self) -> None:
        self.emit(0x0A)

    def lsr_a(self) -> None:
        self.emit(0x4A)

    def inc_a(self) -> None:
        self.emit(0x1A)

    def dec_a(self) -> None:
        self.emit(0x3A)

    def adc_dp(self, dp: int) -> None:
        self.emit(0x65, dp & 0xFF)

    def and_dp(self, dp: int) -> None:
        self.emit(0x25, dp & 0xFF)

    def eor_dp(self, dp: int) -> None:
        self.emit(0x45, dp & 0xFF)

    def cmp_dp(self, dp: int) -> None:
        self.emit(0xC5, dp & 0xFF)

    def stx_abs(self, addr: int) -> None:
        self.emit(0x8E, addr & 0xFF, (addr >> 8) & 0xFF)

    def sty_abs(self, addr: int) -> None:
        self.emit(0x8C, addr & 0xFF, (addr >> 8) & 0xFF)

    def ldy_abs(self, addr: int | str) -> None:
        if isinstance(addr, str):
            self._abs(0xAC, addr)
        else:
            self.emit(0xAC, addr & 0xFF, (addr >> 8) & 0xFF)

    def ldx_abs(self, addr: int | str) -> None:
        if isinstance(addr, str):
            self._abs(0xAE, addr)
        else:
            self.emit(0xAE, addr & 0xFF, (addr >> 8) & 0xFF)

    def sta_absy(self, addr: int) -> None:
        self.emit(0x99, addr & 0xFF, (addr >> 8) & 0xFF)

    def rol_a(self) -> None:
        self.emit(0x2A)

    def ror_a(self) -> None:
        self.emit(0x6A)

    def rep(self, value: int) -> None:
        self.emit(0xC2, value & 0xFF)
        if value & 0x20:
            self.m16 = True
        if value & 0x10:
            self.x16 = True

    def sep(self, value: int) -> None:
        self.emit(0xE2, value & 0xFF)
        if value & 0x20:
            self.m16 = False
        if value & 0x10:
            self.x16 = False

    def lda_imm(self, value: int) -> None:
        self.emit(0xA9)
        if self.m16:
            self.dw(value)
        else:
            self.emit(value & 0xFF)

    def ldx_imm(self, value: int) -> None:
        self.emit(0xA2)
        if self.x16:
            self.dw(value)
        else:
            self.emit(value & 0xFF)

    def ldy_imm(self, value: int) -> None:
        self.emit(0xA0)
        if self.x16:
            self.dw(value)
        else:
            self.emit(value & 0xFF)

    def lda_dp(self, dp: int) -> None:
        self.emit(0xA5, dp & 0xFF)

    def sta_dp(self, dp: int) -> None:
        self.emit(0x85, dp & 0xFF)

    def ldx_dp(self, dp: int) -> None:
        self.emit(0xA6, dp & 0xFF)

    def stx_dp(self, dp: int) -> None:
        self.emit(0x86, dp & 0xFF)

    def ldy_dp(self, dp: int) -> None:
        self.emit(0xA4, dp & 0xFF)

    def sty_dp(self, dp: int) -> None:
        self.emit(0x84, dp & 0xFF)

    def stz_dp(self, dp: int) -> None:
        self.emit(0x64, dp & 0xFF)

    def inc_dp(self, dp: int) -> None:
        self.emit(0xE6, dp & 0xFF)

    def dec_dp(self, dp: int) -> None:
        self.emit(0xC6, dp & 0xFF)

    def lda_abs(self, addr: int | str) -> None:
        if isinstance(addr, str):
            self._abs(0xAD, addr)
        else:
            self.emit(0xAD, addr & 0xFF, (addr >> 8) & 0xFF)

    def sta_abs(self, addr: int | str) -> None:
        if isinstance(addr, str):
            self._abs(0x8D, addr)
        else:
            self.emit(0x8D, addr & 0xFF, (addr >> 8) & 0xFF)

    def stz_abs(self, addr: int) -> None:
        self.emit(0x9C, addr & 0xFF, (addr >> 8) & 0xFF)

    def lda_long(self, addr24: int) -> None:
        self.emit(0xAF, addr24 & 0xFF, (addr24 >> 8) & 0xFF, (addr24 >> 16) & 0xFF)

    def sta_long(self, addr24: int) -> None:
        self.emit(0x8F, addr24 & 0xFF, (addr24 >> 8) & 0xFF, (addr24 >> 16) & 0xFF)

    def lda_il(self, dp: int) -> None:
        """LDA [dp] 24-bit indirect."""
        self.emit(0xA7, dp & 0xFF)

    def lda_absx(self, addr: int | str) -> None:
        if isinstance(addr, str):
            self._abs(0xBD, addr)
        else:
            self.emit(0xBD, addr & 0xFF, (addr >> 8) & 0xFF)

    def sta_absx(self, addr: int) -> None:
        self.emit(0x9D, addr & 0xFF, (addr >> 8) & 0xFF)

    def and_imm(self, value: int) -> None:
        self.emit(0x29)
        if self.m16:
            self.dw(value)
        else:
            self.emit(value & 0xFF)

    def ora_imm(self, value: int) -> None:
        self.emit(0x09)
        if self.m16:
            self.dw(value)
        else:
            self.emit(value & 0xFF)

    def eor_imm(self, value: int) -> None:
        self.emit(0x49)
        if self.m16:
            self.dw(value)
        else:
            self.emit(value & 0xFF)

    def cmp_imm(self, value: int) -> None:
        self.emit(0xC9)
        if self.m16:
            self.dw(value)
        else:
            self.emit(value & 0xFF)

    def cpx_imm(self, value: int) -> None:
        self.emit(0xE0)
        if self.x16:
            self.dw(value)
        else:
            self.emit(value & 0xFF)

    def cpy_imm(self, value: int) -> None:
        self.emit(0xC0)
        if self.x16:
            self.dw(value)
        else:
            self.emit(value & 0xFF)

    def adc_imm(self, value: int) -> None:
        self.emit(0x69)
        if self.m16:
            self.dw(value)
        else:
            self.emit(value & 0xFF)

    def sbc_imm(self, value: int) -> None:
        self.emit(0xE9)
        if self.m16:
            self.dw(value)
        else:
            self.emit(value & 0xFF)

    def bit_imm(self, value: int) -> None:
        self.emit(0x89)
        if self.m16:
            self.dw(value)
        else:
            self.emit(value & 0xFF)

    def jmp(self, label: str) -> None:
        self._abs(0x4C, label)

    def jsr(self, label: str) -> None:
        self._abs(0x20, label)

    def jml(self, label: str) -> None:
        self._long(0x5C, label)

    def bra(self, label: str) -> None:
        self._rel(0x80, label)

    def beq(self, label: str) -> None:
        self._rel(0xF0, label)

    def bne(self, label: str) -> None:
        self._rel(0xD0, label)

    def bcc(self, label: str) -> None:
        self._rel(0x90, label)

    def bcs(self, label: str) -> None:
        self._rel(0xB0, label)

    def bpl(self, label: str) -> None:
        self._rel(0x10, label)

    def bmi(self, label: str) -> None:
        self._rel(0x30, label)


def lorom_offset(bank: int, addr: int) -> int:
    return ((bank & 0x7F) << 15) + (addr & 0x7FFF)

#!/usr/bin/env python3
"""
exe_tool.py — canivete do SLUS_010.68 para trabalho de hook/patch (Trilha A e B).

Sem dependências. Opera direto no PS-X EXE (`extracted/SLUS_010.68`).

Comandos:
  dis <addr> [n]          desassembla n instruções (padrão 16) a partir de addr
  callers <addr>          acha todos os `jal addr` do EXE (call sites)
  jal <addr>              mostra o encoding de `jal addr` (palavra + bytes LE)
  freespace [minwords]    varre runs de padding (zeros/0xff) alinhados — candidatos a
                          hospedar código de hook (padrão: >= 32 palavras)
  hooksite <callsite> <novo_alvo>
                          mostra o patch exato (endereço de arquivo, palavra antiga->nova)

Endereços aceitam 0x8003132c ou 8003132c.
"""
import sys, struct, os

_REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXE = os.path.join(_REPO, "extracted", "SLUS_010.68")
HDR = 0x800

REGS = ["zero", "at", "v0", "v1", "a0", "a1", "a2", "a3", "t0", "t1", "t2", "t3",
        "t4", "t5", "t6", "t7", "s0", "s1", "s2", "s3", "s4", "s5", "s6", "s7",
        "t8", "t9", "k0", "k1", "gp", "sp", "fp", "ra"]


def load():
    data = open(EXE, "rb").read()
    pc0, gp0, taddr, tsize = struct.unpack("<4I", data[0x10:0x20])
    return data, taddr, tsize


DATA, TADDR, TSIZE = load()


def a2f(a):
    return (a - TADDR) + HDR


def f2a(o):
    return TADDR + (o - HDR)


def word(a):
    o = a2f(a)
    return struct.unpack("<I", DATA[o:o + 4])[0]


def parse_addr(s):
    s = s.lower()
    if not s.startswith("0x"):
        s = "0x" + s
    return int(s, 16)


def dis(i, pc=0):
    op = i >> 26; rs = (i >> 21) & 31; rt = (i >> 16) & 31
    rd = (i >> 11) & 31; sh = (i >> 6) & 31; fn = i & 63
    imm = i & 0xFFFF
    s = imm - 0x10000 if imm & 0x8000 else imm
    R = lambda n: REGS[n]
    if i == 0:
        return "nop"
    if op == 0:
        f = {0x00: "sll", 0x02: "srl", 0x03: "sra", 0x04: "sllv", 0x06: "srlv",
             0x21: "addu", 0x23: "subu", 0x24: "and", 0x25: "or", 0x26: "xor",
             0x2a: "slt", 0x2b: "sltu", 0x18: "mult", 0x1a: "div"}.get(fn)
        if fn == 0x08: return f"jr {R(rs)}"
        if fn == 0x09: return f"jalr {R(rd)},{R(rs)}"
        if fn in (0x00, 0x02, 0x03): return f"{f} {R(rd)},{R(rt)},{sh}"
        if fn in (0x10, 0x12): return f"{'mfhi' if fn==0x10 else 'mflo'} {R(rd)}"
        if f: return f"{f} {R(rd)},{R(rs)},{R(rt)}"
        return f"special fn=0x{fn:02x}"
    if op == 2: return f"j 0x{((i & 0x3FFFFFF) << 2) | 0x80000000:08x}"
    if op == 3: return f"jal 0x{((i & 0x3FFFFFF) << 2) | 0x80000000:08x}"
    tgt = pc + 4 + s * 4
    if op == 4: return f"beq {R(rs)},{R(rt)},0x{tgt:08x}"
    if op == 5: return f"bne {R(rs)},{R(rt)},0x{tgt:08x}"
    if op == 6: return f"blez {R(rs)},0x{tgt:08x}"
    if op == 7: return f"bgtz {R(rs)},0x{tgt:08x}"
    if op == 1: return f"bltz/bgez {R(rs)},0x{tgt:08x}"
    m = {8: "addi", 9: "addiu", 10: "slti", 11: "sltiu", 12: "andi", 13: "ori",
         14: "xori"}.get(op)
    if m: return f"{m} {R(rt)},{R(rs)},{s}"
    if op == 0x0F: return f"lui {R(rt)},0x{imm:04x}"
    ld = {0x20: "lb", 0x21: "lh", 0x23: "lw", 0x24: "lbu", 0x25: "lhu",
          0x28: "sb", 0x29: "sh", 0x2B: "sw"}.get(op)
    if ld: return f"{ld} {R(rt)},{s}({R(rs)})"
    return f"op=0x{op:02x} raw=0x{i:08x}"


def cmd_dis(addr, n=16):
    for k in range(n):
        a = addr + k * 4
        print(f"  0x{a:08x}: {word(a):08x}  {dis(word(a), a)}")


def jal_enc(target):
    return 0x0C000000 | ((target >> 2) & 0x03FFFFFF)


def cmd_callers(addr):
    enc = jal_enc(addr)
    pat = struct.pack("<I", enc)
    hits, start = [], HDR
    while True:
        i = DATA.find(pat, start)
        if i < 0:
            break
        if (i - HDR) % 4 == 0:
            hits.append(f2a(i))
        start = i + 1
    print(f"jal 0x{addr:08x} = 0x{enc:08x} ({pat.hex(' ')}) — {len(hits)} call site(s):")
    for h in hits:
        print(f"  0x{h:08x}   (delay slot: {dis(word(h + 4), h + 4)})")


def cmd_freespace(minwords=32):
    """Runs de padding alinhados a 4 — candidatos a hospedar o hook."""
    end = HDR + TSIZE
    runs, cur, val = [], None, None
    o = HDR
    while o + 4 <= end:
        wv = struct.unpack("<I", DATA[o:o + 4])[0]
        if wv in (0x00000000, 0xFFFFFFFF) and (cur is None or wv == val):
            if cur is None:
                cur, val = o, wv
        else:
            if cur is not None and (o - cur) // 4 >= minwords:
                runs.append((cur, (o - cur) // 4, val))
            cur, val = None, None
        o += 4
    if cur is not None and (end - cur) // 4 >= minwords:
        runs.append((cur, (end - cur) // 4, val))
    print(f"texto: 0x{TADDR:08x}..0x{TADDR + TSIZE:08x} (t_size 0x{TSIZE:x})")
    print(f"runs de padding >= {minwords} palavras: {len(runs)}")
    for off, nw, v in sorted(runs, key=lambda r: -r[1])[:25]:
        print(f"  0x{f2a(off):08x}  {nw:>6} palavras ({nw*4:>7} bytes)  fill=0x{v:08x}")


def cmd_hooksite(callsite, new_target):
    old = word(callsite)
    new = jal_enc(new_target)
    print(f"call site 0x{callsite:08x}  (offset de arquivo 0x{a2f(callsite):x})")
    print(f"  antes: 0x{old:08x}  {dis(old, callsite)}")
    print(f"  depois:0x{new:08x}  {dis(new, callsite)}")
    print(f"  bytes: {struct.pack('<I', old).hex(' ')} -> {struct.pack('<I', new).hex(' ')}")
    print(f"  delay slot (intacto) 0x{callsite+4:08x}: {dis(word(callsite + 4), callsite + 4)}")


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a:
        print(__doc__); sys.exit()
    c = a[0]
    if c == "dis":
        cmd_dis(parse_addr(a[1]), int(a[2]) if len(a) > 2 else 16)
    elif c == "callers":
        cmd_callers(parse_addr(a[1]))
    elif c == "jal":
        t = parse_addr(a[1]); e = jal_enc(t)
        print(f"jal 0x{t:08x} = 0x{e:08x}  bytes(LE) {struct.pack('<I', e).hex(' ')}")
    elif c == "freespace":
        cmd_freespace(int(a[1]) if len(a) > 1 else 32)
    elif c == "hooksite":
        cmd_hooksite(parse_addr(a[1]), parse_addr(a[2]))
    else:
        print("cmd?", c)

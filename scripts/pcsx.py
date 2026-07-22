#!/usr/bin/env python3
"""
pcsx.py — Controle total do NASCAR Rumble no PCSX-Redux via web API + canal Lua.

Requer: PCSX-Redux rodando com Web Server (8080) e o bootstrap Lua registrado
(handler /api/v1/lua/x). Ver docs/FASE5_RAM_MAP.md.

Capacidades:
  - eval Lua arbitrário          (lua)
  - apertar/soltar/tap de botões (press/release/tap)   [olhos = input do controle]
  - ler/escrever memória         (rd/wr)
  - screenshot da tela (VRAM)    (shot)

Botões (bit): SELECT=0 START=3 UP=4 RIGHT=5 DOWN=6 LEFT=7 L2=8 R2=9 L1=10 R1=11
              TRIANGLE=12 CIRCLE=13 CROSS=14 SQUARE=15
"""
import sys, time, urllib.request, urllib.parse
BASE = "http://localhost:8080"
BTN = dict(SELECT=0, START=3, UP=4, RIGHT=5, DOWN=6, LEFT=7, L2=8, R2=9, L1=10,
           R1=11, TRIANGLE=12, CIRCLE=13, CROSS=14, SQUARE=15)


def lua(code):
    url = BASE + "/api/v1/lua/x?code=" + urllib.parse.quote(code)
    return urllib.request.urlopen(urllib.request.Request(url, method="POST"), timeout=10).read().decode("utf-8","replace")


def _btn(b):
    return BTN[b.upper()] if isinstance(b, str) else int(b)


def press(*btns):
    for b in btns:
        lua(f"PCSX.SIO0.slots[1].pads[1].setOverride({_btn(b)}) return 1")


def release(*btns):
    for b in btns:
        lua(f"PCSX.SIO0.slots[1].pads[1].clearOverride({_btn(b)}) return 1")


def release_all():
    for b in BTN.values():
        lua(f"PCSX.SIO0.slots[1].pads[1].clearOverride({b}) return 1")


def tap(btn, ms=120):
    press(btn); time.sleep(ms/1000.0); release(btn)


def pause():
    lua("PCSX.pauseEmulator() return 1")


def resume():
    lua("PCSX.resumeEmulator() return 1")


def save_state():
    """Cria um ponto de restauração limpo (global Lua _RESTORE). NUNCA imprime o objeto (é enorme)."""
    lua("_RESTORE = PCSX.createSaveState() return 'saved'")


def load_state():
    """Volta ao ponto de restauração — base dos testes repetíveis sem contaminação de batida."""
    lua("if _RESTORE then PCSX.loadSaveState(_RESTORE) end return 'loaded'")


def rd(addr, n=1):
    with urllib.request.urlopen(BASE + "/api/v1/cpu/ram/raw", timeout=15) as r:
        return r.read()[addr-0x80000000: addr-0x80000000+n]


def wr(addr, data: bytes):
    off = addr - 0x80000000
    url = f"{BASE}/api/v1/cpu/ram/raw?offset={off}&size={len(data)}"
    urllib.request.urlopen(urllib.request.Request(url, data=data, method="POST"), timeout=10).read()


def shot(path="experiments/ram/shots/shot.png"):
    import numpy as np
    from PIL import Image
    from pathlib import Path
    vram = urllib.request.urlopen(BASE + "/api/v1/gpu/vram/raw", timeout=20).read()
    a = np.frombuffer(vram, dtype=np.uint16).reshape(512, 1024)
    def rgb(sub):
        r = ((sub & 0x1F) << 3).astype(np.uint8); g = (((sub >> 5) & 0x1F) << 3).astype(np.uint8)
        b = (((sub >> 10) & 0x1F) << 3).astype(np.uint8)
        return np.stack([r, g, b], -1)
    # os dois framebuffers (duplo buffer): (0,0) e (0,256), ~384 de largura
    top = rgb(a[0:240, 0:384]); bot = rgb(a[256:496, 0:384])
    img = np.concatenate([top, bot], axis=0)
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    Image.fromarray(img, "RGB").save(path)
    return path


if __name__ == "__main__":
    a = sys.argv[1:]
    if not a: print(__doc__); sys.exit()
    cmd = a[0]
    if cmd == "lua": print(lua(" ".join(a[1:])))
    elif cmd == "tap": tap(a[1], int(a[2]) if len(a) > 2 else 120); print("tap", a[1])
    elif cmd == "press": press(*a[1:]); print("press", a[1:])
    elif cmd == "release": release(*a[1:]); print("release", a[1:])
    elif cmd == "release_all": release_all(); print("released all")
    elif cmd == "shot": print(shot(a[1] if len(a) > 1 else "experiments/ram/shots/shot.png"))
    elif cmd == "rd": print(rd(int(a[1], 0), int(a[2]) if len(a) > 2 else 1).hex(" "))
    elif cmd == "pause": pause(); print("paused")
    elif cmd == "resume": resume(); print("resumed")
    elif cmd == "save_state": save_state(); print("restore criado")
    elif cmd == "load_state": load_state(); print("restore carregado")
    else: print("cmd?", cmd)

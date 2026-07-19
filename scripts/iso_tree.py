#!/usr/bin/env python3
"""
iso_tree.py — Parser de ISO9660 sobre imagens de PS1 (MODE2/2352).

Lê a imagem BIN "raw" (2352 bytes/setor, Mode2 Form1) sem convertê-la,
percorre a árvore de diretórios ISO9660 e emite:

  - ISO_TREE.md  : tabela com caminho, LBA, tamanho, SHA-1, magic e classificação
  - iso_tree.json: mesma informação em formato estruturado (para outras ferramentas)

Uso:
    python3 scripts/iso_tree.py "NASCAR Rumble (USA)/NASCAR Rumble (USA).bin"
    python3 scripts/iso_tree.py <bin> --extract extracted/   # também extrai os arquivos

Projeto NASCAR Rumble ModSDK. Não modifica a imagem original (somente leitura).
"""
import argparse
import hashlib
import json
import struct
import sys
from datetime import date
from pathlib import Path

SECTOR = 2352          # Mode2/2352
DATA_OFFSET = 24       # sync(12) + header(4) + subheader(8) => início dos dados (Form1)
USER_DATA = 2048       # bytes úteis por setor (Form1)


class RawIso:
    """Acesso a uma imagem MODE2/2352 como se fossem setores de 2048 bytes."""

    def __init__(self, path: Path):
        self.path = Path(path)
        self.f = open(self.path, "rb")

    def read_sectors(self, lba: int, count: int = 1) -> bytes:
        out = bytearray()
        for i in range(count):
            self.f.seek((lba + i) * SECTOR + DATA_OFFSET)
            out += self.f.read(USER_DATA)
        return bytes(out)

    def read_file(self, lba: int, size: int) -> bytes:
        n_sectors = (size + USER_DATA - 1) // USER_DATA
        return self.read_sectors(lba, n_sectors)[:size]

    def close(self):
        self.f.close()


# ---- Identificação de formato por magic bytes -------------------------------

def identify(data: bytes, name: str) -> tuple[str, str]:
    """Retorna (formato, classificacao) a partir dos primeiros bytes."""
    head = data[:16]
    up = name.upper()

    if head[:8] == b"PS-X EXE":
        return ("PS-X EXE (executável MIPS R3000)", "✅")
    if head[:4] == b"LRTC":          # 'CTRL' invertido
        return ("Container EA CTRL/SHOC/SHDR (chunks 4CC invertido)", "✅")
    if head[:4] == b"RVWS":          # 'SWVR' invertido
        return ("EA SWVR (áudio/stream — família Future Cop)", "✅")
    if head[:4] == b"VLC0":
        return ("Vídeo EA (VLC0 / família WVE-TGV)", "🟡")
    if up.endswith(".LSC"):
        return ("Loading screen (provável imagem comprimida)", "🔵")
    if up == "SYSTEM.CNF":
        return ("Config de boot (texto)", "✅")
    if up == "DUMMY.DAT":
        return ("Padding de posicionamento de setores", "🟡")
    if all(b == 0 for b in head):
        return ("Zeros (padding?)", "❓")
    return (f"Desconhecido (magic {head[:4].hex()})", "❓")


# ---- Walk do ISO9660 --------------------------------------------------------

def parse_dir_records(data: bytes):
    """Gera (nome, flags, lba, size) de um bloco de diretório ISO9660."""
    i = 0
    while i < len(data):
        rec_len = data[i]
        if rec_len == 0:
            # resto do setor é padding: pula para o próximo limite de 2048
            i = (i // USER_DATA + 1) * USER_DATA
            continue
        rec = data[i:i + rec_len]
        lba = struct.unpack("<I", rec[2:6])[0]
        size = struct.unpack("<I", rec[10:14])[0]
        flags = rec[25]
        name_len = rec[32]
        name = rec[33:33 + name_len]
        if name not in (b"\x00", b"\x01"):   # ignora '.' e '..'
            yield name.decode("ascii", "replace").split(";")[0], flags, lba, size
        i += rec_len


def walk(iso: RawIso, lba: int, size: int, path: str = "", acc=None):
    if acc is None:
        acc = []
    block = iso.read_sectors(lba, (size + USER_DATA - 1) // USER_DATA)
    for name, flags, elba, esize in parse_dir_records(block):
        full = f"{path}/{name}"
        is_dir = bool(flags & 0x02)
        if is_dir:
            acc.append({"path": full, "type": "dir", "lba": elba, "size": esize})
            walk(iso, elba, esize, full, acc)
        else:
            acc.append({"path": full, "type": "file", "lba": elba, "size": esize})
    return acc


def read_pvd(iso: RawIso):
    pvd = iso.read_sectors(16)
    assert pvd[1:6] == b"CD001", "PVD inválido — a imagem é MODE2/2352?"
    volume = pvd[40:72].decode("ascii", "replace").strip()
    vol_sectors = struct.unpack("<I", pvd[80:84])[0]
    root = pvd[156:190]
    root_lba = struct.unpack("<I", root[2:6])[0]
    root_size = struct.unpack("<I", root[10:14])[0]
    return volume, vol_sectors, root_lba, root_size


# ---- Saída ------------------------------------------------------------------

def hsize(n: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    f = float(n)
    for u in units:
        if f < 1024 or u == "GB":
            return f"{n} B" if u == "B" else f"{f:.1f} {u}"
        f /= 1024
    return f"{n} B"


def main():
    ap = argparse.ArgumentParser(description="Parser de ISO9660 para imagens PS1 MODE2/2352")
    ap.add_argument("bin", help="Caminho da imagem .bin (MODE2/2352)")
    ap.add_argument("--out-md", default="docs/ISO_TREE.md")
    ap.add_argument("--out-json", default="docs/iso_tree.json")
    ap.add_argument("--extract", metavar="DIR", help="Extrai todos os arquivos para DIR")
    args = ap.parse_args()

    iso = RawIso(Path(args.bin))
    volume, vol_sectors, root_lba, root_size = read_pvd(iso)
    entries = walk(iso, root_lba, root_size)

    files = [e for e in entries if e["type"] == "file"]
    total_files = len(files)
    total_dirs = len([e for e in entries if e["type"] == "dir"])

    # Hash + identificação (lê o conteúdo lógico de cada arquivo)
    for e in files:
        data = iso.read_file(e["lba"], e["size"])
        e["sha1"] = hashlib.sha1(data).hexdigest()
        e["magic_hex"] = data[:8].hex()
        fmt, cls = identify(data, Path(e["path"]).name)
        e["format"] = fmt
        e["class"] = cls
        if args.extract:
            dst = Path(args.extract) / e["path"].lstrip("/")
            dst.parent.mkdir(parents=True, exist_ok=True)
            dst.write_bytes(data)

    # JSON
    meta = {
        "source": Path(args.bin).name,
        "volume_id": volume,
        "volume_sectors": vol_sectors,
        "generated": str(date.today()),
        "file_count": total_files,
        "dir_count": total_dirs,
    }
    Path(args.out_json).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_json).write_text(json.dumps({"meta": meta, "entries": entries}, indent=2, ensure_ascii=False))

    # Markdown
    lines = [
        "# ISO_TREE — NASCAR Rumble (USA)",
        "",
        "> Gerado por `scripts/iso_tree.py` (somente leitura sobre o `.bin`). "
        "Classificação: ✅ Confirmado · 🟡 Provável · 🔵 Hipótese · ❓ Desconhecido",
        "",
        f"- **Volume:** `{volume}`  ",
        f"- **Setores no volume:** {vol_sectors:,} (~{hsize(vol_sectors*USER_DATA)})  ",
        f"- **Arquivos:** {total_files} · **Diretórios:** {total_dirs}  ",
        f"- **Gerado em:** {date.today()}",
        "",
        "| Caminho | LBA | Tamanho | Formato | Cl. | SHA-1 |",
        "|---|---:|---:|---|:--:|---|",
    ]
    for e in sorted(files, key=lambda x: x["lba"]):
        lines.append(
            f"| `{e['path']}` | {e['lba']} | {hsize(e['size'])} | {e['format']} | "
            f"{e['class']} | `{e['sha1'][:12]}…` |"
        )
    lines += ["", "## Diretórios", "", "| Caminho | LBA |", "|---|---:|"]
    for e in sorted([x for x in entries if x["type"] == "dir"], key=lambda x: x["lba"]):
        lines.append(f"| `{e['path']}/` | {e['lba']} |")
    lines.append("")

    Path(args.out_md).parent.mkdir(parents=True, exist_ok=True)
    Path(args.out_md).write_text("\n".join(lines))

    iso.close()
    print(f"OK: {total_files} arquivos, {total_dirs} diretórios.")
    print(f"  -> {args.out_md}")
    print(f"  -> {args.out_json}")
    if args.extract:
        print(f"  -> extraído para {args.extract}")


if __name__ == "__main__":
    main()

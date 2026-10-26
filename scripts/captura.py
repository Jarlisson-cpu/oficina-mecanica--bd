"""Gera uma imagem PNG (estilo terminal) a partir da saída REAL do psql.

Não altera o texto: só o desenha. Usado para as capturas de tela das
evidências.
"""
from PIL import Image, ImageDraw, ImageFont

FONTE = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
FONTE_B = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf"

BG, BAR, FG = (30, 32, 38), (52, 55, 64), (220, 223, 228)
VERDE, VERMELHO, AMARELO, CINZA, AZUL = (126, 211, 137), (255, 123, 114), (240, 200, 110), (140, 146, 158), (130, 180, 255)


def cor_da_linha(linha: str):
    s = linha.strip()
    if s.startswith("ERROR") or s.startswith("psql:") and "ERROR" in s:
        return VERMELHO
    if s.startswith("DETAIL") or s.startswith("HINT") or s.startswith("CONTEXT"):
        return AMARELO
    if s.startswith("--"):
        return CINZA
    if s.endswith("PASSOU") or "| PASSOU" in s:
        return VERDE
    if s.endswith("FALHOU") or "| FALHOU" in s:
        return VERMELHO
    if s.startswith(("INSERT", "UPDATE", "DELETE", "SELECT", "VALUES", "FROM", "WHERE", "RETURNING",
                     "EXPLAIN", "CREATE", "DROP", "SET", "BEGIN", "ROLLBACK", "WITH", "JOIN", "GROUP",
                     "ORDER", "LIMIT", "UNION", "  FROM", "  WHERE", "\\")):
        return AZUL
    return FG


def render(texto: str, destino: str, titulo: str = "psql — banco oficina (PostgreSQL 16)",
           tam: int = 15, max_col: int = 120):
    linhas = []
    for l in texto.rstrip("\n").split("\n"):
        l = l.replace("\t", "    ")
        while len(l) > max_col:
            linhas.append(l[:max_col])
            l = "  " + l[max_col:]
        linhas.append(l)
    try:
        f = ImageFont.truetype(FONTE, tam)
        fb = ImageFont.truetype(FONTE_B, tam - 1)
    except OSError:  # máquina sem a fonte DejaVu: usa a fonte embutida do Pillow
        f = fb = ImageFont.load_default(size=tam)
    cw = f.getbbox("M")[2]
    lh = int(tam * 1.45)
    pad, barra = 18, 34
    w = max(560, pad * 2 + cw * max(len(l) for l in linhas))
    h = barra + pad * 2 + lh * len(linhas)
    img = Image.new("RGB", (w, h), BG)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, w, barra], fill=BAR)
    for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
        d.ellipse([14 + i * 22, 11, 26 + i * 22, 23], fill=c)
    d.text((90, 8), titulo, font=fb, fill=(200, 203, 210))
    y = barra + pad
    for l in linhas:
        d.text((pad, y), l, font=f, fill=cor_da_linha(l))
        y += lh
    img.save(destino, optimize=True)

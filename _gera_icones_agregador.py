#!/usr/bin/env python3
"""Gera o icone do Agregador de Pesquisas no padrao dos icones do iOS recente.

Mesma linguagem do icone do Self Creighton (tabelinha/_gera_icones.py): squircle
em vez de retangulo arredondado, pecas elevadas com gradiente proprio, fio de luz
na aresta superior, especular (banda + radial) para ler como vidro, base
escurecida para dar espessura e sombra difusa sobre a placa.

Quatro variantes, para escolher:
  medidor  - o medidor atual (arco vermelho/azul, ponteiro dourado) em vidro
  barras   - duas pecas elevadas, vermelha e azul, como a barra do voto popular
  anel     - rosca dividida vermelho/azul, com miolo roxo
  curvas   - duas linhas cruzando (a corrida ao longo do tempo)

    python3 _gera_icones_agregador.py            # gera todas as variantes
    python3 _gera_icones_agregador.py medidor    # so uma

Gera PNG (32/64/180/512) e SVG a partir das MESMAS constantes, para nunca
divergirem. Saida em icones_agregador/<variante>/.
"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

BASE = Path(__file__).parent / "icones_agregador"

# Paleta do painel. Tons um pouco mais vivos que os do HTML, porque sobre a
# placa escura e com verniz por cima a cor chapada apaga.
ROXO_TOPO, ROXO_BASE = (58, 42, 104), (32, 20, 62)      # placa
VERM_TOPO, VERM_BASE = (232, 86, 100), (176, 34, 48)    # esquerda / Lula
AZUL_TOPO, AZUL_BASE = (122, 148, 255), (46, 74, 200)   # direita / Flavio
OURO_TOPO, OURO_BASE = (233, 205, 122), (185, 150, 58)  # ponteiro / divisor
CREME = (248, 247, 244)

N_SQUIRCLE = 5.0
SS = 4


def _L(arr):
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))


def squircle(size, n=N_SQUIRCLE):
    S = size * SS
    y, x = np.mgrid[0:S, 0:S].astype(np.float64)
    c = (S - 1) / 2.0
    r = S / 2.0
    dentro = (np.abs((x - c) / r) ** n + np.abs((y - c) / r) ** n) <= 1.0
    return _L(dentro * 255).resize((size, size), Image.LANCZOS)


def vgrad(size, topo, base):
    t = np.linspace(0.0, 1.0, size)[:, None]
    arr = np.stack([topo[i] * (1 - t) + base[i] * t for i in range(3)], axis=-1)
    return Image.fromarray(np.repeat(arr, size, axis=1).astype(np.uint8)).convert("RGB")


def rebordo(m, size, desloca, desfoque, forca):
    d = Image.new("L", (size, size), 0)
    d.paste(m, (0, desloca))
    r = np.clip(np.asarray(m, np.int16) - np.asarray(d, np.int16), 0, 255)
    r = _L(r).filter(ImageFilter.GaussianBlur(desfoque))
    luz = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    luz.putalpha(_L(np.asarray(r, np.float64) * forca))
    return luz


def envidraca(img, m, size):
    """Aplica especular (banda + radial) e base escurecida sobre uma mascara."""
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float64)
    t = yy / size
    banda = np.clip(1.0 - t / 0.42, 0, 1) ** 1.7 * 0.24
    d = np.sqrt(((xx - size * 0.34) / (size * 0.62)) ** 2
                + ((yy - size * 0.20) / (size * 0.46)) ** 2)
    radial = np.clip(1.0 - d, 0, 1) ** 2.0 * 0.30
    luz = np.clip(banda + radial, 0, 1) * 255
    camada = Image.new("RGBA", (size, size), (255, 255, 255, 0))
    camada.putalpha(_L(np.minimum(luz, np.asarray(m, np.float64))))
    img = Image.alpha_composite(img, camada)

    fundo = np.clip((t - 0.68) / 0.32, 0, 1) ** 1.5 * 0.18 * 255
    escuro = Image.new("RGBA", (size, size), (22, 28, 32, 0))
    escuro.putalpha(_L(np.minimum(fundo, np.asarray(m, np.float64))))
    return Image.alpha_composite(img, escuro)


def sombra_de(m, px, pos, desl, desf, forca=0.34):
    """Sombra montada no canvas INTEIRO (senao o borrao e cortado e vira halo)."""
    sm = Image.new("L", (px, px), 0)
    sm.paste(m, (pos[0], pos[1] + desl))
    sm = sm.filter(ImageFilter.GaussianBlur(desf))
    s = Image.new("RGBA", (px, px), (16, 12, 34, 0))
    s.putalpha(_L(np.asarray(sm, np.float64) * forca))
    return s


def placa(px, topo=ROXO_TOPO, base=ROXO_BASE):
    m = squircle(px)
    img = vgrad(px, topo, base).convert("RGBA")
    img.putalpha(m)
    return img, m


def _anel_mask(px, cx, cy, r_ext, r_int, a0, a1):
    """Mascara de setor de anel, por supersampling (angulos em graus, 0=leste, anti-horario)."""
    S = px * SS
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float64)
    X = (xx + 0.5) / SS - cx
    Y = (yy + 0.5) / SS - cy
    rr = np.sqrt(X * X + Y * Y)
    ang = (np.degrees(np.arctan2(-Y, X)) + 360.0) % 360.0
    if a0 <= a1:
        setor = (ang >= a0) & (ang <= a1)
    else:
        setor = (ang >= a0) | (ang <= a1)
    dentro = (rr <= r_ext) & (rr >= r_int) & setor
    return _L(dentro * 255).resize((px, px), Image.LANCZOS)


def _barra_mask(px, x, y, w, h, raio_n=N_SQUIRCLE):
    """Mascara de barra com cantos squircle (superelipse esticada)."""
    S = px * SS
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float64)
    X = (xx + 0.5) / SS
    Y = (yy + 0.5) / SS
    cx, cy = x + w / 2.0, y + h / 2.0
    dentro = (np.abs((X - cx) / (w / 2.0)) ** raio_n
              + np.abs((Y - cy) / (h / 2.0)) ** raio_n) <= 1.0
    return _L(dentro * 255).resize((px, px), Image.LANCZOS)


def _pinta(px, mask, topo, base, com_vidro=True):
    img = vgrad(px, topo, base).convert("RGBA")
    img.putalpha(mask)
    img = Image.alpha_composite(
        img, _mascarar(rebordo(mask, px, max(1, px // 40), max(0.6, px / 130), 0.9), mask, px))
    if com_vidro:
        img = envidraca(img, mask, px)
    return img


def _mascarar(camada, mask, px):
    a = np.minimum(np.asarray(camada.getchannel("A"), np.float64),
                   np.asarray(mask, np.float64))
    out = camada.copy()
    out.putalpha(_L(a))
    return out


# ── variantes ────────────────────────────────────────────────────────────────

def v_medidor(px):
    img, pm = placa(px)
    cx, cy = px / 2.0, px * 0.62
    r_ext, r_int = px * 0.335, px * 0.205
    for (a0, a1), (t, b) in [((92, 178), (VERM_TOPO, VERM_BASE)),
                             ((2, 88), (AZUL_TOPO, AZUL_BASE))]:
        m = _anel_mask(px, cx, cy, r_ext, r_int, a0, a1)
        img = Image.alpha_composite(img, sombra_de(m, px, (0, 0), max(1, round(px * 0.015)), max(0.9, px * 0.022)))
        img = Image.alpha_composite(img, _pinta(px, m, t, b))
    # Ponteiro dourado quase de pe, so levemente inclinado para a direita (lado azul).
    # Curto de proposito: a ponta para longe do arco, o que tambem melhora a leitura
    # a 16px, onde ponteiro comprido + pivo viravam um borrao unico.
    ang = np.radians(72.0)
    L = px * 0.225
    esp = max(2.0, px * 0.052)
    S = px * SS
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float64)
    X = (xx + 0.5) / SS - cx
    Y = (yy + 0.5) / SS - cy
    ux, uy = np.cos(ang), -np.sin(ang)
    proj = X * ux + Y * uy
    perp = np.abs(-X * uy + Y * ux)
    largura = esp / 2.0 * np.clip(1.0 - proj / L * 0.55, 0.25, 1.0)
    pm_ = _L(((proj >= -px * 0.02) & (proj <= L) & (perp <= largura)) * 255).resize((px, px), Image.LANCZOS)
    img = Image.alpha_composite(img, sombra_de(pm_, px, (0, 0), max(1, round(px * 0.012)), max(0.8, px * 0.018)))
    img = Image.alpha_composite(img, _pinta(px, pm_, OURO_TOPO, OURO_BASE))
    # pivo creme
    rb = px * 0.072
    bm = _anel_mask(px, cx, cy, rb, 0.0, 0, 360)
    img = Image.alpha_composite(img, sombra_de(bm, px, (0, 0), max(1, round(px * 0.012)), max(0.8, px * 0.018)))
    img = Image.alpha_composite(img, _pinta(px, bm, (255, 255, 255), (214, 210, 200)))
    return img, pm


def v_barras(px):
    """Tres barras assentadas na MESMA linha de base: le como grafico, nao como blocos
    soltos. Cantos mais quadrados (n alto) pelo mesmo motivo."""
    img, pm = placa(px)
    marg = px * 0.185
    util = px - marg * 2
    vao = util * 0.085
    larg = (util - vao * 2) / 3.0
    base_y = px * 0.795
    alturas = [px * 0.46, px * 0.335, px * 0.22]
    cores = [(VERM_TOPO, VERM_BASE), (AZUL_TOPO, AZUL_BASE), (OURO_TOPO, OURO_BASE)]
    for i, ((t, b), h) in enumerate(zip(cores, alturas)):
        x = marg + i * (larg + vao)
        m = _barra_mask(px, x, base_y - h, larg, h, 7.0)
        img = Image.alpha_composite(img, sombra_de(m, px, (0, 0), max(1, round(px * 0.016)), max(0.9, px * 0.024)))
        img = Image.alpha_composite(img, _pinta(px, m, t, b))
    return img, pm


def v_anel(px):
    img, pm = placa(px)
    cx = cy = px / 2.0
    r_ext, r_int = px * 0.335, px * 0.155
    for (a0, a1), (t, b) in [((88, 275), (VERM_TOPO, VERM_BASE)),
                             ((275, 88), (AZUL_TOPO, AZUL_BASE))]:
        m = _anel_mask(px, cx, cy, r_ext, r_int, a0, a1)
        img = Image.alpha_composite(img, sombra_de(m, px, (0, 0), max(1, round(px * 0.016)), max(0.9, px * 0.024)))
        img = Image.alpha_composite(img, _pinta(px, m, t, b))
    return img, pm


def _curva_mask(px, pts, esp):
    """Mascara de curva com pontas arredondadas: distancia minima a uma bezier
    quadratica amostrada. pts = (p0, controle, p1)."""
    S = px * SS
    yy, xx = np.mgrid[0:S, 0:S].astype(np.float64)
    X = (xx + 0.5) / SS
    Y = (yy + 0.5) / SS
    (ax, ay), (cx_, cy_), (bx, by) = pts
    dist = None
    n = 80
    ant = None
    for i in range(n + 1):
        t = i / n
        px_ = (1 - t) ** 2 * ax + 2 * (1 - t) * t * cx_ + t * t * bx
        py_ = (1 - t) ** 2 * ay + 2 * (1 - t) * t * cy_ + t * t * by
        if ant is not None:
            vx, vy = px_ - ant[0], py_ - ant[1]
            L2 = vx * vx + vy * vy
            if L2 > 0:
                s = np.clip(((X - ant[0]) * vx + (Y - ant[1]) * vy) / L2, 0, 1)
                dx = X - (ant[0] + s * vx)
                dy = Y - (ant[1] + s * vy)
                d = np.sqrt(dx * dx + dy * dy)
                dist = d if dist is None else np.minimum(dist, d)
        ant = (px_, py_)
    return _L((dist <= esp / 2.0) * 255).resize((px, px), Image.LANCZOS)


def v_curvas(px):
    """Duas linhas de tendencia que CONVERGEM sem se cruzar. Cruzar no centro
    produz um 'X', que o olho le como icone de fechar, nao como grafico."""
    img, pm = placa(px)
    esp = px * 0.105
    verm = ((px * 0.18, px * 0.62), (px * 0.50, px * 0.40), (px * 0.82, px * 0.36))
    azul = ((px * 0.18, px * 0.80), (px * 0.50, px * 0.72), (px * 0.82, px * 0.54))
    for pts, (t, b) in [(verm, (VERM_TOPO, VERM_BASE)), (azul, (AZUL_TOPO, AZUL_BASE))]:
        m = _curva_mask(px, pts, esp)
        img = Image.alpha_composite(img, sombra_de(m, px, (0, 0), max(1, round(px * 0.015)), max(0.9, px * 0.022)))
        img = Image.alpha_composite(img, _pinta(px, m, t, b))
    return img, pm


VARIANTES = {"medidor": v_medidor, "barras": v_barras, "anel": v_anel, "curvas": v_curvas}


def desenha(nome, px):
    img, pm = VARIANTES[nome](px)
    img = Image.alpha_composite(
        img, rebordo(pm, px, max(1, px // 34), max(0.6, px / 120), 0.75))
    img.putalpha(_L(np.minimum(np.asarray(img.getchannel("A"), np.int16),
                               np.asarray(pm, np.int16))))
    return img


# ── SVG do medidor ───────────────────────────────────────────────────────────
# Gerado das MESMAS constantes dos PNG (angulos, raios, cores), para o favicon
# embutido no HTML nunca divergir dos PNG do iOS.

def _hex(c):
    return "#%02x%02x%02x" % c


def _sq_path(cx, cy, r, n=N_SQUIRCLE, pts=96):
    e = 2.0 / n
    d = []
    for i in range(pts):
        a = 2 * np.pi * i / pts
        ca, sa = np.cos(a), np.sin(a)
        x = cx + r * np.sign(ca) * abs(ca) ** e
        y = cy + r * np.sign(sa) * abs(sa) ** e
        d.append(f"{'M' if i == 0 else 'L'}{x:.2f} {y:.2f}")
    return " ".join(d) + " Z"


def _setor(cx, cy, re, ri, a0, a1):
    """Setor de anel. Angulos em graus, 0=leste, anti-horario (y do SVG cresce p/ baixo)."""
    def P(r, a):
        t = np.radians(a)
        return cx + r * np.cos(t), cy - r * np.sin(t)
    x0, y0 = P(re, a0); x1, y1 = P(re, a1)
    x2, y2 = P(ri, a1); x3, y3 = P(ri, a0)
    grande = 1 if (a1 - a0) % 360 > 180 else 0
    return (f"M{x0:.2f} {y0:.2f} A{re:.2f} {re:.2f} 0 {grande} 0 {x1:.2f} {y1:.2f} "
            f"L{x2:.2f} {y2:.2f} A{ri:.2f} {ri:.2f} 0 {grande} 1 {x3:.2f} {y3:.2f} Z")


def gera_svg_medidor(px=512):
    cx, cy = px / 2.0, px * 0.62
    re, ri = px * 0.335, px * 0.205
    ang, L = 72.0, px * 0.225
    esp = max(2.0, px * 0.052)
    rb = px * 0.072

    t = np.radians(ang)
    ux, uy = np.cos(t), -np.sin(t)
    pxx, pyy = -uy, ux                       # perpendicular
    bx, by = cx - ux * px * 0.02, cy - uy * px * 0.02
    tx, ty = cx + ux * L, cy + uy * L
    w0, w1 = esp / 2.0, esp / 2.0 * 0.45     # base larga, ponta fina
    agulha = (f"M{bx + pxx * w0:.2f} {by + pyy * w0:.2f} L{tx + pxx * w1:.2f} {ty + pyy * w1:.2f} "
              f"L{tx - pxx * w1:.2f} {ty - pyy * w1:.2f} L{bx - pxx * w0:.2f} {by - pyy * w0:.2f} Z")

    defs = [
        f'<linearGradient id="pl" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{_hex(ROXO_TOPO)}"/><stop offset="1" stop-color="{_hex(ROXO_BASE)}"/></linearGradient>',
        f'<linearGradient id="gv" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{_hex(VERM_TOPO)}"/><stop offset="1" stop-color="{_hex(VERM_BASE)}"/></linearGradient>',
        f'<linearGradient id="ga" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{_hex(AZUL_TOPO)}"/><stop offset="1" stop-color="{_hex(AZUL_BASE)}"/></linearGradient>',
        f'<linearGradient id="go" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="{_hex(OURO_TOPO)}"/><stop offset="1" stop-color="{_hex(OURO_BASE)}"/></linearGradient>',
        f'<linearGradient id="gp" x1="0" y1="0" x2="0" y2="1">'
        f'<stop offset="0" stop-color="#ffffff"/><stop offset="1" stop-color="{_hex((214, 210, 200))}"/></linearGradient>',
        '<linearGradient id="vz" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset="0" stop-color="#fff" stop-opacity=".26"/><stop offset=".42" stop-color="#fff" stop-opacity="0"/></linearGradient>',
        '<radialGradient id="es" cx=".34" cy=".20" r=".62">'
        '<stop offset="0" stop-color="#fff" stop-opacity=".32"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></radialGradient>',
        '<linearGradient id="bs" x1="0" y1="0" x2="0" y2="1">'
        '<stop offset=".68" stop-color="#161c20" stop-opacity="0"/><stop offset="1" stop-color="#161c20" stop-opacity=".18"/></linearGradient>',
        f'<filter id="sb" x="-40%" y="-40%" width="180%" height="190%">'
        f'<feDropShadow dx="0" dy="{px * 0.014:.1f}" stdDeviation="{px * 0.020:.1f}" flood-color="#100c22" flood-opacity=".34"/></filter>',
        f'<clipPath id="cp"><path d="{_sq_path(px / 2, px / 2, px / 2)}"/></clipPath>',
    ]

    corpo = [f'<path d="{_sq_path(px/2, px/2, px/2)}" fill="url(#pl)"/>']
    for d, g in [(_setor(cx, cy, re, ri, 92, 178), "gv"), (_setor(cx, cy, re, ri, 2, 88), "ga")]:
        corpo.append(f'<g filter="url(#sb)"><path d="{d}" fill="url(#{g})"/></g>')
        corpo.append(f'<path d="{d}" fill="url(#bs)"/><path d="{d}" fill="url(#vz)"/><path d="{d}" fill="url(#es)"/>')
    corpo.append(f'<g filter="url(#sb)"><path d="{agulha}" fill="url(#go)"/></g>')
    corpo.append(f'<path d="{agulha}" fill="url(#vz)"/>')
    corpo.append(f'<g filter="url(#sb)"><circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rb:.2f}" fill="url(#gp)"/></g>')
    corpo.append(f'<circle cx="{cx:.2f}" cy="{cy:.2f}" r="{rb:.2f}" fill="url(#vz)"/>')

    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {px} {px}" role="img" '
            f'aria-label="Agregador de pesquisas">\n  <defs>{"".join(defs)}</defs>\n'
            f'  <g clip-path="url(#cp)">\n    ' + "\n    ".join(corpo) + '\n  </g>\n</svg>\n')


if __name__ == "__main__":
    alvos = sys.argv[1:] or list(VARIANTES)
    for nome in alvos:
        if nome not in VARIANTES:
            print(f"variante desconhecida: {nome}"); continue
        d = BASE / nome
        d.mkdir(parents=True, exist_ok=True)
        for arq, px in [("favicon-32.png", 32), ("favicon-64.png", 64),
                        ("apple-touch-icon.png", 180), ("icone-512.png", 512)]:
            desenha(nome, px * 2).resize((px, px), Image.LANCZOS).save(d / arq)
        if nome == "medidor":
            (d / "favicon.svg").write_text(gera_svg_medidor(), encoding="utf-8")
        print(f"{nome}: {', '.join(p.name for p in sorted(d.iterdir()))}")

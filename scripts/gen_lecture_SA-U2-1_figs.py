#!/usr/bin/env python3
"""gen_lecture_SA-U2-1_figs.py — 重繪 study/lecture-SA-U2-1.html 的 SVG 圖解

與 gen_lecture_SA-U1-2_figs.py 同一套做法：
  * 結構圖一律依題目真實尺寸（World: m→px）繪製；
  * 彎矩圖、剪力圖、撓度曲線、能量曲線全部由解析中的公式直接計算，
    並以 assert 對照 raw/solutions/ 的答案（數字不是手畫上去的）；
  * HTML 內以 <!--FIG:id--> ... 標記圖位，本腳本只替換標記後 <div class="fig"> 內的 <svg>…</svg>，
    圖說（.cap）與正文不動。可重複執行。

用法：python scripts/gen_lecture_SA-U2-1_figs.py [study/lecture-SA-U2-1.html]
"""

# ======================= svglib.py（與 U1-2 腳本相同） =======================
"""Tiny SVG drawing helpers for structural-analysis lecture figures.

All geometry is in screen px; structural drawings use World(...) to map
metres -> px so that every figure is drawn to scale.  No <marker> elements
are used (arrowheads are explicit polygons) so several SVGs can live inline
in one HTML page without id clashes.
"""
import math

INK = '#37474f'
LOAD = '#c62828'
REAC = '#1565c0'
MOM = '#6a1b9a'
DIM = '#78909c'
GOOD = '#2e7d32'
ORG = '#ef6c00'
GHOST = '#b0bec5'
MUT = '#607d8b'


def f(v):
    s = f"{v:.2f}".rstrip('0').rstrip('.')
    return '0' if s == '-0' else s


def esc(t):
    return t.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


class SVG:
    def __init__(self, w, h, title=''):
        self.w, self.h, self.el, self.title = w, h, [], title

    def add(self, s):
        self.el.append(s)

    # ---------- primitives ----------
    def line(self, x1, y1, x2, y2, c=INK, w=2, dash=None, cap='round', op=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        o = f' opacity="{op}"' if op else ''
        self.add(f'<line x1="{f(x1)}" y1="{f(y1)}" x2="{f(x2)}" y2="{f(y2)}" stroke="{c}" '
                 f'stroke-width="{w}" stroke-linecap="{cap}"{d}{o}/>')

    def pl(self, pts, c=INK, w=2, fill='none', dash=None, close=False, op=None, join='round'):
        p = ' '.join(f'{f(x)},{f(y)}' for x, y in pts)
        tag = 'polygon' if close else 'polyline'
        d = f' stroke-dasharray="{dash}"' if dash else ''
        o = f' opacity="{op}"' if op else ''
        self.add(f'<{tag} points="{p}" fill="{fill}" stroke="{c}" stroke-width="{w}" '
                 f'stroke-linejoin="{join}"{d}{o}/>')

    def area(self, pts, fill, op=0.25, c='none', w=0):
        p = ' '.join(f'{f(x)},{f(y)}' for x, y in pts)
        self.add(f'<polygon points="{p}" fill="{fill}" fill-opacity="{op}" stroke="{c}" stroke-width="{w}"/>')

    def rect(self, x, y, w, h, fill='#fff', c=INK, sw=1, rx=0, op=None, dash=None):
        o = f' fill-opacity="{op}"' if op is not None else ''
        d = f' stroke-dasharray="{dash}"' if dash else ''
        self.add(f'<rect x="{f(x)}" y="{f(y)}" width="{f(w)}" height="{f(h)}" rx="{rx}" fill="{fill}"{o} '
                 f'stroke="{c}" stroke-width="{sw}"{d}/>')

    def circ(self, x, y, r, fill='#fff', c=INK, w=2):
        self.add(f'<circle cx="{f(x)}" cy="{f(y)}" r="{f(r)}" fill="{fill}" stroke="{c}" stroke-width="{w}"/>')

    def text(self, x, y, t, size=12.5, c=INK, anchor='middle', bold=False, italic=False, raw=False):
        b = ' font-weight="bold"' if bold else ''
        i = ' font-style="italic"' if italic else ''
        tt = t if raw else esc(t)
        self.add(f'<text x="{f(x)}" y="{f(y)}" font-size="{size}" fill="{c}" text-anchor="{anchor}"{b}{i}>{tt}</text>')

    def halo(self, x, y, t, size=12.5, c=INK, anchor='middle', bold=False):
        """text with white halo for legibility over lines"""
        b = ' font-weight="bold"' if bold else ''
        self.add(f'<text x="{f(x)}" y="{f(y)}" font-size="{size}" fill="{c}" text-anchor="{anchor}"{b} '
                 f'stroke="#fff" stroke-width="4" paint-order="stroke" stroke-linejoin="round">{esc(t)}</text>')

    # ---------- arrows ----------
    def head(self, x, y, ang, c, L=10, W=4.5):
        """arrowhead with tip at (x,y) pointing along angle ang (screen radians)"""
        ca, sa = math.cos(ang), math.sin(ang)
        bx, by = x - L * ca, y - L * sa
        p1 = (bx + W * sa, by - W * ca)
        p2 = (bx - W * sa, by + W * ca)
        self.add(f'<polygon points="{f(x)},{f(y)} {f(p1[0])},{f(p1[1])} {f(p2[0])},{f(p2[1])}" fill="{c}"/>')

    def arrow(self, x1, y1, x2, y2, c=LOAD, w=2.5, L=10, W=4.5, dash=None, both=False):
        ang = math.atan2(y2 - y1, x2 - x1)
        ex, ey = x2 - (L - 2) * math.cos(ang), y2 - (L - 2) * math.sin(ang)
        sx, sy = x1, y1
        if both:
            sx, sy = x1 + (L - 2) * math.cos(ang), y1 + (L - 2) * math.sin(ang)
        self.line(sx, sy, ex, ey, c, w, dash=dash, cap='butt')
        self.head(x2, y2, ang, c, L, W)
        if both:
            self.head(x1, y1, ang + math.pi, c, L, W)

    def moment(self, cx, cy, r, ccw=True, c=MOM, w=2.4, a0=None, span=270):
        """circular moment arrow. ccw in the *screen-visual* sense."""
        if a0 is None:
            a0 = -135 if ccw else -45
        # visual angles: measured from +x, counter-clockwise visually (y up)
        sgn = 1 if ccw else -1
        a1 = a0 + sgn * span
        n = 40
        pts = []
        for k in range(n + 1):
            a = math.radians(a0 + (a1 - a0) * k / n)
            pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        self.pl(pts[:-3], c, w)
        # tangent at end
        a = math.radians(a1)
        tx, ty = -math.sin(a) * sgn, -math.cos(a) * sgn  # derivative wrt angle, y flipped
        ex, ey = pts[-1]
        self.head(ex, ey, math.atan2(ty, tx), c, 9, 4.5)

    # ---------- supports (drawn pointing 'down' then rotated) ----------
    def _g(self, x, y, rot, body):
        self.add(f'<g transform="translate({f(x)},{f(y)}) rotate({rot})">{body}</g>')

    def pin(self, x, y, rot=0, s=1.0, c=INK):
        h, b = 16 * s, 11 * s
        body = (f'<polygon points="0,0 {-b},{h} {b},{h}" fill="#fff" stroke="{c}" stroke-width="2"/>'
                + self._ground(h, b * 1.5, c))
        self._g(x, y, rot, body)
        self.circ(x, y, 3.2 * s, '#fff', c, 1.8)

    def roller(self, x, y, rot=0, s=1.0, c=INK):
        h, b = 13 * s, 10 * s
        r = 3.6 * s
        body = (f'<polygon points="0,0 {-b},{h} {b},{h}" fill="#fff" stroke="{c}" stroke-width="2"/>'
                f'<circle cx="{-b*0.5}" cy="{h+r}" r="{r}" fill="#fff" stroke="{c}" stroke-width="1.6"/>'
                f'<circle cx="{b*0.5}" cy="{h+r}" r="{r}" fill="#fff" stroke="{c}" stroke-width="1.6"/>'
                + self._ground(h + 2 * r, b * 1.6, c))
        self._g(x, y, rot, body)
        self.circ(x, y, 3.2 * s, '#fff', c, 1.8)

    def fixed(self, x, y, rot=0, s=1.0, c=INK, half=16):
        body = f'<line x1="{-half*s}" y1="0" x2="{half*s}" y2="0" stroke="{c}" stroke-width="3"/>'
        for k in range(6):
            xx = -half * s + k * (2 * half * s / 5)
            body += f'<line x1="{f(xx)}" y1="0" x2="{f(xx-6*s)}" y2="{f(8*s)}" stroke="{c}" stroke-width="1.4"/>'
        self._g(x, y, rot, body)

    def _ground(self, y, half, c):
        g = f'<line x1="{-half}" y1="{y}" x2="{half}" y2="{y}" stroke="{c}" stroke-width="2"/>'
        n = 5
        for k in range(n):
            xx = -half + 4 + k * (2 * half - 4) / (n - 1)
            g += f'<line x1="{f(xx)}" y1="{y}" x2="{f(xx-6)}" y2="{y+7}" stroke="{c}" stroke-width="1.3"/>'
        return g

    def hinge(self, x, y, r=5.5, c=INK):
        self.circ(x, y, r, '#fff', c, 2.2)

    def node(self, x, y, r=3.4, c=INK):
        self.circ(x, y, r, '#fff', c, 1.6)

    def wall(self, x, y1, y2, side=1, c=INK):
        """vertical wall line at x; hatching on side (+1 right, -1 left)"""
        self.line(x, y1, x, y2, c, 2.5)
        n = int((y2 - y1) / 9)
        for k in range(n + 1):
            yy = y1 + k * (y2 - y1) / n
            self.line(x, yy, x + side * 7, yy - 6, c, 1.3)

    def dim(self, x1, y1, x2, y2, label, off=0, c=DIM, size=12, lab_off=None):
        """dimension line between two points, offset perpendicular by off px"""
        ang = math.atan2(y2 - y1, x2 - x1)
        nx, ny = -math.sin(ang), math.cos(ang)
        a1, b1 = x1 + nx * off, y1 + ny * off
        a2, b2 = x2 + nx * off, y2 + ny * off
        if off:
            self.line(x1, y1, a1 + nx * 4 * (1 if off > 0 else -1), b1 + ny * 4 * (1 if off > 0 else -1), c, 0.8)
            self.line(x2, y2, a2 + nx * 4 * (1 if off > 0 else -1), b2 + ny * 4 * (1 if off > 0 else -1), c, 0.8)
        self.arrow(a1, b1, a2, b2, c, 1, L=7, W=3, both=True)
        lo = lab_off if lab_off is not None else (-6 if abs(ang) < 1e-6 or abs(abs(ang) - math.pi) < 1e-6 else 0)
        mx, my = (a1 + a2) / 2, (b1 + b2) / 2
        if abs(math.cos(ang)) > 0.5:
            self.halo(mx, my + lo, label, size, c)
        else:
            self.halo(mx - 6, my + 4, label, size, c, anchor='end')

    def render(self, extra_style=''):
        t = f'<title>{esc(self.title)}</title>' if self.title else ''
        return (f'<svg viewBox="0 0 {self.w} {self.h}" xmlns="http://www.w3.org/2000/svg" '
                f'role="img" font-family="&quot;Microsoft JhengHei&quot;,&quot;Noto Sans TC&quot;,sans-serif">'
                f'{t}' + ''.join(self.el) + '</svg>')


class World:
    """metres -> px.  y up in world, down on screen."""

    def __init__(self, ox, oy, s, sy=None):
        self.ox, self.oy, self.s = ox, oy, s
        self.sy = s if sy is None else sy

    def __call__(self, x, y=0):
        return self.ox + self.s * x, self.oy - self.sy * y

    def X(self, x):
        return self.ox + self.s * x

    def Y(self, y):
        return self.oy - self.sy * y


# ======================= helpers（U2-1 專用） =======================
from fractions import Fraction as Fr
TITLE = '#0d47a1'
BMD = '#c62828'      # 彎矩圖
SFD = '#1565c0'      # 剪力圖
DEF = '#1565c0'      # 撓度曲線
GAP = '#b71c1c'


def rich(*parts):
    """raw SVG text markup; a 1-tuple ('A',) is rendered as a subscript."""
    out, low = [], False
    for p in parts:
        if isinstance(p, tuple):
            out.append(f'<tspan font-size="72%" dy="3">{esc(p[0])}</tspan>')
            low = True
        else:
            out.append(f'<tspan dy="-3">{esc(p)}</tspan>' if low else esc(p))
            low = False
    return ''.join(out)


def rtext(S, x, y, markup, size=12.5, c=INK, anchor='middle', bold=False, halo=False):
    b = ' font-weight="bold"' if bold else ''
    h = (' stroke="#fff" stroke-width="4" paint-order="stroke" stroke-linejoin="round"'
         if halo else '')
    S.add(f'<text x="{f(x)}" y="{f(y)}" font-size="{size}" fill="{c}" text-anchor="{anchor}"{b}{h}>'
          f'{markup}</text>')


def udl(S, xa, xb, y, h=24, step=22, c=LOAD, w=1.4):
    n = max(2, int(round((xb - xa) / step)))
    yt = y - h
    S.line(xa, yt, xb, yt, c, w)
    for k in range(n + 1):
        x = xa + (xb - xa) * k / n
        S.arrow(x, yt, x, y - 3, c, w, L=7, W=3)
    return yt


def mdiag(S, P1, P2, func, L, k, nrm, c=BMD, n=90, op=0.16, w=1.8):
    """diagram of func(t), t∈[0,L] along member P1→P2; +value drawn toward screen vector nrm."""
    pts = []
    for i in range(n + 1):
        t = L * i / n
        v = func(t)
        x = P1[0] + (P2[0] - P1[0]) * i / n
        y = P1[1] + (P2[1] - P1[1]) * i / n
        pts.append((x + nrm[0] * k * v, y + nrm[1] * k * v))
    S.area([P1] + pts + [P2], c, op)
    S.pl(pts, c, w)
    S.line(*P1, *pts[0], c, w)
    S.line(*P2, *pts[-1], c, w)
    return pts


def integrate(Mfun, L, EI=1.0, n=4000, v0=0.0, t0=0.0):
    """EI v'' = M (sagging +, v up +).  returns xs, slope, v"""
    xs = [L * i / n for i in range(n + 1)]
    th, v = [t0], [v0]
    for i in range(1, n + 1):
        h = xs[i] - xs[i - 1]
        th.append(th[-1] + (Mfun(xs[i - 1]) + Mfun(xs[i])) / 2 * h / EI)
        v.append(v[-1] + (th[-2] + th[-1]) / 2 * h)
    return xs, th, v


def simpson(fn, a, b, n=2000):
    h = (b - a) / n
    s = fn(a) + fn(b)
    for i in range(1, n):
        s += (4 if i % 2 else 2) * fn(a + i * h)
    return s * h / 3


class Plot:
    def __init__(self, S, x0, y0, w, h, xr, yr, logy=False):
        self.S, self.x0, self.y0, self.w, self.h = S, x0, y0, w, h
        self.xr, self.yr, self.logy = xr, yr, logy

    def X(self, x):
        return self.x0 + (x - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, y):
        if self.logy:
            a, b = math.log10(self.yr[0]), math.log10(self.yr[1])
            return self.y0 + self.h - (math.log10(y) - a) / (b - a) * self.h
        return self.y0 + self.h - (y - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def P(self, x, y):
        return self.X(x), self.Y(y)

    def frame(self, xt=(), yt=(), xlab='', ylab='', grid=True):
        S = self.S
        for x, t in xt:
            if grid:
                S.line(self.X(x), self.y0, self.X(x), self.y0 + self.h, '#eceff1', 1)
            S.text(self.X(x), self.y0 + self.h + 16, t, 11, MUT)
        for y, t in yt:
            if grid:
                S.line(self.x0, self.Y(y), self.x0 + self.w, self.Y(y), '#eceff1', 1)
            S.text(self.x0 - 7, self.Y(y) + 4, t, 11, MUT, 'end')
        S.line(self.x0, self.y0 + self.h, self.x0 + self.w + 6, self.y0 + self.h, MUT, 1.6)
        S.line(self.x0, self.y0 + self.h, self.x0, self.y0 - 6, MUT, 1.6)
        S.head(self.x0 + self.w + 10, self.y0 + self.h, 0, MUT, 8, 3.5)
        S.head(self.x0, self.y0 - 10, -math.pi / 2, MUT, 8, 3.5)
        if xlab:
            S.text(self.x0 + self.w + 14, self.y0 + self.h + 4, xlab, 12, MUT, 'start')
        if ylab:
            S.text(self.x0, self.y0 - 16, ylab, 12, MUT, 'middle')

    def curve(self, fn, a, b, c=SFD, w=2.6, n=200, dash=None):
        pts = [self.P(a + (b - a) * i / n, fn(a + (b - a) * i / n)) for i in range(n + 1)]
        self.S.pl(pts, c, w, dash=dash)
        return pts


# ============ 範例 A：一端固定一端滾支承（w、L 正規化為 1） ============
def exA():
    """ξ 自固定端 A 量。回傳 M0、m、M（下緣受拉為正）與 R。"""
    R = Fr(3, 8)
    M0 = lambda s: -(1 - s) ** 2 / 2
    m = lambda s: (1 - s)
    M = lambda s: M0(s) + float(R) * m(s)
    # 最小功：∫ M m dξ = 0
    assert abs(simpson(lambda s: M(s) * m(s), 0, 1)) < 1e-12
    assert abs(M(0) + 1 / 8) < 1e-12 and abs(M(5 / 8) - 9 / 128) < 1e-12 and abs(M(0.25)) < 1e-12
    return M0, m, M, float(R)


# ---------------------------------------------------------------- 0-1
def fig_0_1():
    """缺口 Δ0 → 多餘力推回去；三條撓度曲線都是解析解、同一比例。"""
    S = SVG(900, 352, '力法骨架：拆束制、出缺口、推回去')
    S.text(450, 22, '力法家族的共同骨架（一端固定一端滾支承、全跨 w；三格撓度同一比例尺）', 14, TITLE, bold=True)
    D0 = 62.0                                    # px for Δ0 = wL⁴/8EI
    v0 = lambda s: -s * s * (6 - 4 * s + s * s) / 24 * 8     # /Δ0  (down −)
    vR = lambda s: s * s * (3 - s) / 6 * 3 * 8 / 8           # R=3wL/8 → tip = Δ0 (up +)
    va = lambda s: v0(s) + vR(s)
    assert abs(v0(1) + 1) < 1e-12 and abs(vR(1) - 1) < 1e-12 and abs(va(1)) < 1e-12
    # 真實撓度最大值 = wL⁴/185EI ≈ 0.0432 Δ0，位於距固定端 0.5785L
    xs = [i / 2000 for i in range(2001)]
    vmin = min(va(x) for x in xs)
    smin = xs[[va(x) for x in xs].index(vmin)]
    assert abs(-vmin / 8 - 1 / 184.6) < 2e-5 and abs(smin - 0.5785) < 2e-3

    panels = [(14, '#fafafa', '#cfd8dc', INK, '① 原結構：1 度靜不定'),
              (312, '#ffebee', '#ef9a9a', GAP, '② 拆掉 B 支承 → 出現缺口 Δ₀'),
              (610, '#e8f5e9', '#a5d6a7', GOOD, '③ 多餘力 X 把缺口推回去')]
    for k, (x0, bg, bd, col, title) in enumerate(panels):
        S.rect(x0, 38, 276, 232, bg, bd, 1, rx=10)
        S.text(x0 + 138, 60, title, 13.5, col, bold=True)
        xa, xb, y = x0 + 40, x0 + 244, 132
        Lp = xb - xa
        P = lambda s, v: (xa + Lp * s, y - D0 * v)
        S.wall(xa, y - 26, y + 26, side=-1)
        S.text(xa - 4, y - 32, 'A', 12, INK, 'end', bold=True)
        S.text(xb + 4, y - 32, 'B', 12, INK, 'start', bold=True)
        if k == 0:
            udl(S, xa, xb, y, 24)
            S.text(x0 + 138, 88, 'w', 12, LOAD, bold=True)
            S.line(xa, y, xb, y, INK, 4)
            S.roller(xb, y + 2, s=0.9)
            S.pl([P(s, va(s)) for s in xs[::20]], DEF, 2.2)
            S.text(x0 + 138, 206, '反力 4 個（A 三個＋B 一個）', 12, INK)
            S.text(x0 + 138, 225, '平衡方程只有 3 條', 12, INK)
            S.text(x0 + 138, 252, '藍線＝真實撓度（同比例）：最大僅 0.043 Δ₀', 11.5, DEF)
        elif k == 1:
            udl(S, xa, xb, y, 24)
            S.line(xa, y, xb, y, GHOST, 2, dash='5 4')
            S.roller(xb, y + 2, s=0.9, c=GHOST)
            pts = [P(s, v0(s)) for s in xs[::20]]
            S.pl(pts, GAP, 4)
            S.arrow(xb + 14, y, xb + 14, y + D0, GAP, 1.8, L=7, W=3)
            S.line(xb + 4, y, xb + 20, y, GAP, 1)
            S.line(xb + 4, y + D0, xb + 20, y + D0, GAP, 1)
            S.text(xb + 4, y + D0 + 18, 'Δ₀', 14, GAP, 'end', bold=True)
            rtext(S, x0 + 138, 225, rich('Δ', ('0',), ' = wL⁴ / 8EI（懸臂端撓度）'), 12, GAP)
            S.text(x0 + 138, 252, '基本結構＝懸臂梁，靜定可直接算', 11.5, GAP)
        else:
            S.line(xa, y, xb, y, GHOST, 2, dash='5 4')
            S.pl([P(s, v0(s)) for s in xs[::20]], GAP, 1.5, dash='4 3', op=0.6)
            S.pl([P(s, va(s)) for s in xs[::20]], GOOD, 4)
            S.arrow(xb, y + D0 + 10, xb, y + 6, GOOD, 3)
            S.text(xb - 8, y + D0 + 4, 'X', 14, GOOD, 'end', bold=True)
            rtext(S, x0 + 138, 225, rich('δ', ('11',), 'X = (L³/3EI)·X 正好抵銷 Δ', ('0',)), 12, GOOD)
            S.text(x0 + 138, 252, '⟹ X = 3wL/8（綠粗線＝疊加後）', 11.5, GOOD, bold=True)
    S.text(301, 160, '→', 22, MUT, bold=True)
    S.text(599, 160, '→', 22, MUT, bold=True)
    S.rect(110, 284, 680, 54, '#e3f2fd', '#90caf9', 1.6, rx=9)
    rtext(S, 450, 306, rich('B 點位移 = −Δ', ('0',), ' + δ', ('11',), 'X = 0　⟺　∂U/∂X = 0'), 14, TITLE, bold=True)
    rtext(S, 450, 327, rich('X = Δ', ('0',), ' / δ', ('11',), ' = (wL⁴/8EI) ÷ (L³/3EI) = 3wL/8'), 12.5, TITLE)
    return S.render()


# ---------------------------------------------------------------- 0-2
def fig_0_2():
    """U(X) 的真實拋物線：斜率 = B 點（沿 X 方向）位移。"""
    U = lambda X: X * X / 6 - X / 8 + 1 / 40              # × w²L⁵/EI，X × wL
    dU = lambda X: X / 3 - 1 / 8                            # × wL⁴/EI
    # 用積分重算一次 U(X)（防止上式抄錯）
    for X in (0, 0.2, 0.375, 0.7):
        Ui = simpson(lambda s: (X * s - s * s / 2) ** 2 / 2, 0, 1)
        assert abs(Ui - U(X)) < 1e-12
    assert abs(U(3 / 8) - 1 / 640) < 1e-12
    S = SVG(900, 330, '應變能 U(X) 是開口向上的拋物線')
    S.text(450, 22, '範例 A 的 U(X)（依公式畫，不是示意）：切線斜率 = B 點沿 X 方向的位移', 14, TITLE, bold=True)
    pl = Plot(S, 92, 56, 400, 220, (-0.05, 0.85), (0, 0.04))
    pl.frame(xt=[(0, '0'), (0.25, '0.25'), (0.375, '3/8'), (0.5, '0.5'), (0.75, '0.75')],
             yt=[(0, '0'), (0.01, '0.01'), (0.02, '0.02'), (0.03, '0.03'), (0.04, '0.04')],
             xlab='X / wL', ylab='U ÷ (w²L⁵/EI)')
    pl.curve(U, -0.05, 0.85, SFD, 3.2)
    for X0, col, lab, anc, dy in ((0, GAP, '斜率 −wL⁴/8EI：B 下垂 Δ₀', 'start', -10),
                                 (0.375, GOOD, '斜率 0：B 不動 ⟹ 真實解', 'middle', -62),
                                 (0.75, ORG, '斜率 +wL⁴/8EI：推過頭', 'end', -10)):
        a, b = X0 - 0.11, X0 + 0.11
        S.line(*pl.P(a, U(X0) + dU(X0) * (a - X0)), *pl.P(b, U(X0) + dU(X0) * (b - X0)), col, 2)
        S.circ(*pl.P(X0, U(X0)), 5, col, '#fff', 1.5)
        x, y = pl.P(X0, U(X0))
        S.halo(x + (8 if anc == 'start' else -8 if anc == 'end' else 0), y + dy, lab, 11.5, col, anc, bold=True)
    S.line(*pl.P(0.375, U(0.375)), pl.X(0.375), pl.Y(0), GOOD, 1, dash='3 3')
    S.halo(pl.X(0.375) + 10, pl.Y(0.0016) + 2, 'U_min = w²L⁵/640EI', 11, GOOD, 'start')
    S.line(pl.X(0.375), pl.Y(U(0.375)) - 8, pl.X(0.375), pl.Y(U(0.375)) - 50, GOOD, 1, dash='2 2')
    # right panel
    S.rect(576, 52, 312, 226, '#f3e5f5', '#ce93d8', 1, rx=9)
    S.text(732, 76, '把 M = −wx²/2 + X·x 代進 U', 12.5, MOM, bold=True)
    rtext(S, 732, 102, rich('U(X) = ', 'L³', '/6EI · X²  −  wL⁴/8EI · X  +  w²L⁵/40EI'), 11.5, MOM)
    S.text(732, 130, '二次項係數 ∫m²/2EI dx = L³/6EI > 0', 12, MOM)
    S.text(732, 150, '⟹ 開口一定向上，駐點一定是最小值', 12, MOM, bold=True)
    rtext(S, 732, 182, rich('∂U/∂X = δ', ('11',), 'X − Δ', ('0',)), 13, MOM, bold=True)
    S.text(732, 204, '＝ B 點「沿 X 方向（向上）」的位移', 12, MOM)
    S.text(732, 232, '所以「令 ∂U/∂X = 0」就是', 12, MOM)
    S.text(732, 252, '「B 點不准動」，最小是副產品', 12.5, MOM, bold=True)
    S.text(306, 318, '橫軸以 wL 為單位、縱軸以 w²L⁵/EI 為單位；三條切線的斜率與 B 點位移逐一對應', 11.5, MUT)
    return S.render()


# ---------------------------------------------------------------- 1-1
def fig_1_1():
    S = SVG(900, 318, '力—位移圖：應變能與餘能')
    S.text(450, 22, '力—位移圖：曲線「下方」是應變能 U，「左方」是餘能 U*', 14, TITLE, bold=True)
    pl = Plot(S, 86, 50, 360, 220, (0, 1.25), (0, 1.25))
    pl.frame(xlab='Δ', ylab='P')
    d = 0.09
    S.area([pl.P(0, 0), pl.P(1, 0), pl.P(1, 1)], SFD, 0.16)
    S.area([pl.P(0, 0), pl.P(0, 1), pl.P(1, 1)], ORG, 0.16)
    S.area([pl.P(1, 0), pl.P(1 + d, 0), pl.P(1 + d, 1 + d), pl.P(1, 1)], SFD, 0.55)
    S.area([pl.P(0, 1), pl.P(0, 1 + d), pl.P(1 + d, 1 + d), pl.P(1, 1)], ORG, 0.55)
    S.line(*pl.P(0, 0), *pl.P(1.2, 1.2), INK, 3)
    S.text(pl.X(1.2) + 4, pl.Y(1.2) - 2, 'P = kΔ', 12, INK, 'start', bold=True)
    S.halo(pl.X(0.72), pl.Y(0.24), 'U = ½PΔ', 13, SFD, bold=True)
    S.halo(pl.X(0.28), pl.Y(0.78), 'U* = ½PΔ', 13, ORG, bold=True)
    S.line(pl.X(1), pl.Y(0), pl.X(1), pl.Y(1), MUT, 1, dash='3 3')
    S.line(pl.X(0), pl.Y(1), pl.X(1), pl.Y(1), MUT, 1, dash='3 3')
    S.text(pl.X(1), pl.Y(0) + 16, 'Δ', 11.5, MUT)
    S.text(pl.X(0) - 7, pl.Y(1) + 4, 'P', 11.5, MUT, 'end')
    S.halo(pl.X(1 + d) + 6, pl.Y(0.45), 'dU = P·dΔ', 12, SFD, 'start', bold=True)
    S.halo(pl.X(0.45), pl.Y(1 + d) - 8, 'dU* = Δ·dP', 12, '#e65100', bold=True)
    # right box
    S.rect(486, 48, 400, 224, '#f3e5f5', '#ce93d8', 1, rx=9)
    x = 504
    S.text(686, 72, '卡氏第二定理的兩行推導', 13, MOM, bold=True)
    S.text(x, 100, '① 線彈性：U = ½kΔ² = P²/2k', 12.5, MOM, 'start')
    S.text(x, 124, '② 對 P 偏微分：∂U/∂P = P/k = Δ', 12.5, MOM, 'start', bold=True)
    S.text(x, 156, '嚴格版本是 Δ = ∂U*/∂P（橘色長條 Δ·dP）。', 12, MOM, 'start')
    S.text(x, 176, '線彈性時兩塊三角形一樣大（U = U*），', 12, MOM, 'start')
    S.text(x, 196, '所以可以直接拿 U 來微分。', 12, MOM, 'start')
    S.text(x, 226, '一旦降伏、挫曲（曲線彎掉）U ≠ U*：', 12, LOAD, 'start', bold=True)
    S.text(x, 246, '只能在每個線彈性階段內各自使用 → SA-2019-1', 12, LOAD, 'start')
    S.text(450, 304, '藍色長條 P·dΔ 是「力做的功」的增量；橘色長條 Δ·dP 才是「對 P 微分」量到的東西', 11.5, MUT)
    return S.render()


# ---------------------------------------------------------------- 2-2
def fig_2_2():
    """M = M0 + X·m 的疊加，三張圖同一比例（範例 A）。"""
    M0, m, M, R = exA()
    S = SVG(900, 292, '彎矩疊加 M = M0 + X·m')
    S.text(450, 22, '範例 A 的彎矩疊加（同一比例，畫在受拉側：上方＝上緣受拉）', 14, TITLE, bold=True)
    k = 128.0                                   # px per wL²
    titles = [rich('M', ('0',), '：基本結構（懸臂）只受 w'),
              rich('X·m：X = 3wL/8 作用在 B'),
              rich('M = M', ('0',), ' + X·m：真實彎矩')]
    funcs = [M0, lambda s: R * m(s), M]
    cols = [GAP, GOOD, SFD]
    for j in range(3):
        x0 = 30 + j * 295
        xa, xb, y = x0 + 20, x0 + 230, 158
        rtext(S, x0 + 125, 58, titles[j], 12.5, cols[j], bold=True)
        mdiag(S, (xa, y), (xb, y), funcs[j], 1.0, k, (0, 1), cols[j])
        S.line(xa, y, xb, y, INK, 3.4)
        S.wall(xa, y - 20, y + 20, side=-1)
        S.text(xa - 6, y + 34, 'A', 11.5, INK, 'end', bold=True)
        S.text(xb + 6, y + 4, 'B', 11.5, INK, 'start', bold=True)
        if j == 0:
            S.halo(xa + 6, y - k / 2 - 6, '−wL²/2', 12, GAP, 'start', bold=True)
        elif j == 1:
            S.halo(xa + 6, y + k * R + 16, '+3wL²/8', 12, GOOD, 'start', bold=True)
            S.arrow(xb, y + 40, xb, y + 6, GOOD, 2.6)
            S.text(xb - 6, y + 40, 'X', 12, GOOD, 'end', bold=True)
        else:
            S.halo(xa + 6, y - k / 8 - 6, '−wL²/8', 12, SFD, 'start', bold=True)
            S.halo(xa + (xb - xa) * 5 / 8, y + k * 9 / 128 + 16, '+9wL²/128', 12, SFD, bold=True)
            S.circ(xa + (xb - xa) * 0.25, y, 3.5, ORG, ORG, 1)
            S.halo(xa + (xb - xa) * 0.25, y - 10, '反曲點 L/4', 10.5, ORG)
        if j < 2:
            S.text(x0 + 268, y + 6, '+' if j == 0 else '=', 24, MUT, bold=True)
    S.rect(140, 232, 620, 48, '#f3e5f5', '#ba68c8', 1.4, rx=9)
    S.text(450, 252, '中間那張是 X × m，m 是「X = 1 時」的彎矩圖（三角形，B 端 0、A 端 L）', 12, MOM)
    S.text(450, 272, '所以 M 對 X 微分，剩下的就是 m：∂M/∂X ≡ m', 13, MOM, bold=True)
    return S.render()


# ---------------------------------------------------------------- 3-1
def fig_3_1():
    S = SVG(900, 300, '軸向應變能佔彎曲應變能的比例')
    S.text(450, 22, '細長桿件可放心丟掉軸向項：U軸 / U彎 ≈ ¼(h/L)²（矩形斷面、懸臂端受力）', 14, TITLE, bold=True)
    pl = Plot(S, 96, 50, 440, 200, (1, 30), (0.01, 100), logy=True)
    pl.frame(xt=[(1, '1'), (3, '3'), (5, '5'), (10, '10'), (15, '15'), (20, '20'), (25, '25'), (30, '30')],
             yt=[(0.01, '0.01%'), (0.1, '0.1%'), (1, '1%'), (10, '10%'), (100, '100%')],
             xlab='L / h', ylab='U軸 / U彎')
    S.rect(pl.X(8), pl.y0, pl.X(25) - pl.X(8), pl.h, GOOD, 'none', 0, op=0.08)
    S.text((pl.X(8) + pl.X(25)) / 2, pl.y0 + 16, '一般梁、柱、剛架', 11.5, GOOD, bold=True)
    S.rect(pl.X(1), pl.y0, pl.X(3) - pl.X(1), pl.h, LOAD, 'none', 0, op=0.08)
    S.text(pl.X(3) + 6, pl.y0 + pl.h - 10, '← 深梁／短柱：軸向不可略', 11.5, LOAD, 'start', bold=True)
    r = lambda a: 25 / (a * a)
    assert abs(r(10) - 0.25) < 1e-12
    pl.curve(r, 1, 30, SFD, 3)
    for a, lab in ((1, '25%'), (3, '2.8%'), (10, '0.25%'), (20, '0.06%')):
        S.circ(*pl.P(a, r(a)), 4.5, SFD, '#fff', 1.4)
        S.halo(pl.X(a) + 8, pl.Y(r(a)) - 6, lab, 11.5, SFD, 'start', bold=True)
    S.rect(596, 50, 290, 200, '#f3e5f5', '#ce93d8', 1, rx=9)
    S.text(741, 74, '算一次就記住', 13, MOM, bold=True)
    S.text(612, 100, 'U軸 = P²L/2EA，U彎 = P²L³/6EI', 12, MOM, 'start')
    S.text(612, 122, '比值 = 3I/(AL²) = 3(r/L)²', 12, MOM, 'start')
    S.text(612, 144, '矩形 r = h/√12 ⟹ ≈ ¼(h/L)²', 12, MOM, 'start')
    S.text(612, 176, '剛架：只留彎曲項', 12.5, GOOD, 'start', bold=True)
    S.text(612, 198, '桁架：根本沒有彎矩，只剩軸向', 12.5, SFD, 'start', bold=True)
    S.text(612, 220, '兩者都給（EI、EA）：兩項都算', 12.5, LOAD, 'start', bold=True)
    S.text(330, 288, '縱軸為對數刻度。L/h = 10 時軸向能量只佔 0.25%，這就是「只給 EI」的題目在暗示你的事', 11.5, MUT)
    return S.render()


# ---------------------------------------------------------------- 4-1
def fig_4_1():
    """三題的靜不定度實際數法（依比例）。"""
    S = SVG(900, 330, '靜不定度：三題的實際數法')
    S.text(450, 22, '數靜不定度：把反力一個一個畫出來再數（三題皆依比例）', 14, TITLE, bold=True)
    boxes = [(12, 'SA-2005-1　斜桿剛架'), (310, 'SA-2013-2　L 型剛架'), (608, 'SA-2017-2　兩端固定＋內鉸')]
    for x0, t in boxes:
        S.rect(x0, 36, 282, 284, '#fafafa', '#cfd8dc', 1, rx=10)
        S.text(x0 + 141, 58, t, 13, TITLE, bold=True)
    # ① SA-2005-1 : B(0,4) A(8,4) C(4,0)
    W = World(52, 196, 24)
    B, A, C = W(0, 4), W(8, 4), W(4, 0)
    S.line(*B, *A, INK, 3.5); S.line(*B, *C, INK, 3.5)
    S.wall(A[0], A[1] - 20, A[1] + 20, side=1)
    S.roller(*C, s=0.85)
    S.arrow(B[0], B[1] - 40, B[0], B[1] - 4, LOAD, 2.6)
    S.text(B[0] + 6, B[1] - 30, '10 N', 11.5, LOAD, 'start', bold=True)
    for p, t, dx, dy in ((B, 'B', -8, 4), (A, 'A', 10, -12), (C, 'C', 14, 2)):
        S.text(p[0] + dx, p[1] + dy, t, 12, INK, 'end' if dx < 0 else 'start', bold=True)
    S.arrow(A[0] + 52, A[1], A[0] + 22, A[1], REAC, 2.2)
    S.arrow(A[0] + 30, A[1] + 34, A[0] + 30, A[1] + 8, REAC, 2.2)
    S.moment(A[0] + 2, A[1] - 26, 11, ccw=True, c=REAC, a0=-30, span=240)
    S.arrow(C[0], C[1] + 54, C[0], C[1] + 30, REAC, 2.2)
    S.text(A[0] + 26, A[1] + 50, 'A：3', 12, REAC, bold=True)
    S.text(C[0] + 10, C[1] + 50, 'C：1', 12, REAC, 'start', bold=True)
    S.text(153, 286, '4 個反力 − 3 條平衡 ＝ 1 度', 13, INK, bold=True)
    S.text(153, 306, '多餘力選 C 點反力 R_C', 11.5, MUT)
    # ② SA-2013-2 : A(0,0) B(0,10) C(10,10)
    W = World(372, 262, 15)
    A, B, C, Mid = W(0, 0), W(0, 10), W(10, 10), W(5, 10)
    S.line(*A, *B, INK, 3.5); S.line(*B, *C, INK, 3.5)
    S.fixed(*A, s=1.0)
    S.pin(*C, s=0.85)
    S.arrow(Mid[0], Mid[1] - 36, Mid[0], Mid[1] - 4, LOAD, 2.6)
    S.text(Mid[0] + 6, Mid[1] - 26, '20 kN', 11.5, LOAD, 'start', bold=True)
    for p, t, dx, dy in ((A, 'A', -12, 0), (B, 'B', -8, -6), (C, 'C', 8, -8)):
        S.text(p[0] + dx, p[1] + dy, t, 12, INK, 'end' if dx < 0 else 'start', bold=True)
    S.arrow(A[0] - 46, A[1] - 40, A[0] - 5, A[1] - 40, REAC, 2.2)
    S.arrow(A[0] + 26, A[1] + 2, A[0] + 26, A[1] - 30, REAC, 2.2)
    S.moment(A[0], A[1], 18, ccw=True, c=REAC, a0=100, span=150)
    S.arrow(C[0] + 46, C[1] + 8, C[0] + 14, C[1] + 8, REAC, 2.2)
    S.arrow(C[0], C[1] + 62, C[0], C[1] + 30, REAC, 2.2)
    S.text(A[0] + 34, A[1] - 22, 'A：3', 12, REAC, 'start', bold=True)
    S.text(C[0] + 12, C[1] + 56, 'C：2', 12, REAC, 'start', bold=True)
    S.text(451, 300, '5 − 3 ＝ 2 度 → 解聯立', 13, INK, bold=True)
    # ③ SA-2017-2 : a(0) c(6) b(10)
    W = World(640, 176, 22)
    a, c, b = W(0, 0), W(6, 0), W(10, 0)
    udl(S, a[0], b[0], a[1], 22, 18)
    S.text(W.X(5), a[1] - 30, 'w', 12, LOAD, bold=True)
    S.line(*a, *b, INK, 3.5)
    S.wall(a[0], a[1] - 22, a[1] + 22, side=-1); S.wall(b[0], b[1] - 22, b[1] + 22, side=1)
    S.hinge(*c, 5.5, MOM)
    S.text(c[0], c[1] + 20, 'c', 12, MOM, bold=True)
    for p, s_ in ((a, 1), (b, -1)):
        S.arrow(p[0] + 16 * s_, p[1] + 36, p[0] + 16 * s_, p[1] + 10, REAC, 2.2)
        S.moment(p[0], p[1], 15, ccw=(s_ > 0), c=REAC, a0=(250 if s_ > 0 else -70), span=120)
        S.arrow(p[0] - 30 * s_, p[1] - 30, p[0] - 6 * s_, p[1] - 30, GHOST, 2, dash='3 2')
    S.text(a[0] - 18, a[1] - 38, 'H_a', 11, GHOST, 'middle')
    S.text(b[0] + 18, b[1] - 38, 'H_b', 11, GHOST, 'middle')
    S.text(749, 240, '反力 6 − 平衡 3 − 鉸 M_c = 0 ＝ 2 度', 12, INK)
    S.text(749, 260, '但水平那 1 度與彎曲解耦', 11, MUT)
    S.text(749, 276, '（只有垂直載重 ⟹ H_a = H_b = 0）', 11, MUT)
    S.text(749, 300, '真正要解的：1 度', 13.5, LOAD, bold=True)
    S.text(749, 315, '內鉸只送 1 條方程，沒有送你靜定', 11, LOAD)
    return S.render()


# ---------------------------------------------------------------- 4-2
def fig_4_2():
    """SA-2017-2 兩種多餘力選法（依比例：m = 6、n = 4）。"""
    S = SVG(900, 340, 'SA-2017-2 兩種多餘力選法')
    S.text(450, 22, 'SA-2017-2（依比例 m : n = 6 : 4）：兩種多餘力選法，答案相同、代數量差很多', 14, TITLE, bold=True)
    S.rect(12, 38, 432, 290, '#ffebee', '#ef9a9a', 1, rx=10)
    S.rect(456, 38, 432, 290, '#e8f5e9', '#a5d6a7', 1, rx=10)
    rtext(S, 228, 62, rich('選法 A：釋放 a 端轉動束制，取 M', ('a',), ' = X'), 13, GAP, bold=True)
    rtext(S, 672, 62, rich('選法 B：切開內鉸，取鉸處剪力 V'), 13, GOOD, bold=True)
    # --- A
    W = World(58, 150, 34)
    a, c, b = W(0, 0), W(6, 0), W(10, 0)
    udl(S, a[0], b[0], a[1], 22, 17)
    S.line(*a, *b, INK, 3.5)
    S.pin(*a, s=0.9)
    S.wall(b[0], b[1] - 22, b[1] + 22, side=1)
    S.hinge(*c, 5.5)
    S.moment(a[0], a[1], 17, ccw=True, c=MOM, a0=200, span=230)
    rtext(S, a[0] - 4, a[1] - 26, rich('X = M', ('a',)), 12, MOM, 'end', bold=True)
    S.text(a[0], a[1] + 40, 'a', 12, INK, bold=True); S.text(c[0], c[1] + 22, 'c', 12, INK, bold=True)
    S.text(b[0] - 6, b[1] + 38, 'b', 12, INK, 'end', bold=True)
    y = 214
    for t, col, bd in (('基本結構：a 鉸、c 內鉸、b 固定 → 穩定 ✔', GAP, False),
                       ('左段 M = R_a·x + X − wx²/2，R_a = wm/2 − X/m', GAP, False),
                       ('∂M/∂X = 1 − x/m；右段還要先由平衡求 R_b、M_b', GAP, False),
                       ('每段 3～4 項，偏微分後再相乘，符號極易出錯', GAP, True)):
        S.text(228, y, t, 12, col, bold=bd); y += 24
    S.text(228, 316, '能算，但代數量大', 12.5, GAP, bold=True)
    # --- B
    W = World(502, 150, 34)
    a, c, b = W(0, 0), W(6, 0), W(10, 0)
    g = 9
    udl(S, a[0], c[0] - g, a[1], 22, 17)
    udl(S, c[0] + g, b[0], a[1], 22, 17)
    S.line(a[0], a[1], c[0] - g, c[1], INK, 3.5)
    S.line(c[0] + g, c[1], b[0], b[1], INK, 3.5)
    S.wall(a[0], a[1] - 22, a[1] + 22, side=-1)
    S.wall(b[0], b[1] - 22, b[1] + 22, side=1)
    S.arrow(c[0] - g, c[1] + 40, c[0] - g, c[1] + 5, GOOD, 2.6)
    S.arrow(c[0] + g, c[1] - 38, c[0] + g, c[1] - 5, GOOD, 2.6)
    S.text(c[0] - g - 6, c[1] + 40, 'V', 13, GOOD, 'end', bold=True)
    S.text(c[0] + g + 6, c[1] - 30, 'V', 13, GOOD, 'start', bold=True)
    S.text(a[0], a[1] + 40, 'a', 12, INK, bold=True)
    S.text(b[0], b[1] + 40, 'b', 12, INK, bold=True)
    S.arrow(c[0] - g - 4, c[1] + 58, a[0] + 6, a[1] + 58, MUT, 1, L=6, W=2.6)
    S.text((a[0] + c[0]) / 2, a[1] + 54, 'x（自 c 向左）', 11, MUT)
    S.arrow(c[0] + g + 4, c[1] + 58, b[0] - 6, b[1] + 58, MUT, 1, L=6, W=2.6)
    S.text((b[0] + c[0]) / 2 + 6, a[1] + 54, 'ξ（自 c 向右）', 11, MUT)
    y = 238
    for t, bd in (('左右各自是一根懸臂梁（靜定 ✔）', False),
                  ('左：M = Vx − wx²/2，∂M/∂V = x', False),
                  ('右：M = −Vξ − wξ²/2，∂M/∂V = −ξ', False)):
        S.text(672, y, t, 12, GOOD, bold=bd); y += 24
    S.text(672, 316, '每段只有兩項 → 代數量少一半以上（§10 示範）', 12.5, GOOD, bold=True)
    return S.render()


# ---------------------------------------------------------------- 5-1
def sa2005_1():
    """SA-2005-1：以最小功條件重算 R_C（回傳 R_C 與兩桿彎矩函數，外側受拉取正）。"""
    r2 = math.sqrt(2)

    def g(Rc):
        bc = simpson(lambda s: (Rc * s / r2) * (s / r2), 0, 4 * r2)
        ba = simpson(lambda x: ((Rc - 10) * x - 4 * Rc) * (x - 4), 0, 8)
        return bc + ba
    Rc = -g(0) / (g(1) - g(0))
    assert abs(Rc - (20 - 10 * r2)) < 1e-9
    Mbc = lambda s: Rc * s / r2                      # 外側（左下）受拉
    Mba = lambda x: -((Rc - 10) * x - 4 * Rc)        # 上緣受拉取正（解析式的負號）
    assert abs(Mbc(4 * r2) - 40 * (2 - r2)) < 1e-9 and abs(Mba(8) - 40 * r2) < 1e-9
    return Rc, Mbc, Mba


def fig_5_1():
    Rc, Mbc, Mba = sa2005_1()
    r2 = math.sqrt(2)
    S = SVG(900, 370, 'SA-2005-1 自由體圖陷阱')
    S.text(450, 22, 'SA-2005-1（依比例）：BA 桿為什麼不必在 x = 4 分段', 14, TITLE, bold=True)
    # ---- left: FBD at x = 2
    W = World(66, 272, 40)
    B, A, C = W(0, 4), W(8, 4), W(4, 0)
    xc = 2.0
    K = W(xc, 4)
    S.area([(B[0] - 14, B[1] - 14), (K[0], K[1] - 14), (K[0], K[1] + 14),
            (C[0] + 18, C[1] + 6), (C[0] - 16, C[1] + 22), (B[0] - 14, B[1] + 10)], GOOD, 0.10)
    S.line(*K, *A, GHOST, 3.5)
    S.wall(A[0], A[1] - 20, A[1] + 20, side=1, c=GHOST)
    S.line(*B, *K, GOOD, 4.5); S.line(*B, *C, GOOD, 4.5)
    S.roller(*C, s=0.85)
    S.line(K[0], K[1] - 40, K[0], K[1] + 40, LOAD, 2, dash='6 4')
    S.text(K[0], K[1] - 46, '切在 x = 2', 11.5, LOAD, bold=True)
    S.arrow(B[0], B[1] - 46, B[0], B[1] - 4, LOAD, 2.8)
    S.text(B[0] + 6, B[1] - 34, '10 N', 12, LOAD, 'start', bold=True)
    S.arrow(C[0], C[1] + 62, C[0], C[1] + 34, REAC, 2.8)
    rtext(S, C[0] + 10, C[1] + 58, rich('R', ('C',), ' = 20 − 10√2 = ' + f'{Rc:.2f} N'), 12, REAC, 'start', bold=True)
    S.line(C[0], C[1] - 4, C[0], B[1] + 6, REAC, 1.2, dash='3 3')
    S.text(C[0] + 6, W.Y(2.6), 'R_C 作用線（x = 4）', 11, REAC, 'start')
    S.dim(*W(0, 4), *W(2, 4), 'x', off=-24)
    S.dim(*W(2, 4), *W(4, 4), '4 − x', off=-24)
    for p, t, dx, dy in ((B, 'B', -10, 4), (A, 'A', 12, -8), (C, 'C', -14, 4)):
        S.text(p[0] + dx, p[1] + dy, t, 12.5, INK, 'end' if dx < 0 else 'start', bold=True)
    S.rect(18, 304, 420, 60, '#e8f5e9', '#a5d6a7', 1, rx=8)
    S.text(228, 326, '綠色＝左側自由體：整根 BC 桿永遠在裡面（不論 x < 4 或 x > 4）', 11.5, GOOD, bold=True)
    S.text(228, 348, 'M(x) = −10x + R_C (x − 4)　0 ≤ x ≤ 8 一條式子；x < 4 時力臂只是變負', 11.5, GOOD)
    # ---- right: BMD (tension side), to scale
    W = World(510, 286, 40)
    B, A, C = W(0, 4), W(8, 4), W(4, 0)
    k = 0.85
    S.text(675, 52, '彎矩圖（N·m，畫在受拉側）', 13, TITLE, bold=True)
    pa = mdiag(S, B, A, Mba, 8, k, (0, -1))
    pc = mdiag(S, C, B, Mbc, 4 * r2, k, (-1 / r2, 1 / r2))
    S.line(*B, *A, INK, 3.2); S.line(*B, *C, INK, 3.2)
    S.wall(A[0], A[1] - 20, A[1] + 20, side=1); S.roller(*C, s=0.8)
    S.halo(pa[0][0] - 4, pa[0][1] - 4, f'{Mba(0):.2f}', 12, BMD, 'end', bold=True)
    S.halo(pa[-1][0] - 6, pa[-1][1] - 6, f'{Mba(8):.2f}', 12, BMD, 'end', bold=True)
    S.halo(pc[-1][0] - 6, pc[-1][1] + 14, f'{Mbc(4 * r2):.2f}', 12, BMD, 'end', bold=True)
    S.text(C[0] - 12, C[1] + 4, '0', 12, BMD, 'end', bold=True)
    x4 = W.X(4)
    S.line(x4, B[1] + 16, x4, pa[45][1], ORG, 1.2, dash='3 3')
    S.halo(x4, B[1] + 30, 'x = 4：沒有轉折', 11.5, ORG, bold=True)
    S.text(W.X(6.4), B[1] + 52, 'BA：上緣受拉、一直線', 11, BMD)
    S.text(C[0] - 96, W.Y(1.4), 'BC：外側受拉', 11, BMD, 'end')
    S.text(675, 332, '節點 B 兩桿彎矩相等（23.43）＝ 節點彎矩平衡', 11.5, MUT)
    S.text(675, 352, '若在 x = 4 硬分段，第二段的式子其實和第一段一模一樣', 11.5, MUT)
    return S.render()


# ---------------------------------------------------------------- 6-1
def sa2014_4():
    """SA-2014-4：R、彎矩函數（x 自 C 向左，下緣受拉為正）、撓度。"""
    def M(x, R, Mb=0.0):
        return R * x + Mb - (20 * (x - 6) if x > 6 else 0)
    g = lambda R: simpson(lambda x: M(x, R) * x, 0, 6) + simpson(lambda x: M(x, R) * x, 6, 12)
    R = -g(0) / (g(1) - g(0))
    assert abs(R - 6.25) < 1e-9
    EI = 1000.0
    th = (simpson(lambda x: M(x, R), 0, 6) + simpson(lambda x: M(x, R), 6, 12)) / EI
    assert abs(th - 0.09) < 1e-9
    # 撓度：ξ 自 A 量，A 固定
    xs, sl, v = integrate(lambda s: M(12 - s, R), 12, EI)
    assert abs(v[-1]) < 1e-4 and abs(sl[-1] - 0.09) < 1e-4
    return R, (lambda x: M(x, R)), xs, sl, v


def fig_6_1():
    R, Mx, xs, sl, v = sa2014_4()
    S = SVG(900, 430, 'SA-2014-4 虛擬彎矩、彎矩圖與變形')
    S.text(450, 22, 'SA-2014-4（依比例）：多餘力 R、虛擬彎矩 M̄ 放在 C，求 θ_C', 14, TITLE, bold=True)
    heads = [(12, '① 多餘力與虛擬量'), (310, '② 彎矩圖（kN·m，受拉側）'), (608, '③ 變形（位移放大 4 倍）')]
    for x0, t in heads:
        S.rect(x0, 36, 282, 386, '#fafafa', '#cfd8dc', 1, rx=10)
        S.text(x0 + 141, 58, t, 13, TITLE, bold=True)

    def frame(ox, ghost=False):
        W = World(ox, 128, 14)
        A, B, C, D = W(0, 0), W(6, 0), W(12, 0), W(12, -12)
        col = GHOST if ghost else INK
        S.line(*A, *C, col, 3.4); S.line(*C, *D, col, 3.4)
        S.wall(A[0], A[1] - 18, A[1] + 18, side=-1)
        S.roller(*D, s=0.85)
        return W, A, B, C, D
    # ①
    W, A, B, C, D = frame(46)
    S.arrow(B[0], B[1] - 40, B[0], B[1] - 4, LOAD, 2.8)
    S.text(B[0] + 6, B[1] - 30, '20 kN', 12, LOAD, 'start', bold=True)
    S.arrow(D[0] - 24, D[1] + 26, D[0] - 24, D[1] - 10, REAC, 2.8)
    S.text(D[0] - 30, D[1] + 22, 'R', 13, REAC, 'end', bold=True)
    S.moment(C[0], C[1], 15, ccw=True, c=MOM, a0=-60, span=250)
    S.text(C[0] + 14, C[1] - 18, 'M̄', 14, MOM, 'start', bold=True)
    for p, t, dx, dy in ((A, 'A', 0, -24), (B, 'B', 0, 20), (C, 'C', -14, 20), (D, 'D', 22, 4)):
        S.text(p[0] + dx, p[1] + dy, t, 12, INK, 'end' if dx < 0 else 'middle', bold=True)
    S.text(W.X(3), A[1] + 20, 'EI', 11, MUT); S.text(W.X(12) + 10, W.Y(-6), '2EI', 11, MUT, 'start')
    S.rect(22, 330, 262, 84, '#fff3e0', '#ffcc80', 1, rx=8)
    S.text(153, 350, 'D 是水平面上的滾支承 ⟹ D_x = 0', 11.5, '#e65100', bold=True)
    S.text(153, 370, '柱上任一斷面：M = R × 0 = 0', 11.5, '#e65100')
    S.text(153, 390, '⟹ U_CD = 0，2EI 從頭到尾用不到', 11.5, '#e65100', bold=True)
    S.text(153, 408, 'M̄ 只進入 AC 梁：∂M/∂M̄ = 1', 11, MUT)
    # ②
    W, A, B, C, D = frame(344)
    k = 0.95
    pts = mdiag(S, C, A, Mx, 12, k, (0, 1))
    S.line(*A, *C, INK, 3.4)
    xz = 120 / 13.75             # zero: 6.25x − 20(x−6) = 0 → x = 8.727（自 C）
    assert abs(Mx(xz)) < 1e-9
    S.halo(B[0], B[1] + k * 37.5 + 16, '+37.5', 12, BMD, bold=True)
    S.halo(A[0] + 6, A[1] - k * 45 - 6, '−45', 12, BMD, 'start', bold=True)
    S.circ(W.X(12 - xz), A[1], 3.5, ORG, ORG, 1)
    S.halo(W.X(12 - xz) + 4, A[1] - 10, f'反曲點 距 A {12 - xz:.3f} m', 10.5, ORG, 'start')
    S.text(C[0] + 8, W.Y(-6), 'M ≡ 0', 13, GOOD, 'start', bold=True)
    S.rect(320, 330, 262, 84, '#e3f2fd', '#90caf9', 1, rx=8)
    S.text(451, 350, '∂U/∂R = 0 ⟹ 576R − 3600 = 0', 11.5, TITLE)
    S.text(451, 370, 'R = 6.25 kN（↑）', 12.5, TITLE, bold=True)
    S.text(451, 392, 'θ_C = ∫M·1 dx / EI = (450 − 360)/EI', 11.5, TITLE)
    S.text(451, 410, '= 90/EI = 0.09 rad（逆時針）', 12, TITLE, bold=True)
    # ③ deflected shape, magnified
    W, A, B, C, D = frame(642, ghost=True)
    mag = 4.0
    pts = [(W.X(x), W.Y(mag * vv)) for x, vv in list(zip(xs, v))[::40]]
    S.pl(pts, DEF, 3)
    th = sl[-1] * mag
    Dp = (C[0] + 12 * 14 * math.sin(th), C[1] + 12 * 14 * math.cos(th))
    S.line(*C, *Dp, DEF, 3)
    S.roller(*Dp, s=0.75, c=DEF)
    vmin = min(v)
    xm = xs[v.index(vmin)]
    S.halo(W.X(xm), W.Y(mag * vmin) + 18, f'最大撓度 {abs(vmin) * 1000:.0f} mm（距 A {xm:.2f} m）', 10.5, DEF)
    S.line(C[0], C[1], C[0] + 40, C[1], GHOST, 1)
    S.line(C[0], C[1], C[0] + 40 * math.cos(th), C[1] - 40 * math.sin(th), MOM, 1.6)
    S.text(C[0] + 30, C[1] - 20, 'θ_C', 12, MOM, 'start', bold=True)
    S.halo(Dp[0] - 14, Dp[1] - 12, f'D 右移 {12 * math.sin(sl[-1]) * 1000:.0f} mm', 10.5, DEF, 'end')
    S.rect(618, 330, 262, 84, '#e3f2fd', '#90caf9', 1, rx=8)
    S.text(749, 350, '梁曲線由 EIv″ = M 積分而得', 11.5, TITLE)
    S.text(749, 370, 'C 點 v = 0（就是 ∂U/∂R = 0）', 11.5, TITLE)
    S.text(749, 390, '柱只跟著 C 剛體轉動（M ≡ 0）', 11.5, TITLE)
    S.text(749, 408, 'D 在滾支承上水平滑動', 11.5, TITLE)
    return S.render()


# ---------------------------------------------------------------- 7-1 / 9-1  SA-2016-3
def sa2016_3():
    """CD 桿：y 自 C 向下，左側受拉為正（解析 §4 的慣例）。"""
    Mt, Mb = -25.3, 17.0                       # M(0) = M_CD，M(20) = −M_DC
    M = lambda y: Mt + (Mb - Mt) * y / 20
    m = lambda y: y
    d = simpson(lambda y: M(y) * m(y), 0, 20)
    assert abs(d - 580) < 1e-9
    y0 = -Mt / ((Mb - Mt) / 20)
    assert abs(y0 - 11.96) < 5e-3
    neg = simpson(lambda y: M(y) * m(y), 0, y0)
    pos = simpson(lambda y: M(y) * m(y), y0, 20)
    assert abs(neg + 603.3) < 0.1 and abs(pos - 1183.3) < 0.1
    th = simpson(M, 0, 20)
    assert abs(th + 83) < 1e-9
    return M, m, y0, neg, pos


def fig_7_1():
    M, m, y0, neg, pos = sa2016_3()
    S = SVG(900, 430, 'SA-2016-3 真實系統與虛力系統')
    S.text(450, 22, 'SA-2016-3（依比例）：真實彎矩題目已給，虛力系統由你自己挑', 14, TITLE, bold=True)
    S.rect(12, 36, 432, 386, '#e3f2fd', '#90caf9', 1, rx=10)
    S.rect(456, 36, 432, 386, '#e8f5e9', '#a5d6a7', 1, rx=10)
    S.text(228, 58, '真實系統 M：靜不定，但四個桿端彎矩都給了', 13, TITLE, bold=True)
    S.text(672, 58, '虛力系統 m：切掉 C 左側，只留懸臂柱 CD', 13, GOOD, bold=True)
    th60 = math.radians(60)
    for ox, real in ((150, True), (594, False)):
        W = World(ox, 114, 10.5)
        B, C, D, A = W(0, 0), W(12, 0), W(12, -20), W(-10 * math.cos(th60), -10 * math.sin(th60))
        if real:
            udl(S, B[0], C[0], B[1], 20, 16)
            S.text(W.X(6), B[1] - 26, '2 kN/m', 11.5, LOAD, bold=True)
            S.line(*A, *B, INK, 3.4); S.line(*B, *C, INK, 3.4); S.line(*C, *D, INK, 3.4)
            S.fixed(*A, s=0.8); S.fixed(*D, s=0.9)
            pts = mdiag(S, C, D, M, 20, 1.7, (-1, 0))
            S.line(*C, *D, INK, 3.4)
            S.halo(pts[0][0] + 6, C[1] + 16, '25.3（右側受拉）', 11.5, BMD, 'start', bold=True)
            S.halo(pts[-1][0] - 6, D[1] - 6, '17.0（左側受拉）', 11.5, BMD, 'end', bold=True)
            S.circ(D[0], W.Y(-y0), 3.5, ORG, ORG, 1)
            S.halo(D[0] + 8, W.Y(-y0) + 4, f'反曲點 y = {y0:.2f} m', 11, ORG, 'start')
            S.text(D[0] + 8, W.Y(-16.5), 'CD = 20 m', 11, MUT, 'start')
            S.text(W.X(6), B[1] + 16, 'BC = 12 m', 11, MUT)
            S.text(A[0] - 6, A[1] + 22, 'A', 12, INK, 'end', bold=True)
            S.text((A[0] + B[0]) / 2 - 8, (A[1] + B[1]) / 2 + 4, '10 m', 11, MUT, 'end')
            S.text(A[0] - 18, A[1] + 42, 'A 的位置題目沒給', 10.5, MUT, 'start')
            S.text(A[0] - 18, A[1] + 56, '（圖取 60°，僅示意）', 10.5, MUT, 'start')
            S.rect(28, 340, 400, 76, '#fff', '#90caf9', 1, rx=8)
            S.text(46, 360, 'M_AB = −23.2、M_BC = +5.63　← 用不到（干擾資訊）', 11.5, GHOST, 'start', bold=True)
            S.text(46, 381, 'M_CD = −25.3、M_DC = −17.0　← 只用這兩個', 11.5, ORG, 'start', bold=True)
            S.text(46, 403, '換成斷面彎矩：近端同號、遠端反號 ⟹ M(0) = −25.3、M(20) = +17.0', 10.5, TITLE, 'start')
        else:
            S.line(*A, *B, GHOST, 2.4, dash='6 5'); S.line(*B, *C, GHOST, 2.4, dash='6 5')
            S.fixed(*D, s=0.9)
            pts = mdiag(S, C, D, m, 20, 2.8, (-1, 0), GOOD)
            S.line(*C, *D, GOOD, 4)
            S.arrow(C[0] - 46, C[1], C[0] - 5, C[1], GOOD, 3)
            S.text(C[0] - 26, C[1] - 8, '1', 14, GOOD, 'middle', bold=True)
            S.halo(pts[-1][0] - 6, D[1] - 6, 'm = 20（左側受拉）', 11.5, GOOD, 'end', bold=True)
            S.halo(C[0] + 8, C[1] + 18, 'm = 0', 11.5, GOOD, 'start', bold=True)
            S.text(W.X(4), W.Y(-6), 'AB、BC 的 m ≡ 0', 12, GOOD, bold=True)
            S.text(W.X(4), W.Y(-7.4), '（根本不在虛系統裡）', 11, GOOD)
            S.rect(472, 340, 400, 76, '#fff', '#a5d6a7', 1, rx=8)
            S.text(490, 360, '虛系統只需滿足平衡，不必和真實結構同構', 11.5, GOOD, 'start', bold=True)
            S.text(490, 381, '⟹ 積分只剩 CD 桿：Δ_C = ∫₀²⁰ M·m dy / EI', 11.5, GOOD, 'start')
            S.text(490, 403, '⟹ 完全不需要 AB 的傾角，也不需要 BC 的彎矩', 11.5, GOOD, 'start', bold=True)
        for p, t, dx in ((B, 'B', -8), (C, 'C', 8), (D, 'D', 20)):
            S.text(p[0] + dx, p[1] - 8 if t != 'D' else p[1] + 4, t, 12, INK, 'end' if dx < 0 else 'start', bold=True)
    return S.render()


def fig_9_1():
    M, m, y0, neg, pos = sa2016_3()
    S = SVG(900, 330, 'SA-2016-3 CD 桿的圖形積分')
    S.text(450, 22, '實例：SA-2016-3 的 CD 桿（y 自 C 向下，左側受拉為正）— Simpson 三點就是精確值', 14, TITLE, bold=True)
    specs = [(40, 'M(y)', M, (-30, 20), [(-25.3, '−25.3'), (-4.15, '−4.15'), (17.0, '+17.0')], BMD),
             (330, 'm(y) = y', m, (0, 22), [(0, '0'), (10, '10'), (20, '20')], GOOD),
             (620, 'M·m', lambda y: M(y) * m(y), (-130, 360), [(0, '0'), (-41.5, '−41.5'), (340, '+340')], MOM)]
    for x0, t, fn, yr, sp, col in specs:
        pl = Plot(S, x0 + 30, 62, 220, 170, (0, 20), yr)
        S.line(pl.X(0), pl.Y(0), pl.X(20), pl.Y(0), MUT, 1.4)
        S.text(x0 + 140, 50, t, 13, col, bold=True)
        if t == 'M·m':
            pn = [pl.P(0, 0)] + [pl.P(y, fn(y)) for y in [y0 * i / 60 for i in range(61)]] + [pl.P(y0, 0)]
            pp = [pl.P(y0, 0)] + [pl.P(y, fn(y)) for y in [y0 + (20 - y0) * i / 60 for i in range(61)]] + [pl.P(20, 0)]
            S.area(pn, SFD, 0.25); S.area(pp, BMD, 0.22)
            S.halo(pl.X(y0 / 2), pl.Y(-60) + 18, f'{neg:.1f}'.replace('-', '−'), 12, SFD, bold=True)
            S.halo(pl.X(17.6), pl.Y(70), f'+{pos:.1f}', 12, BMD, bold=True)
        else:
            S.area([pl.P(0, 0)] + [pl.P(y, fn(y)) for y in (0, 20)] + [pl.P(20, 0)], col, 0.15)
        pl.curve(fn, 0, 20, col, 2.6)
        for (yv, lab), yy in zip(sp, (0, 10, 20)):
            S.circ(*pl.P(yy, yv), 4.5, col, '#fff', 1.4)
            dy = -9 if yv >= 0 else 17
            S.halo(pl.X(yy) + (6 if yy == 0 else -6 if yy == 20 else 0), pl.Y(yv) + dy, lab, 11.5, col,
                   'start' if yy == 0 else 'end' if yy == 20 else 'middle', bold=True)
        for yy, lab in ((0, 'C'), (10, '中點'), (20, 'D')):
            S.text(pl.X(yy), pl.Y(yr[0]) + 16, lab, 11, MUT)
        if t == 'M(y)':
            S.circ(pl.X(y0), pl.Y(0), 3.2, ORG, ORG, 1)
            S.halo(pl.X(y0), pl.Y(0) - 8, f'{y0:.2f}', 10.5, ORG)
        if x0 < 600:
            S.text(x0 + 282, 150, '×' if x0 < 300 else '=', 22, MUT, bold=True)
    S.rect(60, 262, 780, 58, '#f3e5f5', '#ce93d8', 1.4, rx=9)
    S.text(450, 284, 'Simpson：Δ_C = (20/6EI)[(−25.3)(0) + 4(−4.15)(10) + (17.0)(20)] = (10/3EI)(174) = 580/EI（向右）', 12.5, MOM, bold=True)
    S.text(450, 306, f'逐段面積驗算：{neg:.1f}'.replace('-', '−') + f' + {pos:.1f} = {neg + pos:.1f}　— 兩個一次式相乘是二次式，Simpson 一字不差', 11.5, MOM)
    return S.render()


# ---------------------------------------------------------------- 8-1  SA-2019-1
def sa2019_1():
    L = dict(DB=12, AC=12, DC=9, AB=9, CB=15, DA=15)
    # 各桿內力 = a·P + b·T（解析 §4 Step 1 的節點法結果）
    F = dict(DB=(0, -0.8), DC=(0, -0.6), CB=(1.25, 1), AB=(-0.75, -0.6), AC=(0, -0.8), DA=(0, 1))
    cTT = sum(F[k][1] ** 2 * L[k] for k in L)
    cTP = sum(F[k][0] * F[k][1] * L[k] for k in L)
    T = -cTP / cTT
    assert abs(cTT - 51.84) < 1e-9 and abs(T + 95 / 216) < 1e-12
    f1 = sum((F[k][0] + F[k][1] * T) * F[k][0] * L[k] for k in L)       # U_B·EA / P
    f2 = sum(F[k][0] ** 2 * L[k] for k in L)                             # DA 退出後
    assert abs(f1 - 665 / 36) < 1e-9 and abs(f2 - 28.5) < 1e-12
    P1 = 144 / abs(T)
    Pu = 400 / 0.75
    assert abs(P1 - 327.41) < 0.01
    # 第一階段其他桿未先達強度（拉 1250；壓：對角 144、水平 225、垂直 400）
    cap = dict(DB=225, AC=225, DC=400, AB=400, CB=144, DA=144)
    for k in L:
        Fk = (F[k][0] + F[k][1] * T) * P1
        assert (Fk <= 1250 + 1e-6) if Fk > 0 else (-Fk <= cap[k] + 1e-6), k
    return f1, f2, P1, Pu


def fig_8_1():
    f1, f2, P1, Pu = sa2019_1()
    U1, U1b, Uu = f1 * P1, f2 * P1, f2 * Pu
    assert abs(U1 - 6048) < 0.1 and abs(U1b - 9331.2) < 0.1 and abs(Uu - 15200) < 0.1
    S = SVG(900, 330, 'SA-2019-1 P–U_B 關係')
    S.text(450, 22, 'SA-2019-1：P–U_B 關係（三個轉折點都是計算值）— 卡氏定理只在每段直線內成立', 14, TITLE, bold=True)
    pl = Plot(S, 80, 52, 455, 222, (0, 17500), (0, 600))
    pl.frame(xt=[(0, '0'), (5000, '5000'), (10000, '10000'), (15000, '15000')],
             yt=[(0, '0'), (100, '100'), (200, '200'), (300, '300'), (400, '400'), (500, '500')],
             xlab='U_B · EA', ylab='P (kN)')
    S.line(*pl.P(U1, P1), *pl.P(f1 * Pu, Pu), GHOST, 1.6, dash='5 4')
    S.halo(pl.X(f1 * Pu) - 4, pl.Y(Pu) - 8, '若 DA 不挫曲', 10.5, MUT, 'end')
    pts = [(0, 0), (U1, P1), (U1b, P1), (Uu, Pu), (17000, Pu)]
    S.pl([pl.P(*p) for p in pts[:2]], SFD, 3.4)
    S.pl([pl.P(*p) for p in pts[1:3]], LOAD, 3.4, dash='7 4')
    S.pl([pl.P(*p) for p in pts[2:4]], GOOD, 3.4)
    S.pl([pl.P(*p) for p in pts[3:]], MUT, 3.4)
    for p, lab, dx, dy, anc in (((U1, P1), '(6048, 327.4)', -8, -10, 'end'),
                                ((U1b, P1), '(9331, 327.4)', 8, 18, 'start'),
                                ((Uu, Pu), '(15200, 533.3)', -8, -12, 'end')):
        S.circ(*pl.P(*p), 4.5, '#fff', INK, 1.8)
        S.halo(pl.X(p[0]) + dx, pl.Y(p[1]) + dy, lab, 11, INK, anc, bold=True)
    S.halo(pl.X(2600), pl.Y(190), f'Ⅰ 一度靜不定：斜率 EA/{f1:.2f}', 11.5, SFD, 'start', bold=True)
    S.halo(pl.X(U1 + 200), pl.Y(P1) - 12, 'DA 挫曲：P 不變、位移跳躍', 11, LOAD, 'start', bold=True)
    S.halo(pl.X(11800), pl.Y(390), f'Ⅱ 靜定：斜率 EA/{f2:g}', 11.5, GOOD, 'start', bold=True)
    S.halo(pl.X(17000), pl.Y(Pu) - 10, 'AB 挫曲 → 機構', 11, MUT, 'end', bold=True)
    S.rect(616, 52, 272, 222, '#f3e5f5', '#ce93d8', 1, rx=9)
    x = 630
    for i, (t, col, bd) in enumerate((('第Ⅰ段（線彈性、1 度靜不定）', MOM, True),
                                      ('∂U/∂T = 0 ⟹ T = F_DA = −95P/216', MOM, False),
                                      ('DA 壓力達 144 kN ⟹ P₁ = 327.4 kN', MOM, False),
                                      ('第Ⅱ段（DA 內力歸零 → 靜定）', GOOD, True),
                                      ('F_AB = −0.75P，達 400 kN', GOOD, False),
                                      ('⟹ P_ult = 533.3 kN', GOOD, True),
                                      ('跨段不能直接用 U：曲線有轉折', LOAD, True),
                                      ('每段各自 Δ = ∂U/∂P（§1 圖）', LOAD, False))):
        S.text(x, 78 + i * 24 + (8 if i >= 3 else 0) + (8 if i >= 6 else 0), t, 12, col, 'start', bold=bd)
    S.text(320, 318, '橫軸 U_B·EA（kN·m）：除以 EA 即得位移。斜率變小＝結構變軟（少了一根桿）', 11.5, MUT)
    return S.render()


# ---------------------------------------------------------------- 10-1  範例 A
def fig_10_1():
    M0, m, M, R = exA()
    V = lambda s: 5 / 8 - s                       # 自 A 量，向上為正（左側斷面）
    xs, sl, v = integrate(M, 1.0)
    vmin = min(v)
    smin = xs[v.index(vmin)]
    assert abs(v[-1]) < 1e-7 and abs(-1 / vmin - 185) < 1 and abs(smin - 0.5785) < 1e-3
    vexact = lambda s: -s * s * (3 - 5 * s + 2 * s * s) / 48
    assert max(abs(vexact(x) - y) for x, y in zip(xs[::50], v[::50])) < 1e-7
    S = SVG(900, 488, '範例 A：結構、剪力、彎矩、撓度')
    S.text(450, 22, '範例 A（一端固定一端滾支承、全跨 w）：四張圖對齊同一根梁，全部依公式計算', 14, TITLE, bold=True)
    xa, xb = 170, 770
    Lp = xb - xa
    X = lambda s: xa + Lp * s
    labs = [(84, '結構'), (196, '剪力 V'), (300, '彎矩 M'), (414, '撓度 v')]
    for y, t in labs:
        S.text(46, y + 4, t, 13, TITLE, 'start', bold=True)
    # structure
    y = 84
    udl(S, xa, xb, y, 24, 24)
    S.text(X(0.5), y - 30, 'w', 12.5, LOAD, bold=True)
    S.line(xa, y, xb, y, INK, 4)
    S.wall(xa, y - 22, y + 22, side=-1)
    S.roller(xb, y + 2, s=0.9)
    S.text(xa - 10, y - 26, 'A', 13, INK, 'end', bold=True); S.text(xb + 14, y - 8, 'B', 13, INK, 'start', bold=True)
    S.arrow(xa + 18, y + 44, xa + 18, y + 8, REAC, 2.4)
    S.text(xa + 24, y + 42, 'R_A = 5wL/8', 11.5, REAC, 'start', bold=True)
    S.arrow(xb - 20, y + 44, xb - 20, y + 16, REAC, 2.4)
    S.text(xb - 26, y + 42, 'R_B = 3wL/8（多餘力）', 11.5, REAC, 'end', bold=True)
    # SFD
    y = 196; kv = 64
    pts = mdiag(S, (xa, y), (xb, y), V, 1, kv, (0, -1), SFD)
    S.line(xa, y, xb, y, INK, 1.6)
    S.halo(xa + 6, y - kv * 5 / 8 - 4, '+5wL/8', 11.5, SFD, 'start', bold=True)
    S.halo(xb - 6, y + kv * 3 / 8 + 14, '−3wL/8', 11.5, SFD, 'end', bold=True)
    S.circ(X(5 / 8), y, 3.5, ORG, ORG, 1)
    # BMD (tension side: + below)
    y = 296; km = 420
    mdiag(S, (xa, y), (xb, y), M, 1, km, (0, 1), BMD)
    S.line(xa, y, xb, y, INK, 1.6)
    S.halo(xa + 6, y - km / 8 - 5, '−wL²/8（上緣受拉）', 11.5, BMD, 'start', bold=True)
    S.halo(X(5 / 8), y + km * 9 / 128 + 16, '+9wL²/128', 11.5, BMD, bold=True)
    S.circ(X(0.25), y, 3.5, ORG, ORG, 1)
    S.halo(X(0.25), y - 10, '反曲點：距 A 為 L/4', 10.5, ORG)
    S.line(X(5 / 8), 186, X(5 / 8), y + km * 9 / 128, ORG, 1, dash='3 3')
    S.halo(X(5 / 8) + 8, 188, 'V = 0 ⟺ M 最大：距 B 為 3L/8', 10.5, ORG, 'start')
    # deflection
    y = 398; kd = 34 / (1 / 185)
    S.line(xa, y, xb, y, GHOST, 1.4, dash='5 4')
    S.pl([(X(s), y - kd * vv) for s, vv in list(zip(xs, v))[::40]], DEF, 3)
    S.wall(xa, y - 16, y + 16, side=-1)
    S.roller(xb, y + 2, s=0.7)
    S.line(X(smin), y, X(smin), y - kd * vmin, DEF, 1, dash='2 2')
    S.halo(X(smin), y - kd * vmin + 16, 'v_max = wL⁴/185EI', 11.5, DEF, bold=True)
    S.halo(X(smin), y - kd * vmin + 31, '距 A 0.5785L（＝距 B 0.4215L）', 10.5, DEF)
    S.halo(xa + 8, y - 10, 'A：v = 0、v′ = 0', 10.5, DEF, 'start')
    S.halo(xb - 14, y - 12, 'B：v = 0', 10.5, DEF, 'end')
    S.text(450, 478, '彎矩畫在受拉側（正彎矩＝下緣受拉，畫在梁下方）。撓度曲線由 EIv″ = M 積分而得，與公式 v = −wξ²(3L² − 5Lξ + 2ξ²)/48EI 完全重合', 11, MUT)
    return S.render()


# ---------------------------------------------------------------- 10-2 / 10-3  範例 B（SA-2017-2）
def exB(m=6.0, n=4.0, w=10.0):
    V = 3 * w * (m ** 4 - n ** 4) / (8 * (m ** 3 + n ** 3))
    ML = lambda x: V * x - w * x * x / 2            # x 自 c 向 a
    MR = lambda t: -V * t - w * t * t / 2           # ξ 自 c 向 b
    # 最小功條件
    g = simpson(lambda x: ML(x) * x, 0, m) + simpson(lambda t: MR(t) * (-t), 0, n)
    assert abs(g) < 1e-7
    D = m * m - m * n + n * n
    Ma = -w * m * (m ** 3 - m * m * n + m * n * n + 3 * n ** 3) / (8 * D)
    Mb = -w * n * (3 * m ** 3 + m * m * n - m * n * n + n ** 3) / (8 * D)
    assert abs(ML(m) - Ma) < 1e-9 and abs(MR(n) - Mb) < 1e-9
    return V, ML, MR, Ma, Mb


def fig_10_2():
    m, n, w = 6.0, 4.0, 10.0
    V, ML, MR, Ma, Mb = exB(m, n, w)
    assert abs(V - 13.93) < 5e-3 and abs(Ma + 96.4) < 0.05 and abs(Mb + 135.7) < 0.05
    # 撓度：兩支懸臂各自積分（EI = 1），c 點兩側必須等高
    sL, slL, vL = integrate(lambda s: ML(m - s), m)          # s 自 a
    sR, slR, vR = integrate(lambda s: MR(n - s), n)          # s 自 b（往左）
    assert abs(vL[-1] - vR[-1]) < 1e-3 * abs(vL[-1])
    S = SVG(900, 410, '範例 B 數值抽驗：彎矩圖與撓度')
    S.text(450, 22, f'範例 B 數值抽驗（m = 6、n = 4、w = 10，依比例）：V = {V:.2f}', 14, TITLE, bold=True)
    W = World(150, 0, 60)
    a, c, b = W.X(0), W.X(m), W.X(m + n)
    for y, t in ((76, '結構'), (214, '彎矩 M'), (324, '撓度 v')):
        S.text(46, y + 4, t, 13, TITLE, 'start', bold=True)
    y = 76
    udl(S, a, b, y, 22, 24)
    S.line(a, y, b, y, INK, 4)
    S.wall(a, y - 22, y + 22, side=-1); S.wall(b, y - 22, y + 22, side=1)
    S.hinge(c, y, 6, MOM)
    S.text(a - 8, y - 26, 'a', 13, INK, 'end', bold=True); S.text(b + 8, y - 26, 'b', 13, INK, 'start', bold=True)
    S.text(c, y + 24, 'c（內鉸）', 12, MOM, bold=True)
    S.dim(a, y + 34, c, y + 34, 'm = 6', off=0, lab_off=14)
    S.dim(c, y + 34, b, y + 34, 'n = 4', off=0, lab_off=14)
    y = 214; k = 0.55
    pl_ = mdiag(S, (c, y), (a, y), ML, m, k, (0, 1))
    pr_ = mdiag(S, (c, y), (b, y), MR, n, k, (0, 1))
    S.line(a, y, b, y, INK, 1.6)
    S.halo(a + 6, y + k * Ma - 6, f'M_a = {Ma:.1f}'.replace('-', '−'), 12, BMD, 'start', bold=True)
    S.halo(b - 6, y + k * Mb - 6, f'M_b = {Mb:.1f}'.replace('-', '−'), 12, BMD, 'end', bold=True)
    xpk = V / w
    S.halo(W.X(m - xpk), y + k * ML(xpk) + 15, f'+{ML(xpk):.2f}', 11, BMD, bold=True)
    S.circ(c, y, 4, '#fff', MOM, 2)
    S.halo(c + 8, y + 18, 'M_c = 0', 11, MOM, 'start', bold=True)
    y = 300; kd = 44 / abs(vL[-1])
    S.line(a, y, b, y, GHOST, 1.4, dash='5 4')
    S.pl([(W.X(s), y - kd * vv) for s, vv in list(zip(sL, vL))[::40]], DEF, 3)
    S.pl([(W.X(m + n - s), y - kd * vv) for s, vv in list(zip(sR, vR))[::40]], DEF, 3)
    S.wall(a, y - 16, y + 16, side=-1); S.wall(b, y - 16, y + 16, side=1)
    S.hinge(c, y - kd * vL[-1], 5, MOM)
    S.halo(c, y - kd * vL[-1] + 22, f'v_c = {vL[-1]:.0f}/EI（左右兩支懸臂算出同一值）'.replace('-', '−'), 11.5, DEF, bold=True)
    S.halo(c + 10, y - kd * vL[-1] - 10, '鉸處斜率不連續（折角）', 10.5, MOM, 'start')
    S.text(450, 398, '負彎矩（上緣受拉）畫在梁上方。短的那一段（n）比較硬 → 分到較大的 V 與較大的固端彎矩 |M_b| > |M_a|', 11.5, MUT)
    return S.render()


def fig_10_3():
    S = SVG(900, 330, '範例 B 的極限檢查')
    S.text(450, 22, '把範例 B 的答案畫成 m/L 的函數：三個極限檢查一眼看完（縱軸 |M| / wL²）', 14, TITLE, bold=True)
    pl = Plot(S, 80, 52, 520, 226, (0, 1), (0, 0.15))
    pl.frame(xt=[(0, '0'), (0.25, '0.25'), (0.5, '0.5'), (0.6, '0.6'), (0.75, '0.75'), (1, '1')],
             yt=[(0, '0'), (1 / 12, '1/12'), (0.125, '1/8')], xlab='m / L', ylab='|M| / wL²')

    def mm(al):
        if al <= 1e-9 or al >= 1 - 1e-9:
            return (0.0, 0.125) if al < 0.5 else (0.125, 0.0)
        _, _, _, Ma, Mb = exB(al, 1 - al, 1.0)
        return -Ma, -Mb
    S.line(pl.X(0), pl.Y(1 / 12), pl.X(1), pl.Y(1 / 12), GHOST, 1.2, dash='5 4')
    als = [i / 200 for i in range(201)]
    S.pl([pl.P(al, mm(al)[0]) for al in als], BMD, 3)
    S.pl([pl.P(al, mm(al)[1]) for al in als], SFD, 3)
    S.halo(pl.X(0.2), pl.Y(mm(0.2)[0]) + 16, '|M_a|', 12, BMD, bold=True)
    S.halo(pl.X(0.2), pl.Y(mm(0.2)[1]) - 8, '|M_b|', 12, SFD, bold=True)
    pk = max(als[1:-1], key=lambda al: mm(al)[1])
    for x, y in ((0.5, 0.125), (1.0, 0.125), (1.0, 0.0), (0.0, 0.125), (0.0, 0.0)):
        S.circ(*pl.P(x, y), 5, GOOD, '#fff', 1.5)
    S.line(pl.X(0.5), pl.Y(0.118), pl.X(0.5), pl.Y(0.05), GOOD, 1, dash='2 3')
    S.halo(pl.X(0.5), pl.Y(0.045), '① 對稱 m = n：V = 0', 11, GOOD, bold=True)
    S.halo(pl.X(0.5), pl.Y(0.045) + 15, '兩端都 = w(L/2)²/2 = wL²/8', 10.5, GOOD)
    S.halo(pl.X(0.985), pl.Y(0.143), '② n → 0：|M_a| → wL²/8（範例 A）', 11, GOOD, 'end', bold=True)
    S.halo(pl.X(0.985), pl.Y(0.0) - 8, '|M_b| → 0', 11, GOOD, 'end', bold=True)
    a6 = mm(0.6)
    for yv, col in ((a6[0], BMD), (a6[1], SFD)):
        S.circ(*pl.P(0.6, yv), 4, col, '#fff', 1.3)
    S.line(pl.X(0.6), pl.Y(0), pl.X(0.6), pl.Y(a6[1]), MUT, 1, dash='2 3')
    S.rect(626, 52, 260, 226, '#e8f5e9', '#a5d6a7', 1, rx=9)
    for i, (t, bd) in enumerate((('怎麼讀這張圖', True), ('紅、藍兩條曲線對 m/L = 0.5 左右鏡射', False),
                                 ('⟹ ③ 互換檢查（m ↔ n）通過', True),
                                 ('兩條線在 0.5 與端點都碰到 1/8', False), ('⟹ ①② 兩個極限都對', True), ('', False),
                                 (f'|M_b| 最大約 {mm(pk)[1]:.3f}wL²（m/L ≈ {pk:.2f}）', False),
                                 ('虛線 = 無內鉸兩端固定梁 wL²/12', False),
                                 ('內鉸讓固端彎矩可能大於 wL²/8', False))):
        if t:
            S.text(642, 78 + i * 22, t, 12 if not bd else 12.5, GOOD, 'start', bold=bd)
    S.text(340, 318, f'm/L = 0.6 的兩個圓點 = 範例 B 數值抽驗：{a6[0]:.4f}、{a6[1]:.4f}（× wL² = 1000 → 96.4、135.7）', 11.5, MUT)
    return S.render()


# ======================= driver =======================
FIGS = {
    '0-1': fig_0_1, '0-2': fig_0_2, '1-1': fig_1_1, '2-2': fig_2_2, '3-1': fig_3_1,
    '4-1': fig_4_1, '4-2': fig_4_2, '5-1': fig_5_1, '6-1': fig_6_1, '7-1': fig_7_1,
    '8-1': fig_8_1, '9-1': fig_9_1, '10-1': fig_10_1, '10-2': fig_10_2, '10-3': fig_10_3,
}


def inject(html):
    import re
    n = 0
    for fid, fn in FIGS.items():
        pat = re.compile(r'(<!--FIG:%s-->\s*<div class="fig">\s*)<svg.*?</svg>' % re.escape(fid), re.S)
        html, k = pat.subn(lambda m: m.group(1) + fn(), html)
        if k != 1:
            raise SystemExit(f'marker FIG:{fid} found {k} times')
        n += k
    return html, n


if __name__ == '__main__':
    import sys, pathlib
    p = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                     pathlib.Path(__file__).resolve().parent.parent / 'study' / 'lecture-SA-U2-1.html')
    html, n = inject(p.read_text(encoding='utf-8'))
    p.write_text(html, encoding='utf-8')
    print(f'{p}: {n} figures regenerated')

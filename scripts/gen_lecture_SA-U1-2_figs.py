#!/usr/bin/env python3
"""gen_lecture_SA-U1-2_figs.py — 重繪 study/lecture-SA-U1-2.html 的全部 SVG 圖解

所有結構圖依題目真實尺寸（World: m→px）繪製；內力圖、變位曲線由解析中的公式
直接計算（含 assert 自我檢查，數值與 raw/solutions/ 對應解析一致）。
HTML 內以 <!--FIG:id--> ... <!--/FIG:id--> 標記圖位，本腳本只替換標記之間的 <svg>…</svg>，
圖說（.cap）與正文不動。可重複執行。

用法：python scripts/gen_lecture_SA-U1-2_figs.py [study/lecture-SA-U1-2.html]
"""

# ======================= svglib.py =======================
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

# ======================= figs_a.py =======================
"""§1–§2 figures"""


# ---------------------------------------------------------------- 1-1
def fig_1_1():
    S = SVG(900, 268, '靜定判定四種狀態')
    panels = [
        (15, '#ffebee', '#ef9a9a', LOAD, 'd < 0　機構', 'r = 2，d = 2−3 = −1'),
        (240, '#e8f5e9', '#a5d6a7', GOOD, 'd = 0　靜定', 'r = 3，d = 0'),
        (465, '#fff3e0', '#ffcc80', ORG, 'd > 0　靜不定', 'r = 4，d = +1'),
        (690, '#f3e5f5', '#ce93d8', MOM, '特例　瞬間不穩定', 'r = 3，d = 0 但反力平行'),
    ]
    texts = [
        ['約束不足', '→ 先懷疑漏看構件', '（繫索？支承方向？）'],
        ['內力唯一，與 EI 無關', '沉陷、溫差不生內力', '← 本單元的主場'],
        ['內力受 EI 分配', '沉陷、溫差會生內力', '→ 轉往 SA-U2'],
        ['三個反力全是垂直的', '水平力 H 無從平衡', '→ 公式管不到，要用眼睛'],
    ]
    for k, (x0, bg, bd, col, title, sub) in enumerate(panels):
        w = 195 if k == 3 else 205
        S.rect(x0, 12, w, 244, bg, bd, 1, rx=10)
        S.text(x0 + w / 2, 36, title, 15, col, bold=True)
        S.text(x0 + w / 2, 56, sub, 11.5, col)
        y = 112
        xa, xb = x0 + 28, x0 + w - 28
        S.line(xa, y, xb, y, INK, 4)
        if k == 0:
            S.roller(xa + 10, y); S.roller(xb - 10, y)
            S.arrow(x0 + 70, y - 22, x0 + 140, y - 22, LOAD, 2.5)
            S.text(x0 + w / 2, y - 30, '整根梁可水平滑走', 11.5, LOAD)
        elif k == 1:
            S.pin(xa + 10, y); S.roller(xb - 10, y)
            S.arrow(xa + 10, y + 52, xa + 10, y + 30, REAC, 2)
            S.arrow(xa - 18, y + 4, xa + 4, y + 4, REAC, 2)
            S.arrow(xb - 10, y + 52, xb - 10, y + 30, REAC, 2)
        elif k == 2:
            S.pin(xa + 10, y); S.roller((xa + xb) / 2, y); S.roller(xb - 10, y)
        else:
            for xx in (xa + 8, (xa + xb) / 2, xb - 8):
                S.roller(xx, y)
            S.arrow(xa - 6, y - 22, xa + 46, y - 22, LOAD, 2.5)
            S.text(xa + 20, y - 30, 'H', 12, LOAD, bold=True)
            S.line(xa + 8, y + 58, xb - 8, y + 58, MOM, 1.5, dash='4 3')
            for xx in (xa + 8, (xa + xb) / 2, xb - 8):
                S.arrow(xx, y + 58, xx, y + 36, MOM, 1.6, L=7, W=3)
        for j, t in enumerate(texts[k]):
            S.text(x0 + w / 2, 196 + j * 20, t, 12.5, col if j < 2 else INK)
    return S.render()


# ---------------------------------------------------------------- 1-2
def fig_1_2():
    S = SVG(900, 300, '三種隱藏條件')
    # ① SA-2002-2 truss, to scale
    W = World(28, 168, 7.0)
    P = dict(A=(0, 0), B=(32, 0), D=(0, 12), F=(8, 12), C=(16, 12), H=(24, 12), I=(32, 12),
             E=(8, 6), G=(24, 6))
    mem = ['DF', 'FC', 'CH', 'HI', 'AD', 'BI', 'FE', 'HG', 'DE', 'AE', 'EC', 'CG', 'GB', 'GI']
    S.text(140, 24, '① 虛線 = 繫索（SA-2002-2）', 14, REAC, bold=True)
    for m in mem:
        S.line(*W(*P[m[0]]), *W(*P[m[1]]), INK, 2.2)
    S.line(*W(*P['A']), *W(*P['B']), REAC, 3, dash='8 5')
    for k, v in P.items():
        S.node(*W(*v), 2.8)
    S.pin(*W(0, 0), s=0.8); S.roller(*W(32, 0), s=0.8)
    S.halo(W.X(16), W.Y(0) + 15, 'AB 繫索（只能受拉）', 11.5, REAC)
    for k in 'ABCD':
        pass
    S.text(W.X(0) - 9, W.Y(0) + 4, 'A', 11, INK, 'end'); S.text(W.X(32) + 9, W.Y(0) + 4, 'B', 11, INK, 'start')
    S.text(140, 214, '少了它：m + r = 14 + 3 = 17 < 2j = 18', 12, INK)
    S.text(140, 233, '節點 A 有 Ax、Ay、AD、AE、AB 五個未知', 12, INK)
    S.text(140, 252, '→ 必須先用截面法取出 AB 拉力', 12, INK)

    # ② three-hinged arch made of two truss halves
    S.text(445, 24, '② 缺底弦 = 三鉸拱（SA-2013-1 型）', 14, REAC, bold=True)
    W2 = World(355, 168, 9.0)
    L = [(0, 0), (4, 6), (10, 12), (6, 4)]   # left half nodes: support, top-chord, crown, inner
    pts_l = {'a': (0, 0), 'b': (5, 7.5), 'k': (10, 12), 'c': (7, 3.5)}
    pts_r = {k: (20 - x, y) for k, (x, y) in pts_l.items()}
    for half in (pts_l, pts_r):
        for m in ('ab', 'bk', 'ac', 'ck', 'bc'):
            S.line(*W2(*half[m[0]]), *W2(*half[m[1]]), INK, 2.2)
        for v in half.values():
            S.node(*W2(*v), 2.8)
    S.line(*W2(0, 0), *W2(20, 0), LOAD, 2, dash='4 4')
    S.halo(W2.X(10), W2.Y(0) + 4, '底弦不存在', 11.5, LOAD)
    S.hinge(*W2(10, 12), 6, MOM)
    S.text(W2.X(10), W2.Y(12) - 11, '中央鉸 k', 11.5, MOM, bold=True)
    S.pin(*W2(0, 0), s=0.8); S.pin(*W2(20, 0), s=0.8)
    S.text(445, 214, '兩端都是鉸 → 4 個反力', 12, INK)
    S.text(445, 233, '第 4 式：任一半對中央鉸 ΣM = 0', 12, INK)
    S.text(445, 252, '若誤當一鉸一滾：節點 k 兩式互相矛盾', 12, INK)

    # ③ roller against vertical wall
    S.text(752, 24, '③ 滾支承靠垂直牆（SA-2010-1 型）', 14, REAC, bold=True)
    y = 112
    S.wall(842, 54, 176, side=1)
    S.line(650, y, 820, y, INK, 4)
    S.pin(650, y)
    S.roller(820, y, rot=-90)
    S.arrow(818, y - 30, 770, y - 30, REAC, 2.5)
    S.text(794, y - 38, 'R（⊥ 牆面）', 12, REAC, bold=True)
    S.text(752, 214, '反力垂直於「接觸面」→ 只有水平分量', 12, INK)
    S.text(752, 233, '垂直方向完全自由', 12, INK)
    S.text(752, 252, '慣性假設「滾支承給垂直力」→ 全盤皆錯', 12, LOAD)
    return S.render()


# ---------------------------------------------------------------- 2-1
def fig_2_1():
    """SA-2004-1 to scale: original + two free bodies with solved numbers"""
    S = SVG(900, 420, 'SA-2004-1 內鉸分離體')
    S.text(450, 22, '內鉸 B 把結構分成「附屬結構 BCD」與「主結構 AB」（SA-2004-1，依比例）', 14.5, '#0d47a1', bold=True)
    W = World(130, 352, 40)        # 1 m = 40 px
    A, B, C, D = W(0, 0), W(0, 4), W(4, 4), W(6, 4)
    S.line(*A, *B, INK, 4.5); S.line(*B, *D, INK, 4.5)
    S.fixed(*A, s=1.1)
    S.roller(*C)
    S.hinge(*B, 6.5, MOM)
    # udl
    yt = B[1] - 32
    S.line(B[0], yt, D[0], yt, LOAD, 1.6)
    for k in range(13):
        x = W.X(k * 0.5)
        S.arrow(x, yt, x, B[1] - 6, LOAD, 1.5, L=7, W=3)
    S.text(D[0] - 4, yt - 8, 'w = 2 t/m', 12.5, LOAD, 'end', bold=True)
    # 4t
    S.arrow(A[0] - 62, W.Y(2), A[0] - 4, W.Y(2), LOAD, 3)
    S.text(A[0] - 40, W.Y(2) - 9, '4 t', 13, LOAD, bold=True)
    S.text(B[0] - 12, B[1] - 6, 'B', 13, INK, 'end', bold=True)
    S.text(C[0] + 18, C[1] + 16, 'C', 13, INK, 'start', bold=True)
    S.text(D[0] + 6, D[1] + 4, 'D', 13, INK, 'start', bold=True)
    S.text(A[0] + 14, A[1] + 22, 'A', 13, INK, bold=True)
    S.dim(*W(0, 0), *W(0, 2), '2 m', off=-88)
    S.dim(*W(0, 2), *W(0, 4), '2 m', off=-88)
    S.dim(*W(0, 0), *W(4, 0), '4 m', off=28, lab_off=14)
    S.dim(*W(4, 0), *W(6, 0), '2 m', off=28, lab_off=14)
    S.text(230, 408, '原結構：4 個未知反力（A 三個＋C 一個）', 12, MUT)

    S.arrow(382, 210, 428, 210, REAC, 3)
    S.text(405, 200, '切開', 13, REAC, bold=True)

    # FBD 1 : BCD
    S.rect(440, 40, 450, 168, '#e8f5e9', '#66bb6a', 1, rx=9)
    S.text(665, 60, '① 附屬結構 BCD（先解）', 13.5, '#1b5e20', bold=True)
    W1 = World(500, 140, 40)
    b, c, d = W1(0, 0), W1(4, 0), W1(6, 0)
    S.line(*b, *d, INK, 4.5)
    yt = b[1] - 30
    S.line(b[0], yt, d[0], yt, LOAD, 1.4)
    for k in range(13):
        S.arrow(W1.X(k * 0.5), yt, W1.X(k * 0.5), b[1] - 5, LOAD, 1.4, L=7, W=3)
    S.text(d[0] + 4, yt + 4, '2 t/m', 11.5, LOAD, 'start')
    S.hinge(*b, 5.5, MOM)
    S.arrow(b[0], b[1] + 40, b[0], b[1] + 6, REAC, 2.6)
    S.text(b[0] - 8, b[1] + 34, 'By = 3 t', 12.5, REAC, 'end', bold=True)
    S.text(b[0] - 8, b[1] + 50, 'Bx = 0', 12, REAC, 'end')
    S.arrow(c[0], c[1] + 40, c[0], c[1] + 6, REAC, 2.6)
    S.text(c[0] + 8, c[1] + 34, 'Cy = 9 t', 12.5, REAC, 'start', bold=True)
    S.text(665, 200, 'ΣM_B = 0：4Cy = 12×3 → Cy = 9 ；ΣFy = 0 → By = 3', 11.5, '#1b5e20')

    # FBD 2 : AB
    S.rect(440, 218, 450, 182, '#fff3e0', '#ffb74d', 1, rx=9)
    S.text(665, 238, '② 主結構 AB（後解）', 13.5, '#e65100', bold=True)
    W2 = World(600, 378, 22)
    a2, m2, b2 = W2(0, 0), W2(0, 2), W2(0, 4)
    S.area([(b2[0] - 10, b2[1]), (b2[0] + 10, b2[1]), (m2[0] + 10, m2[1]), (m2[0] - 10, m2[1])], GOOD, 0.18)
    S.line(*a2, *b2, INK, 4.5)
    S.hinge(*b2, 5, MOM)
    S.arrow(b2[0], b2[1] - 2 - 30, b2[0], b2[1] - 7, REAC, 2.4)
    S.text(b2[0] + 8, b2[1] - 16, '3 t（By 的反作用）', 12, REAC, 'start')
    S.arrow(m2[0] - 50, m2[1], m2[0] - 4, m2[1], LOAD, 2.8)
    S.text(m2[0] - 30, m2[1] - 8, '4 t', 12.5, LOAD, bold=True)
    S.arrow(a2[0] + 2, a2[1], a2[0] - 44, a2[1], REAC, 2.6)
    S.text(a2[0] - 48, a2[1] + 4, 'Ax = 4 t', 12, REAC, 'end', bold=True)
    S.arrow(a2[0] + 26, a2[1] + 22, a2[0] + 26, a2[1] - 4, REAC, 2.4)
    S.text(a2[0] + 32, a2[1] + 18, 'Ay = 3 t', 12, REAC, 'start', bold=True)
    S.moment(a2[0], a2[1], 14, ccw=True, c=REAC, a0=100, span=200)
    S.text(a2[0] - 20, a2[1] - 16, 'M_A = 8 t-m', 12, REAC, 'end', bold=True)
    S.text(m2[0] + 16, W2.Y(3) + 4, '這段 V = M = 0', 12, GOOD, 'start', bold=True)
    S.text(700, 330, 'ΣFx：Ax = 4 t（←）', 11.5, '#e65100', 'start')
    S.text(700, 349, 'ΣFy：Ay = 3 t（↑）', 11.5, '#e65100', 'start')
    S.text(700, 368, 'ΣM_A：M_A = 4×2 = 8 t-m（逆時針）', 11.5, '#e65100', 'start')
    S.text(700, 387, '力流：附屬 → 主結構，永遠單向', 11.5, INK, 'start')
    return S.render()


# ---------------------------------------------------------------- 2-2
def fig_2_2():
    """SA-2004-1 SFD and BMD drawn on the frame (exact functions)."""
    S = SVG(900, 345, 'SA-2004-1 SFD 與 BMD')

    def frame(W, title):
        A, B, D = W(0, 0), W(0, 4), W(6, 4)
        S.text((A[0] + D[0]) / 2 - 20, 34, title, 14, '#0d47a1', bold=True)
        S.line(*A, *B, INK, 3); S.line(*B, *D, INK, 3)
        S.fixed(*A, s=0.9); S.roller(*W(4, 4), s=0.75); S.hinge(*B, 4.5, MOM)
        return A, B, D

    # ---- SFD ----
    W = World(120, 300, 42)
    frame(W, '剪力圖 SFD（t）')
    kv = 7.0   # px per t
    # column: V=+4 for y in 0..2 drawn to the left
    pts = [W(0, 0), (W.X(0) - 4 * kv, W.Y(0)), (W.X(0) - 4 * kv, W.Y(2)), W(0, 2)]
    S.area(pts, '#1565c0', 0.18); S.pl(pts, REAC, 1.8)
    S.halo(W.X(0) - 4 * kv - 4, W.Y(1) + 4, '+4', 12, REAC, 'end', bold=True)
    S.halo(W.X(0) - 6, W.Y(3) + 4, '0', 12, GOOD, 'end', bold=True)
    # beam V(x) = 3-2x (0..4), 12-2x (4..6); positive up
    seg1 = [(W.X(x / 10), W.Y(4) - kv * (3 - 2 * x / 10)) for x in range(0, 41)]
    seg2 = [(W.X(4 + x / 10), W.Y(4) - kv * (12 - 2 * (4 + x / 10))) for x in range(0, 21)]
    S.area([W(0, 4)] + seg1 + [W(4, 4)], '#1565c0', 0.18)
    S.area([W(4, 4)] + seg2 + [W(6, 4)], '#1565c0', 0.18)
    S.pl([W(0, 4)] + seg1 + seg2, REAC, 1.8)
    S.halo(W.X(0) + 4, W.Y(4) - 3 * kv - 5, '+3', 12, REAC, 'start', bold=True)
    S.halo(W.X(4) - 4, W.Y(4) + 5 * kv + 14, '−5', 12, REAC, 'end', bold=True)
    S.halo(W.X(4) + 5, W.Y(4) - 4 * kv - 5, '+4', 12, REAC, 'start', bold=True)
    S.line(W.X(1.5), W.Y(4) - 30, W.X(1.5), W.Y(4) + 30, ORG, 1.2, dash='3 3')
    S.halo(W.X(1.5) + 5, W.Y(4) - 34, 'V = 0 @ x = 1.5 m', 11.5, ORG, 'start')

    # ---- BMD (tension side) ----
    W = World(580, 300, 42)
    frame(W, '彎矩圖 BMD（t-m，畫在受拉側）')
    km = 9.0
    # column: M = 8-4y (left side tension) for y 0..2
    pts = [W(0, 0), (W.X(0) - 8 * km, W.Y(0)), W(0, 2)]
    S.area(pts, LOAD, 0.15); S.pl(pts, LOAD, 1.8)
    S.halo(W.X(0) - 8 * km - 4, W.Y(0) - 4, '8', 12.5, LOAD, 'end', bold=True)
    S.halo(W.X(0) + 8, W.Y(1.2), '左側受拉', 11, LOAD, 'start')
    S.halo(W.X(0) + 8, W.Y(3), 'M = 0', 11.5, GOOD, 'start', bold=True)
    # beam: M = 3x - x^2 (0..4), -(6-x)^2 (4..6). positive (bottom tension) drawn below
    def M(x):
        return 3 * x - x * x if x <= 4 else -(6 - x) ** 2
    xs = [k / 20 for k in range(0, 121)]
    pts = [(W.X(x), W.Y(4) + km * M(x)) for x in xs]
    S.area([W(0, 4)] + pts + [W(6, 4)], LOAD, 0.15)
    S.pl(pts, LOAD, 1.8)
    S.halo(W.X(1.5), W.Y(4) + km * 2.25 + 16, '+2.25', 12.5, LOAD, bold=True)
    S.halo(W.X(4), W.Y(4) - km * 4 - 6, '−4', 12.5, LOAD, bold=True)
    S.circ(W.X(3), W.Y(4), 3.5, ORG, ORG, 1)
    S.line(W.X(3), W.Y(4), W.X(3.4), W.Y(4) + 34, ORG, 1)
    S.halo(W.X(3.4) + 3, W.Y(4) + 44, '反曲點 x = 3 m', 11.5, ORG, 'start')
    S.halo(W.X(1.5), W.Y(4) + km * 2.25 + 31, '(x = 1.5 m)', 10.5, LOAD)
    S.line(W.X(1.5), W.Y(4) - 4, W.X(1.5), W.Y(4) + km * 2.25, ORG, 1.2, dash='3 3')
    return S.render()

# ======================= figs_b.py =======================
"""§2.2–§4 figures"""
from fractions import Fraction as Fr


# ---------------------------------------------------------------- 2-3  SA-2002-1 loads + BMD
def M_2002_1():
    """inner-side-tension BMD of SA-2002-1 (kN-m) — values from the 2026-10-23 corrected solution"""
    def colL(y):            # left column, y from A
        return 10 * y if y <= 2 else 10 * y - 6
    def beam(x):            # from C
        if x <= 2:
            return 34 + x / 3
        if x <= 3:
            return 104 / 3 - 5 / 3 * (x - 2)
        return 33 - 29 / 3 * (x - 3)
    def colR(y):            # right column, y from H
        return 4 * y - y * y if y <= 2 else 4.0
    # self-checks against the solution
    assert abs(colL(2) - 20) < 1e-9 and abs(colL(2.0001) - 14) < 1e-2 and abs(colL(4) - 34) < 1e-9
    assert abs(beam(2) - 104 / 3) < 1e-9 and abs(beam(3) - 33) < 1e-9 and abs(beam(6) - 4) < 1e-9
    assert abs(colR(2) - 4) < 1e-9
    return colL, beam, colR


def fig_2_3():
    colL, beam, colR = M_2002_1()
    S = SVG(900, 390, 'SA-2002-1 載重與彎矩圖')
    # ---- left: loads (corrected) ----
    W = World(70, 330, 36)
    A, B, C, D, E, F, G, H = W(0, 0), W(0, 2), W(0, 4), W(2, 4), W(3, 4), W(6, 4), W(6, 2), W(6, 0)
    S.text(180, 26, '載重（依 2026-10-23 校正後解析）', 13.5, '#0d47a1', bold=True)
    S.line(*A, *C, INK, 3.5); S.line(*C, *F, INK, 3.5); S.line(*F, *H, INK, 3.5)
    S.pin(*A, s=0.85); S.pin(*H, s=0.85); S.hinge(*F, 6)
    S.circ(*C, 3.5, INK, INK, 1)
    for p, t, dx in ((A, 'A', -10), (B, 'B', -10), (D, 'D', 0), (E, 'E', 0), (G, 'G', 10), (H, 'H', 10)):
        if t in 'DE':
            S.text(p[0], p[1] + 18, t, 12, INK, bold=True)
        else:
            S.text(p[0] + dx, p[1] + 4, t, 12, INK, 'end' if dx < 0 else 'start', bold=True)
    S.text(F[0] + 9, F[1] - 9, 'F', 12, INK, 'start', bold=True)
    S.text(C[0] - 8, C[1] + 18, 'C', 12, INK, 'end', bold=True)
    S.arrow(C[0] - 52, C[1], C[0] - 5, C[1], LOAD, 2.6)
    S.text(C[0] - 30, C[1] - 8, '10 kN', 11.5, LOAD, bold=True)
    S.moment(B[0], B[1], 13, ccw=True, c=MOM, a0=-60, span=280)
    S.text(B[0] + 18, B[1] + 4, '6 kN-m（逆）', 11.5, MOM, 'start')
    for k in range(4):
        x = W.X(0.25 + k * 0.5)
        S.moment(x, C[1] - 13, 7, ccw=False, c=MOM, w=1.6, a0=150, span=260)
    S.text(W.X(1), C[1] - 30, 'm = 2 kN-m/m（順）', 11.5, MOM)
    S.arrow(E[0], E[1] - 50, E[0], E[1] - 5, LOAD, 2.6)
    S.text(E[0] + 5, E[1] - 40, '8 kN', 11.5, LOAD, 'start', bold=True)
    S.moment(F[0] - 20, F[1], 11, ccw=True, c=MOM, a0=-20, span=260)
    S.text(F[0] - 34, F[1] + 4, '4', 11.5, MOM, 'end', bold=True)
    S.moment(F[0], F[1] + 22, 11, ccw=False, c=MOM, a0=200, span=260)
    S.text(F[0] + 15, F[1] + 40, '4', 11.5, MOM, 'start', bold=True)
    for k in range(5):
        y = W.Y(k * 0.5)
        S.arrow(H[0] + 30, y, H[0] + 4, y, LOAD, 1.4, L=7, W=3)
    S.line(H[0] + 30, W.Y(0), H[0] + 30, W.Y(2), LOAD, 1.4)
    S.text(H[0] + 34, W.Y(1) + 4, '2 kN/m', 11.5, LOAD, 'start')
    S.text(180, 362, 'A_x = 10 ←，A_y = 5/3 ↓；H_x = 4 →，H_y = 29/3 ↑', 11.5, REAC)
    S.text(180, 380, 'F：梁端 4 逆、柱端 4 順；內鉸傳力 P = 0，Q = 29/3', 11.5, REAC)

    # ---- right: BMD, inner side tension ----
    W = World(470, 330, 50)
    A, C, F, H = W(0, 0), W(0, 4), W(6, 4), W(6, 0)
    S.text(620, 26, 'BMD（kN-m，畫在受拉側 = 內側）', 13.5, '#0d47a1', bold=True)
    S.line(*A, *C, INK, 3); S.line(*C, *F, INK, 3); S.line(*F, *H, INK, 3)
    S.pin(*A, s=0.8); S.pin(*H, s=0.8); S.hinge(*F, 5.5)
    k = 1.7
    ys = [i / 50 for i in range(0, 201)]
    # left column (right side): split at the jump
    p1 = [(W.X(0) + k * colL(y), W.Y(y)) for y in ys if y <= 2]
    p2 = [(W.X(0) + k * colL(y), W.Y(y)) for y in ys if y > 2]
    p2 = [(W.X(0) + k * 14, W.Y(2))] + p2
    S.area([A] + p1 + [W(0, 2)], LOAD, 0.15); S.area([W(0, 2)] + p2 + [C], LOAD, 0.15)
    S.pl(p1, LOAD, 1.8); S.pl(p2, LOAD, 1.8)
    S.line(p1[-1][0], p1[-1][1], p2[0][0], p2[0][1], MOM, 2.4)
    xs = [i / 50 for i in range(0, 301)]
    pb = [(W.X(x), W.Y(4) + k * beam(x)) for x in xs]
    S.area([C] + pb + [F], LOAD, 0.15); S.pl(pb, LOAD, 1.8)
    S.line(pb[-1][0], pb[-1][1], F[0], F[1], MOM, 2.4)
    ys2 = [i / 50 for i in range(0, 201)]
    pr = [(W.X(6) - k * colR(y), W.Y(y)) for y in ys2]
    S.area([H] + pr + [F], LOAD, 0.15); S.pl(pr, LOAD, 1.8)
    S.line(pr[-1][0], pr[-1][1], F[0], F[1], MOM, 2.4)
    # labels
    S.halo(W.X(0) + k * 20 + 5, W.Y(2) + 12, '20', 12, LOAD, 'start', bold=True)
    S.halo(W.X(0) + k * 14 + 5, W.Y(2) - 6, '14', 12, LOAD, 'start', bold=True)
    S.halo(W.X(0) + k * 34 + 5, W.Y(4) - 6, '34', 12, LOAD, 'start', bold=True)
    S.halo(W.X(0) - 6, W.Y(0) + 4, '0', 12, LOAD, 'end', bold=True)
    S.halo(W.X(0) - 6, W.Y(2) + 4, 'B：跳 −6', 11.5, MOM, 'end')
    S.halo(W.X(2), W.Y(4) + k * beam(2) + 15, '34.67', 11.5, LOAD, bold=True)
    S.halo(W.X(3), W.Y(4) + k * 33 + 15, '33', 11.5, LOAD, bold=True)
    S.halo(W.X(5.5), W.Y(4) + k * 4 + 16, '梁側 4 → 0', 11.5, MOM, 'end', bold=True)
    S.halo(W.X(6) - k * 4 - 6, W.Y(2) + 4, '4', 12, LOAD, 'end', bold=True)
    S.halo(W.X(6) - k * 4 - 6, W.Y(3.2), '柱側 4 → 0', 11.5, MOM, 'end', bold=True)
    S.halo(W.X(6) - 6, W.Y(1) + 4, '拋物線', 11, LOAD, 'end')
    S.text(W.X(0) + 2, 362, '紫色＝集中力矩造成的跳躍；內鉸 F 的梁側、柱側各自由 4 歸零', 11.5, MOM, 'start')
    S.text(W.X(0) + 2, 380, '左柱斜率 = 10（B 跳躍前後平行）；C–D 斜率 = V + m = 1/3', 11.5, INK, 'start')
    return S.render()


# ---------------------------------------------------------------- 3-1 zero-force rules with projection axis
def fig_3_1():
    S = SVG(820, 270, '零力桿兩法則')
    import math
    # rule 1
    S.text(205, 24, '法則一｜無載重的二桿節點', 15, '#0d47a1', bold=True)
    n = (205, 92)
    a1 = math.radians(210); a2 = math.radians(-25)
    p1 = (n[0] + 130 * math.cos(a1), n[1] - 130 * math.sin(a1))
    p2 = (n[0] + 130 * math.cos(a2), n[1] - 130 * math.sin(a2))
    S.line(*n, *p1, LOAD, 4, dash='8 4'); S.line(*n, *p2, LOAD, 4, dash='8 4')
    S.node(*n, 6)
    S.text(p1[0] + 20, p1[1] + 22, '桿 1', 12.5, INK)
    S.text(p2[0] - 10, p2[1] + 22, '桿 2', 12.5, INK)
    # axis perpendicular to member 1
    perp = a1 + math.pi / 2
    q1 = (n[0] + 52 * math.cos(perp), n[1] - 52 * math.sin(perp))
    q2 = (n[0] - 85 * math.cos(perp), n[1] + 85 * math.sin(perp))
    S.line(*q1, *q2, REAC, 1.8, dash='6 4')
    S.text(q2[0] + 6, q2[1] + 4, 'n ⟂ 桿 1', 12, REAC, 'start', bold=True)
    S.text(205, 200, 'ΣF_n = 0：桿 1 在 n 方向無分量', 12.5, INK)
    S.text(205, 220, '⟹ F₂ sinθ = 0 ⟹ F₂ = 0，再換方向 ⟹ F₁ = 0', 12.5, LOAD, bold=True)
    S.text(205, 244, '（兩桿不共線才成立）', 11.5, MUT)
    # rule 2
    S.text(610, 24, '法則二｜無載重、三桿中兩桿共線', 15, '#0d47a1', bold=True)
    n = (610, 120)
    S.line(470, 120, 750, 120, GOOD, 4)
    S.line(n[0], n[1], n[0] + 70, n[1] - 75, LOAD, 4, dash='8 4')
    S.node(*n, 6)
    S.text(500, 110, 'F₁', 13, GOOD, bold=True); S.text(720, 110, 'F₂', 13, GOOD, bold=True)
    S.text(n[0] + 80, n[1] - 76, 'F₃', 13, LOAD, 'start', bold=True)
    S.line(610, 40, 610, 186, REAC, 1.8, dash='6 4')
    S.text(616, 184, 'n ⟂ 共線方向', 12, REAC, 'start', bold=True)
    S.text(610, 210, 'ΣF_n = 0：F₁、F₂ 在 n 方向都沒有分量', 12.5, INK)
    S.text(610, 230, '⟹ F₃ = 0；沿共線方向 ⟹ F₁ = F₂', 12.5, LOAD, bold=True)
    S.text(610, 252, '（第三桿與共線桿夾任何角度都成立）', 11.5, MUT)
    return S.render()


# ---------------------------------------------------------------- 3-2 Ritter generic with lever arm
def fig_3_2():
    import math
    S = SVG(900, 330, 'Ritter 截面法')
    S.text(450, 24, '同一個截面，換力矩中心就換出一根桿（取左半自由體）', 15, '#0d47a1', bold=True)
    W = World(40, 262, 30)
    N = {'L0': (0, 0), 'L1': (4, 0), 'L2': (8, 0), 'L3': (12, 0), 'L4': (16, 0),
         'U1': (4, 3), 'U2': (8, 3), 'U3': (12, 3)}
    left = ['L0L1', 'L0U1', 'U1L1']
    right = ['L2L3', 'L3L4', 'U2U3', 'U3L4', 'U2L2', 'U3L3', 'L2U3']
    cut = {'U1U2': '上弦', 'U1L2': '斜桿', 'L1L2': '下弦'}
    for m in right:
        S.line(*W(*N[m[:2]]), *W(*N[m[2:]]), GHOST, 2.2)
    for m in left:
        S.line(*W(*N[m[:2]]), *W(*N[m[2:]]), INK, 3)
    xc = 6.0
    # stubs up to cut and force arrows (tension = away from the left FBD)
    def stub(a, b, lab, col):
        (x1, y1), (x2, y2) = N[a], N[b]
        t = (xc - x1) / (x2 - x1)
        xm, ym = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
        S.line(*W(x1, y1), *W(xm, ym), INK, 3)
        S.line(*W(xm, ym), *W(x2, y2), GHOST, 2.2)
        ang = math.atan2(-(y2 - y1), (x2 - x1))
        p = W(xm, ym)
        q = (p[0] + 46 * math.cos(ang), p[1] + 46 * math.sin(ang))
        S.arrow(*p, *q, col, 2.6)
        return q
    q = stub('U1', 'U2', '上弦', GOOD); S.text(q[0] + 4, q[1] - 6, 'F上弦', 12.5, GOOD, 'start', bold=True)
    q = stub('U1', 'L2', '斜桿', REAC); S.text(q[0] + 6, q[1] + 2, 'F斜', 12.5, REAC, 'start', bold=True)
    q = stub('L1', 'L2', '下弦', ORG); S.text(q[0] - 6, q[1] - 8, 'F下弦', 12.5, ORG, 'end', bold=True)
    S.line(W.X(xc), W.Y(3) - 30, W.X(xc), W.Y(0) + 30, LOAD, 2, dash='9 5')
    S.text(W.X(xc), W.Y(3) - 36, '截面', 12.5, LOAD, bold=True)
    for k, v in N.items():
        S.node(*W(*v), 3.2, INK if v[0] <= 4 else GHOST)
    S.pin(*W(0, 0)); S.roller(*W(16, 0), c=GHOST)
    S.arrow(W.X(0), W.Y(0) + 56, W.X(0), W.Y(0) + 6, REAC, 2.4)
    S.text(W.X(0) + 6, W.Y(0) + 50, 'R', 12.5, REAC, 'start', bold=True)
    # load P at L1 (downward, drawn below node)
    S.arrow(W.X(4), W.Y(0) + 10, W.X(4), W.Y(0) + 48, LOAD, 2.4)
    S.text(W.X(4) + 6, W.Y(0) + 46, 'P', 12.5, LOAD, 'start', bold=True)
    # moment centres
    u1, l2 = W(4, 3), W(8, 0)
    S.circ(*u1, 7, MOM, '#fff', 2); S.text(u1[0] - 10, u1[1] - 10, 'U（求下弦的中心）', 12, MOM, 'end', bold=True)
    S.circ(*l2, 7, ORG, '#fff', 2); S.text(l2[0] + 12, l2[1] + 26, 'L（求上弦的中心）', 12, ORG, 'start', bold=True)
    S.dim(*W(2.4, 0), *W(2.4, 3), 'd', off=0)
    # rule panel
    S.rect(560, 52, 330, 260, '#f7f9fb', '#cfd8dc', 1, rx=9)
    S.text(725, 78, '選擇規則', 13.5, '#0d47a1', bold=True)
    rows = [
        ('要 下弦 → 對 U 取矩（上弦、斜桿都過 U）', ORG),
        ('　F下弦 · d = M_U　⟹　F下弦 = M_U / d', ORG),
        ('要 上弦 → 對 L 取矩（斜桿、下弦都過 L）', GOOD),
        ('　F上弦 · d = −M_L', GOOD),
        ('要 斜桿 → ΣFy = 0（上下弦水平時）', REAC),
        ('　F斜 · sinα = 截面剪力 V', REAC),
        ('上下弦不平行：斜桿也用取矩，', INK),
        ('　中心取上下弦延長線的交點', INK),
        ('力臂算不清 → 點到直線距離公式', LOAD),
    ]
    for i, (t, c) in enumerate(rows):
        S.text(578, 106 + i * 23, t, 12.2, c, 'start')
    return S.render()


# ---------------------------------------------------------------- 3-3 SA-2002-2 cut for the tie force
def fig_3_3():
    import math
    S = SVG(900, 380, 'SA-2002-2 截面法求繫索拉力')
    S.text(450, 22, 'SA-2002-2（依比例）：切 FC、EC、AB，取左半對 C 取矩', 14.5, '#0d47a1', bold=True)
    W = World(115, 270, 12.5)
    P = dict(A=(0, 0), B=(32, 0), D=(0, 12), F=(8, 12), C=(16, 12), H=(24, 12), I=(32, 12),
             E=(8, 6), G=(24, 6))
    lab = {'DF': 'a', 'DE': 'b', 'AE': 'c', 'CH': 'd', 'CG': 'e'}
    leftm = ['DF', 'AD', 'FE', 'DE', 'AE']
    rightm = ['CH', 'HI', 'BI', 'HG', 'CG', 'GB', 'GI']
    for m in rightm:
        S.line(*W(*P[m[0]]), *W(*P[m[1]]), GHOST, 2.2)
    S.line(*W(*P['A']), *W(*P['B']), GHOST, 2.2, dash='8 5')
    for m in leftm:
        S.line(*W(*P[m[0]]), *W(*P[m[1]]), INK, 3)
    xc = 12.0

    def stub(a, b, col, lab_, dy):
        (x1, y1), (x2, y2) = P[a], P[b]
        t = (xc - x1) / (x2 - x1)
        xm, ym = x1 + t * (x2 - x1), y1 + t * (y2 - y1)
        S.line(*W(x1, y1), *W(xm, ym), col if a == 'A' else INK, 3, dash='8 5' if a == 'A' else None)
        S.line(*W(xm, ym), *W(x2, y2), GHOST, 2.2, dash='8 5' if a == 'A' else None)
        ang = math.atan2(-(y2 - y1), (x2 - x1))
        p = W(xm, ym)
        q = (p[0] + 32 * math.cos(ang), p[1] + 32 * math.sin(ang))
        S.arrow(*p, *q, col, 2.6)
        S.halo(q[0] + (4 if dy > 0 else -2), q[1] + dy, lab_, 12, col, 'start' if dy > 0 else 'end', bold=True)
    stub('F', 'C', GOOD, 'F_FC', -10)
    stub('E', 'C', GOOD, 'F_EC', 14)
    stub('A', 'B', REAC, 'F_AB（繫索）', 16)
    S.line(W.X(xc), W.Y(12) - 26, W.X(xc), W.Y(0) + 26, LOAD, 2, dash='9 5')
    for k, v in P.items():
        S.node(*W(*v), 3.4, INK if v[0] <= 8 else GHOST)
        S.text(W.X(v[0]) + (-9 if v[0] == 0 else 8), W.Y(v[1]) + (-8 if v[1] == 12 else 16), k, 12,
               INK if v[0] <= 8 else MUT, 'end' if v[0] == 0 else 'start', bold=True)
    for m, l in lab.items():
        (x1, y1), (x2, y2) = P[m[0]], P[m[1]]
        S.halo(W.X((x1 + x2) / 2) + 6, W.Y((y1 + y2) / 2) - 5, l, 12.5, MOM, 'start', bold=True)
    # loads
    for nd in ('D', 'F', 'C', 'H', 'I'):
        x, y = W(*P[nd])
        c = LOAD if P[nd][0] <= 8 else '#ef9a9a'
        S.arrow(x, y - 40, x, y - 6, c, 2.2)
        S.text(x + 4, y - 32, '20', 11, c, 'start')
    x, y = W(*P['D'])
    S.arrow(x - 48, y, x - 6, y, LOAD, 2.4); S.text(x - 30, y - 7, '16', 11, LOAD)
    # reactions
    x, y = W(0, 0)
    S.pin(x, y, s=0.85)
    S.arrow(x - 4, y + 4, x - 48, y + 4, REAC, 2.4); S.text(x - 50, y + 1, 'A_x = 16', 11.5, REAC, 'end', bold=True)
    S.arrow(x + 20, y + 44, x + 20, y + 10, REAC, 2.4); S.text(x + 26, y + 40, 'A_y = 44', 11.5, REAC, 'start', bold=True)
    xb, yb = W(32, 0)
    S.roller(xb, yb, s=0.85, c=GHOST)
    S.text(xb - 14, yb + 32, 'B_y = 56', 11, MUT, 'end')
    # moment centre and arm
    c = W(16, 12)
    S.circ(*c, 8, MOM, '#fff', 2)
    S.text(c[0], c[1] - 48, '力矩中心 C (16, 12)', 12, MOM, bold=True)
    S.line(c[0], c[1] + 8, c[0], W.Y(0), MOM, 1.2, dash='3 3')
    S.dim(W.X(16) + 14, W.Y(12), W.X(16) + 14, W.Y(0), '12 m', off=0)
    # result panel
    S.rect(560, 300, 330, 72, '#f3e5f5', '#ce93d8', 1, rx=8)
    S.text(575, 322, 'ΣM_C = −44(16) −16(12) +20(16) +20(8) +12F_AB = 0', 11.5, MOM, 'start')
    S.text(575, 342, '⟹ F_AB = 104/3 ≈ 34.7 T（拉）✓ 繫索必為拉', 12, MOM, 'start', bold=True)
    S.text(575, 362, 'a = 88/3 壓　b = 50/3 拉　c = 70/3 壓　d = 40/3 壓　e = 80/3 壓', 11, INK, 'start')
    return S.render()


# ---------------------------------------------------------------- 4-1 exact w-V-M shapes
def fig_4_1():
    S = SVG(880, 420, 'w-V-M 四種載重')
    rows = {'w': 66, 'V': 190, 'M': 330}
    S.text(20, 60, '載重 w', 14, '#0d47a1', 'start', bold=True)
    S.text(20, 186, '剪力 V', 14, '#0d47a1', 'start', bold=True)
    S.text(20, 326, '彎矩 M', 14, '#0d47a1', 'start', bold=True)
    cols = [(150, '無載重段'), (340, '均佈載重 w'), (530, '集中力 P'), (720, '集中力矩 M₀')]
    Wd = 140
    n = 140
    def X(c, u):
        return c + Wd * u
    for k, (c, title) in enumerate(cols):
        S.text(c + Wd / 2, 26, title, 13.5, INK, bold=True)
        for base in (rows['V'], rows['M']):
            S.line(c - 4, base, c + Wd + 4, base, GHOST, 1)
        S.line(c, rows['w'], c + Wd, rows['w'], INK, 3)
    kV = 50
    # col 1: no load: V = 0.6, M = 0.6u
    c = cols[0][0]
    S.text(c + Wd / 2, rows['w'] + 26, 'w = 0', 12, MUT)
    V = lambda u: 0.6
    S.pl([(X(c, 0), rows['V'] - kV * 0.6), (X(c, 1), rows['V'] - kV * 0.6)], REAC, 2.6)
    S.pl([(X(c, 0), rows['M'] + 25), (X(c, 1), rows['M'] + 25 - kV * 0.6 * 1.2)], LOAD, 2.6)
    S.text(c + Wd / 2, rows['V'] + 30, '水平（定值）', 12, MUT)
    S.text(c + Wd / 2, rows['M'] + 50, '斜直線，斜率 = V', 12, MUT)
    # col 2: uniform w=1.2 : V = 0.66-1.2u ; M = 0.66u - 0.6u^2
    c = cols[1][0]
    for i in range(8):
        x = X(c, (i + 0.5) / 8)
        S.arrow(x, rows['w'] - 24, x, rows['w'] - 3, LOAD, 1.5, L=7, W=3)
    S.line(c, rows['w'] - 24, c + Wd, rows['w'] - 24, LOAD, 1.4)
    pV = [(X(c, i / n), rows['V'] - kV * (0.66 - 1.2 * i / n)) for i in range(n + 1)]
    kM = 160
    pM = [(X(c, i / n), rows['M'] + 10 - kM * (0.66 * i / n - 0.6 * (i / n) ** 2)) for i in range(n + 1)]
    S.pl(pV, REAC, 2.6); S.pl(pM, LOAD, 2.6)
    u0 = 0.55
    S.line(X(c, u0), rows['V'], X(c, u0), rows['M'] + 10 - kM * (0.66 * u0 - 0.6 * u0 ** 2), ORG, 1.2, dash='3 3')
    S.circ(X(c, u0), rows['V'], 4, ORG, ORG, 1)
    S.circ(X(c, u0), rows['M'] + 10 - kM * (0.66 * u0 - 0.6 * u0 ** 2), 4, ORG, ORG, 1)
    S.text(c + Wd / 2, rows['V'] + 52, '斜直線；過零點 = M 極值', 12, MUT)
    S.text(c + Wd / 2, rows['M'] + 50, '拋物線（2 次）', 12, MUT)
    # col 3: point load at 0.5
    c = cols[2][0]
    S.arrow(X(c, .5), rows['w'] - 32, X(c, .5), rows['w'] - 3, LOAD, 2.6)
    S.text(X(c, .5) + 8, rows['w'] - 20, 'P', 13, LOAD, 'start', bold=True)
    S.pl([(X(c, 0), rows['V'] - kV * .45), (X(c, .5), rows['V'] - kV * .45), (X(c, .5), rows['V'] + kV * .45),
          (X(c, 1), rows['V'] + kV * .45)], REAC, 2.6)
    S.text(X(c, .5) + 6, rows['V'] - 2, '跳 P', 12, LOAD, 'start', bold=True)
    S.pl([(X(c, 0), rows['M'] + 18), (X(c, .5), rows['M'] + 18 - 0.45 * .5 * 160), (X(c, 1), rows['M'] + 18)], LOAD, 2.6)
    S.text(c + Wd / 2, rows['V'] + 52, 'V 垂直跳躍，量 = P', 12, MUT)
    S.text(c + Wd / 2, rows['M'] + 50, 'M 折點（連續、不平滑）', 12, MUT)
    # col 4: moment M0 at 0.5 ; V=0.3 ; M = 0.3u*k + jump
    c = cols[3][0]
    S.moment(X(c, .5), rows['w'] - 2, 13, ccw=False, c=MOM, a0=200, span=250)
    S.text(X(c, .5) + 18, rows['w'] - 18, 'M₀', 13, MOM, 'start', bold=True)
    S.pl([(X(c, 0), rows['V'] - kV * 0.35), (X(c, 1), rows['V'] - kV * 0.35)], REAC, 2.6)
    kM = 100
    m = lambda u: 0.35 * u - 0.15 + (0.35 if u > 0.5 else 0)
    p1 = [(X(c, u), rows['M'] - kM * m(u)) for u in (0, 0.5)]
    p2 = [(X(c, u), rows['M'] - kM * (0.35 * u - 0.15 + 0.35)) for u in (0.5, 1)]
    S.pl(p1, LOAD, 2.6); S.pl(p2, LOAD, 2.6)
    S.line(*p1[1], *p2[0], MOM, 2.6)
    S.text(p1[1][0] + 6, (p1[1][1] + p2[0][1]) / 2 + 4, '跳 M₀', 12, MOM, 'start', bold=True)
    # parallel guide
    S.line(p1[1][0], p1[1][1], p1[1][0] + 70, p1[1][1] - kM * 0.35 * 0.5, LOAD, 1, dash='3 3')
    S.text(c + Wd / 2, rows['V'] + 30, 'V 完全不變', 12, MUT)
    S.text(c + Wd / 2, rows['M'] + 50, 'M 跳躍；前後兩段平行', 12, MUT)
    S.text(440, 408, '每欄的 V、M 曲線都由 dV/dx = −w、dM/dx = V 直接積分繪出（同欄同比例）', 11.5, MUT)
    return S.render()


# ---------------------------------------------------------------- 4-2 joint C exploded (SA-2002-1)
def fig_4_2():
    S = SVG(900, 330, '剛節點 C 自由體')
    S.text(450, 22, 'SA-2002-1 剛節點 C 拆成三塊：柱頂、節點、梁端（數值取自校正後解析）', 14, '#0d47a1', bold=True)
    # column stub
    cx, top = 250, 205
    S.rect(cx - 9, top, 18, 95, '#eceff1', INK, 1.6)
    S.text(cx, 320, '柱頂（內側=右側受拉）', 11.5, INK)
    S.arrow(cx, top - 2, cx, top - 40, REAC, 2.4); S.text(cx - 6, top - 30, '5/3（拉）', 11.5, REAC, 'end', bold=True)
    S.arrow(cx + 4, top + 12, cx + 50, top + 12, GOOD, 2.4); S.text(cx + 54, top + 16, '10', 11.5, GOOD, 'start', bold=True)
    S.moment(cx, top + 34, 18, ccw=True, c=MOM, a0=-70, span=230)
    S.text(cx - 26, top + 64, '34（逆）', 11.5, MOM, 'end', bold=True)
    # joint
    jx, jy = 440, 150
    S.rect(jx - 22, jy - 22, 44, 44, '#fff8e1', ORG, 2, rx=4)
    S.text(jx, jy + 5, 'C', 14, ORG, bold=True)
    S.arrow(jx, jy + 24, jx, jy + 62, REAC, 2.4); S.text(jx + 6, jy + 58, '5/3', 11.5, REAC, 'start', bold=True)
    S.arrow(jx - 6, jy + 18, jx - 52, jy + 18, GOOD, 2.4); S.text(jx - 56, jy + 22, '10（柱給）', 11.5, GOOD, 'end', bold=True)
    S.arrow(jx - 76, jy - 10, jx - 24, jy - 10, LOAD, 2.6); S.text(jx - 56, jy - 18, '10 kN 外力', 11.5, LOAD, bold=True)
    S.arrow(jx + 30, jy + 40, jx + 30, jy + 4, REAC, 2.4); S.text(jx + 36, jy + 40, '5/3', 11.5, REAC, 'start', bold=True)
    S.moment(jx, jy, 34, ccw=False, c=MOM, a0=250, span=100)
    S.text(jx - 34, jy + 46, '34（順）', 11.5, MOM, 'end', bold=True)
    S.moment(jx, jy, 34, ccw=True, c=MOM, a0=-30, span=100)
    S.text(jx + 34, jy - 36, '34（逆）', 11.5, MOM, 'start', bold=True)
    S.text(jx, jy + 96, '節點：ΣFx = 10 − 10 + N梁 = 0', 11.5, INK)
    S.text(jx, jy + 114, 'ΣFy = −5/3 + 5/3 = 0　ΣM = 34 − 34 = 0', 11.5, INK)
    # beam stub
    bx, by = 600, 150
    S.rect(bx, by - 9, 150, 18, '#eceff1', INK, 1.6)
    S.text(bx + 75, by + 34, '梁端（內側=下側受拉）', 11.5, INK)
    S.arrow(bx + 8, by - 46, bx + 8, by - 11, REAC, 2.4); S.text(bx + 14, by - 38, '5/3', 11.5, REAC, 'start', bold=True)
    S.moment(bx + 4, by, 22, ccw=False, c=MOM, a0=250, span=200)
    S.text(bx - 22, by - 24, '34（順）', 11.5, MOM, 'end', bold=True)
    S.text(bx + 75, by - 20, 'N梁 = 0', 12, GOOD, bold=True)
    # summary
    S.rect(560, 210, 330, 104, '#f7f9fb', '#cfd8dc', 1, rx=8)
    S.text(575, 234, '柱的「軸力」5/3 → 梁的「剪力」5/3', 12.2, REAC, 'start', bold=True)
    S.text(575, 256, '柱的「剪力」10 → 與外力 10 抵銷 → 梁軸力 0', 12.2, GOOD, 'start', bold=True)
    S.text(575, 278, '彎矩 34 原封不動傳過去', 12.2, MOM, 'start', bold=True)
    S.text(575, 300, '受拉側：柱的右側（內）→ 梁的下側（內）', 12.2, LOAD, 'start')
    return S.render()

# ======================= figs_c.py =======================
"""§5–§6 figures"""


# ---------------------------------------------------------------- 5-1 conjugate beam supports
def fig_5_1():
    S = SVG(840, 360, '共軛梁支承轉換')
    S.text(420, 24, '共軛梁支承轉換：「位移 y ↔ 彎矩 M̄、轉角 θ ↔ 剪力 V̄」逐條推出來', 14.5, '#0d47a1', bold=True)
    S.line(420, 44, 420, 348, GHOST, 1.5, dash='6 5')
    S.text(215, 56, '實梁', 14, GOOD, bold=True)
    S.text(625, 56, '共軛梁', 14, LOAD, bold=True)
    rows = [
        ('fixedL', '固定端：y = 0，θ = 0', 'free', '自由端：M̄ = 0，V̄ = 0'),
        ('freeR', '自由端：y ≠ 0，θ ≠ 0', 'fixedR', '固定端：M̄ ≠ 0，V̄ ≠ 0'),
        ('pinL', '端點鉸／滾：y = 0，θ ≠ 0', 'pinL', '端點鉸／滾：M̄ = 0，V̄ ≠ 0'),
        ('intsup', '內部支承：y = 0，θ 連續', 'inthinge', '內鉸：M̄ = 0，V̄ 連續'),
        ('inthinge', '內鉸：y 連續，θ 可跳', 'intsup', '內部支承：M̄ 連續，V̄ 可跳'),
    ]

    def draw(kind, x0, y, col):
        xa, xb = x0, x0 + 110
        if kind in ('fixedL',):
            S.line(xa, y, xb, y, INK, 4); S.fixed(xa, y, rot=90, s=0.9, half=14)
        elif kind == 'fixedR':
            S.line(xa, y, xb, y, INK, 4); S.fixed(xb, y, rot=-90, s=0.9, half=14)
        elif kind == 'free':
            S.line(xa, y, xb, y, INK, 4); S.circ(xa, y, 4, col, col, 1)
        elif kind == 'freeR':
            S.line(xa, y, xb, y, INK, 4); S.circ(xb, y, 4, col, col, 1)
        elif kind == 'pinL':
            S.line(xa, y, xb, y, INK, 4); S.pin(xa, y, s=0.75)
        elif kind == 'intsup':
            S.line(xa - 10, y, xb + 10, y, INK, 4); S.roller((xa + xb) / 2, y, s=0.75)
        elif kind == 'inthinge':
            S.line(xa - 10, y, xb + 10, y, INK, 4); S.hinge((xa + xb) / 2, y, 6, col)

    for i, (k1, t1, k2, t2) in enumerate(rows):
        y = 96 + i * 56
        draw(k1, 50, y, GOOD)
        S.text(190, y + 5, t1, 12.5, INK, 'start')
        draw(k2, 460, y, LOAD)
        S.text(600, y + 5, t2, 12.5, LOAD, 'start')
        S.text(420, y + 5, '⇄', 15, MUT)
    return S.render()


# ---------------------------------------------------------------- 5-2 SA-2003-2 displaced shape
def fig_5_2():
    S = SVG(900, 330, 'SA-2003-2 變位圖')
    S.text(450, 22, 'SA-2003-2：剛梁＋三連桿（幾何依比例；位移放大顯示，單位 Fλ/EA）', 14, '#0d47a1', bold=True)
    W = World(80, 92, 46)
    k = 4.6                                      # px per (F·λ/EA)
    uA, vA, th = 9 / 4, 3.0, -9 / 4              # th in F/EA per λ
    def disp(x):                                  # rigid beam displacement at x (λ)
        return uA, vA + x * th
    assert abs(disp(4)[1] + 6) < 1e-12 and abs(disp(8)[1] + 15) < 1e-12
    A, B, C, D, E = W(0, 0), W(4, 0), W(8, 0), W(0, -3), W(4, -3)
    # original (ghost)
    S.line(*A, *C, GHOST, 5)
    for p, q in ((A, D), (B, E), (A, E)):
        S.line(*p, *q, GHOST, 2.5)
    # displaced
    def dp(x):
        u, v = disp(x)
        return W.X(x) + k * u, W.Y(0) - k * v
    A2, B2, C2 = dp(0), dp(4), dp(8)
    S.line(*A2, *C2, LOAD, 4.5)
    S.line(*D, *A2, LOAD, 1.8, dash='5 3'); S.line(*E, *A2, LOAD, 1.8, dash='5 3'); S.line(*E, *B2, LOAD, 1.8, dash='5 3')
    S.pin(*D); S.pin(*E)
    for p in (A, B, C):
        S.node(*p, 3)
    S.hinge(*A2, 4, LOAD); S.hinge(*B2, 4, LOAD)
    for p, t, dx, dy in ((A, 'A', -10, -8), (B, 'B', 6, -10), (C, 'C', 8, -8), (D, 'D', -16, 6), (E, 'E', 14, 6)):
        S.text(p[0] + dx, p[1] + dy, t, 13, INK, 'end' if dx < 0 else 'start', bold=True)
    # load
    S.arrow(C2[0], C2[1] - 46, C2[0], C2[1] - 6, LOAD, 2.6); S.text(C2[0] + 6, C2[1] - 36, 'F', 13, LOAD, 'start', bold=True)
    # member force labels on original links
    S.halo(W.X(0) + 8, W.Y(-2.6), 'AD：F（拉）', 12, REAC, 'start', bold=True)
    S.halo(W.X(2.3), W.Y(-1.25), 'AE：0', 12, REAC, 'start', bold=True)
    S.halo(W.X(4) + 8, W.Y(-2.45), 'BE：2F（壓）', 12, REAC, 'start', bold=True)
    # displacement callouts
    S.line(C[0], C[1], C[0] + 40, C[1], ORG, 0.8, dash='2 2'); S.line(C2[0], C2[1], C[0] + 40, C2[1], ORG, 0.8, dash='2 2')
    S.arrow(C[0] + 36, C[1], C[0] + 36, C2[1], ORG, 1.6, L=8, W=3.5)
    S.halo(C[0] + 42, (C[1] + C2[1]) / 2 + 4, 'v_C = 15 ↓', 12.5, ORG, 'start', bold=True)
    S.halo(B2[0] + 10, B2[1] + 42, 'v_B = 6 ↓（= BE 縮短 6）', 11.5, ORG, 'start')
    S.halo(A2[0] + 8, A2[1] - 10, 'A′：u = 9/4 →，v = 3 ↑', 11.5, ORG, 'start')
    S.dim(*W(0, -3), *W(4, -3), '4λ', off=30, lab_off=14)
    S.dim(*W(4, -3), *W(8, -3), '4λ', off=30, lab_off=14)
    S.dim(*W(0, 0), *W(0, -3), '3λ', off=40)
    # panel
    S.rect(560, 150, 330, 165, '#f7f9fb', '#cfd8dc', 1, rx=9)
    rows = [('① 零力桿 AE 卻逼出水平位移：', INK, True),
            ('　e_AE = −0.8u_A + 0.6v_A = 0 ⟹ u_A = ¾ v_A', INK, False),
            ('② 剛梁小轉角：v_B = v_A + 4λθ = e_BE', INK, True),
            ('　3 + 4λθ = −6 ⟹ θ = −9F/4EA（順時針）', INK, False),
            ('③ v_C = v_A + 8λθ = 3 − 18 = −15', LOAD, True),
            ('灰＝原位置；紅＝變位後（放大）', MUT, False)]
    for i, (t, c, b) in enumerate(rows):
        S.text(574, 174 + i * 24, t, 12, c, 'start', bold=b)
    return S.render()


# ---------------------------------------------------------------- 6-1 settlement: determinate vs indeterminate (exact curve)
def fig_6_1():
    S = SVG(860, 340, '靜定 vs 靜不定 沉陷')
    S.line(430, 14, 430, 326, GHOST, 2, dash='7 5')
    S.text(215, 32, '靜定：讓得開', 15, GOOD, bold=True)
    S.text(645, 32, '靜不定：讓不開', 15, LOAD, bold=True)
    D = 36
    # left
    xa, xb, y = 70, 360, 100
    S.line(xa, y, xb, y, GHOST, 2, dash='5 4')
    S.line(xa, y, xb, y + D, GOOD, 4.5)
    S.pin(xa, y); S.roller(xb, y + D)
    S.arrow(xb + 26, y, xb + 26, y + D, ORG, 2, L=8, W=3.5)
    S.text(xb + 32, y + D / 2 + 4, 'Δ', 14, ORG, 'start', bold=True)
    S.line(xa, 196, xb, 196, LOAD, 2.5)
    S.text(xa - 6, 200, 'M', 13, LOAD, 'end', bold=True)
    S.text(215, 190, 'M ≡ 0', 12.5, LOAD, bold=True)
    S.text(215, 232, '梁保持直線，只繞 A 轉了 Δ/L', 13, '#1b5e20')
    S.text(215, 254, '曲率 = 0 ⟹ M = 0 ⟹ 全無內力', 13, '#1b5e20')
    S.text(215, 282, '位移是純剛體轉動，靠幾何比例就能算', 12.5, MUT)
    S.text(215, 304, '材料換成橡皮或鑽石，答案完全一樣', 12.5, MUT)
    # right: two equal spans, middle support settles; exact shape
    xa, xm, xb = 480, 645, 810
    L = xm - xa
    S.line(xa, y, xb, y, GHOST, 2, dash='5 4')
    pts = []
    for i in range(0, 101):
        xi = i / 100
        v = D * (1.5 * xi - 0.5 * xi ** 3)
        pts.append((xa + L * xi, y + v))
    pts += [(xb - (p[0] - xa), p[1]) for p in reversed(pts[:-1])]
    S.pl(pts, LOAD, 4.5)
    S.pin(xa, y); S.roller(xm, y + D); S.roller(xb, y)
    S.arrow(xm + 24, y, xm + 24, y + D, ORG, 2, L=8, W=3.5)
    S.text(xm + 30, y + D / 2 + 4, 'Δ', 14, ORG, 'start', bold=True)
    # M diagram (triangle, sagging, drawn below)
    S.line(xa, 176, xb, 176, LOAD, 1)
    S.area([(xa, 176), (xm, 214), (xb, 176)], LOAD, 0.18)
    S.pl([(xa, 176), (xm, 214), (xb, 176)], LOAD, 2.2)
    S.text(xa - 6, 180, 'M', 13, LOAD, 'end', bold=True)
    S.text(xm, 230, 'M_max = 3EIΔ / L²（L = 單跨長）', 11.5, LOAD, bold=True)
    S.text(645, 254, '曲率 ≠ 0 ⟹ M ≠ 0 ⟹ 產生內力', 13, '#b71c1c')
    S.text(645, 282, '曲線 y = Δ(1.5ξ − 0.5ξ³)：同跨中集中力的彈性曲線', 12, MUT)
    S.text(645, 304, '內力正比於 EI ／ 沉陷量 → SA-U2 的題目', 12.5, MUT)
    return S.render()


# ---------------------------------------------------------------- 6-2 SA-2024-2 rigid-body line
def fig_6_2():
    S = SVG(900, 440, 'SA-2024-2 剛體位移線')
    S.text(450, 20, 'SA-2024-2（依比例）：F 沉陷 12 mm 造成的剛體位移，與量測值的差 = 桿件變形的貢獻', 13.5, '#0d47a1', bold=True)
    W = World(85, 150, 30)
    bot = 'ABCDEFG'; top = 'HIJKLMN'
    P = {bot[i]: (4 * i, 0) for i in range(7)}
    P.update({top[i]: (4 * i, 3) for i in range(7)})
    mem = [bot[i] + bot[i + 1] for i in range(6)] + [top[i] + top[i + 1] for i in range(6)] + \
          [bot[i] + top[i] for i in range(7)] + ['HB', 'BJ', 'JD', 'DL', 'LF', 'FN']
    assert len(mem) == 25
    for m in mem:
        c, w = INK, 2
        if m == 'CD':
            c, w = MOM, 4.5
        if m == 'DE':
            c, w = ORG, 4.5
        S.line(*W(*P[m[0]]), *W(*P[m[1]]), c, w)
    for k, v in P.items():
        S.node(*W(*v), 3)
        if k in top:
            S.text(W.X(v[0]), W.Y(3) - 9, k, 12, INK, bold=True)
    S.roller(*W(4, 0), s=0.85); S.pin(*W(20, 0), s=0.85)
    for k in bot:
        dx = -8 if k in 'BF' else 0
        S.text(W.X(P[k][0]) + dx, W.Y(0) + (36 if k in 'BF' else 17), k, 12, INK, bold=True)
    S.halo(W.X(10), W.Y(0) - 7, 'CD：δ', 12, MOM, bold=True)
    S.halo(W.X(14), W.Y(0) - 7, 'DE：ΔT', 12, ORG, bold=True)
    S.arrow(W.X(20) + 26, W.Y(0) + 4, W.X(20) + 26, W.Y(0) + 30, ORG, 2, L=7, W=3)
    S.text(W.X(20) + 32, W.Y(0) + 24, '12 mm', 11.5, ORG, 'start', bold=True)
    # displacement plot (down positive)
    y0, k = 262, 7.0
    S.text(W.X(24), y0 - 40, '下弦節點垂直位移（mm，向下為正）', 12, '#0d47a1', 'end', bold=True)
    S.line(W.X(0) - 10, y0, W.X(24) + 10, y0, GHOST, 1.2)
    rig = lambda x: 12 * (x - 4) / 16
    S.line(W.X(0), y0 + k * rig(0), W.X(24), y0 + k * rig(24), REAC, 2, dash='7 4')
    S.halo(W.X(0.6), y0 + k * rig(0.6) - 14, '剛體位移線 Δ = 12(x−4)/16（B 不動）', 11.5, REAC, 'start')
    for nd in bot:
        x = P[nd][0]
        S.circ(W.X(x), y0 + k * rig(x), 3.4, REAC, '#fff', 1.2)
        S.line(W.X(x), W.Y(0) + 6, W.X(x), y0 - 4, GHOST, 0.8, dash='2 3')
    for x, val in ((0, '−3'), (4, '0'), (20, '12'), (24, '15')):
        S.halo(W.X(x) - 7, y0 + k * rig(x) + (16 if x != 0 else 4), val, 11, REAC, 'end')
    for x, meas, lab in ((8, 4.8, '+1.8'), (16, 6.4, '−2.6')):
        r = rig(x)
        S.circ(W.X(x), y0 + k * meas, 5, ORG, '#fff', 1.5)
        S.arrow(W.X(x) + 14, y0 + k * r, W.X(x) + 14, y0 + k * meas, MOM, 2, L=7, W=3)
        S.halo(W.X(x) + 20, y0 + k * (r + meas) / 2 + 4, f'{lab} mm（桿件變形）', 11.5, MOM, 'start', bold=True)
        up, dn = (r, meas) if r < meas else (meas, r)
        for val in (r, meas):
            yy = y0 + k * val + (-7 if val == up else 17)
            S.halo(W.X(x) - 9, yy, (f'剛體 {val:g}' if val == r else f'量測 {val:g}'), 11.5, REAC if val == r else ORG, 'end', bold=True)
    S.text(450, 428, '解聯立：δ + δ_DE/3 = 1.8、δ/3 + δ_DE = −2.6 ⟹ δ = +3 mm（過長）、δ_DE = −3.6 mm ⟹ ΔT = −60 °C（降溫）', 11.8, INK)
    return S.render()


# ---------------------------------------------------------------- 6-3 SA-2023-1
def deflection_2023_1(P=28.125, EI=20000.0):
    """returns x-grid (m) and rigid / elastic / total deflection (mm, up +)"""
    def M(x):
        if 2 <= x <= 6:
            return -0.5 * P * (x - 2)
        if 6 < x <= 10:
            return 2 * P - 0.5 * P * (x - 6)
        return 0.0
    h = 0.001
    n = int(round(8 / h))
    # integrate from B with unit-slope trial, then fix slope so v(D) = 0
    def shoot(th0):
        v, th = 0.0, th0
        vs, ths = [0.0], [th0]
        for i in range(n):
            x = 2 + i * h
            th += M(x + h / 2) / EI * h
            v += (ths[-1] + th) / 2 * h
            vs.append(v); ths.append(th)
        return vs, ths
    v0, _ = shoot(0.0)
    th0 = -v0[-1] / 8
    vs, ths = shoot(th0)
    xs = [i / 100 for i in range(0, 1201)]
    el = []
    for x in xs:
        if x < 2:
            el.append(th0 * (x - 2))
        elif x > 10:
            el.append(vs[-1] + ths[-1] * (x - 10))
        else:
            el.append(vs[min(int(round((x - 2) / h)), n)])
    el = [1000 * v for v in el]
    rig = [-3 * (x - 2) / 8 for x in xs]
    tot = [a + b for a, b in zip(el, rig)]
    return xs, rig, el, tot


def fig_6_3():
    xs, rig, el, tot = deflection_2023_1()
    assert abs(el[-1] - 3.75) < 0.01, el[-1]          # 8P/3EI = 3.75 mm upward
    assert abs(tot[-1]) < 0.01
    S = SVG(900, 475, 'SA-2023-1 疊加')
    S.text(450, 20, 'SA-2023-1（依比例）：降維成力偶 → 剛體位移 + 彈性位移 = 0', 14, '#0d47a1', bold=True)
    # original structure
    W = World(60, 190, 27)
    a, b, c, d, e, fF = W(0, 0), W(2, 0), W(6, 0), W(10, 0), W(12, 0), W(6, 4)
    S.line(*a, *e, INK, 4); S.line(*c, *fF, INK, 4)
    S.roller(*b, s=0.8); S.pin(*d, s=0.8)
    S.arrow(fF[0] + 4, fF[1], fF[0] + 54, fF[1], LOAD, 2.8); S.text(fF[0] + 30, fF[1] - 8, 'P', 13, LOAD, bold=True)
    for p, t in ((a, 'A'), (b, 'B'), (c, 'C'), (d, 'D'), (e, 'E')):
        S.text(p[0] + (10 if t == 'C' else 0), p[1] - 10, t, 12, INK, 'start' if t == 'C' else 'middle', bold=True)
    S.text(fF[0] - 8, fF[1] + 4, 'F', 12, INK, 'end', bold=True)
    S.dim(*W(6, 0), *W(6, 4), '4 m', off=-34)
    S.arrow(d[0] + 22, d[1] + 2, d[0] + 22, d[1] + 28, ORG, 2, L=7, W=3)
    S.text(d[0] + 28, d[1] + 22, '3 mm', 11.5, ORG, 'start', bold=True)
    for x0, x1, t in ((0, 2, '2'), (2, 6, '4'), (6, 10, '4'), (10, 12, '2')):
        S.dim(*W(x0, 0), *W(x1, 0), t, off=40, lab_off=14)
    S.text(W.X(6), 260, 'B 滾、D 鉸：r = 3，d = 0 靜定', 11.5, MUT)
    # equivalent
    S.text(470, 108, '≡', 26, MUT)
    W2 = World(520, 190, 27)
    a2, c2, e2 = W2(0, 0), W2(6, 0), W2(12, 0)
    S.line(*a2, *e2, INK, 4); S.roller(*W2(2, 0), s=0.8); S.pin(*W2(10, 0), s=0.8)
    S.moment(c2[0], c2[1], 16, ccw=False, c=LOAD, a0=200, span=270)
    S.text(c2[0], c2[1] - 26, 'M_C = 4P（順時針）', 12.5, LOAD, bold=True)
    S.text(W2.X(6), 232, '水平力 P 由鉸 D 吸收，不生彎矩', 11.5, MUT)
    S.text(W2.X(6), 250, 'M：B→C 由 0 到 −2P，C→D 由 +2P 到 0', 11.5, MUT)
    # deflection plot
    Wd = World(80, 362, 55)
    k = 14.0                                         # px per mm, up positive
    S.text(20, 290, '梁的垂直位移（mm，向上為正；P = 28.125 kN）', 12, '#0d47a1', 'start', bold=True)
    S.line(Wd.X(0) - 8, Wd.Y(0), Wd.X(12) + 8, Wd.Y(0), GHOST, 1.2)
    def curve(vals, c, w, dash=None):
        S.pl([(Wd.X(x), Wd.Y(0) - k * v) for x, v in zip(xs, vals)][::4] + [(Wd.X(12), Wd.Y(0) - k * vals[-1])], c, w, dash=dash)
    curve(rig, REAC, 2, '7 4'); curve(el, GOOD, 2, '3 3'); curve(tot, LOAD, 3)
    for x, t in ((2, 'B'), (6, 'C'), (10, 'D'), (12, 'E')):
        S.line(Wd.X(x), Wd.Y(0) - 50, Wd.X(x), Wd.Y(0) + 62, GHOST, 0.8, dash='2 3')
        S.text(Wd.X(x), Wd.Y(0) + 76, t, 12, INK, bold=True)
    S.halo(Wd.X(12) + 6, Wd.Y(0) - k * rig[-1] + 4, '剛體 −3.75', 11.5, REAC, 'start', bold=True)
    S.halo(Wd.X(12) + 6, Wd.Y(0) - k * el[-1] + 4, '彈性 +3.75 = 8P/3EI', 11.5, GOOD, 'start', bold=True)
    S.halo(Wd.X(12) + 6, Wd.Y(0) + 4, '合計 0 ✓', 12, LOAD, 'start', bold=True)
    S.halo(Wd.X(10) + 8, Wd.Y(0) + k * 3 + 20, '−3（D 下陷）', 11, REAC, 'start')
    S.text(Wd.X(0), 466, '藍虛線＝剛體轉動（繞 B）　綠點線＝力偶 4P 的彈性變形　紅實線＝兩者疊加', 11.5, MUT, 'start')
    return S.render()


# ======================= driver =======================
FIGS = {
    '1-1': fig_1_1, '1-2': fig_1_2, '2-1': fig_2_1, '2-2': fig_2_2, '2-3': fig_2_3,
    '3-1': fig_3_1, '3-2': fig_3_2, '3-3': fig_3_3, '4-1': fig_4_1, '4-2': fig_4_2,
    '5-1': fig_5_1, '5-2': fig_5_2, '6-1': fig_6_1, '6-2': fig_6_2, '6-3': fig_6_3,
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
                     pathlib.Path(__file__).resolve().parent.parent / 'study' / 'lecture-SA-U1-2.html')
    html, n = inject(p.read_text(encoding='utf-8'))
    p.write_text(html, encoding='utf-8')
    print(f'{p}: {n} figures regenerated')

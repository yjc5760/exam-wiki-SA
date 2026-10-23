#!/usr/bin/env python3
"""gen_lecture_SA-U1-3_figs.py — 重繪 study/lecture-SA-U1-3.html 的 SVG 圖解

結構圖一律依題目真實尺寸（World: m→px）繪製；影響線縱距由閉合式計算，
靜不定題另以內建的純 Python 2D 剛架有限元逐點重算（SA-2015-2、2016-2、2018-4），
並以 assert 對照 raw/solutions/ 各題解析的數值（含 2026-08-26 勘誤後的值）。
HTML 內以 <!--FIG:id--> ... 標記圖位，本腳本只替換標記後的 <svg>…</svg>，
圖說（.cap）與正文不動。可重複執行；不依賴 numpy。

用法：python scripts/gen_lecture_SA-U1-3_figs.py [study/lecture-SA-U1-3.html]
      python scripts/gen_lecture_SA-U1-3_figs.py --preview out.html   （只輸出圖，供檢查）
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

# ======================= fe.py =======================
"""純 Python 2D 剛架有限元（不依賴 numpy），供靜不定影響線獨立驗算。

Frame(nodes) ; add(i, j, hinge_i=False, hinge_j=False, EA=1e9, EI=1)
support(node, ux, uy, rz) ; 載重一律施於節點（細分網格）。
剪力釋放：用兩個節點 + link(nL, nR, 'rot','ux') 讓轉角／水平位移共用，垂直不連。
"""


def _lu(A):
    n = len(A)
    M = [r[:] for r in A]
    perm = list(range(n))
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        if abs(M[p][c]) < 1e-12:
            raise ValueError('singular stiffness (mechanism?)')
        M[c], M[p] = M[p], M[c]; perm[c], perm[p] = perm[p], perm[c]
        piv = M[c][c]; Mc = M[c]
        for r in range(c + 1, n):
            Mr = M[r]
            if Mr[c]:
                f = Mr[c] / piv; Mr[c] = f
                for k in range(c + 1, n):
                    Mr[k] -= f * Mc[k]
    return M, perm


def _lusolve(LU, b):
    M, perm = LU
    n = len(b)
    y = [b[perm[i]] for i in range(n)]
    for i in range(n):
        Mi = M[i]
        y[i] -= sum(Mi[k] * y[k] for k in range(i))
    for i in range(n - 1, -1, -1):
        Mi = M[i]
        y[i] = (y[i] - sum(Mi[k] * y[k] for k in range(i + 1, n))) / Mi[i]
    return y


class Frame:
    def __init__(self, nodes):
        self.nodes = [tuple(map(float, p)) for p in nodes]
        self.el, self.fix, self.links = [], {}, []

    def add(self, i, j, hi=False, hj=False, EA=1e7, EI=1.0):
        self.el.append((i, j, hi, hj, EA, EI))

    def support(self, n, ux=False, uy=False, rz=False):
        self.fix[n] = (ux, uy, rz)

    def link(self, a, b, *what):           # 'ux','uy','rz' 共用
        self.links.append((a, b, what))

    def _k(self, e):
        import math
        i, j, hi, hj, EA, EI = e
        (x1, y1), (x2, y2) = self.nodes[i], self.nodes[j]
        L = math.hypot(x2 - x1, y2 - y1)
        c, s = (x2 - x1) / L, (y2 - y1) / L
        a, b1, b2, b3 = EA / L, 12 * EI / L**3, 6 * EI / L**2, 4 * EI / L
        kl = [[a, 0, 0, -a, 0, 0], [0, b1, b2, 0, -b1, b2], [0, b2, b3, 0, -b2, b3 / 2],
              [-a, 0, 0, a, 0, 0], [0, -b1, -b2, 0, b1, -b2], [0, b2, b3 / 2, 0, -b2, b3]]
        rel = ([2] if hi else []) + ([5] if hj else [])
        for r in rel:                        # 靜力凝聚：釋放端彎矩
            krr = kl[r][r]
            kl = [[kl[p][q] - kl[p][r] * kl[r][q] / krr for q in range(6)] for p in range(6)]
        T = [[c, s, 0, 0, 0, 0], [-s, c, 0, 0, 0, 0], [0, 0, 1, 0, 0, 0],
             [0, 0, 0, c, s, 0], [0, 0, 0, -s, c, 0], [0, 0, 0, 0, 0, 1]]
        kg = [[sum(T[p][m] * kl[m][q2] * T[q2][q] for m in range(6) for q2 in range(6))
               for q in range(6)] for p in range(6)]
        return kg, rel

    def solve(self, loads):
        return self.solve_many([loads])[0]

    def solve_many(self, load_list):
        """load_list: [{node: (Fx, Fy, Mz)}] → [(disp, reactions)]"""
        nn = len(self.nodes)
        dof = [[3 * n, 3 * n + 1, 3 * n + 2] for n in range(nn)]
        for a, b, what in self.links:
            for w in what:
                k = {'ux': 0, 'uy': 1, 'rz': 2}[w]
                dof[b][k] = dof[a][k]
        N = 3 * nn
        K = [[0.0] * N for _ in range(N)]
        for e in self.el:
            kg, _ = self._k(e)
            ids = dof[e[0]] + dof[e[1]]
            for p in range(6):
                for q in range(6):
                    K[ids[p]][ids[q]] += kg[p][q]
        fixed = set()
        for n, fl in self.fix.items():
            for k in range(3):
                if fl[k]:
                    fixed.add(dof[n][k])
        used = sorted({d for row in dof for d in row})
        free = [d for d in used if d not in fixed and abs(K[d][d]) > 1e-12]
        LU = _lu([[K[p][q] for q in free] for p in free])
        out = []
        for loads in load_list:
            F = [0.0] * N
            for n, (fx, fy, mz) in loads.items():
                F[dof[n][0]] += fx; F[dof[n][1]] += fy; F[dof[n][2]] += mz
            u = _lusolve(LU, [F[p] for p in free])
            U = [0.0] * N
            for d, v in zip(free, u):
                U[d] = v
            disp = [[U[dof[n][k]] for k in range(3)] for n in range(nn)]
            R = {}
            for n, fl in self.fix.items():
                R[n] = [sum(K[dof[n][k]][q] * U[q] for q in range(N)) - F[dof[n][k]] if fl[k] else 0.0
                        for k in range(3)]
            out.append((disp, R))
        return out


def beam_frame(xs, EI=1.0):
    """沿 x 軸、節點 xs（已排序）的連續梁"""
    fr = Frame([(x, 0) for x in xs])
    for i in range(len(xs) - 1):
        fr.add(i, i + 1, EI=EI)
    return fr


def grid(stations, h):
    """含 stations 的等距細分網格"""
    xs = set()
    for a, b in zip(stations[:-1], stations[1:]):
        n = max(1, round((b - a) / h))
        for k in range(n + 1):
            xs.add(round(a + (b - a) * k / n, 9))
    return sorted(xs)
# ======================= figs.py =======================
"""U1-3 影響線講義圖解。座標一律依比例（World: m→px）；縱距一律由公式或
有限元算出，並以 assert 對照 raw/solutions/ 各題解析的數值。
本講義慣例：影響線正值畫在軸線上方。"""
import math

IL1 = '#2e7d32'      # 影響線主色
IL2 = '#1565c0'
IL3 = '#6a1b9a'
IL4 = '#ef6c00'
IL5 = '#c62828'
TITLE = '#0d47a1'


def frange(a, b, n):
    return [a + (b - a) * k / n for k in range(n + 1)]


def il_plot(S, W, pts, c, w=2.6, op=0.13, dash=None):
    """pts: [(x, ordinate)] world; 允許同 x 兩點表示跳躍。正負區分別上色。"""
    base = W.Y(0)
    # 填色：逐段梯形，依符號
    for (x1, y1), (x2, y2) in zip(pts[:-1], pts[1:]):
        if x2 - x1 < 1e-12:
            continue
        if y1 * y2 < 0:                       # 跨零：切開
            xm = x1 + (x2 - x1) * y1 / (y1 - y2)
            segs = [((x1, y1), (xm, 0.0)), ((xm, 0.0), (x2, y2))]
        else:
            segs = [((x1, y1), (x2, y2))]
        for (a, ya), (b, yb) in segs:
            S.area([W(a, 0), W(a, ya), W(b, yb), W(b, 0)], c, op)
    S.pl([W(x, y) for x, y in pts], c, w, dash=dash)


def axis(S, W, x0, x1, c=GHOST, w=1.3):
    S.line(W.X(x0) - 6, W.Y(0), W.X(x1) + 6, W.Y(0), c, w)


def dot(S, W, x, y, c, lab=None, dx=0, dy=None, size=12, anchor='middle', bold=True, r=3.6):
    px, py = W(x, y)
    S.circ(px, py, r, c, '#fff', 1.2)
    if lab is not None:
        if dy is None:
            dy = -9 if y >= 0 else 18
        S.halo(px + dx, py + dy, lab, size, c, anchor, bold)


def drop(S, W, x, y, c=GHOST):
    S.line(W.X(x), W.Y(0), W.X(x), W.Y(y), c, 1, dash='3 3')


def row_label(S, x, y, t, c, sub=None):
    S.text(x, y, t, 13.5, c, 'start', bold=True)
    if sub:
        S.text(x, y + 17, sub, 11, MUT, 'start')


def beam_line(S, W, x0, x1, y=0, w=4.5):
    S.line(*W(x0, y), *W(x1, y), INK, w)


def load(S, x, y, c=LOAD, L=30, lab='P = 1', size=12.5, w=2.6, lab_dx=0):
    S.arrow(x, y - L, x, y - 4, c, w)
    if lab:
        S.text(x + lab_dx, y - L - 6, lab, size, c, bold=True)


def shear_release(S, x, y, c=IL2):
    """剪力釋放符號：兩條平行短連桿（可上下錯動、不能相對轉動）"""
    S.rect(x - 7, y - 10, 14, 20, '#fff', c, 1.8, rx=2)
    S.line(x - 3, y - 7, x - 3, y + 7, c, 1.6)
    S.line(x + 3, y - 7, x + 3, y + 7, c, 1.6)


# ---------------------------------------------------------------- 0-1
def fig_0_1():
    L, P_at, sec = 10.0, 3.0, 6.0
    bmd = lambda s: (L - P_at) * s / L if s <= P_at else P_at * (L - s) / L
    il = lambda x: (L - sec) * x / L if x <= sec else sec * (L - x) / L
    assert abs(bmd(sec) - 1.2) < 1e-12 and abs(il(P_at) - 1.2) < 1e-12   # 同一個數
    S = SVG(900, 350, '彎矩圖與影響線的差別')
    S.line(450, 14, 450, 336, GHOST, 1.2, dash='6 5')
    for k, (x0, col, ttl, sub) in enumerate((
            (30, LOAD, '彎矩圖 BMD：載重固定在 x = 3 m', '橫軸 s ＝「斷面」在哪'),
            (480, IL1, '影響線 IL：斷面固定在 s = 6 m', '橫軸 x ＝「單位載重」在哪'))):
        S.text(x0 + 195, 26, ttl, 14.5, col, bold=True)
        S.text(x0 + 195, 45, sub, 12, MUT)
        W = World(x0 + 25, 100, 34)
        beam_line(S, W, 0, L)
        S.pin(*W(0)); S.roller(*W(L))
        if k == 0:
            load(S, W.X(P_at), W.Y(0), lab='P（不動）')
            S.line(W.X(sec), W.Y(0) - 12, W.X(sec), W.Y(0) + 12, MUT, 1.2, dash='2 2')
            S.text(W.X(sec), W.Y(0) - 16, 's = 6', 11, MUT)
        else:
            for xx, op in ((1, .35), (3, 1), (5, .35), (8.5, .35)):
                S.arrow(W.X(xx), W.Y(0) - 30, W.X(xx), W.Y(0) - 4, LOAD, 2.2 if op == 1 else 1.4)
            S.text(W.X(3), W.Y(0) - 36, '1（到處跑）', 11.5, LOAD, bold=True)
            S.line(W.X(sec), W.Y(0) - 12, W.X(sec), W.Y(0) + 12, IL1, 3)
            S.text(W.X(sec) + 6, W.Y(0) + 26, '斷面 s = 6（不動）', 11.5, IL1, 'start', bold=True)
        Wp = World(x0 + 25, 262, 34, 42)
        axis(S, Wp, 0, L)
        fn = bmd if k == 0 else il
        brk = sorted({0, L, P_at if k == 0 else sec})
        il_plot(S, Wp, [(x, fn(x)) for x in brk], col)
        pk = P_at if k == 0 else sec
        dot(S, Wp, pk, fn(pk), col, (f'Pab/L = 2.1P' if k == 0 else 'ab/L = 2.4 m'), dy=-10)
        q = sec if k == 0 else P_at
        drop(S, Wp, q, fn(q), col)
        dot(S, Wp, q, fn(q), MOM, None)
        S.halo(Wp.X(q) + (10 if k == 0 else -10), Wp.Y(fn(q)) - 12,
               ('M(s=6) = 1.2P' if k == 0 else 'IL(x=3) = 1.2 m'), 12.5, MOM,
               'start' if k == 0 else 'end', True)
        S.text(Wp.X(L) + 10, Wp.Y(0) + 4, 's' if k == 0 else 'x', 13, MUT, 'start', italic=True)
        S.text(x0 + 195, 300, ('縱座標單位：力·長度（kN·m）' if k == 0 else '縱座標單位：長度（m）＝每單位載重的彎矩'),
               12, col, bold=True)
    S.rect(130, 312, 640, 30, '#f3e5f5', '#ce93d8', 1, rx=7)
    S.text(450, 332, '同一個 1.2 出現在兩張圖的「不同位置」：BMD 在 s = 6 讀，IL 在 x = 3 讀 —— 橫軸意義相反', 12.5, MOM, bold=True)
    return S.render()


# ---------------------------------------------------------------- 1-1
def propped_Cy(x, L=10.0):
    return x * x * (3 * L - x) / (2 * L ** 3)


def fig_1_1():
    L, xp = 10.0, 4.0
    X = propped_Cy(xp)
    assert abs(X - 0.208) < 1e-12
    S = SVG(900, 400, 'Müller-Breslau 與 Betti 定理')
    S.text(450, 24, '兩個狀態、一條功的互等式（一端固定一端滾支承，L = 10 m，依比例）', 14.5, TITLE, bold=True)
    # state 1
    S.rect(16, 40, 424, 200, '#ffebee', '#ef9a9a', 1, rx=10)
    S.text(228, 62, '狀態 ①：原結構，單位載重在 x = 4 m', 13.5, '#b71c1c', bold=True)
    W1 = World(60, 150, 34)
    beam_line(S, W1, 0, L)
    S.wall(W1.X(0), 120, 180, side=-1)
    S.roller(*W1(L))
    load(S, W1.X(xp), W1.Y(0), lab='1')
    S.arrow(W1.X(L), W1.Y(0) + 64, W1.X(L), W1.Y(0) + 32, REAC, 2.6)
    S.text(W1.X(L) - 8, W1.Y(0) + 60, 'X = R_C = 0.208', 12.5, REAC, 'end', bold=True)
    S.dim(*W1(0, 0), *W1(xp, 0), 'x = 4', off=40, lab_off=14)
    S.text(228, 228, 'C 點位移 = 0（支承在）', 12, '#b71c1c')
    # state 2
    S.rect(460, 40, 424, 200, '#e8f5e9', '#a5d6a7', 1, rx=10)
    S.text(672, 62, '狀態 ②：拆掉 C 的支承，強迫 C 上移 Δ = 1', 13.5, '#1b5e20', bold=True)
    W2 = World(504, 190, 34, 34 * 2.6)
    S.line(W2.X(0), W2.Y(0), W2.X(L), W2.Y(0), GHOST, 2, dash='5 4')
    S.wall(W2.X(0), 160, 220, side=-1)
    pts = [W2(x, propped_Cy(x)) for x in frange(0, L, 60)]
    S.pl(pts, IL1, 4)
    S.arrow(W2.X(L) + 14, W2.Y(0), W2.X(L) + 14, W2.Y(1) + 2, IL1, 2.4)
    S.text(W2.X(L) + 4, W2.Y(1) - 6, 'Δ = 1', 12.5, IL1, 'end', bold=True)
    drop(S, W2, xp, X, IL1)
    dot(S, W2, xp, X, IL1, 'δ(4) = 0.208', dy=-10)
    S.text(672, 228, 'δ(x) = x²(3L−x)/(2L³)　（懸臂撓曲線，已正規化）', 12, '#1b5e20')
    # Betti
    S.rect(110, 254, 680, 136, '#f3e5f5', '#ba68c8', 1.6, rx=10)
    S.text(450, 280, 'Betti：①的力在②的位移上作的功 ＝ ②的力在①的位移上作的功', 13.5, '#4a148c', bold=True)
    S.text(450, 308, '(−1)·δ(x)　+　X·Δ　=　F_C · 0', 14, MOM)
    S.text(450, 330, '↑ 載重向下、δ 向上　↑ 反力與 Δ 同向　↑ ① 中 C 不動，右邊為 0', 11.5, MUT)
    S.text(450, 360, '⟹　IL_X(x) = δ(x)　：　x = 4 時兩個狀態都讀到 0.208', 15, '#4a148c', bold=True)
    S.text(450, 380, '算一次撓曲線，就得到整條影響線（不用對每個 x 重解一次結構）', 11.5, MOM)
    return S.render()


# ---------------------------------------------------------------- 2-1
def fig_2_1():
    L, a = 10.0, 4.0
    b = L - a
    S = SVG(900, 360, '三種束制的拆法')
    cols = [
        (8, '#e8f5e9', '#a5d6a7', IL1, '① 反力 R_A：拿掉支承，平移 1'),
        (305, '#e3f2fd', '#90caf9', IL2, '② 剪力 V：剪力釋放，平行錯動 1'),
        (602, '#fff3e0', '#ffcc80', IL4, '③ 彎矩 M：插鉸，相對轉角 1'),
    ]
    for k, (x0, bg, bd, c, ttl) in enumerate(cols):
        S.rect(x0, 10, 290, 340, bg, bd, 1, rx=10)
        S.text(x0 + 145, 32, ttl, 13, c, bold=True)
        W = World(x0 + 20, 80, 25)
        beam_line(S, W, 0, L, w=3.5)
        S.text(x0 + 145, 122, '原結構（斷面距 A 為 a = 4 m）' if k else '簡支梁 L = 10 m；A 支承拿掉（灰）', 11, MUT)
        if k == 0:
            S.roller(*W(L), s=0.8)
            S.arrow(W.X(0) - 16, W.Y(0) + 34, W.X(0), W.Y(0) + 6, c, 2.2)
            S.pin(*W(0), s=0.8, c=GHOST)
        else:
            S.pin(*W(0), s=0.8); S.roller(*W(L), s=0.8)
            if k == 1:
                shear_release(S, W.X(a), W.Y(0), c)
            else:
                S.hinge(W.X(a), W.Y(0), 5.5, c)
        Wp = World(x0 + 20, 206, 25, 56 if k < 2 else 24)
        S.line(Wp.X(0), Wp.Y(0), Wp.X(L), Wp.Y(0), GHOST, 1.6, dash='4 4')
        if k == 0:
            pts = [(0, 1.0), (L, 0.0)]
            S.roller(*Wp(L), s=0.7)
            il_plot(S, Wp, pts, c, 3.2)
            S.arrow(Wp.X(0) - 12, Wp.Y(0), Wp.X(0) - 12, Wp.Y(1) + 2, c, 2)
            S.text(Wp.X(0) - 2, Wp.Y(1) - 6, 'Δ = 1', 12, c, 'start', bold=True)
            S.text(x0 + 145, 268, '繞 B 剛體轉動 → 一條直線', 12, c, bold=True)
            S.text(x0 + 145, 290, 'IL = (L − x)/L　無因次', 12, INK)
            S.text(x0 + 145, 312, '在 A 為 1、在 B 為 0', 12, INK)
        elif k == 1:
            pts = [(0, 0), (a, -a / L), (a, b / L), (L, 0)]
            S.pin(*Wp(0), s=0.7); S.roller(*Wp(L), s=0.7)
            il_plot(S, Wp, pts, c, 3.2)
            dot(S, Wp, a, -a / L, c, '−a/L = −0.4', dx=-6, dy=16, anchor='end')
            dot(S, Wp, a, b / L, c, '+b/L = +0.6', dx=6, dy=-6, anchor='start')
            S.line(Wp.X(a) + 30, Wp.Y(-a / L), Wp.X(a) + 30, Wp.Y(b / L), MOM, 1.2)
            S.text(Wp.X(a) + 36, Wp.Y(0) + 4, '跳 1', 12, MOM, 'start', bold=True)
            S.text(x0 + 145, 268, '兩段斜率都是 −1/L：保持平行', 12, c, bold=True)
            S.text(x0 + 145, 290, '只錯動、不相對轉動', 12, INK)
            S.text(x0 + 145, 312, '斷面左 −a/L、右 +b/L，差 = 1', 12, INK)
        else:
            pk = a * b / L
            pts = [(0, 0), (a, pk), (L, 0)]
            S.pin(*Wp(0), s=0.7); S.roller(*Wp(L), s=0.7)
            il_plot(S, Wp, pts, c, 3.2)
            S.hinge(*Wp(a, pk), 4.5, c)
            dot(S, Wp, a, pk, c, 'ab/L = 2.4 m', dy=-12)
            S.text(Wp.X(1.6), Wp.Y(pk * 0.4) + 18, '斜率 b/L', 11, c)
            S.text(Wp.X(7.2), Wp.Y(pk * 0.47) + 18, '斜率 −a/L', 11, c)
            S.text(x0 + 145, 268, '鉸往上頂：兩段夾角 = 1 rad', 12, c, bold=True)
            S.text(x0 + 145, 290, 'b/L − (−a/L) = 0.6 + 0.4 = 1', 12, INK)
            S.text(x0 + 145, 312, '縱座標單位是長度（m）', 12, INK)
        S.text(x0 + 145, 338, ['支承處 → 該支承自身為 1', '斷面處 → 不連續', '斷面處 → 連續但有折角'][k],
               11.5, MUT)
    return S.render()


# ---------------------------------------------------------------- 2-2 SA-2015-2
def il_2015_2(h=0.5):
    xs = grid([0, 15, 30, 40, 50, 80], h)
    fr = Frame([(x, 0) for x in xs]); I = {x: i for i, x in enumerate(xs)}
    for i in range(len(xs) - 1):
        fr.add(i, i + 1, hj=(xs[i + 1] == 40))
    fr.support(0, True, True)
    for x in (30, 50, 80):
        fr.support(I[x], False, True)
    res = fr.solve_many([{k: (0, -1, 0)} for k in range(len(xs))])
    RA = [r[1][0][1] for r in res]
    return xs, RA, I


def fig_2_2():
    xs, RA, I = il_2015_2()
    VF = lambda k: RA[k] - (1 if xs[k] < 15 else 0)
    assert abs(RA[I[15]] - 1 + 73 / 128) < 1e-8 and abs(RA[I[15]] - 55 / 128) < 1e-8
    assert abs(RA[I[40]] + 1 / 6) < 1e-8
    kmax = max(range(I[50], len(xs)), key=lambda k: RA[k])
    assert abs(RA[kmax] - 0.0722) < 2e-4
    S = SVG(900, 290, 'SA-2015-2 剪力影響線')
    S.text(450, 22, 'SA-2015-2（依比例）：1 度靜不定 → 剪力釋放後恰成靜定 → 曲線 ＋ 單位跳躍', 14, TITLE, bold=True)
    W = World(60, 78, 9.6)
    beam_line(S, W, 0, 80)
    S.pin(*W(0), s=0.8)
    for x in (30, 50, 80):
        S.roller(*W(x), s=0.8)
    S.hinge(*W(40), 5.5, MOM)
    shear_release(S, W.X(15), W.Y(0), IL2)
    for x, t in ((0, 'A'), (15, 'F'), (30, 'B'), (40, 'C'), (50, 'D'), (80, 'E')):
        S.text(W.X(x), W.Y(0) - 14, t, 12.5, INK, bold=True)
    for x0, x1, t in ((0, 15, '15'), (15, 30, '15'), (30, 40, '10'), (40, 50, '10'), (50, 80, '30 m')):
        S.dim(*W(x0, 0), *W(x1, 0), t, off=34, lab_off=14)
    Wp = World(60, 196, 9.6, 105)
    axis(S, Wp, 0, 80)
    pts = [(xs[k], VF(k)) for k in range(I[15] + 1)] + [(xs[k], RA[k]) for k in range(I[15], len(xs))]
    il_plot(S, Wp, pts, IL2, 2.8)
    dot(S, Wp, 15, RA[I[15]] - 1, IL2, '−73/128', dx=-6, dy=14, anchor='end')
    dot(S, Wp, 15, RA[I[15]], IL2, '+55/128', dx=6, dy=-4, anchor='start')
    dot(S, Wp, 40, RA[I[40]], MOM, 'C：−1/6（內鉸 → 折角）', dy=20)
    dot(S, Wp, xs[kmax], RA[kmax], IL2, f'+0.072 @ x ≈ {xs[kmax]:.1f}', dy=-10)
    for x in (30, 50, 80):
        dot(S, Wp, x, 0, INK, None, r=2.6)
    S.text(Wp.X(13), Wp.Y(0.22), 'F 兩側切線平行（只錯動、不轉）→', 11, IL2, 'end')
    S.text(450, 282, '四個支承處都是 0；F⁺ − F⁻ = 55/128 + 73/128 = 1 ✓（腳本以梁有限元逐點重算，與共軛梁解相符）', 11.5, MUT)
    return S.render()


# ---------------------------------------------------------------- 3-1
def fig_3_1():
    L = 10.0
    S = SVG(900, 316, '靜定折線 vs 靜不定曲線')
    S.line(450, 14, 450, 304, GHOST, 1.2, dash='6 5')
    S.text(225, 28, '靜定：簡支梁，求 R_A', 14.5, IL1, bold=True)
    S.text(675, 28, '靜不定：一端固定一端滾支承，求 R_C', 14.5, IL5, bold=True)
    W = World(55, 80, 34)
    beam_line(S, W, 0, L); S.pin(*W(0)); S.roller(*W(L))
    S.text(225, 126, '拿掉 A ⟹ 只剩一個支承 ⟹ 機構', 12, MUT)
    Wp = World(55, 232, 34, 80)
    axis(S, Wp, 0, L)
    il_plot(S, Wp, [(0, 1), (L, 0)], IL1, 3)
    dot(S, Wp, 0, 1, IL1, '1', dx=-10, dy=4, anchor='end')
    dot(S, Wp, 5, 0.5, IL1, '0.5', dy=-10)
    S.text(225, 276, '剛體轉動：IL = (L − x)/L，一條直線', 12.5, IL1, bold=True)
    S.text(225, 298, '不需要 EI、不需要積分', 12, INK)
    W2 = World(505, 80, 34)
    beam_line(S, W2, 0, L); S.wall(W2.X(0), 56, 104, side=-1); S.roller(*W2(L))
    S.text(675, 126, '拿掉 C ⟹ 剩懸臂梁 ⟹ 仍然穩定', 12, MUT)
    Wq = World(505, 232, 34, 80)
    axis(S, Wq, 0, L)
    S.line(Wq.X(0), Wq.Y(0), Wq.X(L), Wq.Y(1), GHOST, 1.4, dash='6 4')
    il_plot(S, Wq, [(x, propped_Cy(x)) for x in frange(0, L, 60)], IL5, 3)
    dot(S, Wq, 10, 1, IL5, '1', dx=10, dy=4, anchor='start')
    dot(S, Wq, 5, 5 / 16, IL5, '5/16 = 0.3125', dx=-6, dy=-10, anchor='end')
    S.line(Wq.X(0), Wq.Y(0) - 1, Wq.X(2.6), Wq.Y(0) - 1, MOM, 2.4)
    S.text(Wq.X(0.2), Wq.Y(0) + 16, '在 A 與軸相切（θ_A = 0）', 11, MOM, 'start')
    S.text(Wq.X(6.4), Wq.Y(0.82), '虛線＝若是簡支', 11, MUT, 'end')
    S.text(675, 276, '彈性撓曲線：IL = x²(3L − x)/(2L³)，三次曲線', 12.5, IL5, bold=True)
    S.text(675, 298, 'EI 在正規化時消掉', 12, INK)
    return S.render()


# ---------------------------------------------------------------- 4-1 Gerber hierarchy
XA, XB, XF, XC, XD, XE = 0.0, 4.0, 6.0, 8.0, 12.0, 16.0


def fig_4_1():
    S = SVG(900, 330, 'SA-2025-2 主從關係')
    S.text(450, 22, 'SA-2025-2（依比例，4@4 m）：先看「誰擱在誰身上」，影響線就只是幾條直線的接力', 14, TITLE, bold=True)
    W = World(130, 86, 40)
    beam_line(S, W, XA, XE)
    S.wall(W.X(0), 62, 110, side=-1)
    S.hinge(*W(XB), 5.5, MOM); S.hinge(*W(XD), 5.5, MOM)
    S.roller(*W(XC)); S.roller(*W(XE))
    S.line(W.X(XF), W.Y(0) - 11, W.X(XF), W.Y(0) + 11, IL2, 2.4)
    S.text(W.X(0) + 12, W.Y(0) + 22, 'A', 12.5, INK, 'start', bold=True)
    for x, t in ((XB, 'B'), (XF, 'F'), (XC, 'C'), (XD, 'D'), (XE, 'E')):
        S.text(W.X(x), W.Y(0) - 14, t, 12.5, IL2 if t == 'F' else INK, bold=True)
    for x0 in (0, 4, 8, 12):
        S.dim(*W(x0, 0), *W(x0 + 4, 0), '4 m', off=36, lab_off=14)
    S.text(W.X(XF), W.Y(0) + 70, 'F：B–C 間的斷面（C 左 2 m），不是自由端', 11.5, IL2, bold=True)
    # exploded hierarchy
    y0 = 262
    Wl = World(130, y0, 40)
    lv = [(XA, XB, 0, IL1, '① 主段 A–B：固定端撐著，自己站得住'),
          (XB, XD, 44, IL2, '② B–D：左端擱在 B 的尖上，C 支承撐住，C–D 外伸'),
          (XD, XE, 88, IL3, '③ D–E：左端擱在 D 的尖上，E 支承撐住')]
    for x0, x1, up, c, t in lv:
        yy = y0 - up
        S.line(Wl.X(x0) + (8 if up else 0), yy, Wl.X(x1), yy, c, 5)
        S.text(Wl.X(x1) + 12 if x1 < 16 else Wl.X(x0) - 10, yy + 4, '', 12, c)
    S.wall(Wl.X(0), y0 - 22, y0 + 22, side=-1)
    S.roller(Wl.X(XC), y0 - 44, s=0.8)
    S.roller(Wl.X(XE), y0 - 88, s=0.8)
    # resting arrows
    for xx, ytop, ybot, c in ((XB, y0 - 44, y0, IL2), (XD, y0 - 88, y0 - 44, IL3)):
        S.arrow(Wl.X(xx), ytop + 4, Wl.X(xx), ybot - 4, c, 2.2, L=8, W=3.5)
        S.circ(Wl.X(xx), ybot, 3.5, '#fff', c, 1.8)
    S.text(Wl.X(1.4), y0 + 34, lv[0][4], 12, IL1, 'start', bold=True)
    S.text(Wl.X(1.4), y0 - 6 - 44 + 54, '', 12, IL2)
    S.halo(Wl.X(4.3), y0 - 54, lv[1][4], 12, IL2, 'start', True)
    S.halo(Wl.X(12.2), y0 - 98, lv[2][4], 12, IL3, 'start', True)
    S.text(Wl.X(16) + 18, y0 - 30, '力只往下傳：', 12, INK, 'start', bold=True)
    S.text(Wl.X(16) + 18, y0 - 12, '③ → ② → ①', 12, INK, 'start')
    S.text(Wl.X(16) + 18, y0 + 6, '反過來不會', 12, LOAD, 'start', bold=True)
    return S.render()


# ---------------------------------------------------------------- 5-1 panel-point loading
def fig_5_1():
    d, h, n = 3.0, 4.0, 6
    Lt = d * n
    Vp = lambda xn: -xn / Lt if xn <= 3 else (Lt - xn) / Lt        # 第 2 節間（3–6）剪力，節點值
    def truss_T(x):                                                  # 斜桿內力 = 1.25 V（節點值線性內插）
        if x <= 3:
            return 1.25 * (-x / Lt)
        if x >= 6:
            return 1.25 * (Lt - x) / Lt
        return 1.25 * (Vp(3) + (Vp(6) - Vp(3)) * (x - 3) / 3)
    beamV = lambda x: 1.25 * (-x / Lt if x < 4.5 else (Lt - x) / Lt)
    assert abs(truss_T(3) + 5 / 24) < 1e-12 and abs(truss_T(6) - 5 / 6) < 1e-12
    x0z = 3 + 3 * (1 / 6) / (5 / 6)
    assert abs(truss_T(x0z)) < 1e-12 and abs(x0z - 3.6) < 1e-12
    S = SVG(900, 450, '桁架間接載重與節間直線')
    S.text(450, 22, '間接載重：P = 1 先落在縱梁上，再以槓桿比例傳到兩側節點（6 @ 3 m、桁高 4 m，依比例）', 14, TITLE, bold=True)
    W = World(110, 188, 38)
    # truss members
    for i in range(n):
        S.line(*W(i * d, 0), *W((i + 1) * d, 0), INK, 2.4)
        S.line(*W(i * d, h), *W((i + 1) * d, h), INK, 2.4)
    for i in range(n + 1):
        S.line(*W(i * d, 0), *W(i * d, h), INK, 2)
    for i in range(n):
        x1 = i * d
        if i < n / 2:
            p0, p1 = (x1, h), (x1 + d, 0)
        else:
            p0, p1 = (x1, 0), (x1 + d, h)
        hl = (i == 1)
        S.line(*W(*p0), *W(*p1), LOAD if hl else INK, 3.6 if hl else 2)
    for i in range(n + 1):
        S.node(*W(i * d, 0), 3); S.node(*W(i * d, h), 3)
    S.pin(*W(0, 0)); S.roller(*W(Lt, 0))
    S.halo(W.X(4.4), W.Y(2.5), '斜桿 T', 12.5, LOAD, 'start', True)
    # stringer
    ys = W.Y(0) + 40
    S.line(W.X(0), ys, W.X(Lt), ys, IL2, 3, dash='10 4')
    for i in range(n + 1):
        S.line(W.X(i * d), W.Y(0) + 4, W.X(i * d), ys, IL2, 1.2, dash='2 3')
    S.text(W.X(Lt) + 10, ys + 4, '縱梁', 12, IL2, 'start', bold=True)
    S.arrow(W.X(4.5), ys - 34, W.X(4.5), ys - 4, LOAD, 2.6)
    S.text(W.X(4.5) + 6, ys - 24, 'P = 1（節間中點）', 12, LOAD, 'start', bold=True)
    for xx in (3, 6):
        S.arrow(W.X(xx), ys + 2, W.X(xx), W.Y(0) + 8, REAC, 2, L=7, W=3)
    S.text(W.X(3) - 6, ys + 18, '0.5', 12, REAC, 'end', bold=True)
    S.text(W.X(6) + 6, ys + 18, '0.5', 12, REAC, 'start', bold=True)
    # IL
    Wp = World(110, 360, 38, 82)
    axis(S, Wp, 0, Lt)
    bpts = [(0, 0), (4.5, beamV(4.49999999)), (4.5, beamV(4.5)), (Lt, 0)]
    S.pl([Wp(x, y) for x, y in bpts], GHOST, 2, dash='6 4')
    tpts = [(x, truss_T(x)) for x in (0, 3, 6, 9, 12, 15, 18)]
    il_plot(S, Wp, tpts, IL1, 3)
    for x in (0, 3, 6, 9, 12, 15, 18):
        dot(S, Wp, x, truss_T(x), IL1, None, r=3.2)
    dot(S, Wp, 3, truss_T(3), IL1, '−5/24', dx=-4, dy=18, anchor='end')
    dot(S, Wp, 6, truss_T(6), IL1, '+5/6', dx=6, dy=-6, anchor='start')
    dot(S, Wp, 4.5, truss_T(4.5), LOAD, '節間中點 0.3125', dx=8, dy=-8, anchor='start')
    dot(S, Wp, 3.6, 0, MOM, 'x = 3.6 過零', dx=-8, dy=-10, anchor='end')
    S.halo(Wp.X(10.5), Wp.Y(1.0), '虛線＝若載重直接作用在梁上（剪力 ×1.25）：節間中跳躍', 11.5, MUT, 'start')
    S.halo(Wp.X(10.5), Wp.Y(1.0) + 17, '實線＝桁架：節點值之間一律直線，沒有跳躍', 11.5, IL1, 'start', True)
    S.text(450, 412, 'T = V_節間 / sin θ = 1.25 V（sin θ = 4/5）。節點值照抄梁的剪力 IL × 1.25，節間用直線連', 12, INK)
    S.text(450, 434, '例外：細長拉桿換手會在節間另外造出折點（見下方 SA-2022-3 的 N_km）', 12, LOAD, bold=True)
    return S.render()


# ---------------------------------------------------------------- 5-2 SA-2022-3
def _ra22(x):
    if x <= 12:
        return (12 - x) / 12
    if x <= 15:
        return (x - 12) / 12
    if x <= 21:
        return (18 - x) / 12
    return (x - 30) / 36


def _pleft(x, a, b):          # 節間 a–b 左側（含節點 a 以左）的載重量
    return 1.0 if x <= a else (0.0 if x >= b else (b - x) / (b - a))


def il_2022_3(x):
    ra = _ra22(x)
    V1 = ra - _pleft(x, 3, 6)
    V2 = ra - _pleft(x, 6, 9)
    kn = 1.25 * V2
    km = min(V1, 0.0) - V2
    mn = (6 * ra - (6 - x if x <= 6 else 0.0)) / 4
    return ra, km, kn, mn


def fig_5_2():
    tab = {0: (1, 0, 0, 0), 3: (3 / 4, 0, -5 / 16, 3 / 8), 4: (2 / 3, 1 / 3, -5 / 12, 1 / 2),
           6: (1 / 2, 1 / 2, -5 / 8, 3 / 4), 8: (1 / 3, 0, 0, 1 / 2), 9: (1 / 4, -1 / 4, 5 / 16, 3 / 8),
           12: (0, 0, 0, 0), 15: (1 / 4, -1 / 4, 5 / 16, 3 / 8), 18: (0, 0, 0, 0),
           21: (-1 / 4, 0, -5 / 16, -3 / 8), 24: (-1 / 6, 0, -5 / 24, -1 / 4), 27: (-1 / 12, 0, -5 / 48, -1 / 8),
           30: (0, 0, 0, 0)}
    for x, v in tab.items():
        got = il_2022_3(x)
        assert all(abs(g - e) < 1e-12 for g, e in zip(got, v)), (x, got, v)
    S = SVG(900, 800, 'SA-2022-3 桁架與影響線')
    S.text(450, 22, 'SA-2022-3（依比例，10 @ 3 m、高 4 m）：三種「斷面切到幾根桿」決定一切', 14, TITLE, bold=True)
    W = World(80, 196, 25.5, 25.5)
    # members
    XT = [3, 6, 9, 12, 15, 18, 21, 24, 27]
    TOP = [(3, 6), (6, 9), (9, 12), (12, 15), (15, 18), (18, 21), (24, 27)]
    DIAG = [("/", 0), ("X", 3), ("\\", 6), ("X", 9), (None, 12), ("X", 15), ("\\", 18), ("/", 21), ("X", 24), ("\\", 27)]
    S.area([W(12, 0), W(12, 4), W(15, 4), W(15, 0)], IL4, 0.18)
    S.area([W(21, 0), W(21, 4), W(24, 4), W(24, 0)], IL3, 0.12)
    for i in range(10):
        c = IL2 if i == 2 else INK
        S.line(*W(3 * i, 0), *W(3 * i + 3, 0), c, 3.4 if i == 2 else 2)
    for a, b in TOP:
        S.line(*W(a, 4), *W(b, 4), INK, 2)
    for x in XT:
        S.line(*W(x, 0), *W(x, 4), IL3 if x == 6 else INK, 3.4 if x == 6 else 1.6)
    for d, x0 in DIAG:
        if d is None:
            continue
        ends = []
        if d in ('X', '/'):
            ends.append(((x0, 0), (x0 + 3, 4)))
        if d in ('X', '\\'):
            ends.append(((x0, 4), (x0 + 3, 0)))
        for p0, p1 in ends:
            if d == 'X':
                S.line(*W(*p0), *W(*p1), ORG, 1.3, dash='4 3')
            elif x0 == 6:
                S.line(*W(*p0), *W(*p1), LOAD, 3.6)
            else:
                S.line(*W(*p0), *W(*p1), INK, 1.8)
    for i in range(11):
        S.node(*W(3 * i, 0), 2.6)
    for x in XT:
        S.node(*W(x, 4), 2.6)
    for x in (0, 12, 18):
        S.roller(*W(x, 0), s=0.75)
    S.pin(*W(30, 0), s=0.75)
    S.circ(*W(21, 0), 7, 'none', IL3, 2)
    for x, t in ((0, 'a'), (12, 'b'), (18, 'c'), (30, 'e')):
        S.text(W.X(x), W.Y(0) + 40, t, 12.5, INK, bold=True)
    S.text(W.X(21) - 10, W.Y(0) + 20, 'd', 12.5, IL3, 'end', bold=True)
    S.text(W.X(6), W.Y(4) - 8, 'k', 12, IL3, bold=True)
    S.text(W.X(6) - 4, W.Y(0) + 16, 'm', 12, IL3, 'end', bold=True)
    S.text(W.X(9) + 4, W.Y(0) + 16, 'n', 12, IL2, 'start', bold=True)
    S.halo(W.X(7.5) + 8, W.Y(2.6), 'kn', 12, LOAD, 'start', True)
    # callouts
    S.text(W.X(13.5), W.Y(4) - 26, '① 12–15 無斜桿', 11.5, IL4, bold=True)
    S.text(W.X(13.5), W.Y(4) - 12, '只切到兩根平行弦 → 剪力釋放', 10.5, IL4)
    S.text(W.X(22.5), W.Y(4) - 26, '② 21–24 只切兩根', 11.5, IL3, bold=True)
    S.text(W.X(22.5), W.Y(4) - 12, '共點於 d → 等效內鉸', 10.5, IL3)
    S.text(W.X(4.5), W.Y(4) - 26, '③ X 型 = 細長拉桿', 11.5, ORG, bold=True)
    S.text(W.X(4.5), W.Y(4) - 12, '（橘虛線，只受拉）', 10.5, ORG)
    S.text(870, 166, 'kn：單斜桿', 11.5, LOAD, 'end', bold=True)
    S.text(870, 182, '可拉可壓', 11, LOAD, 'end')
    # IL rows
    rows = [('R_a', 0, 62, IL1, '向上為正'), ('N_kn', 2, 72, LOAD, '拉為正'),
            ('N_km', 1, 80, IL3, '拉為正'), ('N_mn', 3, 80, IL2, '拉為正')]
    xs_all = sorted(set(list(range(0, 31, 3)) + [4, 8]))
    for r, (nm, idx, sc, c, sub) in enumerate(rows):
        oy = (318, 436, 584, 712)[r]
        Wp = World(80, oy, 25.5, sc)
        axis(S, Wp, 0, 30)
        pts = [(x, il_2022_3(x)[idx]) for x in xs_all]
        il_plot(S, Wp, pts, c, 2.4)
        S.text(10, oy - 18, nm, 13, c, 'start', bold=True)
        S.text(10, oy - 3, sub, 10.5, MUT, 'start')
        for x in xs_all:
            v = pts[xs_all.index(x)][1]
            if abs(v) > 1e-12:
                lab = {1: '1', 0.75: '3/4', 0.5: '1/2', 0.25: '1/4', -0.25: '−1/4', -1 / 6: '−1/6',
                       -5 / 8: '−5/8', 5 / 16: '5/16', -5 / 16: '−5/16', 1 / 3: '1/3', 2 / 3: '2/3',
                       3 / 8: '3/8', -3 / 8: '−3/8', 0.5 + 0: '1/2'}
                key = min(lab, key=lambda q: abs(q - v))
                t = lab[key] if abs(key - v) < 1e-9 else None
                show = (nm == 'R_a' and x in (0, 15, 21)) or (nm == 'N_kn' and x in (6, 9, 21)) or \
                       (nm == 'N_km' and x in (4, 6, 9, 15)) or (nm == 'N_mn' and x in (6, 15, 21))
                dot(S, Wp, x, v, c, t if show else None, r=2.8, size=11.5)
    Wkm = World(80, 584, 25.5, 80)
    S.line(Wkm.X(4), Wkm.Y(0) + 6, Wkm.X(4), Wkm.Y(1 / 3) - 2, MOM, 1, dash='2 2')
    S.halo(Wkm.X(4) - 8, Wkm.Y(1 / 3) - 30, 'x = 4：折點不在節點上', 11, MOM, 'end', True)
    S.halo(Wkm.X(4) - 8, Wkm.Y(1 / 3) - 16, '（3–6 細長拉桿換手）', 11, MOM, 'end', True)
    S.halo(Wp.X(16.5), 436 - 34, 'N_kn 沒有恆零平台：最大是壓力 −5/8', 11, LOAD, 'start', True)
    S.halo(Wp.X(19), 318 - 40, 'x > 12 後 R_a 不為零，還會變號', 11, IL1, 'start', True)
    return S.render()


# ---------------------------------------------------------------- 6-1 SA-2016-2
def il_2016_2(xi):
    return (6 * xi + 3 * xi ** 2 - xi ** 3) / 8


def fe_2016_2(braced=False, n=20):
    Lm = 1.0
    nodes = [(0, k * Lm / n) for k in range(n + 1)] + [(k * Lm / n, Lm) for k in range(1, n + 1)]
    fr = Frame(nodes)
    for i in range(len(nodes) - 1):
        fr.add(i, i + 1, EA=1e8)
    fr.support(0, True, True, True)
    fr.support(len(nodes) - 1, False, True)
    if braced:
        fr.support(n, True, False)
    beam = [n] + list(range(n + 1, 2 * n + 1))
    res = fr.solve_many([{k: (0, -1, 0)} for k in beam])
    return [k / n for k in range(n + 1)], [r[1][len(nodes) - 1][1] for r in res]


def fig_6_1():
    xi, fe = fe_2016_2()
    assert max(abs(a - il_2016_2(x)) for x, a in zip(xi, fe)) < 1e-6
    _, wrong = fe_2016_2(braced=True)
    S = SVG(900, 340, 'SA-2016-2 側移')
    S.text(450, 22, 'SA-2016-2：基本結構取「A 端固定的懸臂剛架」，側移自動包含在撓曲線裡', 14, TITLE, bold=True)
    Lp = 170
    ax, ay = 110, 300
    # undeformed
    S.line(ax, ay, ax, ay - Lp, GHOST, 2, dash='5 4'); S.line(ax, ay - Lp, ax + Lp, ay - Lp, GHOST, 2, dash='5 4')
    S.fixed(ax, ay, s=1.0)
    # deformed (EI chosen so that tip rise = 0.30 L visually)
    k = 0.30 / (8 / 6)                      # 1/EI in units of L^-? : v(L) = (8/6)L^3/EI
    col = [(ax - Lp * k * 0.5 * (y) ** 2, ay - Lp * y) for y in frange(0, 1, 30)]   # u = -M y^2/2EI, M=L
    uB = -k * 0.5
    thB = k * 1.0
    beam = []
    for x in frange(0, 1, 40):
        v = thB * x + k * x * x * (3 - x) / 6
        beam.append((ax + Lp * (uB + x), ay - Lp * (1 + v)))
    S.pl(col, IL5, 3.6); S.pl(beam, IL5, 3.6)
    S.arrow(beam[-1][0] + 16, beam[-1][1] + 34, beam[-1][0] + 16, beam[-1][1] + 2, REAC, 2.4)
    S.text(beam[-1][0] + 22, beam[-1][1] + 26, '1', 13, REAC, 'start', bold=True)
    S.arrow(ax, ay - Lp - 18, col[-1][0], ay - Lp - 18, ORG, 2, L=7, W=3)
    S.text(ax + 4, ay - Lp - 26, '側移 L³/2EI', 11.5, ORG, 'start', bold=True)
    S.text(ax - 16, ay - Lp + 4, 'B', 12.5, INK, 'end', bold=True)
    S.text(ax - 22, ay - 4, 'A', 12.5, INK, 'end', bold=True)
    S.text(ax + Lp + 6, ay - Lp + 16, 'C（拿掉）', 12, INK, 'start')
    S.text(215, 324, '柱：彎矩恆為 L（剪力 0）→ 單曲率、頂端必側移', 11.5, IL5)
    # IL
    W = World(480, 270, 360, 200)
    axis(S, W, 0, 1)
    il_plot(S, W, [(x, il_2016_2(x)) for x in frange(0, 1, 50)], IL5, 3)
    S.pl([W(x, y) for x, y in zip(xi, wrong)], MUT, 2, dash='6 4')
    for x in (0.25, 0.5, 0.75):
        dot(S, W, x, il_2016_2(x), IL5, f'{il_2016_2(x):.3f}', dx=-6, dy=-8, anchor='end')
    dot(S, W, 1, 1, IL5, '1', dx=8, dy=4, anchor='start')
    S.text(W.X(0), W.Y(0) + 20, 'B', 12.5, INK, bold=True)
    S.text(W.X(1), W.Y(0) + 20, 'C', 12.5, INK, bold=True)
    S.text(660, 52, 'IL_VC(x) = (6L²x + 3Lx² − x³)/(8L³)', 14, IL5, bold=True)
    S.text(660, 72, '在 B 端斜率 3/(4L) ≠ 0：B 會轉、也會側移', 11.5, IL5)
    wm = wrong[len(xi) // 2]
    dot(S, W, 0.5, wm, MUT, f'漏側移（B 當不動）：{wm:.3f}', dx=8, dy=20, anchor='start', bold=False)
    S.text(660, 312, '實線（柔度法）與剛架有限元逐點相符；虛線是誤當無側移的錯答案', 11.5, MUT)
    return S.render()


# ---------------------------------------------------------------- 7-1 SA-2011-3
def il_2011_MC(x, L=30.0):
    MB = lambda u: -u * (L * L - u * u) / (4 * L * L)
    if x <= L:
        return 0.5 * MB(x)
    simp = (x - L) * 15 / 30 if x <= 45 else (2 * L - x) * 15 / 30
    return simp + 0.5 * MB(2 * L - x)


def fig_7_1():
    L, w = 30.0, 2.0
    n = 3000
    h = 2 * L / n
    xs = [k * h for k in range(n + 1)]
    ys = [il_2011_MC(x) for x in xs]
    pos = sum((ys[k] + ys[k + 1]) / 2 * h for k in range(n) if xs[k] >= L)
    neg = sum((ys[k] + ys[k + 1]) / 2 * h for k in range(n) if xs[k] < L)
    assert abs(pos - 84.375) < 1e-3 and abs(neg + 28.125) < 1e-3
    assert abs(il_2011_MC(45) - 195 / 32) < 1e-12
    assert abs(il_2011_MC(L / math.sqrt(3)) + 1.443) < 1e-3
    assert abs(w * pos - 168.75) < 2e-3 and abs(w * (pos + neg) - 112.5) < 2e-3
    S = SVG(900, 356, 'SA-2011-3 M_C 載重佈置')
    S.text(450, 22, 'SA-2011-3（依比例）：均佈載重只鋪在 IL 為正的那一跨', 14, TITLE, bold=True)
    W = World(70, 104, 12.5)
    beam_line(S, W, 0, 60)
    S.roller(*W(0)); S.roller(*W(30)); S.pin(*W(60))
    yt = W.Y(0) - 30
    S.rect(W.X(30), yt, W.X(60) - W.X(30), 22, '#c8e6c9', IL1, 1)
    for x in frange(30, 60, 12):
        S.arrow(W.X(x), yt + 2, W.X(x), W.Y(0) - 4, IL1, 1.3, L=6, W=2.6)
    S.text(W.X(45), yt - 7, 'w = 2 kN/m（只佈 BD）', 12.5, IL1, bold=True)
    S.rect(W.X(0), yt + 6, W.X(30) - W.X(0), 16, 'none', LOAD, 1.2, dash='4 3')
    S.text(W.X(15), yt, 'AB 跨不放（放了會抵銷）', 11.5, LOAD)
    for x, t in ((0, 'A'), (30, 'B'), (45, 'C'), (60, 'D')):
        S.text(W.X(x) + (0 if t == 'C' else 16), W.Y(0) + (18 if t == 'C' else 16), t, 12.5, INK, 'middle' if t == 'C' else 'start', bold=True)
    S.line(W.X(45), W.Y(0) - 8, W.X(45), W.Y(0) + 8, IL3, 2.4)
    Wp = World(70, 250, 12.5, 14)
    axis(S, Wp, 0, 60)
    il_plot(S, Wp, [(x, y) for x, y in zip(xs[::25], ys[::25])], IL3, 2.8, op=0.0)
    S.area([Wp(x, 0) for x in (30,)] + [Wp(x, y) for x, y in zip(xs, ys) if x >= 30][::20] + [Wp(60, 0)], IL1, 0.25)
    S.area([Wp(0, 0)] + [Wp(x, y) for x, y in zip(xs, ys) if x <= 30][::20] + [Wp(30, 0)], LOAD, 0.22)
    dot(S, Wp, 45, il_2011_MC(45), IL3, '+195/32 = 6.094 m', dy=-10)
    xm = L / math.sqrt(3)
    dot(S, Wp, xm, il_2011_MC(xm), LOAD, '−1.443 m @ x = L/√3', dy=20)
    S.halo(Wp.X(45), Wp.Y(2.2), '+84.375 m²', 13, '#1b5e20', 'middle', True)
    S.halo(Wp.X(15), Wp.Y(0) - 8, '−28.125 m²', 12, LOAD, 'middle', True)
    S.rect(130, 296, 640, 50, '#fff', '#cfd8dc', 1, rx=8)
    S.text(450, 316, '只鋪 BD：M_max,C = 2 × 84.375 = 168.75 kN·m　✓', 13, IL1, bold=True)
    S.text(450, 336, '鋪滿全長：2 × (84.375 − 28.125) = 112.5 kN·m　✗ 少 33%，而且是不保守的錯', 12.5, LOAD)
    return S.render()


# ---------------------------------------------------------------- 7-2 SA-2004-2
def fig_7_2():
    il = lambda x: 3 * x / 40 if x <= 10 else (1 - x / 40 if x <= 40 else 0)
    P = [20, 40, 40, 40]
    off = [0, 2.4, 3.9, 5.4]
    def eff(k):                          # 第 k 軸壓在峰值 x=10
        x1 = 10 - off[k]
        return sum(p * il(x1 + o) for p, o in zip(P, off)), x1
    vals = [eff(k)[0] for k in range(3)]
    assert abs(vals[1] - 96.9) < 1e-9 and abs(vals[0] - 93.3) < 1e-9 and abs(vals[2] - 93.15) < 1e-9
    # 斜率法則：P1 在左：20*3/40 - 120/40 < 0 ；P1,P2 在左：60*3/40 - 80/40 > 0
    assert 20 * 3 / 40 - 120 / 40 < 0 < 60 * 3 / 40 - 80 / 40
    S = SVG(900, 376, 'SA-2004-2 車隊極值')
    S.text(450, 22, 'SA-2004-2（依比例）：bc 桿影響線 ＋ 卡車臨界位置（第二軸壓在峰值）', 14, TITLE, bold=True)
    W = World(90, 282, 18, 190)
    axis(S, W, 0, 40)
    il_plot(S, W, [(0, 0), (10, 0.75), (40, 0)], IL2, 2.8)
    S.text(W.X(4), W.Y(0.42), '斜率 +3/40', 11.5, IL2, 'end')
    S.text(W.X(25), W.Y(0.45), '斜率 −1/40', 11.5, IL2)
    for x, t in ((0, 'a'), (10, 'b'), (20, 'c'), (30, 'd'), (40, 'e')):
        S.text(W.X(x), W.Y(0) + 20, t, 12.5, INK, bold=True)
    x1 = 7.6
    for p, o in zip(P, off):
        x = x1 + o
        y = il(x)
        drop(S, W, x, y, IL2)
        dot(S, W, x, y, IL2, None, r=3)
        top = W.Y(0.75) - 70
        S.arrow(W.X(x), top, W.X(x), top + 18 + p * 0.55, LOAD, 2.4 if p == 40 else 1.8)
        S.text(W.X(x), top - 6, f'{p}', 11.5, LOAD, bold=True)
        S.text(W.X(x) + (0 if o else -4), W.Y(y) + (-8 if o != 2.4 else -10) - (12 if o == 0 else 0),
               f'{y:g}', 10.5, IL2, 'middle')
    S.arrow(W.X(21), W.Y(0.75) - 56, W.X(16), W.Y(0.75) - 56, INK, 2)
    S.text(W.X(21.5), W.Y(0.75) - 52, '行駛方向（20 kN 為前導）', 11.5, INK, 'start')
    # trial table
    tx = 600
    ty = 0
    S.rect(tx, 92 + ty, 280, 120, '#fff', '#cfd8dc', 1, rx=8)
    S.text(tx + 140, 112 + ty, '逐一把輪子放到峰值 x = 10', 12.5, TITLE, bold=True)
    rows = [('20 kN（第 1 軸）', vals[0], False), ('40 kN（第 2 軸）', vals[1], True), ('40 kN（第 3 軸）', vals[2], False)]
    for i, (t, v, best) in enumerate(rows):
        yy = 138 + ty + i * 24
        S.text(tx + 16, yy, t, 12, INK, 'start', bold=best)
        S.text(tx + 264, yy, f'{v:.2f} kN' + (' ★' if best else ''), 12, LOAD if best else INK, 'end', bold=best)
    S.text(tx + 140, 206 + ty, 'ΣP·s：+(60·3−80)/40 > 0 換號 → 第 2 軸', 10.5, MUT)
    S.text(450, 334, '最重的不一定放峰值就最大：前導 20 kN 落在陡的左坡（3/40），後三軸落在緩的右坡（1/40）', 12, INK)
    S.text(450, 358, 'F_bc,max = 20(0.57) + 40(0.75) + 40(0.7125) + 40(0.675) = 96.9 kN（拉）', 12.5, LOAD, bold=True)
    return S.render()


# ---------------------------------------------------------------- 8-1 SA-2018-4
def v_2018_4(x):
    EI = 800.0
    if x > 10:
        x = 20 - x
    if x <= 5:
        return x * (x * x - 25) / 51200
    s = x - 5
    return s * (300 - 4 * s * s) / (48 * EI) + (-35 / 32) * s * (10 - s) / (2 * EI)


def fe_2018_4():
    xs = [k * 0.5 for k in range(41)]
    nodes = [(x, 0) for x in xs] + [(2, -4), (18, -4)]
    fr = Frame(nodes)
    for i in range(40):
        fr.add(i, i + 1, EA=1e9, EI=800)
    F, G = 41, 42
    fr.add(10, F, EA=1e9, EI=800); fr.add(30, G, EA=1e9, EI=800)
    fr.support(0, False, True); fr.support(40, False, True)
    fr.support(F, True, True, True); fr.support(G, True, True, True)
    disp, _ = fr.solve({20: (0, -1, 0)})
    return xs, [-disp[i][1] for i in range(41)]


def fig_8_1():
    xs, fe = fe_2018_4()
    assert max(abs(a - v_2018_4(x)) for x, a in zip(xs, fe)) < 1e-7
    assert abs(v_2018_4(10) - 55 / 6144) < 1e-12
    assert abs(v_2018_4(5 / math.sqrt(3)) + 5 * math.sqrt(3) / 9216) < 1e-12
    S = SVG(900, 392, 'SA-2018-4 位移影響線')
    S.text(450, 22, 'SA-2018-4（依比例）：位移影響線 ＝「在 C 施加單位力」的撓曲線 —— 不拆任何束制', 14, TITLE, bold=True)
    W = World(150, 80, 30)
    beam_line(S, W, 0, 20)
    S.line(*W(5, 0), *W(2, -4), INK, 4); S.line(*W(15, 0), *W(18, -4), INK, 4)
    S.roller(*W(0)); S.roller(*W(20))
    S.fixed(*W(2, -4), rot=-37, s=0.9); S.fixed(*W(18, -4), rot=37, s=0.9)
    load(S, W.X(10), W.Y(0), lab='1（只放這一次）')
    for x, y, t, an in ((0, 0, 'A', 'end'), (5, 0, 'B', 'start'), (15, 0, 'D', 'end'), (20, 0, 'E', 'start'),
                        (2, -4, 'F', 'end'), (18, -4, 'G', 'start')):
        S.text(W.X(x) + (-10 if an == 'end' else 10), W.Y(y) - 8, t, 12.5, INK, an, bold=True)
    S.text(W.X(10) + 8, W.Y(0) + 18, 'C', 12.5, INK, 'start', bold=True)
    S.text(W.X(10), W.Y(-1.6), '對稱 + 忽略軸向變形 ⟹ u = 0、v_B = v_D = 0', 11.5, MUT)
    S.text(W.X(10), W.Y(-1.6) + 17, '⟹ B、D 當不動支承，斜撐退化成轉動彈簧 4EI/5', 11.5, MUT)
    Wp = World(150, 302, 30, 9000)
    axis(S, Wp, 0, 20)
    il_plot(S, Wp, [(x, v_2018_4(x)) for x in frange(0, 20, 160)], IL3, 2.8)
    dot(S, Wp, 10, 55 / 6144, IL3, '55/6144 ≈ 0.00895 m/kN', dy=-10)
    xm = 5 / math.sqrt(3)
    dot(S, Wp, xm, v_2018_4(xm), IL3, '−0.00094', dy=22)
    dot(S, Wp, 20 - xm, v_2018_4(xm), IL3, '−0.00094', dy=22)
    for x in (0, 5, 15, 20):
        dot(S, Wp, x, 0, INK, None, r=2.6)
    S.text(Wp.X(0) - 12, Wp.Y(0) + 4, 'IL_vC', 12.5, IL3, 'end', bold=True)
    S.text(Wp.X(0) - 12, Wp.Y(0) + 20, '（向下為正）', 10.5, MUT, 'end')
    S.text(450, 378, '縱距單位是「長度／力」：外跨為負＝載重放在 AB 或 DE 會把 C 頂起來（蹺蹺板）', 12, INK)
    return S.render()


# ---------------------------------------------------------------- 9-1 SA-2025-2 five ILs
def il_2025_2(x):
    RE = max(x - 12, 0) / 4
    RC = (max(x - 4, 0) - 12 * RE) / 4
    RA = 1 - RC - RE
    MA = -(x - 8 * RC - 16 * RE)            # 講義：下緣受拉為正（解析檔取上緣受拉為正，差一個負號）
    return RA, RC, RE, MA


def fig_9_1():
    tbl = {0: (1, 0, 0, 0), 4: (1, 0, 0, -4), 6: (0.5, 0.5, 0, -2), 8: (0, 1, 0, 0),
           12: (-1, 2, 0, 4), 16: (0, 0, 1, 0)}
    for x, v in tbl.items():
        assert all(abs(a - b) < 1e-12 for a, b in zip(il_2025_2(x), v)), (x, il_2025_2(x))
    VF = lambda x, side: il_2025_2(x)[0] - (1 if (x < 6 or (x == 6 and side < 0)) else 0)
    assert VF(6, -1) == -0.5 and VF(6, 1) == 0.5 and VF(12, 1) == -1
    S = SVG(900, 630, 'SA-2025-2 五條影響線')
    S.text(450, 22, 'SA-2025-2（依比例）：五條影響線全部是直線段，折點只在 A、B、F、C、D、E', 14, TITLE, bold=True)
    W = World(170, 76, 42)
    beam_line(S, W, 0, 16)
    S.wall(W.X(0), 52, 100, side=-1)
    S.hinge(*W(4), 5.5, MOM); S.hinge(*W(12), 5.5, MOM)
    S.roller(*W(8)); S.roller(*W(16))
    S.line(W.X(6), W.Y(0) - 11, W.X(6), W.Y(0) + 11, IL2, 2.4)
    ks = [0, 4, 6, 8, 12, 16]
    for x, t in zip(ks, 'ABFCDE'):
        if t == 'A':
            S.text(W.X(x) + 12, W.Y(0) + 22, t, 12.5, INK, 'start', bold=True)
        else:
            S.text(W.X(x), W.Y(0) - 14, t, 12.5, IL2 if t == 'F' else INK, bold=True)
        S.line(W.X(x), 100, W.X(x), 586, GHOST, 0.8, dash='2 4')
    rows = [
        ('R_A', '（↑ 為正）', IL1, 40, lambda x: [(x, il_2025_2(x)[0])]),
        ('R_C', '', IL5, 32, lambda x: [(x, il_2025_2(x)[1])]),
        ('R_E', '', IL3, 40, lambda x: [(x, il_2025_2(x)[2])]),
        ('M_A', '（m；下緣受拉為正）', IL4, 9, lambda x: [(x, il_2025_2(x)[3])]),
        ('V_F', '', IL2, 44, None),
    ]
    labs = {
        'R_A': {0: '1', 4: '1'}, 'R_C': {8: '1', 12: '2'}, 'R_E': {16: '1'},
        'M_A': {4: '−4', 12: '+4'}, 'V_F': {}}
    oys = [172, 330, 398, 466, 540]
    for (nm, sub, c, sc, fn), oy in zip(rows, oys):
        Wp = World(170, oy, 42, sc)
        axis(S, Wp, 0, 16)
        if nm == 'V_F':
            pts = [(0, 0), (4, 0), (6, VF(6, -1)), (6, VF(6, 1)), (8, 0), (12, -1), (16, 0)]
        else:
            pts = [p for x in ks for p in fn(x)]
        il_plot(S, Wp, pts, c, 2.8)
        S.text(20, oy - 6, nm, 14, c, 'start', bold=True)
        if sub:
            S.text(20, oy + 11, sub, 10.5, MUT, 'start')
        for x, y in pts:
            dot(S, Wp, x, y, c, None, r=2.8)
        for x, t in labs[nm].items():
            y = dict(pts)[x]
            dot(S, Wp, x, y, c, t, dy=(-9 if y > 0 else 18))
        if nm == 'R_A':
            dot(S, Wp, 12, -1, c, '−1', dx=-8, dy=12, anchor='end')
        if nm == 'V_F':
            dot(S, Wp, 6, -0.5, c, '−0.5', dx=-6, dy=16, anchor='end')
            dot(S, Wp, 6, 0.5, c, '+0.5', dx=6, dy=-4, anchor='start')
            dot(S, Wp, 12, -1, c, '−1', dy=18)
            S.text(Wp.X(6) + 40, Wp.Y(0) + 16, '跳 1、兩側平行', 11, c, 'start')
    S.halo(World(170, 330, 42, 32).X(12) + 12, 330 - 64 + 6, '槓桿效應：載重在 D 時 C 要出 2', 11, IL5, 'start', True)
    S.halo(World(170, 172, 42, 40).X(12) + 12, 172 + 40 + 4, 'A 被往下拉（上拔）', 11, IL1, 'start', True)
    S.text(450, 616, 'A–B 段：R_A 平移不轉（固定端只釋放垂直力）、R_C 與 R_E 為 0（主段不動）；D–E 段只有 R_E 自己動', 11.5, MUT)
    return S.render()


# ---------------------------------------------------------------- 9-2 SA-2003-4
def fig_9_2():
    L = 10.0
    Cy = propped_Cy
    VB = lambda x: -Cy(x) if x < 5 else 1 - Cy(x)
    MB = lambda x: 5 * Cy(x) - max(x - 5, 0)
    assert abs(Cy(5) - 5 / 16) < 1e-12 and abs(VB(5.0000001) - 11 / 16) < 1e-6
    assert abs(MB(5) - 25 / 16) < 1e-12 and abs(MB(2.5) - 0.4296875) < 1e-12 and abs(MB(7.5) - 0.6640625) < 1e-12
    S = SVG(900, 520, 'SA-2003-4 三條影響線')
    S.text(450, 22, 'SA-2003-4（依比例，L = 10 m）：先有 C_y 的曲線，V_B、M_B 只是它的靜力組合', 14, TITLE, bold=True)
    W = World(190, 70, 56)
    beam_line(S, W, 0, L)
    S.wall(W.X(0), 46, 94, side=-1); S.roller(*W(L))
    S.line(W.X(5), W.Y(0) - 10, W.X(5), W.Y(0) + 10, IL2, 2.4)
    for x, t in ((0, 'A'), (5, 'B'), (10, 'C')):
        if t == 'A':
            S.text(W.X(x) + 12, W.Y(0) + 22, t, 12.5, INK, 'start', bold=True)
        else:
            S.text(W.X(x), W.Y(0) - 14, t, 12.5, INK, bold=True)
        S.line(W.X(x), 96, W.X(x), 500, GHOST, 0.8, dash='2 4')
    xs = frange(0, L, 80)
    # Cy
    Wp = World(190, 200, 56, 90)
    axis(S, Wp, 0, L)
    il_plot(S, Wp, [(x, Cy(x)) for x in xs], IL5, 2.8)
    S.text(20, 194, 'C_y', 14, IL5, 'start', bold=True)
    S.text(20, 211, 'x²(3L−x)/2L³', 11, MUT, 'start')
    for x, t in ((2.5, '0.0859'), (5, '5/16'), (7.5, '0.6328'), (10, '1')):
        dot(S, Wp, x, Cy(x), IL5, t, dy=(4 if x == 10 else -9), dx=(-10 if x == 10 else 0), anchor=('end' if x == 10 else 'middle'))
    # VB
    Wv = World(190, 330, 56, 90)
    axis(S, Wv, 0, L)
    il_plot(S, Wv, [(x, -Cy(x)) for x in xs if x <= 5] + [(x, 1 - Cy(x)) for x in xs if x >= 5], IL2, 2.8)
    S.text(20, 324, 'V_B', 14, IL2, 'start', bold=True)
    S.text(20, 341, '−C_y ｜ 1 − C_y', 11, MUT, 'start')
    dot(S, Wv, 5, -5 / 16, IL2, '−5/16', dx=-6, dy=16, anchor='end')
    dot(S, Wv, 5, 11 / 16, IL2, '+11/16', dx=6, dy=-4, anchor='start')
    S.text(Wv.X(5) + 40, Wv.Y(0.25), '跳 1', 11.5, MOM, 'start', bold=True)
    # MB
    Wm = World(190, 470, 56, 40)
    axis(S, Wm, 0, L)
    S.pl([Wm(0, 0), Wm(5, 2.5), Wm(10, 0)], GHOST, 1.8, dash='6 4')
    il_plot(S, Wm, [(x, MB(x)) for x in xs], IL4, 2.8)
    S.text(20, 464, 'M_B（m）', 14, IL4, 'start', bold=True)
    S.text(20, 481, '5C_y − ⟨x−5⟩', 11, MUT, 'start')
    dot(S, Wm, 5, 25 / 16, IL4, '25/16 = 1.5625', dx=-8, dy=-6, anchor='end')
    dot(S, Wm, 2.5, MB(2.5), IL4, '0.4297', dy=-9)
    dot(S, Wm, 7.5, MB(7.5), IL4, '0.6641', dy=-9)
    S.text(Wm.X(7.6), Wm.Y(1.5), '簡支梁 ab/L = 2.5（虛線）', 11, MUT, 'start')
    S.text(450, 512, '固定端讓 C_y 曲線在 A 附近貼平 → B 的彎矩只剩簡支值的 62.5%', 11.5, MUT)
    return S.render()


# ======================= driver =======================
FIGS = {
    '0-1': fig_0_1, '1-1': fig_1_1, '2-1': fig_2_1, '2-2': fig_2_2, '3-1': fig_3_1,
    '4-1': fig_4_1, '5-1': fig_5_1, '5-2': fig_5_2, '6-1': fig_6_1, '7-1': fig_7_1,
    '7-2': fig_7_2, '8-1': fig_8_1, '9-1': fig_9_1, '9-2': fig_9_2,
}


def inject(html):
    import re
    n = 0
    for fid, fn in FIGS.items():
        pat = re.compile(r'(<!--FIG:%s-->\s*<div class="fig">\s*)<svg.*?</svg>' % re.escape(fid), re.S)
        svg = fn()
        html, k = pat.subn(lambda m: m.group(1) + svg, html)
        if k != 1:
            raise SystemExit(f'marker FIG:{fid} found {k} times')
        n += k
    return html, n


if __name__ == '__main__':
    import sys, pathlib
    if len(sys.argv) > 1 and sys.argv[1] == '--preview':
        out = pathlib.Path(sys.argv[2] if len(sys.argv) > 2 else 'preview.html')
        body = ''.join(f'<h3>{k}</h3><div style="border:1px solid #ccc;margin:8px 0">{fn()}</div>' for k, fn in FIGS.items())
        out.write_text('<!doctype html><meta charset="utf-8"><body style="max-width:940px">' + body, encoding='utf-8')
        print('preview', out)
        sys.exit()
    p = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else
                     pathlib.Path(__file__).resolve().parent.parent / 'study' / 'lecture-SA-U1-3.html')
    html, n = inject(p.read_text(encoding='utf-8'))
    p.write_text(html, encoding='utf-8')
    print(f'{p}: {n} figures regenerated')

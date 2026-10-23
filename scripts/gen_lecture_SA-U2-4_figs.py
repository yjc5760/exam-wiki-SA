#!/usr/bin/env python3
"""gen_lecture_SA-U2-4_figs.py — 產生 study/lecture-SA-U2-4.html 的計算式 SVG 圖解

做法與 gen_lecture_SA-U1-2_figs.py 相同：HTML 內以 <!--FIG:id--> 標記圖位，本腳本只替換
標記後 <div class="fig"> 裡的 <svg>…</svg>，圖說（.cap）與正文不動，可重複執行。

和手繪版的差別：所有變形曲線、彎矩圖、勁度係數都由內建的平面剛架直接勁度法求解器（mech.py 段，
純 Python）算出 —— 變形曲線由 v'' = M/EI 逐段積分並檢查閉合、彎矩圖由桿端力回代；
每張圖都以 assert 對照 raw/solutions/ 各題解析的數值（SA-2010-4、2011-4、2012-4、2018-2、
2022-4、2025-1、2025-4），任何一個對不上就停止、不寫檔。

用法：python scripts/gen_lecture_SA-U2-4_figs.py [study/lecture-SA-U2-4.html]
"""

# ======================= svglib.py (same as gen_lecture_SA-U1-2_figs.py) =======================
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
# ======================= mech.py =======================
"""Tiny plane-frame direct-stiffness solver (pure Python) + member shape / BMD helpers.

Every number drawn in the U2-4 figures comes from here, so the drawings are
consistent with the hand solutions quoted in the text (asserted in each fig_*).
Conventions: global x right, y up, rotations counter-clockwise positive.
Member local axis i->j; local +y = local x rotated +90 deg.
Member loads act in local -y (i.e. 'downward' for a beam drawn left->right).
"""


def _solve(A, b):
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        piv = M[c][c]
        if abs(piv) < 1e-14:
            raise ValueError('singular stiffness matrix')
        for r in range(n):
            if r != c:
                fct = M[r][c] / piv
                if fct:
                    for k in range(c, n + 1):
                        M[r][k] -= fct * M[c][k]
    return [M[i][n] / M[i][i] for i in range(n)]


class Frame:
    def __init__(self):
        self.N, self.E, self.fix, self.F, self.spr = [], [], {}, {}, []

    def node(self, x, y):
        self.N.append((x, y))
        return len(self.N) - 1

    def el(self, i, j, EI=1.0, EA=1e9, load=None):
        """load: ('udl', w) | ('pt', P, a)  (local -y)"""
        self.E.append(dict(i=i, j=j, EI=EI, EA=EA, load=load))
        return len(self.E) - 1

    def support(self, n, ux=1, uy=1, rz=1):
        self.fix[n] = (ux, uy, rz)

    def load(self, n, fx=0.0, fy=0.0, m=0.0):
        a = self.F.get(n, [0.0, 0.0, 0.0])
        self.F[n] = [a[0] + fx, a[1] + fy, a[2] + m]

    def spring(self, n1, dof, k, n2=None):
        """dof 0/1/2 ; n2=None -> grounded spring"""
        self.spr.append((n1, dof, k, n2))

    # ---- element kinematics ----
    def geom(self, e):
        (x1, y1), (x2, y2) = self.N[e['i']], self.N[e['j']]
        L = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        return L, (x2 - x1) / L, (y2 - y1) / L

    @staticmethod
    def kloc(L, EI, EA):
        a, b, c, d, g = EA / L, 12 * EI / L ** 3, 6 * EI / L ** 2, 4 * EI / L, 2 * EI / L
        return [[a, 0, 0, -a, 0, 0], [0, b, c, 0, -b, c], [0, c, d, 0, -c, g],
                [-a, 0, 0, a, 0, 0], [0, -b, -c, 0, b, -c], [0, c, g, 0, -c, d]]

    @staticmethod
    def T(c, s):
        t = [[0.0] * 6 for _ in range(6)]
        for o in (0, 3):
            t[o][o], t[o][o + 1], t[o + 1][o], t[o + 1][o + 1], t[o + 2][o + 2] = c, s, -s, c, 1
        return t

    @staticmethod
    def fef(L, load):
        """fixed-end forces ON the member, local, [Fx,Fy,M]i + [Fx,Fy,M]j"""
        if not load:
            return [0.0] * 6
        if load[0] == 'udl':
            w = load[1]
            return [0, w * L / 2, w * L * L / 12, 0, w * L / 2, -w * L * L / 12]
        P, a = load[1], load[2]
        b = L - a
        return [0, P * b * b * (3 * a + b) / L ** 3, P * a * b * b / L ** 2,
                0, P * a * a * (a + 3 * b) / L ** 3, -P * a * a * b / L ** 2]

    def solve(self):
        n = 3 * len(self.N)
        K = [[0.0] * n for _ in range(n)]
        R = [0.0] * n
        for nd, f in self.F.items():
            for k in range(3):
                R[3 * nd + k] += f[k]
        for e in self.E:
            L, c, s = self.geom(e)
            kl, t, ff = self.kloc(L, e['EI'], e['EA']), self.T(c, s), self.fef(L, e['load'])
            kg = [[sum(t[a][p] * kl[a][b] * t[b][q] for a in range(6) for b in range(6))
                   for q in range(6)] for p in range(6)]
            idx = [3 * e['i'] + k for k in range(3)] + [3 * e['j'] + k for k in range(3)]
            for p in range(6):
                R[idx[p]] -= sum(t[a][p] * ff[a] for a in range(6))
                for q in range(6):
                    K[idx[p]][idx[q]] += kg[p][q]
        for n1, dof, k, n2 in self.spr:
            a = 3 * n1 + dof
            K[a][a] += k
            if n2 is not None:
                b = 3 * n2 + dof
                K[b][b] += k
                K[a][b] -= k
                K[b][a] -= k
        free = [d for d in range(n) if not self.fix.get(d // 3, (0, 0, 0))[d % 3]]
        x = _solve([[K[p][q] for q in free] for p in free], [R[p] for p in free])
        self.D = [0.0] * n
        for d, v in zip(free, x):
            self.D[d] = v
        return self

    def d(self, nd):
        return self.D[3 * nd:3 * nd + 3]

    def end_forces(self, k):
        """local end forces on member k: [Ni,Vi,Mi,Nj,Vj,Mj] (+y local, ccw)"""
        e = self.E[k]
        L, c, s = self.geom(e)
        kl, t, ff = self.kloc(L, e['EI'], e['EA']), self.T(c, s), self.fef(L, e['load'])
        dg = self.d(e['i']) + self.d(e['j'])
        dl = [sum(t[a][b] * dg[b] for b in range(6)) for a in range(6)]
        return [sum(kl[a][b] * dl[b] for b in range(6)) + ff[a] for a in range(6)]

    def M_of(self, k):
        """internal moment M(x) of member k (sagging + , i.e. tension on local -y side)"""
        e = self.E[k]
        L, _, _ = self.geom(e)
        f = self.end_forces(k)
        Mi, Vi, load = f[2], f[1], e['load']

        def M(x):
            m = -Mi + Vi * x
            if load and load[0] == 'udl':
                m -= load[1] * x * x / 2
            elif load:
                m -= load[1] * max(0.0, x - load[2])
            return m
        return M, L

    def shape(self, k, amp, n=60):
        """deformed member polyline (world coords): v'' = M/EI integrated from end i"""
        e = self.E[k]
        L, c, s = self.geom(e)
        t = self.T(c, s)
        dg = self.d(e['i']) + self.d(e['j'])
        dl = [sum(t[a][b] * dg[b] for b in range(6)) for a in range(6)]
        M, _ = self.M_of(k)
        h = L / n
        v, th = dl[1], dl[2]
        vs = [v]
        for m in range(n):
            x0 = m * h
            k1 = M(x0) / e['EI']; k2 = M(x0 + h / 2) / e['EI']; k3 = M(x0 + h) / e['EI']
            v += th * h + h * h * (k1 / 3 + k2 * 2 / 3) / 2     # Simpson-ish 2nd integral
            th += h * (k1 + 4 * k2 + k3) / 6
            vs.append(v)
        err = abs(vs[-1] - dl[4]) + abs(th - dl[5])
        scale = max(1e-9, max(abs(q) for q in dl))
        assert err < 2e-3 * scale + 1e-9, ('shape closure', k, err)
        # remove tiny numerical drift linearly so the end lands exactly on node j
        drift = vs[-1] - dl[4]
        (x1, y1) = self.N[e['i']]
        pts = []
        for m, vv in enumerate(vs):
            xi = m / n
            vv -= drift * xi
            ua = dl[0] + (dl[3] - dl[0]) * xi
            pts.append((x1 + c * xi * L + amp * (ua * c - vv * s),
                        y1 + s * xi * L + amp * (ua * s + vv * c)))
        return pts

    def bmd(self, k, sc, n=60):
        """BMD polygon (world coords) drawn on the tension side; returns (pts, M(x), L)"""
        e = self.E[k]
        L, c, s = self.geom(e)
        M, _ = self.M_of(k)
        (x1, y1) = self.N[e['i']]
        nx, ny = -s, c
        pts = [(x1, y1)]
        for m in range(n + 1):
            x = L * m / n
            off = -M(x) * sc
            pts.append((x1 + c * x + nx * off, y1 + s * x + ny * off))
        pts.append((x1 + c * L, y1 + s * L))
        return pts, M, L

    def bmd_at(self, k, xi, sc):
        """screen-independent: point at fraction xi on member k offset to the BMD line"""
        e = self.E[k]
        L, c, s = self.geom(e)
        M, _ = self.M_of(k)
        (x1, y1) = self.N[e['i']]
        off = -M(xi * L) * sc
        return (x1 + c * xi * L - s * off, y1 + s * xi * L + c * off), M(xi * L)


def near(a, b, tol=1e-6):
    return abs(a - b) <= tol * max(1.0, abs(b))


def frac(v, den=(1, 2, 3, 4, 5, 6, 7, 8, 12, 14, 16, 24, 48, 96)):
    """pretty fraction string for a value known to be a simple rational"""
    for d in den:
        n = round(v * d)
        if abs(n / d - v) < 1e-6:
            if d == 1:
                return f'{n}'
            return f'{n}/{d}'
    return f'{v:.3f}'


def impose(F, vals):
    """set nodal displacements directly (unit-displacement experiments); vals {(node,dof): v}"""
    F.D = [0.0] * (3 * len(F.N))
    for (nd, k), v in vals.items():
        F.D[3 * nd + k] = v
    return F


def node_force(F, nd):
    """resultant global force the members exert ON node nd reversed = force that must be applied"""
    out = [0.0, 0.0, 0.0]
    for k, e in enumerate(F.E):
        if nd not in (e['i'], e['j']):
            continue
        L, c, s = F.geom(e)
        f = F.end_forces(k)
        o = 0 if e['i'] == nd else 3
        out[0] += c * f[o] - s * f[o + 1]
        out[1] += s * f[o] + c * f[o + 1]
        out[2] += f[o + 2]
    return out
# ======================= figs_a.py =======================
"""shared helpers + §0–§2 figures"""
BLUE_D = '#0d47a1'
GRN_D = '#1b5e20'
PUR_D = '#4a148c'
RED_D = '#b71c1c'


def members(S, W, F, ks=None, c=INK, w=4, skip=()):
    for k, e in enumerate(F.E):
        if (ks is not None and k not in ks) or k in skip:
            continue
        S.line(*W(*F.N[e['i']]), *W(*F.N[e['j']]), c, w)


def ghost(S, W, F, ks=None):
    members(S, W, F, ks, GHOST, 1.6)
    for k, e in enumerate(F.E):
        if ks is not None and k not in ks:
            continue
        S.line(*W(*F.N[e['i']]), *W(*F.N[e['j']]), GHOST, 1.6, dash='5 4')


def shape(S, W, F, k, amp, c=REAC, w=3, dash=None):
    S.pl([W(*p) for p in F.shape(k, amp)], c, w, dash=dash)


def max_disp(F, ks):
    m = 1e-12
    for k in ks:
        e = F.E[k]
        pts = F.shape(k, 1.0)
        (x1, y1), (x2, y2) = F.N[e['i']], F.N[e['j']]
        n = len(pts) - 1
        for q, (x, y) in enumerate(pts):
            x0, y0 = x1 + (x2 - x1) * q / n, y1 + (y2 - y1) * q / n
            m = max(m, ((x - x0) ** 2 + (y - y0) ** 2) ** 0.5)
    return m


def amp_for(F, ks, px, scale):
    return px / (max_disp(F, ks) * scale)


def udl(S, x1, x2, y, h=18, n=None, c=LOAD, label=None):
    n = n or max(3, int((x2 - x1) / 22))
    S.line(x1, y - h, x2, y - h, c, 1.8)
    for k in range(n + 1):
        xx = x1 + (x2 - x1) * k / n
        S.arrow(xx, y - h, xx, y - 2, c, 1.6, L=7, W=3)
    if label:
        S.text((x1 + x2) / 2, y - h - 6, label, 12.5, c, bold=True, italic=True)


def lock(S, x, y, c=MUT):
    """small clamp symbol meaning 'rotation locked'"""
    S.rect(x - 8, y - 8, 16, 16, '#eceff1', c, 1.4, rx=2)
    S.line(x - 5, y - 5, x + 5, y + 5, c, 1.4)
    S.line(x - 5, y + 5, x + 5, y - 5, c, 1.4)


def mat(S, x, y, cells, cw=46, ch=24, size=12, colors=None, bold_cols=(), bg=None):
    """draw a bracketed matrix with top-left at (x,y); cells: list of rows of str"""
    r, c = len(cells), len(cells[0])
    W_, H_ = c * cw, r * ch
    if bg:
        for j, col in bg.items():
            S.rect(x + j * cw + 2, y + 2, cw - 4, H_ - 4, col, 'none', 0, rx=4)
    for i, row in enumerate(cells):
        for j, t in enumerate(row):
            col = (colors[i][j] if colors else INK)
            S.text(x + j * cw + cw / 2, y + i * ch + ch / 2 + 4.5, t, size, col, bold=j in bold_cols)
    for xx, sg in ((x, 1), (x + W_, -1)):
        S.pl([(xx + 6 * sg, y), (xx, y), (xx, y + H_), (xx + 6 * sg, y + H_)], INK, 1.6, join='miter')
    return W_, H_


def beam3(load_left=True):
    """A fixed — B roller — C fixed, spans L=1, UDL w=1 on AB (used in §0 and §6)"""
    F = Frame()
    a, b, c = F.node(0, 0), F.node(1, 0), F.node(2, 0)
    F.el(a, b, load=('udl', 1.0) if load_left else None)
    F.el(b, c)
    F.support(a); F.support(b, 1, 1, 0); F.support(c)
    return F


# ---------------------------------------------------------------- 0-1
def fig_0_1():
    S = SVG(900, 360, '力法與位移法：先假設什麼')
    F = beam3().solve()
    thB = F.d(1)[2]
    assert near(thB, 1 / 96)
    S.line(450, 14, 450, 270, GHOST, 1.4, dash='6 5')
    S.text(230, 30, '力法：未知量 = 多餘力', 15, LOAD, bold=True)
    S.text(670, 30, '位移法：未知量 = 節點位移', 15, GOOD, bold=True)
    # left : primary = cantilever, redundants X1 (V_B), X2 (V_C), X3 (M_C)
    W = World(60, 130, 170)
    S.line(*W(0, 0), *W(2, 0), INK, 4)
    S.fixed(*W(0, 0), rot=90)
    udl(S, W.X(0), W.X(1), W.Y(0), label='w')
    S.roller(*W(1, 0), c=GHOST); S.fixed(*W(2, 0), rot=-90, c=GHOST)
    S.arrow(W.X(1), W.Y(0) + 58, W.X(1), W.Y(0) + 6, LOAD, 2.6)
    S.text(W.X(1) + 8, W.Y(0) + 54, 'X₁', 13, LOAD, 'start', bold=True)
    S.arrow(W.X(2) - 4, W.Y(0) + 58, W.X(2) - 4, W.Y(0) + 6, LOAD, 2.6)
    S.text(W.X(2) - 12, W.Y(0) + 54, 'X₂', 13, LOAD, 'end', bold=True)
    S.moment(W.X(2), W.Y(0), 17, ccw=True, c=LOAD, a0=200, span=250)
    S.text(W.X(2) + 6, W.Y(0) - 26, 'X₃', 13, LOAD, 'start', bold=True)
    S.text(W.X(0), W.Y(0) + 30, 'A', 12, INK, bold=True)
    S.text(230, 214, '拆掉 B、C 的多餘約束 → 懸臂梁（基本結構）', 12.5, RED_D)
    S.text(230, 234, '靜不定度 3 → 3 個未知力 X₁、X₂、X₃', 12.5, RED_D, bold=True)
    S.text(230, 254, '「拆哪幾個」要人來選，選法不唯一', 12, LOAD)
    # right : real structure, deflected shape with the single unknown theta_B
    W2 = World(500, 130, 170)
    amp = amp_for(F, (0, 1), 26, 170)
    ghost(S, W2, F)
    members(S, W2, F, w=4)
    shape(S, W2, F, 0, amp, GOOD, 3); shape(S, W2, F, 1, amp, GOOD, 3)
    S.fixed(*W2(0, 0), rot=90); S.roller(*W2(1, 0)); S.fixed(*W2(2, 0), rot=-90)
    udl(S, W2.X(0), W2.X(1), W2.Y(0) - 2, label='w')
    S.moment(W2.X(1), W2.Y(0), 20, ccw=True, c=MOM, a0=200, span=240)
    S.halo(W2.X(1) + 24, W2.Y(0) - 22, 'θB', 13.5, MOM, 'start', bold=True)
    for x, t in ((0, 'A'), (1, 'B'), (2, 'C')):
        S.text(W2.X(x) + (10 if x == 1 else 0), W2.Y(0) + 34, t, 12, INK, bold=True)
    S.text(670, 214, 'A、C 固定，B 不能上下 → 只有 θB 能動', 12.5, GRN_D)
    S.text(670, 234, '自由度 1 → 1 個未知量（數出來的，唯一）', 12.5, GRN_D, bold=True)
    S.text(670, 254, f'綠線＝真實變形（放大）：θB = wL³/96EI（逆時針）', 12, GOOD)
    S.rect(170, 284, 560, 62, '#e3f2fd', '#90caf9', 1.6, rx=9)
    S.text(450, 308, '矩陣分析法 = 位移法 + 一套機械化的簿記規則', 14, BLUE_D, bold=True)
    S.text(450, 330, '同一根梁：力法 3 個未知數、位移法 1 個。未知數少、又不必挑，才交得給電腦', 12, REAC)
    return S.render()


# ---------------------------------------------------------------- 1-1
def beam2dof():
    """A fixed — B roller — C roller, L=1 each : DOFs D1 = θB, D2 = θC"""
    F = Frame()
    a, b, c = F.node(0, 0), F.node(1, 0), F.node(2, 0)
    F.el(a, b); F.el(b, c)
    return F


def fig_1_1():
    S = SVG(900, 400, '單位位移實驗')
    S.text(450, 22, '同一根兩自由度梁做兩場實驗，各量出 [K] 的一行（L、EI 各跨相同）', 14, BLUE_D, bold=True)
    panels = [(14, '#fafafa', '#cfd8dc', MUT, '結構與自由度', None),
              (310, '#e8f5e9', '#a5d6a7', GOOD, '實驗 1：D₁ = θB = 1，θC 鎖住', 1),
              (606, '#e3f2fd', '#90caf9', REAC, '實驗 2：D₂ = θC = 1，θB 鎖住', 2)]
    K = {}
    for x0, bg, bd, col, title, exp in panels:
        S.rect(x0, 36, 280, 222, bg, bd, 1, rx=9)
        S.text(x0 + 140, 58, title, 13, col, bold=True)
        W = World(x0 + 30, 150, 110)
        F = beam2dof()
        if exp:
            impose(F, {(exp, 2): 1.0})
            ghost(S, W, F)
            shape(S, W, F, 0, 0.32, col, 3.2); shape(S, W, F, 1, 0.32, col, 3.2)
            fb, fc = node_force(F, 1)[2], node_force(F, 2)[2]
            K[(1, exp)], K[(2, exp)] = fb, fc
            names = {(1, 1): 'K₁₁', (2, 1): 'K₂₁', (1, 2): 'K₁₂', (2, 2): 'K₂₂'}
            for nd, val in ((1, fb), (2, fc)):
                if abs(val) < 1e-9:
                    continue
                S.moment(W.X(nd), W.Y(0), 17 if nd == exp else 13, ccw=val > 0, c=col, w=2.6,
                         a0=210, span=230)
                S.halo(W.X(nd) + (2 if nd == 1 else -4), W.Y(0) - 30,
                       f'{names[(nd, exp)]} = {frac(val)}EI/L', 12.5, col, 'middle', bold=True)
        else:
            members(S, W, F)
            S.moment(W.X(1), W.Y(0), 16, ccw=True, c=MOM, a0=210, span=230)
            S.moment(W.X(2), W.Y(0), 16, ccw=True, c=MOM, a0=210, span=230)
            S.halo(W.X(1), W.Y(0) - 26, 'D₁ = θB', 12.5, MOM, bold=True)
            S.halo(W.X(2) - 6, W.Y(0) - 26, 'D₂ = θC', 12.5, MOM, bold=True)
        S.fixed(*W(0, 0), rot=90); S.roller(*W(1, 0)); S.roller(*W(2, 0))
        for x, t in ((0, 'A'), (1, 'B'), (2, 'C')):
            S.text(W.X(x) + (12 if x else 0), W.Y(0) + 40, t, 12, INK, bold=True)
        if exp == 1:
            S.text(x0 + 140, 222, 'AB、BC 都在 B 端被轉 1：4 + 4 = 8', 12, GRN_D)
            S.text(x0 + 140, 242, 'BC 的遠端 C 被「傳」到 2（鎖住它要出力）', 12, GRN_D)
        elif exp == 2:
            S.text(x0 + 140, 222, '只有 BC 被轉：近端 4、遠端 B 拿到 2', 12, BLUE_D)
            S.text(x0 + 140, 242, 'AB 沒有變形，不參與', 12, BLUE_D)
        else:
            S.text(x0 + 140, 222, 'A 固定；B、C 只能轉、不能上下', 12, INK)
            S.text(x0 + 140, 242, '共 2 個自由度 → [K] 是 2×2', 12, INK)
    assert near(K[(1, 1)], 8) and near(K[(2, 1)], 2) and near(K[(1, 2)], 2) and near(K[(2, 2)], 4)
    # assembled matrix
    S.text(206, 302, '[K] =', 15, INK, 'end', bold=True)
    S.text(240, 302, 'EI', 13, INK); S.line(230, 306, 250, 306, INK, 1.2); S.text(240, 320, 'L', 13, INK)
    cells = [[frac(K[(1, 1)]), frac(K[(1, 2)])], [frac(K[(2, 1)]), frac(K[(2, 2)])]]
    mat(S, 262, 282, cells, 52, 28, 15, colors=[[GOOD, REAC], [GOOD, REAC]], bold_cols=(0, 1),
        bg={0: '#e8f5e9', 1: '#e3f2fd'})
    S.text(288, 352, '第 1 行＝實驗 1', 11.5, GOOD); S.text(340, 370, '第 2 行＝實驗 2', 11.5, REAC)
    S.rect(420, 276, 466, 104, '#f3e5f5', '#ce93d8', 1, rx=9)
    S.text(653, 298, 'K₁₂ = K₂₁ = 2EI/L　（Maxwell–Betti 互易定理）', 13, PUR_D, bold=True)
    S.text(436, 322, '實驗 1 的力對實驗 2 的位移作的功', 12, MOM, 'start')
    S.text(436, 342, '＝ 實驗 2 的力對實驗 1 的位移作的功', 12, MOM, 'start')
    S.text(436, 366, '兩場實驗各自量到的「交叉力」必定相等 → 拿來驗算', 12, MOM, 'start', bold=True)
    return S.render()


# ---------------------------------------------------------------- 2-2
def frame_2018_2():
    F = Frame()
    A, B, C, D = F.node(0, 1), F.node(0, 0), F.node(1, 0), F.node(1, -1)
    F.el(A, B); F.el(B, C, load=('pt', 1.0, 0.5)); F.el(C, D)
    F.support(A); F.support(D)
    return F


def fig_2_2():
    S = SVG(900, 400, 'SA-2018-2 自由度盤點')
    F = frame_2018_2().solve()
    u, _, tB = F.d(1)
    tC = F.d(2)[2]
    assert near(u, -1 / 48) and near(tB, -1 / 24) and near(tC, 1 / 24)
    S.text(450, 22, 'SA-2018-2（依比例）：六個候選分量，被「忽略軸向變形」刪到剩三個', 14, BLUE_D, bold=True)
    # left panel: candidates
    W = World(150, 182, 112)
    members(S, W, F)
    S.fixed(*W(0, 1), rot=180); S.fixed(*W(1, -1))
    S.arrow(W.X(0.5), W.Y(0) - 46, W.X(0.5), W.Y(0) - 4, LOAD, 2.6)
    S.text(W.X(0.5) + 8, W.Y(0) - 34, 'P', 13, LOAD, 'start', bold=True)
    for (x, y), t, dx in (((0, 1), 'A（頂部固定）', 14), ((0, 0), 'B', -12), ((1, 0), 'C', 12),
                          ((1, -1), 'D（底部固定）', 14)):
        S.text(W.X(x) + dx, W.Y(y) + 5, t, 12, INK, 'start' if dx > 0 else 'end', bold=True)
    # crossed-out vB, vC  and merged uB=uC
    for x, lab in ((0, 'vB = 0'), (1, 'vC = 0')):
        xx = W.X(x)
        S.arrow(xx, W.Y(0) + 50, xx, W.Y(0) + 12, GHOST, 2)
        S.line(xx - 7, W.Y(0) + 24, xx + 7, W.Y(0) + 38, LOAD, 2)
        S.line(xx + 7, W.Y(0) + 24, xx - 7, W.Y(0) + 38, LOAD, 2)
        S.text(xx + (-12 if x == 0 else 12), W.Y(0) + 64, lab, 11.5, LOAD,
               'end' if x == 0 else 'start')
    S.arrow(W.X(0) - 62, W.Y(0) - 2, W.X(0) - 22, W.Y(0) - 2, MOM, 2.4)
    S.text(W.X(0) - 66, W.Y(0) + 2, 'u', 13, MOM, 'end', bold=True)
    S.arrow(W.X(1) + 22, W.Y(0) - 2, W.X(1) + 62, W.Y(0) - 2, GHOST, 2)
    S.text(W.X(1) + 66, W.Y(0) + 2, 'uC ≡ uB', 11.5, MUT, 'start')
    for x, t in ((0, 'θB'), (1, 'θC')):
        S.moment(W.X(x), W.Y(0), 15, ccw=True, c=MOM, a0=160 if x == 0 else 200, span=220)
        S.halo(W.X(x) + (-22 if x == 0 else 22), W.Y(0) - 22, t, 12.5, MOM,
               'end' if x == 0 else 'start', bold=True)
    S.rect(16, 330, 400, 60, '#e8f5e9', '#a5d6a7', 1, rx=8)
    S.text(216, 352, 'AB、CD 垂直不縮 → vB = vC = 0；BC 水平不伸 → uB = uC', 12, GRN_D)
    S.text(216, 374, '6 個候選 → 剩 u、θB、θC，[K] 為 3×3', 12.5, GRN_D, bold=True)
    # right panel: computed deflected shape
    W2 = World(600, 182, 112)
    amp = amp_for(F, (0, 1, 2), 30, 112)
    ghost(S, W2, F)
    for k in range(3):
        shape(S, W2, F, k, amp, REAC, 3.2)
    S.fixed(*W2(0, 1), rot=180); S.fixed(*W2(1, -1))
    S.arrow(W2.X(0.5), W2.Y(0) - 46, W2.X(0.5), W2.Y(0) - 4, LOAD, 2.6)
    pB = W2(0 + amp * u, 0)
    S.arrow(W2.X(0) - 4, W2.Y(0) + 26, pB[0] - 4, W2.Y(0) + 26, MOM, 2.2, L=7, W=3)
    S.text(W2.X(0) - 30, W2.Y(0) + 46, 'u = −PL³/48EI（向左）', 12, MOM, 'end', bold=True)
    S.text(W2.X(1) + 20, W2.Y(0) - 30, 'θC = +PL²/24EI（逆）', 12, MOM, 'start')
    S.text(W2.X(0) - 18, W2.Y(0) - 30, 'θB = −PL²/24EI（順）', 12, MOM, 'end')
    S.rect(470, 330, 414, 60, '#fff3e0', '#ffcc80', 1, rx=8)
    S.text(677, 352, '藍線＝直接勁度法解出的變形（放大），側移 u ≠ 0', 12, '#e65100')
    S.text(677, 374, 'Z 字型是「點對稱」：垂直載重也會推出側移', 12.5, '#e65100', bold=True)
    return S.render()


# ---------------------------------------------------------------- 2-3
def frame_2012_4():
    F = Frame()
    a, b, c, d = F.node(0, 0), F.node(0, 1), F.node(0.5, 1), F.node(1, 1)
    F.el(a, b); F.el(b, c); F.el(c, d, EI=1e6)
    return F


def fig_2_3():
    S = SVG(900, 380, 'SA-2012-4 剛性桿的蹺蹺板效應')
    S.text(450, 22, 'SA-2012-4（依比例）：令 r₂ = 1（d 點順時針轉），剛性桿 cd 帶著 c 點一起動', 14, BLUE_D, bold=True)
    # correct state
    F = frame_2012_4()
    impose(F, {(2, 1): 0.5, (2, 2): -1.0, (3, 2): -1.0})       # v_c = +L/2, θc = θd = −1 (cw)
    f = F.end_forces(1)
    Mbc, Mcb, Vc = -f[2], -f[5], f[4]                            # cw-positive end moments on bc
    assert near(Mbc, 16) and near(Mcb, 20) and near(Vc, 72)
    K22 = Mcb + Vc * 0.5
    assert near(K22, 56)
    # wrong state: forget v_c
    G = frame_2012_4()
    impose(G, {(2, 2): -1.0, (3, 2): -1.0})
    g = G.end_forces(1)
    K22w = -g[5] + g[4] * 0.5
    assert near(-g[2], 4) and near(-g[5], 8) and near(K22w, 20)
    for x0, FF, col, title in ((10, F, REAC, '正確：c 點同時「轉」又「上升」'),
                               (455, G, ORG, '常見錯誤：只傳轉角、漏掉 vc')):
        W = World(x0 + 40, 330, 150)
        S.text(x0 + 210, 56, title, 13.5, col, bold=True)
        ghost(S, W, FF)
        S.line(*W(0, 0), *W(0, 1), INK, 4)
        shape(S, W, FF, 1, 0.42, col, 3.2)
        vc = FF.d(2)[1]
        S.line(*W(0.5, 1 + 0.42 * vc), *W(1, 1), INK, 8)
        S.fixed(*W(0, 0)); S.pin(*W(1, 1))
        S.text(W.X(0) - 10, W.Y(0) + 4, 'a', 12, INK, 'end', bold=True)
        S.text(W.X(0) - 10, W.Y(1) + 4, 'b', 12, INK, 'end', bold=True)
        S.text(W.X(1) + 12, W.Y(1) + 4, 'd', 12, INK, 'start', bold=True)
        cy = W.Y(1) - (0.42 * 0.5 * 150 if FF is F else 0)
        S.text(W.X(0.5), cy - 14, 'c', 12, INK, bold=True)
        S.moment(W.X(1), W.Y(1), 20, ccw=False, c=MOM, a0=150, span=230)
        S.halo(W.X(1) + 8, W.Y(1) - 30, 'r₂', 13, MOM, 'start', bold=True)
        S.text(W.X(0.75), W.Y(1) + 26, 'EI = ∞', 11.5, MUT)
        if FF is F:
            S.line(W.X(0.5) + 10, W.Y(1), W.X(0.5) + 10, cy, MOM, 1.4, dash='3 3')
            S.halo(W.X(0.5) + 6, (W.Y(1) + cy) / 2 + 4, 'vc = r₂·L/2', 12, MOM, 'end', bold=True)
            lines = [('bc 弦角 ψ = vc ÷ (L/2) = 1', REAC), ('Mbc = 16EI/L，Mcb = 20EI/L', REAC),
                     ('剪力 V = 36EI/L ÷ (L/2) = 72EI/L²', REAC),
                     ('K₂₂ = 20 + 72·(L/2) = 56EI/L ✓', GRN_D)]
        else:
            lines = [('bc 只被轉 1、弦角 ψ = 0', ORG), ('Mbc = 4EI/L，Mcb = 8EI/L', ORG),
                     ('剪力 V = 12EI/L ÷ (L/2) = 24EI/L²', ORG),
                     (f'K₂₂ = 8 + 24·(L/2) = {frac(K22w)}EI/L ✗', LOAD),
                     ('（正解 56EI/L，差將近 3 倍）', LOAD)]
        for j, (t, cc) in enumerate(lines):
            S.text(x0 + 236, 150 + j * 24, t, 11.5, cc, 'start', bold=j >= 3)
    S.text(450, 368, '剛性桿本身不變形、不必建元素矩陣；但它是蹺蹺板 —— 轉角與垂直位移都要傳給相鄰的柔性桿', 12, MUT)
    return S.render()


# ---------------------------------------------------------------- 2-4
def solve_2022_4():
    EI, h = 97200.0, 3.6
    k, kd = 12 * EI / h ** 3, 12 * EI / (2 * h) ** 3
    A = [[2 * k, 2 * kd, 0], [-2 * k, 2 * k + 2 * kd, 0], [0, -4 * k, 4 * k]]
    D1, D2, D3 = _solve(A, [600.0, 500.0, 300.0])
    assert near(k, 25000) and near(kd, 3125)
    assert near(D1, 0.0098) and near(D2, 0.0176) and near(D3, 0.0206)
    Va, Vm = k * D1, kd * D2
    assert near(Va, 245) and near(Vm, 55) and near(2 * Va + 2 * Vm, 600)
    return k, kd, (D1, D2, D3), Va, Vm


def fig_2_4():
    k, kd, Ds, Va, Vm = solve_2022_4()
    S = SVG(900, 420, 'SA-2022-4 剪力棟架與挑高柱')
    S.text(450, 22, 'SA-2022-4（依比例）：一樓右兩跨沒有梁 → m、n 兩柱直通兩層成為挑高柱', 14, BLUE_D, bold=True)
    sc = 22.0
    W = World(130, 340, sc)
    Wd = World(575, 340, sc)
    Y = (0, 3.6, 7.2, 10.8)
    cols = [(0, 0, 1), (0, 1, 2), (0, 2, 3), (4, 0, 1), (4, 1, 2), (4, 2, 3), (8, 0, 2), (8, 2, 3),
            (12, 0, 2), (12, 2, 3)]
    beams = [(0, 4, 1), (0, 12, 2), (0, 12, 3)]
    D = (0.0,) + Ds
    amp = 30 / (Ds[2] * sc)
    for WW, deformed in ((W, False), (Wd, True)):
        if deformed:
            for x, i, j in cols:
                S.line(WW.X(x), WW.Y(Y[i]), WW.X(x), WW.Y(Y[j]), GHOST, 1.2, dash='4 3')
        for x, i, j in cols:
            tall = (j - i) == 2
            c = ORG if tall else INK
            if deformed:
                pts = []
                for q in range(31):
                    xi = q / 30
                    uu = D[i] + (D[j] - D[i]) * (3 * xi * xi - 2 * xi ** 3)
                    pts.append((WW.X(x + amp * uu), WW.Y(Y[i] + (Y[j] - Y[i]) * xi)))
                S.pl(pts, c, 2.4 if tall else 1.8)
            else:
                S.line(WW.X(x), WW.Y(Y[i]), WW.X(x), WW.Y(Y[j]), c, 2.4 if tall else 1.8)
        for x1, x2, lv in beams:
            off = amp * D[lv] if deformed else 0
            S.line(WW.X(x1 + off), WW.Y(Y[lv]), WW.X(x2 + off), WW.Y(Y[lv]), INK, 5)
        for x in (0, 4, 8, 12):
            S.fixed(WW.X(x), WW.Y(0), s=0.7)
    for x, t in ((0, 'a'), (4, 'e'), (8, 'm'), (12, 'n')):
        S.text(W.X(x) + 8, W.Y(0) - 6, t, 12.5, INK, 'start', bold=True, italic=True)
    for lv, t, F_ in ((1, 'b', 100), (2, 'c', 200), (3, 'd', 300)):
        S.text(W.X(0) + 6, W.Y(Y[lv]) - 6, t, 12.5, INK, 'start', bold=True, italic=True)
        S.arrow(W.X(0) - 54, W.Y(Y[lv]), W.X(0) - 4, W.Y(Y[lv]), LOAD, 2.4)
        S.text(W.X(0) - 58, W.Y(Y[lv]) + 4, f'{F_} kN', 11.5, LOAD, 'end', bold=True)
    for x0, x1 in ((0, 4), (4, 8), (8, 12)):
        S.dim(W.X(x0), W.Y(0) + 26, W.X(x1), W.Y(0) + 26, '4 m', size=11)
    for lv in range(3):
        S.arrow(W.X(12) + 22, W.Y(Y[lv]) - 2, W.X(12) + 22, W.Y(Y[lv + 1]) + 2, DIM, 1, L=6, W=3, both=True)
        S.text(W.X(12) + 28, (W.Y(Y[lv]) + W.Y(Y[lv + 1])) / 2 + 4, '3.6 m', 11, DIM, 'start')
    S.halo(W.X(10), W.Y(3.6) + 4, '這裡沒有梁', 11.5, ORG, bold=True)
    S.line(W.X(4.3), W.Y(3.6), W.X(11.7), W.Y(3.6), ORG, 1.2, dash='3 4')
    # deformed labels
    for lv, nm in ((1, 'Δ₁'), (2, 'Δ₂'), (3, 'Δ₃')):
        xx = Wd.X(0 + amp * D[lv])
        S.halo(xx - 8, Wd.Y(Y[lv]) + 4, f'{nm} = {D[lv]*1000:.1f} mm', 11.5, REAC, 'end', bold=True)
    S.text(Wd.X(5), 384, f'一般柱 k = 12EI/h³ = {k:,.0f} kN/m　挑高柱 12EI/(2h)³ = k/8 = {kd:,.0f} kN/m', 11.5, INK)
    S.text(Wd.X(5), 404, f'基底剪力：a、e 各 {Va:.0f} kN，m、n 各 {Vm:.0f} kN，合計 600 kN ✓', 11.5, GRN_D, bold=True)
    S.text(W.X(6), 404, '橘色＝挑高柱（高 7.2 m）', 11.5, ORG, bold=True)
    S.text(Wd.X(6), 48, '梁 EI = ∞：節點不轉，柱呈 S 形（變形放大）', 12, MUT)
    return S.render()


# ---------------------------------------------------------------- 2-5
def fig_2_5():
    import math
    S = SVG(900, 330, '剛接／半剛性／鉸接')
    S.text(450, 22, '同一個節點 B，三種接法：柱端轉角 θ₁、梁端轉角 θ₂ 是否綁在一起', 14, BLUE_D, bold=True)
    cases = [(20, '剛接　kθ → ∞', '#e8f5e9', '#a5d6a7', GOOD, 0.30, 0.30, '1 個轉角自由度', 'θ₁ = θ₂'),
             (310, '半剛性　kθ = 10EI/L（SA-2019-4）', '#fff3e0', '#ffcc80', ORG, 0.38, 0.18,
              '2 個（以彈簧耦合）', 'M = kθ(θ₁ − θ₂)'),
             (600, '鉸接　kθ = 0', '#ffebee', '#ef9a9a', LOAD, 0.42, 0.06, '2 個（完全脫鉤）', 'M = 0')]
    for x0, title, bg, bd, col, t1, t2, ndof, rel in cases:
        S.rect(x0, 38, 280, 200, bg, bd, 1, rx=9)
        S.text(x0 + 140, 60, title, 12.5, col, bold=True)
        cx, cy, Lm = x0 + 110, 112, 110
        # ghost
        S.line(cx, cy, cx, cy + 90, GHOST, 1.5, dash='5 4'); S.line(cx, cy, cx + Lm, cy, GHOST, 1.5, dash='5 4')
        ac, ab = math.pi / 2 - t1, -t2          # screen angles after ccw rotations t1, t2
        S.line(cx, cy, cx + 90 * math.cos(ac), cy + 90 * math.sin(ac), INK, 4)
        S.line(cx, cy, cx + Lm * math.cos(ab), cy + Lm * math.sin(ab), INK, 4)
        if col == ORG:
            S.pl([(cx + (3 + 13 * q / 60) * math.cos(q / 60 * 5 * math.pi),
                   cy + (3 + 13 * q / 60) * math.sin(q / 60 * 5 * math.pi)) for q in range(61)], ORG, 1.6)
        elif col == LOAD:
            S.hinge(cx, cy, 6, LOAD)
        S.circ(cx, cy, 3.5, INK, INK, 1)
        # rotation arcs
        r = 46
        S.pl([(cx + r * math.cos(math.pi / 2 - t1 * q / 10), cy + r * math.sin(math.pi / 2 - t1 * q / 10))
              for q in range(11)], MOM, 2)
        S.text(cx + 30, cy + 58, 'θ₁', 12.5, MOM, 'start', bold=True)
        r2 = 70
        S.pl([(cx + r2 * math.cos(-t2 * q / 10), cy + r2 * math.sin(-t2 * q / 10)) for q in range(11)], REAC, 2)
        S.text(cx + r2 + 6, cy - 4 - 30 * t2, 'θ₂', 12.5, REAC, 'start', bold=True)
        S.text(x0 + 140, 214, ndof, 12.5, col, bold=True)
        S.text(x0 + 140, 232, rel, 12, INK)
    S.rect(120, 252, 660, 66, '#f3e5f5', '#ce93d8', 1, rx=9)
    S.text(450, 274, '半剛性與鉸接：節點要拆成兩個轉角自由度，彈簧當作「零長度元素」', 13, PUR_D, bold=True)
    S.text(450, 298, '[k]彈簧 = kθ [ 1 −1 ; −1 1 ]　 kθ→∞ 退化成剛接（兩自由度合一）、kθ=0 退化成鉸接（兩自由度脫鉤）', 12, MOM)
    return S.render()
# ======================= figs_b.py =======================
"""§3–§6 figures"""
import math


def sg(v, nd=1):
    if abs(v) < 1e-9:
        return "0"
    t = f"{v:+.{nd}f}"
    return t.replace("-", "−")


def force_arrow(S, x, y, val, col, up_len=34, label=None, side='start', dx=8):
    """vertical force arrow at (x,y) on beam axis; val>0 up"""
    if val > 0:
        S.arrow(x, y + up_len + 6, x, y + 6, col, 2.4)
        ly = y + up_len
    else:
        S.arrow(x, y - up_len - 6, x, y - 6, col, 2.4)
        ly = y - up_len
    if label:
        S.halo(x + (dx if side == 'start' else -dx), ly, label, 12.5, col, side, bold=True)


def moment_arrow(S, x, y, val, col, r=18, label=None, lx=0, ly=-28, anchor='middle'):
    S.moment(x, y, r, ccw=val > 0, c=col, w=2.4, a0=200 if val > 0 else -20, span=230)
    if label:
        S.halo(x + lx, y + ly, label, 12.5, col, anchor, bold=True)


# ---------------------------------------------------------------- 3-1
def fig_3_1():
    S = SVG(900, 380, '梁元素四個係數')
    S.text(450, 22, '兩端固定梁的兩場實驗：自由度順序 {vi, θi, vj, θj}，向上、逆時針為正', 14, BLUE_D, bold=True)
    specs = [(14, '#e8f5e9', '#a5d6a7', GOOD, GRN_D, '實驗 A：vi = 1（左端上移 1），其餘鎖住', (0, 1),
              ['12EI/L³', '6EI/L²', '−12EI/L³', '6EI/L²'], (12, 6, -12, 6)),
             (458, '#e3f2fd', '#90caf9', REAC, BLUE_D, '實驗 B：θi = 1（左端逆轉 1 rad），其餘鎖住', (0, 2),
              ['6EI/L²', '4EI/L', '−6EI/L²', '2EI/L'], (6, 4, -6, 2))]
    for x0, bg, bd, col, dcol, title, dof, labels, expect in specs:
        S.rect(x0, 36, 428, 330, bg, bd, 1, rx=10)
        S.text(x0 + 214, 60, title, 13, dcol, bold=True)
        F = Frame()
        i, j = F.node(0, 0), F.node(1, 0)
        F.el(i, j)
        impose(F, {dof: 1.0})
        f = F.end_forces(0)                       # [Ni,Vi,Mi,Nj,Vj,Mj]  (EI = L = 1)
        got = (f[1], f[2], f[4], f[5])
        assert all(near(a, b) for a, b in zip(got, expect)), got
        W = World(x0 + 74, 160, 280)
        amp = 0.16 if dof[1] == 1 else 0.16
        S.line(*W(0, 0), *W(1, 0), GHOST, 1.6, dash='5 4')
        shape(S, W, F, 0, amp, col, 4)
        yi = W.Y(amp * (1 if dof[1] == 1 else 0))
        S.fixed(W.X(0), yi, rot=90, half=18); S.fixed(W.X(1), W.Y(0), rot=-90, half=18)
        if dof[1] == 1:
            S.line(W.X(0) - 28, W.Y(0), W.X(0) - 28, yi, MOM, 1.2)
            S.arrow(W.X(0) - 28, W.Y(0), W.X(0) - 28, yi + 1, MOM, 1.8, L=7, W=3)
            S.text(W.X(0) - 34, (W.Y(0) + yi) / 2 + 4, 'vi = 1', 12, MOM, 'end', bold=True)
        else:
            S.pl([(W.X(0) + 40 * math.cos(-a), W.Y(0) + 40 * math.sin(-a)) for a in
                  [amp * q / 10 for q in range(11)]], MOM, 1.6)
            S.line(W.X(0), W.Y(0), W.X(0) + 50, W.Y(0), MOM, 1, dash='3 3')
            S.text(W.X(0) + 54, W.Y(0) + 18, 'θi = 1', 12, MOM, 'start', bold=True)
        # end actions
        force_arrow(S, W.X(0) + 2, yi, got[0], LOAD, 40, labels[0], 'start')
        moment_arrow(S, W.X(0), yi, got[1], MOM, 20, labels[1], 0, -32 if got[1] > 0 else 34)
        force_arrow(S, W.X(1) - 2, W.Y(0), got[2], LOAD, 40, labels[2].lstrip('−'), 'end', 10)
        moment_arrow(S, W.X(1), W.Y(0), got[3], MOM, 20, labels[3], 26, 40, 'start')
        S.text(W.X(0) - 34, W.Y(0) + 64, 'i 端', 13, INK, bold=True)
        S.text(W.X(1) - 30, W.Y(0) + 64, 'j 端', 13, INK, bold=True)
        # column vector
        S.text(x0 + 24, 296, '量到的四個端力 ＝ [k] 的第', 12.5, dcol, 'start')
        S.text(x0 + 186, 296, '1' if dof[1] == 1 else '2', 13, dcol, 'start', bold=True)
        S.text(x0 + 196, 296, '行：', 12.5, dcol, 'start')
        for q, t in enumerate(labels):
            S.rect(x0 + 24 + q * 98, 310, 90, 30, '#fff', bd, 1, rx=6)
            S.text(x0 + 69 + q * 98, 330, t, 13, dcol, bold=True)
        S.text(x0 + 214, 358, '（剪力 Vi · 彎矩 Mi · 剪力 Vj · 彎矩 Mj）', 11.5, MUT)
    return S.render()


# ---------------------------------------------------------------- 4-1
def fig_4_1():
    S = SVG(900, 340, '桁架桿只感受沿桿的位移')
    S.text(450, 24, '桁架桿只「看得見」沿桿方向的那一份位移（向量依比例畫）', 14, BLUE_D, bold=True)
    ang = math.radians(33.0)
    c, s = math.cos(ang), math.sin(ang)
    xi_, yi_ = 60, 286
    L = 280
    xj, yj = xi_ + L * c, yi_ - L * s
    S.line(xi_, yi_, xj, yj, INK, 5)
    S.pin(xi_, yi_)
    S.circ(xj, yj, 6, '#fff', INK, 2.4)
    S.text(xi_ - 14, yi_ - 6, 'i', 14, INK, bold=True, italic=True)
    S.text(xj - 6, yj + 24, 'j', 14, INK, bold=True, italic=True)
    S.halo(xi_ + 0.45 * L * c + 14, yi_ - 0.45 * L * s + 22, '長度 L，方向 (c, s)', 12.5, MUT, 'start')
    # extension of axis
    S.line(xj, yj, xj + 150 * c, yj - 150 * s, GHOST, 1.2, dash='6 4')
    u, v = 110.0, -12.0                         # displacement of j (px, y-up)
    e = c * u + s * v                          # projection
    px, py = xj + e * c, yj - e * s
    tx, ty = xj + u, yj - v
    S.arrow(xj, yj, tx, ty, REAC, 3)
    S.halo(tx + 8, ty + 18, '節點位移 d = (u, v)', 12.5, REAC, 'start', bold=True)
    S.arrow(xj, yj, px, py, ORG, 3.4)
    S.halo((xj + px) / 2 - 10, (yj + py) / 2 - 16, '伸長 e = c·u + s·v', 12.5, '#e65100', 'end', bold=True)
    S.line(tx, ty, px, py, MUT, 1.4, dash='3 3')
    # right-angle mark at projection foot
    q = 9
    S.pl([(px - q * c, py + q * s), (px - q * c + q * s, py + q * s + q * c), (px + q * s, py + q * c)], MUT, 1.2)
    S.halo(px + 12, py - 26, '垂直分量：只讓桿轉動', 11.5, MUT, 'start')
    S.halo(px + 12, py - 10, '（小變形下不伸長、不出力）', 11.5, MUT, 'start')
    # steps box
    S.rect(560, 60, 326, 236, '#fff3e0', '#ffcc80', 1, rx=9)
    S.text(723, 84, '三個步驟，各自都很直觀', 13, '#e65100', bold=True)
    rows = [('① 投影：只有沿桿分量讓桿伸長', 'e = c·u + s·v'),
            ('② 虎克定律：伸長多少 → 軸力多少', 'N = (EA/L)·e'),
            ('③ 投影回去：軸力分回 x、y', 'Fx = c·N，Fy = s·N')]
    for k, (a, b) in enumerate(rows):
        S.text(576, 114 + k * 52, a, 12.5, '#5d4037', 'start')
        S.text(596, 136 + k * 52, b, 13, '#bf360c', 'start', bold=True)
    S.text(723, 270, '合起來 (EA/L)·[c s]ᵀ[c s] = (EA/L)[c² cs; cs s²]', 12, '#e65100', bold=True)
    S.rect(40, 302, 480, 30, '#e3f2fd', '#90caf9', 1, rx=7)
    S.text(280, 322, '矩陣的秩 = 1 → 對「垂直於桿」的位移完全沒有勁度', 12.5, BLUE_D, bold=True)
    return S.render()


# ---------------------------------------------------------------- 4-2
def truss_solve(free, nodes, bars, P, EA):
    """single free node truss; returns K(2x2), (u,v), bar forces (tension +)"""
    K = [[0.0, 0.0], [0.0, 0.0]]
    info = []
    xa, ya = nodes[free]
    for o in bars:
        xo, yo = nodes[o]
        L = math.hypot(xo - xa, yo - ya)
        c, s = (xo - xa) / L, (yo - ya) / L
        k = EA / L
        kk = [[k * c * c, k * c * s], [k * c * s, k * s * s]]
        for p in range(2):
            for q in range(2):
                K[p][q] += kk[p][q]
        info.append((o, L, c, s, kk))
    u, v = _solve(K, list(P))
    forces = {o: EA / L * (c * (0 - u) + s * (0 - v)) for o, L, c, s, _ in info}
    return K, (u, v), forces, info


def fig_4_2():
    nodes = {'A': (0, 4), 'B': (-3, 0), 'C': (0, 0), 'D': (4, 1)}
    K, (u, v), N, info = truss_solve('A', nodes, 'BCD', (100.0, -225.0), 1e4)
    assert near(K[0][1], 0, 1e-9) and near(K[0][0], 2000) and near(K[1][1], 4500)
    assert near(u, 0.05) and near(v, -0.05) and near(N['B'], -20)
    # equilibrium of node A
    fx = 100 + sum(N[o] * c for o, L, c, s, _ in info)
    fy = -225 + sum(N[o] * s for o, L, c, s, _ in info)
    assert abs(fx) < 1e-6 and abs(fy) < 1e-6
    S = SVG(900, 380, 'SA-2010-4 交叉項抵消')
    S.text(450, 22, 'SA-2010-4（依比例）：AB、AD 的 cs 一正一負，[K] 直接變成對角矩陣', 14, BLUE_D, bold=True)
    W = World(205, 290, 48)
    colors = {'B': GOOD, 'C': MUT, 'D': REAC}
    amp = 22.0
    for o, L, c, s, kk in info:
        S.line(*W(*nodes['A']), *W(*nodes[o]), colors[o], 4)
        S.line(W.X(nodes['A'][0] + amp * u), W.Y(nodes['A'][1] + amp * v), *W(*nodes[o]), colors[o], 1.4, dash='4 3')
    for o in 'BCD':
        S.pin(*W(*nodes[o]), s=0.85)
    S.circ(*W(*nodes['A']), 5, '#fff', INK, 2.2)
    S.arrow(W.X(0) + 6, W.Y(4), W.X(0) + 54, W.Y(4), LOAD, 2.6)
    S.text(W.X(0) + 58, W.Y(4) + 4, '100 kN', 12, LOAD, 'start', bold=True)
    S.arrow(W.X(0), W.Y(4) - 50, W.X(0), W.Y(4) - 7, LOAD, 2.6)
    S.text(W.X(0) + 6, W.Y(4) - 40, '225 kN', 12, LOAD, 'start', bold=True)
    for nm, dx, dy, an in (('A', -10, -8, 'end'), ('B', -10, 22, 'end'), ('C', 10, 22, 'start'), ('D', 12, 4, 'start')):
        S.text(W.X(nodes[nm][0]) + dx, W.Y(nodes[nm][1]) + dy, nm, 13, INK, an, bold=True)
    S.circ(W.X(amp * u), W.Y(4 + amp * v), 4, ORG, ORG, 1)
    S.halo(W.X(amp * u) + 8, W.Y(4 + amp * v) - 6, 'A′', 12, ORG, 'start', bold=True)
    S.text(20, 350, f'橘點 A′＝解出的位移：u = {u*1000:.0f} mm（→）、v = {-v*1000:.0f} mm（↓）', 11.5, ORG, 'start')
    S.text(20, 368, f'虛線＝變形後的桿件（位移放大 {amp:.0f} 倍）', 11.5, ORG, 'start')
    for x0, x1, t in ((-3, 0, '3 m'), (0, 4, '4 m')):
        S.dim(W.X(x0), W.Y(0) + 34, W.X(x1), W.Y(0) + 34, t, size=11)
    S.text(W.X(-3) - 4, W.Y(2) + 4, 'L=5', 11, GOOD, 'end')
    S.text(W.X(2.2), W.Y(2.8) - 4, 'L=5', 11, REAC, 'start')
    # matrices
    x = 470
    S.text(x, 64, '各桿對節點 A 的貢獻（kN/m，c、s 由 A 指向支承）', 12.5, INK, 'start', bold=True)
    y = 80
    for o, L, c, s, kk in info:
        S.text(x, y + 30, f'A{o}', 13, colors[o], 'start', bold=True)
        S.text(x + 30, y + 22, f'c = {sg(c, 1)}', 11.5, colors[o], 'start')
        S.text(x + 30, y + 40, f's = {sg(s, 1)}', 11.5, colors[o], 'start')
        cells = [[f'{kk[0][0]:.0f}', sg(kk[0][1], 0) if abs(kk[0][1]) > 1e-9 else '0'],
                 [sg(kk[1][0], 0) if abs(kk[1][0]) > 1e-9 else '0', f'{kk[1][1]:.0f}']]
        cols = [[colors[o], LOAD if abs(kk[0][1]) > 1e-9 else colors[o]],
                [LOAD if abs(kk[1][0]) > 1e-9 else colors[o], colors[o]]]
        mat(S, x + 100, y + 6, cells, 62, 22, 12.5, colors=cols)
        y += 62
    S.line(x, y + 2, x + 300, y + 2, INK, 1)
    S.text(x, y + 34, '[K]', 13, INK, 'start', bold=True)
    mat(S, x + 100, y + 12, [[f'{K[0][0]:.0f}', '0'], ['0', f'{K[1][1]:.0f}']], 62, 22, 13,
        colors=[[INK, GOOD], [GOOD, INK]], bold_cols=(0, 1))
    S.text(x + 240, y + 28, '交叉項 960 − 960 = 0', 11.5, GOOD, 'start', bold=True)
    S.text(x + 240, y + 46, 'u、v 解耦，不必解聯立', 11.5, GOOD, 'start')
    S.rect(470, 330, 416, 40, '#fff3e0', '#ffcc80', 1, rx=8)
    S.text(678, 355, f'回代：N(AB) = {sg(N["B"],0)}、N(AC) = {sg(N["C"],0)}、N(AD) = {sg(N["D"],0)} kN，三桿皆受壓', 12, '#e65100', bold=True)
    return S.render()


# ---------------------------------------------------------------- 5-1
def fig_5_1():
    S = SVG(900, 330, '組裝：按自由度編號抄進大矩陣')
    S.text(450, 22, '以 §10 門型剛架為例：三個元素的小矩陣，照旁邊標的自由度「抄」進 3×3（係數單位略：EI/L、EI/L²、EI/L³）',
           13, BLUE_D, bold=True)
    els = [('柱 AB', GOOD, '#e8f5e9', ('θB', 'Δ'), [['4', '−6'], ['−6', '12']]),
           ('梁 BC', REAC, '#e3f2fd', ('θB', 'θC'), [['4', '2'], ['2', '4']]),
           ('柱 CD', ORG, '#fff3e0', ('θC', 'Δ'), [['4', '−6'], ['−6', '12']])]
    order = ['θB', 'θC', 'Δ']
    G = [[[] for _ in range(3)] for _ in range(3)]
    for k, (nm, col, bg, dofs, m) in enumerate(els):
        x0, y0 = 30, 46 + k * 90
        S.rect(x0, y0, 250, 80, bg, col, 1, rx=8)
        S.text(x0 + 12, y0 + 22, nm, 13, col, 'start', bold=True)
        mat(S, x0 + 90, y0 + 18, m, 50, 24, 13, colors=[[col] * 2] * 2)
        for q, d in enumerate(dofs):
            S.text(x0 + 115 + q * 50, y0 + 14, d, 11.5, col, bold=True)
            S.text(x0 + 206, y0 + 34 + q * 24, '← ' + d, 11.5, col, 'start', bold=True)
        for p in range(2):
            for q in range(2):
                G[order.index(dofs[p])][order.index(dofs[q])].append((m[p][q], col))
    # global matrix
    gx, gy, cw, ch = 400, 70, 120, 64
    S.text(gx - 14, gy + 1.5 * ch + 6, '[K] =', 15, INK, 'end', bold=True)
    for q, d in enumerate(order):
        S.text(gx + q * cw + cw / 2, gy - 10, d, 13, MOM, bold=True)
        S.text(gx + 3 * cw + 14, gy + q * ch + ch / 2 + 5, '← ' + d, 12.5, MOM, 'start', bold=True)
    for p in range(3):
        for q in range(3):
            S.rect(gx + q * cw + 3, gy + p * ch + 3, cw - 6, ch - 6, '#fafafa', '#e0e0e0', 1, rx=6)
            items = G[p][q]
            if not items:
                S.text(gx + q * cw + cw / 2, gy + p * ch + ch / 2 + 5, '0', 14, GHOST, bold=True)
                continue
            tot_w = len(items) * 34 + (len(items) - 1) * 14
            sx = gx + q * cw + cw / 2 - tot_w / 2
            for k, (t, col) in enumerate(items):
                xx = sx + k * 48 + 17
                S.text(xx, gy + p * ch + ch / 2 + 6, t, 15, col, bold=True)
                if k:
                    S.text(xx - 24, gy + p * ch + ch / 2 + 6, '+', 14, INK)
    S.pl([(gx + 8, gy), (gx, gy), (gx, gy + 3 * ch), (gx + 8, gy + 3 * ch)], INK, 1.8, join='miter')
    S.pl([(gx + 3 * cw - 8, gy), (gx + 3 * cw, gy), (gx + 3 * cw, gy + 3 * ch), (gx + 3 * cw - 8, gy + 3 * ch)],
         INK, 1.8, join='miter')
    S.text(gx + 1.5 * cw, gy + 3 * ch + 28, '對角線：接在同一自由度上的元素全部相加（8、8、24）', 12, INK)
    S.text(gx + 1.5 * cw, gy + 3 * ch + 48, '空格 = 0：沒有任何元素同時接到這兩個自由度（柱 AB 與 θC 無關）', 12, MUT)
    return S.render()


# ---------------------------------------------------------------- 6-1
def fig_6_1():
    S = SVG(900, 380, '先鎖住、再放開')
    F3 = beam3().solve()                                     # real answer
    FI = beam3(); impose(FI, {})                             # locked
    FII = beam3(load_left=False); impose(FII, {(1, 2): F3.d(1)[2]})
    # consistency: P = -f_F at B equals K * theta
    PB = -(FI.end_forces(0)[5] + FI.end_forces(1)[2])
    assert near(PB, 1 / 12) and near(F3.d(1)[2], PB / 8)
    for k in range(2):
        MI, _ = FI.M_of(k); MII, _ = FII.M_of(k); MR, _ = F3.M_of(k)
        for xx in (0, .25, .5, .8, 1):
            assert near(MI(xx) + MII(xx), MR(xx), 1e-9)
    titles = [('狀態 I：節點全鎖', '#fafafa', '#cfd8dc', '#455a64', FI),
              ('狀態 II：把不平衡力矩反號加回 B', '#e8f5e9', '#a5d6a7', GRN_D, FII),
              ('狀態 I + II = 真實答案', '#e3f2fd', '#90caf9', BLUE_D, F3)]
    sc_w = 230 / 2
    bsc = 0.36 / 0.11                                         # world BMD scale
    for p, (t, bg, bd, col, F) in enumerate(titles):
        x0 = 12 + p * 296
        S.rect(x0, 34, 280, 258, bg, bd, 1, rx=9)
        S.text(x0 + 140, 56, t, 12.5, col, bold=True)
        W = World(x0 + 25, 120, sc_w)
        S.line(*W(0, 0), *W(2, 0), INK, 3.5)
        S.fixed(*W(0, 0), rot=90, half=13); S.roller(*W(1, 0), s=0.8); S.fixed(*W(2, 0), rot=-90, half=13)
        if F is not FII:
            udl(S, W.X(0), W.X(1), W.Y(0), 15, 6)
        if F is FI:
            lock(S, W.X(1), W.Y(0) - 26)
            S.text(W.X(1) + 12, W.Y(0) - 32, 'θB 鎖住', 11, MUT, 'start')
        if F is FII:
            S.moment(W.X(1), W.Y(0), 18, ccw=True, c=GOOD, w=2.6, a0=200, span=230)
            S.halo(W.X(1) + 22, W.Y(0) - 22, '+wL²/12', 12, GOOD, 'start', bold=True)
        # BMD
        Wb = World(x0 + 25, 215, sc_w)
        S.line(*Wb(0, 0), *Wb(2, 0), GHOST, 1.2)
        for k in range(2):
            pts, M, L = F.bmd(k, bsc)
            S.area([Wb(*q) for q in pts], col, 0.18)
            S.pl([Wb(*q) for q in pts[1:-1]], col, 2)
        # labels: end values and span extreme of AB
        labs = []
        for k in range(2):
            M, L = F.M_of(k)
            labs += [(k, 0.0, M(0.0)), (k, 1.0, M(1.0))]
            if F is not FII and k == 0:
                xs = [q / 200 for q in range(201)]
                xm = max(xs, key=lambda q: M(q))
                labs.append((k, xm, M(xm)))
        seen = set()
        for k, xi, val in labs:
            xw = k + xi
            key = (round(xw, 3), round(val, 6))
            if key in seen or abs(val) < 1e-9:
                continue
            seen.add(key)
            (px, py), _ = F.bmd_at(k, xi, bsc)
            X, Y = Wb(px, py)
            txt = ('+' if val > 0 else '−') + frac(abs(val))
            dy = 14 if val > 0 else -6
            if F is FII and k == 1 and xi == 0.0:
                X += 26
            S.halo(X, Y + dy, txt, 11.5, col, 'middle', bold=True)
        S.text(x0 + 140, 268, '單位 wL²；＋＝下緣受拉（畫在受拉側）', 10.5, MUT)
    S.text(304, 120, '+', 22, MUT, bold=True); S.text(600, 120, '=', 22, MUT, bold=True)
    S.rect(120, 304, 660, 64, '#f3e5f5', '#ce93d8', 1, rx=9)
    S.text(450, 326, '{P} = {節點直接外力} − {固端力}：B 點 P = 0 − (−wL²/12 + 0) = +wL²/12', 12.5, PUR_D, bold=True)
    S.text(450, 350, '解 8EI/L · θB = wL²/12 → θB = wL³/96EI；最後內力 = 狀態 I 的固端力 + 狀態 II', 12, MOM)
    return S.render()


# ---------------------------------------------------------------- 6-2
def solve_2011_4():
    nodes = {'A': (3, 4), 'B': (0, 4), 'C': (0, 0), 'D': (6, 0)}
    EA, dl = 1e4, 0.02
    LAC = 5.0
    T0 = EA / LAC * dl
    cA, sA = -0.6, -0.8                            # A -> C
    P = (T0 * cA, T0 * sA)                          # equivalent nodal load = bar pull on A (toward C)
    K, (u, v), N, info = truss_solve('A', nodes, 'BCD', P, EA)
    N['C'] += T0                                    # add back the locked-state force
    assert near(T0, 40) and near(P[0], -24) and near(P[1], -32)
    assert near(u, -9 / 1790) and near(v, -0.0125)
    assert near(N['B'], -16.76, 1e-3) and near(N['C'], 13.97, 1e-3) and near(N['D'], -13.97, 1e-3)
    fx = sum(N[o] * c for o, L, c, s, _ in info); fy = sum(N[o] * s for o, L, c, s, _ in info)
    assert abs(fx) < 1e-6 and abs(fy) < 1e-6        # node A in equilibrium with no external load
    return nodes, T0, P, (u, v), N


def fig_6_2():
    nodes, T0, P, (u, v), N = solve_2011_4()
    S = SVG(900, 330, 'SA-2011-4 製造誤差')
    S.text(450, 22, 'SA-2011-4（依比例）：AC 桿短了 0.02 m —— 同一招「先鎖住、再放開、最後加回」', 14, BLUE_D, bold=True)
    panels = [('狀態 I：鎖住 A，硬把 AC 拉上', '#fafafa', '#cfd8dc', '#455a64'),
              ('狀態 II：放開 A，把桿的拉力當外力', '#e8f5e9', '#a5d6a7', GRN_D),
              ('I + II：真實內力', '#e3f2fd', '#90caf9', BLUE_D)]
    for p, (t, bg, bd, col) in enumerate(panels):
        x0 = 12 + p * 296
        S.rect(x0, 34, 280, 284, bg, bd, 1, rx=9)
        S.text(x0 + 140, 56, t, 12.5, col, bold=True)
        W = World(x0 + 50, 232, 30)
        A = nodes['A']
        amp = 40.0 if p else 0
        Ad = (A[0] + amp * u, A[1] + amp * v)
        for o in 'BCD':
            cc = ORG if o == 'C' else INK
            if p == 0 and o == 'C':
                # short bar drawn with a visible gap, stretched by the dashed line
                d = 0.02 * 18
                S.line(*W(*nodes['C']), *W(A[0] - 0.6 * d * 0, A[1]), cc, 1.2, dash='3 3')
                S.line(*W(*nodes['C']), *W(A[0] - 0.6 * 0.9, A[1] - 0.8 * 0.9), cc, 4)
            else:
                S.line(*W(*nodes[o]), *W(*(Ad if p else A)), cc, 4)
            S.pin(*W(*nodes[o]), s=0.75)
        S.circ(*W(*(Ad if p else A)), 4.5, '#fff', INK, 2)
        for nm, dx, dy, an in (('B', -8, 4, 'end'), ('C', -8, 22, 'end'), ('D', 8, 22, 'start')):
            S.text(W.X(nodes[nm][0]) + dx, W.Y(nodes[nm][1]) + dy, nm, 12, INK, an, bold=True)
        AX, AY = W(*(Ad if p else A))
        if p == 0:
            S.text(AX + 10, AY - 8, 'A', 12, INK, 'start', bold=True)
            lock(S, AX, AY - 26)
            S.arrow(AX, AY, AX - 0.6 * 44, AY + 0.8 * 44, LOAD, 2.4)
            S.halo(AX - 22, AY + 44, f'T₀ = {T0:.0f} kN', 12, LOAD, 'end', bold=True)
            S.halo(AX - 22, AY + 60, '= EAΔ/L', 11, LOAD, 'end')
            S.text(x0 + 140, 268, '桿受拉 → 它把 A「拉向 C」', 12, '#455a64')
            S.text(x0 + 140, 288, '鎖住 A 的力剛好相反（離開 C）', 12, '#455a64')
            S.text(x0 + 140, 306, '這組反力就是「固端力」', 11.5, MUT)
        elif p == 1:
            S.text(AX + 10, AY - 8, 'A′', 12, INK, 'start', bold=True)
            S.arrow(W.X(A[0]), W.Y(A[1]), W.X(A[0]) - 0.6 * 44, W.Y(A[1]) + 0.8 * 44, GOOD, 2.6)
            S.circ(*W(*A), 3, GHOST, GHOST, 1)
            S.text(x0 + 140, 268, f'{{P}} = ({sg(P[0],0)}, {sg(P[1],0)}) kN，方向「拉向 C」', 12, GRN_D, bold=True)
            S.text(x0 + 140, 288, f'解得 u = {sg(u*1000,2)} mm、v = {sg(v*1000,1)} mm', 12, GRN_D)
            S.text(x0 + 140, 306, f'（A 往 C 方向移；圖中放大 {amp:.0f} 倍）', 11.5, MUT)
        else:
            S.text(AX + 10, AY - 8, 'A′', 12, INK, 'start', bold=True)
            for o, (dx, dy, an) in (('B', (0, -10, 'middle')), ('C', (-16, 0, 'end')), ('D', (16, 0, 'start'))):
                mx, my = (W.X(nodes[o][0]) + AX) / 2, (W.Y(nodes[o][1]) + AY) / 2
                tag = 'T' if N[o] > 0 else 'C'
                S.halo(mx + dx, my + dy, f'{sg(N[o],2)}（{tag}）', 11.5, LOAD if tag == 'C' else GOOD, an, bold=True)
            S.text(x0 + 140, 268, f'AC = {sg(N["C"]-T0,2)} + {T0:.0f} = {sg(N["C"],2)} kN（拉）', 12, BLUE_D, bold=True)
            S.text(x0 + 140, 288, '漏掉 T₀ 就會得到 −26.03（壓），整個顛倒', 12, LOAD)
            S.text(x0 + 140, 306, '節點 A：ΣFx = ΣFy = 0 ✓', 11.5, GRN_D)
    return S.render()
# ======================= figs_c.py =======================
"""§7, §8, §10 figures"""


def portal(b=1.0, P=0.0):
    """SA-2025-1 portal: A(0,0) B(0,1) C(1,1) D(1,0); columns EI=1, beam EI=b, L=1"""
    F = Frame()
    A, B, C, D = F.node(0, 0), F.node(0, 1), F.node(1, 1), F.node(1, 0)
    F.el(A, B); F.el(B, C, EI=b); F.el(D, C)
    F.support(A); F.support(D)
    if P:
        F.load(B, fx=P)
    return F


def k_portal(b):
    F = portal(b, 1.0).solve()
    return 1.0 / F.d(1)[0]


# ---------------------------------------------------------------- 7-1
def fig_7_1():
    S = SVG(900, 420, '靜態凝縮：放開一個轉角')
    S.text(450, 22, '把遠端轉角「放開」（凝縮掉）：同一根梁，勁度一定變小', 14, BLUE_D, bold=True)
    # (a) rotation, far end fixed
    Fa = Frame(); i, j = Fa.node(0, 0), Fa.node(1, 0); Fa.el(i, j); impose(Fa, {(i, 2): 1.0})
    fa = Fa.end_forces(0)
    assert near(fa[2], 4) and near(fa[5], 2)
    # (b) rotation, far end pinned  (solve with unit moment, then scale)
    Fb = Frame(); i, j = Fb.node(0, 0), Fb.node(1, 0); Fb.el(i, j)
    Fb.support(i, 1, 1, 0); Fb.support(j, 1, 1, 0); Fb.load(i, m=1.0); Fb.solve()
    kb = 1 / Fb.d(i)[2]
    assert near(kb, 3)
    Fb.D = [x * kb for x in Fb.D]
    fb = Fb.end_forces(0)
    assert near(fb[2], 3) and near(fb[5], 0, 1e-9)
    # (c) sway, both ends clamped against rotation
    Fc = Frame(); i, j = Fc.node(0, 0), Fc.node(1, 0); Fc.el(i, j); impose(Fc, {(j, 1): 1.0})
    fc = Fc.end_forces(0)
    assert near(fc[4], 12) and near(fc[2], -6) and near(fc[5], -6)
    # (d) sway, far end free to rotate
    Fd = Frame(); i, j = Fd.node(0, 0), Fd.node(1, 0); Fd.el(i, j)
    Fd.support(i); Fd.support(j, 1, 0, 0); Fd.load(j, fy=1.0); Fd.solve()
    kd = 1 / Fd.d(j)[1]
    assert near(kd, 3)
    Fd.D = [x * kd for x in Fd.D]
    fd = Fd.end_forces(0)
    assert near(fd[2], -3) and near(fd[5], 0, 1e-9)
    panels = [
        (14, 40, Fa, GOOD, '#e8f5e9', '#a5d6a7', '轉角實驗：遠端固定', [('近端 4EI/L', GOOD), ('遠端 2EI/L', GOOD)], 'rot', 'fix'),
        (458, 40, Fb, ORG, '#fff3e0', '#ffcc80', '轉角實驗：遠端鉸（θj 放開）', [('近端 3EI/L（↓25%）', ORG), ('遠端 0', ORG)], 'rot', 'pin'),
        (14, 214, Fc, GOOD, '#e8f5e9', '#a5d6a7', '側移實驗：兩端都不准轉', [('剪力 12EI/L³', GOOD), ('兩端彎矩 6EI/L²', GOOD)], 'sway', 'fix'),
        (458, 214, Fd, ORG, '#fff3e0', '#ffcc80', '側移實驗：遠端可自由轉', [('剪力 3EI/L³（↓75%）', ORG), ('近端彎矩 3EI/L²', ORG)], 'sway', 'pin')]
    for x0, y0, F, col, bg, bd, title, notes, kind, far in panels:
        S.rect(x0, y0, 428, 160, bg, bd, 1, rx=9)
        S.text(x0 + 214, y0 + 22, title, 13, col, bold=True)
        W = World(x0 + 50, y0 + 96, 230)
        S.line(*W(0, 0), *W(1, 0), GHOST, 1.4, dash='5 4')
        amp = 0.22 if kind == 'rot' else 0.18
        shape(S, W, F, 0, amp, col, 3.6)
        S.fixed(*W(0, 0), rot=90, half=16)
        yj = W.Y(amp * F.d(1)[1])
        if far == 'fix':
            S.fixed(W.X(1), yj, rot=-90, half=16)
        else:
            if kind == 'rot':
                S.pin(*W(1, 0), s=0.8)
            else:
                S.hinge(W.X(1), yj, 5.5, col)
        if kind == 'rot':
            S.moment(W.X(0), W.Y(0), 18, ccw=True, c=MOM, a0=200, span=230)
            S.halo(W.X(0) + 4, W.Y(0) - 26, 'θi = 1', 12, MOM, 'start', bold=True)
        else:
            S.arrow(W.X(1) + 26, W.Y(0), W.X(1) + 26, yj + 1, MOM, 1.8, L=7, W=3)
            S.text(W.X(1) + 32, (W.Y(0) + yj) / 2 + 4, 'Δ = 1', 12, MOM, 'start', bold=True)
        S.text(x0 + 214, y0 + 146, '　　'.join(t for t, _ in notes), 12.5, col, bold=True)
    S.rect(110, 384, 680, 30, '#f3e5f5', '#ce93d8', 1, rx=8)
    S.text(450, 404, 'K* = Kaa − Kab Kbb⁻¹ Kba：4 − 2·(1/4)·2 = 3；12 − 6·(1/4)·6 = 3。扣掉的那項恆 ≥ 0 → 只會變軟', 12.5, PUR_D, bold=True)
    return S.render()


# ---------------------------------------------------------------- 7-2
def fig_7_2():
    S = SVG(900, 430, '門型剛架側向勁度光譜')
    formula = lambda b: 24 - 72 / (4 + 6 * b)
    bs = [q / 20 for q in range(0, 201)]
    ks = []
    for b in bs:
        k = k_portal(max(b, 1e-9))
        assert abs(k - formula(b)) < 1e-4 * 24, (b, k)
        ks.append(k)
    assert near(k_portal(1.0), 84 / 5, 1e-5)
    S.text(450, 22, '門型剛架側向勁度 k 隨梁柱勁度比 b 的變化（每一點都以直接勁度法實際求解）', 13.5, BLUE_D, bold=True)
    x0, y0, w, h = 80, 360, 470, 300
    X = lambda b: x0 + w * b / 10
    Y = lambda k: y0 - h * k / 26
    S.line(x0, y0, x0 + w + 10, y0, MUT, 1.6); S.line(x0, y0, x0, y0 - h - 6, MUT, 1.6)
    for b in (0, 1, 2, 4, 6, 8, 10):
        S.line(X(b), y0, X(b), y0 + 5, MUT, 1); S.text(X(b), y0 + 19, str(b), 11, DIM)
    for k in (0, 6, 12, 16.8, 24):
        S.line(x0 - 5, Y(k), x0, Y(k), MUT, 1); S.text(x0 - 8, Y(k) + 4, f'{k:g}', 11, DIM, 'end')
        if k:
            S.line(x0, Y(k), x0 + w, Y(k), '#eceff1', 1)
    S.text(x0 + w / 2, y0 + 40, '梁柱勁度比 b = EI(梁) / EI(柱)', 12, MUT)
    S.add(f'<text x="24" y="{y0 - h / 2}" font-size="12" fill="{MUT}" text-anchor="middle" '
          f'transform="rotate(-90 24 {y0 - h / 2})">k ÷ (EI/L³)</text>')
    S.line(x0, Y(24), x0 + w, Y(24), LOAD, 1.8, dash='7 5')
    S.text(x0 + w - 4, Y(24) - 8, '上限 24（梁 EI = ∞，剪力棟架）', 11.5, LOAD, 'end', bold=True)
    S.pl([(X(b), Y(k)) for b, k in zip(bs, ks)], REAC, 3.4)
    S.circ(X(0), Y(6), 5.5, GOOD, '#fff', 1.5)
    S.text(X(0) + 12, Y(6) + 18, 'b = 0：6（每柱 3EI/L³）', 11.5, GOOD, 'start', bold=True)
    S.circ(X(1), Y(16.8), 5.5, MOM, '#fff', 1.5)
    S.line(X(1), Y(16.8), X(1), y0, '#ce93d8', 1.2, dash='4 4')
    S.halo(X(1) + 12, Y(16.8) + 22, 'SA-2025-1：b = 1 → 84/5 = 16.8', 12, MOM, 'start', bold=True)
    S.text(x0 + w / 2 + 30, Y(9), 'k = (24 − 72/(4+6b)) · EI/L³', 12.5, REAC, bold=True)
    # insets
    for q, (b, lab, col) in enumerate(((1e-6, 'b = 0　k = 6', GOOD), (1.0, 'b = 1　k = 16.8', MOM),
                                       (1e6, 'b = ∞　k = 24', LOAD))):
        yy = 60 + q * 122
        S.rect(588, yy - 18, 298, 112, '#fafafa', '#e0e0e0', 1, rx=8)
        S.text(600, yy, lab, 12.5, col, 'start', bold=True)
        F = portal(b, 1.0).solve()
        W = World(640, yy + 82, 66)
        ghost(S, W, F)
        amp = 0.30 / F.d(1)[0]
        for k in range(3):
            shape(S, W, F, k, amp, col, 2.6)
        S.fixed(*W(0, 0), s=0.6); S.fixed(*W(1, 0), s=0.6)
        th = -F.d(1)[2] / F.d(1)[0]
        S.text(760, yy + 30, f'θ = {th:.2f} Δ/L', 12, col, 'start')
        S.text(760, yy + 50, ['柱頂自由轉', '部分受梁束制', '節點不轉'][q], 11.5, MUT, 'start')
        S.text(760, yy + 70, ['＝修正勁度', '＝靜態凝縮', '＝剪力棟架'][q], 11.5, MUT, 'start')
    S.text(450, 420, '兩端點是修正勁度與剪力棟架這兩個特例，中間整條曲線就是靜態凝縮的結果 —— 三招其實是一招', 12, PUR_D, bold=True)
    return S.render()


# ---------------------------------------------------------------- 8-1
def fig_8_1():
    S = SVG(900, 400, '格床：同一轉角對兩根桿是不同變形')
    S.text(450, 22, 'SA-2025-4（U 型格床）：雙箭頭 = 轉角向量（右手定則）；向量沿桿軸 → 扭轉，垂直桿軸 → 彎曲', 13, BLUE_D, bold=True)
    ex, ey = (0.94, 0.34), (0.70, -0.55)
    s, ox, oy = 200, 120, 246

    def P(x, y, z=0):
        return ox + s * (x * ex[0] + y * ey[0]), oy + s * (x * ex[1] + y * ey[1]) - s * z
    a, b, c, d = P(1, 0), P(0, 0), P(0, 1), P(1, 1)
    S.line(*a, *d, GHOST, 1.2, dash='4 4')
    for p1, p2 in ((a, b), (b, c), (c, d)):
        S.line(*p1, *p2, INK, 7)
    # loads on bc
    for q in range(9):
        t = q / 8
        x, y = P(0, t)
        S.arrow(x, y - 48, x, y - 7, LOAD, 1.6, L=7, W=3)
    S.line(*P(0, 0, 48 / s), *P(0, 1, 48 / s), LOAD, 1.6)
    S.text(P(0, .5, 60 / s)[0] - 14, P(0, .5, 60 / s)[1], 'ω', 14, LOAD, bold=True)
    for p, nm, dx, dy in ((a, 'a（固定）', 10, 18), (b, 'b', -14, 6), (c, 'c', -14, -6), (d, 'd（固定）', 12, 4)):
        S.text(p[0] + dx, p[1] + dy, nm, 13, INK, 'start' if dx > 0 else 'end', bold=True)
    for p in (a, d):
        S.rect(p[0] - 6, p[1] - 14, 12, 28, '#cfd8dc', INK, 1.2)

    def vec(p, u, col, lab, L=70, flip=False):
        sx, sy = (u[0], u[1])
        if flip:
            sx, sy = -sx, -sy
        q = (p[0] + L * sx, p[1] + L * sy)
        S.arrow(*p, *q, col, 2.6)
        import math
        ang = math.atan2(sy, sx)
        S.head(q[0] - 9 * sx, q[1] - 9 * sy, ang, col, 10, 4.5)
        S.halo(q[0] + 8 * sx + (6 if sx >= 0 else -6), q[1] + 8 * sy + 4, lab, 13, col,
               'start' if sx >= 0 else 'end', bold=True)
    bo = (b[0], b[1] + 22)                     # drawn just below the bars so they stay visible
    S.line(*b, *bo, MUT, 1, dash='2 2')
    vec(bo, ex, MOM, 'θxb')
    vec(bo, ey, GOOD, 'θyb')
    vec(c, ex, MOM, 'θxc = −θxb', flip=True)
    vec(c, ey, GOOD, 'θyc = θyb')
    S.text(P(0.62, 0)[0] + 10, P(0.62, 0)[1] + 28, 'ab（沿 x）', 12, MUT)
    S.text(P(0, 0.5)[0] + 30, P(0, 0.5)[1] + 22, 'bc（沿 y）', 12, MUT)
    # explanation boxes
    S.rect(560, 46, 326, 150, '#f3e5f5', '#ce93d8', 1, rx=9)
    S.text(574, 70, '節點 b 的 θx（紫）', 13, PUR_D, 'start', bold=True)
    S.text(574, 94, '對 ab（桿軸 = x）：扭轉 GJ/L = 2GI/L', 12, MOM, 'start')
    S.text(574, 116, '對 bc（桿軸 = y）：彎曲 4EI/L', 12, MOM, 'start')
    S.text(574, 138, '　θxc = −θxb → 遠端貢獻 2EI/L·(−1)', 12, MOM, 'start')
    S.text(574, 162, 'ΣMx：(2GI/L + 4EI/L − 2EI/L)θxb', 12, PUR_D, 'start', bold=True)
    S.text(574, 182, '　　= (2GI + 2EI)/L · θxb', 12, PUR_D, 'start', bold=True)
    S.rect(560, 208, 326, 128, '#e8f5e9', '#a5d6a7', 1, rx=9)
    S.text(574, 232, '節點 b 的 θy（綠）', 13, GRN_D, 'start', bold=True)
    S.text(574, 256, '對 ab（桿軸 = x）：彎曲 4EI/L、耦合 6EI/L²', 12, GOOD, 'start')
    S.text(574, 278, '對 bc（桿軸 = y）：扭轉，但 θyc = θyb', 12, GOOD, 'start')
    S.text(574, 300, '　→ 相對扭角 0，bc 不出扭矩', 12, GOOD, 'start')
    S.text(574, 322, '這就是對稱把 6×6 砍到 3×3 的原因', 12, GRN_D, 'start', bold=True)
    S.rect(40, 350, 846, 40, '#fff3e0', '#ffcc80', 1, rx=8)
    S.text(463, 375, '彎曲（EI）與扭轉（GJ）會加在同一格 → 實心圓桿 J = Ix + Iy = 2I，兩項才合得起來（矩形、工型不適用）', 12.5, '#e65100', bold=True)
    return S.render()


# ---------------------------------------------------------------- 10-x
CW = -1.0      # θ clockwise-positive in §10 (matches K13 = −6EI/L²)


def fig_10_1():
    S = SVG(900, 300, 'SA-2025-1 結構與自由度')
    F = portal()
    W = World(150, 262, 176)
    members(S, W, F, w=6)
    S.fixed(*W(0, 0)); S.fixed(*W(1, 0))
    S.arrow(W.X(0) - 60, W.Y(1), W.X(0) - 6, W.Y(1), LOAD, 3)
    S.text(W.X(0) - 66, W.Y(1) + 5, 'P', 15, LOAD, 'end', bold=True)
    for (x, y), t, dx, dy, an in (((0, 0), 'A', -12, -12, 'end'), ((1, 0), 'D', 12, -12, 'start'),
                                  ((0, 1), 'B', -10, 24, 'end'), ((1, 1), 'C', 12, 24, 'start')):
        S.text(W.X(x) + dx, W.Y(y) + dy, t, 14, INK, an, bold=True)
    S.halo(W.X(0.5), W.Y(1) + 22, '梁 BC：EI, L', 12, MUT)
    S.halo(W.X(0) + 12, W.Y(0.5), '柱 EI, L', 12, MUT, 'start')
    S.halo(W.X(1) - 12, W.Y(0.5), '柱 EI, L', 12, MUT, 'end')
    for x, t in ((0, 'θB'), (1, 'θC')):
        S.moment(W.X(x), W.Y(1), 22, ccw=False, c=MOM, a0=150, span=230)
        S.halo(W.X(x) + 2, W.Y(1) - 32, t + '（順時針 +）', 12.5, MOM, 'middle', bold=True)
    S.arrow(W.X(1) + 30, W.Y(1) + 40, W.X(1) + 80, W.Y(1) + 40, MOM, 2.6)
    S.text(W.X(1) + 86, W.Y(1) + 45, 'Δ（向右 +，B、C 共用）', 12.5, MOM, 'start', bold=True)
    S.rect(560, 120, 326, 150, '#e8f5e9', '#a5d6a7', 1, rx=9)
    S.text(723, 144, '自由度盤點（§2）', 13, GRN_D, bold=True)
    for q, t in enumerate(['柱不縮短 → vB = vC = 0', '梁不伸長 → uB = uC ≡ Δ', 'A、D 固定 → 全束制',
                           '剩 3 個：θB、θC、Δ', '正向：θ 順時針、Δ 向右']):
        S.text(578, 170 + q * 21, t, 12, GRN_D, 'start', bold=q >= 3)
    return S.render()


def fig_10_2():
    S = SVG(900, 350, 'SA-2025-1 三場單位位移實驗')
    S.text(450, 22, '三場單位位移實驗（變形依 Hermite 形狀函數計算）：每一場量出 [K] 的一行', 14, BLUE_D, bold=True)
    exps = [('θB = 1（順）', {(1, 2): CW}, GOOD, '#e8f5e9', '#a5d6a7', (8, 2, -6)),
            ('θC = 1（順）', {(2, 2): CW}, REAC, '#e3f2fd', '#90caf9', (2, 8, -6)),
            ('Δ = 1（右）', {(1, 0): 1.0, (2, 0): 1.0}, ORG, '#fff3e0', '#ffcc80', (-6, -6, 24))]
    for q, (t, imp, col, bg, bd, expect) in enumerate(exps):
        x0 = 12 + q * 296
        S.rect(x0, 36, 280, 304, bg, bd, 1, rx=9)
        S.text(x0 + 140, 58, '實驗 ' + str(q + 1) + '：' + t, 13, col, bold=True)
        F = portal()
        impose(F, imp)
        fB, fC = node_force(F, 1), node_force(F, 2)
        got = (CW * fB[2], CW * fC[2], fB[0] + fC[0])        # (θB, θC, Δ) rows, θ cw-positive
        assert all(near(a, b_) for a, b_ in zip(got, expect)), (q, got)
        W = World(x0 + 70, 250, 130)
        ghost(S, W, F)
        amp = 0.22
        for k in range(3):
            shape(S, W, F, k, amp, col, 3)
        S.fixed(*W(0, 0), s=0.8); S.fixed(*W(1, 0), s=0.8)
        names = [f'K₁{q+1}', f'K₂{q+1}', f'K₃{q+1}']
        names = [n.replace('1', '₁').replace('2', '₂').replace('3', '₃') for n in names]
        units = ['EI/L', 'EI/L', 'EI/L²'] if q < 2 else ['EI/L²', 'EI/L²', 'EI/L³']
        for r, (val, nm, un) in enumerate(zip(got, names, units)):
            S.text(x0 + 140, 290 + r * 18, f'{nm} = {frac(val).replace("-", "−")} {un}', 12.5, col, bold=True)
        S.text(x0 + 70 - 10, 246, 'A', 11.5, INK, 'end', bold=True); S.text(x0 + 200 + 10, 246, 'D', 11.5, INK, 'start', bold=True)
        if q == 2:
            S.text(x0 + 140, 82, '梁 BC 平移、沒有弦角 → 不出力', 11.5, ORG)
            S.text(x0 + 140, 98, '兩柱各出 12EI/L³ → 24', 11.5, ORG)
        else:
            S.text(x0 + 140, 82, '近端 4 + 4 = 8，梁遠端被傳 2', 11.5, col)
            S.text(x0 + 140, 98, '柱頂要剪力 6EI/L² 才能不側移', 11.5, col)
    return S.render()


def fig_10_3():
    F = portal(1.0, 1.0).solve()
    Dl = F.d(1)[0]
    assert near(1 / Dl, 84 / 5, 1e-6) and near(F.d(1)[2] * CW / Dl, 0.6, 1e-5)
    fAB = F.end_forces(0)
    Mbase, Mtop = fAB[2], fAB[5]
    assert near(Mbase, 2 / 7, 1e-5) and near(Mtop, 3 / 14, 1e-5) and near(abs(fAB[1]), 0.5, 1e-5)
    S = SVG(900, 350, 'SA-2025-1 變形與彎矩圖')
    S.text(450, 22, 'SA-2025-1 解出來的樣子：θ = 0.6Δ/L、k = 16.8EI/L³，回代得彎矩圖', 14, BLUE_D, bold=True)
    W = World(110, 270, 190)
    ghost(S, W, F)
    amp = 0.25 / Dl
    for k in range(3):
        shape(S, W, F, k, amp, REAC, 3.4)
    S.fixed(*W(0, 0)); S.fixed(*W(1, 0))
    S.arrow(W.X(0) - 50, W.Y(1), W.X(0) - 6, W.Y(1), LOAD, 2.8)
    S.text(W.X(0) - 54, W.Y(1) + 5, 'P', 14, LOAD, 'end', bold=True)
    S.text(W.X(0.5), 298, '變形（放大）：柱呈反曲，兩節點順時針轉', 12.5, REAC, bold=True)
    S.halo(W.X(1) + 60, W.Y(1) - 4, 'Δ = 5PL³/84EI', 12, REAC, 'start', bold=True)
    S.halo(W.X(1) + 60, W.Y(1) + 14, 'θ = 0.6Δ/L（順）', 12, REAC, 'start')
    # BMD
    W2 = World(560, 270, 190)
    members(S, W2, F, c=GHOST, w=2)
    bs = 0.26 / (2 / 7)
    for k in range(3):
        pts, M, L = F.bmd(k, bs)
        S.area([W2(*p) for p in pts], LOAD, 0.16)
        S.pl([W2(*p) for p in pts[1:-1]], LOAD, 2)
    S.fixed(*W2(0, 0), s=0.8); S.fixed(*W2(1, 0), s=0.8)
    for k, xi, txt, dx, dy, an in ((0, 0.0, '2PL/7', -6, 4, 'end'), (2, 0.0, '2PL/7', -6, 4, 'end'),
                                   (1, 0.0, '3PL/14', 8, 18, 'start'), (1, 1.0, '3PL/14', 8, -4, 'start')):
        (px, py), val = F.bmd_at(k, xi, bs)
        X, Y = W2(px, py)
        S.halo(X + dx, Y + dy, txt, 12.5, LOAD, an, bold=True)
    S.text(W2.X(0.5), 318, '節點 B、C：柱頂彎矩 = 梁端彎矩 = 3PL/14（節點平衡）', 11.5, MUT)
    S.text(W2.X(0.5), 298, '彎矩圖（畫在受拉側）', 12.5, LOAD, bold=True)
    S.text(W2.X(0.5), 338, '每柱剪力 = (2/7 + 3/14)P = P/2 ✓（兩柱平分側力）', 12, GRN_D, bold=True)
    return S.render()


# ======================= driver =======================
FIGS = {
    '0-1': fig_0_1, '1-1': fig_1_1, '2-2': fig_2_2, '2-3': fig_2_3, '2-4': fig_2_4, '2-5': fig_2_5,
    '3-1': fig_3_1, '4-1': fig_4_1, '4-2': fig_4_2, '5-1': fig_5_1, '6-1': fig_6_1, '6-2': fig_6_2,
    '7-1': fig_7_1, '7-2': fig_7_2, '8-1': fig_8_1, '10-1': fig_10_1, '10-2': fig_10_2, '10-3': fig_10_3,
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
                     pathlib.Path(__file__).resolve().parent.parent / 'study' / 'lecture-SA-U2-4.html')
    html, n = inject(p.read_text(encoding='utf-8'))
    p.write_text(html, encoding='utf-8')
    print(f'{p}: {n} figures regenerated')

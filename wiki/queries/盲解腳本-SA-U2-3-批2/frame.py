"""平面剛架勁度法（盲解路徑 1）
- 桿件可設端鉸（靜態凝聚），載重：桿上均布（全長或局部）、集中力、節點力
- 回傳桿端力；end moments 以「順時針作用於桿端為正」（傾角變位法慣例）輸出
"""
import numpy as np

class Frame:
    def __init__(self):
        self.N = {}; self.M = []; self.fix = {}; self.P = {}; self.spring = {}; self.disp = {}
    def node(self, n, x, y): self.N[n] = (x, y)
    def support(self, n, ux=1, uy=1, rz=1): self.fix[n] = (ux, uy, rz)
    def settle(self, n, dof, val): self.disp[(n, dof)] = val
    def load(self, n, fx=0, fy=0, mz=0):
        p = self.P.setdefault(n, [0, 0, 0]); p[0] += fx; p[1] += fy; p[2] += mz
    def member(self, name, i, j, EI=1.0, EA=1e8, hinge_i=False, hinge_j=False):
        self.M.append(dict(name=name, i=i, j=j, EI=EI, EA=EA, hi=hinge_i, hj=hinge_j, loads=[]))
    def mload(self, name, kind, **kw):
        """kind='udl' w(global, +y up; give wy) over [a,b] along member length (default full)
           kind='pt' global P (px,py) at distance a from i
           kind='udl_local' wperp local (+ local y)"""
        m = [m for m in self.M if m['name'] == name][0]; m['loads'].append((kind, kw))

    def _geo(self, m):
        (x1, y1), (x2, y2) = self.N[m['i']], self.N[m['j']]
        L = np.hypot(x2 - x1, y2 - y1); c, s = (x2 - x1) / L, (y2 - y1) / L
        return L, c, s

    def _kloc(self, m, L):
        EI, EA = m['EI'], m['EA']
        k = np.zeros((6, 6))
        k[0, 0] = k[3, 3] = EA / L; k[0, 3] = k[3, 0] = -EA / L
        a = np.array([[12, 6 * L, -12, 6 * L], [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                      [-12, -6 * L, 12, -6 * L], [6 * L, 2 * L * L, -6 * L, 4 * L * L]]) * EI / L ** 3
        idx = [1, 2, 4, 5]
        for r in range(4):
            for q in range(4): k[idx[r], idx[q]] = a[r, q]
        return k

    def _fef(self, m, L, c, s):
        """fixed-end forces in local coords (forces exerted BY member ends? -> we use equivalent: reactions of fixed beam)"""
        f = np.zeros(6)
        for kind, kw in m['loads']:
            if kind in ('udl', 'udl_local'):
                if kind == 'udl':
                    wx, wy = kw.get('wx', 0), kw.get('wy', 0)
                    proj = kw.get('proj', False)  # load per horizontal projection
                    wl_ax = wx * c + wy * s; wl_pe = -wx * s + wy * c
                    if proj: wl_ax *= abs(c); wl_pe *= abs(c)
                else:
                    wl_ax, wl_pe = 0, kw['w']
                a, b = kw.get('a', 0), kw.get('b', L)
                # numerical integration of point loads
                n = 400; xs = a + (np.arange(n) + 0.5) * (b - a) / n; dx = (b - a) / n
                for x in xs:
                    f += self._fef_pt(L, wl_ax * dx, wl_pe * dx, x)
            elif kind == 'pt':
                px, py = kw.get('px', 0), kw.get('py', 0)
                f += self._fef_pt(L, px * c + py * s, -px * s + py * c, kw['a'])
            elif kind == 'mom':
                f += self._fef_mom(L, kw['m'], kw['a'])
        return f

    @staticmethod
    def _fef_pt(L, pa, pp, a):
        b = L - a; f = np.zeros(6)
        f[0] = -pa * b / L; f[3] = -pa * a / L
        f[1] = -pp * b * b * (3 * a + b) / L ** 3; f[4] = -pp * a * a * (a + 3 * b) / L ** 3
        f[2] = -pp * a * b * b / L ** 2; f[5] = pp * a * a * b / L ** 2
        return f  # end forces needed to hold (fixed-end reactions on member)

    @staticmethod
    def _fef_mom(L, M0, a):
        b = L - a; f = np.zeros(6)
        f[1] = -6 * M0 * a * b / L ** 3; f[4] = 6 * M0 * a * b / L ** 3
        f[2] = M0 * b * (2 * a - b) / L ** 2; f[5] = M0 * a * (2 * b - a) / L ** 2
        f[2] = -f[2] * -1; f[5] = f[5]
        # ccw applied moment M0: fixed-end moments M_i = M0 b(2a-b)/L^2, M_j = M0 a(2b-a)/L^2 (ccw)
        return f

    def _condense(self, k, f, m):
        rel = [d for d, h in ((2, m['hi']), (5, m['hj'])) if h]
        if not rel: return k, f
        keep = [d for d in range(6) if d not in rel]
        krr = k[np.ix_(rel, rel)]; kkr = k[np.ix_(keep, rel)]
        k2 = k.copy(); f2 = f.copy()
        k2[np.ix_(keep, keep)] = k[np.ix_(keep, keep)] - kkr @ np.linalg.solve(krr, kkr.T)
        f2[keep] = f[keep] - kkr @ np.linalg.solve(krr, f[rel])
        for d in rel:
            k2[d, :] = 0; k2[:, d] = 0; f2[d] = 0
        return k2, f2

    def solve(self):
        names = list(self.N); idx = {n: i for i, n in enumerate(names)}
        nd = 3 * len(names); K = np.zeros((nd, nd)); F = np.zeros(nd)
        for n, p in self.P.items(): F[3 * idx[n]:3 * idx[n] + 3] += p
        self._mem = []
        for m in self.M:
            L, c, s = self._geo(m)
            T = np.zeros((6, 6)); R = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]]); T[:3, :3] = R; T[3:, 3:] = R
            k, f = self._condense(self._kloc(m, L), self._fef(m, L, c, s), m)
            kg = T.T @ k @ T; fg = T.T @ f
            dofs = [3 * idx[m['i']] + d for d in range(3)] + [3 * idx[m['j']] + d for d in range(3)]
            K[np.ix_(dofs, dofs)] += kg; F[dofs] -= fg
            self._mem.append((m, L, T, k, f, dofs))
        fixed = []
        for n, fx in self.fix.items():
            for d in range(3):
                if fx[d]: fixed.append(3 * idx[n] + d)
        # rotational dofs with zero stiffness (node where all members hinged) -> fix to avoid singular
        for i in range(nd):
            if i not in fixed and abs(K[i, i]) < 1e-12: fixed.append(i)
        U = np.zeros(nd)
        for (n, d), v in self.disp.items(): U[3 * idx[n] + d] = v
        free = [i for i in range(nd) if i not in fixed]
        U[free] = np.linalg.solve(K[np.ix_(free, free)], F[free] - K[np.ix_(free, fixed)] @ U[fixed])
        Rxn = K @ U - F
        self.U = {n: U[3 * idx[n]:3 * idx[n] + 3] for n in names}
        self.R = {n: Rxn[3 * idx[n]:3 * idx[n] + 3] for n in names if n in self.fix}
        self.end = {}
        for m, L, T, k, f, dofs in self._mem:
            q = k @ (T @ U[dofs]) + f  # local end forces acting on member
            self.end[m['name']] = dict(Ni=-q[0], Vi=q[1], Mi=q[2], Nj=q[3], Vj=q[4], Mj=q[5], L=L,
                                       # clockwise-positive end moments (slope-deflection convention)
                                       Mi_cw=-q[2], Mj_cw=-q[5])
        return self

    def report(self, digits=4):
        for nm, e in self.end.items():
            print(f"{nm}: M_i(cw)={e['Mi_cw']:.{digits}f}  M_j(cw)={e['Mj_cw']:.{digits}f}  V_i={e['Vi']:.{digits}f} V_j={e['Vj']:.{digits}f}  N(tension+)={e['Nj']:.{digits}f}")
        for n, r in self.R.items():
            print(f"R[{n}] = Fx {r[0]:.{digits}f}, Fy {r[1]:.{digits}f}, Mz(ccw) {r[2]:.{digits}f}")

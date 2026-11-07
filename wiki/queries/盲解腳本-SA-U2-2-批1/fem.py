"""平面剛架／桁架直接勁度法（盲解用）
節點自由度可共用（內鉸＝兩節點共用平移、各自轉角）。
元素：('f', i, j, EA, EI, q_local_y)  q 為局部 y 向均佈（局部 y＝x 軸逆時針 90°）
      ('t', i, j, EA, e0)  e0＝無應力長度差（伸長為正：溫度伸長＋、短了－）
"""
import numpy as np


class Model:
    def __init__(self):
        self.xy = []; self.dof = []; self.el = []; self.n = 0

    def node(self, x, y, share=None):
        if share is None:
            d = [self.n, self.n + 1, self.n + 2]; self.n += 3
        else:  # 共用平移、獨立轉角
            s = self.dof[share]; d = [s[0], s[1], self.n]; self.n += 1
        self.xy.append((x, y)); self.dof.append(d); return len(self.xy) - 1

    def frame(self, i, j, EA, EI, q=0.0):
        self.el.append(('f', i, j, EA, EI, q))

    def truss(self, i, j, EA, e0=0.0):
        self.el.append(('t', i, j, EA, e0))

    def geom(self, i, j):
        (x1, y1), (x2, y2) = self.xy[i], self.xy[j]
        L = np.hypot(x2 - x1, y2 - y1); return L, (x2 - x1) / L, (y2 - y1) / L

    def solve(self, fixed, loads=None, presc=None):
        """fixed: {(node, comp)} comp 0=ux 1=uy 2=rz；presc: {(node,comp): 值}"""
        N = self.n; K = np.zeros((N, N)); F = np.zeros(N); self.fe = []
        used_rot = set()
        for e in self.el:
            L, c, s = self.geom(e[1], e[2])
            T = np.zeros((6, 6)); R = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]]); T[:3, :3] = R; T[3:, 3:] = R
            if e[0] == 'f':
                EA, EI, q = e[3], e[4], e[5]
                k = np.zeros((6, 6))
                a = EA / L; b = 12 * EI / L**3; cc = 6 * EI / L**2; d = 4 * EI / L; f = 2 * EI / L
                k[np.ix_([0, 3], [0, 3])] = [[a, -a], [-a, a]]
                k[np.ix_([1, 2, 4, 5], [1, 2, 4, 5])] = [[b, cc, -b, cc], [cc, d, -cc, f], [-b, -cc, b, -cc], [cc, f, -cc, d]]
                fef = np.array([0, q * L / 2, q * L**2 / 12, 0, q * L / 2, -q * L**2 / 12])  # 等效節點力（局部）
                idx = self.dof[e[1]] + self.dof[e[2]]
                used_rot |= {self.dof[e[1]][2], self.dof[e[2]][2]}
            else:
                EA, e0 = e[3], e[4]
                k = np.zeros((6, 6)); a = EA / L; k[np.ix_([0, 3], [0, 3])] = [[a, -a], [-a, a]]
                # 初始伸長 e0：等效節點力 = EA/L*e0 拉開
                fef = np.array([-a * e0, 0, 0, a * e0, 0, 0])
                idx = self.dof[e[1]] + self.dof[e[2]]
            kg = T.T @ k @ T
            K[np.ix_(idx, idx)] += kg; F[idx] += T.T @ fef
            self.fe.append((k, T, fef, idx, L))
        for (nd, cpt), v in (loads or {}).items():
            F[self.dof[nd][cpt]] += v
        U = np.zeros(N); fix = set()
        for nd, cpt in fixed:
            fix.add(self.dof[nd][cpt])
        for (nd, cpt), v in (presc or {}).items():
            fix.add(self.dof[nd][cpt]); U[self.dof[nd][cpt]] = v
        for dd in self.dof:  # 只接桁架的節點：轉角無勁度，固定
            if dd[2] not in used_rot:
                fix.add(dd[2])
        free = [r for r in range(N) if r not in fix]
        Kff = K[np.ix_(free, free)]
        U[free] = np.linalg.solve(Kff, F[free] - K[np.ix_(free, sorted(fix))] @ U[sorted(fix)])
        self.U = U; self.K = K; self.F = F
        self.R = K @ U - F  # 支承反力（全域）
        return U

    def endforces(self, ei):
        """局部桿端力 [N1,V1,M1,N2,V2,M2]（作用於桿端，局部座標正向）"""
        k, T, fef, idx, L = self.fe[ei]
        return k @ (T @ self.U[idx]) - fef

    def axial(self, ei):
        f = self.endforces(ei); return f[3]  # 拉為正

    def moment_at(self, ei, x):
        """局部 x 處彎矩（下緣受拉為正，局部 y 朝上時）"""
        f = self.endforces(ei); q = self.el[ei][5]
        # 取左段自由體：M(x) = -M1 + V1*x + q x^2/2
        return -f[2] + f[1] * x + q * x**2 / 2

"""通用 2D 剛架有限元（可設極大 EA 模擬「不考慮軸向變形」）。
回傳節點位移、支承反力，以及每根元素的桿端彎矩（順時針為正，與傾角變位法一致）。"""
import numpy as np


def solve(nodes, elems, fixed, loads, EI=1.0, EA=1e10):
    """nodes: [(x,y)]
       elems: [(i,j)]  或 [(i,j,EI)]
       fixed: {(node, dof)}  dof: 0=u,1=v,2=theta
       loads: {(node, dof): value}  全域方向
    """
    n = len(nodes)
    K = np.zeros((3 * n, 3 * n))
    kes = []
    for e in elems:
        i, j = e[0], e[1]
        ei = e[2] if len(e) > 2 else EI
        x1, y1 = nodes[i]; x2, y2 = nodes[j]
        L = np.hypot(x2 - x1, y2 - y1); c, s = (x2 - x1) / L, (y2 - y1) / L
        k = np.zeros((6, 6))
        k[0, 0] = k[3, 3] = EA / L; k[0, 3] = k[3, 0] = -EA / L
        b = ei / L ** 3
        kb = np.array([[12, 6 * L, -12, 6 * L],
                       [6 * L, 4 * L * L, -6 * L, 2 * L * L],
                       [-12, -6 * L, 12, -6 * L],
                       [6 * L, 2 * L * L, -6 * L, 4 * L * L]]) * b
        idx = [1, 2, 4, 5]
        for p in range(4):
            for q in range(4):
                k[idx[p], idx[q]] = kb[p, q]
        T = np.zeros((6, 6)); R = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])
        T[:3, :3] = R; T[3:, 3:] = R
        ke = T.T @ k @ T
        kes.append((i, j, L, T, k, ke))
        d = [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
        for p in range(6):
            for q in range(6):
                K[d[p], d[q]] += ke[p, q]
    F = np.zeros(3 * n)
    for (nd, dof), v in loads.items():
        F[3 * nd + dof] += v
    fx = sorted({3 * nd + dof for nd, dof in fixed})
    fr = [k for k in range(3 * n) if k not in fx]
    u = np.zeros(3 * n)
    u[fr] = np.linalg.solve(K[np.ix_(fr, fr)], F[fr])
    Rg = K @ u - F
    # 桿端彎矩：局部座標，傾角變位法慣例（順時針為正）
    #   FE 的局部彎矩以逆時針為正 ⇒ 取負號
    M = {}
    for (i, j, L, T, k, ke) in kes:
        d = [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
        fl = k @ (T @ u[d])
        M[(i, j)] = (-fl[2], -fl[5])          # (M_ij, M_ji) 順時針為正
    return u, {(nd, dof): Rg[3 * nd + dof] for nd, dof in fixed}, M

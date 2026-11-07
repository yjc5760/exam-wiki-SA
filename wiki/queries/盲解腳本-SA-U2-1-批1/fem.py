"""平面剛架／桁架勁度法（盲解用）。
nodes: {name:(x,y)}；elems: list of dict(n1,n2,EI,EA,truss=False,w=0)  w = 垂直向下均布(全域 y 方向, kN/m, 沿水平投影…此處只用於水平桿)
supports: {name:(ux,uy,rz)} 1=束制
springs: {name:(kx,ky,kr)}
loads: {name:(Fx,Fy,M)}
回傳：位移、桿端力（局部座標：N,V,M at i；N,V,M at j）
"""
import numpy as np


def solve(nodes, elems, supports, loads, springs=None, settle=None):
    names = list(nodes)
    idx = {n: i for i, n in enumerate(names)}
    nd = 3 * len(names)
    K = np.zeros((nd, nd)); F = np.zeros(nd)
    store = []
    for e in elems:
        i, j = idx[e['n1']], idx[e['n2']]
        (x1, y1), (x2, y2) = nodes[e['n1']], nodes[e['n2']]
        L = np.hypot(x2 - x1, y2 - y1); c, s = (x2 - x1) / L, (y2 - y1) / L
        EA = e.get('EA', 1e10); EI = e.get('EI', 1.0)
        if e.get('truss'):
            EI = 0.0
        k = np.zeros((6, 6))
        a = EA / L
        k[0, 0] = k[3, 3] = a; k[0, 3] = k[3, 0] = -a
        if EI:
            b1, b2, b3, b4 = 12 * EI / L**3, 6 * EI / L**2, 4 * EI / L, 2 * EI / L
            k[np.ix_([1, 2, 4, 5], [1, 2, 4, 5])] = [[b1, b2, -b1, b2], [b2, b3, -b2, b4], [-b1, -b2, b1, -b2], [b2, b4, -b2, b3]]
        else:
            # 桁架：轉角自由度給極小勁度避免奇異（只在節點全為桁架時有用）
            k[2, 2] = k[5, 5] = 1e-12
        T = np.zeros((6, 6)); R = np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]])
        T[:3, :3] = R; T[3:, 3:] = R
        # 固端力（局部）：垂直全域向下均布 w（每單位桿長）→ 分解
        fe = np.zeros(6)
        w = e.get('w', 0.0)  # 全域 y 向下、每單位「桿長」
        if w:
            wl = np.array([0, -w])  # global vector per length
            qx = wl[0] * c + wl[1] * s; qy = -wl[0] * s + wl[1] * c
            fe += np.array([qx * L / 2, qy * L / 2, qy * L**2 / 12, qx * L / 2, qy * L / 2, -qy * L**2 / 12])
        dofs = [3 * i, 3 * i + 1, 3 * i + 2, 3 * j, 3 * j + 1, 3 * j + 2]
        K[np.ix_(dofs, dofs)] += T.T @ k @ T
        F[dofs] += T.T @ fe
        store.append((e, dofs, k, T, fe, L))
    for n, (fx, fy, m) in loads.items():
        F[3 * idx[n]:3 * idx[n] + 3] += [fx, fy, m]
    for n, ks in (springs or {}).items():
        for d in range(3):
            K[3 * idx[n] + d, 3 * idx[n] + d] += ks[d]
    fixed = [3 * idx[n] + d for n, r in supports.items() for d in range(3) if r[d]]
    # 純桁架節點的轉角
    U = np.zeros(nd)
    for (n, d), v in (settle or {}).items():
        U[3 * idx[n] + d] = v
    free = [d for d in range(nd) if d not in fixed and not ((settle or {}).get((names[d // 3], d % 3)) is not None)]
    Ff = F[free] - K[np.ix_(free, range(nd))] @ U
    U[free] = np.linalg.solve(K[np.ix_(free, free)], Ff)
    out = []
    for e, dofs, k, T, fe, L in store:
        f = k @ T @ U[dofs] - fe
        out.append((e['n1'] + e['n2'], f, L))
    Rxn = K @ U - F
    return {n: U[3 * idx[n]:3 * idx[n] + 3] for n in names}, out, {n: Rxn[3 * idx[n]:3 * idx[n] + 3] for n in names}

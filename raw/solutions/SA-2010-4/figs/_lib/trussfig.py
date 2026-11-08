"""trussfig — 單一（或多個）自由節點桁架：直接勁度法求解＋桿力圖＋節點位移（exam-wiki-SA，2026-11-08，struct-diagram 階段 E）
桿力：拉＋。製造誤差 misfit[(i,j)] = 桿長多出的量（短了為負）。位移：x 向右、y 向上為正。"""
import math
import numpy as np
from structdraw import Canvas, C
from recipes import truss_forces


def solve(nodes, members, EA, free, loads=None, misfit=None):
    loads = loads or {}; misfit = misfit or {}
    idx = {n: k for k, n in enumerate(free)}; n = 2 * len(free)
    K = np.zeros((n, n)); F = np.zeros(n)
    for nd, (fx, fy) in loads.items():
        F[2 * idx[nd]] += fx; F[2 * idx[nd] + 1] += fy
    geo = {}
    for i, j in members:
        (xi, yi), (xj, yj) = nodes[i], nodes[j]; L = math.hypot(xj - xi, yj - yi); c, s = (xj - xi) / L, (yj - yi) / L
        k = EA / L; e = np.array([-c, -s, c, s]); geo[(i, j)] = (L, e, k)
        dofs = [2 * idx[i], 2 * idx[i] + 1] if i in idx else [None, None]
        dofs += [2 * idx[j], 2 * idx[j] + 1] if j in idx else [None, None]
        T0 = -k * misfit.get((i, j), 0.0)                       # 鎖住時把桿接上所需的軸力（短了 ⇒ 拉）
        for a in range(4):
            if dofs[a] is None: continue
            for b in range(4):
                if dofs[b] is not None: K[dofs[a], dofs[b]] += k * e[a] * e[b]
        for a in range(4):
            if dofs[a] is not None: F[dofs[a]] -= T0 * e[a]       # 等效節點載重 = −(鎖住時桿對節點的力)
    d = np.linalg.solve(K, F) if n else np.zeros(0)
    disp = {nd: (0.0, 0.0) for nd in nodes}
    for nd, k in idx.items(): disp[nd] = (d[2 * k], d[2 * k + 1])
    N = {}
    for (i, j), (L, e, k) in geo.items():
        u = np.array([*disp[i], *disp[j]]); N[(i, j)] = k * (e @ u) - k * misfit.get((i, j), 0.0)
    return disp, N


def figure(nodes, N, supports, loads, disp, path, title, note=None, W=760, H=560, dpx=70, fmt=None,
           dlabel=None, dlabel_off=(0, 0), margin=120, loads_out=(), extra=None, lab_pos=None):
    """lab_pos: {(i, j): (xi, side)} 桿力標籤沿桿位置與側邊（+1 左法向、−1 右法向），預設 (0.5, +1)。"""
    """桿力圖＋各自由節點的變形（灰虛線＝放大的變形位置，藍箭頭＝位移向量）。"""
    members = [(i, j, v) for (i, j), v in N.items()]
    class _Blank:
        def format(self, v): return ""
    cv = truss_forces(nodes, members, supports=supports, loads=loads, title=title, note=note, path=None,
                      W=W, H=H, margin=margin, fmt=_Blank())
    peak = max(abs(v) for v in N.values()) or 1
    for (i, j), v in N.items():                               # 桿力標籤：依線寬加大偏移，避免被粗線壓住
        xi, side = (lab_pos or {}).get((i, j), (0.5, 1))
        p0, p1 = nodes[i], nodes[j]; dx, dy = p1[0] - p0[0], p1[1] - p0[1]; L = math.hypot(dx, dy)
        off = (17 + (3.2 + 4.4 * abs(v) / peak) / 2 + 6) * side
        x = cv.X(p0[0] + dx * xi) - dy / L * off; y = cv.Y(p0[1] + dy * xi) - dx / L * off
        col = C["muted"] if abs(v) < 1e-9 else (C["tension"] if v > 0 else C["compr"])
        cv.math_px(x, y + 5, (fmt or "{:+.2f}").format(v).replace("-", "\u2212"), 14, col, weight="700")
    dmax = max(math.hypot(*v) for v in disp.values()) or 1
    s = dpx / cv.sx / dmax
    moved = {n: (p[0] + disp[n][0] * s, p[1] + disp[n][1] * s) for n, p in nodes.items()}
    for (i, j) in N:
        cv.line(moved[i], moved[j], C["deform"], 1.8, dash="5 4")
    for n, (u, v) in disp.items():
        if math.hypot(u, v) < 1e-12: continue
        cv.arrow(nodes[n], moved[n], C["deform"], 2.6, 10)
        if dlabel:
            x, y = cv.X(moved[n][0]) + dlabel_off[0], cv.Y(moved[n][1]) + dlabel_off[1]
            cv.text_px(x, y, dlabel, 13.5, C["deform"], weight="700")
    for nd, (dx, dy), lab, (lx, ly) in loads_out:          # 外力：自節點向外畫（避免與桿件重疊）
        p = nodes[nd]; q0 = (p[0] + dx * 0.12, p[1] + dy * 0.12); q1 = (p[0] + dx, p[1] + dy)
        cv.arrow(q0, q1, C["load"], 3.4, 12)
        cv.math_px(cv.X(q1[0]) + lx, cv.Y(q1[1]) + ly, lab, 16, C["load"], weight="700")
    if extra: extra(cv)
    cv.text_px(46, 250, "藍虛線＝變形後位置（放大示意）", 13, C["deform"], anchor="start")
    cv.save(path)
    return path

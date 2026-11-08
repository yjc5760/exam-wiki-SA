"""SA-2017-1 勘誤重算（2026-11-07）：兩條路徑
  路徑 1：節點法（sympy 精確解 10 條平衡式）→ 桿力、反力、虛擬桿力、δ_C·EA
  路徑 2：直接勁度法（EA = 1，A、E 鉸支），直接解 C 點水平位移 → 與路徑 1 的 δ_C·EA 比對
最後比對寫進 .md 的每個數值，印出 MISMATCHES。"""
import sympy as sp, numpy as np, sys
N = {'A': (0, 0), 'B': (0, 4), 'C': (0, 8), 'D': (3, 4), 'E': (6, 0)}
M = [('A', 'B'), ('B', 'C'), ('B', 'D'), ('A', 'D'), ('C', 'D'), ('D', 'E')]
L = {m: sp.sqrt((N[m[0]][0]-N[m[1]][0])**2 + (N[m[0]][1]-N[m[1]][1])**2) for m in M}
def joints(loads):
    S = {m: sp.Symbol(m[0]+m[1]) for m in M}; R = sp.symbols('Ax Ay Ex Ey'); eqs = []
    for n, (x, y) in N.items():
        fx, fy = loads.get(n, (0, 0))
        for m in M:
            if n in m:
                o = m[1] if n == m[0] else m[0]; dx, dy = N[o][0]-x, N[o][1]-y
                fx += S[m]*dx/L[m]; fy += S[m]*dy/L[m]
        if n == 'A': fx += R[0]; fy += R[1]
        if n == 'E': fx += R[2]; fy += R[3]
        eqs += [fx, fy]
    sol = sp.solve(eqs, list(S.values()) + list(R)); return {m: sol[S[m]] for m in M}, [sol[r] for r in R]
F, R = joints({'C': (12, 0), 'B': (9, 0)}); f, r = joints({'C': (1, 0)})
dC = sum(F[m]*f[m]*L[m] for m in M)
# 路徑 2：直接勁度法
idx = {n: i for i, n in enumerate(N)}; K = np.zeros((10, 10))
for a, b in M:
    (x1, y1), (x2, y2) = N[a], N[b]; l = float(L[(a, b)]); c, s = (x2-x1)/l, (y2-y1)/l
    k = np.outer([-c, -s, c, s], [-c, -s, c, s]) / l; d = [2*idx[a], 2*idx[a]+1, 2*idx[b], 2*idx[b]+1]
    for i in range(4):
        for j in range(4): K[d[i], d[j]] += k[i, j]
free = [i for i in range(10) if i not in (0, 1, 8, 9)]; P = np.zeros(10); P[2*idx['C']] = 12; P[2*idx['B']] = 9
u = np.zeros(10); u[free] = np.linalg.solve(K[np.ix_(free, free)], P[free])
uC = u[2*idx['C']]
EXPECT = {  # 寫進 .md 的值
 'F_AB': 16, 'F_BC': 16, 'F_BD': -9, 'F_AD': 7.5, 'F_CD': -20, 'F_DE': -27.5,
 'A_x': -4.5, 'A_y': -22, 'E_x': -16.5, 'E_y': 22,
 'f_AB': 4/3, 'f_BC': 4/3, 'f_BD': 0, 'f_AD': 0, 'f_CD': -5/3, 'f_DE': -5/3, 'fE_y': 4/3, 'fE_x': -1,
 'sum_AB': 256/3, 'sum_BC': 256/3, 'sum_CD': 500/3, 'sum_DE': 1375/6, 'dC_EA': 566.5, 'L_AD': 5}
GOT = {'F_'+a+b: F[(a, b)] for a, b in M}; GOT.update(dict(zip(['A_x', 'A_y', 'E_x', 'E_y'], R)))
GOT.update({'f_'+a+b: f[(a, b)] for a, b in M}); GOT['fE_y'] = r[3]; GOT['fE_x'] = r[2]
GOT.update({'sum_'+a+b: F[(a, b)]*f[(a, b)]*L[(a, b)] for a, b in [('A', 'B'), ('B', 'C'), ('C', 'D'), ('D', 'E')]})
GOT['dC_EA'] = dC; GOT['L_AD'] = L[('A', 'D')]
bad = [k for k in EXPECT if abs(float(GOT[k]) - EXPECT[k]) > 1e-9]
print({k: float(v) for k, v in GOT.items()})
print('路徑 2 直接勁度法 u_C·EA =', round(uC, 9), '｜路徑 1 =', float(dC))
if abs(uC - float(dC)) > 1e-9: bad.append('path2')
print('MISMATCHES:', len(bad), bad)

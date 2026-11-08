"""SA-2021-4 勘誤重算（2026-11-07）：路徑 1 剛心法；路徑 2 剛性樓板 3 自由度勁度矩陣直接求解（原點在平面中心）"""
import numpy as np
h = 3.6; EId, EIe = 9720, 48600
kd, ke = 12*EId/h**3, 12*EIe/h**3
cols = {'C1': (-3, -2, kd), 'C2': (3, -2, ke), 'C3': (-3, 2, kd), 'C4': (3, 2, ke)}
# 路徑 1：剛心法
Ky = sum(c[2] for c in cols.values()); xr = sum(c[2]*c[0] for c in cols.values())/Ky; yr = sum(c[2]*c[1] for c in cols.values())/Ky
Fy = 108; Mt = Fy*(0 - xr)
Kt = sum(c[2]*((c[1]-yr)**2 + (c[0]-xr)**2) for c in cols.values())
dy, th = Fy/Ky, Mt/Kt
r1 = {k: (-th*(y-yr), dy + th*(x-xr)) for k, (x, y, kk) in cols.items()}
# 路徑 2：3 自由度 (ux, uy, θ) 於原點
K = np.zeros((3, 3)); P = np.zeros(3)
for k, (x, y, kk) in cols.items():
    tx = np.array([1, 0, -y]); ty = np.array([0, 1, x]); K += kk*(np.outer(tx, tx) + np.outer(ty, ty))
    P += 27*ty
U = np.linalg.solve(K, P)
r2 = {k: (U[0] - U[2]*y, U[1] + U[2]*x) for k, (x, y, kk) in cols.items()}
V = {k: (cols[k][2]*r2[k][0], cols[k][2]*r2[k][1]) for k in cols}
EXP = {'kd': 2500, 'ke': 12500, 'Kt': 270000, 'dy_mm': 3.6, 'th': -0.0008,
       'C3u': 1.6, 'C3v': 7.6, 'C4u': 1.6, 'C4v': 2.8, 'C3Vx': 4, 'C3Vy': 19, 'C4Vx': 20, 'C4Vy': 35}
GOT = {'kd': kd, 'ke': ke, 'Kt': Kt, 'dy_mm': dy*1000, 'th': th,
       'C3u': r2['C3'][0]*1000, 'C3v': r2['C3'][1]*1000, 'C4u': r2['C4'][0]*1000, 'C4v': r2['C4'][1]*1000,
       'C3Vx': V['C3'][0], 'C3Vy': V['C3'][1], 'C4Vx': V['C4'][0], 'C4Vy': V['C4'][1]}
bad = [k for k in EXP if abs(GOT[k]-EXP[k]) > 1e-6]
for k in cols:
    assert max(abs(r1[k][i]-r2[k][i]) for i in (0, 1)) < 1e-12, k     # 兩路徑一致
print({k: round(v, 6) for k, v in GOT.items()}); print('ΣVy =', sum(v[1] for v in V.values()), 'ΣVx =', sum(v[0] for v in V.values()))
print('MISMATCHES:', len(bad), bad)

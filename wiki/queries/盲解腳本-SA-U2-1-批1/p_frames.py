import sys; sys.path.insert(0, '/home/claude/bs')
import numpy as np
from fem import solve

def show(title, out):
    print('==', title)
    for nm, f, L in out:
        # 彎矩（正彎矩＝i→j 方向看右手側…此處以 i→j 走向、左側受壓為正 → 對水平左→右桿即下緣受拉為正）
        print(f'  {nm}: L={L:.4f}  N_i={f[0]:+.4f}  V_i={f[1]:+.4f}  M(i)={-f[2]:+.4f}  M(j)={f[5]:+.4f}  (end-moment ccw on member: Mi={f[2]:+.4f}, Mj={f[5]:+.4f})')

# ---- SA-2005-1 ----
I = 20**4 / 12            # cm^4
EI = 1e6 * I / 1e4        # N·m^2
U, out, R = solve({'B': (0, 0), 'A': (8, 0), 'C': (4, -4)},
                  [dict(n1='B', n2='A', EI=EI, EA=1e8 * EI), dict(n1='C', n2='B', EI=EI, EA=1e8 * EI)],
                  {'A': (1, 1, 1), 'C': (0, 1, 0)}, {'B': (0, -10, 0)})
show('SA-2005-1  (EI=%.4g N·m²)' % EI, out); print('  R_C', R['C'], ' R_A', R['A'])
print('  B 位移', U['B'])

# ---- SA-2008-3 ----
U, out, R = solve({'A': (0, 0), 'B': (6, 0), 'C': (10.5, -6)},
                  [dict(n1='A', n2='B', EI=1, EA=1e8, w=2), dict(n1='B', n2='C', EI=1, EA=1e8)],
                  {'A': (0, 1, 0), 'C': (1, 1, 1)}, {})
show('SA-2008-3', out); print('  R_A', R['A'], ' R_C', R['C'])
# 含軸向變形敏感度（EA/EI = 100 /m², 僅參考）
for r in [1e8, 1e4, 1e3]:
    U2, o2, R2 = solve({'A': (0, 0), 'B': (6, 0), 'C': (10.5, -6)},
                       [dict(n1='A', n2='B', EI=1, EA=r, w=2), dict(n1='B', n2='C', EI=1, EA=r)],
                       {'A': (0, 1, 0), 'C': (1, 1, 1)}, {})
    print('   EA/EI=%g  R_A=%.4f  M_B=%.4f' % (r, R2['A'][1], o2[0][1][5]))

# ---- SA-2013-2 ----
U, out, R = solve({'A': (0, 0), 'B': (0, 10), 'P': (5, 10), 'C': (10, 10)},
                  [dict(n1='A', n2='B', EI=1, EA=1e8), dict(n1='B', n2='P', EI=1, EA=1e8), dict(n1='P', n2='C', EI=1, EA=1e8)],
                  {'A': (1, 1, 1), 'C': (1, 1, 0)}, {'P': (0, -20, 0)})
show('SA-2013-2', out); print('  R_C', R['C'], ' R_A', R['A'], ' θ_C·EI', U['C'][2])

# ---- SA-2014-4 ----
U, out, R = solve({'A': (0, 0), 'B': (6, 0), 'C': (12, 0), 'D': (12, -12)},
                  [dict(n1='A', n2='B', EI=1000, EA=1e11), dict(n1='B', n2='C', EI=1000, EA=1e11), dict(n1='C', n2='D', EI=2000, EA=1e11)],
                  {'A': (1, 1, 1), 'D': (0, 1, 0)}, {'B': (0, -20, 0)})
show('SA-2014-4', out); print('  R_D', R['D'], ' θ_C', U['C'][2], ' C', U['C'], ' D', U['D'])

# ---- SA-2018-3 ----
EI = 1000.0; EAc = 500.0
nodes = {'A': (0, 0), 'B': (5, 0), 'C': (10, 0), 'D': (15, 0), 'E': (0, -5), 'F': (5, -5), 'G': (10, -5)}
els = [dict(n1='A', n2='B', EI=EI, EA=1e8 * EI), dict(n1='B', n2='C', EI=EI, EA=1e8 * EI), dict(n1='C', n2='D', EI=EI, EA=1e8 * EI),
       dict(n1='G', n2='C', EI=EI, EA=1e8 * EI),
       dict(n1='E', n2='A', EA=EAc, truss=True), dict(n1='F', n2='B', EA=EAc, truss=True)]
U, out, R = solve(nodes, els, {'E': (1, 1, 1), 'F': (1, 1, 1), 'G': (1, 1, 1)}, {'D': (0, -100, 0)})
show('SA-2018-3', out)
print('  A', U['A'], ' B', U['B'], ' D', U['D'])

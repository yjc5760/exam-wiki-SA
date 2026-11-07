import numpy as np
from fem import Model
m=Model()
bot={0:'a',6:'m',9:'n',12:'b',18:'c',21:'d',30:'e'}
for x in range(0,31,3): m.node(bot.get(x,f"B{x}"),x,0)
for x in [3,6,9,12,15,18,21,24,27]: m.node('k' if x==6 else f"T{x}",x,4)
B=lambda x: bot.get(x,f"B{x}"); T=lambda x: 'k' if x==6 else f"T{x}"
mem=[]
for x in range(0,30,3): mem.append((B(x),B(x+3)))                 # 下弦 10
for x in [3,6,9,12,15,18]: mem.append((T(x),T(x+3)))              # 上弦 3–21
mem.append((T(24),T(27)))                                         # 上弦 24–27
for x in [3,6,9,12,15,18,21,24,27]: mem.append((T(x),B(x)))       # 豎桿 9
diag=[(B(0),T(3)),(T(3),B(6)),(B(3),T(6)),(T(6),B(9)),(T(9),B(12)),(B(9),T(12)),
      (T(15),B(18)),(B(15),T(18)),(T(18),B(21)),(B(21),T(24)),(T(24),B(27)),(B(24),T(27)),(T(27),B(30))]
mem+=diag
print("桿件數",len(mem),"節點數",len(m.nodes))
for a,b in mem: m.truss(a,b,1.0)
for s in 'abc': m.support(s,0,1)
m.support('e',1,1)
imn=mem.index(('m','n')); ink=mem.index(('k','n'))
print("  x     R_a       R_b       R_c       R_e       N_mn      N_nk")
res=[]
for x in range(0,31,3):
    U,R,f=m.solve([(B(x),0,-1,0)])
    r=(x,R[m.dof('a',1)],R[m.dof('b',1)],R[m.dof('c',1)],R[m.dof('e',1)],f[imn],f[ink]); res.append(r)
    print("%3d "%x+" ".join("%9.5f"%v for v in r[1:]))
# EA 敏感度：檢查是否靜不定（改一根桿 EA）
m2=Model(); m2.nodes=m.nodes; m2.nd=m.nd; m2.fix=m.fix
for i,(a,b) in enumerate(mem): m2.truss(a,b,2.0 if i==3 else 1.0)
U,R,f=m2.solve([(B(9),0,-1,0)]); print("改 EA 後 x=9: R_a",R[m2.dof('a',1)],"N_mn",f[imn])

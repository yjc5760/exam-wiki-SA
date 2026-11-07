import numpy as np
from fem import Model
EI=800.0; EA=1e8*EI
m=Model(); dx=0.1
xs=np.round(np.arange(0,20+1e-9,dx),6); names=[]
key={0:'A',5:'B',10:'C',15:'D',20:'E'}
for i,x in enumerate(xs):
    nm=key.get(round(x,6) if round(x,6)%5 else int(round(x)),f"n{i}") if round(x,6) in (0,5,10,15,20) else f"n{i}"
    m.node(nm,x,0); names.append(nm)
for a,b in zip(names[:-1],names[1:]): m.frame(a,b,EI,EA)
m.node('F',2,-4); m.node('G',18,-4)
# 斜撐分段
def strut(top,bot,p0,p1,k=10):
    prev=bot
    for j in range(1,k):
        t=j/k; nm=f"{bot}{j}"; m.node(nm,p1[0]+(p0[0]-p1[0])*t,p1[1]+(p0[1]-p1[1])*t); m.frame(prev,nm,EI,EA); prev=nm
    m.frame(prev,top,EI,EA)
strut('B','F',(5,0),(2,-4)); strut('D','G',(15,0),(18,-4))
m.support('A',0,1,0); m.support('E',0,1,0); m.support('F',1,1,1); m.support('G',1,1,1)
# Maxwell：C 處向下單位力，梁各點向下位移＝影響線
U,R,f=m.solve([('C',0,-1,0)])
v=np.array([-U[m.dof(n,1)] for n in names])   # 向下為正，單位 m/kN
print("C 自身 δ_CC =",v[names.index('C')]," m/kN  (×EI =",v[names.index('C')]*EI,")")
for x in [0,1,2,2.5,3,4,5,6,7.5,10,12.5,15,17.5,20]:
    i=np.argmin(abs(xs-x)); print(f"x={x:5.1f}  δ_C={v[i]*1000:9.4f} mm/kN   ×EI={v[i]*EI:9.5f}")
# 局部極值
for i in range(1,len(v)-1):
    if (v[i]-v[i-1])*(v[i+1]-v[i])<0: print(f"局部極值 x={xs[i]:.2f}  δ={v[i]*1000:.4f} mm/kN  ×EI={v[i]*EI:.5f}")
# 反向驗證：直接逐點載重
chk=[]
for x in [2.5,7.5]:
    i=np.argmin(abs(xs-x)); U2,_,_=m.solve([(names[i],0,-1,0)]); chk.append(-U2[m.dof('C',1)]*1000)
print("直接載重驗證 x=2.5,7.5:",chk)
# B 處水平位移（是否有側移）
print("u_B,u_D (C 載):",U[m.dof('B',0)],U[m.dof('D',0)])

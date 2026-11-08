"""SA-2006-3 五跨連續梁 彎矩分配法（順時針為正）
路徑1：Hardy Cross 彎矩分配（A、F 端先釋放：修正勁度 3EI/L，外加彎矩半值傳遞）迭代至收斂
路徑2：傾角變位法／直接勁度，6 個轉角 θA..θF 全部聯立 numpy 解"""
import numpy as np
L=[6,8,4,8,6]; w=[0,1.2,0,1.2,0]; MA=+5.0; MF=-5.0   # 外加：A 順時針、F 逆時針
nodes='ABCDEF'
FEM=[[-wi*Li**2/12, wi*Li**2/12] for wi,Li in zip(w,L)]
# ---- 路徑1 ----
# 端跨修正：A 鉸、F 滾，桿端彎矩必等於外加彎矩 → M_AB=+5、M_FE=-5；傳到 B、E 半值
fem=[list(f) for f in FEM]
fem[0]=[MA, FEM[0][1]-0.5*(FEM[0][0]-MA)]   # 釋放 A：A端由FEM調到MA，B端加 -1/2*(FEM_A - MA)
fem[4]=[FEM[4][0]-0.5*(FEM[4][1]-MF), MF]
k=[3/L[0]]+[4/l for l in L[1:4]]+[3/L[4]]
DF={}
for j in range(1,5):
    kl,kr=k[j-1],k[j]; DF[j]=(kl/(kl+kr),kr/(kl+kr))
M=[list(f) for f in fem]
print('DF',{nodes[j]:tuple(round(x,4) for x in v) for j,v in DF.items()})
print('FEM(modified)',[[round(a,4) for a in m] for m in M])
for it in range(200):
    mx=0
    for j in range(1,5):
        unb=M[j-1][1]+M[j][0]; mx=max(mx,abs(unb))
        dl=-unb*DF[j][0]; dr=-unb*DF[j][1]
        M[j-1][1]+=dl; M[j][0]+=dr
        if j-1>0: M[j-1][0]+=0.5*dl      # 傳遞（端跨已修正不傳回 A）
        if j<4:  M[j][1]+=0.5*dr
    if mx<1e-12: break
P1=[(round(a,4),round(b,4)) for a,b in M]
print('路徑1 桿端彎矩 (M_ij, M_ji):'); [print(f'  {nodes[i]}{nodes[i+1]}: {a:8.4f} {b:8.4f}') for i,(a,b) in enumerate(P1)]
# ---- 路徑2 ----
K=np.zeros((6,6)); F=np.zeros(6)
for i,(l,f) in enumerate(zip(L,FEM)):
    kk=np.array([[4,2],[2,4]])/l; K[i:i+2,i:i+2]+=kk; F[i:i+2]-=f
F[0]+=MA; F[5]+=MF      # 節點外加彎矩：Σ M_端 = 外加
th=np.linalg.solve(K,F)
P2=[]
for i,(l,f) in enumerate(zip(L,FEM)):
    a,b=th[i],th[i+1]; P2.append((f[0]+(4*a+2*b)/l, f[1]+(2*a+4*b)/l))
print('路徑2 θ*EI:',np.round(th,4))
for i,(a,b) in enumerate(P2): print(f'  {nodes[i]}{nodes[i+1]}: {a:8.4f} {b:8.4f}')
print('max diff',max(abs(np.array(P2)-np.array(M)).ravel()))
# 梁彎矩（正彎矩=下側受拉）
for i,(a,b) in enumerate(P2):
    l=L[i]; ws=w[i]
    # 左端桿端彎矩順時針作用於桿 = 正彎矩（下拉）；右端順時針 = 負彎矩（上拉）
    ML=a; MR=-b
    xs=np.linspace(0,l,8001); Mx=ML+(MR-ML)*xs/l+ws*xs*(l-xs)/2
    j=np.argmax(Mx); zero=xs[np.where(np.diff(np.sign(Mx)))[0]]
    print(f'{nodes[i]}{nodes[i+1]}: M_left={ML:7.3f} M_right={MR:7.3f} Mmax={Mx[j]:.3f}@x={xs[j]:.3f} zeros={np.round(zero,3)} V_left={(MR-ML)/l+ws*l/2:.4f} V_right={(MR-ML)/l-ws*l/2:.4f}')

R=[0]*6
for i,(a,b) in enumerate(P2):
    l=L[i]; ws=w[i]; ML=a; MR=-b; Vl=(MR-ML)/l+ws*l/2; R[i]+=Vl; R[i+1]+=ws*l-Vl
print('支承反力(向上+):',dict(zip(nodes,np.round(R,4))),'ΣR=',round(sum(R),4))

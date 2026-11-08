"""SA-2018-1 剪力牆–構架互制：示意用數值模型（題目不需精確分析，僅用來確認分布形狀）
牆：8 層懸臂撓曲梁（側向 8 自由度凝聚勁度）；構架：剪力型樓層彈簧 k；連桿軸向剛性→同樓層同位移。
「樓層水平勁度 5 倍」三種校準：(i) 12EI/h^3=5k (ii) 3EI/h^3=5k (iii) 均佈樓層力下牆頂位移=構架頂位移/5
路徑2：連續化（Khan–Sbarounis/Heidebrecht–Smith 微分方程 EI y'''' - GA y'' = w）有限差分驗證形狀"""
import numpy as np
n=8; h=1.0; F=1.0
def Kwall(EI):
    z=np.arange(1,n+1)*h; f=np.zeros((n,n))
    for i in range(n):
        for j in range(n):
            a,b=min(z[i],z[j]),max(z[i],z[j]); f[i,j]=a*a*(3*b-a)/(6*EI)
    return np.linalg.inv(f)
def Kframe(k):
    K=np.zeros((n,n))
    for s in range(n):  # story s between floor s-1 and s
        K[s,s]+=k
        if s>0: K[s-1,s-1]+=k; K[s,s-1]-=k; K[s-1,s]-=k
    return K
k=1.0; P=np.full(n,F); Kf=Kframe(k)
uf=np.linalg.solve(Kf,P)[-1]
cases={'(i) 12EI/h3=5k':5*k*h**3/12,'(ii) 3EI/h3=5k':5*k*h**3/3}
# (iii) wall top disp under P = uf/5
EI1=1.0; uw1=np.linalg.solve(Kwall(EI1),P)[-1]; cases['(iii) 頂位移比 1/5']=EI1*uw1/(uf/5)
for name,EI in cases.items():
    Kw=Kwall(EI); u=np.linalg.solve(Kw+Kf,P); ff=Kf@u; fw=Kw@u
    print(f'\n{name}  EI={EI:.3f}  （樓層 1→8，F=1）')
    print(' frame:',np.round(ff,2)); print(' wall :',np.round(fw,2))
    print(' frame story shear:',np.round(np.cumsum(ff[::-1])[::-1],2))
    print(' wall  story shear:',np.round(np.cumsum(fw[::-1])[::-1],2),' base: wall %.0f%% frame %.0f%%'%(100*fw.sum()/8,100*ff.sum()/8))

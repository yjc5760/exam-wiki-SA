"""SA-2024-2 盲解：桁架 F 沉陷 12 mm、CD 製造誤差 δ（+=過長）、DE 溫差 ΔT（+=升溫）
已知 C、E 向下 4.8、6.4 mm，求 δ、ΔT。（無外力 → 靜定桁架無內力，E、A 不入式）
路徑1：單位虛載重法 Δ = Σ n·e − Σ R̄·Δ_support（節點法用 numpy 解平衡）
路徑2：運動學相容 A·d = e（桿伸長 = 節點位移投影），直接解節點位移"""
import numpy as np
alpha=1.5e-5
X={c:4.0*i for i,c in enumerate('ABCDEFG')}; X.update({c:4.0*i for i,c in enumerate('HIJKLMN')})
Y={c:0.0 for c in 'ABCDEFG'}; Y.update({c:3.0 for c in 'HIJKLMN'})
names=list('ABCDEFGHIJKLMN'); idx={n:i for i,n in enumerate(names)}
mem=[a+b for a,b in zip('ABCDEF','BCDEFG')]+[a+b for a,b in zip('HIJKLM','IJKLMN')] \
   +['HA','IB','JC','KD','LE','MF','NG']+['HB','BJ','JD','DL','LF','FN']
assert len(mem)==25
def dc(m):
    a,b=m;dx=X[b]-X[a];dy=Y[b]-Y[a];L=np.hypot(dx,dy);return a,b,dx/L,dy/L,L
# 相容矩陣 Acomp (25×28)：e_m = (u_b-u_a)·n
A=np.zeros((25,28))
for i,m in enumerate(mem):
    a,b,c,s,L=dc(m)
    A[i,2*idx[a]]-=c;A[i,2*idx[a]+1]-=s;A[i,2*idx[b]]+=c;A[i,2*idx[b]+1]+=s
sup=[2*idx['B']+1,2*idx['F'],2*idx['F']+1]   # B 滾(垂直)、F 鉸
# ---------- 路徑1：虛功 ----------
# 平衡 A^T N + R = P  → 未知 [N(25), R(3)]
Eq=np.hstack([A.T,np.zeros((28,3))])
for j,d in enumerate(sup): Eq[d,25+j]=1.0
def unit(node):   # 單位向下載重
    P=np.zeros(28);P[2*idx[node]+1]=-1.0
    sol=np.linalg.solve(Eq,P);return sol[:25],sol[25:]
L={m:dc(m)[4] for m in mem}
res={}
for node in 'CE':
    n,R=unit(node); nCD=n[mem.index('CD')]; nDE=n[mem.index('DE')]
    # 解出的 R 為「節點平衡式中移到左邊的反力」= −(實際反力)；轉成實際反力（向上為正）
    RF=-R[2]; RB=-R[0]
    settle=-RF*(-12.0)      # −R̄Δ, Δ_F=−12 mm（向上為正）；結果 = 沿單位載重方向（向下）位移
    res[node]=(nCD,nDE,settle)
    print(f"路徑1 單位載重@{node}: n_CD={nCD:+.4f}, n_DE={nDE:+.4f}, R̄_F={RF:+.4f}, R̄_B={RB:+.4f}, 沉陷項={settle:+.3f} mm")
# 向下位移 = n_CD·δ + n_DE·(α ΔT L_DE·1000) + 沉陷項
M=np.array([[res[k][0],res[k][1]*alpha*4.0*1000] for k in 'CE'])
rhs=np.array([4.8-res['C'][2],6.4-res['E'][2]])
d1,T1=np.linalg.solve(M,rhs); print(f"路徑1: δ = {d1:+.4f} mm, ΔT = {T1:+.3f} ℃")
# ---------- 路徑2：相容直接解 ----------
def disp(delta,dT):
    e=np.zeros(25);e[mem.index('CD')]=delta;e[mem.index('DE')]=alpha*dT*4.0*1000
    free=[i for i in range(28) if i not in sup]; u=np.zeros(28); u[2*idx['F']+1]=-12.0
    u[free]=np.linalg.solve(A[:,free],e-A[:,sup]@u[sup]);return u
base=disp(0,0); gD=disp(1,0)-base; gT=disp(0,1)-base
vC=lambda u:-u[2*idx['C']+1]; vE=lambda u:-u[2*idx['E']+1]
M2=np.array([[vC(gD),vC(gT)],[vE(gD),vE(gT)]]); r2=np.array([4.8-vC(base),6.4-vE(base)])
d2,T2=np.linalg.solve(M2,r2)
print(f"路徑2: 只沉陷 vC={vC(base):.3f}, vE={vE(base):.3f} mm（向下）")
print(f"路徑2: δ = {d2:+.4f} mm, ΔT = {T2:+.3f} ℃")
u=disp(d2,T2); print("驗算 vC=%.4f vE=%.4f mm 向下"%(vC(u),vE(u)))
print("DE 熱伸長 = %.4f mm"%(alpha*T2*4000))

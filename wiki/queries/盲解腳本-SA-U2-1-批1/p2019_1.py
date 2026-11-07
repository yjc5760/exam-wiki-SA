import numpy as np
exec(open('p_truss.py').read().split("print('== SA-2005-4')")[0])
nodes={'D':(0,9),'B':(12,9),'C':(0,0),'A':(12,0)}
mem=[('D','B'),('C','A'),('D','C'),('B','A'),('D','A'),('C','B')]
kind=['水平','水平','垂直','垂直','對角','對角']
Tcap=1250; Ccap={'水平':225,'垂直':400,'對角':144}
sup={'C':(1,1),'A':(0,1)}
EA=1.0
state=['e']*6   # e 彈性, t 拉降伏(維持1250), c 壓挫(0)
Nf=np.zeros(6); P=0.; UB=0.
hist=[(0,0,list(Nf))]
for step in range(8):
    act=[s=='e' for s in state]
    # 已降伏拉桿以等值節點力作用（固定 1250）；壓挫桿 0
    # 增量：單位 P 增量下的彈性增量內力
    try:
        U,dN,K,free,info,ix=truss(nodes,mem,sup,{'B':(1,0)},EA,active=act)
        if np.linalg.cond(K[np.ix_(free,free)])>1e12: raise np.linalg.LinAlgError
    except np.linalg.LinAlgError:
        print('機構形成（無剩餘勁度），P_u =',round(P,3)); break
    dUB=U[2*ix['B']]
    # 找下一事件
    best=None
    for k in range(6):
        if not act[k] or abs(dN[k])<1e-12: continue
        lim = Tcap if dN[k]>0 else -Ccap[kind[k]]
        dp=(lim-Nf[k])/dN[k]
        if dp>=-1e-9 and (best is None or dp<best[0]): best=(dp,k)
    dp,k=best
    P+=dp; Nf=Nf+dp*np.array(dN); UB+=dp*dUB
    a,b=mem[k]
    print(f'事件{step+1}: P={P:.3f}  U_B·EA={UB:.2f}  {a}{b}({kind[k]}) 達 {"拉 1250" if dN[k]>0 else "壓 %d"%Ccap[kind[k]]}  內力=',np.round(Nf,2))
    if dN[k]>0: state[k]='t'
    else:
        state[k]='c'
        # 壓桿內力歸零：檢查剩餘結構在同一 P 下是否可平衡（重解 P 全量，含已降伏拉桿定值）
        act2=[s=='e' for s in state]
        loads={'B':(P,0)}
        # 拉降伏桿定值力作為節點力
        for j,s in enumerate(state):
            if s=='t':
                v,d,L,_=info[j]
                pass
        try:
            # 以全量重解：彈性桿 + 定值拉桿
            nm=list(nodes); ixx={n:i for i,n in enumerate(nm)}
            Fx={n:[0.,0.] for n in nodes}; Fx['B'][0]+=P
            for j,s in enumerate(state):
                if s=='t':
                    (x1,y1),(x2,y2)=nodes[mem[j][0]],nodes[mem[j][1]];L=np.hypot(x2-x1,y2-y1);c,s_=(x2-x1)/L,(y2-y1)/L
                    Fx[mem[j][0]][0]+=Tcap*c;Fx[mem[j][0]][1]+=Tcap*s_;Fx[mem[j][1]][0]-=Tcap*c;Fx[mem[j][1]][1]-=Tcap*s_
            U2,N2,K2,free2,_,_=truss(nodes,mem,sup,{n:tuple(v) for n,v in Fx.items()},EA,active=act2)
            if np.linalg.cond(K2[np.ix_(free2,free2)])>1e12: raise np.linalg.LinAlgError
            N2=[Tcap if state[j]=='t' else (0 if state[j]=='c' else N2[j]) for j in range(6)]
            print('   壓桿退出後同一 P 重分配：',np.round(N2,2),' U_B·EA=',round(U2[2*ixx['B']],2))
            Nf=np.array(N2); UB=U2[2*ixx['B']]
            viol=[j for j in range(6) if state[j]=='e' and (N2[j]>Tcap+1e-6 or N2[j]<-Ccap[kind[j]]-1e-6)]
            if viol: print('   重分配後又超限：',[mem[j] for j in viol])
        except np.linalg.LinAlgError:
            print('   壓桿退出後已成機構 → P_u =',round(P,3)); break

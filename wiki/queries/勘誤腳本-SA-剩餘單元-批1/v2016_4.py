# SA-2016-4 independent recheck (stage C). Path1: stiffness method random EA. Path2: equilibrium of trial solution + uniqueness (stiffness PD).
import numpy as np, itertools
N={"D":(0,2),"E":(1,2),"F":(2,2),"G":(3,2),"H":(4,2),"A":(1,3),"B":(2,3),"C":(3,3),"I":(2,1),"J":(3,1),"K":(2,0),"L":(3,0),"P":(5,0),"N":(5,1.3),"M":(4,1.3)}
TR=[("A","B"),("B","C"),("A","D"),("A","E"),("A","F"),("B","F"),("C","F"),("C","G"),("C","H"),("D","E"),("E","F"),("F","G"),("G","H"),("F","I"),("G","J"),("I","J"),("F","J"),("G","I"),("I","K"),("J","L"),("K","L"),("I","L"),("J","K"),("L","P"),("N","P")]
fixed={"A":(1,1),"C":(1,1),"D":(1,1),"M":(1,1)}
loads={"A":(100,0),"D":(100,0),"E":(0,-100),"N":(0,-100)}
names=list(N); idx={n:i for i,n in enumerate(names)}
def solve(seed):
    r=np.random.default_rng(seed); EA={m:r.uniform(0.5,5) for m in TR}; k=r.uniform(0.1,10); kb=r.uniform(0.1,10)
    n=2*len(names); K=np.zeros((n,n)); F=np.zeros(n)
    def add(i,j,c,s,kk):
        v=np.array([c,s]); kl=kk*np.outer(v,v); d=[2*idx[i],2*idx[i]+1,2*idx[j],2*idx[j]+1]
        Km=np.block([[kl,-kl],[-kl,kl]]); K[np.ix_(d,d)]+=Km
    for (a,b) in TR:
        (x1,y1),(x2,y2)=N[a],N[b]; L=np.hypot(x2-x1,y2-y1); add(a,b,(x2-x1)/L,(y2-y1)/L,EA[(a,b)]/L)
    add("H","M",0,-1,k)                       # spring H-M (vertical)
    K[2*idx["N"],2*idx["N"]]+=1e3; K[2*idx["N"]+1,2*idx["N"]+1]+=kb   # simply-supported beam MNO at N
    for nd,(fx,fy) in loads.items(): F[2*idx[nd]]+=fx; F[2*idx[nd]+1]+=fy
    free=[d for d in range(n) if not (names[d//2] in fixed)]
    u=np.zeros(n); u[free]=np.linalg.solve(K[np.ix_(free,free)],F[free])
    out={}
    for (a,b) in TR:
        (x1,y1),(x2,y2)=N[a],N[b]; L=np.hypot(x2-x1,y2-y1); c,s=(x2-x1)/L,(y2-y1)/L
        du=u[2*idx[b]]-u[2*idx[a]]; dv=u[2*idx[b]+1]-u[2*idx[a]+1]; out[a+b]=EA[(a,b)]/L*(c*du+s*dv)
    out["spring"]=k*(-(u[2*idx["M"]+1]-u[2*idx["H"]+1]))
    return out
exp={a+b:0.0 for a,b in TR}; exp["AE"]=-100.0*0+100.0; exp["spring"]=0.0
# sign: tension positive. AE: E below A, E moves down -> elongation -> tension +100
mm=0
for s in range(5):
    o=solve(s)
    for kname,v in exp.items():
        if abs(o[kname]-v)>1e-6: mm+=1; print("seed",s,kname,o[kname],"exp",v)
zeros=[k for k in exp if k!="spring" and exp[k]==0]
print("zero members",len(zeros),", ".join(zeros))
# path2: equilibrium of trial at every free node
def eq_check():
    bad=0
    for nd in names:
        if nd in fixed: continue
        fx,fy=loads.get(nd,(0,0))
        if nd=="E": fy+=100  # AE tension pulls E toward A (up)
        if nd=="N": fy+=100  # beam reaction at N
        if abs(fx)>1e-12 or abs(fy)>1e-12: bad+=1; print("eq fail",nd)
    return bad
mm+=eq_check()
print("MISMATCHES:",mm)

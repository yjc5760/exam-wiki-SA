"""SA-2025-4 格子梁：考卷座標 d 原點、a(L,0)、b(L,L)、c(0,L)；z 向上；ω 沿 -z 作用於 bc。J=2I（實心圓）"""
import sympy as sp
g=sp.Symbol('g',positive=True)  # g = GJ/EI = 2G/E（實心圓 J=2I）；以 EI=1、L=1、ω=1 無因次化
E=I=L=w=A=sp.Integer(1); G=g/2; J=2*I
def k3(L):
    k=sp.zeros(12,12)
    def s(i,j,v): k[i,j]=v; k[j,i]=v
    s(0,0,E*A/L);s(6,6,E*A/L);s(0,6,-E*A/L)
    s(3,3,G*J/L);s(9,9,G*J/L);s(3,9,-G*J/L)
    a,b,c,d=12*E*I/L**3,6*E*I/L**2,4*E*I/L,2*E*I/L
    s(1,1,a);s(7,7,a);s(1,7,-a);s(1,5,b);s(1,11,b);s(7,5,-b);s(7,11,-b);s(5,5,c);s(11,11,c);s(5,11,d)
    s(2,2,a);s(8,8,a);s(2,8,-a);s(2,4,-b);s(2,10,-b);s(8,4,b);s(8,10,b);s(4,4,c);s(10,10,c);s(4,10,d)
    return k
def lam(p1,p2):
    ex=sp.Matrix(p2)-sp.Matrix(p1); Lm=sp.sqrt(ex.dot(ex)); ex=ex/Lm; ez=sp.Matrix([0,0,1]); ey=ez.cross(ex)
    r=sp.Matrix([ex.T,ey.T,ez.T]); T=sp.zeros(12,12)
    for i in range(4): T[3*i:3*i+3,3*i:3*i+3]=r
    return Lm,T
P={'a':(L,0,0),'b':(L,L,0),'c':(0,L,0),'d':(0,0,0)}
wb,txb,tyb,wc,txc,tyc=sp.symbols('w_b thx_b thy_b w_c thx_c thy_c'); q=[wb,txb,tyb,wc,txc,tyc]
D={'a':[0]*6,'d':[0]*6,'b':[0,0,wb,txb,tyb,0],'c':[0,0,wc,txc,tyc,0]}
mems=[('a','b',0),('b','c',w),('c','d',0)]
PE=0; store=[]
for n1,n2,qq in mems:
    Lm,T=lam(P[n1],P[n2]); dg=sp.Matrix(D[n1]+D[n2]); dl=T*dg; k=k3(Lm)
    # 等效：外力功 = -ω ∫ w dx；局部 slope s=dw/dx=-θy
    work=-qq*(Lm/2*dl[2]+Lm**2/12*(-dl[4])+Lm/2*dl[8]-Lm**2/12*(-dl[10]))
    PE+= (dl.T*k*dl)[0]/2 - work; store.append((n1,n2,T,k,dg,qq,Lm))
eqs=[sp.expand(sp.diff(PE,x)) for x in q]
K=sp.Matrix([[sp.diff(e,y) for y in q] for e in eqs]); R=-sp.Matrix([e.subs({x:0 for x in q}) for e in eqs])
sol=[sp.factor(x) for x in K.LUsolve(R)]; S=dict(zip(q,sol))
print('K='); sp.pprint(K); print('R=',R.T)
for x in q: print(' ',x,'=',sp.factor(sp.simplify(S[x])))
# 反力：支承端的全域桿端力（含固定端力，ab、cd 無載重）
for n1,n2,T,k,dg,qq,Lm in [store[0],store[2]]:
    fg=(T.T*k*T*dg.subs(S)).applyfunc(sp.factor)
    end= slice(0,6) if n1 in 'ad' else slice(6,12)
    sup= n1 if n1 in 'ad' else n2
    r=fg[end,:]; print(f' 支承 {sup}: Fz={sp.factor(r[2])}, Mx={sp.factor(r[3])}, My={sp.factor(r[4])}')
print(' 檢核 ΣFz 應 = ωL')

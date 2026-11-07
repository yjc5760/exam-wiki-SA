"""SA-2009-1 獨立重算（柔度法分數精確＋直接勁度法）與 .md 數值比對。"""
import re, sys
from fractions import Fraction as Fr
import numpy as np
md = open(sys.argv[1], encoding="utf-8").read()
N = {"a": (0, 0), "e": (4, 0), "d": (8, 0), "b": (4, 3), "c": (8, 3)}            # 題目正本 #4
M = [("a","b"),("b","c"),("b","e"),("e","c"),("c","d"),("a","e"),("e","d")]         # 題目正本 #7
AE = 10**4; DA = Fr(-1, 10)
# ── 路徑 1：柔度法（贅力 X1 = d 水平反力，向左為正）以分數精確解平衡 ──
import sympy as sp
names = [f"{i}{j}" for i, j in M]; uu = sp.symbols(" ".join("u_"+n for n in names))
Ray, Rcx, Rcy = sp.symbols("Ray Rcx Rcy")
eqs = []
for n,(x,y) in N.items():
    fx = fy = 0
    for (i,j),u in zip(M,uu):
        if n in (i,j):
            o = j if n == i else i; dx, dy = N[o][0]-x, N[o][1]-y; L = sp.sqrt(dx*dx+dy*dy)
            fx += u*dx/L; fy += u*dy/L
    if n == "a": fy += Ray
    if n == "c": fx += Rcx; fy += Rcy
    if n == "d": fx += -1                                                          # 單位力向左
    eqs += [fx, fy]
sol = sp.solve(eqs, list(uu)+[Ray,Rcx,Rcy], dict=True)[0]
u = {n: sp.nsimplify(sol[s]) for n,s in zip(names,uu)}
Ls = {f"{i}{j}": sp.sqrt((N[j][0]-N[i][0])**2+(N[j][1]-N[i][1])**2) for i,j in M}
S = sum(u[n]**2*Ls[n] for n in names)
D10 = -sol[Ray]*sp.Rational(-1,10)                                                  # 1·Δ10 + R_ay·Δa = 0
X1 = -D10/(S/AE)
calc = {"u_ab":u["ab"],"u_ae":u["ae"],"u_ed":u["ed"],"u_cd":u["cd"],"u_ec":u["ec"],"u_be":u["be"],"u_bc":u["bc"],
        "Rau":sol[Ray],"Rcxu":sol[Rcx],"Rcyu":sol[Rcy],"SumU2L":S,"D10":D10,"X1":X1,
        "Ray":sol[Ray]*X1,"Rcx":sol[Rcx]*X1,"Rcy":sol[Rcy]*X1,"Rdx":X1,
        "N_ab":u["ab"]*X1,"N_ec":u["ec"]*X1,"N_bc":u["bc"]*X1,"N_ae":u["ae"]*X1,"N_be":u["be"]*X1,"N_ed":u["ed"]*X1,"N_cd":u["cd"]*X1}
# ── 路徑 2：直接勁度法（a 指定下沉 0.1 m）──
idx = {n:k for k,n in enumerate(N)}; K = np.zeros((10,10))
for i,j in M:
    (x1,y1),(x2,y2) = N[i],N[j]; L = np.hypot(x2-x1,y2-y1); c,s = (x2-x1)/L,(y2-y1)/L
    k = AE/L*np.outer([-c,-s,c,s],[-c,-s,c,s]); ids = [2*idx[i],2*idx[i]+1,2*idx[j],2*idx[j]+1]
    K[np.ix_(ids,ids)] += k
U = np.zeros(10); fixed = {2*idx["a"]+1:-0.1, 2*idx["c"]:0, 2*idx["c"]+1:0, 2*idx["d"]:0}
for k,v in fixed.items(): U[k]=v
fr = [k for k in range(10) if k not in fixed]; fx = list(fixed)
U[fr] = np.linalg.solve(K[np.ix_(fr,fr)], -K[np.ix_(fr,fx)]@U[fx]); Rr = K@U
stiff = {"Ray":Rr[2*idx["a"]+1],"Rcx":Rr[2*idx["c"]],"Rcy":Rr[2*idx["c"]+1],"Rdx":-Rr[2*idx["d"]]}  # Rdx 向左為正
for i,j in M:
    (x1,y1),(x2,y2) = N[i],N[j]; L = np.hypot(x2-x1,y2-y1); c,s = (x2-x1)/L,(y2-y1)/L
    du = U[[2*idx[j],2*idx[j]+1]]-U[[2*idx[i],2*idx[i]+1]]; stiff["N_"+i+j] = AE/L*(c*du[0]+s*du[1])
# ── .md 中寫的值 ──
mdv = {"u_ab":5/8,"u_ae":-1/2,"u_ed":-1,"u_cd":0,"u_ec":5/8,"u_be":-3/8,"u_bc":1/2,"Rau":-3/8,"Rcxu":1,"Rcyu":3/8,
       "SumU2L":661/64,"D10":-0.0375,"X1":24000/661,"Ray":-9000/661,"Rcx":24000/661,"Rcy":9000/661,"Rdx":24000/661,
       "N_ab":15000/661,"N_ec":15000/661,"N_bc":12000/661,"N_ae":-18.15,"N_be":-9000/661,"N_ed":-36.31,"N_cd":0}
# 確認這些值確實出現在 .md（防止腳本自說自話）
must = [r"u_{ec} = \frac{5}{8}", r"u_{be} = -\frac{3}{8}", r"u_{bc} = \frac{1}{2}", r"u_{ed} = -1", r"u_{cd} = 0",
        r"\frac{661}{64}", r"\frac{24000}{661}", r"\frac{9000}{661}", r"N_{cd} = 0", "+22.69", "+18.15", "-18.15", "-13.62", "-36.31", "13.62", "36.31"]
miss = [m for m in must if m not in md]
mism = []
for k,v in mdv.items():
    c = float(calc[k]); tol = 0.006 if k in ("N_ae","N_ed") else 1e-9
    if abs(c - v) > tol: mism.append((k, v, c, "flex"))
    if k in stiff and abs(stiff[k] - c) > 1e-6: mism.append((k, c, stiff[k], "stiff"))
for k,v in calc.items(): print(f"{k:7s} {str(v):>14s} = {float(v):+.5f}" + (f"   stiff {stiff[k]:+.5f}" if k in stiff else ""))
print("缺字串：", miss); print("MISMATCHES:", len(mism) + len(miss), mism)

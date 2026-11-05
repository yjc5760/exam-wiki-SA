#!/usr/bin/env python3
"""SA-2004-1：剪力圖／彎矩圖（struct-diagram，2026-11-05）
反力取自 SA-2004-1.md §4 Step 1（C_y = 9 t↑、梁上 B_y = 3 t↑、B_x = 0；A_x = 4 t←、A_y = 3 t↑、M_A = 8 t·m 逆時針）；
各桿內力由自由體沿桿積分載重算出，圖形不寫死。
用法：python3 gen_SA-2004-1_vm.py [輸出目錄]；之後以 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C, compose
from nvm_common import frame_panel
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2004-1"

# ── 幾何（題目正本 #4–#7）──
A, B, Cn, Dn = (0, 0), (0, 4), (4, 4), (6, 4)     # Dn：梁右端（考卷未標名，本解記為 D）
w, P = 2.0, 4.0                                   # 梁全長 2 t/m ↓；柱中點 4 t →
# ── 反力（§4 Step 1）──
Cy, By, Bx = 9.0, 3.0, 0.0
Ax, Ay, MA = -4.0, 3.0, 8.0

def col(s):     # A→B，自由體＝A 側；M 右手側（+x，內側）受拉＋
    Me = MA + s*Ax + (-(2-s)*P if s > 2 else 0.0)  # 對截面 (0,s) 之逆時針力矩：M_A、A_x、4t
    Fx = Ax + (P if s > 2 else 0.0)
    return (-Ay, -Fx, -Me)     # 柱剪力正負沿用 §4 Step 3（柱 A–中點 V = +4 t）
def beam(x):    # B→D，自由體＝梁左段；M 下側受拉＋
    V = By - w*x + (Cy if x > 4 else 0.0)
    M = By*x - w*x*x/2 + (Cy*(x-4) if x > 4 else 0.0)
    return (0.0, V, M)

MEM = [dict(p0=A, p1=B, f=col, breaks=[2.0]), dict(p0=B, p1=Dn, f=beam, breaks=[1.5, 3.0, 4.0], vup=True)]
SUP = [(Cn, "roller")]; HNG = [B]
LAB = {"A": (A, -16, 10), "B": (B, -16, -10), "C": (Cn, 26, 26), "D": (Dn, 14, -12)}
X0 = By/w                       # 剪力零點（最大正彎矩）
X1 = 2*By/w                     # 彎矩零點

def fmt(v): return f"{v:.2f}".rstrip("0").rstrip(".").replace("-", "−")

def fig2_vm():
    W, H = 560, 430
    from structdraw import Canvas
    pV = frame_panel(W, H, MEM, 1, 0.16, C["sfd"], C["fill_s"], "剪力圖 SFD", "t",
                     [(0, 1.0, "4", -16, 0), (1, 0.25, "3", 6, -12), (1, 4-1e-9, "−5", -16, 10),
                      (1, 4.25, "4", 10, -10), (1, X0, "x = 1.5 m", 0, -16)], [(A, "fixed")], HNG, LAB, fit_pad=(130, 70, 92, 70))
    pM = frame_panel(W, H, MEM, 2, 0.13, C["bmd"], C["fill_m"], "彎矩圖 BMD（畫在受拉側）", "t·m",
                     [(0, 0.0, "8", -14, 0), (1, X0, fmt(beam(X0)[2]), 0, 14), (1, X1, "x = 3 m", 0, 18),
                      (1, 4.0, fmt(beam(4.0)[2]), 0, -12)], [(A, "fixed")], HNG, LAB, fit_pad=(130, 70, 92, 70))
    for cv in (pV, pM): cv.support(Cn, "roller", 0, 14)
    return compose([pV, pM], title=f"圖 2　{TAG} 剪力圖與彎矩圖",
                   sub="B 為鉸、梁在 B 不傳水平力：柱上半段 V = M = 0；柱彎矩只在 A 到 4 t 作用點之間",
                   note="柱 A 端 8 t·m 外側（左側）受拉；梁 x = 1.5 m 最大正彎矩 2.25、x = 3 m 反彎、C 點 −4（上側受拉）",
                   path=f"{OUT}/{TAG}-fig-2-vm.svg")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig2_vm(); print(f"{TAG}-fig-2-vm.svg 攔：柱彎矩畫到柱頂、柱受拉側畫反、梁 C 點彎矩正負號")

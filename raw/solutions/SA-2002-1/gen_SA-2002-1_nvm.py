#!/usr/bin/env python3
"""SA-2002-1：軸力圖／剪力圖／彎矩圖（struct-diagram，2026-11-05）
反力取自 SA-2002-1.md §4 Step 1（A_x = −10、A_y = −5/3、H_x = 4、H_y = 29/3 kN）；
各桿內力由自由體（左柱、梁取 A 側，右柱取 H 側）沿桿積分載重算出，圖形不寫死。
用法：python3 gen_SA-2002-1_nvm.py [輸出目錄]；之後以 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C, compose
from nvm_common import frame_panel
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2002-1"

# ── 幾何（題目正本 #3–#7）──
A, B, Cn, D, E, F, G, H = (0, 0), (0, 2), (0, 4), (2, 4), (3, 4), (6, 4), (6, 2), (6, 0)
# ── 反力（§4 Step 1）──
Ax, Ay, Hx, Hy = -10.0, -5/3, 4.0, 29/3
# ── 載重（題目正本 #8–#14；逆時針為正）──
P_C = 10.0        # C 點 →
M_B = +6.0        # B 點力偶，逆時針
m_CD = -2.0       # C–D 分布力矩（每 m），順時針
P_E = 8.0         # E 點 ↓
M_Fb = +4.0       # F 左梁端力偶，逆時針
M_Fc = -4.0       # F 下柱頂力偶，順時針
w_GH = 2.0        # G–H 水平均布，←

def mom(P, pts):  # 力系對 P 之逆時針力矩
    return sum((x-P[0])*fy - (y-P[1])*fx for x, y, fx, fy in pts)

def left_col(s):          # A→C，s 自 A 向上；自由體＝A 側
    pts = [(0, 0, Ax, Ay)]; c = M_B if s > 2 else 0.0
    Me = mom((0, s), pts) + c
    return (-Ay, Ax, -Me)                 # N 拉＋；V（右手側＝+x 方向分量）；M 右手側（內側）受拉＋
def beam(s):              # C→F，s 自 C 向右；自由體＝左柱＋梁左段
    pts = [(0, 0, Ax, Ay), (0, 4, P_C, 0)]
    if s > 3: pts.append((3, 4, 0, -P_E))
    c = M_B + m_CD*min(s, 2)
    Me = mom((s, 4), pts) + c
    Fx = sum(p[2] for p in pts); Fy = sum(p[3] for p in pts)
    return (-Fx, Fy, -Me)                 # 剪力：自由體合力向上為＋（梁慣例）；M 下側受拉＋
def right_col(s):         # H→F，s 自 H 向上；自由體＝H 側
    y = min(s, 2.0); pts = [(6, 0, Hx, Hy), (6, y/2, -w_GH*y, 0)]
    Me = mom((6, s), pts)
    Fx = sum(p[2] for p in pts); Fy = sum(p[3] for p in pts)
    return (-Fy, Fx, -Me)                 # M 右手側（外側）受拉＋；本題為負＝內側受拉

MEM = [dict(p0=A, p1=Cn, f=left_col, breaks=[2.0]),
       dict(p0=Cn, p1=F, f=beam, breaks=[2.0, 3.0], vup=True),
       dict(p0=H, p1=F, f=right_col, breaks=[2.0])]
SUP = [(A, "pin"), (H, "pin")]; HNG = [F]
LAB = {"A": (A, -16, 8), "B": (B, -16, 0), "C": (Cn, -16, -10), "D": (D, 0, -14), "E": (E, 0, -14),
       "F": (F, 14, -12), "G": (G, 16, 0), "H": (H, 16, 8)}

def fmt(v): return f"{v:.2f}".rstrip("0").rstrip(".").replace("-", "−")

def fig4_nvm():
    W, Hh = 470, 430
    v = lambda mi, s, k: MEM[mi]['f'](s)[k]
    pN = frame_panel(W, Hh, MEM, 0, 0.11, C["tension"], C["fill_t"], "軸力圖 AFD（拉＋）", "kN",
                     [(0, 1.0, "+5/3", 26, 0), (2, 1.0, "−29/3", -40, 0)], SUP, HNG, LAB)
    pV = frame_panel(W, Hh, MEM, 1, 0.075, C["sfd"], C["fill_s"], "剪力圖 SFD", "kN",
                     [(0, 3.0, "−10", -18, 0), (1, 1.5, "−5/3", 0, 14), (1, 4.5, "−29/3", 0, 14),
                      (2, 0.25, "4", 16, -4)], SUP, HNG, LAB)
    pM = frame_panel(W, Hh, MEM, 2, 0.026, C["bmd"], C["fill_m"], "彎矩圖 BMD（畫在受拉側）", "kN·m",
                     [(0, 2-1e-9, fmt(v(0, 2-1e-9, 2)), 16, -8), (0, 2+1e-9, fmt(v(0, 2+1e-9, 2)), 16, 10),
                      (0, 4.0-1e-9, fmt(v(0, 4.0-1e-9, 2)), 18, 10), (1, 2.0, "104/3", 0, 14), (1, 3.0, fmt(v(1, 3.0, 2)), 6, 14),
                      (1, 6-1e-9, fmt(v(1, 6-1e-9, 2)), -10, 14), (2, 2.0, fmt(-v(2, 2.0, 2)), -18, 0)],
                     SUP, HNG, LAB)
    return compose([pN, pV, pM], title=f"圖 4　{TAG} 軸力圖、剪力圖、彎矩圖",
                   sub="梁軸力為 0（A_x + 10 = 0）；B 點力偶使彎矩跳 6，C–D 分布力矩使斜率變 V + m；F 兩側力偶各把鉸處彎矩拉回 0",
                   note="左柱、梁全段內側受拉；右柱 G–F 段 4 kN·m 定值、內側（左側）受拉",
                   path=f"{OUT}/{TAG}-fig-4-nvm.svg")

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig4_nvm(); print(f"{TAG}-fig-4-nvm.svg 攔：右柱受拉側畫反、梁誤畫軸力、F 鉸處彎矩不為 0")

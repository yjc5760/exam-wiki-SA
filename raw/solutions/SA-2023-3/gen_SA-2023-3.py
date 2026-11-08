#!/usr/bin/env python3
"""SA-2023-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2023-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2023-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2023-3"

# ── 判讀清單 #1–#9 ──
N_ = {"A": (0, 0), "B": (0, 6), "C": (4, 6), "D": (8, 6), "P": (2, 6)}         # #5、#8
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "B")}, {"ij": ("B", "C")}, {"ij": ("C", "D")}],
    supports=[("A", "pin", -90), ("C", "roller"), ("D", "fixed")],            # #1–#3：A 三角形接左側牆
    udl=[("B", "A", 0.9, None)],                                              # #7：向左
    ptexts=[((1.2, 2.2), "20 kN/m", 14, "#C0392B", "start")],
    loads=[("P", (0, 1.6), "50 kN", (24, 8))],                                # #9：向上（使用者確認）
    labels={"A": (16, 6), "B": (-16, -14), "C": (14, -16), "D": (-14, -16)},
    dims=[((0, 6), (2, 6), "2 m", -34), ((0, 6), (4, 6), "4 m", -72), ((4, 6), (8, 6), "4 m", -72),
          ((0, 0), (0, 6), "6 m", -70)],
    extra_pts=[(-1.6, 8.4), (9.0, -0.9)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 560, 520,
                          note="A 鉸支承（左側牆）；C 滾支承；D 固定；20 kN/m 水平向左；50 kN 向上作用於 BC 中點")

FIGURES = [(fig1_problem, "50 kN 方向讀反、A 讀成固定端")]

# ── 解題圖（階段 E，2026-11-08）：數值由勁度法重解，與 SA-2023-3.md §4 Step 4–6 對照（assert）──
#    EIθ_B = 470/11、EIθ_C = 20/11；M_BA = −755/11、M_BC = +755/11、M_CB = −20/11、M_CD = +20/11、M_DC = 10/11
SOL = dict(nodes=N_, supports=[("A", "pin", -90), ("C", "roller"), ("D", "fixed")])

def _solve():
    from frame2d import Frame
    f = Frame()
    for n, p in N_.items(): f.node(n, *p)
    f.support("A", 1, 1, 0); f.support("C", 0, 1, 0); f.support("D", 1, 1, 1)
    f.member("BA", "B", "A", 1.0, w=20)                              # B→A 時局部 −y 朝左：20 kN/m 向左
    f.member("BP", "B", "P", 1.0); f.member("PC", "P", "C", 1.0); f.member("CD", "C", "D", 1.0)
    f.load("P", fy=50)                                               # 50 kN 向上（判讀 #9，使用者確認）
    f.solve()
    cw = lambda nm: (-f.end[nm][2], -f.end[nm][5])
    assert abs(cw("BA")[0] + 755/11) < 1e-6 and abs(cw("PC")[1] + 20/11) < 1e-6 and abs(cw("CD")[1] - 10/11) < 1e-6
    assert abs(f.R["A"][0] - 3205/66) < 1e-5 and abs(f.R["C"][1] + 395/44) < 1e-5
    return f

def fig2_solution():
    from beamfig import frame_figure
    from frameviz import member_moment
    f = _solve()
    ba = next(m for m in f.M if m["name"] == "BA")
    k = max(range(401), key=lambda k: member_moment(f, ba, k/400)); xi_max = k / 400
    L = [("BA", 0.0, 4, 34), ("BA", xi_max, -26, 0), ("BP", 1.0, 0, -18), ("PC", 1.0, -34, -14),
         ("CD", 1.0, -14, -16)]
    return frame_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg",
        "圖 2　SA-2023-3 變形形狀與彎矩圖（單位 kN-m）",
        "無側移；B 順時針轉、BC 被 50 kN 向上頂起",
        "梁 B 端 68.64 下緣受拉；50 kN 向上 ⇒ 中點 14.77 上緣受拉", L, fmt="{:.2f}", W=560, H=500,
        notes=("", f"柱 AB 正彎矩極大在距 A {6*(1-xi_max):.2f} m 處"))

FIGURES.append((fig2_solution, "50 kN 方向讀反（BC 段彎矩整段反號）；20 kN/m 向左被當成向右"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

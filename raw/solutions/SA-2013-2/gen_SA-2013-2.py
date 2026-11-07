#!/usr/bin/env python3
"""SA-2013-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2013-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2013-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2013-2"

# ── 判讀清單 #1–#5 ──
N_ = {"A": (0, 0), "B": (0, 10), "C": (10, 10), "P": (5, 10)}                  # #4
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "B")}, {"ij": ("B", "C")}],               # #1
    supports=[("A", "fixed"), ("C", "pin")],                                  # #2、#3
    loads=[("P", (0, -2.0), "20 kN", (0, -14))],                              # #5
    labels={"A": (18, -10), "B": (-16, -14), "C": (16, -14)},
    dims=[((0, 0), (0, 10), "10 m", -54), ((0, 0), (5, 0), "5 m", 46), ((5, 0), (10, 0), "5 m", 46)],
    extra_pts=[(-1.4, 12.6), (11.4, -1.2)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 560, 520,
                          note="A 固定端；C 鉸支承（水平＋垂直反力）；20 kN 在 BC 中點；各桿 E、I 相同")

FIGURES = [(fig1_problem, "C 讀成滾支承（少一個贅力）、載重位置讀錯")]

def _auto_scales(f, span, dfrac=0.12, mfrac=0.17):
    """依解出的位移與彎矩自動取放大倍率（圖形隨輸入改變，不寫死）。"""
    from frameviz import member_moment
    dmax = max(max(abs(v[0]), abs(v[1])) for v in f.d.values()) or 1
    mmax = max(abs(member_moment(f, m, k/40)) for m in f.M for k in range(41)) or 1
    return dfrac*span/dmax, mfrac*span/mmax

# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2013-2.md §4（C_x = 45/14 向左、C_y = 55/7、θ_C = 625/(7EI) 逆時針）──
from frameviz import solution_figure, build_frame, end_moments
SOL = dict(nodes=N_, members=[dict(name="AB", ij=("A", "B"), EI=1), dict(name="BP", ij=("B", "P"), EI=1),
                              dict(name="PC", ij=("P", "C"), EI=1)],
           supports=[("A", "fixed"), ("C", "pin")], fe_loads=[("P", 0, -20, 0)])

def fig2_solution():
    f = build_frame(SOL)
    assert abs(f.R["C"][0] + 45/14) < 1e-6 and abs(f.R["C"][1] - 55/7) < 1e-6   # C 反力
    assert abs(f.d["C"][2] - 625/7) < 1e-4                                     # θ_C·EI，逆時針為正
    assert abs(f.d["B"][0]) < 1e-3*abs(f.d["C"][2])                            # B 無水平位移（副標題依據）
    ds, ms = _auto_scales(f, 10)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2013-2 變形形狀與彎矩圖（單位 kN·m）", "C 端逆時針轉 625/(7EI)；BC 不伸縮，B 無水平位移",
        "A 端 10.71、B 角 21.43、載重點 39.29", fmt="{:.2f}", W=540, H=470,
        notes=("θ_C = 625/(7EI)", "C 反力：45/14 = 3.21 kN 向左、55/7 = 7.86 kN 向上"))

FIGURES.append((fig2_solution, "θ_C 轉向寫反、C 水平反力方向寫反"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

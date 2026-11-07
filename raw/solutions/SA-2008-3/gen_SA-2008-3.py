#!/usr/bin/env python3
"""SA-2008-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2008-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2008-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2008-3"

# ── 判讀清單 #1–#5 ──
N_ = {"A": (0, 6), "B": (6, 6), "C": (10.5, 0)}                                # #4
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "B")}, {"ij": ("B", "C")}],               # #1
    supports=[("A", "roller"), ("C", "fixed", 0)],                            # #2、#3
    udl=[("A", "B", 1.3, "2 kN/m")],                                          # #5
    labels={"A": (-16, -16), "B": (16, -16), "C": (20, -14)},
    dims=[((0, 0), (6, 0), "6 m", 44), ((6, 0), (10.5, 0), "4.5 m", 44), ((10.5, 0), (10.5, 6), "6 m", 70)],
    extra_pts=[(-0.8, 8.0), (12.0, -1.2)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 480,
                          note="A 滾支承（垂直反力）；C 固定端；載重只在 AB；BC 斜長 7.5 m")

FIGURES = [(fig1_problem, "A、C 支承互換、載重延伸到 BC、BC 投影讀錯")]

def _auto_scales(f, span, dfrac=0.12, mfrac=0.17):
    """依解出的位移與彎矩自動取放大倍率（圖形隨輸入改變，不寫死）。"""
    from frameviz import member_moment
    dmax = max(max(abs(v[0]), abs(v[1])) for v in f.d.values()) or 1
    mmax = max(abs(member_moment(f, m, k/40)) for m in f.M for k in range(41)) or 1
    return dfrac*span/dmax, mfrac*span/mmax

# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2008-3.md §4 步驟 3–4 ──
from frameviz import solution_figure, build_frame, end_moments
RA = 3888/529                                    # §4 步驟 3
SOL = dict(nodes=N_, members=[dict(name="AB", ij=("A", "B"), EI=1, w=2), dict(name="BC", ij=("B", "C"), EI=1)],
           supports=[("A", "roller"), ("C", "fixed")])

def fig2_solution():
    f = build_frame(SOL); M = end_moments(f)
    assert abs(f.R["A"][1] - RA) < 1e-6                       # R_A = 3888/529
    assert abs(abs(M["AB"][1]) - 4284/529) < 1e-6             # M_B = 4284/529
    assert abs(abs(M["BC"][1]) - 6786/529) < 1e-6             # M_C = 6786/529
    ds, ms = _auto_scales(f, 10.5)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2008-3 變形形狀與彎矩圖（單位 kN·m）", "C 無水平反力；BC 只受垂直力",
        "B 角內側受拉、C 端外側受拉", fmt="{:.2f}", W=560, H=470,
        notes=("", "R_A = 3888/529 = 7.35 kN；AB 最大 13.50 @ x = 3.675 m"))

FIGURES.append((fig2_solution, "M_B 受拉側畫反、BC 漏畫反曲點、AB 最大彎矩位置錯"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

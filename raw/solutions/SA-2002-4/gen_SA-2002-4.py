#!/usr/bin/env python3
"""SA-2002-4：題目附圖重繪＋變形形狀與彎矩圖（struct-diagram 規範；2026-11-04）
題目附圖的幾何、支承、載重逐項對應題目正本 SA-2002-4-problem.md §4 判讀清單（註解中的 #n）。
彎矩數值由勁度法重算，並 assert 與解析 §4 一致（-21、-18、18 kN-m）。
用法：python3 gen_SA-2002-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from frameviz import problem_figure, solution_figure, build_frame, end_moments
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2002-4"

# ── 判讀清單 #1–#7 ──
SPEC = dict(
    nodes={"A": (0, 0), "B": (0, 6), "C": (6, 6), "D": (6, 0)},
    members=[dict(name="AB", ij=("A", "B"), EI=1),            # #3 柱 AB：6 m、I
             dict(name="BC", ij=("B", "C"), EI=2, thick=True),  # #5 梁 BC：6 m、2I
             dict(name="DC", ij=("D", "C"), EI=1)],             # #4 柱 CD：6 m、I
    supports=[("A", "fixed"), ("D", "fixed")],                  # #1
    loads=[("B", (2.2, 0), "13 kN", (-30, 0))],                 # #7
    fe_loads=[("B", 13, 0, 0)],
    labels={"A": (-18, 14), "B": (-16, -16), "C": (16, -16), "D": (18, 14)},
    mlabels=[((0, 3.6), "I", None, "end"), ((6, 3.6), "I", None, "start"), ((3, 6.45), "2I", None, "middle")],
    dims=[((0, 0), (6, 0), "6 m", 40), ((6, 0), (6, 6), "6 m", 48), ((0, 0), (0, 6), "6 m", -66)],
    thick={"BC": True})
SPEC["mlabels"] = [((-0.35, 3.0), "I", None, "end"), ((6.35, 3.0), "I", None, "start"), ((3, 6.5), "2I", None, "middle")]

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 520,
                          note="A、D 固接；B、C 剛接；E 為常數")

def fig2_solution():
    f = build_frame(SPEC); M = end_moments(f)
    assert abs(M["AB"][0] + 21) < 1e-3 and abs(M["AB"][1] + 18) < 1e-3 and abs(M["BC"][0] - 18) < 1e-3
    return solution_figure(f, SPEC, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", 0.012, 0.075,
        "SA-2002-4　側推門型剛架：柱雙曲率、梁反對稱", "B、C 同向順時針轉 9/EI，側移 144/EI",
        "柱底迎風側（左）受拉、柱頂內側受拉", munit="", fmt="{:.0f}",
        notes=("", "每柱剪力 (21+18)/6 = 6.5 kN，合計 13 kN ✓"))

FIGURES = [(fig1_problem, "A、D 支承誤讀、I／2I 標反"),
           (fig2_solution, "受拉側畫反（柱底畫成內側受拉、梁 B 端畫成上側受拉）")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

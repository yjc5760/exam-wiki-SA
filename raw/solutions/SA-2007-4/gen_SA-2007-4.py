#!/usr/bin/env python3
"""SA-2007-4：題目附圖重繪＋變形形狀與彎矩圖（struct-diagram 規範；2026-11-04）
題目附圖的幾何、支承、載重逐項對應題目正本 SA-2007-4-problem.md §4 判讀清單（註解中的 #n）。
彎矩由勁度法重算，並 assert 與解析一致（M_AC = -80、M_CB = 80-40√2）。
用法：python3 gen_SA-2007-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from frameviz import problem_figure, solution_figure, build_frame, end_moments
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2007-4"

import math
# ── 判讀清單 #1–#7 ──
SPEC = dict(
    nodes={"A": (0, 0), "B": (0, 4), "C": (4, 4)},       # #4 #5：B 在 A 正上方
    members=[dict(name="AC", ij=("A", "C"), EI=1), dict(name="BC", ij=("B", "C"), EI=1)],
    supports=[("A", "fixed"), ("B", "roller")],           # #1 #2
    loads=[("C", (1.8, 0), "20 N", (30, 0), True)],       # #7
    fe_loads=[("C", 20, 0, 0)],
    labels={"A": (24, 8), "B": (-6, -24), "C": (6, -20)},
    dims=[((0, -0.6), (4, -0.6), "4 m", 30), ((0, 0), (0, 4), "4 m", -52)],
    extra_pts=[(0, -1.2)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 600, 560,
                          note="A 斜置固接；B 滾支承（只有垂直反力）；B 在 A 正上方")

def fig2_solution():
    f = build_frame(SPEC); M = end_moments(f)
    assert abs(M["AC"][0] + 80) < 1e-3 and abs(M["BC"][1] - (80 - 40 * math.sqrt(2))) < 1e-3
    return solution_figure(f, SPEC, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", 0.0017, 0.022,
        "SA-2007-4　斜柱 AC 為雙曲率：反曲點距 A 約 4.38 m", "C 沿垂直 AC 方向（右下）移動",
        "AC：A 端左上側、C 端右下側受拉", munit="", fmt="{:.2f}",
        notes=("", "B 點反力 5.86 N 向下；M_A = 20×4 = 80 N·m"), margins=(70, 90, 95, 95))

FIGURES = [(fig1_problem, "B 水平位置、A 支承方向誤讀"),
           (fig2_solution, "把兩端同為逆時針的桿端彎矩畫成同側、漏掉反曲點")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

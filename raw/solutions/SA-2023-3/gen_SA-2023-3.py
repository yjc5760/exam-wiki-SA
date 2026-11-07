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

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

#!/usr/bin/env python3
"""SA-2021-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2021-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2021-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2021-1"

# ── 判讀清單 #1–#6 ──
N_ = {"a": (0, 0), "P": (2, 0), "b": (4, 0), "c": (8, 0), "d": (10, 0)}       # #5
SPEC = dict(
    nodes=N_, members=[{"ij": ("a", "b")}, {"ij": ("b", "c")}, {"ij": ("c", "d")}],
    supports=[("a", "roller"), ("d", "fixed")],                               # #1、#4
    hinges=["c"],                                                             # #3
    springs=[("b", 1.9, "k")],                                                # #2
    loads=[("P", (0, -1.6), "36 kN", (0, -14)), ("b", (0, -1.6), "36 kN", (0, -14))],   # #6
    labels={"a": (-4, -20), "b": (16, -14), "c": (0, -18), "d": (-14, -16)},
    dims=[((0, 0), (2, 0), "2 m", 104), ((2, 0), (4, 0), "2 m", 104), ((4, 0), (8, 0), "4 m", 104), ((8, 0), (10, 0), "2 m", 104)],
    extra_pts=[(-0.8, 2.4), (10.8, -3.6)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 620, 420,
                          note="a 滾支承；b 點彈簧 k = 15000 kN/m；c 內鉸；d 固定端；EI = 10000 kN-m^{2}")

FIGURES = [(fig1_problem, "c 讀成支承、彈簧位置讀錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

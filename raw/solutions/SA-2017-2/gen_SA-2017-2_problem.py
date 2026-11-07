#!/usr/bin/env python3
"""SA-2017-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2017-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2017-2_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2017-2"

# ── 判讀清單 #1–#4 ──（m、n 為符號；c 位置依圖面約 0.43 L 示意）
N_ = {"a": (0, 0), "c": (4.3, 0), "b": (10, 0)}
SPEC = dict(
    nodes=N_, members=[{"ij": ("a", "c")}, {"ij": ("c", "b")}],
    supports=[("a", "fixed"), ("b", "fixed")],                                # #1
    hinges=["c"],                                                             # #2
    udl=[("a", "b", 1.2, "w")],                                               # #3：滿跨
    labels={"a": (14, 18), "c": (0, 22), "b": (-14, 18)},
    dims=[((0, 0), (4.3, 0), "m", 54), ((4.3, 0), (10, 0), "n", 54), ((0, 0), (10, 0), "L", 96)],
    extra_pts=[(-0.9, 2.0), (10.9, -2.6)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 420,
                          note="a、b 固定端；c 內鉸；w 滿跨（考卷以方塊列表示）；m + n = L")

FIGURES = [(fig1_problem, "把載重方塊讀成構件、w 只作用一側、c 讀成支承")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

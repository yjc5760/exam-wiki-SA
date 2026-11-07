#!/usr/bin/env python3
"""SA-2020-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2020-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2020-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2020-3"

# ── 判讀清單 ──
N_ = {"a": (0, 0), "b": (2, 0), "c": (4, 0), "d": (7, 0)}                          # #1
SPEC = dict(
    nodes=N_, members=[{"ij": ("a", "b")}, {"ij": ("b", "c")}, {"ij": ("c", "d"), "thick": True}],  # #6
    hinges=["c"],                                                                   # #4
    supports=[("a", "pin"), ("b", "roller"), ("d", "fixed")],                        # #2、#3、#5
    labels={"a": (0, -22), "b": (0, -22), "c": (0, -24), "d": (-14, -22)},
    mlabels=[((1, 0.32), "I", None, "middle"), ((3, 0.32), "I", None, "middle"), ((5.5, 0.36), "1.5I", None, "middle")],
    dims=[((0, 0), (2, 0), "2 m", 66), ((2, 0), (4, 0), "2 m", 66), ((4, 0), (7, 0), "3 m", 66)],
    extra_pts=[(-0.6, 0.8), (7.6, -0.6)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 760, 320,
                          note="a 鉸支承、b 滾支承、c 內鉸、d 固定端；cd 段慣性矩 1.5I")

FIGURES = [(fig1_problem, "c 讀成支承、d 讀成鉸支承、漏讀 cd 為 1.5I")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

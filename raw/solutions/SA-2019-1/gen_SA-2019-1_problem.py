#!/usr/bin/env python3
"""SA-2019-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2019-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2019-1_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2019-1"

# ── 判讀清單 #1–#6 ──（考卷附圖沒有尺寸線，尺寸取自題文）
N_ = {"C": (0, 0), "A": (12, 0), "D": (0, 9), "B": (12, 9)}                    # #1、#5
SPEC = dict(
    nodes=N_, members=[],
    truss=[("D", "B"), ("C", "A"), ("D", "C"), ("B", "A"), ("D", "A"), ("C", "B")],   # #2
    joints=list(N_),
    supports=[("C", "pin"), ("A", "roller")],                                 # #3、#4
    loads=[("B", (2.6, 0), "P", (18, 0), True)],                              # #6
    labels={"C": (-18, -8), "A": (18, -8), "D": (-16, -12), "B": (8, -18)},
    dims=[((0, 0), (12, 0), "12 m", 66), ((0, 0), (0, 9), "9 m", -60)],
    extra_pts=[(-2.4, 10.2), (15.8, -2.0)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 620, 480,
                          note="C 鉸支承、A 滾支承；斜桿交叉處不相連；水平 12 m、垂直 9 m、對角 15 m（尺寸取自題文，考卷附圖未標）")

FIGURES = [(fig1_problem, "A、C 支承互換、斜桿交叉點當成節點")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

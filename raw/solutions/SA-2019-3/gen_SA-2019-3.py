#!/usr/bin/env python3
"""SA-2019-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2019-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2019-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2019-3"

# ── 判讀清單 #1–#5 ──（以 L = 1 為單位）
N_ = {"A": (0, 0), "B": (1, 0), "C": (2, 0), "D": (3, 0)}
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "B")}, {"ij": ("B", "C")}, {"ij": ("C", "D")}],
    supports=[("A", "pin"), ("B", "roller"), ("C", "roller"), ("D", "roller")],   # #1、#2
    udl=[("A", "D", 0.2, "w")],                                               # #4
    labels={"A": (-14, -14), "B": (-14, -14), "C": (-14, -14), "D": (14, -14)},
    mlabels=[((0.5, -0.1), "EI, L", None, "middle"), ((1.5, -0.1), "EI, L", None, "middle"), ((2.5, -0.1), "EI, L", None, "middle")],
    dims=[((0, 0), (1, 0), "L", 74), ((1, 0), (2, 0), "L", 74), ((2, 0), (3, 0), "L", 74)],
    extra_pts=[(-0.1, 0.4), (3.1, -0.42)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 680, 330,
                          note="A 鉸支承；B、C、D 滾支承；B、C 同量向下沉陷 Δ（未知，為所求）")

FIGURES = [(fig1_problem, "A 讀成滾支承、只讓一個支承沉陷")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

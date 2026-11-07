#!/usr/bin/env python3
"""SA-2011-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2011-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2011-3_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2011-3"

# ── 判讀清單 ──
N_ = {"A": (0, 0), "B": (30, 0), "C": (45, 0), "D": (60, 0)}                     # #1
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "B")}, {"ij": ("B", "C")}, {"ij": ("C", "D")}],  # #6 連續
    supports=[("A", "roller"), ("B", "roller"), ("D", "pin")],                       # #2–#4
    labels={"A": (0, -22), "B": (0, -22), "C": (0, -22), "D": (0, -22)},
    dims=[((0, 0), (30, 0), "30 m", 66), ((30, 0), (45, 0), "15 m", 66), ((45, 0), (60, 0), "15 m", 66)],
    extra_pts=[(-3, 3), (63, -3)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 860, 320,
                          note="A、B 滾支承、D 鉸支承；C 為 BD 中點（非支承、非內鉸）")

FIGURES = [(fig1_problem, "B 讀成內鉸、C 當成支承")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

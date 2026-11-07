#!/usr/bin/env python3
"""SA-2003-4：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2003-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2003-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2003-4"

# ── 判讀清單 ──
N_ = {"A": (0, 0), "B": (5, 0), "C": (10, 0)}                                  # #1
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "B")}, {"ij": ("B", "C")}],                  # #4 B 不是內鉸
    supports=[("A", "fixed"), ("C", "roller")],                                   # #2、#3
    labels={"A": (-30, 0), "B": (0, -20), "C": (24, -18)},
    mlabels=[((2.5, 0.75), "EI", None, "middle")],                                # #5
    dims=[((0, 0), (5, 0), "5 m", 70), ((5, 0), (10, 0), "5 m", 70)],             # #1
    extra_pts=[(-1.2, 1.5), (11, -1)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 760, 330,
                          note="A 固定端、C 滾支承；B 為跨中斷面（非內鉸）；EI 常數")

FIGURES = [(fig1_problem, "A、C 支承互換、把 B 當成內鉸或支承")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

#!/usr/bin/env python3
"""SA-2005-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2005-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2005-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2005-3"

# ── 判讀清單 ──
N_ = {"A": (0, 0), "B": (10, 0), "D": (15, 0), "C": (20, 0)}                     # #1
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "B")}, {"ij": ("B", "D")}, {"ij": ("D", "C")}],  # #5 連續、無內鉸
    supports=[("A", "roller"), ("B", "pin"), ("C", "roller")],                       # #2–#4
    labels={"A": (-22, -16), "B": (-20, -18), "D": (0, -20), "C": (22, -16)},
    dims=[((0, 0), (10, 0), "10 m", 66), ((10, 0), (20, 0), "10 m", 66)],
    extra_pts=[(-1.5, 1.5), (21.5, -1)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 760, 320,
                          note="A、C 滾支承、B 鉸支承；D 為 BC 跨中點（非支承）")

FIGURES = [(fig1_problem, "B、C 支承讀錯、D 位置讀錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

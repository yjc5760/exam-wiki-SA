#!/usr/bin/env python3
"""SA-2015-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2015-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2015-2_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2015-2"

# ── 判讀清單 ──
N_ = {"A": (0, 0), "F": (15, 0), "B": (30, 0), "C": (40, 0), "D": (50, 0), "E": (80, 0)}   # #1
SPEC = dict(
    nodes=N_, members=[{"ij": (a, b)} for a, b in (("A", "F"), ("F", "B"), ("B", "C"), ("C", "D"), ("D", "E"))],
    hinges=["C"],                                                                   # #4
    supports=[("A", "pin"), ("B", "roller"), ("D", "roller"), ("E", "roller")],      # #2、#3
    labels={"A": (0, -22), "F": (0, -22), "B": (0, -22), "C": (0, -24), "D": (0, -22), "E": (0, -22)},
    dims=[((0, 0), (15, 0), "15 m", 66), ((15, 0), (30, 0), "15 m", 66), ((30, 0), (40, 0), "10 m", 66),
          ((40, 0), (50, 0), "10 m", 66), ((50, 0), (80, 0), "30 m", 66)],
    extra_pts=[(-3, 3), (83, -3)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 960, 320,
                          note="A 鉸支承、B、D、E 滾支承；C 為內鉸；F 為 AB 跨中點")

FIGURES = [(fig1_problem, "C 當成支承、DE 跨長讀成 10 m")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

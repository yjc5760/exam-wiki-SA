#!/usr/bin/env python3
"""SA-2005-2：題目附圖重繪（struct-diagram 規範；2026-11-04）
題目附圖的幾何、支承、載重逐項對應題目正本 SA-2005-2-problem.md §4 判讀清單（註解中的 #n）。
用法：python3 gen_SA-2005-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from frameviz import problem_figure, solution_figure, build_frame, end_moments
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2005-2"

# ── 判讀清單 #1–#8 ──
SPEC = dict(
    nodes={"A": (0, 4), "B": (4, 4), "C": (8, 4), "D": (4, 0), "E": (0, 0)},
    members=[dict(name="AB", ij=("A", "B"), EI=1), dict(name="BC", ij=("B", "C"), EI=1),   # #4 #6
             dict(name="BD", ij=("B", "D"), EI=1), dict(name="ED", ij=("E", "D"), EI=1)],  # #5
    supports=[("A", "fixed"), ("E", "fixed"), ("C", "pin")],                               # #1 #2 #3
    loads=[("B", (0, -1.4), "10 N", (24, -6))],                                            # #8
    labels={"A": (8, -16), "B": (16, -16), "C": (6, -18), "D": (16, 16), "E": (8, 18)},
    dims=[((0, 0), (4, 0), "4 m", 46), ((4, 0), (8, 0), "4 m", 46), ((0, 0), (0, 4), "4 m", -44)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 540,
                          note="A、E 固接；C 鉸支承；B、D 剛接；各桿 E、I 相同")

FIGURES = [(fig1_problem, "C 讀成內鉸、D 讀成鉸接")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

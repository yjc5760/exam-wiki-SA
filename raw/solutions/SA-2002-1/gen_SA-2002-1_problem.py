#!/usr/bin/env python3
"""SA-2002-1：題目附圖重繪（struct-diagram 規範；2026-11-05）
幾何、支承、載重逐項對應題目正本 SA-2002-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2002-1_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2002-1"

# ── 判讀清單 #1–#14 ──
SPEC = dict(
    nodes={"A": (0, 0), "B": (0, 2), "C": (0, 4), "D": (2, 4), "E": (3, 4), "F": (6, 4), "G": (6, 2), "H": (6, 0)},  # #3–#7
    members=[dict(ij=("A", "C")), dict(ij=("C", "F")), dict(ij=("F", "H"))],
    supports=[("A", "pin"), ("H", "pin")],                                    # #1
    hinges=["F"],                                                             # #2
    loads=[("C", (1.3, 0), "10 kN", (-34, -14)),                              # #8
           ("E", (0, -1.3), "8 kN", (0, -14))],                               # #11
    couples=[((0, 2), True, "6 kN-m", (58, -6)),                               # #9 逆時針
             ((5.55, 4.0), True, "4 kN-m", (-30, -34)),                        # #12 梁端逆時針
             ((6.0, 3.45), False, "4 kN-m", (56, 4))],                         # #13 柱頂順時針
    dmoment=[("C", "D", 4, False, "2 kN-m/m", (0, -52))],                    # #10 順時針
    udl=[("G", "H", 0.75, None)],                                             # #14 向左
    labels={"A": (-16, 4), "B": (-34, 0), "C": (-16, 12), "D": (0, 16), "E": (8, 16), "F": (14, -14), "G": (-16, 0), "H": (-16, 6)},
    mlabels=[((7.0, 1.0), "2 kN/m", "#C62828", "start")],
    dims=[((0, 0), (0, 2), "2 m", -58), ((0, 2), (0, 4), "2 m", -58),
          ((0, 0), (3, 0), "3 m", 70), ((3, 0), (6, 0), "3 m", 70), ((0, 4), (2, 4), "2 m", 55),
          ((6, 0), (6, 2), "2 m", -52)],
    extra_pts=[(-0.9, 4), (7.6, 1), (0, -0.4)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 760, 560,
                          note="A、H 鉸支承；F 內鉸；C–D 分布力矩順時針；F 兩側力偶：梁端逆時針、柱頂順時針")

FIGURES = [(fig1_problem, "分布力矩讀成均布力、F 兩側力偶轉向讀反、E 位置讀錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

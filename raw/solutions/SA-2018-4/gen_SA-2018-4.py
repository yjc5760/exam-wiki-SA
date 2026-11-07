#!/usr/bin/env python3
"""SA-2018-4：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2018-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2018-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2018-4"

# ── 判讀清單 ──
N_ = {"A": (0, 0), "B": (5, 0), "C": (10, 0), "D": (15, 0), "E": (20, 0), "F": (2, -4), "G": (18, -4)}  # #1
SPEC = dict(
    nodes=N_, members=[{"ij": (a, b)} for a, b in (("A", "B"), ("B", "C"), ("C", "D"), ("D", "E"), ("F", "B"), ("G", "D"))],  # #2、#3
    supports=[("A", "roller"), ("E", "roller"), ("F", "fixed"), ("G", "fixed")],     # #4、#5
    labels={"A": (-4, -20), "B": (0, -20), "C": (0, -20), "D": (0, -20), "E": (4, -20), "F": (-32, -12), "G": (32, -12)},
    dashed=[("F", "G")],
    dims=[((0, 0), (5, 0), "5 m", -52), ((5, 0), (10, 0), "5 m", -52), ((10, 0), (15, 0), "5 m", -52),
          ((15, 0), (20, 0), "5 m", -52), ((10, -4), (10, 0), "4 m", 0),
          ((2, -4), (5, -4), "3 m", 58), ((15, -4), (18, -4), "3 m", 58)],
    extra_pts=[(-1.5, 1.6), (21.5, -6)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 820, 470,
                          note="A、E 滾支承；F、G 固定支承；B、D 剛接；全部 EI = 800 kN-m²")

FIGURES = [(fig1_problem, "斜撐方向讀反（F、G 在 B、D 外側）、F、G 讀成鉸支承")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

#!/usr/bin/env python3
"""SA-2025-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2025-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2025-2_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2025-2"

# ── 判讀清單 ──
N_ = {"A": (0, 0), "B": (4, 0), "F": (6, 0), "C": (8, 0), "D": (12, 0), "E": (16, 0),
      "F1": (6, -0.45), "F2": (6, 0.45)}                                           # #1、#5
SPEC = dict(
    nodes=N_, members=[{"ij": (a, b)} for a, b in (("A", "B"), ("B", "F"), ("F", "C"), ("C", "D"), ("D", "E"))],
    hinges=["B", "D"],                                                              # #4
    supports=[("A", "fixed"), ("C", "roller"), ("E", "roller")],                     # #2、#3
    dashed=[("F1", "F2")],
    labels={"A": (14, -20), "B": (0, -22), "F": (0, 34), "C": (0, -22), "D": (0, -22), "E": (0, -22)},
    dims=[((0, 0), (4, 0), "4 m", 70), ((4, 0), (8, 0), "4 m", 70), ((8, 0), (12, 0), "4 m", 70),
          ((12, 0), (16, 0), "4 m", 70), ((6, 0), (8, 0), "2 m", -50)],
    extra_pts=[(-0.8, 1.2), (16.8, -1)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 820, 340,
                          note="A 固定端、B、D 內鉸、C、E 滾支承；F 在 C 左方 2 m（剪力斷面）")

FIGURES = [(fig1_problem, "F 當成自由端或支承、B／D 讀成支承")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

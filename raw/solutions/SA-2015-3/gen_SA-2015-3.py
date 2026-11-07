#!/usr/bin/env python3
"""SA-2015-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2015-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2015-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2015-3"

# ── 判讀清單 #1–#7 ──
N_ = {"B": (0, 4), "C": (1, 4), "D": (4, 4), "E": (7, 4), "F": (8, 4), "A": (0, 0), "G": (4, 0), "H": (8, 0)}   # #4、#5
SPEC = dict(
    nodes=N_, members=[{"ij": (a, b)} for a, b in (("B", "C"), ("C", "D"), ("D", "E"), ("E", "F"),
                                                    ("A", "B"), ("G", "D"), ("H", "F"))],
    supports=[("A", "fixed"), ("G", "fixed"), ("H", "fixed")],                # #1
    hinges=["C", "E"],                                                        # #2
    udl=[("B", "F", 0.9, "4 kN/m")],                                          # #7
    labels={"B": (-16, -12), "C": (0, 20), "D": (-14, 18), "E": (0, 20), "F": (16, -12),
            "A": (-20, -16), "G": (20, -16), "H": (20, -16)},
    dims=[((0, 0), (1, 0), "1 m", 44), ((1, 0), (4, 0), "3 m", 44), ((4, 0), (7, 0), "3 m", 44),
          ((7, 0), (8, 0), "1 m", 44), ((8, 0), (8, 4), "4 m", 60)],
    extra_pts=[(-0.6, 5.6), (9.4, -0.8)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 460,
                          note="A、G、H 固定；C、E 為梁上內鉸；EI 定值、忽略軸向變形")

FIGURES = [(fig1_problem, "C、E 位置讀錯（BC、EF 各 1 m）、漏讀中柱 GD")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

#!/usr/bin/env python3
"""SA-2003-2：題目附圖重繪（struct-diagram 規範；2026-11-05）
幾何、支承、載重逐項對應題目正本 SA-2003-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2003-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2003-2"

# ── 判讀清單 #1–#9（長度單位 λ） ──
SPEC = dict(
    nodes={"A": (0, 3), "B": (4, 3), "C": (8, 3), "D": (0, 0), "E": (4, 0)},   # #2
    members=[],
    rigid=[("A", "C")],                                                       # #1 剛梁
    truss=[("A", "D"), ("A", "E"), ("B", "E")],                               # #3
    joints=["A", "B", "D", "E"],                                              # #4 #5
    supports=[("D", "pin"), ("E", "pin")],                                    # #6
    loads=[("C", (0, -1.4), "F", (14, -12))],                                 # #7
    labels={"A": (-16, -14), "B": (14, 14), "C": (14, 14), "D": (-18, 0), "E": (16, 0)},
    mlabels=[((8.6, 1.8), "EI → ∞", None, "end")],
    dims=[((0, 0), (0, 3), "3λ", -60), ((0, 0), (4, 0), "4λ", 62), ((4, 0), (8, 0), "4λ", 62)],
    extra_pts=[(-1, 3), (8.5, 4.6)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 700, 440,
                          note="剛梁 A–B–C 以鉸接連桿 AD、AE、BE（EA 相同）支撐；D、E 鉸支承；F 為力的大小")

FIGURES = [(fig1_problem, "AE 斜桿接到 B、F 讀成節點、連桿長度讀錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

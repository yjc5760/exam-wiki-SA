#!/usr/bin/env python3
"""SA-2024-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2024-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2024-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2024-3"

# ── 判讀清單 #1–#6 ──（L = 1、L_b = 2 為示意；題目只給 L_b/L > 1）
N_ = {"A": (0, 0), "B": (0, 1), "C": (2, 1), "D": (2, 0)}
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "B")}, {"ij": ("B", "C")}, {"ij": ("C", "D")}],
    supports=[("A", "fixed"), ("D", "fixed")],                                # #1
    hinges=["C"],                                                             # #3：C 內鉸（使用者確認）
    loads=[("B", (0.42, 0), "P", (-10, -16))],                               # #6
    labels={"A": (-20, -14), "B": (-12, -16), "C": (14, -16), "D": (20, -14)},
    mlabels=[((1, 1.1), "EI, L_{b}", None, "middle"), ((-0.08, 0.5), "EI, L", None, "end"), ((2.08, 0.5), "EI, L", None, "start")],
    extra_pts=[(-0.6, 1.4), (2.5, -0.2)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 560, 400,
                          note="A、D 固定；B 剛接；C 為梁與右柱之間的內鉸；L_{b}/L > 1（圖中比例為示意）")

FIGURES = [(fig1_problem, "漏讀 C 點內鉸（當成對稱門型剛架）")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

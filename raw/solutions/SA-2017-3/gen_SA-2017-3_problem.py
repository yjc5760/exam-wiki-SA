#!/usr/bin/env python3
"""SA-2017-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2017-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2017-3_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_libp"))   # 本題 figs/_lib 是解析自繪圖用的舊版，題目重繪另用 _libp
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2017-3"

# ── 判讀清單 #1–#7 ──（考卷為照片式插圖，依判讀清單畫成線圖）
N_ = {"A": (0, 0), "B": (0, 4), "C": (6, 4), "D": (6, 0), "M": (6, 2)}         # #3
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "B")}, {"ij": ("B", "C")}, {"ij": ("C", "D")}],
    supports=[("A", "pin"), ("D", "pin")],                                    # #1
    udl=[("B", "C", 0.9, "45 kN/m")],                                         # #5
    loads=[("C", (-1.3, 0), "60 kN", (0, -16)), ("M", (-1.3, 0), "60 kN", (0, -16))],   # #6、#7
    labels={"A": (-16, -6), "B": (-16, -12), "C": (-12, 18), "D": (16, -6)},
    dims=[((0, 0), (0, 4), "4 m", -52), ((0, 0), (6, 0), "6 m", 56),
          ((6, 0), (6, 2), "2 m", 124), ((6, 2), (6, 4), "2 m", 124)],
    extra_pts=[(-0.8, 5.6), (8.9, -0.9)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 600, 480,
                          note="A、D 鉸支承；B、C 為梁柱剛接；兩個 60 kN 皆向左（C 點與右柱中點）")

FIGURES = [(fig1_problem, "下方 60 kN 位置讀錯（應在右柱中點）、水平力方向讀反")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

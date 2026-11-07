#!/usr/bin/env python3
"""SA-2016-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2016-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2016-3_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2016-3"

# ── 判讀清單 #1–#6 ──（AB 傾角考卷未標註：依圖面比例示意，取水平 5 m、垂直 5√3 m）
H_AB = 10 * math.sin(math.radians(60))
N_ = {"B": (0, 20), "C": (12, 20), "D": (12, 0), "A": (-5, 20 - H_AB)}         # #3、#4
SPEC = dict(
    nodes=N_, members=[{"ij": ("A", "B")}, {"ij": ("B", "C")}, {"ij": ("C", "D")}],   # #1
    supports=[("A", "fixed", 0), ("D", "fixed")],                             # #2
    udl=[("B", "C", 1.8, "2 kN/m")],                                          # #5
    labels={"A": (-24, -14), "B": (-16, -16), "C": (16, -16), "D": (22, -16)},
    dims=[((-5, 20 - H_AB), (0, 20), "10 m", -36), ((0, 0), (12, 0), "12 m", 46), ((12, 0), (12, 20), "20 m", 62)],
    ptexts=[((-6.4, 8.6), "AB 傾角考卷未標註（示意）", 12.5, None, "middle")],
    extra_pts=[(-9.5, 23.6), (15.4, -1.6)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 560, 600,
                          note="A、D 固定端；B、C 剛接；載重只在 BC；題給 M_{AB}、M_{BC}、M_{CD}、M_{DC} 見題目正本")

FIGURES = [(fig1_problem, "A 讀成鉸支承、把 AB 傾角當成題目給定")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

#!/usr/bin/env python3
"""SA-2002-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2002-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2002-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2002-3"

# ── 判讀清單 #1–#7（λ 以 1 個長度單位繪製）──
SPEC = dict(
    nodes={"A": (0, 0), "B": (1, 0), "C": (1, 1)},                             # #4 #5
    members=[dict(ij=("A", "B"))],                                             # #4 梁 AB（EI）
    truss=[("B", "C")],                                                        # #5 桿 BC（AE）
    joints=["B"],                                                              # #3 B 為鉸接
    supports=[("A", "fixed"), ("C", "pin", 180)],                              # #1 #2
    loads=[("B", (0, -0.32), "P", (16, 4), True)],                             # #7
    labels={"A": (-30, 0), "B": (18, 14), "C": (-30, -8)},
    mlabels=[((0.5, 0.14), "EI", None, "middle"), ((1.1, 0.5), "AE", None, "start")],
    dims=[((0, 0), (1, 0), "λ", 110), ((1, 0), (1, 1), "λ", -64)],
    extra_pts=[(-0.3, 1.25), (1.45, -0.6)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 460, 480,
                          note="A 固定端；C 鉸支承；B 為梁與桿的鉸接；梁、桿同材料，EI、AE 為常數")

FIGURES = [(fig1_problem, "C 讀成固定端、B 讀成剛接、漏掉桿的軸向變形")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

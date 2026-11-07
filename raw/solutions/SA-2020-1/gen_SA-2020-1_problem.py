#!/usr/bin/env python3
"""SA-2020-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2020-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2020-1_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_libp"))   # 本題 figs/_lib 是解析自繪圖用的舊版，題目重繪另用 _libp
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2020-1"

# ── 判讀清單 #1–#6 ──
N_ = {"a": (0, 3), "b": (4, 3), "c": (8, 0), "P": (6, 1.5)}                    # #3–#5
SPEC = dict(
    nodes=N_, members=[{"ij": ("a", "b")}, {"ij": ("b", "c")}],
    supports=[("a", "fixed"), ("c", "roller", 90)],                           # #1；#6 c 為靠右側垂直牆的滾支承（使用者確認）
    loads=[("P", (0, -1.6), "68 kN", (0, -14))],                              # #5
    labels={"a": (16, -16), "b": (0, -18), "c": (-14, 16)},
    dims=[((0, 0), (4, 0), "4 m", 40), ((4, 0), (6, 0), "2 m", 40), ((6, 0), (8, 0), "2 m", 40),
          ((8, 0), (8, 3), "3 m", 82)],
    extra_pts=[(-0.9, 4.8), (9.6, -0.8)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 600, 440,
                          note="a 固定端；c 為靠垂直牆的滾支承（只有水平反力）；68 kN 在 bc 中點；不計軸向變形")

FIGURES = [(fig1_problem, "c 讀成鉸支承、載重放在 b 點、ab／bc 長度對調")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

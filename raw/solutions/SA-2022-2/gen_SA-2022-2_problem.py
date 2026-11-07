#!/usr/bin/env python3
"""SA-2022-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2022-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2022-2_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_libp"))   # 本題 figs/_lib 是解析自繪圖用的舊版，題目重繪另用 _libp
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2022-2"

# ── 判讀清單 #1–#7 ──
N_ = {"a": (0, 0), "b": (0, 2), "c": (0, 4), "d": (4, 4), "m": (4, 6), "e": (4, 8)}   # #5
SPEC = dict(
    nodes=N_, members=[{"ij": (x, y)} for x, y in (("a", "b"), ("b", "c"), ("c", "d"), ("d", "m"), ("m", "e"))],
    supports=[("a", "pin"), ("e", "pin", 180)],                               # #1、#2：e 倒掛於頂部
    loads=[("b", (1.6, 0), "30 kN", (0, -16)), ("m", (1.6, 0), "30 kN", (0, -16))],   # #7
    labels={"a": (16, 0), "b": (16, 0), "c": (-16, -10), "d": (16, 12), "e": (16, 4)},
    dims=[((4, 0), (4, 2), "2 m", 120), ((4, 2), (4, 4), "2 m", 120), ((4, 4), (4, 6), "2 m", 120),
          ((4, 6), (4, 8), "2 m", 120), ((0, 0), (4, 0), "4 m", 54)],
    extra_pts=[(-2.4, 8.8), (5.8, -0.9)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 520, 600,
                          note="a、e 鉸支承（e 在右柱頂、倒掛）；c、d 剛接；b 為載重點；EI = 40000 kN-m^{2}")

FIGURES = [(fig1_problem, "e 讀成柱底支承、b 讀成節點或鉸")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

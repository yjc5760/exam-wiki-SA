#!/usr/bin/env python3
"""SA-2010-3：題目附圖重繪（struct-diagram 規範；2026-11-04）
題目附圖的幾何、支承、載重逐項對應題目正本 SA-2010-3-problem.md §4 判讀清單（註解中的 #n）。
用法：python3 gen_SA-2010-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from frameviz import problem_figure, solution_figure, build_frame, end_moments
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2010-3"

import math
# ── 判讀清單 #1–#5（L = 1） ──
h = math.sqrt(3) / 2
SPEC = dict(
    nodes={"A": (0, 0), "B": (0.5, h), "E": (1.0, h), "C": (1.5, h), "D": (2.0, 0)},
    members=[dict(name="AB", ij=("A", "B"), EI=1), dict(name="BE", ij=("B", "E"), EI=1),
             dict(name="EC", ij=("E", "C"), EI=1), dict(name="DC", ij=("D", "C"), EI=1)],
    supports=[("A", "fixed"), ("D", "fixed")],
    loads=[("B", (0.32, 0), "P", (-16, 0)), ("E", (0, -0.32), "2P", (22, 0))],
    labels={"A": (-26, -12), "B": (16, 20), "E": (0, 22), "C": (-16, 20), "D": (26, -12)},
    dims=[((0, -0.12), (0.5, -0.12), "L/2", 20), ((0.5, -0.12), (1.0, -0.12), "L/2", 20),
          ((1.0, -0.12), (1.5, -0.12), "L/2", 20), ((1.5, -0.12), (2.0, -0.12), "L/2", 20),
          ((2.12, 0), (2.12, h), "", 46)],
    texts=[((2.37, h / 2), "√3 L/2")])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 700, 520,
                          note="A、D 固接；AB、CD 長 L（傾角 60°）、BC 長 L、E 為中點；EI 常數")

FIGURES = [(fig1_problem, "斜柱長度與傾角、E 位置誤讀")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

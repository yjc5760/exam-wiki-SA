#!/usr/bin/env python3
"""SA-2013-3：題目附圖重繪＋變形形狀與彎矩圖（struct-diagram 規範；2026-11-04）
題目附圖的幾何、支承、載重逐項對應題目正本 SA-2013-3-problem.md §4 判讀清單（註解中的 #n）。
以 L = 1、w = 1 重算，assert 與 2026-11-04 勘誤後解析一致（M_AB = +0.1051、M_CB = −0.1283 wL²）。
用法：python3 gen_SA-2013-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from frameviz import problem_figure, solution_figure, build_frame, end_moments
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2013-3"

# ── 判讀清單 #1–#7（L = 1、w = 1） ──
SPEC = dict(
    nodes={"A": (0, 0), "B": (0, 1), "C": (1, 1), "D": (2, 0)},
    members=[dict(name="AB", ij=("A", "B"), EI=1, rel=(0, 1)),                 # #3 B 內鉸
             dict(name="BC", ij=("B", "C"), EI=2, w=1.0, thick=True),          # #6 #7
             dict(name="DC", ij=("D", "C"), EI=1)],
    supports=[("A", "fixed"), ("D", "fixed")],                                 # #1 #2
    hinges=["B"],
    udl=[("B", "C", 0.22, "w")],
    labels={"A": (20, -12), "B": (-16, -14), "C": (12, -16), "D": (-24, -8)},
    mlabels=[((-0.08, 0.5), "EI", None, "end"), ((0.5, 0.88), "2EI", None, "middle"), ((1.62, 0.62), "EI", None, "start")],
    dims=[((0, -0.18), (1, -0.18), "L", 24), ((1, -0.18), (2, -0.18), "L", 24), ((2.2, 0), (2.2, 1), "L", 30)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 620, 540,
                          note="A、D 固接；B 為內鉸（○）；C 剛接；BC 全長均布 w")

def fig2_solution():
    f = build_frame(SPEC); M = end_moments(f)
    assert abs(M["AB"][0] - 0.1051) < 1e-3 and abs(M["BC"][1] + 0.1283) < 1e-3 and abs(M["DC"][0] - 0.1384) < 1e-3
    return solution_figure(f, SPEC, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", 3.2, 0.9,
        "SA-2013-3　載重向下 → C 往左下移；BC 全跨正彎矩", "B、C 向左、C 同時下沉 0.035wL⁴/EI",
        "BC 最大正彎矩 0.197wL²（距 B 0.628L）", munit="wL²", fmt="{:.3f}", W=560, H=470,
        notes=("", "C 端為正彎矩 0.128wL²，不是負彎矩"))

FIGURES = [(fig1_problem, "B 內鉸、CD 斜桿方向與固接面誤讀"),
           (fig2_solution, "側移方向反（C 往右上）、C 端畫成負彎矩")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

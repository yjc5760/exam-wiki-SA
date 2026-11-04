#!/usr/bin/env python3
"""SA-2012-3：題目附圖重繪＋變形形狀與彎矩圖（struct-diagram 規範；2026-11-04）
題目附圖的幾何、支承、載重逐項對應題目正本 SA-2012-3-problem.md §4 判讀清單（註解中的 #n）。
以 L = 1、P = 1 重算；全部角點與中段彎矩應為 PL/2，assert 之。
用法：python3 gen_SA-2012-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from frameviz import problem_figure, solution_figure, build_frame, end_moments
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2012-3"

# ── 判讀清單 #1–#6（L = 1、P = 1） ──
SPEC = dict(
    nodes={"a": (0, 0), "b": (1, 0), "c": (3, 0), "d": (4, 0), "h": (4, 2), "g": (3, 2), "f": (1, 2), "e": (0, 2)},
    members=[dict(name=n, ij=(n[0], n[1]), EI=1) for n in ("ab", "bc", "cd", "dh", "hg", "gf", "fe", "ea")],
    supports=[("b", "pin"), ("c", "roller")],                                            # #2 #3
    loads=[("f", (0, -0.8), "P", (18, 0)), ("g", (0, -0.8), "P", (18, 0))],               # #6
    fe_loads=[("f", 0, -1, 0), ("g", 0, -1, 0)],
    labels={"a": (-16, 0), "b": (-10, -16), "c": (10, -16), "d": (16, 0), "e": (-16, 0), "f": (-12, 16), "g": (12, 16), "h": (16, 0)},
    dims=[((0, -0.75), (1, -0.75), "L", 22), ((1, -0.75), (3, -0.75), "2L", 22), ((3, -0.75), (4, -0.75), "L", 22),
          ((4.35, 0), (4.35, 2), "2L", 28)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 660, 560,
                          note="封閉框各角剛接；b 鉸支承（框身連續）、c 滾支承；EI 常數")

def fig2_solution():
    f = build_frame(SPEC); M = end_moments(f)
    assert all(abs(abs(v) - 0.5) < 1e-6 for p in M.values() for v in p)
    return solution_figure(f, SPEC, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", 0.17, 0.42,
        "SA-2012-3　封閉矩形框：各角點與中段彎矩均為 PL/2", "a、d、e、h 下沉 7PL³/12EI；f、g 下沉 7PL³/6EI",
        "反曲點在四段懸伸中點", munit="PL", fmt="{:.1f}", W=600, H=470,
        notes=("", "柱與中段為常數彎矩（剪力 0）"))

FIGURES = [(fig1_problem, "b 讀成框身內鉸、P 作用點不在支承正上方"),
           (fig2_solution, "懸伸段漏掉反曲點、中段受拉側畫反")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

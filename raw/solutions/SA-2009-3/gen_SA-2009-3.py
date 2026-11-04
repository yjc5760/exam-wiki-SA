#!/usr/bin/env python3
"""SA-2009-3：題目附圖重繪＋變形形狀與彎矩圖（struct-diagram 規範；2026-11-04）
題目附圖的幾何、支承、載重逐項對應題目正本 SA-2009-3-problem.md §4 判讀清單（註解中的 #n）。
以 L = 10 m、P = 100 kN 重算，assert 與解析一致（K_H = 240EI/13L³、柱底 275 kN-m）。
用法：python3 gen_SA-2009-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from frameviz import problem_figure, solution_figure, build_frame, end_moments
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2009-3"

# ── 判讀清單 #1–#6（L = 10 m） ──
L = 10.0
SPEC = dict(
    nodes={"a": (0, L), "b": (L, L), "c": (2*L, L), "d": (3*L, L), "e": (L, 0), "f": (2*L, 0)},
    members=[dict(name="ab", ij=("a", "b"), EI=1), dict(name="bc", ij=("b", "c"), EI=1), dict(name="cd", ij=("c", "d"), EI=1),
             dict(name="eb", ij=("e", "b"), EI=1), dict(name="fc", ij=("f", "c"), EI=1)],
    supports=[("a", "roller"), ("d", "roller"), ("e", "fixed"), ("f", "fixed")],        # #1 #2
    loads=[("a", (4.0, 0), "P", (-18, 0))],                                              # #6
    fe_loads=[("a", 100, 0, 0)],
    labels={"a": (-6, -20), "b": (-14, -16), "c": (14, -16), "d": (6, -20), "e": (-24, -2), "f": (24, -2)},
    dims=[((0, L), (L, L), "L", -46), ((L, L), (2*L, L), "L", -46), ((2*L, L), (3*L, L), "L", -46),
          ((3*L, 0), (3*L, L), "L", 40)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 800, 500,
                          note="a、d 滾支承；e、f 固接；全部構件 E、I 相同、不計軸向變形")

def fig2_solution():
    f = build_frame(SPEC); M = end_moments(f)
    assert abs(100 / f.d["a"][0] * L**3 - 240 / 13) < 1e-3 and abs(M["eb"][0] + 275) < 1e-3
    return solution_figure(f, SPEC, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", 0.00045, 0.011,
        "SA-2009-3　π 型構架側推（P = 100 kN、L = 10 m）", "b、c 同向轉動；兩柱雙曲率",
        "單位 kN·m", munit="", fmt="{:.0f}", W=620, H=440,
        notes=("", "每柱剪力 (275+225)/10 = 50 kN，合計 100 kN ✓"))

FIGURES = [(fig1_problem, "a、d 支承讀成鉸支（會多一個水平束制、側移變零）"),
           (fig2_solution, "柱底與柱頂彎矩同側、或梁 ab 端有彎矩 → 側移式或對稱關係錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

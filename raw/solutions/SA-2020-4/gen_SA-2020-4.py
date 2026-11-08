#!/usr/bin/env python3
"""SA-2020-4：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2020-4-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2020-4.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C
from probfig_ext import problem_figure_ext, spring_between
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2020-4"

# ── 判讀清單 #1–#9 ──（單位 m；連桿長度與牆寬考卷沒有標，取圖面比例示意）
LK, WW, XB = 1.55, 2.15, 9.6       # 連桿長、牆寬（示意）；(b) 圖的牆左緣 x
XW = 3.2 + LK                      # (a) 牆左緣
N_ = {"g": (0, 0), "d": (0, 3.2), "a": (0, 6.4), "h": (3.2, 0), "e": (3.2, 3.2), "b": (3.2, 6.4),   # #1 #6
      "c": (XW, 6.4), "f": (XW, 3.2)}
SPEC = dict(
    nodes=N_,
    members=[{"ij": ("g", "d")}, {"ij": ("d", "a")}, {"ij": ("h", "e")}, {"ij": ("e", "b")},          # #3 柱
             {"ij": ("a", "b"), "thick": True}, {"ij": ("d", "e"), "thick": True}],                  # #2 剛性梁
    truss=[("b", "c"), ("e", "f")], joints=["b", "c", "e", "f"],                                     # #5 連桿
    supports=[("g", "fixed"), ("h", "fixed")],                                                        # #4
    loads=[("a", (1.5, 0), "60 kN", (-30, -14)), ("d", (1.5, 0), "60 kN", (-30, -14))],               # #7
    labels={"a": (12, -16), "b": (-12, -16), "c": (-10, -16), "d": (12, -16), "e": (-12, -16), "f": (-10, -16),
            "g": (14, -14), "h": (-14, -14)},
    dims=[((XW + WW + 0.95, 0), (XW + WW + 0.95, 3.2), "3.2 m", 0), ((XW + WW + 0.95, 3.2), (XW + WW + 0.95, 6.4), "3.2 m", 0),
          ((0, 0), (3.2, 0), "3.2 m", 56)],
    extra_pts=[(-2.0, 7.4), (XB + WW + 2.6, -3.0)])

def _pre(cv, N):
    for x0 in (XW, XB):                                                                                # 剪力牆（a）（b）
        cv.polygon([(x0, 0), (x0 + WW, 0), (x0 + WW, 6.4), (x0, 6.4)], "rgba(63,74,90,0.16)", C["member"], 2.4)
        cv.line((x0 - 0.5, 0), (x0 + WW + 0.5, 0), C["member"], 2.4)
        for i in range(6):
            x = x0 - 0.3 + i * (WW + 0.6) / 5; cv.line((x, 0), (x - 0.22, -0.3), C["member"], 1.5)

def _post(cv, N):
    for (y, s) in ((6.4, "Δ_{1}, F_{1}"), (3.2, "Δ_{2}, F_{2}")):                          # #8 (b) 自由度
        cv.arrow((XB + WW + 0.15, y), (XB + WW + 1.15, y), C["deform"], 3.0, 11)
        cv.math((XB + WW + 1.15, y), s, 15, C["deform"], "start", dx=6, dy=-14)
    cv.text((XW + WW / 2, 7.0), "剪力牆", 14, C["muted"]); cv.text((XB + WW / 2, 7.0), "剪力牆", 14, C["muted"])
    cv.text((1.6, -2.7), "(a)", 16, C["text"]); cv.text((XB + WW / 2, -2.7), "(b)", 16, C["text"])

def fig1_problem():
    return problem_figure_ext(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 820, 520, pre=_pre, post=_post,
                              note=["柱 EI＝81920 kN-m²、梁 I＝∞；bc、ef 兩端鉸接連桿；柱底 g、h 視為固定（使用者確認）",
                                    "(b) 剪力牆勁度 30000 kN/m × [1, −2; −2, 6]；連桿長、牆寬考卷未標（示意）"],
                              margins=(80, 60, 50, 120))

FIGURES = [(fig1_problem, "Δ₁、Δ₂ 樓層對調、連桿當成可傳彎矩")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

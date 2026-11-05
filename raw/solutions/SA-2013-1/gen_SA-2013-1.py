#!/usr/bin/env python3
"""SA-2013-1：題目附圖重繪（struct-diagram 規範；2026-11-05）
幾何、支承、載重逐項對應題目正本 SA-2013-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2013-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2013-1"

# ── 判讀清單 #1–#7 ──
N_ = {"a": (0, 0), "l": (5, 10), "b": (0, 20), "k": (10, 20), "c": (0, 30), "d": (10, 30), "e": (20, 30),
      "f": (30, 30), "j": (30, 20), "g": (40, 30), "h": (40, 20), "i": (40, 10)}   # #1
SPEC = dict(
    nodes=N_, members=[],
    truss=[("c", "d"), ("d", "e"), ("e", "f"), ("f", "g"), ("c", "b"), ("b", "a"), ("c", "k"), ("d", "k"),
           ("b", "k"), ("k", "e"), ("b", "l"), ("l", "k"), ("a", "l"), ("e", "j"), ("f", "j"), ("j", "g"),
           ("j", "h"), ("g", "h"), ("h", "i"), ("j", "i")],                   # #2 #3（a–b 一根）
    joints=list(N_),
    supports=[("a", "pin"), ("i", "pin")],                                    # #4
    loads=[("c", (0, -5), "5 kN", (0, -14)), ("d", (0, -5), "10 kN", (0, -14)), ("e", (0, -5), "10 kN", (0, -14)),
           ("f", (0, -5), "10 kN", (0, -14)), ("g", (0, -5), "5 kN", (0, -14))],   # #6
    labels={"a": (-16, 0), "l": (14, 6), "b": (-16, 0), "k": (12, 16), "c": (-16, 8), "d": (12, 14), "e": (0, 18),
            "f": (12, 14), "j": (-14, 14), "g": (16, 8), "h": (16, 0), "i": (16, 0)},
    dims=[((0, 0), (0, 10), "10 m", -66), ((0, 10), (0, 20), "10 m", -66), ((0, 20), (0, 30), "10 m", -66),
          ((0, 0), (5, 0), "5 m", 58), ((5, 0), (10, 0), "5 m", 58), ((10, 0), (20, 0), "10 m", 58),
          ((20, 0), (30, 0), "10 m", 58), ((30, 0), (40, 0), "10 m", 58)],
    extra_pts=[(-4, 30), (42, 0)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 680, 620,
                          note="a、i 鉸支承（i 高 10 m）；a–b 為一根連續豎桿，l 高度處沒有節點")

FIGURES = [(fig1_problem, "i 讀成滾支承、a–b 中段多一個節點、i 高度讀錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

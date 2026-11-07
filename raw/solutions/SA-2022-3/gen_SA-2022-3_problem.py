#!/usr/bin/env python3
"""SA-2022-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2022-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2022-3_problem.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2022-3"

# ── 判讀清單 ──
B_ = {i: (3 * i, 0) for i in range(11)}; T_ = {i: (3 * i, 4) for i in range(1, 10)}   # #1、#2
NAME = {("B", 0): "a", ("B", 2): "m", ("B", 3): "n", ("B", 4): "b", ("B", 6): "c", ("B", 7): "d", ("B", 10): "e", ("T", 2): "k"}
nm = lambda s, i: NAME.get((s, i), f"{s}{i}")
N_ = {nm("B", i): p for i, p in B_.items()}; N_.update({nm("T", i): p for i, p in T_.items()})
TR = [(nm("B", i), nm("B", i + 1)) for i in range(10)]                              # 下弦
TR += [(nm("T", i), nm("T", i + 1)) for i in range(1, 7)] + [(nm("T", 8), nm("T", 9))]   # #2 上弦兩段，21–24 無
TR += [(nm("T", i), nm("B", i)) for i in range(1, 10)]                              # #3 豎桿
TR += [(nm("B", 0), nm("T", 1)), (nm("T", 2), nm("B", 3)), (nm("T", 6), nm("B", 7)), (nm("B", 7), nm("T", 8)), (nm("T", 9), nm("B", 10))]  # #4 單斜桿
for p in (1, 3, 5, 8):                                                             # #4 X 形格（3–6、9–12、15–18、24–27）
    TR += [(nm("T", p), nm("B", p + 1)), (nm("B", p), nm("T", p + 1))]
assert len(TR) == 39                                                               # #7
SPEC = dict(
    nodes=N_, members=[], truss=TR, joints=list(N_),
    supports=[("a", "roller"), ("b", "roller"), ("c", "roller"), ("e", "pin")],      # #6
    labels={"a": (-16, -12), "m": (0, 22), "n": (0, 22), "b": (13, -13), "c": (13, -13), "d": (0, 22), "e": (16, -12), "k": (0, -18)},
    dims=[((0, 0), (30, 0), "10@3 m = 30 m", 66), ((30, 0), (30, 4), "4 m", 48)],
    ptexts=[((13.5, 2.0), "無斜桿", 12, None, "middle")],                             # #5
    extra_pts=[(-1, 4.6), (31.5, -1)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 1000, 400,
                          note="a、b、c 滾支承、e 鉸支承；12–15 格無斜桿、21–24 無上弦；mn 為下弦 6–9、nk 為 k(6,4)–n(9,0) 斜桿")

FIGURES = [(fig1_problem, "6–9 格讀成 X 形、12–15 格補上斜桿、b 讀成內鉸")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

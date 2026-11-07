#!/usr/bin/env python3
"""SA-2007-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2007-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2007-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2007-3"

# ── 判讀清單 ──
N_ = {"A": (0, 0), "B": (48, 0), "E": (0, 17), "F": (12, 17), "G": (24, 17), "H": (36, 17), "I": (48, 17),
      "C": (12, 12), "D": (36, 12)}                                                # #1
X1 = 55.0; AX = [X1, X1 + 2.4, X1 + 3.9, X1 + 5.4]                                 # #6
T_ = {f"T{i+1}": (x, 17.0) for i, x in enumerate(AX)}
SPEC = dict(
    nodes={**N_, **T_, "R": (53.6, 19.4)}, members=[],
    truss=[("E", "F"), ("F", "G"), ("G", "H"), ("H", "I"), ("A", "E"), ("I", "B"), ("F", "C"), ("H", "D"),
           ("A", "C"), ("E", "C"), ("C", "G"), ("G", "D"), ("D", "I"), ("D", "B")],   # #2、#3
    joints=list(N_),
    supports=[("A", "pin"), ("B", "pin")],                                          # #4
    loads=[("T1", (0, -2.6), "", (0, 0)), ("T2", (0, -2.6), "", (0, 0)),
           ("T3", (0, -2.6), "", (0, 0)), ("T4", (0, -2.6), "", (0, 0)),     # #6
           ("R", (-2.4, 0), "", (0, 0), True)],                                     # #7
    labels={"A": (18, 2), "B": (-18, 2), "E": (0, -18), "F": (0, -18), "G": (0, -18), "H": (0, -18), "I": (0, -18),
            "C": (16, 16), "D": (-16, 16)},
    dims=[((0, 0), (12, 0), "12 m", 60), ((12, 0), (24, 0), "12 m", 60), ((24, 0), (36, 0), "12 m", 60),
          ((36, 0), (48, 0), "12 m", 60), ((0, 0), (0, 12), "12 m", -50), ((0, 12), (0, 17), "5 m", -50),
          ((AX[0], 17), (AX[1], 17), "", 26), ((AX[1], 17), (AX[2], 17), "", 26), ((AX[2], 17), (AX[3], 17), "", 26)],
    ptexts=[((X1 + 2.7, 24.6), "軸 1–4：20、40、40、40 kN", 12.5, None, "middle"), ((X1 + 2.7, 22.6), "軸距 2.4、1.5、1.5 m（軸 1 在前）", 12.5, None, "middle")],
    extra_pts=[(-5, 17), (65, 0), (52, 26)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 1000, 560,
                          note="A、B 皆鉸支承；上弦 E–I 在 G 連續；C、D 在 F、H 正下方；卡車行駛於上弦、由右往左")

FIGURES = [(fig1_problem, "A 或 B 讀成滾支承、C／D 高程讀錯、G 讀成斷開")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

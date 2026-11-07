#!/usr/bin/env python3
"""SA-2004-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2004-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2004-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2004-2"

# ── 判讀清單 ──
N_ = {"a": (0, 0), "b": (10, 0), "c": (20, 0), "d": (30, 0), "e": (40, 0),
      "B": (10, 10), "C": (20, 10), "D": (30, 10)}                                 # #1
X1 = 47.0; AX = [X1, X1 + 2.4, X1 + 3.9, X1 + 5.4]                                 # #8 軸距 2.4、1.5、1.5 m
T_ = {f"T{i+1}": (x, 2.0) for i, x in enumerate(AX)}
SPEC = dict(
    nodes={**N_, **T_, "R": (45.6, 4.4)}, members=[],
    truss=[("a", "b"), ("b", "c"), ("c", "d"), ("d", "e"), ("B", "C"), ("C", "D"), ("a", "B"), ("D", "e"),
           ("B", "b"), ("C", "c"), ("D", "d"), ("B", "c"), ("c", "D")],             # #2、#3
    joints=list(N_),
    supports=[("a", "pin"), ("e", "roller")],                                       # #4、#5
    loads=[("T1", (0, -2.6), "", (0, 0)), ("T2", (0, -2.6), "", (0, 0)),
           ("T3", (0, -2.6), "", (0, 0)), ("T4", (0, -2.6), "", (0, 0)),     # #7
           ("R", (-2.4, 0), "", (0, 0), True)],                                     # #9 行駛方向（向左）
    labels={"a": (-16, -12), "b": (0, 20), "c": (0, 20), "d": (0, 20), "e": (16, -12),
            "B": (0, -18), "C": (0, -18), "D": (0, -18)},
    dims=[((0, 0), (10, 0), "10 m", 62), ((10, 0), (20, 0), "10 m", 62), ((20, 0), (30, 0), "10 m", 62),
          ((30, 0), (40, 0), "10 m", 62), ((0, 0), (0, 10), "10 m", -48),
          ((AX[0], 2), (AX[1], 2), "", 26), ((AX[1], 2), (AX[2], 2), "", 26), ((AX[2], 2), (AX[3], 2), "", 26)],
    ptexts=[((X1 + 2.7, 9.2), "軸 1–4：20、40、40、40 kN", 12.5, None, "middle"), ((X1 + 2.7, 7.6), "軸距 2.4、1.5、1.5 m（軸 1 在前）", 12.5, None, "middle")],
    extra_pts=[(-4, 10), (57, -2), (45, 10)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 1000, 470,
                          note="a 鉸支承、e 滾支承；B、C、D 在 b、c、d 正上方；卡車由右往左行駛")

FIGURES = [(fig1_problem, "e 讀成鉸支承、斜桿 Bc／cD 方向讀反、軸距或軸重順序抄錯")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

#!/usr/bin/env python3
"""SA-2005-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2005-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2005-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2005-1"

# ── 判讀清單 #1–#7 ──
N_ = {"B": (0, 4), "A": (8, 4), "C": (4, 0)}                                   # #4
SPEC = dict(
    nodes=N_, members=[{"ij": ("B", "A")}, {"ij": ("B", "C")}],               # #1
    supports=[("A", "fixed"), ("C", "roller")],                               # #2、#3
    loads=[("B", (0, -1.3), "10 N", (0, -14))],                               # #5
    labels={"B": (-18, -6), "A": (20, -16), "C": (22, 0)},
    dims=[((0, 0), (4, 0), "4 m", 46), ((4, 0), (8, 0), "4 m", 46), ((0, 0), (0, 4), "4 m", -54)],
    extra_pts=[(-0.6, 5.6), (8.8, -0.9)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 460,
                          note="A 固定端；C 滾支承（垂直反力）；兩桿皆為 20 cm 方形斷面，E = 10^{6} N/cm^{2}")

FIGURES = [(fig1_problem, "C 讀成鉸支承、BC 投影讀錯、A 讀成在 B 左側")]

def _auto_scales(f, span, dfrac=0.12, mfrac=0.17):
    """依解出的位移與彎矩自動取放大倍率（圖形隨輸入改變，不寫死）。"""
    from frameviz import member_moment
    dmax = max(max(abs(v[0]), abs(v[1])) for v in f.d.values()) or 1
    mmax = max(abs(member_moment(f, m, k/40)) for m in f.M for k in range(41)) or 1
    return dfrac*span/dmax, mfrac*span/mmax

# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2005-1.md §4 Step 4–5 ──
from frameviz import solution_figure, build_frame, end_moments
RC = 10*(2 - math.sqrt(2))                     # §4 Step 4：R_C = 10(2−√2) N
SOL = dict(nodes=N_, members=[dict(name="BA", ij=("B", "A"), EI=1), dict(name="CB", ij=("C", "B"), EI=1)],
           supports=[("A", "fixed"), ("C", "roller")], fe_loads=[("B", 0, -10, 0)])

def fig2_solution():
    f = build_frame(SOL); M = end_moments(f)
    assert abs(f.R["C"][1] - RC) < 1e-4                      # §4：R_C（EA = 10^8·EI 的數值誤差約 10^-6）
    assert abs(abs(M["BA"][1]) - 40*math.sqrt(2)) < 1e-4     # §4：A 端 40√2 N·m
    assert abs(abs(M["BA"][0]) - 40*(2 - math.sqrt(2))) < 1e-4
    ds, ms = _auto_scales(f, 8)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2005-1 變形形狀與彎矩圖（單位 N·m）", "C 滾支水平滑動；B 下沉並轉動",
        "BA 全長上緣受拉；BC 外側受拉", fmt="{:.2f}", W=560, H=460,
        notes=("", "R_C = 10(2 − √2) = 5.86 N"))

FIGURES.append((fig2_solution, "BA 在 x = 4 處分段、BC 受拉側畫反"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

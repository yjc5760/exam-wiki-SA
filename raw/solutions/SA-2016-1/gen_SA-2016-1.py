#!/usr/bin/env python3
"""SA-2016-1：題目附圖重繪（struct-diagram 規範；2026-11-05）
幾何、支承、載重逐項對應題目正本 SA-2016-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2016-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2016-1"

# ── 判讀清單 #1–#7 ──
SPEC = dict(
    nodes={"A": (0, 0), "B": (0, 2), "C": (2, 2), "D": (4, 2), "E": (4, 0)},   # #5
    members=[dict(ij=("A", "B")), dict(ij=("B", "D")), dict(ij=("E", "D"))],
    supports=[("A", "pin"), ("E", "fixed")],                                  # #1 #2
    hinges=["C"],                                                             # #3
    loads=[("D", (1.0, 0), "50 kN", (34, 0), True)],                          # #6
    labels={"A": (-18, 0), "B": (-14, -14), "C": (0, -18), "D": (14, -14), "E": (24, -12)},
    dims=[((0, 0), (0, 2), "2 m", -60), ((0, 0), (2, 0), "2 m", 62), ((2, 0), (4, 0), "2 m", 62)],
    extra_pts=[(-0.6, 2), (5.6, 2), (0, -0.5)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 620, 440,
                          note="A 鉸支承；E 固定端（柱底直接接剖線，無三角形）；C 為梁中點內鉸；EI 為常數")

FIGURES = [(fig1_problem, "E 讀成鉸支承（本題舊版解析）、C 漏讀內鉸")]

def _auto_scales(f, span, dfrac=0.12, mfrac=0.17):
    """依解出的位移與彎矩自動取放大倍率（圖形隨輸入改變，不寫死）。"""
    from frameviz import member_moment
    dmax = max(max(abs(v[0]), abs(v[1])) for v in f.d.values()) or 1
    mmax = max(abs(member_moment(f, m, k/40)) for m in f.M for k in range(41)) or 1
    return dfrac*span/dmax, mfrac*span/mmax

def _frame_tools():
    """回傳 frame2d.Frame。並對 frameviz 打兩個本地補丁：
    ① supports 可寫 (節點, 種類, 角度)，牆上鉸支承才畫得對；② 兩端皆鉸、無跨內載重的二力桿，變形畫成直線。"""
    import frameviz
    from frame2d import Frame
    if not getattr(frameviz, "_patch_U22", False):
        _ds, _df = frameviz.draw_supports, frameviz.deformed
        def draw_supports(cv, N, members, supports, size=18):
            _ds(cv, N, members, [s for s in supports if len(s) == 2], size)
            for nd, kind, ang in [s for s in supports if len(s) == 3]:
                cv.support(N[nd], kind, ang, size*0.85)
        def deformed(f, m, scale, n=40):
            if tuple(m["rel"]) == (1, 1) and m["w"] == 0:
                (x0, y0), (x1, y1) = f.N[m["i"]], f.N[m["j"]]; ui, uj = f.d[m["i"]], f.d[m["j"]]
                return [(x0 + (x1-x0)*k/n + (ui[0] + (uj[0]-ui[0])*k/n)*scale,
                         y0 + (y1-y0)*k/n + (ui[1] + (uj[1]-ui[1])*k/n)*scale) for k in range(n + 1)]
            return _df(f, m, scale, n)
        frameviz.draw_supports, frameviz.deformed, frameviz._patch_U22 = draw_supports, deformed, True
    return Frame

# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2016-1.md §4 Step 5–7 ──
from frameviz import solution_figure, end_moments, inflections
SOL = dict(nodes=SPEC["nodes"], supports=[("A", "pin"), ("E", "fixed")], hinges=["C"])

def fig2_solution():
    Frame = _frame_tools(); f = Frame()
    for n, p in SOL["nodes"].items(): f.node(n, *p)
    f.support("A", 1, 1, 0); f.support("E", 1, 1, 1)
    f.member("AB", "A", "B", 1.0); f.member("BC", "B", "C", 1.0, rel=(0, 1))     # C 內鉸
    f.member("CD", "C", "D", 1.0); f.member("ED", "E", "D", 1.0)
    f.load("D", 50, 0, 0); f.solve(); M = end_moments(f)
    assert abs(f.R["A"][0] + 12.5) < 1e-6 and abs(f.R["A"][1] + 12.5) < 1e-6      # §4：A_x = A_y = −12.5
    assert abs(f.R["E"][0] + 37.5) < 1e-6 and abs(f.R["E"][1] - 12.5) < 1e-6      # E_x = −37.5、E_y = +12.5
    assert abs(f.R["E"][2] - 50) < 1e-6                                          # M_E = 50 逆時針
    assert abs(abs(M["AB"][1]) - 25) < 1e-6 and abs(abs(M["CD"][1]) - 25) < 1e-6   # M_B = M_D = 25
    xi = inflections(f, next(m for m in f.M if m["name"] == "ED"))
    assert len(xi) == 1 and abs(xi[0] - 2/3) < 1e-2                              # 反曲點距 E 4/3 m
    ds, ms = _auto_scales(f, 4)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2016-1 變形形狀與彎矩圖（單位 kN·m）", "D 向右側移；C 內鉸兩側斜率不連續",
        "B：柱右、梁下受拉；D：梁上、柱右受拉；E：柱左受拉", fmt="{:.1f}", W=560, H=470,
        notes=("", "DE 柱反曲點距 D 0.67 m；A 反力 12.5 ←、12.5 ↓"))

FIGURES.append((fig2_solution, "B、D、E 受拉側畫反；DE 柱漏畫反曲點；E 當成鉸支承（M_E = 0）"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

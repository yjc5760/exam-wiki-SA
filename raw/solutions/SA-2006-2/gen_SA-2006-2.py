#!/usr/bin/env python3
"""SA-2006-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2006-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2006-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2006-2"

# ── 判讀清單 #1–#8 ──
SPEC = dict(
    nodes={"A": (0, 0), "B": (9, 0), "C": (16, 0), "D": (0, 12)},             # #2 #4 #5
    members=[dict(ij=("A", "C"))],                                             # #6 梁 AC 在 B 連續
    truss=[("D", "B"), ("D", "C")],                                            # #7 連桿
    joints=["B", "C"],                                                         # #3
    supports=[("A", "pin", -90), ("D", "pin", -90)],                           # #1 #2 鉸接於左側牆
    udl=[("A", "C", 1.6, "1 kN/m")],                                           # #8 全長
    labels={"A": (-12, -22), "B": (0, 24), "C": (14, 22), "D": (18, -16)},
    dims=[((0, 0), (9, 0), "9 m", 70), ((9, 0), (16, 0), "7 m", 70), ((0, 0), (0, 12), "12 m", -80)],
    extra_pts=[(-2.2, 12.6), (17, -1.6)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 560,
                          note="A、D 鉸接於同一面牆（D 在 A 正上方 12 m）；梁 AC 在 B 連續，B、C 圓圈為連桿鉸")

FIGURES = [(fig1_problem, "B 讀成梁內鉸（變靜定）、D 不在 A 正上方、均佈只算到 B")]

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

# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2006-2.md §4（T_DB = 86990/7917、T_DC = 80635/15834）──
from frameviz import solution_figure
SOL = dict(nodes=SPEC["nodes"], supports=[("A", "pin", -90), ("D", "pin", -90)])

def fig2_solution():
    Frame = _frame_tools(); f = Frame()
    for n, p in SOL["nodes"].items(): f.node(n, *p)
    f.support("A", 1, 1, 0); f.support("D", 1, 1, 0)
    f.member("AB", "A", "B", 1.0, w=1); f.member("BC", "B", "C", 1.0, w=1)       # 梁在 B 連續；不計軸向
    f.member("DB", "D", "B", 1e-6, rel=(1, 1), EA=1.0); f.member("DC", "D", "C", 1e-6, rel=(1, 1), EA=1.0)
    f.solve()
    assert abs(-f.end["DB"][0] - 86990/7917) < 1e-6                              # T_DB = 10.988 kN
    assert abs(-f.end["DC"][0] - 80635/15834) < 1e-6                             # T_DC = 5.093 kN
    ds, ms = _auto_scales(f, 16)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2006-2 變形形狀與彎矩圖（單位 kN·m）", "兩連桿皆受拉伸長；梁在 B 連續",
        "B 處負彎矩（上緣受拉），不是內鉸", fmt="{:.2f}", W=600, H=470,
        notes=("", "連桿拉力：DB 10.99 kN、DC 5.093 kN"))

FIGURES.append((fig2_solution, "B 當成梁內鉸（結構變靜定）；兩根連桿拉力對調"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

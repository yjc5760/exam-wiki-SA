#!/usr/bin/env python3
"""SA-2009-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2009-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2009-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2009-2"

# ── 判讀清單 #1–#7（連桿 100 m 未按比例，以 8 個長度單位繪製）──
LINK = 8.0
NODES = {"c": (0, 0), "b": (0, 6), "a": (0, 10), "d": (LINK, 10)}            # #5
for k in range(11):                                                          # #7 載重箭頭位置（0–10 m 每 1 m）
    NODES[f"w{k}"] = (0, k)
SPEC = dict(
    nodes=NODES,
    members=[dict(ij=("c", "a"))],                                             # 梁 ac
    truss=[("a", "d")],                                                        # #6 水平連桿
    joints=["a"],                                                              # #3
    supports=[("c", "fixed"), ("d", "pin", 90)],                               # #1 #2
    loads=[(f"w{k}", (-1.3, 0), "", (0, 0), True) for k in range(11)],        # #7 向左，背離 d
    labels={"a": (-14, -18), "b": (16, 0), "c": (16, 10), "d": (-12, 26)},
    mlabels=[((-1.9, 5), "1 kN/m", C["load"], "end")],
    dims=[((0, 0), (0, 10), "10 m", -150), ((0, 0), (0, 6), "6 m", 70), ((0, 10), (LINK, 10), "100 m", -50)],
    extra_pts=[(-4.4, 0), (LINK + 1.2, 11.6), (0, -0.8)])

def fig1_problem():
    cvpath = problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 600, 560,
                            note="c 固定端；a 為連桿鉸；b 為梁上一點（非鉸）；連桿長 100 m（圖未按比例）")
    return cvpath

FIGURES = [(fig1_problem, "載重方向讀反、b 讀成鉸、b 高度量錯")]

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

# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2009-2.md §4.3–4.4（X_1 = 75/26、Δ_b = −1161/6500 m）──
# 連桿 100 m 未按比例：沿用題目重繪圖的 LINK 長度，EA 等比縮小，使 AE/L = 1000/100 = 10 kN/m 不變。
from frameviz import solution_figure
SOL = dict(nodes={"c": (0, 0), "b": (0, 6), "a": (0, 10), "d": (LINK, 10)}, supports=[("c", "fixed"), ("d", "pin", 90)])

def fig2_solution():
    Frame = _frame_tools(); f = Frame()
    for n, p in SOL["nodes"].items(): f.node(n, *p)
    f.support("c", 1, 1, 1); f.support("d", 1, 1, 0)
    f.member("cb", "c", "b", 1000, w=-1); f.member("ba", "b", "a", 1000, w=-1)   # 局部 −y＝右，w = −1 即向左 1 kN/m
    f.member("ad", "a", "d", 1e-6, rel=(1, 1), EA=1000*LINK/100)                  # 等效：AE/L = 10 kN/m
    f.solve()
    X1 = 75/26
    assert abs(-f.end["ad"][0] - X1) < 1e-9                                       # 連桿拉力 X_1 = 75/26
    assert abs(f.d["b"][0] + 1161/6500) < 1e-9                                    # Δ_b = 0.1786 m 向左
    assert abs(f.d["a"][0] + X1/10) < 1e-9                                        # a 向左 = 連桿伸長 X_1/10
    ds, ms = _auto_scales(f, 10)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2009-2 變形形狀與彎矩圖（單位 kN·m）", "Δb = 0.1786 m 向左；連桿未按比例（AE/L = 10 kN/m 不變）",
        "c 端受彎最大；a 端連桿只受軸力", fmt="{:.2f}", W=520, H=480,
        notes=("", "連桿拉力 X1 = 75/26 = 2.885 kN"))

FIGURES.append((fig2_solution, "b 點位移方向畫反（向右）；連桿當成受壓"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

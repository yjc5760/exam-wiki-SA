#!/usr/bin/env python3
"""SA-2014-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2014-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2014-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2014-2"

# ── 判讀清單 #1–#7 ──
SPEC = dict(
    nodes={"A": (0, 0), "D": (6, 0), "B": (12, 0), "C": (0, 4.5)},            # #3 #5
    members=[dict(ij=("A", "B"))],                                             # 梁 AB 在 D 連續（#4）
    truss=[("C", "D")],                                                        # #6 斜桿 CD（7.5 m）
    joints=["D"],                                                              # #4 外部鉸接
    supports=[("A", "fixed"), ("B", "roller"), ("C", "pin", -90)],            # #1 #2 #3
    udl=[("A", "B", 1.3, "8 kN/m")],                     # #7
    mlabels=[((-2.55, 2.25), "4.5 m", C["dim"], "end")],
    labels={"A": (-12, 24), "B": (16, -14), "C": (10, -18), "D": (0, 24)},
    dims=[((0, 0), (6, 0), "6 m", 74), ((6, 0), (12, 0), "6 m", 74), ((0, 0), (0, 4.5), "", -60)],
    extra_pts=[(-3.6, 4.9), (13, -1.4)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 460,
                          note="C 在 A 正上方 4.5 m、D 在梁中點：CD 為斜桿，長 √(6²+4.5²) = 7.5 m；8 kN/m 依題文（考卷附圖未畫載重）")

FIGURES = [(fig1_problem, "CD 讀成垂直桿 4.5 m（本題舊版解析）、載重只算半跨")]

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

# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2014-2.md §4（T = 34560/503、R_B = 11628/503、M_A = −25776/503）──
from frameviz import solution_figure, end_moments, member_moment
SOL = dict(nodes=SPEC["nodes"], supports=[("A", "fixed"), ("B", "roller"), ("C", "pin", -90)])

def fig2_solution():
    Frame = _frame_tools(); f = Frame()
    for n, p in SOL["nodes"].items(): f.node(n, *p)
    f.support("A", 1, 1, 1); f.support("B", 0, 1, 0); f.support("C", 1, 1, 0)
    f.member("AD", "A", "D", 1e4, w=8); f.member("DB", "D", "B", 1e4, w=8)      # 梁軸向不計（frame2d 預設 EA→∞）
    f.member("CD", "C", "D", 1e-6, rel=(1, 1), EA=4e4)                            # 斜桿 CD，7.5 m
    f.solve(); M = end_moments(f)
    assert abs(-f.end["CD"][0] - 34560/503) < 1e-6                                # T = 68.71 kN（拉）
    assert abs(f.R["B"][1] - 11628/503) < 1e-6                                    # R_B = 23.12 kN
    assert abs(M["AD"][0] + 25776/503) < 1e-6 or abs(abs(M["AD"][0]) - 25776/503) < 1e-6   # |M_A| = 51.24
    ad = next(m for m in f.M if m["name"] == "AD"); db = next(m for m in f.M if m["name"] == "DB")
    assert abs(member_moment(f, ad, 3.957/6) - 11.39) < 0.01                     # §4：x = 3.957 m，+11.39
    assert abs(member_moment(f, db, (9.110 - 6)/6) - 33.40) < 0.01               # §4：x = 9.110 m，+33.40
    ds, ms = _auto_scales(f, 12)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2014-2 變形形狀與彎矩圖（單位 kN·m）", "D 下沉、斜桿 CD 受拉伸長；A 固接不轉",
        "|M|max = 51.24 在 A（上緣受拉）", fmt="{:.1f}", W=600, H=440, skip_mark=(("AD", 1.0), ("DB", 0.0)),
        notes=("", "正彎矩：AD 段 11.39（x = 3.96 m）、DB 段 33.40（x = 9.11 m）"), extra_pts_m=[(-0.8, 5.2)])

FIGURES.append((fig2_solution, "CD 畫成垂直桿；最大彎矩放在跨中（實為固接端 A）；漏掉 AD 段兩個、DB 段一個反曲點"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

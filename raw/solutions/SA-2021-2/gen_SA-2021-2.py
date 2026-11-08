#!/usr/bin/env python3
"""SA-2021-2：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2021-2-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2021-2.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2021-2"

# ── 判讀清單 #1–#7 ──
N_ = {"a": (0, 3), "b": (3, 3), "e": (9, 3), "f": (12, 3), "c": (3, 0), "d": (9, 0)}   # #5
SPEC = dict(
    nodes=N_, members=[{"ij": (x, y)} for x, y in (("a", "b"), ("b", "e"), ("e", "f"), ("b", "c"), ("e", "d"), ("c", "d"))],
    supports=[("a", "roller"), ("f", "roller"), ("d", "roller"), ("c", "pin")],   # #1–#3
    loads=[("f", (1.6, 0), "24 kN", (24, -14), True)],                        # #7
    labels={"a": (0, -18), "b": (0, -18), "e": (0, -18), "f": (-4, -18), "c": (-16, -10), "d": (16, -10)},
    dims=[((0, 0), (3, 0), "3 m", 56), ((3, 0), (9, 0), "6 m", 56), ((9, 0), (12, 0), "3 m", 56), ((0, 0), (0, 3), "3 m", -48)],
    extra_pts=[(-0.9, 4.0), (14.4, -0.9)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 660, 400,
                          note="a、d、f 滾支承；c 鉸支承；框 b–e–d–c 各角剛接；EI = 20000 kN-m^{2}；不計軸向變形")

FIGURES = [(fig1_problem, "c、d 支承型式對調、把 c、d 當成桿件之間的鉸")]

def _auto_scales(f, span, dfrac=0.12, mfrac=0.17):
    """依解出的位移與彎矩自動取放大倍率（圖形隨輸入改變，不寫死）。"""
    from frameviz import member_moment
    dmax = max(max(abs(v[0]), abs(v[1])) for v in f.d.values()) or 1
    mmax = max(abs(member_moment(f, m, k/40)) for m in f.M for k in range(41)) or 1
    return dfrac*span/dmax, mfrac*span/mmax

# ── 解題圖（階段 E，2026-11-08）：數值由勁度法重解，與 SA-2021-2.md §4 Step 4–6 對照（assert）──
#    框角 b、e、c、d 剛接（題目正本判讀 #4）；EIθ_b = 10、EIφ = 16、EIΔ = 66（EI = 20000）
#    桿端（順時針為正）：M_ba = M_be = +10、M_bc = −20、M_cb = −16、M_cd = +16
SOL = dict(nodes=N_, supports=[("a", "roller"), ("f", "roller"), ("d", "roller"), ("c", "pin")])

def _solve():
    from frame2d import Frame
    f = Frame(); EI = 20000.0
    for n, p in N_.items(): f.node(n, *p)
    f.support("a", 0, 1, 0); f.support("f", 0, 1, 0); f.support("d", 0, 1, 0); f.support("c", 1, 1, 0)
    for nm, i, j in (("ab", "a", "b"), ("be", "b", "e"), ("ef", "e", "f"),
                     ("bc", "b", "c"), ("ed", "e", "d"), ("cd", "c", "d")):
        f.member(nm, i, j, EI)                                     # 全部剛接；不計軸向
    f.load("f", fx=24)
    f.solve()
    cw = lambda nm: (-f.end[nm][2], -f.end[nm][5])
    assert abs(f.d["b"][0] - 66/EI) < 1e-9 and abs(-f.d["b"][2] - 10/EI) < 1e-9          # Δ_b →、θ_b 順時針
    assert abs(-f.d["c"][2] - 16/EI) < 1e-9                                                # 柱底 θ_c 順時針（≠ 0）
    assert all(abs(a - b) < 1e-6 for a, b in zip(cw("ab") + cw("be") + cw("bc") + cw("cd"),
                                                   (0, 10, 10, 10, -20, -16, 16, 16)))
    return f

def fig2_solution():
    from beamfig import frame_figure
    f = _solve()
    # 梁 abef 的值另見圖 3；本圖只標柱與下梁（位置依彎矩尖端：柱頂畫在框內側、柱底畫在框外側）
    L = [("bc", 0.0, 0, 22), ("ed", 0.0, -8, -16), ("bc", 1.0, -16, 16), ("ed", 1.0, -14, 18),
         ("cd", 0.0, 18, 16), ("cd", 1.0, -20, -12)]
    return frame_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg",
        "圖 2　SA-2021-2 變形形狀與彎矩圖（單位 kN-m）",
        "上梁右移 3.30 mm；柱底隨 cd 梁轉動，柱為雙曲率",
        "柱底 16 ≠ 0：框角剛接，cd 梁抗彎", L, fmt="{:.0f}", W=560, H=450,
        dlabels=[("b", "Δb = 3.30 mm →", 0, -26)],
        notes=("θb = 0.0005 rad、θc = 0.0008 rad（皆順時針）", "柱頂 20、柱底 16、cd 兩端 16；梁 abef 數值見圖 3"))

def fig3_beam():
    from beamfig import beam_strip
    f = _solve()
    def extra(_a, b):
        for x, lab in ((3, "b"), (9, "e")):
            b.text_px(b.X(x) - 12, b.Y(3) + 26, f"{lab} 點跳 20 ＝ 柱頂 |M| 20", 12.5, C["muted"], anchor="end")
    return beam_strip(f, ["ab", "be", "ef"], f"{OUT}/{TAG}-fig-3-beam-bmd.svg",
        "圖 3　SA-2021-2 梁 abef 彎矩圖：b、e 兩側分開標示", W=900, H2=380, yc=0.46, show_def=False,
        supports=[("a", "roller"), ("f", "roller")],
        mlabels=[("ab", 1.0, "L", True), ("be", 0.0, "R", True), ("be", 1.0, "L", True), ("ef", 0.0, "R", True)],
        sub_bmd="同一個「順時針 +10」：在 ab 右端是上緣受拉，在 be 左端是下緣受拉",
        note="be 中點為反曲點（○）；全梁無跨內載重，各段皆為直線、對中點反對稱", extra=extra)

FIGURES += [(fig2_solution, "把 c、d 當柱底鉸（柱底 M = 0、柱單曲率、Δ = 8.1 mm）"),
            (fig3_beam, "把 b、e 處畫成連續平滑、或把四個梁端的受拉側全部標反")]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

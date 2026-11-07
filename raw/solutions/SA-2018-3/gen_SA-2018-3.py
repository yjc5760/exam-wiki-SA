#!/usr/bin/env python3
"""SA-2018-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2018-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2018-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2018-3"

# ── 補畫 probfig 沒有的元素（儲存前注入；只影響本腳本） ──
_save = structdraw.Canvas.save
def _hooked(extra):
    def save(self, path):
        extra(self); structdraw.Canvas.save = _save
        return _save(self, path)
    return save

# ── 判讀清單 #1–#6 ──
N_ = {"A": (0, 5), "B": (5, 5), "C": (10, 5), "D": (15, 5), "G": (10, 0), "E": (0, 0), "F": (5, 0)}   # #1、#4
SPEC = dict(
    nodes=N_, members=[{"ij": (a, b)} for a, b in (("A", "B"), ("B", "C"), ("C", "D"), ("C", "G"))],   # #1、#2
    supports=[("G", "fixed"), ("E", "fixed", 0), ("F", "fixed", 0)],          # #2、#4
    loads=[("D", (0, -1.8), "100 kN", (0, -14))],                             # #5
    labels={"A": (-14, -16), "B": (0, -18), "C": (-14, -16), "D": (14, -16), "E": (-22, -16), "F": (-22, -16), "G": (22, -16)},
    dims=[((0, 5), (5, 5), "5 m", -78), ((5, 5), (10, 5), "5 m", -78), ((10, 5), (15, 5), "5 m", -78),
          ((15, 0), (15, 5), "5 m", 56)],
    extra_pts=[(-1.0, 7.6), (16.6, -1.0)])

def _cables(cv):                                                              # #3：纜索（細虛線，只受拉）
    for a, b in (("A", "E"), ("B", "F")):
        (x0, y0), (x1, y1) = cv.P(N_[a]), cv.P(N_[b])
        cv.parts.append(f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" stroke="{C["member"]}" stroke-width="2.4" stroke-dasharray="9 6"/>')

def fig1_problem():
    structdraw.Canvas.save = _hooked(_cables)
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 460,
                          note="粗實線為梁柱（EI = 1000 kN-m^{2}），G 固定；虛線為只受拉纜索（EA = 500 kN）")

FIGURES = [(fig1_problem, "纜索當成可受壓的桿件、柱 CG 位置讀錯")]

def _auto_scales(f, span, dfrac=0.12, mfrac=0.17):
    """依解出的位移與彎矩自動取放大倍率（圖形隨輸入改變，不寫死）。"""
    from frameviz import member_moment
    dmax = max(max(abs(v[0]), abs(v[1])) for v in f.d.values()) or 1
    mmax = max(abs(member_moment(f, m, k/40)) for m in f.M for k in range(41)) or 1
    return dfrac*span/dmax, mfrac*span/mmax

# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2018-3.md §2（X_2 = 3750/53 kN、AE 鬆弛）──
from frameviz import solution_figure, build_frame, end_moments
T_BF = 3750/53                                   # §2.2（AE 鬆弛，X_1 = 0）
EA_C, L_C = 500.0, 5.0
SOL = dict(nodes={k: N_[k] for k in "ABCDG"},
           members=[dict(name="AB", ij=("A", "B"), EI=1000), dict(name="BC", ij=("B", "C"), EI=1000),
                    dict(name="CD", ij=("C", "D"), EI=1000), dict(name="GC", ij=("G", "C"), EI=1000)],
           supports=[("G", "fixed")],
           fe_loads=[("D", 0, -100, 0), ("B", 0, -T_BF, 0)])      # 纜索 BF 拉力向下拉住 B

def _with_cables(f, ds):
    """把 frameviz 的 compose 暫時換掉：兩個面板都補畫虛線纜索與 E、F 錨碇。"""
    import frameviz
    orig = frameviz.compose
    def wrapped(panels, **kw):
        a, b = panels
        for cv, deformed_panel in ((a, True), (b, False)):
            for top, bot, ok in (("A", "E", False), ("B", "F", True)):
                pt = N_[top]
                if deformed_panel:
                    pt = (pt[0] + f.d[top][0]*ds, pt[1] + f.d[top][1]*ds)
                col = C["tension"] if ok else C["muted"]
                cv.line(N_[bot], pt, col, 2.6, dash="7 6")
                cv.fixed_support(N_[bot], 0, 15)
            if deformed_panel:
                cv.text(N_["E"], "AE 鬆弛", 13, C["muted"], weight="700", dx=44, dy=-90)
                cv.text(N_["F"], "BF 受拉", 13, C["tension"], weight="700", dx=40, dy=-60)
        frameviz.compose = orig
        return orig(panels, **kw)
    frameviz.compose = wrapped

def fig2_solution():
    f = build_frame(SOL); M = end_moments(f)
    assert abs(f.d["B"][1] - T_BF*L_C/EA_C) < 1e-6           # 相容：B 上移量＝BF 伸長量 T·L/EA
    assert f.d["A"][1] < 0                                    # A 下移 → AE 縮短 → 鬆弛（§2.3）
    assert abs(abs(M["BC"][1]) - 5*T_BF) < 1e-6 and abs(abs(M["CD"][0]) - 500) < 1e-6
    ds, ms = _auto_scales(f, 15)
    _with_cables(f, ds)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2018-3 變形形狀與彎矩圖（單位 kN·m）", "A 下移→AE 縮短而鬆弛；B 上移→BF 受拉 70.75 kN",
        "梁全長上緣受拉；柱 CG 承擔差額 146.2", fmt="{:.1f}", W=600, H=460,
        notes=("", "虛線＝纜索（只受拉、不受彎）；AB 段彎矩 0"))

FIGURES.append((fig2_solution, "把 AE 當成可受壓的桿件（兩索都計入）"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

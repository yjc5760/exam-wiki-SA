#!/usr/bin/env python3
"""SA-2022-1：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2022-1-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2022-1.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2022-1"

# ── 判讀清單 #1–#7 ──
N_ = {"d": (0, 0), "c": (5, 0), "b": (10, 0), "a": (15, 0)}                    # #5
SPEC = dict(
    nodes=N_, members=[{"ij": ("d", "c")}, {"ij": ("c", "b")}, {"ij": ("b", "a")}],
    supports=[("d", "roller"), ("a", "fixed")],                               # #1、#4
    hinges=["b"],                                                             # #3
    springs=[("c", 2.2, "k")],                                                # #2
    loads=[("c", (0, -2.0), "72 kN", (0, -14)), ("b", (0, -2.0), "72 kN", (0, -14))],   # #6
    labels={"d": (-4, -20), "c": (-14, -16), "b": (14, -16), "a": (-14, -16)},
    ptexts=[((5.6, -2.5), "e（向下沉陷 Δe）", 12.5, None, "start")],
    dims=[((0, 0), (5, 0), "5 m", 112), ((5, 0), (10, 0), "5 m", 112), ((10, 0), (15, 0), "5 m", 112)],
    extra_pts=[(-0.9, 2.8), (16.0, -4.4)])

# 題給彎矩圖（#7：畫在上方＝正彎矩，依靜力判讀）
M_C, M_A = 120.0, -480.0                                                      # 題給數值（kN-m）
def fig2_problem():
    W, H = 640, 400; s = 34.0; km = 0.0075                                     # 每 kN-m 對應 0.0075 m 模型高度（只為作圖）
    cv = Canvas(W, H, sx=s, ox=65, oy=230, bg="#FFFFFF")
    pts = [(0, 0), (5, M_C * km), (10, 0), (15, M_A * km)]
    cv.polygon([(0, 0)] + pts[1:] + [(15, 0)], C["fill_m"], op=0.9)
    cv.poly(pts + [(15, 0)], C["bmd"], 2.6)
    cv.line((0, 0), (15, 0), C["member"], 2.0)
    cv.line((5, 0), (5, M_C * km), C["bmd"], 1.4)
    for k, x in (("d", 0), ("c", 5), ("b", 10), ("a", 15)):
        cv.text((x, 0), k, 16, C["text"], dy=(18 if x != 15 else -16), weight="700")
    cv.text((5, M_C * km), "120 kN-m", 13.5, C["bmd"], dy=-14, weight="700")
    cv.text((15, M_A * km), "480 kN-m", 13.5, C["bmd"], dy=18, weight="700")
    cv.text_px(W / 2, 22, "題給彎矩圖（照考卷）", 14.5, C["text"], weight="700")
    cv.text_px(W / 2, H - 16, "考卷未標正負號；依靜力判讀：基線上方為正彎矩（下緣受拉）、下方為負彎矩", 12.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-problem.svg")

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 440,
                          note="d 滾支承；c 彈簧 k = 6000 kN/m 接 e；b 內鉸；a 固定端；EI = 250000 kN-m^{2}")

FIGURES = [(fig1_problem, "b 讀成支承、彈簧位置讀錯"),
           (fig2_problem, "把題給彎矩圖的正負讀反（讀反時 M_a 只會是 240）")]

def _auto_scales(f, span, dfrac=0.12, mfrac=0.17):
    """依解出的位移與彎矩自動取放大倍率（圖形隨輸入改變，不寫死）。"""
    from frameviz import member_moment
    dmax = max(max(abs(v[0]), abs(v[1])) for v in f.d.values()) or 1
    mmax = max(abs(member_moment(f, m, k/40)) for m in f.M for k in range(41)) or 1
    return dfrac*span/dmax, mfrac*span/mmax

# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2022-1.md §4 Step 1–4 ──
# 彈簧以 §4 Step 2 解得的彈簧力 F_s = 24 kN（向上）作用於 c 代入，結構其餘部分照原樣建模。
from frameviz import solution_figure, build_frame, end_moments
FS, EI = 24.0, 250000.0
SOL = dict(nodes=N_, members=[dict(name="dc", ij=("d", "c"), EI=EI), dict(name="cb", ij=("c", "b"), EI=EI, rel=(0, 1)),
                              dict(name="ba", ij=("b", "a"), EI=EI)],
           supports=[("d", "roller"), ("a", "fixed")],
           fe_loads=[("c", 0, -72 + FS, 0), ("b", 0, -72, 0)])

SPRING_L = 2.2                                   # 圖上彈簧長度（示意，模型單位 m）

def _with_spring(f, ds, de):
    """補畫：變形後位置的內鉸 b、彈簧 c–e（e 沉陷 de）；彎矩圖面板畫原位置的內鉸。"""
    import frameviz
    orig = frameviz.compose
    def wrapped(panels, **kw):
        a, b = panels
        cx, cy = N_["c"][0], N_["c"][1] + f.d["c"][1]*ds
        ey = -SPRING_L - de*ds
        zz = [(cx, cy)] + [(cx + (0.22 if k % 2 else -0.22), cy + (ey - cy)*(0.15 + 0.7*k/9)) for k in range(10)] + [(cx, ey)]
        a.poly(zz, C["member"], 2.2)
        a.line((cx - 0.55, ey), (cx + 0.55, ey), C["member"], 2.6)
        a.line((cx - 0.55, -SPRING_L), (cx + 0.55, -SPRING_L), C["ghost"], 2.0, dash="5 4")
        a.text((cx, ey), "e", 14, C["text"], weight="700", dx=-22, dy=6)
        a.text((cx, (cy + ey)/2), "k", 14, C["text"], weight="700", dx=30, dy=-14)
        pb = (N_["b"][0], N_["b"][1] + f.d["b"][1]*ds)
        a.dot(pb, 6, fill="#FFFFFF", stroke=C["deform"], w=2.4)
        a.text(pb, "內鉸 b", 13, C["deform"], weight="700", dy=26)
        b.dot(N_["b"], 6, fill="#FFFFFF", stroke="#4A5568", w=2.4)
        frameviz.compose = orig
        return orig(panels, **kw)
    frameviz.compose = wrapped

def fig3_solution():
    f = build_frame(SOL); M = end_moments(f)
    assert abs(f.d["b"][1] + 0.016) < 1e-9 and abs(f.d["c"][1] + 0.012) < 1e-9   # Δ_b = 16 mm、Δ_c = 12 mm
    assert abs(abs(f.R["a"][2]) - 480) < 1e-6 and abs(f.R["d"][1] - 24) < 1e-9    # 與題給彎矩圖一致
    dc_mm = -f.d["c"][1]*1000; de_mm = dc_mm - FS/6000*1000                          # Δ_e = Δ_c − F_s/k
    assert abs(de_mm - 8) < 1e-9
    ds, ms = _auto_scales(f, 15)
    _with_spring(f, ds, de_mm/1000)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-3-deflected-bmd.svg", ds, ms,
        "圖 3　SA-2022-1 變形形狀與彎矩圖（彈簧以 F_s = 24 kN 代入）",
        f"b 下沉 16 mm、c 下沉 {dc_mm:.0f} mm；彈簧縮 4 mm → e 沉陷 {de_mm:.0f} mm",
        "M_c = +120、M_a = −480（與題給圖一致）", fmt="{:.0f}", W=600, H=430,
        notes=("", "內鉸 b 彎矩為零、斜率不連續"), extra_pts_m=[(5, -SPRING_L - 0.4)])

FIGURES.append((fig3_solution, "c 點位移當成 e 點沉陷、內鉸處畫成連續斜率"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

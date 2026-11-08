#!/usr/bin/env python3
"""SA-2015-3：題目附圖重繪（struct-diagram 規範；2026-11-07）
幾何、支承、載重逐項對應題目正本 SA-2015-3-problem.md §4 判讀清單（註解中的 #n），只畫考卷給的東西。
用法：python3 gen_SA-2015-3.py [輸出目錄]；之後執行 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os, math
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
import structdraw
from structdraw import Canvas, C
from probfig import problem_figure
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2015-3"

# ── 判讀清單 #1–#7 ──
N_ = {"B": (0, 4), "C": (1, 4), "D": (4, 4), "E": (7, 4), "F": (8, 4), "A": (0, 0), "G": (4, 0), "H": (8, 0)}   # #4、#5
SPEC = dict(
    nodes=N_, members=[{"ij": (a, b)} for a, b in (("B", "C"), ("C", "D"), ("D", "E"), ("E", "F"),
                                                    ("A", "B"), ("G", "D"), ("H", "F"))],
    supports=[("A", "fixed"), ("G", "fixed"), ("H", "fixed")],                # #1
    hinges=["C", "E"],                                                        # #2
    udl=[("B", "F", 0.9, "4 kN/m")],                                          # #7
    labels={"B": (-16, -12), "C": (0, 20), "D": (-14, 18), "E": (0, 20), "F": (16, -12),
            "A": (-20, -16), "G": (20, -16), "H": (20, -16)},
    dims=[((0, 0), (1, 0), "1 m", 44), ((1, 0), (4, 0), "3 m", 44), ((4, 0), (7, 0), "3 m", 44),
          ((7, 0), (8, 0), "1 m", 44), ((8, 0), (8, 4), "4 m", 60)],
    extra_pts=[(-0.6, 5.6), (9.4, -0.8)])

def fig1_problem():
    return problem_figure(SPEC, f"{OUT}/{TAG}-fig-1-problem.svg", 640, 460,
                          note="A、G、H 固定；C、E 為梁上內鉸；EI 定值、忽略軸向變形")

FIGURES = [(fig1_problem, "C、E 位置讀錯（BC、EF 各 1 m）、漏讀中柱 GD")]

# ── 解題圖（階段 E，2026-11-08）：數值由勁度法重解，與 SA-2015-3.md §4 步驟 4–5 對照（assert）──
#    M_AB = 88/31、M_BA = 176/31、M_BC = −176/31、M_DC = 216/31、M_DG = 0（順時針為正）；G_y = 516/31
#    CD 段：C 鉸對 CD 的向上剪力 V_C = 6 − M_DC/3 = 114/31 ⇒ 正彎矩極大 V_C²/(2w) 於距 C V_C/w 處
def _solve():
    from frame2d import Frame
    f = Frame()
    for n, p in N_.items(): f.node(n, *p)
    for n in "AGH": f.support(n, 1, 1, 1)
    f.member("AB", "A", "B", 1.0); f.member("GD", "G", "D", 1.0); f.member("HF", "H", "F", 1.0)
    f.member("BC", "B", "C", 1.0, w=4, rel=(0, 1)); f.member("CD", "C", "D", 1.0, w=4, rel=(1, 0))   # C 內鉸
    f.member("DE", "D", "E", 1.0, w=4, rel=(0, 1)); f.member("EF", "E", "F", 1.0, w=4, rel=(1, 0))   # E 內鉸
    f.solve()
    cw = lambda nm: (-f.end[nm][2], -f.end[nm][5])
    assert abs(cw("AB")[0] - 88/31) < 1e-6 and abs(cw("BC")[0] + 176/31) < 1e-6 and abs(cw("CD")[1] - 216/31) < 1e-6
    assert abs(cw("GD")[0]) < 1e-6 and abs(f.R["G"][1] - 516/31) < 1e-5
    return f

def fig2_bmd():
    from beamfig import beam_strip
    from frameviz import member_moment
    f = _solve(); w = 4.0
    VC = 6 - (216/31) / 3                                       # §4 步驟 5 同法：114/31
    xm, Mm = VC / w, VC**2 / (2*w)                              # 0.919 m、1.690 kN-m
    cd = next(m for m in f.M if m["name"] == "CD")
    assert abs(member_moment(f, cd, xm/3) - Mm) < 1e-6
    def extra(_a, b):
        b.text_px(b.X(1 + xm), b.Y(4) + 64, f"距 C {xm:.3f} m", 12.5, C["muted"])
        b.text_px(b.X(7 - xm), b.Y(4) + 64, f"距 E {xm:.3f} m", 12.5, C["muted"])
        b.text_px(b.X(4), b.Y(4) + 30, "D：柱 GD 彎矩 0", 12.5, C["muted"])
    return beam_strip(f, ["BC", "CD", "DE", "EF"], f"{OUT}/{TAG}-fig-2-beam-bmd.svg",
        "圖 2　SA-2015-3 梁 B–F 彎矩圖（4 kN/m 全長）", W=900, H2=360, yc=0.46, show_def=False, mpx=95,
        hinges=["C", "E"],
        mlabels=[("BC", 0.0, "R", True), ("CD", xm/3, "C", True), ("CD", 1.0, "C", True),
                 ("DE", 1 - xm/3, "C", True), ("EF", 1.0, "L", True)],
        sub_bmd="B、D、F 負彎矩（上緣受拉）；C、E 鉸 M = 0；CD、DE 段中間有正彎矩極大",
        note="鉸 C、E 下陷 δ = 459/(62EI)；中柱 GD 不受彎、只受軸力 Gy = 516/31 = 16.65 kN", extra=extra)

FIGURES.append((fig2_bmd, "只標 B、D 負彎矩而漏掉 CD 段 +1.69 的正彎矩極大；把鉸 C、E 畫成有彎矩"))

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, catches in FIGURES:
        print(os.path.basename(fn()), "攔：", catches)

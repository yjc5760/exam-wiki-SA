#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SA-2002-1 內鉸剛架 — 解題圖解產生腳本

2026-10-23 載重校正：C-D 段為均布彎矩 2 kN-m/m（CW）；F 梁端 CCW、柱端 CW。
以下常數全部取自校正後的 SA-2002-1.md（Step 1 / Step 2）。
"""
import sys, os
sys.path.insert(0, os.environ.get("STRUCTDRAW_DIR", "/root/.claude/skills/synced/struct-diagram/scripts"))

from structdraw import Canvas, C, compose
from recipes import plot_function

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2002-1"

# ══════════════════════════════════════════════════════════
# 幾何（§1）
# ══════════════════════════════════════════════════════════
A, B, CN, D, E, F, G, H = (0, 0), (0, 2), (0, 4), (2, 4), (3, 4), (6, 4), (6, 2), (6, 0)

# ══════════════════════════════════════════════════════════
# 反力與關鍵內力（§Step 1 / Step 2，2026-10-23 載重校正後）
#   C-D 段為均布彎矩 m=2 kN-m/m（CW）；F 梁端 4 CCW、柱端 4 CW；B 6 CCW
# ══════════════════════════════════════════════════════════
P_F, Q_F = 0, -29/3
Ax, Ay = -10, -5/3
Hx, Hy = 4, 29/3
M_B = 6          # B點集中彎矩，CCW
M_CD = 2         # C-D 均布彎矩，CW（kN-m/m）
M_F_BEAM = 4     # F點梁端集中彎矩，CCW
M_F_COL = 4      # F點柱端集中彎矩，CW

# 彎矩一律「內側受拉為正」（左柱右側、梁底、右柱左側）
M_A, M_B_minus, M_B_plus, M_C = 0, 20, 14, 34
M_D, M_E = 104/3, 33
M_F_beam_pre = 4                   # E-F 段末端、加梁端力矩前（梁底受拉）
M_G = 4                            # 右柱 G 點（左側受拉），G-F 段剪力 0 → 常數
M_F_col_pre = 4                    # G-F 段末端、加柱端力矩前


# ══════════════════════════════════════════════════════════
def frame(cv, color=C["member"], w=6.0, dash=None):
    for s, e in ((A, B), (B, CN), (CN, D), (D, E), (E, F), (F, G), (G, H)):
        cv.line(s, e, color, w, dash=dash, cap="butt")


def fig1_frame():
    """題目重繪（2026-10-23 依原圖 fig-1 校正）：
    ① C-D 段是「均布彎矩」2 kN-m/m（原圖為一排小弧形箭頭），不是均布力；
    ② F 點梁端 4 kN-m 逆時針 CCW、柱端 4 kN-m 順時針 CW；
    ③ B 點 6 kN-m 逆時針 CCW（維持）。"""
    W, H_ = 1040, 620
    cv = Canvas(W, H_, sx=76, ox=150, oy=90, bg="#FFFFFF")
    frame(cv)
    cv.pin_support(A, ang=0); cv.pin_support(H, ang=0)

    # 內鉸 F：空心圓標示（與剛接節點 C 不同）
    cv.circle(F, 0.12, "#FFFFFF", C["member"], 3.0)

    for p, lab, dx, dy in ((A, "A", -18, -14), (B, "B", 18, 0), (CN, "C", -18, 14),
                            (D, "D", 0, 20), (E, "E", 0, 20), (F, "F", 18, -22),
                            (G, "G", -22, 0), (H, "H", -22, -14)):
        if p != F:
            cv.dot(p, 5.2)
        cv.text(p, lab, 16, C["text"], weight="700", dx=dx, dy=dy)

    # C 點集中水平力 10 kN
    cv.arrow((CN[0] - 1.35, CN[1]), CN, C["load"], 3.4, 11)
    cv.math((CN[0] - 1.35, CN[1]), "10", 15, C["load"], "end", dx=-6, dy=-16, weight="700")
    cv.text((CN[0] - 1.35, CN[1]), "kN", 13, C["load"], "end", dx=-6, dy=2)

    # C-D 均布彎矩 2 kN-m/m：上緣線＋一排小弧形箭頭（順時針，同原圖）
    top_y = CN[1] + 0.48
    cv.line((CN[0], top_y), (D[0], top_y), C["load"], 2.0)
    for i in range(5):
        xc = CN[0] + 0.2 + i * 0.4
        cv.line((xc, top_y), (xc, CN[1] + 0.34), C["load"], 1.6)
        cv.moment_arrow((xc, CN[1] + 0.2), r=9, ccw=False, color=C["load"], w=2.2,
                        span=230, start=95)
    cv.math_px(cv.X(1), cv.Y(4) - 58, "m_{CD}=2 kN-m/m", 13.5, C["load"], weight="700")
    cv.text_px(cv.X(1), cv.Y(4) - 80, "均布彎矩（順時針 CW）", 12, C["load"])

    # E 點集中垂直力 8 kN 向下
    cv.arrow((E[0], E[1] + 1.1), E, C["load"], 3.4, 11)
    cv.math((E[0], E[1] + 1.1), "8 kN", 14, C["load"], dy=-14, weight="700")

    # H-G 均布載重 2 kN/m 向左
    cv.udl(H, G, -0.5, n=6, color=C["load"])
    cv.math_px(cv.X(6) + 68, cv.Y(1), "w_{GH}=2 kN/m", 13.5, C["load"], "start", weight="700")

    # B 點集中彎矩 6 kN-m 逆時針 CCW
    cv.moment_arrow(B, r=28, ccw=True, color=C["accent"], w=3.2, span=250, start=205)
    cv.math_px(cv.X(B[0]) + 20, cv.Y(B[1]) - 18, "M_{B}=6 kN-m", 14, C["accent"], "start", weight="700")
    cv.text_px(cv.X(B[0]) + 20, cv.Y(B[1]) + 2, "（逆時針 CCW）", 12, C["accent"], "start")

    # F 點兩個集中彎矩：各自畫在所屬桿端旁
    # 梁端（F 左側、梁上）：逆時針 CCW
    fb = (F[0] - 0.42, F[1])
    cv.moment_arrow(fb, r=20, ccw=True, color=C["accent"], w=3.0, span=240, start=-120)
    cv.math_px(cv.X(fb[0]) - 30, cv.Y(fb[1]) - 50, "M_{F,beam}=4 kN-m", 13, C["accent"], "end", weight="700")
    cv.text_px(cv.X(fb[0]) - 30, cv.Y(fb[1]) - 32, "（梁端，逆時針 CCW）", 11.5, C["accent"], "end")
    # 柱端（F 下方、柱上）：順時針 CW
    fc = (F[0], F[1] - 0.42)
    cv.moment_arrow(fc, r=20, ccw=False, color=C["load"], w=3.0, span=240, start=150)
    cv.math_px(cv.X(fc[0]) + 34, cv.Y(fc[1]) - 2, "M_{F,col}=4 kN-m", 13, C["load"], "start", weight="700")
    cv.text_px(cv.X(fc[0]) + 34, cv.Y(fc[1]) + 16, "（柱端，順時針 CW）", 11.5, C["load"], "start")

    # 尺寸線
    cv.dim(A, B, "2 m", off=-95, label_off=-15)
    cv.dim(B, CN, "2 m", off=-95, label_off=-15)
    cv.dim(CN, D, "2 m", off=64, label_off=17)
    cv.dim(D, E, "1 m", off=64, label_off=17)
    cv.dim(E, F, "3 m", off=64, label_off=17)
    cv.dim(H, G, "2 m", off=-58, label_off=-15)
    cv.dim(G, F, "2 m", off=-58, label_off=-15)

    cv.text_px(W/2, H_ - 34,
               "圖面校正（2026-10-23，依原圖 fig-1）：C-D 段為均布彎矩 2 kN-m/m（非均布力）；"
               "F 點梁端 4 kN-m 逆時針、柱端 4 kN-m 順時針。", 12.5, C["muted"])
    cv.text_px(W/2, H_ - 16, "內鉸 F 以空心圓標示，與剛接節點 C（實心圓）區別。", 12.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-frame-corrected.svg")


def fig2_bmd():
    """BMD 沿路徑展開圖：A→B→C→D→E→F（梁側）／F→G→H（柱側），內側受拉為正。
    攔下的錯：C-D 段把均布彎矩當均布力（會畫成拋物線）；F 兩側未各自由 4 跳回 0。"""
    xs, ys = [], []

    def add(seg_x0, seg_x1, f, n=24):
        """f 吃「該段局部座標」(從 0 開始)，回傳 M 值。"""
        for i in range(n + 1):
            t = i / n
            loc = t * (seg_x1 - seg_x0)
            xs.append(seg_x0 + loc); ys.append(f(loc))

    add(0, 2, lambda y: 10*y)                                 # A-B: 0 -> 20
    xs.append(2); ys.append(M_B_plus)                          # B 跳躍：20 -> 14（逆時針 M_B）
    add(2, 4, lambda y: M_B_plus + 10*y)                       # B-C: 14 -> 34
    add(4, 6, lambda x: M_C + (Ay + M_CD)*x)                   # C-D: 斜率 V+m = 1/3：34 -> 34.67
    add(6, 7, lambda x: M_D + Ay*x)                            # D-E: 34.67 -> 33
    add(7, 10, lambda x: M_E - (29/3)*x)                       # E-F: 33 -> 4
    add(10, 12, lambda loc: M_F_col_pre)                       # F-G: V=0，常數 4（左側受拉）
    add(12, 14, lambda loc: 4*(2-loc) - (2-loc)**2)            # G-H: 4y-y², y=2-loc：4 -> 0

    PW, PH = 980, 380
    L_pad, R_pad, top_px, bot_px = 100, 60, 90, 60
    sx = (PW - L_pad - R_pad) / 14
    px_per_unit = 5.2                              # 每 1 kN-m 對應的像素（純視覺比例）
    scale = px_per_unit / sx
    oy = bot_px + 30
    cv = Canvas(PW, PH, sx=sx, ox=L_pad, oy=oy)
    cv.panel("彎矩圖 BMD（沿 A→B→C→D→E→F→G→H 路徑展開）",
             "內側受拉為正（左柱右側、梁底、右柱左側）；F 點兩側加力矩前皆為內側受拉 4，加力矩後各自歸 0")
    marks = [(0, "0", -14), (2, "20→14", -16), (4, "34", -16),
             (6, f"{M_D:.2f}", -16), (7, "33", -16), (10, "4→0（兩側）", -16),
             (12, "4", -16), (14, "0", -14)]
    plot_function(cv, xs, ys, scale, base_y=0, x0=0, color=C["bmd"], fill=C["fill_m"],
                  w=2.4, marks=marks)

    for x, lab in ((0, "A"), (2, "B"), (4, "C"), (6, "D"), (7, "E"), (10, "F"), (12, "G"), (14, "H")):
        cv.parts.append(f'<line x1="{cv.X(x):.2f}" y1="{cv.Y(0)-200:.2f}" x2="{cv.X(x):.2f}" '
                        f'y2="{cv.Y(0)+20:.2f}" stroke="{C["ghost"]}" stroke-width="1" stroke-dasharray="4 4"/>')
        cv.text_px(cv.X(x), cv.Y(0) + 34, lab, 13.5, C["text"], weight="700")

    cv.math_px(cv.X(5), cv.Y(0) - 60, "C-D: dM/dx=V+m=1/3", 11.5, C["accent"], weight="700")

    cv.text_px(PW/2, PH - 26,
               "M_F（梁側）= 4 − 4（梁端逆時針）= 0　　M_F（柱側）= 4 − 4（柱端順時針）= 0　　C-D 段為均布彎矩：直線、非拋物線",
               13, C["bmd"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-3-bmd-path.svg")


FIGURES = [
    (fig1_frame, "§1 / Step 1", "C-D 均布彎矩誤當均布力、F 兩處力矩轉向判反"),
    (fig2_bmd,   "§Step 2/3",   "C-D 段斜率 V+m；F 兩側各自由 4 跳回 0"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, section, catches in FIGURES:
        print(f"{os.path.basename(fn()):<44} {section:<12} 攔：{catches}")

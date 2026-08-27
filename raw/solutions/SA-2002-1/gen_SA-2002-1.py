#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SA-2002-1 內鉸剛架 — 解題圖解產生腳本

本題本次解析的核心修正：B、F 兩處集中力矩弧形箭頭的轉向被原圖誤判（三處全反）。
以下常數全部取自校正後的 SA-2002-1.md（Step 1 / Step 2）。
"""
import sys, os
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")

from structdraw import Canvas, C, compose
from recipes import plot_function

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2002-1"

# ══════════════════════════════════════════════════════════
# 幾何（§1）
# ══════════════════════════════════════════════════════════
A, B, CN, D, E, F, G, H = (0, 0), (0, 2), (0, 4), (2, 4), (3, 4), (6, 4), (6, 2), (6, 0)

# ══════════════════════════════════════════════════════════
# 反力與關鍵內力（§Step 1 / Step 2，校正後）
# ══════════════════════════════════════════════════════════
Ax, Ay = -8, 7/3
Hx, Hy = 2, 29/3
M_B = 6          # B點集中彎矩，CCW（校正後）
M_F_BEAM = 4     # F點梁端集中彎矩，CW（校正後）
M_F_COL = 4      # F點柱端集中彎矩，CCW（校正後）

M_A, M_B_minus, M_B_plus, M_C = 0, 16, 10, 26
M_maxCD, XI_CD = 985/36, 7/6       # C-D 段最大彎矩位置與值（由 dM/dx=0 解出）
M_D, M_E = 80/3, 25
M_F_beam_pre = -4                  # E-F 段末端、加力矩前
M_H, M_dip_y1, M_G = 0, -1, 0      # 右柱下半
M_F_col_pre = 4                    # G-F 段末端、加力矩前


# ══════════════════════════════════════════════════════════
def frame(cv, color=C["member"], w=6.0, dash=None):
    for s, e in ((A, B), (B, CN), (CN, D), (D, E), (E, F), (F, G), (G, H)):
        cv.line(s, e, color, w, dash=dash, cap="butt")


def fig1_frame():
    """題目重繪：把手繪弧形力矩箭頭的轉向明確標成文字＋正確弧線方向。
    攔下的錯：B、F 兩處力矩方向誤判（本解析初版即誤判全部三處）。"""
    W, H_ = 1040, 620
    cv = Canvas(W, H_, sx=76, ox=150, oy=90, bg="#FFFFFF")
    frame(cv)
    cv.pin_support(A, ang=0); cv.pin_support(H, ang=0)

    # 內鉸 F：空心圓標示（與剛接節點 C 不同）
    cv.circle(F, 0.12, "#FFFFFF", C["member"], 3.0)

    # 節點標籤（放在遠離力矩弧線的一側，避免重疊）
    for p, lab, dx, dy in ((A, "A", -18, -14), (B, "B", 18, 0), (CN, "C", -18, 14),
                            (D, "D", 0, 20), (E, "E", 0, 20), (F, "F", -10, -26),
                            (G, "G", -22, 0), (H, "H", -22, -14)):
        cv.dot(p, 5.2); cv.text(p, lab, 16, C["text"], weight="700", dx=dx, dy=dy)

    # C 點集中水平力 10 kN
    cv.arrow((CN[0] - 1.35, CN[1]), CN, C["load"], 3.4, 11)
    cv.math((CN[0] - 1.35, CN[1]), "10", 15, C["load"], "end", dx=-6, dy=-16, weight="700")
    cv.text((CN[0] - 1.35, CN[1]), "kN", 13, C["load"], "end", dx=-6, dy=2)

    # C-D 均布載重 2 kN/m 向下（height>0 → 法向 (0,1) 反向 = 向下，符合題意）
    cv.udl(CN, D, 0.5, n=6, color=C["load"])
    cv.math_px(cv.X(1), cv.Y(4) - 62, "w_{CD}=2 kN/m", 13.5, C["load"], weight="700")

    # E 點集中垂直力 8 kN 向下
    cv.arrow((E[0], E[1] + 1.1), E, C["load"], 3.4, 11)
    cv.math((E[0], E[1] + 1.1), "8 kN", 14, C["load"], dy=-14, weight="700")

    # H-G 均布載重 2 kN/m 向左（height<0 才能讓法向 (-1,0) 反向 = 向左，符合題意）
    cv.udl(H, G, -0.5, n=6, color=C["load"])
    cv.math_px(cv.X(6) + 68, cv.Y(1), "w_{GH}=2 kN/m", 13.5, C["load"], "start", weight="700")

    # B 點集中彎矩 6 kN-m（校正後：逆時針 CCW）—— 標籤放在右側，避開左側尺寸線
    cv.moment_arrow(B, r=28, ccw=True, color=C["accent"], w=3.2, span=250, start=205)
    cv.math_px(cv.X(B[0]) + 20, cv.Y(B[1]) - 18, "M_{B}=6 kN-m", 14, C["accent"], "start", weight="700")
    cv.text_px(cv.X(B[0]) + 20, cv.Y(B[1]) + 2, "（逆時針 CCW，已校正）", 12, C["accent"], "start")

    # F 點兩個集中彎矩：梁端 4 kN-m CW（內圈）、柱端 4 kN-m CCW（外圈），同一角度範圍、不同半徑以區分
    cv.moment_arrow(F, r=22, ccw=False, color=C["load"], w=3.0, span=235, start=205)
    cv.moment_arrow(F, r=50, ccw=True, color=C["accent"], w=3.0, span=235, start=205)
    cv.math_px(cv.X(F[0]) + 66, cv.Y(F[1]) + 18, "M_{F,beam}=4 kN-m", 13, C["load"], "start", weight="700")
    cv.text_px(cv.X(F[0]) + 66, cv.Y(F[1]) + 35, "（梁端，順時針 CW，已校正）", 11.5, C["load"], "start")
    cv.math_px(cv.X(F[0]) + 66, cv.Y(F[1]) + 62, "M_{F,col}=4 kN-m", 13, C["accent"], "start", weight="700")
    cv.text_px(cv.X(F[0]) + 66, cv.Y(F[1]) + 79, "（柱端，逆時針 CCW，已校正）", 11.5, C["accent"], "start")

    # 尺寸線
    cv.dim(A, B, "2 m", off=-95, label_off=-15)
    cv.dim(B, CN, "2 m", off=-95, label_off=-15)
    cv.dim(CN, D, "2 m", off=64, label_off=17)
    cv.dim(D, E, "1 m", off=64, label_off=17)
    cv.dim(E, F, "3 m", off=64, label_off=17)
    cv.dim(H, G, "2 m", off=-58, label_off=-15)
    cv.dim(G, F, "2 m", off=-58, label_off=-15)

    cv.text_px(W/2, H_ - 34,
               "圖面校正：原圖三處弧形力矩箭頭轉向皆誤判（B 誤判順時針、梁端誤判逆時針、柱端誤判順時針）；"
               "本圖為逐像素追蹤箭頭起訖點角度後之正確轉向。", 12.5, C["muted"])
    cv.text_px(W/2, H_ - 16, "內鉸 F 以空心圓標示，與剛接節點 C（實心圓）區別。", 12.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-frame-corrected.svg")


def fig2_bmd():
    """BMD 沿路徑展開圖：A→B→C→D→E→F（梁側收斂為 0）／F→G→H（柱側收斂為 0）。
    攔下的錯：內鉸兩側彎矩沒有精確收斂到 0（代表某處力矩方向或計算仍有誤）。"""
    xs, ys = [], []

    def add(seg_x0, seg_x1, f, n=24):
        """f 吃「該段局部座標」(從 0 開始)，回傳 M 值。"""
        for i in range(n + 1):
            t = i / n
            loc = t * (seg_x1 - seg_x0)
            xs.append(seg_x0 + loc); ys.append(f(loc))

    add(0, 2, lambda y: 8*y)                                  # A-B: 0 -> 16
    xs.append(2); ys.append(M_B_plus)                          # B 跳躍：16 -> 10（B點外加逆時針力矩）
    add(2, 4, lambda y: M_B_plus + 8*y)                        # B-C: 10 -> 26（局部 y=0~2）
    add(4, 6, lambda x: 26 + (7/3)*x - x*x)                    # C-D: 26 -> 26.67（峰值27.36於x=7/6）
    add(6, 7, lambda x: M_D - (5/3)*x)                         # D-E: 26.67 -> 25
    add(7, 10, lambda x: M_E - (29/3)*x)                       # E-F: 25 -> -4
    xs.append(10); ys.append(M_F_col_pre)                      # F 角隅跳躍：-4 -> +4（梁端與柱端力矩各自作用）
    add(10, 12, lambda loc: M_F_col_pre - 2*loc)               # F-G: 4 -> 0
    add(12, 14, lambda loc: loc*loc - 2*loc)                   # G-H: 0 -> -1(中點) -> 0

    PW, PH = 980, 380
    L_pad, R_pad, top_px, bot_px = 100, 60, 90, 60
    sx = (PW - L_pad - R_pad) / 14
    px_per_unit = 3.9                              # 每 1 kN-m 對應的像素（純視覺比例）
    scale = px_per_unit / sx                        # 換算成 plot_function 吃的「模型單位」比例
    oy = bot_px + max(ys) * px_per_unit
    cv = Canvas(PW, PH, sx=sx, ox=L_pad, oy=oy)
    cv.panel("彎矩圖 BMD（沿 A→B→C→D→E→F→G→H 路徑展開）",
             "填色區域=彎矩值；灰虛線為節點分界；F 點兩側各自獨立收斂到 0")
    marks = [(0, "0", -14), (2, "16→10", -16), (4, "26", -16),
             (6, f"{M_D:.2f}", -16), (7, "25", 16), (10, "−4→+4", 16),
             (12, "0", 16), (14, "0", -14)]
    plot_function(cv, xs, ys, scale, base_y=0, x0=0, color=C["bmd"], fill=C["fill_m"],
                  w=2.4, marks=marks)

    for x, lab in ((0, "A"), (2, "B"), (4, "C"), (6, "D"), (7, "E"), (10, "F"), (12, "G"), (14, "H")):
        cv.parts.append(f'<line x1="{cv.X(x):.2f}" y1="{cv.Y(0)-118:.2f}" x2="{cv.X(x):.2f}" '
                        f'y2="{cv.Y(0)+34:.2f}" stroke="{C["ghost"]}" stroke-width="1" stroke-dasharray="4 4"/>')
        cv.text_px(cv.X(x), cv.Y(0) + 50, lab, 13.5, C["text"], weight="700")

    xi_x = 4 + XI_CD
    cv.dot((xi_x, M_maxCD*scale), 5, fill="#FFFFFF", stroke=C["accent"], w=2.4)
    cv.math_px(cv.X(xi_x), cv.Y(M_maxCD*scale) - 38, f"M_max={M_maxCD:.2f}", 12, C["accent"], weight="700")

    cv.text_px(PW/2, PH - 26,
               "M_F（梁側）= −4+4 = 0　　M_F（柱側）= 4−4 = 0　　兩者獨立收斂為 0 ⇒ 交叉驗證方向判讀無誤",
               13, C["bmd"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-3-bmd-path.svg")


FIGURES = [
    (fig1_frame, "§1 / Step 1", "B、F 兩處弧形力矩箭頭轉向誤判 → 全題反力與內力方向皆反"),
    (fig2_bmd,   "§Step 2/3",   "內鉸 F 兩側彎矩沒有精確收斂到 0 → 方向或計算仍有誤"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, section, catches in FIGURES:
        print(f"{os.path.basename(fn()):<44} {section:<12} 攔：{catches}")

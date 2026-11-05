#!/usr/bin/env python3
"""SA-2008-4 解題圖解（struct-diagram；2026-11-05 階段 E）
  圖 2  BC 桿自由體／剪力圖／彎矩圖：攔「端彎矩對剪力的正負號帶反」（V_B 錯成 2.5、極值跑到 2.5 m）
  圖 3  剛架彎矩圖（畫在受拉側）：攔柱、梁受拉側畫反，以及柱底與柱頂同側的錯誤
所有數值由本腳本以 2×2 勁度矩陣重解（θ_B、θ_C），再與解析 §4 步驟 4–6 的值 assert。
用法：python3 gen_SA-2008-4_bmd.py [輸出目錄]；之後以 struct-diagram 的 render.py 產生 2× PNG。"""
import sys, os
from fractions import Fraction as Fr
_HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(_HERE, "figs", "_lib"))
from structdraw import Canvas, C, compose
from recipes import plot_function

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2008-4"

# ── 題目正本 §4：A(0,0) 固定、B(0,4) 剛接、C(6,4) 鉸支；BC 受 w = 1 kN/m；EI 常數 ──
H, LB, W = Fr(4), Fr(6), Fr(1)
# ── 勁度法（順時針為正，同解析 §4）：K = EI[[1+2/3, 1/3],[1/3, 2/3]]，R = [3, -3] ──
FEM = W * LB**2 / 12                                  # 3 kN-m
K = [[4/H + 4/LB, 2/LB], [2/LB, 4/LB]]
R = [FEM, -FEM]
det = K[0][0]*K[1][1] - K[0][1]*K[1][0]
TB = (R[0]*K[1][1] - K[0][1]*R[1]) / det              # θ_B·EI
TC = (K[0][0]*R[1] - K[1][0]*R[0]) / det              # θ_C·EI
M_AB = 2/H * (TB)                                     # 順時針為正
M_BA = 2/H * (2*TB)
M_BC = 2/LB * (2*TB + TC) - FEM
M_CB = 2/LB * (2*TC + TB) + FEM
V_B = (W*LB*LB/2 - M_BC - M_CB) / LB                  # ΣM_C = 0（M_BC 順時針為正，作用在梁左端）
V_C = W*LB - V_B
X_MAX = V_B / W
M_MAX = M_BC + V_B*X_MAX - W*X_MAX**2/2               # 梁慣例：M(0) = M_BC（順時針左端 = 負彎矩）

def M_beam(x):  # 梁慣例（正彎矩下側受拉），x 由 B 量起
    return M_BC + V_B*x - W*x*x/2

# 梁反曲點：M(x)=0 的較小根（精確解）
from math import sqrt
_a, _b, _c = -W/2, V_B, M_BC
X_INF = float((-_b + sqrt(_b*_b - 4*_a*_c)) / (2*_a))
# 柱：內力彎矩（正 = 柱右側／內側受拉），A 端 = +M_AB、B 端 = -M_BA（順時針為正的桿端彎矩換算）
MA_col, MB_col = M_AB, -M_BA
Y_INF_COL = MA_col / (MA_col - MB_col) * H

# ── 與解析 §4 步驟 4–6 對照 ──
assert (TB, TC) == (3, -6)
assert (M_AB, M_BA, M_BC, M_CB) == (Fr(3, 2), 3, -3, 0)
assert (V_B, V_C, X_MAX, M_MAX) == (Fr(7, 2), Fr(5, 2), Fr(7, 2), Fr(25, 8))
assert abs(X_INF - 1.0) < 1e-12 and Y_INF_COL == Fr(4, 3)
assert M_beam(LB) == 0 and M_beam(0) == -3

def f(v, nd=3):
    v = float(v); s = f"{v:.{nd}f}".rstrip("0").rstrip(".")
    return s


def fig2_bc_vm():
    """BC 桿自由體＋SFD＋BMD（三聯，直向）"""
    Wc, PH = 820, 220
    sx = (Wc - 220) / float(LB); pad = 110
    xs = [float(LB) * i / 120 for i in range(121)]
    V = [float(V_B - W*x) for x in xs]
    M = [float(M_beam(x)) for x in xs]

    top = Canvas(Wc, PH + 40, sx=sx, ox=pad, oy=(PH + 40) * 0.42)
    top.panel("BC 桿自由體", f"B 端彎矩 {f(abs(M_BC))} kN-m 逆時針作用於梁端（負彎矩，取自勁度法回算）；C 鉸 M = 0")
    top.line((0, 0), (float(LB), 0), C["member"], 6, cap="butt")
    top.udl((0, 0), (float(LB), 0), 0.55, n=11, label="w = 1 kN/m")
    top.arrow((0, -0.62), (0, -0.04), C["deform"], 3.0, 11)
    top.text_px(top.X(0) + 12, top.Y(-0.5), f"V_B = {f(V_B)} kN（↑）", 13.5, C["deform"], "start", weight="700")
    top.arrow((float(LB), -0.62), (float(LB), -0.04), C["deform"], 3.0, 11)
    top.text_px(top.X(float(LB)) - 12, top.Y(-0.5), f"V_C = {f(V_C)} kN（↑）", 13.5, C["deform"], "end", weight="700")
    top.moment_arrow((0, 0), r=30, ccw=(M_BC < 0), color=C["load"], w=2.6, span=180, start=100)
    top.text_px(top.X(0) - 40, top.Y(0) - 4, f"{f(abs(M_BC))} kN-m", 13, C["load"], "end", weight="700")

    def strip(vals, color, fill, name, unit, keys):
        top_px, bot_px = 74, 36
        vmax, vmin = max(max(vals), 0.0), min(min(vals), 0.0)
        px_per = (PH + 40 - top_px - bot_px) / ((vmax - vmin) or 1.0)
        cv = Canvas(Wc, PH + 40, sx=sx, ox=pad, oy=PH + 40 - (top_px + vmax * px_per))
        cv.panel(name)
        plot_function(cv, xs, vals, px_per / sx, 0.0, 0.0, color, fill)
        cv.text_px(pad - 14, cv.Y(0), "0", 12, C["muted"], "end")
        cv.text_px(Wc - 22, 32, unit, 12, C["muted"], "end")
        for x, val, t, dy, anc in keys:
            cv.dot((x, val * px_per / sx), 4.2, fill=color)
            cv.text_px(cv.X(x) + (8 if anc == "start" else -8 if anc == "end" else 0),
                       cv.Y(val * px_per / sx) + dy, t, 13, color, anc, weight="700")
        return cv, px_per

    mid, _ = strip(V, C["sfd"], C["fill_s"], "剪力圖 SFD（向上為正）", "kN",
                   [(0, float(V_B), f"+{f(V_B)}", -14, "start"),
                    (float(LB), float(-V_C), f"−{f(V_C)}", 16, "end"),
                    (float(X_MAX), 0.0, f"V = 0 於距 B {f(X_MAX)} m", -24, "start")])
    bot, pp = strip(M, C["bmd"], C["fill_m"], "彎矩圖 BMD（正彎矩＝梁底受拉，向上畫）", "kN-m",
                    [(0, float(M_BC), f"−{f(abs(M_BC))}（梁頂受拉）", 6, "start"),
                     (float(X_MAX), float(M_MAX), f"最大正彎矩 +{f(M_MAX)}（距 B {f(X_MAX)} m）", -16, "middle"),
                     (X_INF, 0.0, f"反曲點 {f(X_INF)} m", 18, "start")])
    bot.line((float(X_MAX), 0), (float(X_MAX), float(M_MAX) * pp / sx), C["accent"], 1.6, dash="5 4")
    return compose([top, mid, bot], cols=1, path=f"{OUT}/{TAG}-fig-2-bc-vm.svg")


def fig3_frame_bmd():
    """剛架彎矩圖（畫在受拉側）"""
    Wc, Hc = 820, 600
    Lm, Rm, Tm, Bm = 120, 80, 86, 70
    k = 0.42                                            # 每 kN-m 對應的模型長度（m）
    xr = (-float(abs(MB_col)) * k - 0.2, float(LB) + 0.3)
    yr = (-0.3, float(H) + float(abs(M_BC)) * k + 0.3)
    sx = min((Wc - Lm - Rm) / (xr[1] - xr[0]), (Hc - Tm - Bm) / (yr[1] - yr[0]))
    cv = Canvas(Wc, Hc, sx=sx, ox=Lm - xr[0] * sx, oy=Bm - yr[0] * sx)
    cv.panel("剛架彎矩圖（畫在受拉側，kN-m）", "柱由 A 端內側 1.5 線性變到 B 端外側 3.0；梁為二次拋物線")
    A, B, Cn = (0, 0), (0, float(H)), (float(LB), float(H))
    # 柱：正值畫在右側（內側），負值畫在左側（外側）
    col = [(float(MA_col + (MB_col - MA_col) * t / 40) * k, float(H) * t / 40) for t in range(41)]
    cv.polygon([A] + col + [B], C["fill_m"], C["bmd"], 2.2)
    # 梁：正彎矩（下側受拉）畫在梁下方
    bx = [float(LB) * i / 80 for i in range(81)]
    beam = [(x, float(H) - float(M_beam(x)) * k) for x in bx]
    cv.polygon([B] + beam + [Cn], C["fill_m"], C["bmd"], 2.2)
    cv.line(A, B, C["member"], 6, cap="butt"); cv.line(B, Cn, C["member"], 6, cap="butt")
    cv.support(A, "fixed"); cv.support(Cn, "pin")
    for p, t, dx, dy in ((A, "A", -16, 10), (B, "B", -16, -14), (Cn, "C", 18, -14)):
        cv.text_px(cv.X(p[0]) + dx, cv.Y(p[1]) + dy, t, 16, C["text"], weight="700")
    cv.text_px(cv.X(float(MA_col) * k) + 8, cv.Y(0) - 10, f"{f(MA_col)}（內側受拉）", 13.5, C["bmd"], "start", weight="700")
    cv.text_px(cv.X(float(MB_col) * k) - 8, cv.Y(float(H)) - 14, f"{f(abs(MB_col))}（外側受拉）", 13.5, C["bmd"], "end", weight="700")
    cv.text_px(cv.X(0) + 10, cv.Y(float(H) + float(abs(M_BC)) * k) - 12, f"{f(abs(M_BC))}（梁頂受拉）", 13.5, C["bmd"], "start", weight="700")
    cv.text_px(cv.X(float(X_MAX)), cv.Y(float(H) - float(M_MAX) * k) + 20, f"+{f(M_MAX)}（梁底受拉，距 B {f(X_MAX)} m）", 13.5, C["bmd"], weight="700")
    cv.line((float(X_MAX), float(H)), (float(X_MAX), float(H) - float(M_MAX) * k), C["accent"], 1.6, dash="5 4")
    for p, t, anc, dx in (((0, float(Y_INF_COL)), f"柱反曲點 距 A {Y_INF_COL.numerator}/{Y_INF_COL.denominator} m", "start", 14),
                          ((X_INF, float(H)), f"梁反曲點 距 B {f(X_INF)} m", "middle", 0)):
        cv.dot(p, 5.2, fill="#FFFFFF", stroke=C["accent"], w=2.6)
        cv.text_px(cv.X(p[0]) + dx, cv.Y(p[1]) - (0 if anc == "start" else 18), t, 12.5, C["accent"], anc, weight="700")
    cv.text_px(Wc / 2, Hc - 24, "最大值 +3.125（BC 跨內）；最小值 −3.0（B 點）；B 角兩桿受拉側在外側連續", 13, C["muted"])
    return compose([cv], path=f"{OUT}/{TAG}-fig-3-frame-bmd.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    fig2_bc_vm(); fig3_frame_bmd()
    print(f"θ_B = {TB}/EI, θ_C = {TC}/EI；M_AB={M_AB}, M_BA={M_BA}, M_BC={M_BC}, M_CB={M_CB}")
    print(f"V_B = {V_B}, x_max = {X_MAX}, M_max = {M_MAX}, 梁反曲點 = {X_INF:.4f}, 柱反曲點 = {Y_INF_COL}")

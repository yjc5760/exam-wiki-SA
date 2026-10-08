#!/usr/bin/env python3
import sys, os
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")
import glob as _g
for _d in _g.glob("/root/.claude/skills/synced/*/struct-diagram/scripts"):
    sys.path.insert(0, _d)
from structdraw import Canvas, C, FONT_M, compose, column_shape, beam_shape

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2018-2"

# ══ 解題結果（來自 SA-2018-2.md §4 Step1／Step5，符號約定：D1=u「向右」為正、
#    轉角與彎矩皆「逆時針」為正，與 structdraw 的全域 CCW 慣例一致，無需換號）══
# 幾何：A(0,2) B(0,1) C(1,1) D(1,0)，各段長 L=1，A 頂部固定、D 底部固定（Z 字型）
M_END = 1/24     # §4 Step5：六個端彎矩量值皆為 PL/24（M_AB, M_BA, M_BC, M_CB, M_CD, M_DC）
M_MID = 5/24      # 梁跨中最大彎矩 = 5PL/24（下方受拉）

# §4 Step4（2026-10-06 修正符號）：FEM_BC=+PL/8（逆時針）
#   D1=u=-PL^3/48EI（向左），D2=θ_B=-PL^2/24EI（順時針），D3=θ_C=+PL^2/24EI（逆時針）
# 比例：θ_B = 2u/L，θ_C = -2u/L
KS = 4.8                          # 繪圖放大：PL^3/EI → 圖面單位（L=1）
D_DRAW = -KS / 48                 # u = -PL^3/48EI → -0.10（向左）
TH_B_CCW = 2.0 * D_DRAW           # θ_B = 2u/L → 負（順時針）
TH_C_CCW = -2.0 * D_DRAW          # θ_C = -2u/L → 正（逆時針）

NA, NB, NC, ND = (0, 2), (0, 1), (1, 1), (1, 0)


def frame(cv, color=C["member"], w=6.5, dash=None):
    for s, e in ((NA, NB), (NB, NC), (NC, ND)):
        cv.line(s, e, color, w, dash=dash, cap="butt")


def ghost(cv):
    frame(cv, C["ghost"], 3.0, dash="6 5")


def fig1_frame():
    """題目重繪：Z 字型（點對稱）構架，取代低解析度截圖"""
    cv = Canvas(480, 560, sx=170, ox=140, oy=70, bg="#FFFFFF")
    frame(cv)
    cv.fixed_support(NA, ang=180)   # 頂部固定，牆面朝上
    cv.fixed_support(ND, ang=0)     # 底部固定
    cv.arrow((0.5, 1.35), (0.5, 1), C["load"], 3.6, 12)
    cv.math((0.5, 1), "P", 19, C["load"], "middle", dy=-72, weight="700")
    for p, lab, ax, ay in ((NA, "A", -20, 6), (NB, "B", -20, 8),
                            (NC, "C", 20, 8), (ND, "D", 20, 6)):
        cv.dot(p, 5.5); cv.text(p, lab, 16, C["text"], weight="700", dx=ax, dy=ay)
    cv.dim((0, 1), (0, 2), "L", off=-52, label_off=-14)
    cv.dim((1, 0), (1, 1), "L", off=52, label_off=14)
    cv.dim((0, 1), (1, 1), "L", off=64, label_off=17)
    cv.text_px(240, 524, "所有桿件 EI、L 相同；A、D 固定；B、C 剛接",
               13, C["muted"])
    cv.text_px(240, 544, "忽略軸向與剪力變形；Z 字型＝點對稱，跨中 P 仍引發側移 u",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


def fig2_dof():
    """自由度辨識：3 個獨立自由度 {u, θ_B, θ_C}"""
    cv = Canvas(760, 560, sx=155, ox=130, oy=70, bg="#FFFFFF")
    frame(cv, "#9AA4B2")
    cv.fixed_support(NA, ang=180); cv.fixed_support(ND, ang=0)
    cv.arrow((1.08, 1), (1.42, 1), C["deform"], 3.4, 12)
    cv.math((1.42, 1), "D_{1}=u", 18, C["deform"], "start", dx=9, weight="700")
    for p, lx, ly, nm in ((NB, -56, -6, "D_{2}=θ_{B}"), (NC, 40, 30, "D_{3}=θ_{C}")):
        cv.moment_arrow(p, r=26, ccw=True, color=C["accent"], w=2.8, span=235, start=205)
        cv.text_px(cv.X(p[0]) + lx, cv.Y(p[1]) + ly, nm, 17, C["accent"],
                   weight="700", italic=True, font=FONT_M)
    for p, lab, ax, ay in ((NA, "A", -20, 6), (NB, "B", 22, -8),
                            (NC, "C", -22, -8), (ND, "D", 20, 6)):
        cv.dot(p, 5.5, fill="#4A5568"); cv.text(p, lab, 15, C["text"], weight="700", dx=ax, dy=ay)
    cv.rect_px(500, 60, 232, 96, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(616, 84, "有效自由度只剩 3 個", 14, "#1D4ED8", weight="700")
    cv.text_px(616, 110, "{ u ,  θ_{B} ,  θ_{C} }", 18, "#1D4ED8", italic=True, font=FONT_M)
    cv.text_px(616, 138, "u_{B}=u_{C}（梁不伸縮）", 12.5, "#1D4ED8")
    cv.text_px(400, 508, "逆時針、向右為正（與 §4 Step1 定義一致）；忽略軸向變形 ⇒ v_{B}=v_{C}=0",
               12.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-dof.svg")


def beam_true(x0, y0, n=60):
    """梁 BC 真實撓曲＝端點轉角的 Hermite 形狀＋兩端固定梁跨中集中載重形狀"""
    pts = beam_shape((x0, y0), 1.0, TH_B_CCW, TH_C_CCW, n=n)
    out = []
    for (x, y) in pts:
        xi = x - x0
        t = min(xi, 1 - xi)
        vp = -KS * t * t * (3 - 4 * t) / 48      # 固定梁中點載重：PL^3/192EI＠中點
        out.append((x, y + vp))
    return out


def fig3_deflected_bmd():
    """變形形狀與彎矩圖：題目明確要求繪製的答案本體"""
    PW, PH = 430, 640

    a = Canvas(PW, PH, sx=170, ox=126, oy=144)
    a.panel("變形形狀（側移向左）", "柱：單曲率、剪力為零　梁：對稱下垂")
    ghost(a)
    # AB：A(頂,固定)；B(底) 隨 u 左移、順時針轉
    a.poly(column_shape((0, 1), 1.0, delta_top=0, theta_top=0,
                        delta_bot=D_DRAW, theta_bot=TH_B_CCW), C["deform"], 5.0)
    # CD：D(底,固定)；C(頂) 隨 u 左移、逆時針轉
    a.poly(column_shape((1, 0), 1.0, delta_top=D_DRAW, theta_top=TH_C_CCW,
                        delta_bot=0, theta_bot=0), C["deform"], 5.0)
    bt = beam_true(D_DRAW, 1)
    a.poly(bt, C["deform"], 5.0)
    a.fixed_support((0, 2), ang=180, size=17); a.fixed_support((1, 0), ang=0, size=17)
    ym = bt[len(bt)//2][1]
    a.arrow((D_DRAW + 0.5, 1.33), (D_DRAW + 0.5, ym + 0.02), C["load"], 3.2, 11)
    a.math((D_DRAW + 0.5, 1.33), "P", 16, C["load"], dx=12, dy=-4, weight="700")
    a.arrow((0.22, 1.12), (0.22 + D_DRAW * 1.6, 1.12), C["accent"], 2.6, 9)
    a.math((0.22, 1.12), "u", 15, C["accent"], "start", dx=6, dy=4, weight="700")
    a.text_px(PW/2, 545, "u = −PL³/48EI（向左）", 13, C["deform"], weight="700")
    a.text_px(PW/2, 570, "θB = −θC = −PL²/24EI（B 順時針、C 逆時針）", 13, C["deform"], weight="700")
    a.text_px(PW/2, 595, "M_AB+M_BA=0 → 柱剪力為零（單曲率）", 12, C["deform"], weight="700")

    b = Canvas(PW, PH, sx=170, ox=126, oy=144)
    b.panel("彎矩圖（繪於受拉側）", "柱、梁端全為 PL/24；梁中點 5PL/24")
    ms = 0.62
    Me, Mm = M_END * ms, M_MID * ms
    # AB 柱：M_AB=+PL/24、M_BA=−PL/24（逆時針為正）⇒ 剪力為零、全段均勻 → 右側（內側）受拉
    b.polygon([(0, 2), (Me, 2), (Me, 1), (0, 1)], C["fill_m"], C["bmd"], 2)
    # CD 柱：M_CD=+PL/24、M_DC=−PL/24 ⇒ 全段均勻 → 右側（外側）受拉
    b.polygon([(1, 1), (1 + Me, 1), (1 + Me, 0), (1, 0)], C["fill_m"], C["bmd"], 2)
    # BC 梁：B、C 端 PL/24 上方受拉（hogging），跨中 5PL/24 下方受拉（sagging）
    # 端點與跨中彎矩異號 ⇒ 彎矩圖需穿越梁軸線；交點由線性內插公式算出（非目測）
    xc = 0.5 * Me / (Me + Mm)
    b.polygon([(0, 1), (0, 1 + Me), (xc, 1)], C["fill_m"], C["bmd"], 2)
    b.polygon([(1, 1), (1, 1 + Me), (1 - xc, 1)], C["fill_m"], C["bmd"], 2)
    b.polygon([(xc, 1), (0.5, 1 - Mm), (1 - xc, 1)], C["fill_m"], C["bmd"], 2)
    frame(b, "#4A5568", 3.4)
    b.fixed_support((0, 2), ang=180, size=17); b.fixed_support((1, 0), ang=0, size=17)
    b.dot((0.5, 1 - Mm), 4.6, fill="#FFFFFF", stroke=C["bmd"], w=2.4)
    b.math_px(b.X(Me) + 6, b.Y(1.5), "PL/24", 12.5, C["bmd"], "start", weight="700")
    b.math_px(b.X(1 + Me) + 6, b.Y(0.5), "PL/24", 12.5, C["bmd"], "start", weight="700")
    b.math_px(b.X(0) + 4, b.Y(1 + Me) - 4, "PL/24", 11.5, C["bmd"], "start", weight="700")
    b.math_px(b.X(1) - 4, b.Y(1 + Me) - 4, "PL/24", 11.5, C["bmd"], "end", weight="700")
    b.math_px(b.X(0.5), b.Y(1 - Mm) + 22, "5PL/24", 12.5, C["bmd"], weight="700")
    b.text_px(PW/2, 545, "節點平衡：M_BA+M_BC=0 ✓　M_CB+M_CD=0 ✓", 12, C["bmd"], weight="700")
    b.text_px(PW/2, 570, "梁中點 M = PL/4 − PL/24 = 5PL/24", 12.5, C["bmd"], weight="700")

    compose([a, b], title="解出 u, θ_{B}, θ_{C} 之後：變形形狀與彎矩圖互相檢核",
            note="兩張圖若對不上（例如柱有剪力、梁端彎矩不等），前面矩陣必有錯",
            path=f"{OUT}/{TAG}-fig-3-deflected-bmd.svg")
    return f"{OUT}/{TAG}-fig-3-deflected-bmd.svg"


FIGURES = [
    (fig1_frame,          "§1",   "Z 字型誤看成鏡射對稱 → 誤判 u=0"),
    (fig2_dof,             "§3",  "自由度數目/方向弄錯 → K 矩陣階數或行列錯位"),
    (fig3_deflected_bmd,   "§4 Step5", "FEM 正負號寫反 → 側移方向、柱受拉側全反；梁中點彎矩算錯"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, section, catches in FIGURES:
        print(f"{os.path.basename(fn()):<40} {section:<10} 攔：{catches}")

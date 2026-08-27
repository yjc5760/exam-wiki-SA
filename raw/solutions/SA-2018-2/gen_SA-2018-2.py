#!/usr/bin/env python3
import sys, os
sys.path.insert(0, "/root/.claude/skills/synced/struct-diagram/scripts")
from structdraw import Canvas, C, FONT_M, compose, column_shape, beam_shape

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2018-2"

# ══ 解題結果（來自 SA-2018-2.md §4 Step1／Step5，符號約定：D1=u「向右」為正、
#    轉角與彎矩皆「逆時針」為正，與 structdraw 的全域 CCW 慣例一致，無需換號）══
# 幾何：A(0,2) B(0,1) C(1,1) D(1,0)，各段長 L=1，A 頂部固定、D 底部固定（Z 字型）
M_END = 1/24     # §4 Step5：六個端彎矩量值皆為 PL/24（M_AB, M_BA, M_BC, M_CB, M_CD, M_DC）
M_MID = 5/24      # 梁跨中最大彎矩 = 5PL/24（下方受拉）

# §4 Step4：D1=u=PL^3/48EI，D2=θ_B=+PL^2/24EI（逆時針），D3=θ_C=-PL^2/24EI（順時針）
# 比例：θ/u = (PL^2/24EI)/(PL^3/48EI) = 2/L
D_DRAW = 0.10                    # 繪圖側移量（純視覺放大，不影響上列任何物理量）
TH_MAG = 2.0 * D_DRAW             # |θ_B|=|θ_C| 對應之繪圖角度
TH_B_CCW = +TH_MAG                # θ_B = +PL^2/24EI，逆時針為正 → 取正
TH_C_CCW = -TH_MAG                # θ_C = -PL^2/24EI，逆時針為正 → 取負（即順時針）

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


def fig3_deflected_bmd():
    """變形形狀與彎矩圖：題目明確要求繪製的答案本體"""
    PW, PH = 430, 640

    a = Canvas(PW, PH, sx=170, ox=126, oy=144)
    a.panel("變形形狀（側移模式）", "柱：純彎曲、剪力為零　梁：反對稱")
    ghost(a)
    # AB：A(頂,固定) 為 column_shape 的「top」；B(底,自由) 為「base」
    a.poly(column_shape((0, 1), 1.0, delta_top=0, theta_top=0,
                        delta_bot=D_DRAW, theta_bot=TH_B_CCW), C["deform"], 5.0)
    # CD：D(底,固定) 為「base」；C(頂,自由) 為「top」
    a.poly(column_shape((1, 0), 1.0, delta_top=D_DRAW, theta_top=TH_C_CCW,
                        delta_bot=0, theta_bot=0), C["deform"], 5.0)
    a.poly(beam_shape((D_DRAW, 1), 1.0, TH_B_CCW, TH_C_CCW), C["deform"], 5.0)
    a.fixed_support((0, 2), ang=180, size=17); a.fixed_support((1, 0), ang=0, size=17)
    a.dot((D_DRAW + 0.5, 1), 5.0, fill="#FFFFFF", stroke=C["accent"], w=2.6)
    a.math_px(a.X(D_DRAW + 0.5), a.Y(1) + 22, "梁中點：反曲點", 12, C["accent"], weight="700")
    a.arrow((D_DRAW - 0.30, 1.30), (D_DRAW, 1), C["load"], 3.2, 11)
    a.math((D_DRAW - 0.30, 1.30), "P", 16, C["load"], dx=-8, dy=-10, weight="700")
    a.math_px(PW/2, 545, "u=PL^{3}/48EI", 13, C["deform"], weight="700")
    a.math_px(PW/2, 570, "θ_{B}=-θ_{C}=PL^{2}/24EI", 13, C["deform"], weight="700")
    a.text_px(PW/2, 595, "M_AB+M_BA=0 → 柱剪力為零（純彎曲）", 12, C["deform"], weight="700")

    b = Canvas(PW, PH, sx=170, ox=126, oy=144)
    b.panel("彎矩圖（繪於受拉側）", "柱、梁端全為 PL/24；梁中點 5PL/24")
    ms = 0.62
    Me, Mm = M_END * ms, M_MID * ms
    # AB 柱：M_AB=M_BA=PL/24（同號、剪力為零 ⇒ 全段均勻彎矩）→ 左側/外側受拉
    b.polygon([(0, 2), (-Me, 2), (-Me, 1), (0, 1)], C["fill_m"], C["bmd"], 2)
    # CD 柱：M_CD=M_DC=PL/24（畫在柱左側/內側，依 md 圖說）
    b.polygon([(1, 1), (1 - Me, 1), (1 - Me, 0), (1, 0)], C["fill_m"], C["bmd"], 2)
    # BC 梁：B、C 端 PL/24 上方受拉（負彎矩／hogging），跨中 5PL/24 下方受拉（正彎矩／sagging）
    # 端點與跨中彎矩異號 ⇒ 彎矩圖需穿越梁軸線；交點由線性內插公式算出（非目測）
    xc = 0.5 * Me / (Me + Mm)          # B→跨中之零彎矩點（相對 B 的 x 距離）
    b.polygon([(0, 1), (0, 1 + Me), (xc, 1)], C["fill_m"], C["bmd"], 2)
    b.polygon([(1, 1), (1, 1 + Me), (1 - xc, 1)], C["fill_m"], C["bmd"], 2)
    b.polygon([(xc, 1), (0.5, 1 - Mm), (1 - xc, 1)], C["fill_m"], C["bmd"], 2)
    frame(b, "#4A5568", 3.4)
    b.fixed_support((0, 2), ang=180, size=17); b.fixed_support((1, 0), ang=0, size=17)
    b.dot((0.5, 1 - Mm), 4.6, fill="#FFFFFF", stroke=C["bmd"], w=2.4)
    b.math_px(b.X(-Me) - 6, b.Y(1.5), "PL/24", 12.5, C["bmd"], "end", weight="700")
    b.math_px(b.X(1 - Me) - 6, b.Y(0.5), "PL/24", 12.5, C["bmd"], "end", weight="700")
    b.math_px(b.X(0) + 4, b.Y(1 + Me) - 4, "PL/24", 11.5, C["bmd"], "start", weight="700")
    b.math_px(b.X(1) - 4, b.Y(1 + Me) - 4, "PL/24", 11.5, C["bmd"], "end", weight="700")
    b.math_px(b.X(0.5), b.Y(1 - Mm) - 14, "5PL/24", 12.5, C["bmd"], weight="700")
    b.text_px(PW/2, 545, "節點平衡：M_BA+M_BC=0 ✓　M_CD+M_CB=0 ✓", 12, C["bmd"], weight="700")
    b.text_px(PW/2, 570, "梁中點 M = PL/4 − PL/24 = 5PL/24", 12.5, C["bmd"], weight="700")

    compose([a, b], title="解出 u, θ_{B}, θ_{C} 之後：變形形狀與彎矩圖互相檢核",
            note="兩張圖若對不上（例如柱有剪力、梁端彎矩不等），前面矩陣必有錯",
            path=f"{OUT}/{TAG}-fig-3-deflected-bmd.svg")
    return f"{OUT}/{TAG}-fig-3-deflected-bmd.svg"


FIGURES = [
    (fig1_frame,          "§1",   "Z 字型誤看成鏡射對稱 → 誤判 u=0"),
    (fig2_dof,             "§3",  "自由度數目/方向弄錯 → K 矩陣階數或行列錯位"),
    (fig3_deflected_bmd,   "§4 Step5", "柱端彎矩正負號寫反、梁中點彎矩算錯"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, section, catches in FIGURES:
        print(f"{os.path.basename(fn()):<40} {section:<10} 攔：{catches}")

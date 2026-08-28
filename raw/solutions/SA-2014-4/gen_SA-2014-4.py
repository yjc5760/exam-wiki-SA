#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SA-2014-4 L 型剛架最小功法 — 解題圖解產生腳本

用法： python3 gen_SA-2014-4.py [輸出目錄]
"""
import sys, os, glob
_c = sorted(glob.glob(os.path.expanduser("~/.claude/skills/**/struct-diagram/scripts"), recursive=True))
sys.path.insert(0, _c[0] if _c else "/root/.claude/skills/synced/struct-diagram/scripts")

from structdraw import Canvas, C, FONT_M, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2014-4"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SA-2014-4.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §1 幾何與載重
L_AC, L_CD = 12.0, 12.0        # AC 梁長、CD 柱長 (m)
X_B        = 6.0               # B 點距 A (m)
P          = 20.0              # B 點向下集中載重 (kN)
EI         = 1000.0            # AC 桿 EI (kN-m^2)；CD 桿為 2EI，本題用不到

# §4 Step 2：最小功法解得之 D 點垂直反力
R = 6.25                       # kN（向上）

# §4 Step 3–4：C 點轉角
THETA_C = 0.09                 # rad（逆時針）

# ── 由上列結果算出的圖形幾何（皆為算式，非硬寫）──────────
# 斷面內彎矩（下側受拉為正），x 由 A 起算
def M_beam(x):
    """AC 梁斷面內彎矩（下側受拉為正），取斷面右側自由體：R 上舉、P 下壓。"""
    m = R*(L_AC - x)
    if x <= X_B:
        m -= P*(X_B - x)
    return m

M_A    = M_beam(0.0)                    # = -45.0 kN-m（上緣受拉）
M_B    = M_beam(X_B)                    # = +37.5 kN-m（下緣受拉）
X_ZERO = (P*X_B - R*L_AC) / (P - R)     # 解 R(L-x) - P(x_B - x) = 0 → 反曲點

# 梁撓度（EI v'' = M，A 端固定 v=v'=0），全部由 R、P、EI 積分而來
def v_beam(x):
    if x <= X_B:
        return (2.291666666666667*x**3 - 22.5*x**2)/EI
    return (-1.0416666666666667*x**3 + 37.5*x**2 - 360.0*x + 720.0)/EI
V_MAX = min(v_beam(i*L_AC/400) for i in range(401))
U_D   = THETA_C * L_CD                  # 柱無彎矩 ⇒ 剛體轉動，D 點水平位移
AMP   = 2.0                             # 變形圖放大倍率（純視覺）


def _sanity():
    assert abs(M_A + 45.0) < 1e-9 and abs(M_B - 37.5) < 1e-9, (M_A, M_B)
    assert abs(X_ZERO - 3.2727272727) < 1e-6, X_ZERO
    assert abs(v_beam(L_AC)) < 1e-9, v_beam(L_AC)          # v_C = 0（D 為滾支承）
    slope = (v_beam(L_AC) - v_beam(L_AC-1e-5))/1e-5
    assert abs(slope - THETA_C) < 1e-4, slope              # θ_C = 0.09 rad 逆時針


def _frame(cv, col=C["member"], w=6.5, dash=None):
    cv.line((0, 0), (L_AC, 0), col, w, dash=dash, cap="butt")
    cv.line((L_AC, 0), (L_AC, -L_CD), col, w, dash=dash, cap="butt")


def _nodes(cv):
    for (px, py), lab, ax, ay in (((0, 0), "A", -8, -20), ((X_B, 0), "B", 0, -22),
                                  ((L_AC, 0), "C", 22, -14), ((L_AC, -L_CD), "D", 22, -6)):
        cv.dot((px, py), 5.5)
        cv.text_px(cv.X(px)+ax, cv.Y(py)+ay, lab, 17, C["text"], weight="700")


# ══════════════════════════════════════════════════════════
def fig1_frame_fbd():
    """題目重繪＋CD 柱自由體：把「2EI 用不到」變成看得見的力學事實"""
    W, H = 580, 540
    # ── 左：題目重繪 ──
    a = Canvas(W, H, sx=22.0, ox=130, oy=390, bg="#FFFFFF")
    _frame(a)
    a.fixed_support((0, 0), 90)
    a.roller_support((L_AC, -L_CD), 0)
    a.arrow((X_B, 2.6), (X_B, 0), C["load"], 3.4, 12)
    a.math_px(a.X(X_B), a.Y(2.6)-16, f"P = {P:.0f} kN", 15, C["load"], weight="700")
    a.dim((0, 0), (X_B, 0), "6 m", off=46, label_off=15)
    a.dim((X_B, 0), (L_AC, 0), "6 m", off=46, label_off=15)
    a.dim((L_AC, 0), (L_AC, -L_CD), "12 m", off=-72, label_off=-18)
    a.math((L_AC*0.25, 0), "EI", 16, C["muted"], dy=-26)
    a.math((L_AC, -L_CD*0.62), "2EI", 16, C["muted"], "start", dx=18)
    _nodes(a)
    a.text_px(W/2, 30, "題目重繪", 16, C["text"], weight="700")
    a.text_px(W/2, H-28, f"A 固接；D 為水平面滾支承；EI = {EI:.0f} kN-m²（AC）、2EI（CD）",
              13, C["muted"])

    # ── 右：CD 柱自由體（切斷面必須同時標 N / V / M）──
    b = Canvas(W, H, sx=22.0, ox=130, oy=395, bg="#FFFFFF")
    b.line((0, 0), (L_AC, 0), C["ghost"], 4.0, dash="7 6", cap="butt")
    b.line((L_AC, 0), (L_AC, -L_CD), C["member"], 6.5, cap="butt")
    b.roller_support((L_AC, -L_CD), 0)
    box = [(L_AC-1.4, 1.4), (L_AC+1.4, 1.4), (L_AC+1.4, -L_CD-1.4), (L_AC-1.4, -L_CD-1.4)]
    for k in range(4):
        b.line(box[k], box[(k+1) % 4], C["accent"], 1.6, dash="6 5")
    b.arrow((L_AC, 3.2), (L_AC, 1.7), C["deform"], 3.0, 10)
    b.text_px(b.X(L_AC), b.Y(3.2)-16, f"N = R = {R:.2f} kN（軸壓）", 14, C["deform"], weight="700")
    b.math_px(b.X(L_AC)-52, b.Y(-1.0), "V = 0", 14.5, C["muted"], "end", weight="700")
    b.math_px(b.X(L_AC)-52, b.Y(-2.6), "M = 0", 14.5, C["muted"], "end", weight="700")
    b.text_px(b.X(L_AC)-52, b.Y(-4.2), "（切斷面內力）", 12.5, C["muted"], "end")
    b.arrow((L_AC, -L_CD-2.6), (L_AC, -L_CD-0.7), C["load"], 3.2, 11)
    b.math_px(b.X(L_AC)+18, b.Y(-L_CD-1.8), f"R = {R:.2f} kN", 14.5, C["load"], "start", weight="700")
    b.math_px(b.X(L_AC)-58, b.Y(-L_CD-0.2), "D_{x} = 0", 14.5, C["load"], "end", weight="700")
    b.rect_px(30, 252, 258, 122, "#FFF6F1", 12, "#F0C9B8", 1.3)
    b.text_px(46, 278, "水平面滾支承 ⇒ D_{x} = 0", 13.5, "#9A3412", "start", weight="700")
    for k, t in enumerate(["柱上任一斷面對 D 取矩，力臂為 0",
                           "⇒ 全柱 M ≡ 0 ⇒ 應變能 U_{CD} = 0",
                           "⇒ 題目給的 2EI 完全用不到"]):
        b.text_px(46, 306 + k*24, t, 12.5, "#9A3412", "start")
    for (px, py), lab, ax, ay in (((L_AC, 0), "C", 22, -12), ((L_AC, -L_CD), "D", 26, -12)):
        b.dot((px, py), 5.5); b.text_px(b.X(px)+ax, b.Y(py)+ay, lab, 17, C["text"], weight="700")
    b.text_px(W/2, 30, "CD 柱自由體（切斷面標 N / V / M 三者）", 16, C["text"], weight="700")
    b.text_px(W/2, H-28, "柱只受軸壓，不受彎——這是本題唯一要看穿的事", 13, C["muted"])

    path = f"{OUT}/{TAG}-fig-1-frame-fbd.svg"
    compose([a, b], cols=2, path=path,
            title="題目重繪與 CD 柱自由體：2EI 是誘餌",
            note="若誤以為 CD 受彎而假設了不存在的水平反力，靜不定度、彎矩方程式與答案會全盤皆錯。")
    return path


# ══════════════════════════════════════════════════════════
def fig2_bmd():
    """彎矩圖（繪於受拉側）"""
    W, H = 760, 580
    cv = Canvas(W, H, sx=24.0, ox=210, oy=370, bg="#FFFFFF")
    _frame(cv, C["ghost"], 5.0)
    cv.fixed_support((0, 0), 90); cv.roller_support((L_AC, -L_CD), 0)
    Mmax = max(abs(M_A), abs(M_B))
    k = 2.6 / Mmax                       # 每 1 kN-m 對應的模型長度
    n = 200
    pts = [(i*L_AC/n, -M_beam(i*L_AC/n)*k) for i in range(n+1)]   # 正彎矩(下緣受拉)畫在下方
    cv.polygon([(0, 0)] + pts + [(L_AC, 0)], C["fill_m"], C["bmd"], 2.6)
    cv.line((0, 0), (L_AC, 0), C["muted"], 1.6)
    # 柱：M ≡ 0
    cv.line((L_AC, 0), (L_AC, -L_CD), C["bmd"], 3.4)
    cv.math_px(cv.X(L_AC)+18, cv.Y(-L_CD/2), "M_{CD} ≡ 0", 15, C["bmd"], "start", weight="700")
    # 關鍵值
    cv.text_px(cv.X(0)+8, cv.Y(-M_A*k)-18,
               f"M_A = {M_A:+.1f} kN-m（上緣受拉）".replace("-", "\u2212"),
               14, C["bmd"], "start", weight="700")
    cv.text_px(cv.X(X_B), cv.Y(-M_B*k)+24, f"M_B = +{M_B:.1f} kN-m（下緣受拉）", 14, C["bmd"], weight="700")
    cv.dot((X_ZERO, 0), 5.6, fill="#FFFFFF", stroke=C["accent"], w=3.0)
    cv.poly([(X_ZERO, 0), (X_ZERO, 1.3), (8.6, 1.3)], C["accent"], 1.4, dash="4 4")
    cv.text_px(cv.X(8.8), cv.Y(1.3), f"反曲點  x = {X_ZERO:.3f} m", 13.5, C["accent"], "start", weight="700")
    cv.math_px(cv.X(L_AC)+18, cv.Y(0)+2, "M_{C} = 0", 14.5, C["accent"], "start", weight="700")
    _nodes(cv)
    cv.legend(30, H-150, [(C["bmd"], "彎矩圖（繪於受拉側）"), (C["ghost"], "構材原位置"),
                          (C["accent"], "反曲點 / 零彎矩")])
    cv.text_px(W/2, 34, "彎矩圖 BMD（繪於受拉側，單位 kN-m）", 17, C["text"], weight="700")
    cv.text_px(W/2, 58, f"R = {R:.2f} kN 由最小功法解得；圖上每個數值都由 R 與 P 算出", 13, C["muted"])
    cv.text_px(W/2, H-24, "節點 C：梁端彎矩 = 0、柱端彎矩 = 0 ⇒ 自動平衡；柱全段無彎矩是本題的關鍵事實。",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-bmd.svg")


# ══════════════════════════════════════════════════════════
def fig3_deflected():
    """變形形狀與 θ_C 轉向"""
    W, H = 800, 580
    cv = Canvas(W, H, sx=24.0, ox=200, oy=390, bg="#FFFFFF")
    _frame(cv, C["ghost"], 4.2, dash="7 6")
    cv.fixed_support((0, 0), 90); cv.roller_support((L_AC, -L_CD), 0)
    n = 200
    cv.poly([(i*L_AC/n, v_beam(i*L_AC/n)*AMP) for i in range(n+1)], C["deform"], 5.0)
    # 柱：M ≡ 0 ⇒ 保持直線，繞 C 剛體轉動 θ_C
    cv.poly([(L_AC + THETA_C*AMP*t, -t) for t in [i*L_CD/40 for i in range(41)]],
            C["deform"], 5.0)
    cv.arrow((X_B, 3.4), (X_B, 0), C["load"], 3.2, 11)
    cv.text_px(cv.X(X_B), cv.Y(3.4)-16, f"P = {P:.0f} kN", 14.5, C["load"], weight="700")
    # θ_C（逆時針）
    cv.moment_arrow((L_AC, 0.75), r=30, ccw=True, color=C["accent"], w=2.8, span=205, start=15)
    cv.text_px(cv.X(L_AC)+54, cv.Y(0)-44, f"θ_C = {THETA_C} rad（逆時針）",
               15, C["accent"], "start", weight="700")
    # v_C = 0
    cv.dot((L_AC, 0), 6.0, fill="#FFFFFF", stroke=C["bmd"], w=3.0)
    cv.text_px(cv.X(L_AC)+18, cv.Y(0)+30, "v_C = 0", 14, C["bmd"], "start", weight="700")
    cv.text_px(cv.X(L_AC)+18, cv.Y(0)+50, "（D 為滾支承 + 柱軸向不變形）", 12.5, C["muted"], "start")
    # 最大撓度
    xs = [i*L_AC/400 for i in range(401)]
    xm = min(xs, key=v_beam)
    cv.line((xm, 0), (xm, v_beam(xm)*AMP), C["accent"], 1.4, dash="4 4")
    cv.text_px(cv.X(xm), cv.Y(v_beam(xm)*AMP)+26,
               f"v_{{max}} = {v_beam(xm):.3f} m（x = {xm:.2f} m）", 13.5, C["accent"], weight="700")
    # D 水平位移
    cv.arrow((L_AC, -L_CD-1.6), (L_AC + U_D*AMP, -L_CD-1.6), C["deform"], 2.8, 10)
    cv.text_px(cv.X(L_AC + U_D*AMP)+12, cv.Y(-L_CD-1.6),
               f"u_D = θ_C × {L_CD:.0f} = {U_D:.2f} m", 13.5, C["deform"], "start", weight="700")
    _nodes(cv)
    cv.text_px(W/2, 34, f"變形形狀（位移放大 {AMP:.0f} 倍）", 17, C["text"], weight="700")
    cv.text_px(W/2, 58, "梁為三次／四次曲線；柱因 M ≡ 0 保持「直線」，僅隨 C 剛體轉動",
               13, C["muted"])
    cv.text_px(W/2, H-24,
               "柱若在圖上被畫成彎曲，代表誤認 CD 有彎矩——與 §4 的 M_{CD} = 0 自相矛盾。",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-3-deflected.svg")


FIGURES = [
    (fig1_frame_fbd, "攔下「看到 2EI 就假設 CD 受彎」"),
    (fig2_bmd,       "攔下受拉側畫反、以及在 CD 上畫出不存在的彎矩"),
    (fig3_deflected, "攔下把柱畫成曲線、θ_C 轉向畫反、忘記 v_C = 0"),
]

if __name__ == "__main__":
    _sanity()
    for fn, why in FIGURES:
        print(f"{fn():<52}  ← {why}")

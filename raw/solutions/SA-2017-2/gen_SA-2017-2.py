#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SA-2017-2 兩端固定＋內鉸梁的最小功法 — 解題圖解產生腳本

用法： python3 gen_SA-2017-2.py [輸出目錄]
"""
import sys, os, glob
_c = sorted(glob.glob(os.path.expanduser("~/.claude/skills/**/struct-diagram/scripts"), recursive=True))
sys.path.insert(0, _c[0] if _c else "/root/.claude/skills/synced/struct-diagram/scripts")
from structdraw import Canvas, C, FONT, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2017-2"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SA-2017-2.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §4.5 / §4.6 最終公式（斷面內彎矩，下側受拉為正；兩者恆為負 = hogging）
def Ma_of(m, n, w=1.0):
    return -w*m*(m+n)*(m**2 - 2*m*n + 3*n**2) / (8*(m**2 - m*n + n**2))

def Mb_of(m, n, w=1.0):
    return -w*n*(m+n)*(3*m**2 - 2*m*n + n**2) / (8*(m**2 - m*n + n**2))

FIXED_FIXED = 1.0/12.0        # 無內鉸的兩端固定梁：wL²/12（對照基準）

# §4.8 代表案例（用來畫三聯圖；改這三個數字整組圖會跟著變）
L_REP, W_REP, BETA = 10.0, 10.0, 0.40
M_REP, N_REP = BETA*L_REP, (1-BETA)*L_REP
X_REP  = Ma_of(M_REP, N_REP, W_REP)                    # = M_a
RA_REP = W_REP*M_REP/2 - X_REP/M_REP                   # §4.2 式(1)
RB_REP = W_REP*L_REP - RA_REP                          # §4.2 式(2)
MB_REP = Mb_of(M_REP, N_REP, W_REP)

def V_rep(x):  return RA_REP - W_REP*x
def M_rep(x):  return RA_REP*x + X_REP - W_REP*x*x/2
X_V0 = RA_REP/W_REP                                     # 剪力零點
M_SPAN_MAX = M_rep(X_V0)


def _sanity():
    # 對稱檢查：m = n 時 M_a = M_b = -wm²/2 = -wL²/8
    assert abs(Ma_of(0.5, 0.5) - (-0.125)) < 1e-12
    assert abs(Ma_of(0.5, 0.5) - Mb_of(0.5, 0.5)) < 1e-12
    # 內鉸貼近 b 端：M_a → -wL²/8
    assert abs(Ma_of(1-1e-9, 1e-9) + 0.125) < 1e-6
    # 代表案例：鉸點彎矩必須為零、兩端彎矩與公式一致
    assert abs(M_rep(M_REP)) < 1e-9, M_rep(M_REP)
    assert abs(M_rep(L_REP) - MB_REP) < 1e-9, (M_rep(L_REP), MB_REP)
    assert abs(M_rep(0.0) - X_REP) < 1e-12
    # 內鉸使對稱情況的固端彎矩「變大」——本題 §5 訂正過的關鍵事實
    assert abs(Ma_of(0.5, 0.5)) > FIXED_FIXED


# ══════════════════════════════════════════════════════════
def fig1_beam():
    """題目重繪：內鉸的位置與靜不定度"""
    W, H = 820, 420
    L = 10.0
    cv = Canvas(W, H, sx=52.0, ox=150, oy=196, bg="#FFFFFF")
    cv.line((0, 0), (L, 0), C["member"], 7.0, cap="butt")
    cv.fixed_support((0, 0), 90)
    cv.fixed_support((L, 0), -90)
    cv.udl((0, 0), (L, 0), 0.95, n=13, label=None)
    cv.text_px(cv.X(L/2), cv.Y(0.95)-18, "w（向下均佈，全跨）", 14.5, C["load"], weight="700")
    # 內鉸
    xc = BETA*L
    cv.circle((xc, 0), 0.17, fill="#FFFFFF", stroke=C["accent"], w=3.4)
    cv.text_px(cv.X(xc), cv.Y(0)+34, "c：內鉸（M = 0，剪力仍傳遞）", 13.5, C["accent"], weight="700")
    cv.dim((0, 0), (xc, 0), "m", off=88, label_off=16)
    cv.dim((xc, 0), (L, 0), "n", off=88, label_off=16)
    cv.dim((0, 0), (L, 0), "L = m + n", off=132, label_off=16)
    for x, lab, dxp in ((0, "a", -6), (L, "b", 6)):
        cv.dot((x, 0), 5.5)
        cv.text_px(cv.X(x)+dxp, cv.Y(0)-26, lab, 17, C["text"], weight="700")
    # 靜不定度
    cv.rect_px(W-266, 54, 246, 118, "#F5F7FA", 12, C["border"], 1.3)
    cv.text_px(W-248, 78, "靜不定度", 13.5, C["text"], "start", weight="700")
    for i, t in enumerate(["未知反力 R_a、M_a、R_b、M_b：4 個",
                           "整體平衡：2 條", "內鉸條件 M_c = 0：1 條",
                           "⇒ i = 4 − 3 = 1（一度靜不定）"]):
        cv.text_px(W-248, 102 + i*21, t, 12.5,
                   C["accent"] if i == 3 else C["muted"], "start",
                   weight="700" if i == 3 else "400")
    cv.text_px(W/2, 30, "題目重繪（向量版）", 17, C["text"], weight="700")
    cv.text_px(W/2, H-24,
               "有鉸不等於靜定：鉸只提供一條方程式，兩端固定梁仍剩一度靜不定。", 13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-beam.svg")


# ══════════════════════════════════════════════════════════
def fig2_curve():
    """固端彎矩隨鉸點位置的變化，與「無內鉸」基準對照"""
    W, H = 900, 580
    Lm, Rm, Tm, Bm = 108, 236, 96, 92
    XMAX, YMAX = 1.0, 0.145
    kx = (W-Lm-Rm)/XMAX
    ky = (H-Tm-Bm)/YMAX
    cv = Canvas(W, H, sx=1.0, bg="#FFFFFF")
    def PX(b, v): return (Lm + b*kx, H - Bm - v*ky)
    def seg(a, b, col, w=3.4, dash=None):
        (x0, y0), (x1, y1) = PX(*a), PX(*b)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        cv.parts.append(f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" '
                        f'stroke="{col}" stroke-width="{w}" stroke-linecap="round"{d}/>')
    def curve(f, col, w=3.6):
        pts = []
        for i in range(1, 1000):
            b = i/1000.0
            pts.append("%.2f,%.2f" % PX(b, abs(f(b, 1-b))))
        cv.parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{col}" '
                        f'stroke-width="{w}" stroke-linejoin="round"/>')
    # 軸
    seg((0, 0), (XMAX, 0), C["muted"], 1.8); seg((0, 0), (0, YMAX), C["muted"], 1.8)
    for b in (0, 0.2, 0.4, 0.6, 0.8, 1.0):
        x, y = PX(b, 0); cv.text_px(x, y+20, f"{b:.1f}", 12, C["muted"])
        cv.parts.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+6}" stroke="{C["muted"]}" stroke-width="1.4"/>')
    for v in (0, 0.025, 0.05, 0.075, 0.10, 0.125):
        x, y = PX(0, v); cv.text_px(x-12, y, f"{v:.3f}", 12, C["muted"], "end")
        cv.parts.append(f'<line x1="{x-6}" y1="{y}" x2="{x}" y2="{y}" stroke="{C["muted"]}" stroke-width="1.4"/>')
    cv.text_px(Lm + (W-Lm-Rm)/2, H-32, "鉸點位置　m / L", 14, C["muted"])
    cv.parts.append(f'<text x="34" y="{Tm+170}" font-size="14" fill="{C["muted"]}" '
                    f'transform="rotate(-90 34 {Tm+170})" text-anchor="middle" '
                    f'font-family="{FONT}">固端彎矩 / (w L²)</text>')
    # 基準線
    seg((0, FIXED_FIXED), (XMAX, FIXED_FIXED), C["muted"], 2.6, dash="8 6")
    x, y = PX(0.005, FIXED_FIXED)
    cv.text_px(x+4, y-14, f"wL²/12 = {FIXED_FIXED:.4f}", 12.5, C["muted"], "start", weight="700")
    cv.text_px(x+4, y+16, "（無內鉸的兩端固定梁）", 12, C["muted"], "start")
    curve(Ma_of, C["bmd"]); curve(Mb_of, C["deform"])
    # 對稱點（標註放在下方空白帶，以虛線引出）
    xp, yp = PX(0.5, abs(Ma_of(0.5, 0.5)))
    ax_, ay_ = PX(0.175, 0.052)
    seg((0.5, abs(Ma_of(0.5, 0.5))), (0.36, 0.056), C["accent"], 1.4, dash="4 4")
    cv.parts.append(f'<circle cx="{xp:.2f}" cy="{yp:.2f}" r="6.4" fill="#FFFFFF" '
                    f'stroke="{C["accent"]}" stroke-width="3"/>')
    cv.text_px(ax_, ay_, "m = n（鉸在跨中）", 13.5, C["accent"], "start", weight="700")
    cv.text_px(ax_, ay_+21, f"M_a = M_b = wL²/8 = {abs(Ma_of(0.5,0.5)):.4f} wL²", 13,
               C["accent"], "start", weight="700")
    cv.text_px(ax_, ay_+42, "比無內鉸大 50%", 13, C["accent"], "start")
    # 兩條曲線的標籤
    x, y = PX(0.30, abs(Ma_of(0.30, 0.70))); cv.text_px(x-14, y-10, "|M_a|（a 端）", 14, C["bmd"], "end", weight="700")
    x, y = PX(0.72, abs(Mb_of(0.72, 0.28))); cv.text_px(x+14, y-6, "|M_b|（b 端）", 14, C["deform"], "start", weight="700")
    # 低於基準的區間
    xp, yp = PX(0.75, abs(Ma_of(0.75, 0.25)))
    seg((0.75, abs(Ma_of(0.75, 0.25))), (0.70, 0.058), C["bmd"], 1.4, dash="4 4")
    cv.parts.append(f'<circle cx="{xp:.2f}" cy="{yp:.2f}" r="5.4" fill="#FFFFFF" '
                    f'stroke="{C["bmd"]}" stroke-width="2.8"/>')
    bx_, by_ = PX(0.575, 0.052)
    cv.text_px(bx_, by_, f"m/L = 0.75 時 |M_a| = {abs(Ma_of(0.75,0.25)):.4f} wL²", 12.5,
               C["bmd"], "start", weight="700")
    cv.text_px(bx_, by_+20, "少數幾段區間才小於 wL²/12 —— 沒有單調規律", 12.5, C["muted"], "start")
    cv.text_px(W/2, 34, "內鉸會讓固端彎矩變小嗎？——不會，多數情況反而變大", 17, C["text"], weight="700")
    cv.text_px(W/2, 58, "曲線由 §4.5、§4.6 的封閉解直接繪出，非示意圖", 13, C["muted"])
    cv.text_px(W/2, H-10,
               "以「應小於 wL²/12」來自我驗算會把正確答案判成錯的；可靠的驗算是 §4.6 的對稱性與 m ↔ n 對調。",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-curve.svg")


# ══════════════════════════════════════════════════════════
def fig3_vm():
    """代表案例 m = 0.4L 的載重／剪力／彎矩三聯圖"""
    Wp, Hp = 820, 230
    sx = (Wp - 210)/L_REP
    ox = 128
    n = 400
    xs = [i*L_REP/n for i in range(n+1)]

    top = Canvas(Wp, Hp, sx=sx, ox=ox, oy=Hp*0.42, bg="#FFFFFF")
    top.panel("載重與支承", None)
    top.line((0, 0), (L_REP, 0), C["member"], 6.5, cap="butt")
    top.fixed_support((0, 0), 90); top.fixed_support((L_REP, 0), -90)
    top.udl((0, 0), (L_REP, 0), 0.9, n=13, label=None)
    top.text_px(top.X(L_REP*0.62), top.Y(0.9)-16, f"w = {W_REP:.0f} kN/m", 13.5, C["load"], weight="700")
    top.circle((M_REP, 0), 0.16, fill="#FFFFFF", stroke=C["accent"], w=3.2)
    top.text_px(top.X(M_REP), top.Y(0)+28, "c（內鉸）", 12.5, C["accent"], weight="700")
    top.dim((0, 0), (M_REP, 0), f"m = {M_REP:.0f} m", off=62, label_off=15)
    top.dim((M_REP, 0), (L_REP, 0), f"n = {N_REP:.0f} m", off=62, label_off=15)

    def strip(f, name, color, fill, unit, marks, zero_marks=()):
        vals = [f(x) for x in xs]
        vmax, vmin = max(max(vals), 0.0), min(min(vals), 0.0)
        rng = (vmax - vmin) or 1.0
        px_per = (Hp - 78 - 40)/rng
        cv = Canvas(Wp, Hp, sx=sx, ox=ox, oy=Hp - (78 + vmax*px_per), bg="#FFFFFF")
        cv.panel(name, None)
        k = px_per/sx
        pts = [(x, f(x)*k) for x in xs]
        cv.polygon([(0, 0)] + pts + [(L_REP, 0)], fill, color, 2.4)
        cv.line((0, 0), (L_REP, 0), C["muted"], 1.6)
        for x, txt, dxp, dyp in marks:
            cv.text_px(cv.X(x)+dxp, cv.Y(f(x)*k)+dyp, txt, 13, color,
                       "start" if dxp > 0 else "end", weight="700")
        for x, txt in zero_marks:
            cv.dot((x, 0), 5.4, fill="#FFFFFF", stroke=C["accent"], w=2.8)
            cv.text_px(cv.X(x), cv.Y(0)-24, txt, 12.5, C["accent"], weight="700")
        cv.text_px(Wp-24, 34, unit, 12, C["muted"], "end")
        return cv

    sfd = strip(V_rep, "剪力圖 SFD", C["sfd"], C["fill_s"], "kN",
                [(0.0, f"+{RA_REP:.2f}", 8, -14), (L_REP, f"−{RB_REP:.2f}", -8, 14)],
                [(X_V0, f"V = 0 於 x = {X_V0:.3f} m")])
    # BMD：繪於受拉側 ⇒ 正彎矩（下緣受拉）畫在下方
    bmd = strip(lambda x: -M_rep(x), "彎矩圖 BMD（繪於受拉側）", C["bmd"], C["fill_m"], "kN-m",
                [(0.0, f"M_a = {X_REP:.2f}", 8, -16),
                 (L_REP, f"M_b = {MB_REP:.2f}", -8, -16),
                 (X_V0, f"跨中最大 +{M_SPAN_MAX:.2f}", 0, 22)],
                [(M_REP, "內鉸 M = 0")])
    path = f"{OUT}/{TAG}-fig-3-vm.svg"
    compose([top, sfd, bmd], cols=1, path=path,
            title=f"代表案例 m / L = {BETA:.1f}（L = {L_REP:.0f} m、w = {W_REP:.0f} kN/m）",
            sub="所有座標由 §4.5、§4.6 的封閉解代入算出；改 BETA 重跑，三張圖一起變",
            note=f"驗算三處：內鉸 x = {M_REP:.0f} m 的彎矩必須為 0；剪力零點 x = {X_V0:.3f} m "
                 f"必須落在彎矩極值處；兩端彎矩必須都是負值（hogging）。")
    return path


FIGURES = [
    (fig1_beam,  "攔下「有鉸就是靜定」與內鉸位置畫錯"),
    (fig2_curve, "攔下「內鉸讓固端彎矩變小」這個錯誤結論（原 §5 的錯誤）"),
    (fig3_vm,    "攔下鉸點彎矩不為零、剪力零點與彎矩極值對不上、固端彎矩符號寫反"),
]

if __name__ == "__main__":
    _sanity()
    for fn, why in FIGURES:
        print(f"{fn():<52}  ← {why}")

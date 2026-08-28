#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SA-2016-3 虛功法選取靜定基本結構 — 解題圖解產生腳本

用法： python3 gen_SA-2016-3.py [輸出目錄]
"""
import sys, os, glob, math
_c = sorted(glob.glob(os.path.expanduser("~/.claude/skills/**/struct-diagram/scripts"), recursive=True))
sys.path.insert(0, _c[0] if _c else "/root/.claude/skills/synced/struct-diagram/scripts")
from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2016-3"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SA-2016-3.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §1 幾何與載重
L_AB, L_BC, L_CD = 10.0, 12.0, 20.0      # m
W_UDL = 2.0                              # kN/m（BC 上向下均佈）
# §5 由全剛架模型反推之 AB 傾角（圖上未標，本題解法不需要）
AB_DX, AB_DY = 5.0, 5.0*math.sqrt(3.0)   # A 相對 B 的水平／垂直距離；√(dx²+dy²)=10

# §1 題目給定之桿端彎矩（傾角變位法慣例：順時針作用於桿端為正）
M_AB, M_BC, M_CD, M_DC = -23.2, 5.63, -25.3, -17.0    # kN-m

# §4 Step 2：桿端彎矩 → 斷面內彎矩（左側受拉為正，軸線 C→D）
#            近端同號、遠端反號
M_TOP = M_CD          # = -25.3（C 端右側受拉）
M_BOT = -M_DC         # = +17.0（D 端左側受拉）
M_MID = (M_TOP + M_BOT)/2
Y_INFL = -M_TOP / ((M_BOT - M_TOP)/L_CD)              # 反曲點（自 C 起算）

# §4 Step 3：虛彎矩 m(y) = +y（柱頂向右單位力 ⇒ 左側受拉 ⇒ 正）
def m_virt(y):  return y
def M_real(y):  return M_TOP + (M_BOT - M_TOP)*y/L_CD

# §4 Step 4：圖形積分（Simpson，對二次式為精確）
DELTA_CX = L_CD/6*(M_TOP*m_virt(0) + 4*M_MID*m_virt(L_CD/2) + M_BOT*m_virt(L_CD))
THETA_C  = -(M_MID*L_CD)          # 順時針虛力矩 ⇒ 負值代表逆時針
AREA_NEG = sum((M_real(k*Y_INFL/2000)*m_virt(k*Y_INFL/2000)) for k in range(2000))*Y_INFL/2000
AREA_POS = DELTA_CX - AREA_NEG


def _sanity():
    assert abs(M_TOP + 25.3) < 1e-9 and abs(M_BOT - 17.0) < 1e-9
    assert abs(M_MID + 4.15) < 1e-9, M_MID
    assert abs(Y_INFL - 11.9622) < 1e-3, Y_INFL
    assert abs(DELTA_CX - 580.0) < 1e-6, DELTA_CX
    assert abs(THETA_C - 83.0) < 1e-6, THETA_C
    assert abs(math.hypot(AB_DX, AB_DY) - L_AB) < 1e-9


NODE = {"A": (-AB_DX, -AB_DY), "B": (0.0, 0.0), "C": (L_BC, 0.0), "D": (L_BC, -L_CD)}


def _frame(cv, col=C["member"], w=6.0, dash=None):
    for a, b in (("A", "B"), ("B", "C"), ("C", "D")):
        cv.line(NODE[a], NODE[b], col, w, dash=dash, cap="butt")


def _labels(cv, skip=()):
    for nm, (ax, ay) in (("A", (-22, 14)), ("B", (-14, -28)), ("C", (22, -14)), ("D", (24, 10))):
        if nm in skip:
            continue
        cv.dot(NODE[nm], 5.5)
        cv.text_px(cv.X(NODE[nm][0])+ax, cv.Y(NODE[nm][1])+ay, nm, 17, C["text"], weight="700")


# ══════════════════════════════════════════════════════════
def fig1_frame():
    """題目重繪：把「傾角沒給」這件事標明白"""
    W, H = 700, 640
    cv = Canvas(W, H, sx=17.5, ox=250, oy=430, bg="#FFFFFF")
    _frame(cv)
    cv.fixed_support(NODE["A"], 0)
    cv.fixed_support(NODE["D"], 0)
    cv.udl(NODE["B"], NODE["C"], 2.0, n=11, label=None)
    cv.text_px(cv.X(L_BC/2), cv.Y(2.0)-18, f"w = {W_UDL:.0f} kN/m", 15, C["load"], weight="700")
    cv.dim(NODE["A"], NODE["B"], "10 m", off=56, label_off=16)
    cv.dim(NODE["B"], NODE["C"], "12 m", off=-72, label_off=-16)
    cv.dim(NODE["C"], NODE["D"], "20 m", off=-64, label_off=-17)
    cv.text_px(cv.X(NODE["A"][0]), cv.Y(NODE["A"][1])+56,
               "AB 傾角原圖未標註", 12.5, C["muted"], weight="700")
    cv.text_px(cv.X(NODE["A"][0]), cv.Y(NODE["A"][1])+76,
               "本圖依 §5 反推之 60° 繪製，本題解法用不到", 12.5, C["muted"])
    _labels(cv)
    # 給定的桿端彎矩
    cv.rect_px(18, 88, 200, 168, "#F5F7FA", 12, C["border"], 1.3)
    cv.text_px(36, 112, "題目給定的桿端彎矩 (kN-m)", 13, C["text"], "start", weight="700")
    for i, (nm, v) in enumerate((("M_{AB}", M_AB), ("M_{BC}", M_BC),
                                 ("M_{CD}", M_CD), ("M_{DC}", M_DC))):
        used = nm in ("M_{CD}", "M_{DC}")
        cv.math_px(36, 140 + i*23, f"{nm} = {v}".replace("-", "\u2212"), 14.5,
                   C["accent"] if used else "#AAB2BD", "start", weight="700")
    cv.text_px(36, 238, "橘色兩項才會用到", 12.5, C["accent"], "start", weight="700")
    cv.text_px(W/2, 34, "題目重繪（向量版）", 17, C["text"], weight="700")
    cv.text_px(W/2, 58, "A、D 皆固接；BC 受 2 kN/m 向下均佈；EI 為常數", 13, C["muted"])
    cv.text_px(W/2, H-26, "題目給了四個桿端彎矩，卻沒給 AB 的傾角——這是「不要算全結構」的明示。",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


# ══════════════════════════════════════════════════════════
def fig2_primary():
    """虛力系統的基本結構選取：為什麼可以把 AB、BC 丟掉"""
    W, H = 620, 600
    def base():
        return Canvas(W, H, sx=15.0, ox=228, oy=400, bg="#FFFFFF")
    # ── 左：直接對原（靜不定）結構施加單位力 ──
    a = base(); _frame(a, C["member"], 5.4)
    a.fixed_support(NODE["A"], 0); a.fixed_support(NODE["D"], 0)
    a.arrow((L_BC-4.5, 0), (L_BC, 0), C["load"], 3.4, 12)
    a.math_px(a.X(L_BC-2.2), a.Y(0)-18, "1", 17, C["load"], weight="700")
    a.math_px(a.X(-AB_DX/2)-32, a.Y(-AB_DY/2), "m ≠ 0", 14.5, C["load"], "end", weight="700")
    a.math_px(a.X(L_BC/2), a.Y(0)+30, "m ≠ 0", 14.5, C["load"], weight="700")
    a.math_px(a.X(L_BC)+22, a.Y(-L_CD/2), "m ≠ 0", 14.5, C["load"], "start", weight="700")
    _labels(a)
    a.text_px(W/2, 34, "（不建議）直接拿原結構當虛力系統", 16, C["load"], weight="700")
    a.text_px(W/2, H-52, "三根桿都有虛彎矩，且虛系統本身也是二度靜不定", 13, C["muted"])
    a.text_px(W/2, H-30, "⇒ 必須先解一次靜不定才能求 m，計算量翻倍", 13, C["muted"])
    # ── 右：切斷 C 之靜定基本結構 ──
    b = base()
    b.line(NODE["A"], NODE["B"], C["ghost"], 5.0, dash="7 6", cap="butt")
    b.line(NODE["B"], NODE["C"], C["ghost"], 5.0, dash="7 6", cap="butt")
    b.line(NODE["C"], NODE["D"], C["member"], 5.4, cap="butt")
    b.fixed_support(NODE["A"], 0); b.fixed_support(NODE["D"], 0)
    b.arrow((L_BC-4.5, 0), (L_BC, 0), C["load"], 3.4, 12)
    b.math_px(b.X(L_BC-2.2), b.Y(0)-18, "1", 17, C["load"], weight="700")
    # 切斷記號
    b.line((L_BC-1.0, 2.2), (L_BC-1.0, -2.2), C["accent"], 2.4, dash="5 4")
    b.text_px(b.X(L_BC-1.0), b.Y(2.2)-16, "在 C 切開", 13, C["accent"], weight="700")
    b.math_px(b.X(-AB_DX/2)-32, b.Y(-AB_DY/2), "m = 0", 14.5, C["bmd"], "end", weight="700")
    b.math_px(b.X(L_BC/2)-20, b.Y(0)+30, "m = 0", 14.5, C["bmd"], weight="700")
    b.math_px(b.X(L_BC)+22, b.Y(-L_CD/2), "m = y", 15, C["deform"], "start", weight="700")
    _labels(b)
    b.text_px(W/2, 34, "（採用）改成「固定於 D 的懸臂柱」", 16, C["bmd"], weight="700")
    b.text_px(W/2, H-52, "左半段（A–B–C）無任何載重 ⇒ 虛彎矩恆為零", 13, C["muted"])
    b.text_px(W/2, H-30, "⇒ 只需 CD 一根桿的積分，AB 的幾何完全用不到", 13, C["muted"])
    path = f"{OUT}/{TAG}-fig-2-primary.svg"
    compose([a, b], cols=2, path=path,
            title="虛力系統的基本結構可以任選：只要滿足靜力平衡",
            sub="真實彎矩 M 由題目給定（已含所有靜不定效應）；虛彎矩 m 不必來自同一個結構",
            note="這是本題唯一的觀念：虛力系統與真實系統可以不同構。"
                 "誤以為兩者必須相同，就會掉進「先解全剛架」的陷阱。")
    return path


# ══════════════════════════════════════════════════════════
def fig3_integration():
    """M 圖 × m 圖 × 乘積面積：三聯圖"""
    W, H = 430, 620
    def col_panel(f, title, sub, color, fill, unit, marks, scale_ref):
        cv = Canvas(W, H, sx=18.0, ox=235, oy=510, bg="#FFFFFF")
        cv.line((0, 0), (0, -L_CD), C["ghost"], 5.0, cap="butt")
        k = 5.2 / scale_ref                     # 每 1 單位對應的模型長度
        n = 120
        pts = [(-f(i*L_CD/n)*k, -i*L_CD/n) for i in range(n+1)]   # 正值(左側受拉)畫在左邊
        cv.polygon([(0, 0)] + pts + [(0, -L_CD)], fill, color, 2.6)
        for y, txt, dxp, dyp in marks:
            cv.math_px(cv.X(-f(y)*k)+dxp, cv.Y(-y)+dyp, txt.replace("-", "−"),
                       13.5, color, "start" if dxp > 0 else "end", weight="700")
        cv.dot((0, 0), 5.5); cv.dot((0, -L_CD), 5.5)
        cv.text_px(cv.X(0)+16, cv.Y(0)-12, "C", 16, C["text"], weight="700")
        cv.text_px(cv.X(0)+16, cv.Y(-L_CD)+14, "D", 16, C["text"], weight="700")
        cv.text_px(W/2, 34, title, 15.5, C["text"], weight="700")
        cv.text_px(W/2, 56, sub, 12.5, C["muted"])
        cv.text_px(W/2, H-26, unit, 12.5, C["muted"])
        return cv

    p1 = col_panel(M_real, "真實彎矩 M(y)", "左側受拉為正", C["bmd"], C["fill_m"],
                   "單位 kN-m", [(0.0, f"{M_TOP}", 14, -14), (L_CD, f"+{M_BOT}", -14, 14),
                                 (L_CD/2, f"{M_MID}", 14, 0)], 25.3)
    p1.dot((0, -Y_INFL), 5.6, fill="#FFFFFF", stroke=C["accent"], w=2.9)
    p1.text_px(p1.X(0)+18, p1.Y(-Y_INFL), f"反曲點 y = {Y_INFL:.2f} m", 12.5, C["accent"], "start", weight="700")

    p2 = col_panel(m_virt, "虛彎矩 m(y) = +y", "柱頂向右單位力 ⇒ 左側受拉", C["deform"], C["fill_c"],
                   "單位 m（無因次力 × 長度）",
                   [(L_CD, "+20", -14, 14), (L_CD/2, "+10", -14, 0)], 25.3)

    def prod(y): return M_real(y)*m_virt(y)
    p3 = col_panel(prod, "乘積 M(y)·m(y)", f"淨面積 ∫ M·m dy = {DELTA_CX:.0f}", C["accent"],
                   "rgba(180,83,9,0.18)", "單位 kN-m²",
                   [(L_CD, f"+{prod(L_CD):.0f}", -14, 14)], 340.0)
    p3.text_px(p3.X(0)+40, p3.Y(-6.0), f"負區面積 {AREA_NEG:.0f}", 12.5, C["muted"], "start")
    p3.text_px(p3.X(0)-108, p3.Y(-17.6), f"正區面積 +{AREA_POS:.0f}", 12.5, C["accent"], "end", weight="700")

    path = f"{OUT}/{TAG}-fig-3-integration.svg"
    compose([p1, p2, p3], cols=3, path=path,
            title=f"CD 桿的圖形積分：C 點水平位移 = ∫ M·m/EI dy = {DELTA_CX:.0f}/EI（向右）",
            sub="兩端受拉側相反 ⇒ 柱為雙曲率；乘積曲線先負後正，淨面積才是答案",
            note="M 與 m 若同時翻號，乘積不變、答案照樣對；但只翻其中一個，答案就整個變號。"
                 "「往右推 ⇒ 左側受拉」是本題最容易寫反的一步。")
    return path


FIGURES = [
    (fig1_frame,      "攔下「四個桿端彎矩都要用」與支承型式誤讀"),
    (fig2_primary,    "攔下「虛力系統必須與原結構同靜不定度」的誤解"),
    (fig3_integration,"攔下受拉側畫反、漏掉反曲點、把乘積曲線當成單邊面積"),
]

if __name__ == "__main__":
    _sanity()
    for fn, why in FIGURES:
        print(f"{fn():<54}  ← {why}")

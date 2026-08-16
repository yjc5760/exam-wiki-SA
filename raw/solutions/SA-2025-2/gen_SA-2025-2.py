#!/usr/bin/env python3
"""
SA-2025-2 Gerber 梁影響線 — 解題圖解產生腳本

用法：
    python3 gen_SA-2025-2.py [輸出目錄]

⚠ 幾何來源：本檔一律以「考卷附圖 SA-2025-2-fig-1.png」量得的配置為準
   （A=0 固定端、B=4 內鉸、C=8 滾支承、D=12 內鉸、E=16 滾支承、F=6 斷面，4@4 m）。
   SA-2025-2.md §1 原文寫的 AB=2 / 五跨 18 m / F 為自由端與附圖不符，
   已於 .md 加註勘誤區塊；本腳本不採用該組數字。

三條鐵則的落實：
  1. 圖上每個縱距與每一條分段式都由下方 IL 函數算出，沒有一個數字是手打的
  2. 改 XA…XF 任何一個座標重跑，五條影響線與機構圖會一起變
  3. fig-4 的縱距用「幾何機構」獨立算一遍，與 fig-2 的平衡法結果互相 assert
"""
import sys, os
from fractions import Fraction as Fr

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_HERE, "figs", "_lib"), os.path.join(_HERE, "_lib")):
    if os.path.isdir(_p):
        sys.path.insert(0, _p)

from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2025-2"

# ══════════════════════════════════════════════════════════
# 幾何（由 SA-2025-2-fig-1.png 判讀：4@4 m，F 位於 C 左方 2 m）
# ══════════════════════════════════════════════════════════
XA, XB, XC, XD, XE = 0.0, 4.0, 8.0, 12.0, 16.0
XF = XC - 2.0                       # 附圖頂部的 2 m 尺寸線
SPAN = XE - XA
STA = [("A", XA), ("B", XB), ("F", XF), ("C", XC), ("D", XD), ("E", XE)]
LBL = {x: nm for nm, x in STA}

# 靜定度：R_A,H_A,M_A,R_C,R_E = 5 個未知；平衡 3 + 鉸條件 2 = 5
N_UNKNOWN, N_EQUIL, N_HINGE = 5, 3, 2
assert N_UNKNOWN - N_EQUIL - N_HINGE == 0


# ══════════════════════════════════════════════════════════
# 影響線（平衡法）：單位載重位於 x
#   鉸 D 右側自由體對 D 取矩 → R_E
#   鉸 B 右側自由體對 B 取矩 → R_C
#   全域 ΣFy、ΣM_A → R_A、M_A
#   A→F 左側自由體 → V_F（左上為正）
# ══════════════════════════════════════════════════════════
def RE(x):
    return max(x - XD, 0.0) / (XE - XD)


def RC(x):
    return (max(x - XB, 0.0) - (XE - XB) * RE(x)) / (XC - XB)


def RA(x):
    return 1.0 - RC(x) - RE(x)


def MA(x):
    return x - XC * RC(x) - XE * RE(x)


def VF(x, load_right_of_F=False):
    """V_F（左上為正）＝ A–F 左側自由體：R_A 減去落在 F 左方的載重。
    載重恰在 x = XF 時分兩支：load_right_of_F=False 取左極限、True 取右極限。"""
    load_left = (x < XF) if load_right_of_F else (x <= XF)
    return RA(x) - (1.0 if load_left else 0.0)


def VFL(x):
    return VF(x, False)


def VFR(x):
    return VF(x, True)


# 每條 IL 的直線段（折點只出現在支承、內鉸；V_F 另加剪力斷面 F）
IL = [
    ("R_{A}", RA,  [(XA, XB), (XB, XD), (XD, XE)], False, ()),
    ("R_{C}", RC,  [(XA, XB), (XB, XD), (XD, XE)], False, ()),
    ("R_{E}", RE,  [(XA, XD), (XD, XE)],           False, ()),
    ("M_{A}", MA,  [(XA, XB), (XB, XD), (XD, XE)], True,  ()),
]

# ── 交叉驗算：任意載重位置的整體平衡與兩個鉸條件 ────────────
for xt in (XB, XC, XD, XE, XF, 2.0, 10.0, 14.0):
    assert abs(RA(xt) + RC(xt) + RE(xt) - 1.0) < 1e-12, xt            # ΣFy
    assert abs(MA(xt) + XC * RC(xt) + XE * RE(xt) - xt) < 1e-12, xt   # ΣM_A
    assert abs((XC - XB) * RC(xt) + (XE - XB) * RE(xt)
               - max(xt - XB, 0.0)) < 1e-12, xt                       # 鉸 B 右側
    assert abs((XE - XD) * RE(xt) - max(xt - XD, 0.0)) < 1e-12, xt    # 鉸 D 右側
assert abs(VFR(XF) - VFL(XF) - 1.0) < 1e-12          # 單位載重跨過 F ⇒ 跳躍 = 1


# ══════════════════════════════════════════════════════════
# Müller–Breslau：純幾何機構（完全不用平衡方程）
#   剛體節段以鉸 B、D 轉折；支承處位移為零；被釋放處給單位位移／轉角
# ══════════════════════════════════════════════════════════
def _chain(vA, sAB, cC, cE):
    """A→B→D→E 的剛體鏈：給定 A 端位移與 A–B 段斜率，
    再由 C、E 的零位移條件解出後兩段斜率。"""
    vB = vA + sAB * (XB - XA)
    sBD = (cC - vB) / (XC - XB)              # 通過 C
    vD = vB + sBD * (XD - XB)
    sDE = (cE - vD) / (XE - XD)              # 通過 E
    vE = vD + sDE * (XE - XD)
    return [(XA, vA), (XB, vB), (XD, vD), (XE, vE)]


def mb_RA():
    """移除 A 的垂直約束；旋轉約束仍在 ⇒ A–B 段斜率 = 0"""
    return _chain(vA=1.0, sAB=0.0, cC=0.0, cE=0.0)


def mb_RC():
    """移除 C 的滾支承，C 升 1"""
    return _chain(vA=0.0, sAB=0.0, cC=1.0, cE=0.0)


def mb_RE():
    """移除 E 的滾支承，E 升 1"""
    return _chain(vA=0.0, sAB=0.0, cC=0.0, cE=1.0)


def mb_MA():
    """A 處插入鉸並施加單位相對轉角 ⇒ A–B 段斜率 = 1"""
    return _chain(vA=0.0, sAB=1.0, cC=0.0, cE=0.0)


def mb_VF():
    """F 處插入剪力釋放：兩側保持平行（斜率相同），相對橫向位移 = 1
       v(F−) = sL·(XF−XB)　v(F+) = sR·(XF−XC)　sL = sR
       ⇒ sL·[(XF−XC) − (XF−XB)] = 1 ⇒ sL·(XB−XC) = 1"""
    s = 1.0 / (XB - XC)
    left = [(XA, 0.0), (XB, 0.0), (XF, s * (XF - XB))]
    right = [(XF, s * (XF - XC)), (XD, s * (XD - XC)), (XE, 0.0)]
    return left, right


# ── 機構結果必須與平衡法逐點相符（這就是 fig-4 的價值）──────
for f, fn in ((mb_RA, RA), (mb_RC, RC), (mb_RE, RE), (mb_MA, MA)):
    for x, v in f():
        assert abs(v - fn(x)) < 1e-12, (f.__name__, x, v, fn(x))
_L, _R = mb_VF()
for x, v in _L:
    assert abs(v - VFL(x)) < 1e-12, ("VF-", x, v)
for x, v in _R:
    assert abs(v - VFR(x)) < 1e-12, ("VF+", x, v)


# ══════════════════════════════════════════════════════════
# 分段直線式（由縱距反算，非手打）
# ══════════════════════════════════════════════════════════
def _fr(v):
    return Fr(v).limit_denominator(10000)


def _fs(q):
    return str(q.numerator) if q.denominator == 1 else f"{q.numerator}/{q.denominator}"


def _tx(s):
    n, d = abs(s.numerator), s.denominator
    core = "x" if n == 1 else f"{n}x"
    return core if d == 1 else f"{core}/{d}"


def seg_expr(fn, x0, x1):
    """回傳該段的 v(x) 一次式字串"""
    v0, v1 = _fr(fn(x0 + 1e-9)), _fr(fn(x1 - 1e-9))
    v0, v1 = _fr(round(float(v0), 9)), _fr(round(float(v1), 9))
    s = (v1 - v0) / _fr(x1 - x0)
    a = v0 - s * _fr(x0)
    if s == 0:
        return _fs(a)
    t = _tx(s)
    if a == 0:
        return t if s > 0 else "-" + t
    if s > 0 and a > 0:
        return f"{_fs(a)} + {t}"
    if s > 0 and a < 0:
        return f"{t} - {_fs(-a)}"
    return f"{_fs(a)} - {t}"                       # s < 0


def seg_sub(fn, segs):
    return "　".join(f"{LBL[a]}–{LBL[b]}：v = {seg_expr(fn, a, b)}" for a, b in segs)


# ══════════════════════════════════════════════════════════
# 版面
# ══════════════════════════════════════════════════════════
W_IL, PH_IL = 980, 200
PADL, PADR = 96, 116
SX = (W_IL - PADL - PADR) / SPAN          # px / m
BASE = 116                                 # 基線距面板頂端（px）
PXU = 21.0                                 # px / 每 1 單位無因次縱距
PXU_M = 10.5                               # px / 每 1 m（M_A 專用尺度）
MW = 6.0


def fnum(v):
    return "0" if abs(v) < 1e-9 else f"{v:.10g}"


def guides(cv, PH, y0=68, y1=None):
    y1 = y1 if y1 is not None else PH - 26
    for nm, x in STA:
        px = cv.X(x)
        cv.parts.append(f'<line x1="{px:.2f}" y1="{y0}" x2="{px:.2f}" y2="{y1}" '
                        f'stroke="#DFE5EC" stroke-width="1" stroke-dasharray="3 4"/>')


def stations(cv, PH, color="#9AA4B2"):
    for nm, x in STA:
        cv.text_px(cv.X(x), PH - 14, nm, 11.5, color, weight="700")


def il_panel(name, sub, branches, pxu, unit):
    cv = Canvas(W_IL, PH_IL, sx=SX, ox=PADL, oy=PH_IL - BASE)
    cv.panel(name, sub)
    guides(cv, PH_IL)
    k = pxu / SX
    for br in branches:
        pts = [(x, v * k) for x, v in br]
        cv.polygon([(br[0][0], 0.0)] + pts + [(br[-1][0], 0.0)],
                   C["fill_m"], C["bmd"], 2.2)
    cv.line((XA, 0), (XE, 0), C["muted"], 1.6)
    for br in branches:
        for x, v in br:
            cv.dot((x, v * k), 3.8, fill=C["bmd"])
            if abs(v) < 1e-9:
                continue
            cv.math_px(cv.X(x), cv.Y(v * k) + (-13 if v > 0 else 15),
                       fnum(v), 13, C["bmd"], weight="700")
    cv.text_px(W_IL - 26, 86, unit, 12, C["muted"], "end")
    stations(cv, PH_IL)
    return cv


# ══════════════════════════════════════════════════════════
def fig1_beam():
    """題目重繪：把附圖的支承型式、內鉸位置、F 斷面位置一次釘死"""
    PH = 392
    cv = Canvas(W_IL, PH, sx=SX, ox=PADL, oy=PH - 196, bg="#FFFFFF")
    cv.line((XA, 0), (XE, 0), C["member"], 8.5, cap="butt")
    cv.fixed_support((XA, 0), ang=-90, size=26)
    cv.roller_support((XC, 0), size=17)
    cv.roller_support((XE, 0), size=17)
    for x in (XB, XD):
        cv.dot((x, 0), 7.6, fill="#FFFFFF", stroke=C["member"], w=3.0)
    px = cv.X(XF)
    cv.parts.append(f'<line x1="{px:.2f}" y1="{cv.Y(0)-22:.2f}" x2="{px:.2f}" '
                    f'y2="{cv.Y(0)+22:.2f}" stroke="{C["accent"]}" stroke-width="2.6" '
                    f'stroke-dasharray="5 4"/>')
    for nm, x in STA:
        cv.text((x, 0), nm, 18, C["accent"] if nm == "F" else C["text"],
                weight="700", dy=-50 if nm == "A" else -32)
    cv.text_px(cv.X(XB), cv.Y(0) + 30, "內鉸", 12, C["muted"])
    cv.text_px(cv.X(XD), cv.Y(0) + 30, "內鉸", 12, C["muted"])
    cv.text_px(cv.X(XF), cv.Y(0) + 46, "所求剪力斷面", 12, C["accent"], weight="700")

    xL = 10.0
    cv.arrow((xL, 0.95), (xL, 0.12), C["load"], 3.4, 12)
    cv.math_px(cv.X(xL) + 12, cv.Y(0.55), "P = 1", 16, C["load"], "start", weight="700")
    cv.dim((XA, 0), (xL, 0), "x", off=-78, label_off=-14)
    cv.dim((XF, 0), (XC, 0), "2 m", off=-120, label_off=-14)
    cv.dim((XA, 0), (XE, 0), "4 @ 4 m = 16 m", off=96, label_off=16)
    cv.text_px(W_IL / 2, PH - 52,
               f"未知反力 R_A、H_A、M_A、R_C、R_E 共 {N_UNKNOWN} 個；"
               f"平衡方程 {N_EQUIL} 式 ＋ 內鉸條件 {N_HINGE} 式 "
               f"⇒ 超靜定度 = {N_UNKNOWN - N_EQUIL - N_HINGE}（靜定）",
               13.5, C["muted"])
    cv.text_px(W_IL / 2, PH - 24,
               "F 是 B、C 之間的一個斷面（不是自由端），故 IL of V_F 在 F 處有單位跳躍",
               13.5, C["accent"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-1-beam.svg")


def beam_panel():
    cv = Canvas(W_IL, PH_IL, sx=SX, ox=PADL, oy=PH_IL - BASE)
    cv.panel("結構配置（以下各面板共用此橫向位置）",
             "A 固定端　B、D 內鉸　C、E 滾支承　F 為所求剪力斷面　"
             "單位載重 P = 1 沿梁移動，位置為 x")
    guides(cv, PH_IL)
    cv.line((XA, 0), (XE, 0), C["member"], MW, cap="butt")
    cv.fixed_support((XA, 0), ang=-90, size=20)
    cv.roller_support((XC, 0), size=14)
    cv.roller_support((XE, 0), size=14)
    for x in (XB, XD):
        cv.dot((x, 0), 6.2, fill="#FFFFFF", stroke=C["member"], w=2.6)
    px = cv.X(XF)
    cv.parts.append(f'<line x1="{px:.2f}" y1="{cv.Y(0)-18:.2f}" x2="{px:.2f}" '
                    f'y2="{cv.Y(0)+18:.2f}" stroke="{C["accent"]}" stroke-width="2.4" '
                    f'stroke-dasharray="4 3"/>')
    for nm, x in STA:
        cv.text((x, 0), nm, 15, C["accent"] if nm == "F" else C["text"],
                weight="700", dy=-42 if nm == "A" else -26)
    stations(cv, PH_IL, "#C3CAD5")
    return cv


def fig2_influence_lines():
    """五條影響線：縱距與分段式全部由 IL 函數算出"""
    panels = [beam_panel()]
    for name, fn, segs, is_m, _ in IL:
        pxu = PXU_M if is_m else PXU
        unit = "縱距單位：m" if is_m else "縱距無因次"
        br = [(segs[0][0], fn(segs[0][0]))] + [(b, fn(b)) for a, b in segs]
        panels.append(il_panel(f"IL of {name}", seg_sub(fn, segs), [br], pxu, unit))

    segsL = [(XA, XB), (XB, XF)]
    segsR = [(XF, XD), (XD, XE)]
    left = [(XA, VFL(XA)), (XB, VFL(XB)), (XF, VFL(XF))]
    right = [(XF, VFR(XF)), (XD, VFR(XD)), (XE, VFR(XE))]
    sub = (seg_sub(VFL, segsL) + "　│　"
           + "　".join(f"{LBL[a]}–{LBL[b]}：v = {seg_expr(VFR, a, b)}"
                       for a, b in [(XF, XC), (XC, XD), (XD, XE)][:1] + [(XF, XD), (XD, XE)][1:]))
    sub = seg_sub(VFL, segsL) + "　│　" + seg_sub(VFR, segsR)
    cv = il_panel("IL of V_{F}", sub, [left, right], PXU, "縱距無因次")
    k = PXU / SX
    v0, v1 = VFL(XF), VFR(XF)
    cv.line((XF, v0 * k), (XF, v1 * k), C["accent"], 2.4, dash="4 3")
    cv.text_px(cv.X(XF) + 12, (cv.Y(v0 * k) + cv.Y(v1 * k)) / 2,
               "跳躍 = 1", 12.5, C["accent"], "start", weight="700")
    panels.append(cv)

    compose(panels, cols=1,
            title="五條影響線（縱距＝單位載重位於 x 時該量的值）",
            sub="折點只出現在支承、內鉸與所求剪力斷面；各段皆為直線，故只需算折點縱距再連線",
            note="M_A 面板的縱距尺度與其餘四張不同（單位 m）。"
                 "IL of R_C 峰值 2 大於 1 是槓桿效應：D 為內鉸，DE 段對 C 形同懸臂。",
            path=f"{OUT}/{TAG}-fig-2-influence-lines.svg")
    return f"{OUT}/{TAG}-fig-2-influence-lines.svg"


# ══════════════════════════════════════════════════════════
def fbd_panel(xL, label):
    """鉸右側自由體（外層 B→E，內層 D→E）。自由體圖不畫支承，只畫反力。"""
    PH = 316
    cv = Canvas(W_IL, PH, sx=SX, ox=PADL, oy=PH - 166)
    rc, re_, ra, ma = RC(xL), RE(xL), RA(xL), MA(xL)
    cv.panel(label, f"代表位置 x = {fnum(xL)} m")

    y0 = cv.Y(0)
    x0p, x1p = cv.X(XB) - 18, cv.X(XE) + 34
    cv.rect_px(x0p, y0 - 78, x1p - x0p, 132, "rgba(29,78,216,0.05)", 12)
    cv.parts.append(f'<rect x="{x0p}" y="{y0-78}" width="{x1p-x0p}" height="132" '
                    f'rx="12" fill="none" stroke="{C["deform"]}" stroke-width="1.6" '
                    f'stroke-dasharray="7 5"/>')
    x2p = cv.X(XD) - 12
    cv.parts.append(f'<rect x="{x2p}" y="{y0-48}" width="{x1p-16-x2p}" height="86" '
                    f'rx="10" fill="none" stroke="{C["accent"]}" stroke-width="1.5" '
                    f'stroke-dasharray="5 4"/>')

    cv.line((XA, 0), (XB, 0), C["ghost"], 4.0, dash="7 5", cap="butt")
    cv.line((XB, 0), (XE, 0), C["member"], MW, cap="butt")
    cv.dot((XB, 0), 6.2, fill="#FFFFFF", stroke=C["member"], w=2.6)
    cv.dot((XD, 0), 6.2, fill="#FFFFFF", stroke=C["member"], w=2.6)
    for nm, x in STA:
        cv.text((x, 0), nm, 13, C["muted"], weight="700", dy=-20)

    # 切斷面 B：N、V、M 三者都要標（M = 0 才是鉸提供的條件）
    bx = cv.X(XB)
    cv.arrow((XB, -0.86), (XB, -0.10), C["deform"], 2.6, 9)
    cv.math_px(bx - 12, y0 + 30, "V_{B}", 13.5, C["deform"], "end", weight="700")
    cv.arrow((XB - 0.95, 0.0), (XB - 0.12, 0.0), C["deform"], 2.4, 9)
    cv.math_px(bx - 46, y0 - 15, "N_{B} = 0", 12.5, C["deform"], weight="700")
    cv.math_px(bx + 8, y0 - 60, "M_{B} = 0（鉸）", 13, C["accent"], "start", weight="700")

    # 反力（自由體圖不畫支承符號）
    for x, val, nm in ((XC, rc, "R_{C}"), (XE, re_, "R_{E}")):
        if val >= 0:
            cv.arrow((x, -0.86), (x, -0.10), C["load"], 3.0, 10)
        else:
            cv.arrow((x, -0.10), (x, -0.86), C["load"], 3.0, 10)
        cv.math_px(cv.X(x), y0 + 76, f"{nm} = {fnum(val)}", 13.5, C["load"], weight="700")

    inside = xL > XB
    col = C["load"] if inside else C["ghost"]
    cv.arrow((xL, 1.05), (xL, 0.12), col, 3.2, 11)
    cv.math_px(cv.X(xL), cv.Y(1.05) - 15, "P = 1", 14, col, weight="700")
    if not inside:
        cv.text_px(cv.X(xL), cv.Y(1.05) - 34, "（落在自由體之外）", 11.5, C["muted"])

    dD, dB = max(xL - XD, 0.0), max(xL - XB, 0.0)
    cv.text_px(PADL - 6, PH - 74,
               f"鉸 D 右側 ΣM_D = 0 ： {fnum(XE - XD)}·R_E − 1·({fnum(dD)}) = 0"
               f"　⇒　R_E = {fnum(re_)}", 13.5, C["accent"], "start", weight="700")
    cv.text_px(PADL - 6, PH - 48,
               f"鉸 B 右側 ΣM_B = 0 ： {fnum(XC - XB)}·R_C + {fnum(XE - XB)}·R_E "
               f"− 1·({fnum(dB)}) = 0　⇒　R_C = {fnum(rc)}",
               13.5, C["deform"], "start", weight="700")
    cv.text_px(PADL - 6, PH - 20,
               f"回代全域 ΣFy、ΣM_A ： R_A = {fnum(ra)}　M_A = {fnum(ma)} m",
               13.5, C["muted"], "start", weight="700")
    return cv


def fig3_hinge_fbd():
    """三段載重位置的鉸右側自由體：載重在鉸左側時它不進右側自由體"""
    panels = [
        fbd_panel(2.0,  "① 載重在 A–B 段（x ＜ 4）：兩個自由體都不含載重"),
        fbd_panel(10.0, "② 載重在 B–D 段（4 ≦ x ≦ 12）：只有 B 右側自由體含載重"),
        fbd_panel(14.0, "③ 載重在 D–E 段（x ＞ 12）：兩個自由體都含載重"),
    ]
    compose(panels, cols=1,
            title="內鉸條件的用法：取「鉸右側」自由體對鉸取矩，把固定端的三個未知力全部排除在外",
            sub="藍框＝鉸 B 右側自由體　橙框＝鉸 D 右側自由體　"
                "切斷面同時標出 N、V、M（M = 0 才是鉸提供的那一條方程）",
            note="三段的差別只在「載重有沒有落進該自由體」。這正是影響線必須分段的原因，"
                 "也是最容易錯的一步：載重在鉸左側時，右側自由體的載重項為 0。",
            path=f"{OUT}/{TAG}-fig-3-hinge-fbd.svg")
    return f"{OUT}/{TAG}-fig-3-hinge-fbd.svg"


# ══════════════════════════════════════════════════════════
def _interp(branches, x):
    """在機構折線上內插（釋放點不一定是折點，例如 C）"""
    for br in branches:
        for (a, va), (b, vb) in zip(br, br[1:]):
            if a - 1e-9 <= x <= b + 1e-9:
                return va + (vb - va) * (x - a) / (b - a)
    return 0.0


def mb_panel(title, branches, pxu, released, unit):
    kinks = "　→　".join(f"{LBL[x]} {fnum(v)}" for br in branches for x, v in br)
    cv = Canvas(W_IL, PH_IL, sx=SX, ox=PADL, oy=PH_IL - BASE)
    cv.panel(title, "折點縱距：" + kinks)
    guides(cv, PH_IL)
    k = pxu / SX
    cv.line((XA, 0), (XE, 0), C["ghost"], 3.4, dash="7 5", cap="butt")
    for x in (XC, XE):
        if x not in released:
            cv.roller_support((x, 0), size=12, color="#D4DAE3")
    for br in branches:
        cv.poly([(x, v * k) for x, v in br], C["deform"], 4.4)
    for br in branches:
        for x, v in br:
            cv.dot((x, v * k), 5.0, fill="#FFFFFF", stroke=C["deform"], w=2.4)
            cv.math_px(cv.X(x), cv.Y(v * k) + (-14 if v >= 0 else 16),
                       fnum(v), 13, C["deform"], weight="700")
    for x in released:
        v = _interp(branches, x)
        cv.parts.append(f'<circle cx="{cv.X(x):.2f}" cy="{cv.Y(0):.2f}" r="11" '
                        f'fill="none" stroke="{C["load"]}" stroke-width="2.4" '
                        f'stroke-dasharray="4 3"/>')
        if abs(v) > 1e-9:
            cv.arrow((x, 0.0), (x, v * k), C["load"], 2.4, 9)
    cv.text_px(W_IL - 26, 86, unit, 12, C["muted"], "end")
    stations(cv, PH_IL)
    return cv


def fig4_muller_breslau():
    """Müller–Breslau：用幾何機構把 fig-2 的縱距獨立算一遍"""
    panels = []
    for title, f, pxu, rel, unit in (
        ("釋放 R_A：移除 A 的垂直約束並令 A 升 1（旋轉約束仍在 ⇒ A–B 段保持水平）",
         mb_RA, PXU, (XA,), "縱距無因次"),
        ("釋放 R_C：移除 C 的滾支承並令 C 升 1", mb_RC, PXU, (XC,), "縱距無因次"),
        ("釋放 R_E：移除 E 的滾支承並令 E 升 1", mb_RE, PXU, (XE,), "縱距無因次"),
        ("釋放 M_A：A 處插入鉸並施加單位相對轉角", mb_MA, PXU_M, (XA,), "縱距單位：m"),
    ):
        panels.append(mb_panel(title, [f()], pxu, rel, unit))

    left, right = mb_VF()
    cv = mb_panel("釋放 V_F：F 處插入剪力釋放，兩側保持平行、相對橫向位移 = 1",
                  [left, right], PXU, (), "縱距無因次")
    k = PXU / SX
    cv.line((XF, left[-1][1] * k), (XF, right[0][1] * k), C["load"], 2.6, dash="4 3")
    cv.text_px(cv.X(XF) + 12, (cv.Y(left[-1][1] * k) + cv.Y(right[0][1] * k)) / 2,
               "相對位移 = 1", 12.5, C["load"], "start", weight="700")
    panels.append(cv)

    compose(panels, cols=1,
            title="Müller–Breslau 獨立檢核：移除該量對應的約束，令它產生單位位移，變形形狀即為影響線",
            sub="全程只用幾何（剛體節段以內鉸轉折、支承處位移為零），一條平衡方程都沒用到",
            note="本圖每個縱距都在腳本裡與 fig-2 的平衡法結果逐點 assert 過；"
                 "兩條互相獨立的路徑得到同一組數字，才算真的算對。",
            path=f"{OUT}/{TAG}-fig-4-muller-breslau.svg")
    return f"{OUT}/{TAG}-fig-4-muller-breslau.svg"


# ══════════════════════════════════════════════════════════
FIGURES = [
    (fig1_beam,             "§1",   "把 F 誤讀成自由端、或跨距記成 AB=2 → 整組縱距全錯"),
    (fig2_influence_lines,  "§4",   "影響線當彎矩圖畫；折點不在支承／鉸；漏掉 R_C 峰值 2"),
    (fig3_hinge_fbd,        "§4.1", "載重在鉸左側時仍把它算進右側自由體"),
    (fig4_muller_breslau,   "§5.1", "影響線形狀畫錯（與 fig-2 互為獨立檢核）"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, section, catches in FIGURES:
        print(f"{os.path.basename(fn()):<46} {section:<6} 攔：{catches}")
    print("\n縱距表（單位載重位於 x）")
    xs = (XA, XB, XF, XC, XD, XE)
    print("  x(m)  " + "".join(f"{x:>9.0f}" for x in xs))
    for nm, fn in (("R_A", RA), ("R_C", RC), ("R_E", RE), ("M_A", MA)):
        print(f"  {nm:<6}" + "".join(f"{fn(x):>9.3g}" for x in xs))
    print("  V_F   " + f"{VFL(XA):>9.3g}{VFL(XB):>9.3g}"
          f"{VFL(XF):>6.3g}/{VFR(XF):<3.3g}"
          f"{VFR(XC):>8.3g}{VFR(XD):>9.3g}{VFR(XE):>9.3g}")
    print("\n分段式")
    for nm, fn, segs, _, _u in IL:
        print(f"  IL {nm:<7}" + seg_sub(fn, segs))

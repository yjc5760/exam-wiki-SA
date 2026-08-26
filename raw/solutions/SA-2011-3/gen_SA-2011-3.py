#!/usr/bin/env python3
"""
SA-2011-3 兩跨連續梁影響線（穆勒法 ＋ 面積積分）— 解題圖解產生腳本

用法：
    python3 gen_SA-2011-3.py [輸出目錄]

三條鐵則的落實：
  1. 五條影響線的每一個縱距都由下方閉合式算出；面積由同一組函數數值積分，
     不是把「84.375」抄進圖裡
  2. 改 L（跨距）或 XC（C 的位置）重跑，五條曲線、面積與 M_max 會一起變
  3. 閉合式另與「梁有限元（含贅力 M_B 的一致解）」在 241 個載重位置對照過
"""
import sys, os
from fractions import Fraction as Fr

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_HERE, "figs", "_lib"), os.path.join(_HERE, "_lib")):
    if os.path.isdir(_p):
        sys.path.insert(0, _p)

from structdraw import Canvas, C, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2011-3"

# ══════════════════════════════════════════════════════════
# 幾何與載重
# ══════════════════════════════════════════════════════════
L = 30.0                                  # 單跨跨距
XA, XB, XD = 0.0, L, 2 * L
XC = XB + L / 2                           # C 為 BD 跨中點
SPAN = XD - XA
W_UDL = 2.0                               # kN/m
STA = [("A", XA), ("B", XB), ("C", XC), ("D", XD)]
SUPPORTS = {XA: "roller", XB: "roller", XD: "pin"}

# 靜不定度：反力 4（A、B 各 1，D 為 2）− 平衡 3 = 1 度
N_R, N_EQ = 4, 3
assert N_R - N_EQ == 1


# ══════════════════════════════════════════════════════════
# 影響線（力法：贅力取 B 點彎矩 M_B）
#   單跨簡支梁 + 端彎矩的疊加；u = 載重距「所在跨外側支承」的距離
# ══════════════════════════════════════════════════════════
def MB(x):
    """B 點彎矩影響線（下凹為正 ⇒ 全線為負）。
    由諧合條件 2 M_B L/(3EI) = 載重端轉角 得
        M_B = − u(L² − u²) / (4L²)"""
    u = x if x <= XB else (XD - x)
    return -u * (L ** 2 - u ** 2) / (4 * L ** 2)


def RA(x):
    """A 點反力。載重在 AB 跨時 = 簡支值 + M_B/L；在 BD 跨時只剩 M_B/L（為負）。"""
    simp = (XB - x) / L if x <= XB else 0.0
    return simp + MB(x) / L


def RD(x):
    return RA(XD - x)                     # 對稱結構


def RB(x):
    return 1.0 - RA(x) - RD(x)


def MC(x):
    """C 點彎矩 = 簡支梁 M_C + 端彎矩線性內插值 M_B/2。"""
    simp = 0.0
    if x >= XB:
        s = x - XB
        simp = s / 2 if s <= L / 2 else (XD - x) / 2
    return simp + MB(x) / 2


def VC(x, right=False):
    """C 點剪力（斷面左側向上為正）＝ R_A + R_B − 落在 C 左方的載重。"""
    left = (x < XC) if right else (x <= XC)
    return RA(x) + RB(x) - (1.0 if left else 0.0)


# ── 靜力／幾何自我檢核 ─────────────────────────────────
def _selftest():
    for k in range(241):
        x = k * 0.25
        assert abs(RA(x) + RB(x) + RD(x) - 1.0) < 1e-12, x                    # ΣFy
        assert abs(RB(x) * XB + RD(x) * XD - x) < 1e-9, x                     # ΣM_A
        # M_B 也可由左側自由體算：M_B = R_A·L − (載重在 AB 時的力矩)
        chk = RA(x) * L - (max(XB - x, 0.0) if x <= XB else 0.0)
        assert abs(chk - MB(x)) < 1e-9, (x, chk, MB(x))
        # M_C 亦可由左側自由體算
        chk2 = RA(x) * XC + RB(x) * (XC - XB) - (max(XC - x, 0.0) if x <= XC else 0.0)
        assert abs(chk2 - MC(x)) < 1e-9, (x, chk2, MC(x))
    assert abs(VC(XC, True) - VC(XC, False) - 1.0) < 1e-12                    # 單位跳躍
    for xq in (XA, XB, XD):                                                   # 支承處 M_B = 0
        assert abs(MB(xq)) < 1e-12


_selftest()


def _area(f, a, b, n=200000, clip=None):
    h = (b - a) / n
    s = 0.0
    for i in range(n):
        v = f(a + (i + 0.5) * h)
        if clip == "+": v = max(v, 0.0)
        if clip == "-": v = min(v, 0.0)
        s += v * h
    return s


AREA_POS = _area(MC, XB, XD)              # BD 跨（全為正）
AREA_NEG = _area(MC, XA, XB)              # AB 跨（全為負）
M_MAX = W_UDL * AREA_POS
M_MIN = W_UDL * AREA_NEG
assert abs(AREA_POS - 3 * L ** 2 / 32) < 1e-4, AREA_POS       # = 3L²/32
assert abs(AREA_NEG + L ** 2 / 32) < 1e-4, AREA_NEG           # = −L²/32
assert abs(M_MAX - 168.75) < 1e-3 and abs(M_MIN + 56.25) < 1e-3

# 各條 IL 的極值（數值搜尋，非目測）
_G = [XA + SPAN * i / 24000 for i in range(24001)]
X_MB = min(_G, key=MB)                    # ≈ L/√3 = 17.32
PEAK = {
    "MB":  (X_MB, MB(X_MB)),
    "MCn": (min(_G, key=MC), MC(min(_G, key=MC))),
    "RAn": (min(_G, key=RA), RA(min(_G, key=RA))),
    "VCp": (max([g for g in _G if g < XB], key=lambda t: VC(t)),
            max(VC(g) for g in _G if g < XB)),
}


def _fs(v, nd=4):
    q = Fr(v).limit_denominator(64)
    if abs(float(q) - v) < 1e-9:
        return "0" if q == 0 else (f"{q.numerator:+d}" if q.denominator == 1
                                   else f"{q.numerator:+d}/{q.denominator}")
    return f"{v:+.{nd}g}"


# ══════════════════════════════════════════════════════════
# 版面
# ══════════════════════════════════════════════════════════
W = 1040
PADL, PADR = 72, 72
SX = (W - PADL - PADR) / SPAN
Y_BEAM = 148


def guides(cv, H, y0=72):
    for nm, x in STA:
        p = cv.X(x)
        cv.parts.append(f'<line x1="{p:.2f}" y1="{y0}" x2="{p:.2f}" y2="{H - 30}" '
                        f'stroke="#E6EAF0" stroke-width="1" stroke-dasharray="3 4"/>')


def stations(cv, H):
    for nm, x in STA:
        cv.text_px(cv.X(x), H - 14, nm, 12.5, "#9AA4B2", weight="700")


# ══════════════════════════════════════════════════════════
def fig1_beam():
    """題目重繪。攔：把 C 當支承（它只是 BD 跨的中點斷面）、
    以及把結構當成兩根獨立簡支梁（梁在 B 上方是連續的，不是鉸）。"""
    H = 376
    cv = Canvas(W, H, sx=SX, ox=PADL, oy=H - 206, bg="#FFFFFF")
    cv.panel("題目重繪（兩跨對稱連續梁）",
             "A、B 滾支承　D 鉸支承　梁在 B 上方連續（不是鉸）　"
             "C 為 BD 跨中點的斷面（不是支承）　EI 為定值")
    cv.udl((XB, 0.4), (XD, 0.4), 1.7, n=11, color=C["load"], w=1.8)
    cv.text_px(cv.X((XB + XD) / 2), cv.Y(3.0),
               "w = 2 kN/m（可只佈置在部分跨長）", 13.5, C["load"], weight="700")
    cv.line((XA, 0), (XD, 0), C["member"], 7.5, cap="butt")
    for x, k in SUPPORTS.items():
        cv.support((x, 0), k, size=17)
    px = cv.X(XC)
    cv.parts.append(f'<line x1="{px:.2f}" y1="{cv.Y(0) - 26:.2f}" x2="{px:.2f}" '
                    f'y2="{cv.Y(0) + 26:.2f}" stroke="{C["accent"]}" stroke-width="2.6" '
                    f'stroke-dasharray="5 4"/>')
    for nm, x in STA:
        cv.text_px(cv.X(x), cv.Y(0) + 56, nm, 17,
                   C["accent"] if nm == "C" else C["text"], weight="700")
    cv.text_px(cv.X(XC), cv.Y(0) + 82, "所求 M_{C}、V_{C} 的斷面", 12.5,
               C["accent"], weight="700")
    for a, b, lab in ((XA, XB, "30 m"), (XB, XC, "15 m"), (XC, XD, "15 m")):
        cv.dim((a, 0), (b, 0), lab, off=112, label_off=15)
    cv.text_px(W / 2, H - 22,
               f"反力 {N_R} 個（D 為 2）− 平衡 {N_EQ} 式 ⇒ {N_R - N_EQ} 度靜不定"
               "　⇒　影響線是曲線，不是折線",
               13.5, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-beam.svg")


PH, BASE = 272, 162


def il_panel(name, release, fn, keys, pxu, unit, fn_right=None, jump_at=None):
    cv = Canvas(W, PH, sx=SX, ox=PADL, oy=PH - BASE)
    cv.panel(f"IL of {name}", f"穆勒法：{release}　│　{unit}")
    guides(cv, PH)
    k = pxu / SX
    if jump_at is None:
        xs = [XA + SPAN * i / 800 for i in range(801)]
        cv.polygon([(XA, 0.0)] + [(x, fn(x) * k) for x in xs] + [(XD, 0.0)],
                   C["fill_m"], C["bmd"], 2.4)
    else:
        for a, b, g in ((XA, jump_at, fn), (jump_at, XD, fn_right)):
            xs = [a + (b - a) * i / 500 for i in range(501)]
            cv.polygon([(a, 0.0)] + [(x, g(x) * k) for x in xs] + [(b, 0.0)],
                       C["fill_s"], C["sfd"], 2.4)
        cv.line((jump_at, fn(jump_at) * k), (jump_at, fn_right(jump_at) * k),
                C["accent"], 2.4, dash="4 3")
    cv.line((XA, 0), (XD, 0), C["muted"], 1.6)
    col = C["sfd"] if jump_at is not None else C["bmd"]
    for lab, x, v, dx in keys:
        cv.dot((x, v * k), 4.0, fill=col)
        if abs(v) > 1e-9:
            cv.text_px(cv.X(x) + dx, cv.Y(v * k) + (-14 if v > 0 else 17),
                       lab, 13, col, weight="700")
    stations(cv, PH)
    return cv


def fig2_influence_lines():
    """五條影響線。攔：把靜不定結構的影響線畫成直線折線、
    以及漏掉 V_C 在 AB 跨的正值（蹺蹺板效應）。"""
    panels = []

    panels.append(il_panel(
        "R_{A}", "移除 A 的垂直束制，A 點抬升單位位移", RA,
        [(_fs(RA(XA)), XA, RA(XA), 8),
         (f"{PEAK['RAn'][1]:+.4f} @ x≈{PEAK['RAn'][0]:.1f}", PEAK['RAn'][0], PEAK['RAn'][1], 0)],
        66.0, "AB 跨為正、BD 跨為負；縱距無因次"))

    panels.append(il_panel(
        "R_{B}", "移除 B 的垂直束制，B 點抬升單位位移", RB,
        [(_fs(RB(XB)), XB, RB(XB), 0)],
        66.0, "全線為正（整條梁像拱起的弓）；縱距無因次"))

    panels.append(il_panel(
        "M_{B}", "B 處插入鉸並施加單位相對轉角", MB,
        [(f"{PEAK['MB'][1]:+.4f} @ x≈{PEAK['MB'][0]:.2f}", PEAK['MB'][0], PEAK['MB'][1], 0),
         (f"{MB(XD - PEAK['MB'][0]):+.4f}", XD - PEAK['MB'][0], MB(XD - PEAK['MB'][0]), 0)],
        22.0, "全線為負（任何位置的向下載重都在 B 產生負彎矩）；縱距單位 m"))

    panels.append(il_panel(
        "M_{C}", "C 處插入鉸並施加單位相對轉角", MC,
        [(f"{_fs(MC(XC))} = {MC(XC):+.5g} m", XC, MC(XC), 0),
         (f"{PEAK['MCn'][1]:+.4f} @ x≈{PEAK['MCn'][0]:.2f}", PEAK['MCn'][0], PEAK['MCn'][1], 0)],
        11.0, "AB 跨為負、BD 跨為正；縱距單位 m"))

    panels.append(il_panel(
        "V_{C}", "C 處插入剪力釋放，兩側保持平行並錯動單位位移",
        lambda t: VC(t, False),
        [(_fs(VC(XC, False)), XC, VC(XC, False), -22),
         (_fs(VC(XC, True)), XC, VC(XC, True), 22),
         (f"{PEAK['VCp'][1]:+.4f} @ x≈{PEAK['VCp'][0]:.2f}",
          PEAK['VCp'][0], PEAK['VCp'][1], 0)],
        66.0, "AB 跨為正（蹺蹺板效應）、BC 為負、CD 為正；縱距無因次",
        fn_right=lambda t: VC(t, True), jump_at=XC))

    return compose(panels, cols=1,
                   note="五條都是曲線 —— 靜不定結構的影響線沒有直線段。"
                        "V_{C} 在 AB 跨為正是本題最容易畫錯的地方：BC 段被壓下去，"
                        "會把 B 左側的 AB 跨像蹺蹺板一樣翹起來",
                   path=f"{OUT}/{TAG}-fig-2-influence-lines.svg")


def fig3_mc_loading():
    """M_C 影響線的載重佈置與面積。攔：把 2 kN/m 佈滿全長 60 m —— 那會把 AB 跨的
    負面積一併計入，算出來的不是「最大」彎矩。"""
    H1, H2 = 348, 268
    cv1 = Canvas(W, H1, sx=SX, ox=PADL, oy=H1 - 196)
    cv1.panel("最大正彎矩的載重佈置：只佈在 IL 為正的區間",
              "M_{C} 影響線在 BD 跨全為正、AB 跨全為負　⇒　w 只放 BD 跨（30 m）")
    guides(cv1, H1)
    k = 11.0 / SX
    xs = [XA + SPAN * i / 800 for i in range(801)]
    cv1.polygon([(XA, 0.0)] + [(x, MC(x) * k) for x in xs] + [(XD, 0.0)],
                "rgba(148,163,184,0.16)", C["muted"], 1.8)
    xs2 = [XB + L * i / 400 for i in range(401)]
    cv1.polygon([(XB, 0.0)] + [(x, MC(x) * k) for x in xs2] + [(XD, 0.0)],
                C["fill_m"], C["bmd"], 2.6)
    cv1.line((XA, 0), (XD, 0), C["muted"], 1.6)
    hu = MC(XC) * k + 1.0
    cv1.udl((XB, hu), (XD, hu), 1.0, n=11, color=C["load"], w=1.8)
    cv1.text_px(cv1.X(XC), cv1.Y(hu + 2.0), "w = 2 kN/m（只佈 BD 跨）", 13.5,
                C["load"], weight="700")
    cv1.text_px(cv1.X(L / 2), cv1.Y(MC(L / 2) * k) + 22,
                "此段不佈載重（IL 為負）", 12.5, C["muted"])
    cv1.dot((XC, MC(XC) * k), 4.2, fill=C["bmd"])
    cv1.text_px(cv1.X(XC) - 58, cv1.Y(MC(XC) * k) - 4, f"{MC(XC):+.5g} m", 13,
                C["bmd"], weight="700")
    cv1.text_px(W / 2, H1 - 52,
                f"正面積 = 3L²/32 = {AREA_POS:.5g} m²　⇒　"
                f"M_{{max,C}} = w × 面積 = {W_UDL:g} × {AREA_POS:.5g} = {M_MAX:.5g} kN·m",
                14.5, C["bmd"], weight="700")
    for nm, x in STA:
        cv1.text_px(cv1.X(x), H1 - 18, nm, 12.5, "#9AA4B2", weight="700")

    cv2 = Canvas(W, H2, sx=SX, ox=PADL, oy=H2 - 96)
    cv2.panel("面積的來源：靜定部分 ＋ 贅力部分",
              "M_{C} = M_{C}(簡支) + M_{B}/2　⇒　BD 跨的面積 = A_{1} + A_{2}/2")
    yb = 90
    cv2.text_px(W / 2, yb,
                f"A_{{1}}（簡支三角形，高 L/4 = {L / 4:g} m）"
                f"= ½·L·L/4 = L²/8 = {L ** 2 / 8:.5g} m²", 14.5, C["text"])
    cv2.text_px(W / 2, yb + 34,
                f"A_{{2}}（M_{{B}} 影響線在單跨內的面積）"
                f"= ∫_{{0}}^{{L}} −u(L²−u²)/(4L²) du = −L²/16 = {-L ** 2 / 16:.5g} m²",
                14.5, C["text"])
    cv2.text_px(W / 2, yb + 72,
                f"面積 = A_{{1}} + ½A_{{2}} = L²/8 − L²/32 = 3L²/32 = {AREA_POS:.5g} m²",
                15, C["bmd"], weight="700")
    cv2.text_px(W / 2, yb + 118,
                f"（順帶：AB 跨負面積 = ½·(−L²/16) = {AREA_NEG:.5g} m²　⇒　"
                f"M_{{min,C}} = {M_MIN:.5g} kN·m；量體小於正值，故最大彎矩為 "
                f"{M_MAX:.5g} kN·m）", 13, C["muted"])
    return compose([cv1, cv2], cols=1, path=f"{OUT}/{TAG}-fig-3-mc-loading.svg")


if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for f in (fig1_beam, fig2_influence_lines, fig3_mc_loading):
        f(); print("寫出", f.__name__)
    print(f"\n正面積 = {AREA_POS:.6f}   負面積 = {AREA_NEG:.6f}")
    print(f"M_max,C = {M_MAX:.6f} kN·m    M_min,C = {M_MIN:.6f} kN·m")
    print("\n關鍵縱距")
    print("  x      R_A       R_B       R_D       M_B       M_C       V_C")
    for x in (0, 15, 17.3205, 30, 37.5, 45, 52.5, 60):
        print(f"{x:7.2f} " + "  ".join(f"{v:+8.4f}" for v in
              (RA(x), RB(x), RD(x), MB(x), MC(x), VC(x, True))))
    print("\n極值")
    for k2, (xx, vv) in PEAK.items():
        print(f"  {k2:4s}  x = {xx:7.3f}   v = {vv:+.6f}")

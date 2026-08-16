#!/usr/bin/env python3
"""
SA-2025-3 非均勻斷面桿件的傾角變位公式 — 解題圖解產生腳本

用法：
    python3 gen_SA-2025-3.py [輸出目錄]

斷面分布取自考卷附圖 SA-2025-3-fig-1.png：AB 分三段各 L/3，
剛度依序為 EI、2EI、EI（對稱），P 作用於跨中 x = L/2。
SA-2025-3.md §4.6 只寫到通式；本腳本把該通式套進這個 EI(x) 分布，
用 4 點 Gauss–Legendre 分段精確積分算出所有係數的實際值。

⚠ 兩處與 .md 原文不一致，已於 .md 加註勘誤區塊，本腳本採用修正後版本：
   (1) 符號約定：桿端彎矩、桿端轉角、弦轉角一律「順時針為正」
       （與附圖兩個彎矩箭頭方向、以及 §4.6／§5.1 的公式相容）。
       .md §1 文字寫「θ 逆時針為正」，與其自身公式牴觸。
   (2) §4.5 的 Δ_B^(P) 應與 Δ_A^(P) 反號：m̄_A = +(1−x/L)、m̄_B = −(x/L)。
       .md 兩者同號，代回均勻梁會得到 M_F = 3PL/8 而非 PL/8。

三條鐵則的落實：
  1. 圖上每個係數都由下方積分算出，沒有一個是手打的
  2. 改 EI_PROFILE 重跑，四張圖的數值、變形曲線、反曲點位置會一起變
  3. 每張圖都在腳本裡對「均勻梁退化值」或「邊界條件」做 assert
"""
import sys, os

_HERE = os.path.dirname(os.path.abspath(__file__))
for _p in (os.path.join(_HERE, "figs", "_lib"), os.path.join(_HERE, "_lib")):
    if os.path.isdir(_p):
        sys.path.insert(0, _p)

from structdraw import Canvas, C, compose, beam_shape
from recipes import bar_compare

OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(_HERE, "figs")
TAG = "SA-2025-3"

# ══════════════════════════════════════════════════════════
# 輸入（無因次化：L = 1、EI 基準 = 1、P = 1）
#   結果的物理單位：f ~ L/EI　k ~ EI/L　θ ~ PL²/EI　M_F ~ PL
# ══════════════════════════════════════════════════════════
EI_PROFILE = [(0.0, 1 / 3, 1.0), (1 / 3, 2 / 3, 2.0), (2 / 3, 1.0, 1.0)]   # 附圖
BREAKS = sorted({0.0, 1 / 3, 0.5, 2 / 3, 1.0})     # EI 折點 ∪ 載重位置


def EI(u):
    for a, b, v in EI_PROFILE:
        if a - 1e-12 <= u <= b + 1e-12:
            return v
    raise ValueError(u)


# ── 4 點 Gauss–Legendre（對 ≤7 次多項式精確；分段避開 EI 與 M0 的折點）──
_GX = (-0.8611363115940526, -0.3399810435848563,
       0.3399810435848563, 0.8611363115940526)
_GW = (0.3478548451374538, 0.6521451548625461,
       0.6521451548625461, 0.3478548451374538)


def integ(f, breaks=None):
    tot = 0.0
    bs = breaks or BREAKS
    for a, b in zip(bs, bs[1:]):
        h, m = (b - a) / 2, (a + b) / 2
        tot += h * sum(w * f(m + h * x) for x, w in zip(_GX, _GW))
    return tot


# ── 單位「順時針」桿端彎矩造成的彎矩圖（sagging 為正）──────────
def mA(u):
    return 1.0 - u          # A 端單位順時針彎矩


def mB(u):
    return -u               # B 端單位順時針彎矩


def M0(u):
    """簡支主結構在跨中 P 之彎矩圖（P = 1、L = 1）"""
    return 0.5 * min(u, 1.0 - u)


# ── 柔度係數 f = ∫ m_i m_j / EI ────────────────────────────
f_AA = integ(lambda u: mA(u) ** 2 / EI(u))
f_BB = integ(lambda u: mB(u) ** 2 / EI(u))
f_AB = integ(lambda u: mA(u) * mB(u) / EI(u))
DET = f_AA * f_BB - f_AB ** 2

# ── 勁度係數 k = F⁻¹ ──────────────────────────────────────
k_AA = f_BB / DET
k_BB = f_AA / DET
k_AB = -f_AB / DET
k_BA = k_AB
C_AB = -f_AB / f_BB                    # A→B 傳遞係數
C_BA = -f_AB / f_AA
k_psiA = -(k_AA + k_AB)                # 弦轉角項
k_psiB = -(k_BA + k_BB)

# ── 固端彎矩（相容條件 θ_total = 0）──────────────────────────
th_A_P = integ(lambda u: M0(u) * mA(u) / EI(u))     # 簡支主結構端點轉角（順時針正）
th_B_P = integ(lambda u: M0(u) * mB(u) / EI(u))
M_FAB = -(k_AA * th_A_P + k_AB * th_B_P)
M_FBA = -(k_BA * th_A_P + k_BB * th_B_P)

# ── 均勻梁退化（把 EI(u) 換成常數 1 重算一遍，非手打）────────
_save = EI_PROFILE[:]
EI_PROFILE[:] = [(0.0, 1.0, 1.0)]
u_fAA = integ(lambda u: mA(u) ** 2 / EI(u))
u_fBB = integ(lambda u: mB(u) ** 2 / EI(u))
u_fAB = integ(lambda u: mA(u) * mB(u) / EI(u))
u_DET = u_fAA * u_fBB - u_fAB ** 2
u_kAA, u_kAB = u_fBB / u_DET, -u_fAB / u_DET
u_kpsi = -(u_kAA + u_kAB)
u_C = -u_fAB / u_fBB
u_thA = integ(lambda u: M0(u) * mA(u) / EI(u))
u_thB = integ(lambda u: M0(u) * mB(u) / EI(u))
u_MFAB = -(u_kAA * u_thA + u_kAB * u_thB)
EI_PROFILE[:] = _save

# 均勻梁必須退化為課本值，否則整套推導就是錯的
assert abs(u_fAA - 1 / 3) < 1e-12 and abs(u_fAB + 1 / 6) < 1e-12
assert abs(u_kAA - 4.0) < 1e-10 and abs(u_kAB - 2.0) < 1e-10
assert abs(u_kpsi + 6.0) < 1e-10 and abs(u_C - 0.5) < 1e-12
assert abs(u_thA - 1 / 16) < 1e-12 and abs(u_thB + 1 / 16) < 1e-12
assert abs(u_MFAB + 0.125) < 1e-10          # M_F,AB = −PL/8
# 本題為對稱斷面 ⇒ f_AA = f_BB、C_AB = C_BA、M_FAB = −M_FBA
assert abs(f_AA - f_BB) < 1e-12 and abs(M_FAB + M_FBA) < 1e-12


# ══════════════════════════════════════════════════════════
# 實際變形曲線：EI·v'' = M(u)（sagging 正、y 向上、順時針轉角 ⇒ dv/dx = −θ）
# ══════════════════════════════════════════════════════════
def deflection(Mfun, theta_A_cw=0.0, per=400):
    """在每個 EI／載重分段內 κ = M/EI 恰為一次式，故下列遞推是「精確」的：
         s(b) = s(a) + h(κa + κb)/2
         v(b) = v(a) + h·s(a) + h²(2κa + κb)/6
    邊界：v(0) = 0、dv/dx(0) = −θ_A（順時針轉角為正）。"""
    us, v, sl = [0.0], [0.0], [-theta_A_cw]
    for a, b in zip(BREAKS, BREAKS[1:]):
        ei = EI(0.5 * (a + b))
        h = (b - a) / per
        for i in range(per):
            u0 = a + i * h
            k0, k1 = Mfun(u0) / ei, Mfun(u0 + h) / ei
            v.append(v[-1] + h * sl[-1] + h * h * (2 * k0 + k1) / 6)
            sl.append(sl[-1] + 0.5 * h * (k0 + k1))
            us.append(u0 + h)
    return us, v, sl


STATES = {}   # name -> (M(u), θ_A(cw), 期望 v(1), 期望 θ_B(cw))
STATES["a"] = (lambda u: k_AA * mA(u) + k_BA * mB(u),  1.0, 0.0, 0.0)
STATES["b"] = (lambda u: k_AB * mA(u) + k_BB * mB(u),  0.0, 0.0, 1.0)
STATES["c"] = (lambda u: k_psiA * mA(u) + k_psiB * mB(u), 0.0, -1.0, 0.0)  # ψ = 1 cw
STATES["d"] = (lambda u: M0(u) + M_FAB * mA(u) + M_FBA * mB(u), 0.0, 0.0, 0.0)

SHAPES = {}
for nm, (Mf, thA, v_end, thB_end) in STATES.items():
    us, v, sl = deflection(Mf, thA)
    assert abs(v[-1] - v_end) < 1e-10, (nm, v[-1], v_end)          # 端點位移
    assert abs(-sl[-1] - thB_end) < 1e-10, (nm, -sl[-1], thB_end)  # 端點轉角
    SHAPES[nm] = (us[::8], v[::8])                              # 繪圖用抽稀

# 狀態 (d) 的反曲點（M = 0）——不是目測，是解出來的
Md = STATES["d"][0]
INFL = []
_n = 4000
for i in range(_n):
    a, b = i / _n, (i + 1) / _n
    if Md(a) * Md(b) < 0:
        lo, hi = a, b
        for _ in range(60):
            mid = 0.5 * (lo + hi)
            if Md(lo) * Md(mid) <= 0:
                hi = mid
            else:
                lo = mid
        INFL.append(0.5 * (lo + hi))
assert len(INFL) == 2 and abs(INFL[0] + INFL[1] - 1.0) < 1e-6      # 對稱


# ══════════════════════════════════════════════════════════
# 版面小工具
# ══════════════════════════════════════════════════════════
def n3(v, d=4):
    return f"{v:.{d}g}"


SEGD = {1.0: 0.030, 2.0: 0.052}          # 繪圖用斷面半高（僅示意剛度大小）


def draw_member(cv, y=0.0, color=C["member"], label=True):
    for a, b, ei in EI_PROFILE:
        d = SEGD.get(ei, 0.04)
        cv.polygon([(a, y - d), (b, y - d), (b, y + d), (a, y + d)], color)
        if label:
            cv.math_px(cv.X((a + b) / 2), cv.Y(y) + 40,
                       ("EI" if ei == 1 else f"{ei:g}EI"), 16, C["muted"], weight="700")


# ══════════════════════════════════════════════════════════
def fig1_member_sign():
    """題目重繪 ＋ 符號約定：本題最大的失分點是轉角正負搞錯"""
    PW, PH = 660, 400

    a = Canvas(PW, PH, sx=430, ox=112, oy=190)
    a.panel("① 桿件 AB 與斷面分布（取自考卷附圖）", "三段各 L/3，剛度 EI ─ 2EI ─ EI（對稱）")
    draw_member(a)
    a.arrow((0.5, 0.20), (0.5, 0.06), C["load"], 3.4, 12)
    a.math_px(a.X(0.5) + 14, a.Y(0.14), "P", 19, C["load"], "start", weight="700")
    a.moment_arrow((0.0, 0.0), r=34, ccw=False, color=C["bmd"], w=3.0, span=230, start=160)
    a.math_px(a.X(0.0) - 46, a.Y(0.0) - 34, "M_{AB}", 16, C["bmd"], "end", weight="700")
    a.moment_arrow((1.0, 0.0), r=34, ccw=False, color=C["bmd"], w=3.0, span=230, start=110)
    a.math_px(a.X(1.0) + 46, a.Y(0.0) - 34, "M_{BA}", 16, C["bmd"], "start", weight="700")
    a.dot((0, 0), 5.0); a.dot((1, 0), 5.0)
    a.math((0, 0), "A", 17, C["text"], "end", dx=-16, dy=-16)
    a.math((1, 0), "B", 17, C["text"], "start", dx=16, dy=-16)
    for i, (s, e, _) in enumerate(EI_PROFILE):
        a.dim((s, 0), (e, 0), "L/3", off=72, label_off=15)
    a.text_px(PW / 2, PH - 26, "兩個桿端彎矩箭頭都是順時針 → 這就是本題採用的正向",
              13, C["bmd"], weight="700")

    b = Canvas(PW, PH, sx=430, ox=112, oy=190)
    b.panel("② 符號約定：一律順時針為正", "θ_A、θ_B、ψ = Δ/L、M_AB、M_BA 五者同一個正向")
    D = 0.155                       # 繪圖用側移量
    thA, thB = 0.34, -0.06          # 順時針為正的端點轉角（僅示意大小）
    b.line((0, 0), (1, 0), C["ghost"], 3.0, dash="7 5", cap="butt")
    b.line((0, 0), (1, -D), C["accent"], 2.2, dash="6 4")            # 弦線
    b.poly(beam_shape((0, 0), 1.0, -thA, -thB, 0.0, -D), C["deform"], 5.0)
    b.dot((0, 0), 5.4, fill=C["deform"]); b.dot((1, -D), 5.4, fill=C["deform"])
    b.arrow((1, 0), (1, -D), C["load"], 2.6, 10)
    b.math_px(b.X(1) + 16, b.Y(-D / 2), "Δ", 17, C["load"], "start", weight="700")
    b.moment_arrow((0, 0), r=30, ccw=False, color=C["deform"], w=2.6, span=150, start=170)
    b.math_px(b.X(0) - 6, b.Y(0) - 46, "θ_{A}", 16, C["deform"], "middle", weight="700")
    b.moment_arrow((1, -D), r=30, ccw=False, color=C["deform"], w=2.6, span=150, start=170)
    b.math_px(b.X(1) - 34, b.Y(-D) - 44, "θ_{B}", 16, C["deform"], "middle", weight="700")
    b.math_px(b.X(0.5), b.Y(-D * 0.5) + 26, "ψ = Δ/L", 16, C["accent"], weight="700")
    b.text_px(b.X(0.5), b.Y(-D * 0.5) + 48, "弦線相對原位置的順時針轉角",
              12.5, C["accent"])
    b.math((0, 0), "A", 15, C["text"], "end", dx=-14, dy=6)
    b.math((1, -D), "B'", 15, C["text"], "start", dx=16, dy=6)
    b.rect_px(58, PH - 96, PW - 116, 62, "#FFF6F1", 10, "#F0C9B8", 1.3)
    b.text_px(PW / 2, PH - 74, "⚠ .md §1 文字寫「θ 逆時針為正」，與附圖箭頭及 §4.6 公式牴觸",
              12.5, "#9A3412", weight="700")
    b.text_px(PW / 2, PH - 52, "若照字面採逆時針正，θ 項須整組改號；作答時務必先寫清楚自己的約定",
              12.5, "#9A3412")

    compose([a, b],
            title="桿端彎矩、桿端轉角、弦轉角的正向必須先釘死，公式才有意義",
            sub="灰虛線＝原位置　橙虛線＝變形後的弦線　藍實線＝變形後的桿件",
            note="本圖是全題唯一的符號權威。正向一改，"
                 "「近端勁度項 ＋ 遠端勁度項 − 側移項 ＋ 固端彎矩項」裡每一項的正負都要跟著改。",
            path=f"{OUT}/{TAG}-fig-1-member-sign.svg")
    return f"{OUT}/{TAG}-fig-1-member-sign.svg"


# ══════════════════════════════════════════════════════════
def _state_panel(key, title, sub, mAB, mBA, notes, scale):
    PW, PH = 500, 396
    cv = Canvas(PW, PH, sx=320, ox=90, oy=196)
    cv.panel(title, sub)
    draw_member(cv, color=C["ghost"], label=False)
    cv.line((0, 0), (1, 0), C["ghost"], 1.6, dash="6 5", cap="butt")
    us, v = SHAPES[key]
    cv.poly([(u, vv * scale) for u, vv in zip(us, v)], C["deform"], 5.0)
    cv.dot((0, v[0] * scale), 5.0, fill=C["deform"])
    cv.dot((1, v[-1] * scale), 5.0, fill=C["deform"])
    cv.math((0, v[0] * scale), "A", 15, C["text"], "end", dx=-38, dy=4)
    cv.math((1, v[-1] * scale), "B", 15, C["text"], "start", dx=38, dy=4)

    for x, m in ((0.0, mAB), (1.0, mBA)):
        yv = (v[0] if x == 0 else v[-1]) * scale
        cv.moment_arrow((x, yv), r=22, ccw=(m < 0),
                        color=C["bmd"], w=2.6, span=200, start=170)
    cv.math_px(PW / 2, PH - 78, f"M_{{AB}} = {n3(mAB)}", 15, C["bmd"], weight="700")
    cv.math_px(PW / 2, PH - 54, f"M_{{BA}} = {n3(mBA)}", 15, C["bmd"], weight="700")
    cv.text_px(PW / 2, PH - 26, notes, 12.5, C["muted"])
    return cv


def fig2_superposition():
    """四個子問題的疊加：漏掉任何一項，傾角變位公式就少一段"""
    s1 = 0.20 / max(abs(min(SHAPES["a"][1])), abs(max(SHAPES["a"][1])))
    s3 = 0.20
    s4 = 0.22 / max(abs(v) for v in SHAPES["d"][1])
    panels = [
        _state_panel("a", "(a) θ_A = 1，其餘鎖住", "→ 勁度矩陣第 1 行",
                     k_AA, k_BA, f"k_{{AA}} = {n3(k_AA)} EI/L　k_{{BA}} = {n3(k_BA)} EI/L", s1),
        _state_panel("b", "(b) θ_B = 1，其餘鎖住", "→ 勁度矩陣第 2 行",
                     k_AB, k_BB, f"k_{{AB}} = {n3(k_AB)} EI/L　k_{{BB}} = {n3(k_BB)} EI/L", s1),
        _state_panel("c", "(c) ψ = Δ/L = 1，兩端不轉動", "→ 側移項",
                     k_psiA, k_psiB,
                     f"k_{{Aψ}} = −(k_{{AA}} + k_{{AB}}) = {n3(k_psiA)} EI/L", s3),
        _state_panel("d", "(d) 兩端固定、P 於跨中", "→ 固端彎矩",
                     M_FAB, M_FBA,
                     f"M_{{F,AB}} = {n3(M_FAB)} PL　M_{{F,BA}} = {n3(M_FBA)} PL", s4),
    ]
    # 狀態 (d) 標出反曲點（由 M(u)=0 解出）
    d = panels[3]
    us, v = SHAPES["d"]
    for xi in INFL:
        vv = v[min(range(len(us)), key=lambda i: abs(us[i] - xi))] * s4
        d.dot((xi, vv), 5.2, fill="#FFFFFF", stroke=C["accent"], w=2.8)
        d.math_px(d.X(xi), d.Y(vv) - 16, f"{xi:.3f}L", 12.5, C["accent"], weight="700")
    d.text_px(250, 236, "○ ＝ 反曲點（M = 0）", 12, C["accent"], weight="700")

    compose([panels[0], panels[1], panels[2], panels[3]], cols=2,
            title="廣義傾角變位公式 ＝ 四個子問題的疊加（各係數已套入本題的 EI ─ 2EI ─ EI 分布）",
            sub="A 端彎矩 ＝ 近端勁度×θA ＋ 遠端勁度×θB − (近端＋遠端)×ψ ＋ 固端彎矩　（全部順時針為正）",
            note="藍線為實際變形曲線，由 EI·v″ = M(u) 逐點積分而得（不是示意），"
                 "故中央 2EI 段的曲率明顯較兩端平緩。",
            path=f"{OUT}/{TAG}-fig-2-superposition.svg")
    return f"{OUT}/{TAG}-fig-2-superposition.svg"


# ══════════════════════════════════════════════════════════
def _curve_panel(title, sub, curves, ylab, note=None, PW=600, PH=340):
    ys = [y for _, ys_, _, _ in curves for y in ys_]
    lo, hi = min(min(ys), 0.0), max(max(ys), 0.0)
    rng = (hi - lo) or 1.0
    top, bot = 86, 60
    ppu = (PH - top - bot) / rng
    sx = (PW - 150) / 1.0
    cv = Canvas(PW, PH, sx=sx, ox=90, oy=bot - lo * ppu)
    cv.panel(title, sub)
    k = ppu / sx
    for j, (lab, ys_, col, fill) in enumerate(curves):
        xs = [i / (len(ys_) - 1) for i in range(len(ys_))]
        if fill:
            cv.polygon([(0, 0)] + [(x, y * k) for x, y in zip(xs, ys_)] + [(1, 0)],
                       fill, col, 2.2)
        else:
            cv.poly([(x, y * k) for x, y in zip(xs, ys_)], col, 2.6)
    cv.line((0, 0), (1, 0), C["muted"], 1.4)
    cv.legend(PW - 190, top + 6, [(c, l) for l, _y, c, _f in curves])
    for a, b, ei in EI_PROFILE:
        if a > 0:
            cv.parts.append(f'<line x1="{cv.X(a):.2f}" y1="{top-14}" x2="{cv.X(a):.2f}" '
                            f'y2="{PH-bot+18}" stroke="#DFE5EC" stroke-width="1" '
                            f'stroke-dasharray="3 4"/>')
    cv.math((0, 0), "A", 13, C["muted"], dy=20)
    cv.math((1, 0), "B", 13, C["muted"], dy=20)
    cv.text_px(PW - 22, top - 6, ylab, 11.5, C["muted"], "end")
    if note:
        cv.text_px(PW / 2, PH - 22, note, 12.5, C["muted"])
    return cv


def fig3_flexibility():
    """柔度係數怎麼來的：f_AB 為負是幾何必然，不是抄錯號"""
    n = 240
    us = [i / n for i in range(n + 1)]

    p1 = _curve_panel(
        "① 單位順時針桿端彎矩造成的彎矩圖", "m_A = 1 − u（A 端）　m_B = −u（B 端）",
        [("m_A", [mA(u) for u in us], C["bmd"], C["fill_m"]),
         ("m_B", [mB(u) for u in us], C["load"], C["fill_t"])],
        "無因次",
        "兩者一正一負：A 端順時針彎矩在 A 附近造成正彎矩，B 端順時針彎矩造成負彎矩")

    p2 = _curve_panel(
        "② 權重 1/EI(u)", "中央 L/3 為 2EI ⇒ 該段對積分的貢獻只剩一半",
        [("1/EI", [1.0 / EI(min(max(u, 1e-9), 1 - 1e-9)) for u in us],
          C["deform"], C["fill_c"])],
        "1/EI",
        "柔度是「以 1/EI 為權重」的加權積分，斷面愈大權重愈小")

    p3 = _curve_panel(
        "③ 被積函數 m_i·m_j / EI", "曲線下的面積即為柔度係數",
        [("m_A²/EI", [mA(u) ** 2 / EI(min(max(u, 1e-9), 1 - 1e-9)) for u in us],
          C["bmd"], C["fill_m"]),
         ("m_A·m_B/EI", [mA(u) * mB(u) / EI(min(max(u, 1e-9), 1 - 1e-9)) for u in us],
          C["load"], C["fill_t"])],
        "L/EI",
        f"f_{{AA}} = f_{{BB}} = {n3(f_AA)} L/EI　　f_{{AB}} = {n3(f_AB)} L/EI（乘積全段 ≤ 0 ⇒ 必為負）")

    compose([p1, p2, p3], cols=3,
            title="柔度係數 ＝ ∫ (兩個單位彎矩圖的乘積) / EI(u) du：看完就知道 f(AB) 為什麼必定是負的",
            sub=f"均勻梁退化：f(AA) = {n3(u_fAA)} = 1/3、f(AB) = {n3(u_fAB)} = −1/6 "
                f"⇒ k(AA) = {n3(u_kAA)} EI/L、k(AB) = {n3(u_kAB)} EI/L、C = {n3(u_C)}（腳本已 assert）",
            note=f"本題 C(AB) = C(BA) = −f(AB)/f(AA) = {n3(C_AB)}，小於均勻梁的 0.5——"
                 f"中央 2EI 段愈剛，兩端愈「各自為政」，傳遞過去的比例愈低。",
            path=f"{OUT}/{TAG}-fig-3-flexibility.svg")
    return f"{OUT}/{TAG}-fig-3-flexibility.svg"


# ══════════════════════════════════════════════════════════
def fig4_prismatic_check():
    """把通式代回均勻梁：對不上就是前面某個積分或某個號寫錯了"""
    bar_compare(
        [(f"|k_{{Aψ}}|　本題（EI–2EI–EI）", "= k_{AA} + k_{AB}（側移項）", abs(k_psiA),
          f"{n3(abs(k_psiA))} EI/L", C["accent"]),
         ("|k_{Aψ}|　均勻梁", "課本值 6EI/L", abs(u_kpsi), f"{n3(abs(u_kpsi))} EI/L", "#94A3B8"),
         ("k_{AA}　本題", "近端勁度", k_AA, f"{n3(k_AA)} EI/L", C["accent"]),
         ("k_{AA}　均勻梁", "課本值 4EI/L", u_kAA, f"{n3(u_kAA)} EI/L", "#94A3B8"),
         ("k_{AB}　本題", "遠端（傳遞）勁度", k_AB, f"{n3(k_AB)} EI/L", C["accent"]),
         ("k_{AB}　均勻梁", "課本值 2EI/L", u_kAB, f"{n3(u_kAB)} EI/L", "#94A3B8")],
        title="通式退化檢核：令 EI(u) ≡ 常數，四個係數必須回到課本的 4／2／6／½",
        sub="橙＝本題（中央 L/3 為 2EI）　灰＝均勻梁。三組數字都滿足 |側移項| ＝ 近端勁度 ＋ 遠端勁度",
        note=f"本題傳遞係數 C = {n3(C_AB)}（均勻梁 {n3(u_C)}）；"
             f"固端彎矩 = {n3(M_FAB)} PL（均勻梁 {n3(u_MFAB)} PL = −PL/8）。"
             f"若通式代回均勻梁得到 −3PL/8，就是主結構 B 端轉角的號寫反了。",
        path=f"{OUT}/{TAG}-fig-4-prismatic-check.svg")
    return f"{OUT}/{TAG}-fig-4-prismatic-check.svg"


# ══════════════════════════════════════════════════════════
FIGURES = [
    (fig1_member_sign,      "§1",   "轉角／弦轉角正負慣例搞錯 → 整組公式符號全錯"),
    (fig2_superposition,    "§4.1", "漏掉側移項或固端彎矩項，公式只寫出一半"),
    (fig3_flexibility,      "§4.2", "f_AB 的負號寫成正號 → 傳遞係數算成負值"),
    (fig4_prismatic_check,  "§5.1", "通式代回均勻梁對不上 4／2／6／½ 與 −PL/8"),
]

if __name__ == "__main__":
    os.makedirs(OUT, exist_ok=True)
    for fn, section, catches in FIGURES:
        print(f"{os.path.basename(fn()):<48} {section:<6} 攔：{catches}")
    print(f"""
本題（L/3 三段 EI–2EI–EI）與均勻梁對照
                      本題        均勻梁
  f_AA = f_BB   {f_AA:>10.6f}  {u_fAA:>10.6f}   × L/EI
  f_AB          {f_AB:>10.6f}  {u_fAB:>10.6f}   × L/EI
  k_AA = k_BB   {k_AA:>10.6f}  {u_kAA:>10.6f}   × EI/L
  k_AB = k_BA   {k_AB:>10.6f}  {u_kAB:>10.6f}   × EI/L
  k_Aψ          {k_psiA:>10.6f}  {u_kpsi:>10.6f}   × EI/L
  C_AB = C_BA   {C_AB:>10.6f}  {u_C:>10.6f}
  θ_A^(P)       {th_A_P:>10.6f}  {u_thA:>10.6f}   × PL²/EI
  M_F,AB        {M_FAB:>10.6f}  {u_MFAB:>10.6f}   × PL
  反曲點        {INFL[0]:.4f}L 與 {INFL[1]:.4f}L""")

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SA-2006-1 樑＋桁架混合結構的最小功法 — 解題圖解產生腳本

用法： python3 gen_SA-2006-1.py [輸出目錄]

桁架虛內力 u0 不是抄來的：腳本自己以節點法解一次靜定基本結構（純 Python 高斯消去），
再與 §4 Step 4 的清單比對，對不上就 assert 失敗。
"""
import sys, os, glob, math
_c = sorted(glob.glob(os.path.expanduser("~/.claude/skills/**/struct-diagram/scripts"), recursive=True))
sys.path.insert(0, _c[0] if _c else "/root/.claude/skills/synced/struct-diagram/scripts")
from structdraw import Canvas, C, FONT, compose

OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2006-1"
R2 = math.sqrt(2.0)

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SA-2006-1.md，勿手動改動）
# ══════════════════════════════════════════════════════════
BAY, HGT = 10.0, 10.0            # §1 桁架單格寬、桁架高 (m)
SPAN     = 4*BAY                 # 樑與桁架總跨 40 m
P        = 10.0                  # §1 樑上集中載重 (kN)
XP1, XP2 = 15.0, 25.0            # §1 載重位置
XA, XB, XD = 0.0, 10.0, 30.0     # §4 Step 1 樑之三個垂直支承

# §4 Step 2：桁架水平贅力
def H_of(RD):  return RD - 20.0
# §4 Step 1 / Step 3：兩段應變能偏微分
def beam_term(RD):   return 4000.0*RD - 32500.0                                  # × 1/EI
def truss_term(RD):  return (160.0 + 120.0*R2)*RD - (2000.0 + 1600.0*R2)         # × 1/EA
# §4 Step 3：贅力參數解（α = EI/EA）
def RD_of(a):  return (812.5 + a*(50.0 + 40.0*R2)) / (100.0 + a*(4.0 + 3.0*R2))
# §4 Step 4：J 點垂直變位（× 1/EA）
def dJ_of(a):  return 20.0*(1.0 + R2)*(20.0 - RD_of(a))
DJ_SOFT = 20.0*(1.0+R2)*(20.0 - 812.5/100.0)                                     # α → 0
DJ_STIFF = 20.0*(1.0+R2)*(20.0 - (50.0+40.0*R2)/(4.0+3.0*R2))                    # α → ∞

# ── 桁架幾何（節點座標；樑另外畫在上方）──────────────────
TN = {"F": (0.0, 0.0), "B'": (BAY, 0.0), "C'": (2*BAY, 0.0), "D'": (3*BAY, 0.0),
      "G": (4*BAY, 0.0), "H": (BAY, -HGT), "J": (2*BAY, -HGT), "K": (3*BAY, -HGT)}
TM = [("F", "B'"), ("B'", "C'"), ("C'", "D'"), ("D'", "G"),
      ("H", "J"), ("J", "K"),
      ("B'", "H"), ("C'", "J"), ("D'", "K"),
      ("F", "H"), ("H", "C'"), ("C'", "K"), ("K", "G")]


def _solve(loads, roller_at_G=True):
    """節點法解靜定桁架（F 鉸、G 滾支承）。純 Python 高斯消去，不依賴 numpy。
    loads: {節點: (Fx, Fy)}。回傳 {桿: 軸力}（拉為正）。"""
    unk = [("m", m) for m in TM] + [("r", "Fx"), ("r", "Fy"), ("r", "Gy")]
    if not roller_at_G:
        unk.append(("r", "Gx"))
    idx = {u: i for i, u in enumerate(unk)}
    rows, rhs = [], []
    for nd in TN:
        for comp in (0, 1):
            row = [0.0]*len(unk)
            for m in TM:
                if nd in m:
                    o = m[1] if m[0] == nd else m[0]
                    dx = TN[o][0]-TN[nd][0]; dy = TN[o][1]-TN[nd][1]
                    L = math.hypot(dx, dy)
                    row[idx[("m", m)]] = (dx if comp == 0 else dy)/L
            for rn, nn, cc in (("Fx", "F", 0), ("Fy", "F", 1), ("Gy", "G", 1), ("Gx", "G", 0)):
                if ("r", rn) in idx and nd == nn and comp == cc:
                    row[idx[("r", rn)]] = 1.0
            rows.append(row)
            rhs.append(-loads.get(nd, (0.0, 0.0))[comp])
    n = len(unk)
    A = [rows[i][:] + [rhs[i]] for i in range(len(rows))]
    # 高斯消去（方程式數 = 未知數數）
    assert len(A) == n, (len(A), n)
    for c in range(n):
        piv = max(range(c, n), key=lambda r: abs(A[r][c]))
        assert abs(A[piv][c]) > 1e-9, f"奇異矩陣 @ {c}"
        A[c], A[piv] = A[piv], A[c]
        for r in range(n):
            if r != c and abs(A[r][c]) > 1e-14:
                f = A[r][c]/A[c][c]
                for k in range(c, n+1):
                    A[r][k] -= f*A[c][k]
    sol = {unk[i]: A[i][n]/A[i][i] for i in range(n)}
    return {m: sol[("m", m)] for m in TM}


# §4 Step 4：於 J 點施加向下單位虛力，基本結構為「G 改滾支承（H = 0）」
U0 = _solve({"J": (0.0, -1.0)})

# §4 Step 4 所列之虛內力（用來核對腳本解出來的 U0）
U0_DOC = {("F", "B'"): -0.5, ("B'", "C'"): -0.5, ("C'", "D'"): -0.5, ("D'", "G"): -0.5,
          ("H", "J"): 1.0, ("J", "K"): 1.0,
          ("B'", "H"): 0.0, ("C'", "J"): 1.0, ("D'", "K"): 0.0,
          ("F", "H"): 0.5*R2, ("H", "C'"): -0.5*R2, ("C'", "K"): -0.5*R2, ("K", "G"): 0.5*R2}


def _sanity():
    for m in TM:
        assert abs(U0[m] - U0_DOC[m]) < 1e-9, (m, U0[m], U0_DOC[m])
    assert abs(H_of(RD_of(1.0)) - (RD_of(1.0) - 20.0)) < 1e-12
    # 參數解須落在兩個極限之間
    for a in (0.01, 0.1, 1.0, 10.0, 100.0):
        assert DJ_STIFF - 1e-6 <= dJ_of(a) <= DJ_SOFT + 1e-6, (a, dJ_of(a))
    assert abs(DJ_SOFT - 573.36) < 0.02 and abs(DJ_STIFF - 341.44) < 0.02, (DJ_SOFT, DJ_STIFF)
    # 樑段與桁架段的組合式在 α=1 時應使 B + T = 0
    a = 1.0; rd = RD_of(a)
    assert abs(beam_term(rd)/a + truss_term(rd)) < 1e-6


def _truss(cv, forces=None, fmt="{:+.4g}", lab=None, width=True):
    peak = max((abs(v) for v in (forces or {}).values()), default=1.0) or 1.0
    for m in TM:
        p0, p1 = TN[m[0]], TN[m[1]]
        if forces is None:
            cv.line(p0, p1, C["member"], 4.0, cap="butt"); continue
        v = forces[m]
        if abs(v) < 1e-9:
            cv.line(p0, p1, C["muted"], 2.2, dash="7 5")
        else:
            cv.line(p0, p1, C["tension"] if v > 0 else C["compr"],
                    2.8 + (3.8*abs(v)/peak if width else 1.4), cap="butt")
        t, side = (lab or {}).get(m, (0.5, 1))
        mx = p0[0] + (p1[0]-p0[0])*t; my = p0[1] + (p1[1]-p0[1])*t
        dx, dy = p1[0]-p0[0], p1[1]-p0[1]; L = math.hypot(dx, dy)
        col = C["muted"] if abs(v) < 1e-9 else (C["tension"] if v > 0 else C["compr"])
        cv.math_px(cv.X(mx) - dy/L*15*side, cv.Y(my) - dx/L*15*side,
                   fmt.format(v).replace("-", "−"), 12, col, weight="700")
    for nm, p in TN.items():
        cv.dot(p, 4.8)


# ══════════════════════════════════════════════════════════
def fig1_frame():
    """題目重繪：樑與桁架是兩個構件，只透過滾支承傳垂直力"""
    W, H = 900, 540
    YB = 2.4                                  # 繪圖用：樑畫在桁架上弦之上（實際不計深度）
    cv = Canvas(W, H, sx=16.0, ox=120, oy=301.6, bg="#FFFFFF")
    _truss(cv)
    cv.line((0, YB), (SPAN, YB), C["member2"], 7.0, cap="butt")
    # 支承
    cv.roller_support((0, YB), 0)
    cv.support(TN["F"], "pin"); cv.support(TN["G"], "pin")
    for x in (XB, XD):
        cv.circle((x, YB/2), YB/2, fill="#FFFFFF", stroke=C["accent"], w=2.8)
    for x, lab in ((XP1, "10 kN"), (XP2, "10 kN")):
        cv.arrow((x, YB+3.4), (x, YB), C["load"], 3.2, 11)
        cv.text_px(cv.X(x), cv.Y(YB+3.4)-15, lab, 13.5, C["load"], weight="700")
    for nm, x in (("A", XA), ("B", XB), ("C", 2*BAY), ("D", XD), ("E", SPAN)):
        cv.dot((x, YB), 5.0)
        cv.text_px(cv.X(x), cv.Y(YB)-22, nm, 15.5, C["text"], weight="700")
    for nm, p in TN.items():
        if nm == "F":   dx_, dy_ = -34, 0
        elif nm == "G": dx_, dy_ = 34, 0
        elif p[1] == 0: dx_, dy_ = -20, -14
        else:           dx_, dy_ = 0, 24
        cv.text_px(cv.X(p[0])+dx_, cv.Y(p[1])+dy_, nm, 14.5, C["muted"], weight="700")
    cv.dim((0, -HGT), (SPAN, -HGT), "4 @ 10 m = 40 m", off=62, label_off=16)
    cv.dim((0.0, 0.0), (0.0, -HGT), "10 m", off=64, label_off=16)
    cv.dim((0, YB), (XP1, YB), "15 m", off=-104, label_off=-15)
    cv.dim((XP1, YB), (XP2, YB), "10 m", off=-104, label_off=-15)
    cv.dim((XP2, YB), (SPAN, YB), "15 m", off=-104, label_off=-15)
    cv.text_px(W/2, 32, "題目重繪（向量版）：樑 AE 疊在桁架上，兩者只在 B、D 以滾支承接觸",
               16.5, C["text"], weight="700")
    cv.text_px(W/2, 56, "A 為滾支承（地面）；B、D 為滾支承（橘色圈，只傳垂直力）；F、G 為鉸支承；E 端自由；E、I、A 皆為常數",
               13, C["muted"])
    cv.text_px(W/2, H-24,
               "樑不是桁架的上弦桿：滾支承不傳水平力，故桁架另有自己的上弦桿 F–B′–C′–D′–G。",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-1-frame.svg")


# ══════════════════════════════════════════════════════════
def fig2_fbd():
    """分離自由體：兩個贅力 R_D 與 H 的來源"""
    W, H = 640, 460
    a = Canvas(W, H, sx=12.6, ox=76, oy=196, bg="#FFFFFF")
    a.line((0, 0), (SPAN, 0), C["member2"], 6.5, cap="butt")
    for x, lab in ((XP1, "10 kN"), (XP2, "10 kN")):
        a.arrow((x, 4.2), (x, 0), C["load"], 3.0, 10)
        a.text_px(a.X(x), a.Y(4.2)-14, lab, 12.5, C["load"], weight="700")
    for x, lab, col in ((XA, "R_{A} = 2R_{D} − 20", C["deform"]),
                        (XB, "R_{B} = 40 − 3R_{D}", C["deform"]),
                        (XD, "R_{D}", C["accent"])):
        a.arrow((x, -4.6), (x, -0.4), col, 3.0, 10)
        a.math_px(a.X(x), a.Y(-4.6)+18, lab, 12.5, col, weight="700")
        if x == XD:
            a.text_px(a.X(x), a.Y(-4.6)+38, "贅力 ①", 12, col, weight="700")
    for nm, x in (("A", XA), ("B", XB), ("D", XD), ("E", SPAN)):
        a.dot((x, 0), 5.0); a.text_px(a.X(x), a.Y(0)-20, nm, 15, C["text"], weight="700")
    a.text_px(W/2, 32, "① 樑 AE 的自由體", 16, C["text"], weight="700")
    a.text_px(W/2, H-52, "三個垂直支承、兩條平衡方程 ⇒ 一度靜不定", 13, C["muted"])
    a.text_px(W/2, H-30, "取 R_D 為贅力，R_A、R_B 由靜力平衡以 R_D 表示", 13, C["muted"])

    b = Canvas(W, H, sx=11.4, ox=90, oy=260, bg="#FFFFFF")
    _truss(b)
    b.support(TN["F"], "pin"); b.support(TN["G"], "pin")
    for x, lab in ((XB, "P_{B} = 40 − 3R_{D}"), (XD, "P_{D} = R_{D}")):
        b.arrow((x, 4.6), (x, 0.4), C["load"], 3.0, 10)
        b.math_px(b.X(x), b.Y(4.6)-14, lab, 12.5, C["load"], weight="700")
    b.arrow((0, -5.2), (0, -0.9), C["deform"], 2.8, 9)
    b.math_px(b.X(0)-6, b.Y(-5.2)+18, "F_{y} = 30 − 2R_{D}", 12.5, C["deform"], "middle", weight="700")
    b.arrow((SPAN, -5.2), (SPAN, -0.9), C["deform"], 2.8, 9)
    b.math_px(b.X(SPAN), b.Y(-5.2)+18, "G_{y} = 10", 12.5, C["deform"], weight="700")
    b.arrow((-4.6, 0), (-0.6, 0), C["accent"], 2.8, 9)
    b.math_px(b.X(-4.6)-6, b.Y(0)-16, "H", 14, C["accent"], "start", weight="700")
    b.text_px(b.X(-4.6)-6, b.Y(0)+18, "贅力 ②", 12, C["accent"], "start", weight="700")
    b.arrow((SPAN+4.6, 0), (SPAN+0.6, 0), C["accent"], 2.8, 9)
    b.math_px(b.X(SPAN+4.6)+6, b.Y(0)-16, "H", 12.5, C["accent"], "end", weight="700")
    for nm, p in TN.items():
        dx_, dy_ = (-16, -13) if p[1] == 0 else (0, 20)
        b.text_px(b.X(p[0])+dx_, b.Y(p[1])+dy_, nm, 13.5, C["muted"], weight="700")
    b.text_px(W/2, 32, "② 桁架的自由體", 16, C["text"], weight="700")
    b.text_px(W/2, H-52, "F、G 皆為鉸支承 ⇒ 四個反力、三條平衡方程 ⇒ 一度靜不定", 13, C["muted"])
    b.text_px(W/2, H-30, "取水平反力 H 為第二個贅力（不可假設 H = 0）", 13, C["muted"])
    path = f"{OUT}/{TAG}-fig-2-fbd.svg"
    compose([a, b], cols=2, path=path,
            title="把系統拆成兩個自由體：整體為二度靜不定（兩個贅力：R꞉D 與 H）".replace("R꞉D", "R_D"),
            sub="樑傳給桁架的只有 B′、D′ 兩個垂直力；桁架的水平推力由 F、G 的鉸支承承擔",
            note="漏掉 H 是本題最常見的失分點：F、G 皆為鉸，桁架受載後會向外撐，"
                 "必有水平反力才能平衡。")
    return path


# ══════════════════════════════════════════════════════════
def fig3_virtual():
    """虛力系統 u0：靜定基本結構下的桁架虛內力（純數值，與 R_D 無關）"""
    W, H = 900, 560
    cv = Canvas(W, H, sx=16.0, ox=120, oy=323.6, bg="#FFFFFF")
    cv.line((0, 2.4), (SPAN, 2.4), C["ghost"], 5.0, dash="8 6", cap="butt")
    cv.text_px(cv.X(SPAN/2), cv.Y(2.4)-18,
               "樑：基本結構中已與桁架切離、且無虛載重 ⇒ 虛彎矩 m_{0} ≡ 0",
               13.5, C["muted"], weight="700")
    lab = {("F", "H"): (0.34, 1), ("H", "C'"): (0.66, 1),
           ("C'", "K"): (0.34, 1), ("K", "G"): (0.38, 1),
           ("H", "J"): (0.5, -1), ("J", "K"): (0.5, -1)}
    _truss(cv, U0, fmt="{:+.4g}", lab=lab)
    cv.support(TN["F"], "pin"); cv.roller_support(TN["G"], 0, color=C["accent"])
    cv.arrow((2*BAY, -HGT), (2*BAY, -HGT-4.6), C["load"], 3.2, 11)
    cv.text_px(cv.X(2*BAY), cv.Y(-HGT-4.6)+22, "1 kN（向下）", 14, C["load"], weight="700")
    for nm, p in TN.items():
        dx_, dy_ = (-18, -14) if p[1] == 0 else (-18, 16)
        cv.text_px(cv.X(p[0])+dx_, cv.Y(p[1])+dy_, nm, 14.5, C["text"], weight="700")
    cv.legend(28, H-136, [(C["tension"], "虛內力 受拉 (+)"), (C["compr"], "虛內力 受壓 (−)"),
                          (C["muted"], "零桿"), (C["ghost"], "已切離、m_{0} = 0 的樑")])
    cv.text_px(28, H-56, "橘色滾支承：G 由鉸改為滾 ⇒ 虛力系統中 H = 0（基本結構的第二個釋放）",
               12.5, C["accent"], "start", weight="700")
    cv.text_px(W/2, 32, "虛力系統 u_{0}：J 點單位力作用於「切斷 R_D、G 改滾支承」的靜定基本結構",
               16, C["text"], weight="700")
    cv.text_px(W/2, 56, "數值由本腳本以節點法重新解出，並與 §4 Step 4 的清單逐桿比對", 13, C["muted"])
    cv.text_px(W/2, H-24,
               "上弦四桿的 u_{0} 全為 −0.5，而真實內力總和為零 ⇒ 上弦對 Δ_{J} 完全沒有貢獻。",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-3-virtual.svg")


# ══════════════════════════════════════════════════════════
def fig4_alpha():
    """Δ_J 隨 α = EI/EA 的變化：參數解有上下界，不可亂假設"""
    W, H = 880, 540
    Lm, Rm, Tm, Bm = 116, 210, 92, 92
    A0, A1 = -2.0, 3.0            # log10(α)
    Y0, Y1 = 300.0, 620.0
    kx = (W-Lm-Rm)/(A1-A0); ky = (H-Tm-Bm)/(Y1-Y0)
    cv = Canvas(W, H, sx=1.0, bg="#FFFFFF")
    def PX(la, v): return (Lm + (la-A0)*kx, H - Bm - (v-Y0)*ky)
    def seg(p, q, col, w=3.2, dash=None):
        (x0, y0), (x1, y1) = PX(*p), PX(*q)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        cv.parts.append(f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" '
                        f'stroke="{col}" stroke-width="{w}" stroke-linecap="round"{d}/>')
    seg((A0, Y0), (A1, Y0), C["muted"], 1.8); seg((A0, Y0), (A0, Y1), C["muted"], 1.8)
    for la in range(int(A0), int(A1)+1):
        x, y = PX(la, Y0); cv.text_px(x, y+20, f"10^{{{la}}}", 12.5, C["muted"])
        cv.parts.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+6}" stroke="{C["muted"]}" stroke-width="1.4"/>')
    for v in (300, 350, 400, 450, 500, 550, 600):
        x, y = PX(A0, v); cv.text_px(x-12, y, f"{v}", 12, C["muted"], "end")
        cv.parts.append(f'<line x1="{x-6}" y1="{y}" x2="{x}" y2="{y}" stroke="{C["muted"]}" stroke-width="1.4"/>')
    cv.text_px(Lm+(W-Lm-Rm)/2, H-30, "剛度比　α = EI / EA", 14, C["muted"])
    cv.parts.append(f'<text x="34" y="{Tm+160}" font-size="14" fill="{C["muted"]}" '
                    f'transform="rotate(-90 34 {Tm+160})" text-anchor="middle" '
                    f'font-family="{FONT}">J 點垂直變位 ΔJ · EA  (kN·m)</text>')
    # 兩條漸近線
    for v, txt, col in ((DJ_SOFT, f"α → 0（樑極柔）：{DJ_SOFT:.1f}", C["load"]),
                        (DJ_STIFF, f"α → ∞（樑極剛）：{DJ_STIFF:.1f}", C["deform"])):
        seg((A0, v), (A1, v), col, 2.2, dash="8 6")
        x, y = PX(A1, v)
        cv.text_px(x+12, y, txt, 12.5, col, "start", weight="700")
    pts = []
    for i in range(801):
        la = A0 + (A1-A0)*i/800
        pts.append("%.2f,%.2f" % PX(la, dJ_of(10**la)))
    cv.parts.append(f'<polyline points="{" ".join(pts)}" fill="none" stroke="{C["bmd"]}" '
                    f'stroke-width="4.0" stroke-linejoin="round"/>')
    for la in (-1.0, 0.0, 1.0, 2.0):
        x, y = PX(la, dJ_of(10**la))
        cv.parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="5.2" fill="#FFFFFF" '
                        f'stroke="{C["bmd"]}" stroke-width="2.6"/>')
    x, y = PX(0.0, dJ_of(1.0))
    cv.text_px(x-16, y+26, f"α = 1 時 Δ_{{J}} = {dJ_of(1.0):.1f} / EA", 13, C["bmd"], "end", weight="700")
    cv.text_px(W/2, 34, "參數解不是「算不出來」，而是一條有上下界的曲線", 17, C["text"], weight="700")
    cv.text_px(W/2, 58, f"不論 EI/EA 為何，Δ_{{J}}·EA 必落在 {DJ_STIFF:.0f} ～ {DJ_SOFT:.0f} 之間（相差僅 {DJ_SOFT/DJ_STIFF:.2f} 倍）",
               13, C["muted"])
    cv.text_px(W/2, H-18,
               "考場上若擅自假設「樑剛性無限大」或「桁架無限剛」，等於直接取到端點值，屬過度推論。",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-4-alpha.svg")


FIGURES = [
    (fig1_frame,   "攔下「把樑當成桁架上弦桿」與支承型式誤讀"),
    (fig2_fbd,     "攔下漏掉水平贅力 H、以及贅力選取後反力表示式寫錯"),
    (fig3_virtual, "攔下基本結構選錯（以為要用原靜不定結構）與零桿誤判"),
    (fig4_alpha,   "攔下擅自假設 EI/EA 比值、或對參數解沒有信心"),
]

if __name__ == "__main__":
    _sanity()
    for fn, why in FIGURES:
        print(f"{fn():<52}  ← {why}")

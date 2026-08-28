#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""SA-2019-1 靜不定桁架漸進破壞 — 解題圖解產生腳本

用法： python3 gen_SA-2019-1.py [輸出目錄]

三條鐵則的落實：
  1. 圖上每個桿力都由下方常數區的內力係數 × 該階段的臨界載重算出，未硬寫。
  2. 改 CAP_* 或幾何，圖形與臨界載重自動跟著變。
  3. 每張圖攔的錯寫在 FIGURES 表。
"""
import sys, os, glob

_cand = sorted(glob.glob(os.path.expanduser("~/.claude/skills/**/struct-diagram/scripts"),
                         recursive=True))
sys.path.insert(0, _cand[0] if _cand else "/root/.claude/skills/synced/struct-diagram/scripts")

from structdraw import Canvas, C, FONT_M, compose


OUT = sys.argv[1] if len(sys.argv) > 1 else "figs"
TAG = "SA-2019-1"

# ══════════════════════════════════════════════════════════
# 解題結果（全部來自 SA-2019-1.md，勿手動改動）
# ══════════════════════════════════════════════════════════
# §1 幾何
LH, LV, LD = 12.0, 9.0, 15.0                 # 水平 / 垂直 / 對角桿長 (m)
# §1 桿件強度
CAP_T          = 1250.0                      # 各桿軸拉強度 (kN)
CAP_C_DIAG     = 144.0                       # 對角桿軸壓強度
CAP_C_HORIZ    = 225.0                       # 水平桿軸壓強度
CAP_C_VERT     = 400.0                       # 垂直桿軸壓強度

# §4 Step 1：最小功法解得之贅力（以 P 為單位）
T_COEF = -95/216                             # F_DA / P

# §4 Step 1：各桿內力係數 F_i / P（第一階段，靜不定）
S1 = {("D","A"): T_COEF,
      ("C","B"): 1.25 + T_COEF,              # = +175/216
      ("D","B"): -0.8*T_COEF,
      ("C","A"): -0.8*T_COEF,
      ("D","C"): -0.6*T_COEF,
      ("B","A"): -0.75 - 0.6*T_COEF}         # = -105/216

# §4 Step 2：DA 挫曲退出後（靜定）之內力係數
S2 = {("D","A"): 0.0, ("C","B"): 1.25, ("D","B"): 0.0,
      ("C","A"): 0.0, ("D","C"): 0.0, ("B","A"): -0.75}

# §4 Step 1 / Step 3：兩階段之臨界載重（由係數與強度算出，非抄寫）
P1    = CAP_C_DIAG / abs(S1[("D","A")])      # = 327.41 kN，DA 先挫曲
P_ULT = CAP_C_VERT / abs(S2[("B","A")])      # = 533.33 kN，AB 挫曲 → 機構

# §4 Step 1 / Step 2：兩階段之柔度（U_B · EA / P）
F1 = LD*S1[("C","B")]*1.25 + LV*S1[("B","A")]*(-0.75)     # = 665/36
F2 = LD*S2[("C","B")]*1.25 + LV*S2[("B","A")]*(-0.75)     # = 28.5

U1  = F1 * P1                                # 6048/EA
U1B = F2 * P1                                # 9331.2/EA（跳躍後）
U2  = F2 * P_ULT                             # 15200/EA

NODES = {"C": (0.0, 0.0), "A": LH, "D": 0.0, "B": LH}
NODES = {"C": (0.0, 0.0), "A": (LH, 0.0), "D": (0.0, LV), "B": (LH, LV)}


def _sanity():
    assert abs(P1 - 327.41) < 0.01, P1
    assert abs(P_ULT - 533.333) < 0.01, P_ULT
    assert abs(F1 - 665/36) < 1e-9, F1
    assert abs(F2 - 28.5) < 1e-9, F2
    assert abs(U1 - 6048.0) < 0.01 and abs(U1B - 9331.2) < 0.1 and abs(U2 - 15200.0) < 0.1
    # DA 必須是第一階段最先失效者
    caps = {("D","A"): CAP_C_DIAG, ("C","B"): CAP_T, ("D","B"): CAP_T,
            ("C","A"): CAP_T, ("D","C"): CAP_T, ("B","A"): CAP_C_VERT}
    first = min(caps, key=lambda k: caps[k]/abs(S1[k]))
    assert first == ("D","A"), first


# ══════════════════════════════════════════════════════════
def _truss_panel(members, P, title, note, W=620, H=520):
    """自繪桁架力流圖（recipe 的標註一律置於桿中點，兩根對角桿會疊字，故自組）。"""
    import math
    xs = [p[0] for p in NODES.values()]; ys = [p[1] for p in NODES.values()]
    Lm, Rm, Tm, Bm = 118, 152, 118, 128
    sc = min((W-Lm-Rm)/(max(xs)-min(xs)), (H-Tm-Bm)/(max(ys)-min(ys)))
    cv = Canvas(W, H, sx=sc, ox=Lm-min(xs)*sc, oy=Bm-min(ys)*sc, bg="#FFFFFF")
    peak = max(abs(m[2]) for m in members) or 1.0
    for n1, n2, N, t, side in members:
        p0, p1 = NODES[n1], NODES[n2]
        if abs(N) < 1e-9:
            cv.line(p0, p1, C["muted"], 2.4, dash="7 5")
            col = C["muted"]
        else:
            col = C["tension"] if N > 0 else C["compr"]
            cv.line(p0, p1, col, 3.2 + 4.6*abs(N)/peak, cap="butt")
        mx = p0[0] + (p1[0]-p0[0])*t; my = p0[1] + (p1[1]-p0[1])*t
        dx, dy = p1[0]-p0[0], p1[1]-p0[1]; L = math.hypot(dx, dy) or 1
        cv.math_px(cv.X(mx) - dy/L*18*side, cv.Y(my) - dx/L*18*side,
                   f"{N:+.1f}".replace("-", "\u2212"), 13.5, col, weight="700")
    cv.support(NODES["C"], "pin"); cv.support(NODES["A"], "roller")
    tip = (NODES["B"][0] + 0.30*LH, NODES["B"][1])
    cv.arrow(NODES["B"], tip, C["load"], 3.4, 12)
    cv.math_px(cv.X(tip[0]) + 12, cv.Y(tip[1]), "P", 18, C["load"], "start", weight="700")
    for nm, (px, py) in NODES.items():
        cv.dot((px, py), 5.6)
        ox = -22 if px == min(xs) else 22
        oy = -18
        cv.text_px(cv.X(px)+ox, cv.Y(py)+oy, nm, 16, C["text"], weight="700")
    cv.legend(24, H-72, [(C["tension"], "受拉 (+)"), (C["compr"], "受壓 (−)"),
                         (C["muted"], "內力為零 / 已退出")])
    cv.text_px(W/2, 34, title, 16, C["text"], weight="700")
    cv.text_px(W/2, H-22, note, 13, C["muted"])
    return cv


def fig1_truss_stages():
    """兩階段桁架力流對照：各桿在其階段臨界載重下的實際軸力 (kN)"""
    # (桿, 標註位置比例 t, 偏移側) —— 兩根對角桿分別標在 30% / 72% 處以免疊字
    LAYOUT = [("D","B",0.50, 1), ("C","A",0.50,-1), ("D","C",0.50, 1),
              ("B","A",0.50, 1), ("D","A",0.28, 1), ("C","B",0.74, 1)]
    def mk(S, P):
        return [(a, b, S[(a, b)]*P, t, sd) for a, b, t, sd in LAYOUT]
    p1 = _truss_panel(mk(S1, P1), P1,
                      f"第一階段（一度靜不定）：P = P_{{1}} = {P1:.2f} kN",
                      f"DA 達對角桿壓力強度 {CAP_C_DIAG:.0f} kN → 最先挫曲")
    p2 = _truss_panel(mk(S2, P_ULT), P_ULT,
                      f"第二階段（靜定）：P = P_{{ult}} = {P_ULT:.2f} kN",
                      f"AB 達垂直桿壓力強度 {CAP_C_VERT:.0f} kN → 形成機構")
    path = f"{OUT}/{TAG}-fig-1-truss.svg"
    compose([p1, p2], cols=2, path=path,
            title="桁架力流：DA 挫曲前後的內力重分配（數值單位 kN，+ 受拉 / − 受壓）",
            sub="DA 退出後 DB、DC、AC 三根由受拉直接歸零，載重全部改由 CB、AB 承擔",
            note="AC 在第一階段並非零桿（+115.2 kN）——A 為滾支承不提供水平反力，"
                 "不代表 AC 不受力。這是本題最常見的誤判。")
    return path


# ══════════════════════════════════════════════════════════
def _axes(cv, x0, x1, y0, y1, xlab, ylab, xticks, yticks, xfmt="{:.0f}", yfmt="{:.0f}"):
    cv.line((x0, y0), (x1, y0), C["muted"], 1.8)
    cv.line((x0, y0), (x0, y1), C["muted"], 1.8)
    for t in xticks:
        cv.line((t, y0), (t, y0 - (y1-y0)*0.016), C["muted"], 1.4)
        cv.text((t, y0), xfmt.format(t), 12, C["muted"], dy=20)
    for t in yticks:
        cv.line((x0, t), (x0 - (x1-x0)*0.012, t), C["muted"], 1.4)
        cv.text((x0, t), yfmt.format(t), 12, C["muted"], anchor="end", dx=-10)
    cv.text((x1, y0), xlab, 13.5, C["muted"], dy=42)
    cv.text((x0, y1), ylab, 13.5, C["muted"], dy=-26)


def fig2_p_u():
    """P–U_B 關係圖（題目明文要求繪製）"""
    XMAX, YMAX = 17500.0, 610.0
    W, H = 860, 560
    Lm, Rm, Tm, Bm = 104, 190, 66, 74
    sx = min((W-Lm-Rm)/XMAX, (H-Tm-Bm)/YMAX)
    cv = Canvas(W, H, sx=1.0, ox=0, oy=0, bg="#FFFFFF")
    # 自訂等向縮放不適用（兩軸單位差異太大），改用兩個獨立比例，直接畫像素
    kx = (W-Lm-Rm)/XMAX
    ky = (H-Tm-Bm)/YMAX
    def PX(u, p): return (Lm + u*kx, H - Bm - p*ky)

    def line(a, b, col, w=3.4, dash=None):
        (x0,y0),(x1,y1) = PX(*a), PX(*b)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        cv.parts.append(f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" '
                        f'stroke="{col}" stroke-width="{w}" stroke-linecap="round"{d}/>')

    # 座標軸
    line((0,0), (XMAX,0), C["muted"], 1.8)
    line((0,0), (0,YMAX), C["muted"], 1.8)
    for u in (0, 3000, 6000, 9000, 12000, 15000):
        x, y = PX(u, 0); cv.text_px(x, y+20, f"{u:,}", 12, C["muted"])
        cv.parts.append(f'<line x1="{x}" y1="{y}" x2="{x}" y2="{y+6}" stroke="{C["muted"]}" stroke-width="1.4"/>')
    for p in (0, 100, 200, 300, 400, 500, 600):
        x, y = PX(0, p); cv.text_px(x-12, y, f"{p}", 12, C["muted"], "end")
        cv.parts.append(f'<line x1="{x-6}" y1="{y}" x2="{x}" y2="{y}" stroke="{C["muted"]}" stroke-width="1.4"/>')
    cv.text_px(Lm + (W-Lm-Rm)/2, H-24, "B 點水平位移   U_{B} · EA   (kN·m)", 14, C["muted"])
    cv.parts.append(f'<text x="34" y="{Tm+120}" font-family="{FONT_M}" font-size="15" '
                    f'fill="{C["muted"]}" transform="rotate(-90 34 {Tm+120})" text-anchor="middle">'
                    f'外力 P (kN)</text>')

    # 三段路徑
    line((0,0), (U1, P1), C["deform"], 4.2)                       # 第一階段
    line((U1,P1), (U1B,P1), C["load"], 4.2, dash="9 6")           # 位移跳躍
    line((U1B,P1), (U2,P_ULT), C["bmd"], 4.2)                     # 第二階段
    line((U2,P_ULT), (XMAX*0.985, P_ULT), C["muted"], 4.2, dash="4 7")  # 機構

    # 輔助虛線
    for u, p in ((U1,P1), (U1B,P1), (U2,P_ULT)):
        line((u,0),(u,p), C["ghost"], 1.4, dash="4 5")
        line((0,p),(u,p), C["ghost"], 1.4, dash="4 5")
    for u, p in ((U1,P1), (U1B,P1), (U2,P_ULT)):
        x, y = PX(u, p); cv.dot((0,0)) if False else None
        cv.parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="6" fill="#FFFFFF" '
                        f'stroke="{C["accent"]}" stroke-width="3"/>')

    # 標註
    x, y = PX(U1, P1)
    cv.text_px(x-18, y-32, f"DA 挫曲：P_{{1}} = {P1:.2f} kN", 13.5, C["deform"], "end", weight="700")
    cv.math_px(x-18, y-13, f"U_{{B}} EA = {U1:,.0f}", 13, C["deform"], "end")
    x, y = PX((U1+U1B)/2, P1)
    cv.text_px(x, y+26, "位移瞬間跳躍（P 不變）", 13, C["load"], weight="700")
    cv.math_px(x, y+45, f"ΔU_{{B}} EA = {U1B-U1:,.1f}", 12.5, C["load"])
    x, y = PX(U2, P_ULT)
    cv.text_px(x+22, y+22, "AB 挫曲 → 破壞機構", 13.5, C["bmd"], "start", weight="700")
    cv.math_px(x+22, y+42, f"P_{{ult}} = {P_ULT:.2f} kN", 13, C["bmd"], "start")
    cv.math_px(x+22, y+62, f"U_{{B}} EA = {U2:,.0f}", 13, C["bmd"], "start")

    # 勁度標註
    xm, ym = PX(U1*0.5, P1*0.5)
    cv.math_px(xm-8, ym-16, f"k_{{1}} = EA/{F1:.3f}", 13.5, C["deform"], "end", weight="700")
    xm, ym = PX((U1B+U2)/2, (P1+P_ULT)/2)
    cv.math_px(xm+10, ym+22, f"k_{{2}} = EA/{F2:.1f}", 13.5, C["bmd"], "start", weight="700")

    cv.legend(W-192, H-206, [(C["deform"], "階段一：靜不定"),
                            (C["load"],   "挫曲後位移跳躍"),
                            (C["bmd"],    "階段二：靜定"),
                            (C["muted"],  "機構（P 不再增加）")])
    cv.text_px(W/2, 34, "P – U_{B} 關係圖（座標為真實計算值，非示意）", 17, C["text"], weight="700")
    cv.text_px(W/2, 56, "壓桿挫曲後內力歸零 ⇒ 勁度下降且位移水平跳躍；兩段皆為直線（線彈性）",
               13, C["muted"])
    return cv.save(f"{OUT}/{TAG}-fig-2-p-u.svg")


FIGURES = [
    (fig1_truss_stages, "攔下「A 為滾支承 ⇒ AC 是零桿」的誤判，以及拉壓正負號寫反"),
    (fig2_p_u,          "攔下把位移跳躍畫成連續曲線、或把兩段斜率畫反"),
]

if __name__ == "__main__":
    _sanity()
    for fn, why in FIGURES:
        print(f"{fn():<52}  ← {why}")

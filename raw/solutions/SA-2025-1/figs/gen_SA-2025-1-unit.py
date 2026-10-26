#!/usr/bin/env python3
"""
SA-2025-1 勁度矩陣「圖解法」：三個單位位移實驗，各求一直行（column）
用法：python3 gen_SA-2025-1-unit.py [輸出目錄＝本腳本所在 figs/]
相依：同目錄 structdraw_v2.py（struct-diagram skill 新版；舊 structdraw.py 留給 gen_sa2025_1.py）

每個狀態三格：① 變形 → ② 桿端力（作用在桿件上）→ ③ 節點外力 ＝ K 的第 j 直行
所有桿端力由傾角變位公式算出（EI=L=1 的係數，單位另行標註），K 由節點加總得到，
不手填任何一個係數。
"""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from structdraw_v2 import Canvas, C, compose, column_shape, beam_shape

OUT = sys.argv[1] if len(sys.argv) > 1 else HERE
TAG = "SA-2025-1"

# ══════════════════════════════════════════════════════════
# 力學（SA-2025-1 §4.2 傾角變位公式；轉角與彎矩順時針為正，Δ 與水平力向右為正）
#   M_nf = 2EI/L (2θn + θf − 3ψ)，柱的弦轉角 ψ = Δ/L
# ══════════════════════════════════════════════════════════
def member_end_forces(tB, tC, D):
    """回傳各桿端力係數（作用在桿件上）。單位：θ 狀態彎矩 EI/L、剪力 EI/L²；Δ 狀態再多一次 1/L。"""
    f = {}
    # 柱 AB（近端 B、遠端 A）
    f["M_BA"] = 2 * (2 * tB + 0 - 3 * D)
    f["M_AB"] = 2 * (2 * 0 + tB - 3 * D)
    f["H_B"] = -(f["M_BA"] + f["M_AB"])        # 柱頂水平力（向右＋）；對柱底取矩 ΣM=0
    f["H_A"] = -f["H_B"]
    # 柱 DC（近端 C、遠端 D）
    f["M_CD"] = 2 * (2 * tC - 3 * D)
    f["M_DC"] = 2 * (tC - 3 * D)
    f["H_C"] = -(f["M_CD"] + f["M_DC"])
    f["H_D"] = -f["H_C"]
    # 梁 BC（ψ = 0，柱不縮短）
    f["M_BC"] = 2 * (2 * tB + tC)
    f["M_CB"] = 2 * (2 * tC + tB)
    f["V_C"] = f["M_BC"] + f["M_CB"]           # C 端向上（由柱軸力承擔，不進 K）
    f["V_B"] = -f["V_C"]
    return f

def K_column(f):
    """節點平衡：外加力 ＝ 匯集到該節點的桿端力總和"""
    return (f["M_BA"] + f["M_BC"], f["M_CD"] + f["M_CB"], f["H_B"] + f["H_C"])

STATES = [  # (tB, tC, D, 名稱)
    (1, 0, 0, r"θ_{B} = 1"),
    (0, 1, 0, r"θ_{C} = 1"),
    (0, 0, 1, r"Δ = 1"),
]

def unit(row_is_force, col_is_delta):
    p = 1 + row_is_force + col_is_delta
    return "EI/L" if p == 1 else f"EI/L^{{{p}}}"

def fmt(v, row_is_force, col_is_delta, signed=True):
    if v == 0: return "0"
    s = ("−" if v < 0 else "") if signed else ""
    return f"{s}{abs(v)}{unit(row_is_force, col_is_delta)}"

# ══════════════════════════════════════════════════════════
PW, PH, SX, OX, OY = 372, 470, 150, 111, 170
MW = 6.0
GAP = 0.05          # 自由體圖中桿件之間的間隙

def ghost(cv):
    for s, e in (((0, 0), (0, 1)), ((0, 1), (1, 1)), ((1, 1), (1, 0))):
        cv.line(s, e, C["ghost"], 3.0, dash="6 5", cap="butt")

def mom(cv, p, v, lab, out, color, r=22, lr=None, span=200, lab_out=None):
    """彎矩箭頭（v>0 順時針），弧開口朝結構內側、弧身在 out 方向（度）；標籤放在 out 方向外側"""
    import math
    if v == 0: return
    st = out + span / 2 if v > 0 else out - span / 2
    cv.moment_arrow(p, r=r, ccw=(v < 0), color=color, w=2.6, span=span, start=st)
    d = (lr or r + 16)
    lo = out if lab_out is None else lab_out
    ox, oy = math.cos(math.radians(lo)), -math.sin(math.radians(lo))
    anchor = "start" if ox > 0.35 else ("end" if ox < -0.35 else "middle")
    cv.math_px(cv.X(p[0]) + ox * d, cv.Y(p[1]) + oy * d + (5 if oy > 0.3 else 0), lab, 13.5, color, anchor, weight="700")

def harrow(cv, p, v, lab, color, lab_dy=-14, length=0.30, push=True, lab_x=None, anchor=None):
    """作用在 p 點的水平力（v>0 向右）。push=True：頭端貼 p；False：尾端貼 p（拉）"""
    if v == 0: return
    x, y = p
    sgn = 1 if v > 0 else -1
    a, e = ((x - sgn * length, y), (x, y)) if push else ((x, y), (x + sgn * length, y))
    cv.arrow(a, e, color, 3.0, 10)
    far = a[0] if push else e[0]                       # 遠離構件的那一端
    outward = 1 if far > x else -1
    lx = lab_x if lab_x is not None else far + outward * 0.03
    anc = anchor or ("start" if outward > 0 else "end")
    cv.math_px(cv.X(lx), cv.Y(y) + lab_dy, lab, 13.5, color, anc, weight="700")

def varrow(cv, p, v, color, length=0.17):
    if v == 0: return
    x, y = p
    a = (x, y - length) if v > 0 else (x, y + length)
    cv.arrow(a, (x, y), color, 2.0, 8)

def panel_deform(tB, tC, D, name, j):
    cv = Canvas(PW, PH, sx=SX, ox=OX, oy=OY)
    cv.panel("① 單位位移實驗", "")
    plain = name.replace("_{", "").replace("}", "")
    cv.text_px(PW / 2, 56, f"令 {plain}，其餘自由度鎖住", 13, C["muted"])
    ghost(cv)
    d = 0.17 * D
    b, c = -0.42 * tB, -0.42 * tC                      # 繪圖放大；轉為逆時針正
    cv.poly(column_shape((0, 0), 1.0, d, b), C["deform"], 5.0)
    cv.poly(column_shape((1, 0), 1.0, d, c), C["deform"], 5.0)
    cv.poly(beam_shape((d, 1), 1.0, b, c), C["deform"], 5.0)
    cv.fixed_support((0, 0), size=17); cv.fixed_support((1, 0), size=17)
    for p in ((d, 1), (1 + d, 1)):
        cv.dot(p, 4.5, fill=C["deform"])
    for p, lab, dx, dy in (((0, 0), "A", -30, -14), ((d, 1), "B", -22, 22), ((1 + d, 1), "C", 32, 26), ((1, 0), "D", 30, -14)):
        cv.text(p, lab, 15, C["text"], weight="700", dx=dx, dy=dy)
    if tB: cv.moment_arrow((0, 1), r=24, ccw=False, color=C["deform"], w=2.6, span=235, start=205)
    if tC: cv.moment_arrow((1, 1), r=24, ccw=False, color=C["deform"], w=2.6, span=235, start=160)
    if D:  cv.arrow((d + 0.10, 1.22), (d + 0.42, 1.22), C["deform"], 2.8, 10)
    lab = {0: ("B 點順時針轉 1", -0.02), 1: ("C 點順時針轉 1", 1.02), 2: ("頂部向右移 1", 0.5)}[j]
    cv.text((lab[1], 1.40), lab[0], 13, C["deform"], weight="700")
    cv.text_px(PW / 2, PH - 58, "藍＝變形，灰虛線＝原位置", 12.5, C["muted"])
    lock = {0: "C 不轉、頂部不側移", 1: "B 不轉、頂部不側移", 2: "B、C 都不轉"}[j]
    cv.text_px(PW / 2, PH - 36, "鎖住：" + lock, 12.5, C["muted"])
    return cv

AMB = C["accent"]          # 剪力：琥珀
GRN = C["bmd"]             # 彎矩：綠
RED = C["load"]            # 節點外力：紅
NODE = ("B", "C", "Δ")

def num(v):
    return ("−" if v < 0 else "") + str(abs(v))

def terms(vals):
    nz = [v for v in vals if v]
    return " + ".join(num(v) if v > 0 else f"({num(v)})" for v in nz) if nz else "0"

def panel_fbd(f, j, D):
    cv = Canvas(PW, PH, sx=SX, ox=OX, oy=OY + 22)
    cv.panel("② 構件自由體圖（桿端力）", "")
    cv.text_px(PW / 2, 56, "綠＝彎矩、琥珀＝剪力，皆為作用在桿件上的力", 12.5, C["muted"])
    top, by, bx0, bx1 = 0.74, 1.0, 0.15, 0.85
    cd = j == 2
    activeAB = any(f[k] for k in ("M_BA", "M_AB"))
    activeDC = any(f[k] for k in ("M_CD", "M_DC"))
    activeBC = any(f[k] for k in ("M_BC", "M_CB"))
    for x, act in ((0, activeAB), (1, activeDC)):
        cv.line((x, 0), (x, top), C["member"] if act else C["ghost"], MW, cap="butt", dash=None if act else "6 5")
    cv.line((bx0, by), (bx1, by), C["member"] if activeBC else C["ghost"], MW, cap="butt", dash=None if activeBC else "6 5")
    mlab = lambda v: fmt(v, 0, cd, signed=False)
    hlab = lambda v: fmt(v, 1, cd, signed=False)
    for x, out, side, kt, kb, ht, hb in ((0, 0, -1, "M_BA", "M_AB", "H_B", "H_A"), (1, 180, 1, "M_CD", "M_DC", "H_C", "H_D")):
        mom(cv, (x, top), f[kt], mlab(f[kt]), out, GRN, lab_out=35 if out == 0 else 215, lr=44)
        mom(cv, (x, 0), f[kb], mlab(f[kb]), out, GRN, lab_out=-35 if out == 0 else 145, lr=44)
        for y, k in ((top, ht), (0.0, hb)):
            v = f[k]
            if v: harrow(cv, (x, y), v, hlab(v), AMB, lab_dy=0, length=0.30, push=(v * side < 0))
    if activeBC:
        mom(cv, (bx0, by), f["M_BC"], mlab(f["M_BC"]), 90, GRN, lr=40)
        mom(cv, (bx1, by), f["M_CB"], mlab(f["M_CB"]), 90, GRN, lr=40)
        for x, k in ((bx0, "V_B"), (bx1, "V_C")):       # 梁端垂直剪力：畫在梁下方，拉離梁
            v = f[k]
            cv.arrow((x, by - 0.02), (x, by - 0.02 + (0.16 if v > 0 else -0.16)), AMB, 2.2, 8, dash="4 3")
    for x, act in ((0, activeAB), (1, activeDC)):
        if not act:
            for i, ch in enumerate("無變形"):
                cv.text((x, 0.40 - 0.08 * i), ch, 12.5, C["muted"], dx=-16 if x == 0 else 16)
    if not activeBC:
        cv.text((0.5, by + 0.13), "梁 BC 無變形 → 無桿端力", 12.5, C["muted"])
    # 力偶平衡驗算
    chk = []
    if activeAB: chk.append(("柱 AB", f["M_BA"], f["M_AB"], f["H_B"]))
    if activeDC: chk.append(("柱 DC", f["M_CD"], f["M_DC"], f["H_C"]))
    if activeBC: chk.append(("梁 BC", f["M_BC"], f["M_CB"], None))
    y = PH - 96
    cv.text_px(PW / 2, y - 26, "力偶驗算（該桿 ΣM = 0）", 12.5, C["muted"])
    for nm, m1, m2, H in chk:
        mu = "EI/L^{3}" if cd else "EI/L^{2}"
        cv.text_px(80, y, nm, 12.5, C["text"], "end", weight="700")
        if H is None:
            cv.math_px(88, y, f"V_{{C}} = +[{terms([m1, m2])}]{mu} = {m1 + m2}{mu} ✓", 13, AMB, "start")
            cv.text_px(PW - 14, y + 18, "（梁端剪力由柱軸力承擔，不進 K）", 11.5, C["muted"], "end")
        else:
            cv.math_px(88, y, f"H_{{頂}} = −[{terms([m1, m2])}]{mu} = {num(H)}{mu} ✓".replace("H_{頂}", "H_{top}"), 13, AMB, "start")
        y += 24
    return cv

def panel_joint(f, j, D):
    cv = Canvas(PW, PH, sx=SX, ox=OX, oy=OY - 70)
    k1, k2, k3 = K_column(f)
    cd = j == 2
    cv.panel("③ 節點平衡（作用力 ↔ 反作用力）", "")
    cv.text_px(PW / 2, 56, "細線＝桿件給節點的反作用（與②反向）；紅＝外力", 12.5, C["muted"])
    # 節點與桿件殘段
    for x in (0, 1):
        cv.line((x, 1), (x, 0.66), C["ghost"], 3.0, dash="6 5", cap="butt")
    cv.line((0, 1), (1, 1), C["ghost"], 3.0, dash="6 5", cap="butt")
    for x in (0, 1): cv.dot((x, 1), 6, fill=C["member"])
    cv.text((0, 1), "B", 14, C["text"], weight="700", dx=-14, dy=16)
    cv.text((1, 1), "C", 14, C["text"], weight="700", dx=14, dy=16)
    # 反作用彎矩（合計）＝ −(桿端彎矩和)，畫在節點下方內側
    rB, rC = -k1, -k2
    mom(cv, (0, 1), rB, fmt(abs(rB), 0, cd, False), 315, GRN, r=18, lr=40, span=150)
    mom(cv, (1, 1), rC, fmt(abs(rC), 0, cd, False), 225, GRN, r=18, lr=40, span=150)
    # 反作用水平力（柱給節點）＝ −H，畫在柱殘段上
    for x, H, side in ((0, f["H_B"], -1), (1, f["H_C"], 1)):
        R = -H
        if R: harrow(cv, (x, 0.80), R, fmt(abs(R), 1, cd, False), AMB, lab_dy=0, length=0.28, push=(R * side < 0))
    # 外力
    mom(cv, (0, 1), k1, fmt(abs(k1), 0, cd, False), 90, RED, r=26, lr=44, span=160)
    mom(cv, (1, 1), k2, fmt(abs(k2), 0, cd, False), 90, RED, r=26, lr=44, span=160)
    hx = 0 if k3 < 0 else 1
    harrow(cv, (hx, 1), k3, fmt(abs(k3), 1, cd, False), RED, lab_dy=-16, length=0.36, push=False,
           lab_x=hx + (-0.36 if k3 < 0 else 0.36), anchor="end" if k3 < 0 else "start")
    # 平衡式
    mu = "EI/L^{2}" if cd else "EI/L"
    fu = "EI/L^{3}" if cd else "EI/L^{2}"
    rows = [("B 點 ΣM = 0", f"K_{{1{j+1}}} = {terms([f['M_BA'], f['M_BC']])} = {fmt(k1, 0, cd)}"),
            ("C 點 ΣM = 0", f"K_{{2{j+1}}} = {terms([f['M_CD'], f['M_CB']])} = {fmt(k2, 0, cd)}"),
            ("頂部 ΣFx = 0", f"K_{{3{j+1}}} = {terms([f['H_B'], f['H_C']])} = {fmt(k3, 1, cd)}")]
    y = PH - 100
    for lab, eq in rows:
        cv.text_px(104, y, lab, 12.5, C["text"], "end", weight="700")
        cv.math_px(112, y, eq, 13.5, RED, "start", weight="700")
        y += 26
    cv.text_px(PW / 2, y + 2, "外力 ＝ 桿端力之和（兩者同向），故不必再翻號", 11.5, C["muted"])
    return cv

def panel_vec(cols, j):
    cv = Canvas(PW, PH, sx=SX, ox=OX, oy=OY)
    cd = j == 2
    col = cols[j]
    cv.panel(f"④ [K] 第 {j + 1} 直行", "")
    cv.text_px(PW / 2, 56, "三個節點外力由上往下排", 12.5, C["muted"])
    # 大括號向量
    cx, cy0, dy = PW / 2 + 30, 150, 52
    ents = [fmt(col[i], i == 2, cd) for i in range(3)]
    for i, e in enumerate(ents):
        cv.math_px(cx, cy0 + i * dy, e, 19, RED, weight="700")
    bx0, bx1, by0, by1 = cx - 72, cx + 72, cy0 - 30, cy0 + 2 * dy + 26
    for x, s_ in ((bx0, 1), (bx1, -1)):
        pts = [(x + s_ * 10, by0), (x, by0 + 8), (x, (by0 + by1) / 2 - 8), (x - s_ * 8, (by0 + by1) / 2),
               (x, (by0 + by1) / 2 + 8), (x, by1 - 8), (x + s_ * 10, by1)]
        cv.parts.append('<polyline points="' + " ".join(f"{a:.1f},{b:.1f}" for a, b in pts) +
                        f'" fill="none" stroke="{RED}" stroke-width="2.4" stroke-linejoin="round"/>')
    for i in range(3):
        cv.math_px(bx0 - 16, cy0 + i * dy, f"K_{{{i+1}{j+1}}}", 15, C["muted"], "end")
        cv.math_px(bx1 + 14, cy0 + i * dy, ["θ_{B}", "θ_{C}", "Δ"][i], 14, C["deform"], "start")
    # 驗算
    y = by1 + 44
    cv.text_px(24, y, "驗算", 13.5, C["text"], "start", weight="700")
    y += 28
    cv.text_px(24, y, "① 主對角恆正：", 12.5, C["text"], "start")
    cv.math_px(128, y, f"K_{{{j+1}{j+1}}} = {fmt(col[j], j == 2, cd)} > 0 ✓", 13.5, GRN, "start", weight="700")
    y += 24
    cv.text_px(24, y, "② 互易對稱（與其他直行比對）：", 12.5, C["text"], "start")
    for i in range(3):
        if i == j: continue
        y += 24
        other = cols[i][j]
        ok = "✓" if other == col[i] else "✗"
        cv.math_px(44, y, f"K_{{{i+1}{j+1}}} = K_{{{j+1}{i+1}}} = {fmt(col[i], i == 2, cd)} {ok}", 13.5, GRN, "start", weight="700")
        cv.text_px(PW - 16, y, f"（圖 3{'abc'[i]}）", 12, C["muted"], "end")
    return cv

def fig(j, cols):
    tB, tC, D, name = STATES[j]
    f = member_end_forces(tB, tC, D)
    path = f"{OUT}/{TAG}-fig-3{'abc'[j]}-unit-{['thetaB', 'thetaC', 'delta'][j]}.svg"
    plain = name.replace("_{", "").replace("}", "")
    compose([panel_deform(tB, tC, D, name, j), panel_fbd(f, j, D), panel_joint(f, j, D), panel_vec(cols, j)],
            title=f"圖 3{'abc'[j]}　圖解法求 [K] 第 {j + 1} 直行：令 {plain}，其餘鎖住",
            sub="符號約定：轉角與彎矩順時針為正，Δ 與水平力向右為正（與傾角變位法一致）",
            path=path)
    return path

if __name__ == "__main__":
    cols = [K_column(member_end_forces(*STATES[j][:3])) for j in range(3)]
    for i in range(3):
        for j in range(3):
            assert cols[j][i] == cols[i][j], ("不對稱", i, j)
        assert cols[i][i] > 0
    for j in range(3):
        print(fig(j, cols), cols[j])
    print("K 係數（EI、L 次方略）=", [[cols[j][i] for j in range(3)] for i in range(3)], "對稱、主對角正 OK")

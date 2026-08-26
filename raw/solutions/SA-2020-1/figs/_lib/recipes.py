"""
recipes.py — 常見解題圖型的高階產生器
======================================
每個 recipe 都吃「解題已經算出來的數字」，不吃形容詞。
若某個 recipe 不合用，直接用 structdraw.py 的 primitives 組，不要硬套。

  plot_function   任意函數沿構材的填色圖（SFD/BMD/撓度通用）
  beam_vm         梁載重圖 + 剪力圖 + 彎矩圖（三聯）
  mohr2           二維莫爾圓（含 X/Y 點與主應力）
  mohr3           三向應力之三圓莫爾圖
  rc_flexure      RC 斷面／應變／應力三聯圖（Whitney 等值應力塊）
  pm_interaction  P-M 交互曲線（標示純壓、平衡點、純彎）
  truss_forces    桁架力流圖（受拉紅／受壓藍，線寬隨軸力大小）
  bar_compare     量級比較長條圖（如勁度光譜、載重折減比較）
"""
import math
from structdraw import Canvas, C, FONT, FONT_M, compose, esc


# ══════════════════════════════════════════════════════════
def plot_function(cv, xs, ys, scale, base_y=0.0, x0=0.0, color=C["bmd"],
                  fill=C["fill_m"], w=2.2, marks=None, zero_line=True):
    """沿水平方向畫填色函數圖。
    xs, ys : 等長串列（ys 為實際數值，非像素）
    scale  : 每 1 單位數值對應的模型長度
    marks  : [(x, text, dy_px)] 於指定 x 標數值
    """
    pts = [(x0 + x, base_y + y*scale) for x, y in zip(xs, ys)]
    poly = [(x0 + xs[0], base_y)] + pts + [(x0 + xs[-1], base_y)]
    cv.polygon(poly, fill, color, w)
    if zero_line:
        cv.line((x0 + xs[0], base_y), (x0 + xs[-1], base_y), C["muted"], 1.6)
    for x, t, dy in (marks or []):
        i = min(range(len(xs)), key=lambda k: abs(xs[k] - x))
        cv.math_px(cv.X(x0 + x), cv.Y(base_y + ys[i]*scale) + dy, t, 13, color, weight="700")


def beam_vm(span, xs, V, M, supports=(), point_loads=(), udls=(),
            title=None, note=None, path=None, W=760, PH=210,
            v_unit="", m_unit="", key_V=(), key_M=()):
    """梁的三聯圖：載重圖 / 剪力圖 / 彎矩圖。

    span         : 跨度（模型單位）
    xs, V, M     : 等長串列，由解題計算結果提供
    supports     : [(x, 'pin'|'roller'|'fixed')]
    point_loads  : [(x, 'P')]  向下集中載重
    udls         : [(x0, x1, 'w')]
    key_V/key_M  : [(x, '標註文字', dy_px)]
    """
    sx = (W - 200) / span
    pad = 100

    top = Canvas(W, PH, sx=sx, ox=pad, oy=PH*0.30)
    top.panel("載重與支承", None)
    top.line((0, 0), (span, 0), C["member"], 6, cap="butt")
    for x, kind in supports:
        top.support((x, 0), kind)
    for x0_, x1_, lab in udls:
        top.udl((x0_, 0), (x1_, 0), 0.10*span, n=9, label=lab)
    for x, lab in point_loads:
        top.arrow((x, 0.13*span), (x, 0), C["load"], 3.2, 11)
        top.math_px(top.X(x), top.Y(0.13*span) - 15, lab, 15, C["load"], weight="700")
    top.dim((0, 0), (span, 0), "L", off=54, label_off=15)

    def strip(vals, color, fill, name, unit, keys):
        """依 vals 的正負範圍自動配置基線位置與比例，保證不撞標題。"""
        top_px, bot_px = 72, 34
        vmax, vmin = max(max(vals), 0.0), min(min(vals), 0.0)
        rng = (vmax - vmin) or 1.0
        px_per = (PH - top_px - bot_px) / rng
        base_from_top = top_px + vmax*px_per
        cv = Canvas(W, PH, sx=sx, ox=pad, oy=PH - base_from_top)
        cv.panel(name, None)
        plot_function(cv, xs, vals, px_per/sx, 0.0, 0.0, color, fill, marks=keys)
        cv.text_px(pad - 14, cv.Y(0), "0", 12, C["muted"], "end")
        if unit:
            cv.text_px(W - 22, 32, unit, 12, C["muted"], "end")
        return cv

    mid = strip(V, C["sfd"], C["fill_s"], "剪力圖 SFD", v_unit, key_V)
    bot = strip(M, C["bmd"], C["fill_m"], "彎矩圖 BMD", m_unit, key_M)
    return compose([top, mid, bot], title=title, note=note, cols=1, path=path)


# ══════════════════════════════════════════════════════════
def _circle_path(cx, cy, r):
    return (f"M {cx-r:.2f} {cy:.2f} a {r:.2f} {r:.2f} 0 1 0 {2*r:.2f} 0 "
            f"a {r:.2f} {r:.2f} 0 1 0 {-2*r:.2f} 0 Z")


def mohr3(s1, s2, s3, unit="MPa", title=None, note=None, path=None, W=760, H=560,
          names=("σ_{1}", "σ_{2}", "σ_{3}")):
    """三向應力之三圓莫爾圖。輸入三個主應力（含正負號，順序不拘）。
    所有可能之應力狀態落在大圓內、兩小圓外（淡灰區）。"""
    s1, s2, s3 = sorted([s1, s2, s3], reverse=True)
    R = (s1 - s3) / 2 or 1.0
    L, GUT, TOP, BOT = 64, 190, 74, 58      # 左margin / 右側標註槽 / 上 / 下
    lo, hi = min(s3, 0.0), max(s1, 0.0)
    pad = (hi - lo) * 0.14 or 1.0
    xr = (hi + pad) - (lo - pad)
    sc = min((W - L - GUT) / xr, (H - TOP - BOT) / (2 * R * 1.16))
    cv = Canvas(W, H, sx=sc, ox=L - (lo - pad) * sc, oy=H - TOP - R * 1.16 * sc, bg="#FFFFFF")

    big = ((s1 + s3) / 2, R); m12 = ((s1 + s2) / 2, (s1 - s2) / 2); m23 = ((s2 + s3) / 2, (s2 - s3) / 2)
    d = " ".join(_circle_path(cv.X(c), cv.Y(0), rr * sc) for c, rr in (big, m12, m23))
    cv.parts.append(f'<path d="{d}" fill="#DFE5EC" fill-rule="evenodd" opacity="0.8"/>')
    for c, rr in (big, m12, m23):
        cv.circle((c, 0), rr, "none", C["member"], 2.4)

    cv.arrow((lo - pad, 0), (hi + pad, 0), C["muted"], 1.8, 9)
    cv.arrow((0, -R * 1.14), (0, R * 1.22), C["muted"], 1.8, 9)
    cv.math((hi + pad, 0), "σ", 16, C["muted"], "start", dx=8, dy=14)
    cv.math((0, R * 1.22), "τ", 16, C["muted"], "end", dx=-10)

    order = sorted([(s3, names[2]), (s2, names[1]), (s1, names[0])])
    last_x, tier = -1e9, 0
    for v, nm in order:
        cv.dot((v, 0), 4.6, fill=C["member"])
        tier = tier + 1 if cv.X(v) - last_x < 78 else 0
        last_x = cv.X(v)
        nudge = 22 if abs(cv.X(v) - cv.X(0)) > 22 else 40
        cv.math_px(cv.X(v), cv.Y(0) + nudge + tier * 19, f"{nm}={v:g}", 13.5, C["text"], weight="700")

    gx = W - GUT + 14
    for t, c, nm in (((s1-s3)/2, big[0], "τ_{13}"), ((s1-s2)/2, m12[0], "τ_{12}"),
                     ((s2-s3)/2, m23[0], "τ_{23}")):
        cv.dot((c, t), 4.4, fill=C["load"])
        cv.parts.append(f'<line x1="{cv.X(c):.2f}" y1="{cv.Y(t):.2f}" x2="{gx-8:.2f}" '
                        f'y2="{cv.Y(t):.2f}" stroke="{C["load"]}" stroke-width="1.2" stroke-dasharray="4 3"/>')
        cv.math_px(gx, cv.Y(t), f"{nm} = {t:g} {unit}", 13, C["load"], "start", weight="700")

    cv.text_px(W/2, 32, title or "三向應力莫爾圓", 16.5, C["text"], weight="700")
    cv.text_px(W/2, H - 22, note or
               f"絕對最大剪應力 = 大圓半徑 = (σ_{{1}}−σ_{{3}})/2 = {R:g} {unit}", 13, C["muted"])
    if path: cv.save(path)
    return cv


def mohr2(sx_, sy_, txy, unit="MPa", title=None, path=None, W=680, H=560):
    """二維莫爾圓。標出 X(σx,τxy)、Y(σy,−τxy)、主應力與 2θp。"""
    cen = (sx_ + sy_) / 2
    R = math.hypot((sx_ - sy_) / 2, txy) or 1.0
    s1, s2 = cen + R, cen - R
    L, RG, TOP, BOT = 74, 120, 74, 58
    lo, hi = min(s2, 0.0), max(s1, 0.0)
    pad = (hi - lo) * 0.14 or 1.0
    sc = min((W - L - RG) / ((hi + pad) - (lo - pad)), (H - TOP - BOT) / (2 * R * 1.30))
    cv = Canvas(W, H, sx=sc, ox=L - (lo - pad)*sc, oy=H - TOP - R*1.30*sc, bg="#FFFFFF")

    cv.circle((cen, 0), R, C["fill_c"], C["member"], 2.6)
    cv.arrow((lo - pad, 0), (hi + pad, 0), C["muted"], 1.8, 9)
    cv.arrow((0, -R*1.24), (0, R*1.28), C["muted"], 1.8, 9)
    cv.math((hi + pad, 0), "σ", 16, C["muted"], "start", dx=8, dy=14)
    cv.math((0, R*1.28), "τ", 16, C["muted"], "end", dx=-10)

    X, Y = (sx_, txy), (sy_, -txy)
    cv.line(X, Y, C["load"], 2.0, dash="5 4")
    for p, nm in ((X, "X"), (Y, "Y")):
        cv.dot(p, 5.0, fill=C["load"])
        cv.text_px(cv.X(p[0]) + 12, cv.Y(p[1]) - 12, nm, 14, C["load"], "start", weight="700")
    for v, nm in ((s1, "σ_{1}"), (s2, "σ_{2}")):
        cv.dot((v, 0), 4.8, fill=C["member"])
        cv.math_px(cv.X(v), cv.Y(0) + 24, f"{nm}={v:.4g}", 13.5, C["text"], weight="700")
    cv.dot((cen, R), 4.6, fill=C["accent"])
    cv.math_px(cv.X(cen) + 10, cv.Y(R) - 14, f"τ_{{max}}={R:.4g}", 13.5, C["accent"],
               "start", weight="700")

    thp = math.degrees(math.atan2(txy, (sx_ - sy_)/2))
    cv.moment_arrow((cen, 0), r=R*sc*0.34, ccw=thp > 0, color=C["accent"], w=2.2,
                    span=abs(thp), start=0)
    cv.math_px(cv.X(cen) + R*sc*0.40, cv.Y(0) - 14, f"2θ_{{p}}={thp:.1f}°", 12.5,
               C["accent"], "start", weight="700")

    cv.text_px(W/2, 32, title or "二維莫爾圓", 16.5, C["text"], weight="700")
    cv.text_px(W/2, H - 22,
               f"圓心 = (σ_{{x}}+σ_{{y}})/2 = {cen:.4g}　半徑 R = {R:.4g} {unit}",
               13, C["muted"])
    if path: cv.save(path)
    return cv


# ══════════════════════════════════════════════════════════
def rc_flexure(b, h, d, c, a, labels=None, title=None, note=None, path=None,
               PW=330, PH=420, bars=3):
    """RC 撓曲三聯圖：斷面／應變／等值應力塊。

    b, h, d : 斷面寬、全深、有效深（同單位，例如 mm）
    c       : 中性軸深度（解題算出）
    a       : Whitney 等值應力塊深度 a = β₁c（解題算出）

    應變與應力圖的水平尺度為示意（比例只反映相對大小），
    垂直尺度則與斷面同一比例，故 c、a、d 的相對位置是真的。
    """
    lb = {"eps_cu": "ε_{cu}=0.003", "eps_s": "ε_{s}", "fc": "0.85f'_{c}",
          "Cc": "C_{c}", "T": "T=A_{s}f_{y}", "c": "c", "a": "a", "b": "b", "h": "h", "d": "d"}
    lb.update(labels or {})
    sc = (PH - 165) / h                    # 垂直比例（三格共用）
    M = 96 / sc                            # 圖形最大水平寬（96 px 換算成模型單位）

    # ---- 斷面 ----
    p1 = Canvas(PW, PH, sx=sc, ox=PW/2 - b*sc/2, oy=76)
    p1.panel("斷面", f"b × h = {b:g} × {h:g}")
    p1.polygon([(0, 0), (b, 0), (b, h), (0, h)], "#EDF1F6", C["member"], 2.6)
    for i in range(bars):
        xb = b*(0.20 + 0.60*i/(bars-1)) if bars > 1 else b/2
        p1.dot((xb, h - d), 5.6, fill=C["member"], stroke="#FFFFFF", w=1.4)
    p1.dim((0, 0), (b, 0), lb["b"], off=44, label_off=15)
    p1.dim((b, 0), (b, h), lb["h"], off=44, label_off=13)
    p1.dim((0, h), (0, h - d), lb["d"], off=42, label_off=13)

    # ---- 應變 ----
    p2 = Canvas(PW, PH, sx=sc, ox=PW*0.52, oy=76)
    p2.panel("應變分佈", "平面保持平面 → 線性")
    wc = M if c >= (d - c) else M*c/(d - c)          # 壓應變寬
    wt = M if (d - c) >= c else M*(d - c)/c          # 拉應變寬
    p2.line((0, 0), (0, h), C["ghost"], 2, dash="5 4")
    p2.polygon([(0, h), (wc, h), (0, h - c)], C["fill_c"], C["compr"], 2.4)
    p2.polygon([(0, h - c), (-wt, h - d), (0, h - d)], C["fill_t"], C["tension"], 2.4)
    p2.line((-M*1.15, h - c), (M*1.15, h - c), C["accent"], 1.8, dash="6 4")
    p2.math_px(p2.X(wc) + 7, p2.Y(h) + 10, lb["eps_cu"], 12.5, C["compr"], "start", weight="700")
    p2.math_px(p2.X(-wt) - 7, p2.Y(h - d), lb["eps_s"], 13, C["tension"], "end", weight="700")
    p2.text_px(p2.X(M*1.15) + 5, p2.Y(h - c), "N.A.", 12, C["accent"], "start", weight="700")
    p2.dim((0, h), (0, h - c), lb["c"], off=34, label_off=12)

    # ---- 應力 ----
    p3 = Canvas(PW, PH, sx=sc, ox=PW*0.46, oy=76)
    p3.panel("等值應力塊", "Whitney block")
    p3.line((0, 0), (0, h), C["ghost"], 2, dash="5 4")
    p3.polygon([(0, h), (M, h), (M, h - a), (0, h - a)], C["fill_c"], C["compr"], 2.4)
    p3.math_px(p3.X(M) + 7, p3.Y(h) + 10, lb["fc"], 12.5, C["compr"], "start", weight="700")
    p3.arrow((M*0.45, h - a/2), (M*1.35, h - a/2), C["compr"], 3.0, 10)
    p3.arrow((0.0, h - d), (-M*0.80, h - d), C["tension"], 3.0, 10)
    p3.math_px(p3.X(-M*0.40), p3.Y(h - d) - 15, lb["T"], 13, C["tension"], weight="700")
    p3.math_px(p3.X(M*0.85), p3.Y(h - a/2) + 17, lb["Cc"], 13.5, C["compr"], weight="700")
    p3.dim((0, h), (0, h - a), lb["a"], off=30, label_off=11)
    p3.dim((-M*1.02, h - a/2), (-M*1.02, h - d), "jd", off=0, label_off=-15, color=C["accent"])

    return compose([p1, p2, p3], title=title or "RC 梁撓曲：斷面／應變／應力",
                   note=note or "Cc = T 為力平衡條件；c 與 a 由此解出，不是量出來的",
                   path=path)


# ══════════════════════════════════════════════════════════
def pm_interaction(M, P, marks=(), title=None, note=None, path=None,
                   W=640, H=560, m_unit="kN·m", p_unit="kN"):
    """P-M 交互曲線。M,P 為等長串列（由解題計算），marks 為 [(M,P,'標籤')]。"""
    mmax, pmax, pmin = max(M), max(P), min(min(P), 0)
    sx = (W - 200) / (mmax * 1.18)
    sy_scale = (H - 190) / ((pmax - pmin) * 1.10)
    k = sy_scale / sx                        # P 軸相對縮放
    cv = Canvas(W, H, sx=sx, ox=110, oy=90 + (-pmin)*sy_scale, bg="#FFFFFF")

    cv.arrow((0, pmin*k*1.12), (0, pmax*k*1.12), C["muted"], 1.8, 9)
    cv.arrow((0, 0), (mmax*1.18, 0), C["muted"], 1.8, 9)
    cv.math((0, pmax*k*1.12), f"P", 15, C["muted"], "end", dx=-10)
    cv.math((mmax*1.18, 0), f"M", 15, C["muted"], "start", dx=8, dy=14)

    pts = [(m, p*k) for m, p in zip(M, P)]
    cv.polygon([(0, pts[0][1])] + pts + [(0, pts[-1][1])], C["fill_c"], C["compr"], 2.8)
    cv.text_px(cv.X(mmax*0.34), cv.Y(pmax*k*0.42), "安全區", 14, C["compr"], weight="700")

    for m, p, lab in marks:
        cv.dot((m, p*k), 5.4, fill=C["accent"], stroke="#FFFFFF", w=1.8)
        cv.text_px(cv.X(m) + 12, cv.Y(p*k) - 4, lab, 12.5, C["accent"], "start", weight="700")
        cv.line((0, p*k), (m, p*k), C["accent"], 1.1, dash="4 3")

    cv.text_px(W/2, 32, title or "P-M 交互曲線", 16.5, C["text"], weight="700")
    cv.text_px(W/2, 56, f"P（{p_unit}）－ M（{m_unit}）", 12.5, C["muted"])
    cv.text_px(W/2, H - 22, note or
               "曲線上方為壓力控制、下方為拉力控制；平衡點為兩者分界", 13, C["muted"])
    if path: cv.save(path)
    return cv


# ══════════════════════════════════════════════════════════
def truss_forces(nodes, members, supports=(), loads=(), title=None, note=None,
                 path=None, W=740, H=520, margin=110, fmt="{:+.3g}"):
    """桁架力流圖。受拉紅、受壓藍、零桿灰虛線；線寬隨 |N| 變化。

    nodes   : {'A': (x, y), ...}
    members : [('A','B', N), ...]   N > 0 受拉、N < 0 受壓
    supports: [('B', 'pin'|'roller'|'fixed', 角度)]
    loads   : [('A', (dx, dy), 'P')]  dx,dy 為箭頭方向（模型單位）
    """
    # 邊界須涵蓋載重箭頭尾端，否則箭頭會被畫到畫布外
    pts = list(nodes.values()) + [(nodes[n][0]-dx, nodes[n][1]-dy) for n, (dx, dy), _ in loads]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    spanx, spany = (max(xs)-min(xs)) or 1, (max(ys)-min(ys)) or 1
    sc = min((W-2*margin)/spanx, (H-2*margin-40)/spany)
    cv = Canvas(W, H, sx=sc, ox=margin - min(xs)*sc, oy=margin - min(ys)*sc, bg="#FFFFFF")

    peak = max((abs(n) for *_, n in members), default=1) or 1
    for n1, n2, N in members:
        p0, p1 = nodes[n1], nodes[n2]
        if abs(N) < 1e-9:
            cv.line(p0, p1, C["muted"], 2.4, dash="7 5")
        else:
            col = C["tension"] if N > 0 else C["compr"]
            cv.line(p0, p1, col, 3.2 + 4.4*abs(N)/peak, cap="butt")
        mx, my = (p0[0]+p1[0])/2, (p0[1]+p1[1])/2
        dx, dy = p1[0]-p0[0], p1[1]-p0[1]
        L = math.hypot(dx, dy) or 1
        off = 17
        col = C["muted"] if abs(N) < 1e-9 else (C["tension"] if N > 0 else C["compr"])
        cv.math_px(cv.X(mx) - dy/L*off, cv.Y(my) - dx/L*off, fmt.format(N).replace("-", "\u2212"), 13, col, weight="700")

    for name, kind, *rest in supports:
        cv.support(nodes[name], kind, rest[0] if rest else 0)
    for name, (dx, dy), lab in loads:
        p = nodes[name]
        cv.arrow((p[0]-dx, p[1]-dy), p, C["load"], 3.4, 12)
        cv.math_px(cv.X(p[0]-dx), cv.Y(p[1]-dy) - 14, lab, 16, C["load"], weight="700")
    for name, p in nodes.items():
        cv.dot(p, 5.4)
        cv.text_px(cv.X(p[0]) - 16, cv.Y(p[1]) + 16, name, 15, C["text"], weight="700")

    cv.legend(24, 64,
              [(C["tension"], "受拉 (+)"), (C["compr"], "受壓 (−)"), (C["muted"], "零桿")])
    if title: cv.text_px(W/2, 32, title, 16.5, C["text"], weight="700")
    if note:  cv.text_px(W/2, H - 20, note, 13, C["muted"])
    if path: cv.save(path)
    return cv


# ══════════════════════════════════════════════════════════
def bar_compare(cases, title=None, sub=None, note=None, path=None, W=1020, row_h=86,
                sketch=None):
    """量級比較長條圖。用於「答案應落在什麼區間」的合理性檢核。

    cases : [(名稱, 說明, 數值, 標示式, 顏色)]（數值最大者為 100%）
    sketch: f(Canvas_mini, case_index) → 於左側畫迷你示意圖（可為 None）
    """
    H = 118 + row_h*len(cases) + 60
    cv = Canvas(W, H, sx=1, bg="#FFFFFF")
    if title: cv.text_px(W/2, 32, title, 17.5, C["text"], weight="700")
    if sub:   cv.text_px(W/2, 57, sub, 13, C["muted"])
    peak = max(c[2] for c in cases) or 1
    x0, bw = 320, 400
    for i, (name, desc, val, expr, col) in enumerate(cases):
        y = 122 + i*row_h
        if sketch:
            mini = Canvas(120, 74, sx=44, ox=32, oy=14)
            sketch(mini, i)
            cv.parts.append(f'<g transform="translate(20,{y-38})">{"".join(mini.parts)}</g>')
        cv.text_px(150, y-9, name, 14, C["text"], "start", weight="700")
        cv.text_px(150, y+14, desc, 12.5, C["muted"], "start")
        cv.rect_px(x0, y-17, bw, 34, "#EDF1F6", 8)
        cv.rect_px(x0, y-17, bw*val/peak, 34, col, 8)
        cv.text_px(x0 + bw*val/peak - 14, y, f"{100*val/peak:.0f}%", 14, "#FFFFFF", "end", weight="700")
        cv.math_px(x0 + bw + 16, y, expr, 14.5, col, "start", weight="700")
    if note: cv.text_px(W/2, H - 26, note, 13.5, C["muted"])
    if path: cv.save(path)
    return cv

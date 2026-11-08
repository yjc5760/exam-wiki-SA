"""beamfig — 梁（水平桿件串）的變形＋彎矩條圖（exam-wiki-SA，2026-11-08，struct-diagram 階段 E）
數值全部來自 frame2d.Frame 的解；節點兩側彎矩不同時（剛架梁在柱節點跳躍）左右分開標示並註明受拉側。
正彎矩＝下緣受拉，畫在受拉側（正值畫在梁下方）。"""
from structdraw import Canvas, C, compose, FONT, esc
import frameviz
from frameviz import member_moment, deformed, unit, draw_members, draw_supports, fit


def inflections(f, m, n=400):
    """反曲點（彎矩變號處）。frameviz.inflections 在彎矩恰好落在取樣點為 0 時會漏掉（如反對稱梁的跨中），此處補上。"""
    vals = [member_moment(f, m, k / n) for k in range(n + 1)]
    tol = 1e-9 * (max(abs(v) for v in vals) or 1)
    out = []
    for k in range(n):
        a, b = vals[k], vals[k + 1]
        if abs(a) <= tol and 0 < k and vals[k - 1] * b < 0:
            out.append(k / n)
        elif abs(a) > tol and abs(b) > tol and a * b < 0:
            out.append((k + a / (a - b)) / n)
    return [x for x in out if 0.02 < x < 0.98]


frameviz.inflections = inflections          # solution_figure 也用修正版


def _x_of(f, m, xi):
    (x0, y0), (x1, y1) = f.N[m["i"]], f.N[m["j"]]
    return x0 + (x1 - x0) * xi


def beam_strip(f, names, path, title, W=900, H1=250, H2=300, mpx=78, dpx=58,
               supports=(), hinges=(), springs=(), dlabels=(), mlabels=(), sub_def="", sub_bmd="",
               note=None, unit_m="kN-m", show_def=True, xpad=(70, 70), extra=None, yc=0.50, prec=2):
    """names: 梁上桿件名稱（由左至右）。
    supports: [(節點, kind)]；hinges: [節點]；springs: [節點]（畫在變形圖下方）
    dlabels: [(節點, 文字, dy_px)] 變形圖位移標註；mlabels: [(桿件名, xi, 'L'/'R'/'C', 是否寫受拉側)]
    extra(cv_def, cv_bmd): 呼叫端自訂加註。"""
    ms = [m for m in f.M if m["name"] in names]
    ms.sort(key=lambda m: f.N[m["i"]][0])
    xs = [f.N[m["i"]][0] for m in ms] + [f.N[ms[-1]["j"]][0]]
    x0, x1 = min(xs), max(xs)
    sx = (W - xpad[0] - xpad[1]) / (x1 - x0)
    y0 = f.N[ms[0]["i"]][1]
    mmax = max(abs(member_moment(f, m, k / 80)) for m in ms for k in range(81)) or 1
    dmax = max(abs(f.d[n][1]) for m in ms for n in (m["i"], m["j"])) or 1
    for m in ms:
        for p in deformed(f, m, 1.0, 40):
            dmax = max(dmax, abs(p[1] - y0))
    panels = []
    if show_def:
        a = Canvas(W, H1, sx=sx, ox=xpad[0] - x0 * sx, oy=H1 * 0.52 - y0 * sx)
        a.panel("變形形狀（示意放大）", sub_def)
        ds = dpx / sx / dmax
        a.line((x0, y0), (x1, y0), C["ghost"], 2.6, dash="6 5")
        for m in ms:
            a.poly(deformed(f, m, ds), C["deform"], 5.0)
        for nd, kind in supports:
            p = f.N[nd]; dv = f.d[nd][1] * ds
            a.support((p[0], p[1] + dv), kind, 0 if kind != "fixed" else (90 if p[0] <= x0 + 1e-9 else -90), 15)
        for nd in springs:
            p = f.N[nd]; dv = f.d[nd][1] * ds; top = (p[0], p[1] + dv); bot = (p[0], y0 - 0.95 * dpx / sx * 1.05)
            n = 9; pts = [top]
            for k in range(1, n):
                t = k / n; pts.append((p[0] + (0.12 if k % 2 else -0.12) * 46 / sx * 0.5, top[1] + (bot[1] - top[1]) * t))
            pts.append(bot); a.poly(pts, C["muted"], 2.2)
            a.line((p[0] - 18 / sx, bot[1]), (p[0] + 18 / sx, bot[1]), C["muted"], 2.6)
        for nd in hinges:
            p = f.N[nd]; a.dot((p[0], p[1] + f.d[nd][1] * ds), 6, fill="#FFFFFF", stroke=C["deform"], w=2.4)
        for m in ms:
            for xi in inflections(f, m):
                pt = deformed(f, m, ds, 400)[round(xi * 400)]
                a.dot(pt, 5.4, fill="#FFFFFF", stroke=C["accent"], w=2.9)
        for nd, s, dy in dlabels:
            p = f.N[nd]
            a.text_px(a.X(p[0]), a.Y(p[1] + f.d[nd][1] * ds) + dy, s, 13.5, C["deform"], weight="700")
        a.text_px(W / 2, H1 - 14, "○ ＝ 反曲點（彎矩為零）", 12.5, C["accent"], weight="700")
        panels.append(a)
    b = Canvas(W, H2, sx=sx, ox=xpad[0] - x0 * sx, oy=H2 * yc - y0 * sx)
    b.panel("彎矩圖（畫在受拉側；正＝下緣受拉）", sub_bmd)
    msc = mpx / sx / mmax
    for m in ms:
        (px0, py0), (px1, py1) = f.N[m["i"]], f.N[m["j"]]
        pts = [(px0 + (px1 - px0) * k / 80, py0 - member_moment(f, m, k / 80) * msc) for k in range(81)]
        b.polygon([(px0, py0)] + pts + [(px1, py1)], C["fill_m"], C["bmd"], 2)
    b.line((x0, y0), (x1, y0), "#4A5568", 3.2, cap="butt")
    for nd, kind in supports:
        p = f.N[nd]; b.support(p, kind, 0 if kind != "fixed" else (90 if p[0] <= x0 + 1e-9 else -90), 13)
    for nd in hinges:
        b.dot(f.N[nd], 6, fill="#FFFFFF", stroke="#4A5568", w=2.4)
    for m in ms:
        for xi in inflections(f, m):
            b.dot((_x_of(f, m, xi), y0), 5, fill="#FFFFFF", stroke=C["accent"], w=2.6)
    for name, xi, side, tens in mlabels:
        m = next(mm for mm in ms if mm["name"] == name)
        M = member_moment(f, m, xi); x = _x_of(f, m, xi)
        s = ("+" if M > 1e-9 else ("−" if M < -1e-9 else "")) + f"{abs(M):.{prec}f}".rstrip("0").rstrip(".")
        if tens and abs(M) > 1e-9:
            s += "（下緣受拉）" if M > 0 else "（上緣受拉）"
        px = b.X(x) + {"L": -10, "R": 10, "C": 0}[side]
        py = b.Y(y0 - M * msc) + (18 if M > 0 else -16)
        anchor = {"L": "end", "R": "start", "C": "middle"}[side]
        b.text_px(px, py, s, 14, C["bmd"], anchor=anchor, weight="700")
    b.text_px(W - 14, H2 - 14, f"單位：{unit_m}", 12.5, C["muted"], anchor="end")
    if extra:
        extra(panels[0] if show_def else None, b)
    panels.append(b)
    vstack(panels, title=title, note=note, path=path)
    return path


def vstack(panels, title=None, note=None, path=None, bg="#FFFFFF"):
    """直向堆疊、各格高度可不同（structdraw.compose 要求等高，高的那格會被裁掉）。"""
    W = max(p.w for p in panels); top = 76 if title else 0; bot = 46 if note else 0
    H = top + sum(p.h for p in panels) + bot
    parts = [f'<rect width="{W}" height="{H}" fill="{bg}"/>']
    if title:
        parts.append(f'<text x="{W/2}" y="34" font-family="{FONT}" font-size="17.5" fill="{C["text"]}" '
                     f'text-anchor="middle" font-weight="700">{esc(title)}</text>')
    clips, y = [], top
    for i, p in enumerate(panels):
        cid = f"bfclip{i}"
        clips.append(f'<clipPath id="{cid}"><rect x="0" y="0" width="{p.w}" height="{p.h}"/></clipPath>')
        parts.append(f'<g transform="translate(0,{y})" clip-path="url(#{cid})">{"".join(p.parts)}</g>')
        y += p.h
    parts.insert(0, f'<defs>{"".join(clips)}</defs>')
    if note:
        parts.append(f'<text x="{W/2}" y="{H-22}" font-family="{FONT}" font-size="13.5" fill="{C["muted"]}" '
                     f'text-anchor="middle">{esc(note)}</text>')
    svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(parts)}</svg>'
    if path:
        import os
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        open(path, "w", encoding="utf-8").write(svg)
    return svg


def frame_figure(f, sp, path, title, sub_def, sub_bmd, labels, W=560, H=450, dfrac=0.12, mfrac=0.17,
                 margins=(70, 70, 95, 95), notes=("", ""), dlabels=(), skip=(), fmt="{:.2f}", extra=None):
    """剛架：左＝變形形狀、右＝彎矩圖（受拉側）。與 frameviz.solution_figure 相同畫法，
    但彎矩數值標註改由呼叫端指定位置：labels = [(桿件名, xi, dx_px, dy_px)]，數值由勁度法解算出；
    fmt 可為 str 或具 .format(v) 的物件。dlabels = [(節點, 文字, dx, dy)] 標在變形圖。skip：不畫的桿件（如彈簧）。"""
    ms = [m for m in f.M if m["name"] not in skip]
    span = max(max(abs(p[0] - q[0]), abs(p[1] - q[1])) for p in f.N.values() for q in f.N.values()) or 1
    dmax = 0.0                                       # 以整條變形曲線（含節點轉角與跨內撓度）取最大位移；無側移剛架節點平移≈0
    for m in ms:
        p0, p1 = f.N[m["i"]], f.N[m["j"]]
        for k, q in enumerate(deformed(f, m, 1.0, 40)):
            b0 = (p0[0] + (p1[0] - p0[0]) * k / 40, p0[1] + (p1[1] - p0[1]) * k / 40)
            dmax = max(dmax, abs(q[0] - b0[0]), abs(q[1] - b0[1]))
    dmax = dmax or 1
    mmax = max(abs(member_moment(f, m, k / 40)) for m in ms for k in range(41)) or 1
    ds, msc = dfrac * span / dmax, mfrac * span / mmax
    N = sp["nodes"]; members = [{"ij": (m["i"], m["j"])} for m in ms]
    pts = [f.N[n] for m in ms for n in (m["i"], m["j"])]
    for m in ms:
        pts += deformed(f, m, ds, 10)
        p0, p1 = f.N[m["i"]], f.N[m["j"]]; d, L = unit(p0, p1); n = (-d[1], d[0])
        for k in range(11):
            M = member_moment(f, m, k / 10); bpt = (p0[0] + d[0] * k / 10 * L, p0[1] + d[1] * k / 10 * L)
            pts.append((bpt[0] - n[0] * M * msc, bpt[1] - n[1] * M * msc))
    sx, ox, oy = fit(pts, W, H, *margins)
    sup2 = [s for s in sp["supports"] if len(s) == 2]; sup3 = [s for s in sp["supports"] if len(s) == 3]
    def _sup(cv):                                   # (節點, 種類, 角度)：牆上鉸支承等需指定方向
        draw_supports(cv, N, members, sup2, 15)
        for nd, kind, ang in sup3: cv.support(N[nd], kind, ang, 15 * 0.85)
    a = Canvas(W, H, sx=sx, ox=ox, oy=oy); a.panel("變形形狀（示意放大）", sub_def)
    draw_members(a, N, members, C["ghost"], False, dash="6 5")
    for m in ms: a.poly(deformed(f, m, ds), C["deform"], 5.0)
    _sup(a)
    for nd in sp.get("hinges", []):
        a.dot((N[nd][0] + f.d[nd][0] * ds, N[nd][1] + f.d[nd][1] * ds), 6, fill="#FFFFFF", stroke=C["deform"], w=2.4)
    for m in ms:
        for xi in inflections(f, m):
            a.dot(deformed(f, m, ds, 400)[round(xi * 400)], 5.4, fill="#FFFFFF", stroke=C["accent"], w=2.9)
    for nd, s, dx, dy in dlabels:
        p = (N[nd][0] + f.d[nd][0] * ds, N[nd][1] + f.d[nd][1] * ds)
        a.text_px(a.X(p[0]) + dx, a.Y(p[1]) + dy, s, 13, C["deform"], weight="700")
    if notes[0]: a.text_px(W / 2, H - 40, notes[0], 13, C["deform"], weight="700")
    a.text_px(W / 2, H - 16, "○ ＝ 反曲點（彎矩為零）", 12.5, C["accent"], weight="700")
    b = Canvas(W, H, sx=sx, ox=ox, oy=oy); b.panel("彎矩圖（畫在受拉側）", sub_bmd)
    for m in ms:
        p0, p1 = f.N[m["i"]], f.N[m["j"]]; d, L = unit(p0, p1); n = (-d[1], d[0])
        poly = [(p0[0] + d[0] * k / 80 * L - n[0] * member_moment(f, m, k / 80) * msc,
                 p0[1] + d[1] * k / 80 * L - n[1] * member_moment(f, m, k / 80) * msc) for k in range(81)]
        b.polygon([p0] + poly + [p1], C["fill_m"], C["bmd"], 2)
    draw_members(b, N, members, "#4A5568", False)
    _sup(b)
    for nd in sp.get("hinges", []): b.dot(N[nd], 6, fill="#FFFFFF", stroke="#4A5568", w=2.4)
    for m in ms:
        p0, p1 = f.N[m["i"]], f.N[m["j"]]; d, L = unit(p0, p1)
        for xi in inflections(f, m):
            b.dot((p0[0] + d[0] * xi * L, p0[1] + d[1] * xi * L), 5, fill="#FFFFFF", stroke=C["accent"], w=2.6)
    for name, xi, dx, dy in labels:
        m = next(mm for mm in ms if mm["name"] == name)
        p0, p1 = f.N[m["i"]], f.N[m["j"]]; d, L = unit(p0, p1); n = (-d[1], d[0])
        M = member_moment(f, m, xi)
        q = (p0[0] + d[0] * xi * L - n[0] * M * msc, p0[1] + d[1] * xi * L - n[1] * M * msc)
        b.text_px(b.X(q[0]) + dx, b.Y(q[1]) + dy, fmt.format(abs(M)), 14, C["bmd"], weight="700")
    if notes[1]: b.text_px(W / 2, H - 22, notes[1], 12.5, C["bmd"], weight="700")
    if extra: extra(a, b)
    compose([a, b], title=title, path=path)
    return path

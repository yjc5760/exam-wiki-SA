"""
structdraw.py — 結構工程解題圖解 SVG 產生器（雛型）
所有圖形由座標與參數決定，非 AI 生圖，可重跑、可審核。
"""

FONT = "'Noto Sans CJK TC','Microsoft JhengHei','PingFang TC',sans-serif"
FONT_M = "'Latin Modern Math','Cambria Math','Times New Roman',serif"

C = {
    "member":  "#3F4A5A",
    "member2": "#8A94A6",
    "load":    "#C0392B",
    "dim":     "#8A94A6",
    "ghost":   "#C3CAD5",
    "deform":  "#1D4ED8",
    "bmd":     "#2E7D6F",
    "bmdfill": "rgba(46,125,111,0.20)",
    "accent":  "#B45309",
    "text":    "#1F2733",
    "muted":   "#6B7684",
    "panel":   "#F5F7FA",
}


# ---------- 數學字串：_{下標} ^{上標} ----------
def mtext(s, size=15):
    """把 'k_{33} = 24EI/L^{3}' 轉成含 tspan 的 SVG 內容。
    使用絕對 font-size 與 dy 位移，瀏覽器 / WeasyPrint / cairosvg 皆可正確渲染。"""
    small = round(size * 0.68, 2)
    out, i, pend = [], 0, 0.0
    while i < len(s):
        ch = s[i]
        if ch in "_^" and i + 1 < len(s):
            if s[i + 1] == "{":
                j = s.index("}", i + 2)
                body, nxt = s[i + 2:j], j + 1
            else:
                body, nxt = s[i + 1], i + 2
            shift = size * 0.30 if ch == "_" else -size * 0.40
            out.append(f'<tspan dy="{shift - pend:.2f}" font-size="{small}">{body}</tspan>')
            pend = shift
            i = nxt
        else:
            j = i
            while j < len(s) and not (s[j] in "_^" and j + 1 < len(s)):
                j += 1
            body = s[i:j]
            if pend:
                out.append(f'<tspan dy="{-pend:.2f}" font-size="{size}">{body}</tspan>')
                pend = 0.0
            else:
                out.append(body)
            i = j
    return "".join(out)


def est_width(s, size):
    """粗估文字寬度（用於把含上下標的置中文字轉為 start 錨點，避免渲染器差異）"""
    w, i, small = 0.0, 0, 0.68
    def cw(ch, f=1.0):
        o = ord(ch)
        if o > 0x2E80: return 1.0 * size * f
        if ch == " ": return 0.28 * size * f
        return 0.52 * size * f
    while i < len(s):
        if s[i] in "_^" and i + 1 < len(s):
            if s[i+1] == "{":
                j = s.index("}", i+2); body, i = s[i+2:j], j+1
            else:
                body, i = s[i+1], i+2
            w += sum(cw(c, small) for c in body)
        else:
            w += cw(s[i]); i += 1
    return w


class Canvas:
    """SVG 畫布。內部採數學座標 (y 向上)，輸出時自動翻轉。"""

    def __init__(self, w, h, sx=1.0, ox=0.0, oy=0.0, bg=None):
        self.w, self.h = w, h
        self.sx, self.ox, self.oy = sx, ox, oy
        self.parts = []
        self.defs = []
        if bg:
            self.parts.append(f'<rect width="{w}" height="{h}" fill="{bg}"/>')

    # --- 座標轉換 ---
    def X(self, x):
        return self.ox + x * self.sx

    def Y(self, y):
        return self.h - (self.oy + y * self.sx)

    def P(self, p):
        return (self.X(p[0]), self.Y(p[1]))

    # --- 基本圖元 ---
    def line(self, p0, p1, color=C["member"], w=2, dash=None, cap="round", op=1.0):
        x0, y0 = self.P(p0); x1, y1 = self.P(p1)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" '
            f'stroke="{color}" stroke-width="{w}" stroke-linecap="{cap}"{d} opacity="{op}"/>')

    def poly(self, pts, color=C["member"], w=2, dash=None, fill="none", op=1.0):
        s = " ".join(f"{self.X(x):.2f},{self.Y(y):.2f}" for x, y in pts)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(
            f'<polyline points="{s}" fill="{fill}" stroke="{color}" stroke-width="{w}" '
            f'stroke-linecap="round" stroke-linejoin="round"{d} opacity="{op}"/>')

    def polygon(self, pts, fill, stroke="none", w=1, op=1.0):
        s = " ".join(f"{self.X(x):.2f},{self.Y(y):.2f}" for x, y in pts)
        self.parts.append(
            f'<polygon points="{s}" fill="{fill}" stroke="{stroke}" stroke-width="{w}" opacity="{op}"/>')

    def dot(self, p, r=4.5, fill=C["member"], stroke="#FFFFFF", w=1.6):
        x, y = self.P(p)
        self.parts.append(
            f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{w}"/>')

    def text(self, p, s, size=15, color=C["text"], anchor="middle", weight="400",
             italic=False, dx=0, dy=0, font=None, baseline="middle"):
        x, y = self.P(p)
        st = ' font-style="italic"' if italic else ""
        if ("_" in s or "^" in s) and anchor in ("middle", "end"):
            dx = dx - est_width(s, size) * (0.5 if anchor == "middle" else 1.0)
            anchor = "start"
        body = mtext(s, size) if ("_" in s or "^" in s) else s
        self.parts.append(
            f'<text x="{x + dx:.2f}" y="{y + dy:.2f}" font-family="{font or FONT}" '
            f'font-size="{size}" fill="{color}" text-anchor="{anchor}" '
            f'dominant-baseline="{baseline}" font-weight="{weight}"{st}>{body}</text>')

    def math(self, p, s, size=15, color=C["text"], anchor="middle", dx=0, dy=0, weight="400"):
        self.text(p, s, size, color, anchor, weight, italic=True, dx=dx, dy=dy, font=FONT_M)

    def rect_px(self, x, y, w, h, fill, rx=10, stroke="none", sw=1):
        self.parts.append(
            f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{sw}"/>')

    def text_px(self, x, y, s, size=15, color=C["text"], anchor="middle", weight="400",
                italic=False, font=None):
        st = ' font-style="italic"' if italic else ""
        if ("_" in s or "^" in s) and anchor in ("middle", "end"):
            x = x - est_width(s, size) * (0.5 if anchor == "middle" else 1.0)
            anchor = "start"
        body = mtext(s, size) if ("_" in s or "^" in s) else s
        self.parts.append(
            f'<text x="{x}" y="{y}" font-family="{font or FONT}" font-size="{size}" '
            f'fill="{color}" text-anchor="{anchor}" dominant-baseline="middle" '
            f'font-weight="{weight}"{st}>{body}</text>')

    # --- 工程符號 ---
    def arrow(self, p0, p1, color=C["load"], w=3.2, head=10):
        """帶箭頭的力向量（p0 起點 → p1 箭頭端）"""
        import math
        x0, y0 = self.P(p0); x1, y1 = self.P(p1)
        ang = math.atan2(y1 - y0, x1 - x0)
        bx, by = x1 - head * math.cos(ang), y1 - head * math.sin(ang)
        self.parts.append(
            f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{bx:.2f}" y2="{by:.2f}" '
            f'stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')
        hw = head * 0.46
        p = [(x1, y1),
             (bx - hw * math.sin(ang), by + hw * math.cos(ang)),
             (bx + hw * math.sin(ang), by - hw * math.cos(ang))]
        s = " ".join(f"{a:.2f},{b:.2f}" for a, b in p)
        self.parts.append(f'<polygon points="{s}" fill="{color}"/>')

    def moment_arrow(self, p, r=22, ccw=True, color=C["load"], w=2.8, span=250, start=None):
        """彎矩（曲線箭頭）。span 為角度跨距。"""
        import math
        cx, cy = self.P(p)
        a0 = (start if start is not None else 110)
        a1 = a0 + (span if ccw else -span)
        ra0, ra1 = math.radians(a0), math.radians(a1)
        x0, y0 = cx + r * math.cos(ra0), cy - r * math.sin(ra0)
        x1, y1 = cx + r * math.cos(ra1), cy - r * math.sin(ra1)
        large = 1 if abs(span) > 180 else 0
        sweep = 0 if ccw else 1
        self.parts.append(
            f'<path d="M {x0:.2f} {y0:.2f} A {r} {r} 0 {large} {sweep} {x1:.2f} {y1:.2f}" '
            f'fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')
        tang = ra1 + (math.pi / 2 if ccw else -math.pi / 2)
        hx, hy = math.cos(tang), -math.sin(tang)
        hl, hw = 10, 4.6
        px, py = -hy, hx
        pts = [(x1, y1), (x1 - hl * hx + hw * px, y1 - hl * hy + hw * py),
               (x1 - hl * hx - hw * px, y1 - hl * hy - hw * py)]
        s = " ".join(f"{a:.2f},{b:.2f}" for a, b in pts)
        self.parts.append(f'<polygon points="{s}" fill="{color}"/>')

    def fixed_support(self, p, ang=0, size=20, color=C["member"]):
        """固定支承：底線 + 斜剖線。ang=0 表支承面在下方。"""
        import math
        cx, cy = self.P(p)
        a = math.radians(ang)
        ux, uy = math.cos(a), -math.sin(a)      # 支承面方向
        nx, ny = math.sin(a), math.cos(a)       # 指向材料外側（螢幕下方）
        self.parts.append(
            f'<line x1="{cx - ux*size:.2f}" y1="{cy - uy*size:.2f}" '
            f'x2="{cx + ux*size:.2f}" y2="{cy + uy*size:.2f}" '
            f'stroke="{color}" stroke-width="3.2" stroke-linecap="round"/>')
        n = 5
        for i in range(n):
            t = -size + (2 * size) * (i + 0.15) / (n - 0.7)
            bx, by = cx + ux * t, cy + uy * t
            self.parts.append(
                f'<line x1="{bx:.2f}" y1="{by:.2f}" '
                f'x2="{bx - ux*7 + nx*8:.2f}" y2="{by - uy*7 + ny*8:.2f}" '
                f'stroke="{color}" stroke-width="1.8" stroke-linecap="round"/>')

    def dim(self, p0, p1, label, off=0, color=C["dim"], size=14, side=1, label_off=13):
        """尺寸線（含兩端箭頭與延伸線）"""
        import math
        x0, y0 = self.P(p0); x1, y1 = self.P(p1)
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L * off, dx / L * off
        a0 = (x0 + nx, y0 + ny); a1 = (x1 + nx, y1 + ny)
        for s, e in ((( x0, y0), a0), ((x1, y1), a1)):
            self.parts.append(
                f'<line x1="{s[0]:.2f}" y1="{s[1]:.2f}" x2="{e[0]+nx*0.18:.2f}" '
                f'y2="{e[1]+ny*0.18:.2f}" stroke="{color}" stroke-width="1" '
                f'stroke-dasharray="3 3"/>')
        self.parts.append(
            f'<line x1="{a0[0]:.2f}" y1="{a0[1]:.2f}" x2="{a1[0]:.2f}" y2="{a1[1]:.2f}" '
            f'stroke="{color}" stroke-width="1.2"/>')
        for (px, py), sgn in ((a0, 1), (a1, -1)):
            ang = math.atan2(dy * sgn, dx * sgn)
            hl, hw = 8, 3.2
            pts = [(px, py),
                   (px + hl * math.cos(ang) - hw * math.sin(ang), py + hl * math.sin(ang) + hw * math.cos(ang)),
                   (px + hl * math.cos(ang) + hw * math.sin(ang), py + hl * math.sin(ang) - hw * math.cos(ang))]
            s = " ".join(f"{a:.2f},{b:.2f}" for a, b in pts)
            self.parts.append(f'<polygon points="{s}" fill="{color}"/>')
        mx, my = (a0[0] + a1[0]) / 2, (a0[1] + a1[1]) / 2
        lx, ly = -dy / L * label_off, dx / L * label_off
        self.text_px(mx + lx, my + ly, label, size, color, italic=True, font=FONT_M)

    def svg(self):
        d = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">{d}{"".join(self.parts)}</svg>')

    def save(self, path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.svg())


# ---------- 撓曲形狀（Hermite 三次形狀函數） ----------
def hermite(v1, t1, v2, t2, Lm, n=60):
    """回傳 [(xi, w)]，w 為局部橫向撓度。t 為局部端點斜率 dw/dx。"""
    out = []
    for i in range(n + 1):
        x = i / n
        N1 = 1 - 3 * x**2 + 2 * x**3
        N2 = Lm * (x - 2 * x**2 + x**3)
        N3 = 3 * x**2 - 2 * x**3
        N4 = Lm * (x**3 - x**2)
        out.append((x, N1 * v1 + N2 * t1 + N3 * v2 + N4 * t2))
    return out


def column_shape(base, Lm, delta, theta_top, theta_bot=0.0, amp=1.0, n=60):
    """垂直柱：base=(x,y) 底端。回傳整體座標點列。
    整體 CCW 轉角 theta 對應局部 du/dy = -theta。"""
    bx, by = base
    pts = []
    for xi, w in hermite(0.0, -theta_bot, delta, -theta_top, Lm, n):
        pts.append((bx + w * amp, by + xi * Lm))
    return pts


def beam_shape(left, Lm, thL, thR, vL=0.0, vR=0.0, amp=1.0, n=60):
    """水平梁：left=(x,y) 左端。dv/dx = theta（CCW 正）。"""
    lx, ly = left
    return [(lx + xi * Lm, ly + w * amp) for xi, w in hermite(vL, thL, vR, thR, Lm, n)]



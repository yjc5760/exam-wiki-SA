"""
structdraw.py — 結構工程解題圖解的 SVG primitives
==================================================
設計原則：所有圖形由「座標 + 數值」決定，不由描摹決定。
改一個輸入數字，圖形自動跟著變；圖若畫錯，代表數字錯，不是圖錯。

座標系：內部使用數學座標（y 向上），輸出時自動翻轉為 SVG 座標。

完整 API 說明見 references/API.md
"""

FONT = "'Noto Sans CJK TC','Noto Sans TC','Microsoft JhengHei','PingFang TC','Heiti TC',sans-serif"
FONT_M = "'Latin Modern Math','Cambria Math','Times New Roman','Nimbus Roman',serif"

# 統一色票（六科共用，勿在個別圖裡另外定義顏色）
C = {
    "member":  "#3F4A5A",   # 構材
    "member2": "#8A94A6",   # 次要構材
    "ghost":   "#C3CAD5",   # 原始（未變形）位置
    "load":    "#C0392B",   # 外力、外加作用
    "deform":  "#1D4ED8",   # 變形、位移、自由度
    "bmd":     "#2E7D6F",   # 彎矩圖
    "sfd":     "#7C3AED",   # 剪力圖
    "tension": "#C0392B",   # 受拉
    "compr":   "#1D4ED8",   # 受壓
    "accent":  "#B45309",   # 重點標記（反曲點、關鍵位置）
    "dim":     "#8A94A6",   # 尺寸線
    "text":    "#1F2733",
    "muted":   "#6B7684",
    "panel":   "#F5F7FA",   # 子圖底色
    "border":  "#E1E6ED",
    "fill_t":  "rgba(192,57,43,0.18)",
    "fill_c":  "rgba(29,78,216,0.18)",
    "fill_m":  "rgba(46,125,111,0.20)",
    "fill_s":  "rgba(124,58,237,0.18)",
}


# ══════════════════════════════════════════════════════════
# 數學字串：_{下標} ^{上標}
# ══════════════════════════════════════════════════════════
def mtext(s, size=15):
    """'k_{33} = 24EI/L^{3}' → 含 tspan 的 SVG 內容。
    採絕對 font-size + dy 位移，瀏覽器 / WeasyPrint / cairosvg 皆正確。"""
    small = round(size * 0.68, 2)
    out, i, pend = [], 0, 0.0
    while i < len(s):
        ch = s[i]
        if ch in "_^" and i + 1 < len(s):
            if s[i + 1] == "{":
                j = s.index("}", i + 2); body, nxt = s[i + 2:j], j + 1
            else:
                body, nxt = s[i + 1], i + 2
            shift = size * 0.30 if ch == "_" else -size * 0.40
            out.append(f'<tspan dy="{shift - pend:.2f}" font-size="{small}">{body}</tspan>')
            pend = shift; i = nxt
        else:
            j = i
            while j < len(s) and not (s[j] in "_^" and j + 1 < len(s)):
                j += 1
            body = s[i:j]
            if pend:
                out.append(f'<tspan dy="{-pend:.2f}" font-size="{size}">{body}</tspan>'); pend = 0.0
            else:
                out.append(body)
            i = j
    return "".join(out)


def est_width(s, size):
    """粗估文字寬度。用於把含上下標的置中文字改為 start 錨點，
    避免不同渲染器對 text-anchor + tspan 的處理差異。"""
    small = 0.68
    def cw(ch, f=1.0):
        o = ord(ch)
        if o > 0x2E80: return 1.0 * size * f
        if ch == " ":  return 0.28 * size * f
        return 0.52 * size * f
    w, i = 0.0, 0
    while i < len(s):
        if s[i] in "_^" and i + 1 < len(s):
            if s[i + 1] == "{":
                j = s.index("}", i + 2); body, i = s[i + 2:j], j + 1
            else:
                body, i = s[i + 1], i + 2
            w += sum(cw(c, small) for c in body)
        else:
            w += cw(s[i]); i += 1
    return w


def esc(s):
    """XML 字元跳脫（文字內容含 & < > 時務必使用）"""
    return (str(s).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))


# ══════════════════════════════════════════════════════════
class Canvas:
    """一張 SVG 畫布。

    sx  : 每 1 模型單位對應的像素數（等向縮放）
    ox,oy: 模型原點在畫布中的像素位置（oy 由畫布底部起算）
    """

    def __init__(self, w, h, sx=1.0, ox=0.0, oy=0.0, bg=None):
        self.w, self.h = w, h
        self.sx, self.ox, self.oy = sx, ox, oy
        self.parts, self.defs = [], []
        if bg:
            self.parts.append(f'<rect width="{w}" height="{h}" fill="{bg}"/>')

    # ---- 座標轉換 ----
    def X(self, x): return self.ox + x * self.sx
    def Y(self, y): return self.h - (self.oy + y * self.sx)
    def P(self, p): return (self.X(p[0]), self.Y(p[1]))

    # ---- 基本圖元 ----
    def line(self, p0, p1, color=C["member"], w=2, dash=None, cap="round", op=1.0):
        x0, y0 = self.P(p0); x1, y1 = self.P(p1)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{x1:.2f}" y2="{y1:.2f}" '
                          f'stroke="{color}" stroke-width="{w}" stroke-linecap="{cap}"{d} opacity="{op}"/>')

    def poly(self, pts, color=C["member"], w=2, dash=None, fill="none", op=1.0):
        s = " ".join(f"{self.X(x):.2f},{self.Y(y):.2f}" for x, y in pts)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<polyline points="{s}" fill="{fill}" stroke="{color}" stroke-width="{w}" '
                          f'stroke-linecap="round" stroke-linejoin="round"{d} opacity="{op}"/>')

    def polygon(self, pts, fill, stroke="none", w=1, op=1.0):
        s = " ".join(f"{self.X(x):.2f},{self.Y(y):.2f}" for x, y in pts)
        self.parts.append(f'<polygon points="{s}" fill="{fill}" stroke="{stroke}" '
                          f'stroke-width="{w}" opacity="{op}"/>')

    def circle(self, p, r, fill="none", stroke=C["member"], w=2, dash=None, op=1.0):
        x, y = self.P(p)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r*self.sx:.2f}" fill="{fill}" '
                          f'stroke="{stroke}" stroke-width="{w}"{d} opacity="{op}"/>')

    def dot(self, p, r=4.5, fill=C["member"], stroke="#FFFFFF", w=1.6):
        x, y = self.P(p)
        self.parts.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{fill}" '
                          f'stroke="{stroke}" stroke-width="{w}"/>')

    # ---- 文字 ----
    def text(self, p, s, size=15, color=C["text"], anchor="middle", weight="400",
             italic=False, dx=0, dy=0, font=None, baseline="middle"):
        x, y = self.P(p)
        self._text_abs(x + dx, y + dy, s, size, color, anchor, weight, italic, font, baseline)

    def text_px(self, x, y, s, size=15, color=C["text"], anchor="middle", weight="400",
                italic=False, font=None, baseline="middle"):
        self._text_abs(x, y, s, size, color, anchor, weight, italic, font, baseline)

    def _text_abs(self, x, y, s, size, color, anchor, weight, italic, font, baseline="middle"):
        st = ' font-style="italic"' if italic else ""
        if ("_" in s or "^" in s) and anchor in ("middle", "end"):
            x -= est_width(s, size) * (0.5 if anchor == "middle" else 1.0)
            anchor = "start"
        body = mtext(s, size) if ("_" in s or "^" in s) else s
        self.parts.append(f'<text x="{x:.2f}" y="{y:.2f}" font-family="{font or FONT}" '
                          f'font-size="{size}" fill="{color}" text-anchor="{anchor}" '
                          f'dominant-baseline="{baseline}" font-weight="{weight}"{st}>{body}</text>')

    def math(self, p, s, size=15, color=C["text"], anchor="middle", dx=0, dy=0, weight="400"):
        """數學符號（襯線斜體）"""
        self.text(p, s, size, color, anchor, weight, italic=True, dx=dx, dy=dy, font=FONT_M)

    def math_px(self, x, y, s, size=15, color=C["text"], anchor="middle", weight="400"):
        self.text_px(x, y, s, size, color, anchor, weight, italic=True, font=FONT_M)

    def rect_px(self, x, y, w, h, fill, rx=10, stroke="none", sw=1):
        self.parts.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                          f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def panel(self, title=None, sub=None, pad=6, radius=14):
        """子圖外框 + 標題（常用於多聯圖的每一格）"""
        self.rect_px(pad, pad, self.w - 2*pad, self.h - 2*pad, C["panel"], radius, C["border"], 1.2)
        if title: self.text_px(self.w / 2, 32, title, 15.5, C["text"], weight="700")
        if sub:   self.text_px(self.w / 2, 55, sub, 12.5, C["muted"])

    # ---- 箭頭與力 ----
    def arrow(self, p0, p1, color=C["load"], w=3.2, head=10, dash=None):
        """力向量：p0 起點 → p1 箭頭端"""
        import math
        x0, y0 = self.P(p0); x1, y1 = self.P(p1)
        ang = math.atan2(y1 - y0, x1 - x0)
        bx, by = x1 - head * math.cos(ang), y1 - head * math.sin(ang)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<line x1="{x0:.2f}" y1="{y0:.2f}" x2="{bx:.2f}" y2="{by:.2f}" '
                          f'stroke="{color}" stroke-width="{w}" stroke-linecap="round"{d}/>')
        hw = head * 0.46
        pts = [(x1, y1), (bx - hw*math.sin(ang), by + hw*math.cos(ang)),
               (bx + hw*math.sin(ang), by - hw*math.cos(ang))]
        self.parts.append(f'<polygon points="{" ".join(f"{a:.2f},{b:.2f}" for a,b in pts)}" fill="{color}"/>')

    def double_arrow(self, p0, p1, color=C["load"], w=3.0, head=10):
        """雙箭頭（力偶、對稱標示）"""
        self.arrow(p0, p1, color, w, head); self.arrow(p1, p0, color, w, head)

    def moment_arrow(self, p, r=22, ccw=True, color=C["load"], w=2.8, span=250, start=110):
        """彎矩／轉角：曲線箭頭。span 為角度跨距，start 為起始角（數學角，度）。"""
        import math
        cx, cy = self.P(p)
        a0 = start; a1 = a0 + (span if ccw else -span)
        ra0, ra1 = math.radians(a0), math.radians(a1)
        x0, y0 = cx + r*math.cos(ra0), cy - r*math.sin(ra0)
        x1, y1 = cx + r*math.cos(ra1), cy - r*math.sin(ra1)
        large = 1 if abs(span) > 180 else 0
        sweep = 0 if ccw else 1
        self.parts.append(f'<path d="M {x0:.2f} {y0:.2f} A {r} {r} 0 {large} {sweep} {x1:.2f} {y1:.2f}" '
                          f'fill="none" stroke="{color}" stroke-width="{w}" stroke-linecap="round"/>')
        tang = ra1 + (math.pi/2 if ccw else -math.pi/2)
        hx, hy = math.cos(tang), -math.sin(tang)
        hl, hw = 10, 4.6; px, py = -hy, hx
        pts = [(x1, y1), (x1-hl*hx+hw*px, y1-hl*hy+hw*py), (x1-hl*hx-hw*px, y1-hl*hy-hw*py)]
        self.parts.append(f'<polygon points="{" ".join(f"{a:.2f},{b:.2f}" for a,b in pts)}" fill="{color}"/>')

    def udl(self, p0, p1, height, n=9, color=C["load"], w=2.0, taper=None, label=None):
        """均佈／梯形載重。height 為載重高度（模型單位，正值＝箭頭由上往下指向構材）。
        taper=(h0,h1) 時畫梯形分佈。"""
        import math
        (x0, y0), (x1, y1) = p0, p1
        h0, h1 = taper if taper else (height, height)
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy / L, dx / L          # 單位法向
        top = [(x0 + nx*h0, y0 + ny*h0), (x1 + nx*h1, y1 + ny*h1)]
        self.line(top[0], top[1], color, w)
        for i in range(n):
            t = i / (n - 1)
            hh = h0 + (h1 - h0) * t
            bx, by = x0 + dx*t, y0 + dy*t
            self.arrow((bx + nx*hh, by + ny*hh), (bx, by), color, w, 8)
        if label:
            mx, my = (top[0][0] + top[1][0])/2, (top[0][1] + top[1][1])/2
            self.math_px(self.X(mx), self.Y(my) - 14, label, 15, color, weight="700")

    # ---- 支承符號 ----
    def _hatch(self, cx, cy, ux, uy, nx, ny, size, color, n=5, w=1.8):
        for i in range(n):
            t = -size + (2*size) * (i + 0.15) / (n - 0.7)
            bx, by = cx + ux*t, cy + uy*t
            self.parts.append(f'<line x1="{bx:.2f}" y1="{by:.2f}" x2="{bx-ux*7+nx*8:.2f}" '
                              f'y2="{by-uy*7+ny*8:.2f}" stroke="{color}" stroke-width="{w}" '
                              f'stroke-linecap="round"/>')

    def fixed_support(self, p, ang=0, size=20, color=C["member"]):
        """固定端（鉛垂線＋斜剖線）。ang=0：支承面在下方；ang=90：支承面在左側牆。"""
        import math
        cx, cy = self.P(p); a = math.radians(ang)
        ux, uy = math.cos(a), -math.sin(a)
        nx, ny = math.sin(a), math.cos(a)
        self.parts.append(f'<line x1="{cx-ux*size:.2f}" y1="{cy-uy*size:.2f}" '
                          f'x2="{cx+ux*size:.2f}" y2="{cy+uy*size:.2f}" stroke="{color}" '
                          f'stroke-width="3.2" stroke-linecap="round"/>')
        self._hatch(cx, cy, ux, uy, nx, ny, size, color)

    def pin_support(self, p, ang=0, size=16, color=C["member"], ground=True):
        """鉸支承（三角形）。ang=0：底部支承。"""
        import math
        cx, cy = self.P(p); a = math.radians(ang)
        ux, uy = math.cos(a), -math.sin(a)
        nx, ny = math.sin(a), math.cos(a)
        h = size * 1.15
        pts = [(cx, cy), (cx - ux*size*0.72 + nx*h, cy - uy*size*0.72 + ny*h),
               (cx + ux*size*0.72 + nx*h, cy + uy*size*0.72 + ny*h)]
        self.parts.append(f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in pts)}" '
                          f'fill="none" stroke="{color}" stroke-width="2.6" stroke-linejoin="round"/>')
        if ground:
            gx, gy = cx + nx*h, cy + ny*h
            self.parts.append(f'<line x1="{gx-ux*size*1.25:.2f}" y1="{gy-uy*size*1.25:.2f}" '
                              f'x2="{gx+ux*size*1.25:.2f}" y2="{gy+uy*size*1.25:.2f}" '
                              f'stroke="{color}" stroke-width="2.6" stroke-linecap="round"/>')
            self._hatch(gx, gy, ux, uy, nx, ny, size*1.25, color)

    def roller_support(self, p, ang=0, size=16, color=C["member"]):
        """滾支承（三角形＋滾輪）"""
        import math
        cx, cy = self.P(p); a = math.radians(ang)
        ux, uy = math.cos(a), -math.sin(a); nx, ny = math.sin(a), math.cos(a)
        h = size * 1.15
        pts = [(cx, cy), (cx - ux*size*0.72 + nx*h, cy - uy*size*0.72 + ny*h),
               (cx + ux*size*0.72 + nx*h, cy + uy*size*0.72 + ny*h)]
        self.parts.append(f'<polygon points="{" ".join(f"{x:.2f},{y:.2f}" for x,y in pts)}" '
                          f'fill="none" stroke="{color}" stroke-width="2.6" stroke-linejoin="round"/>')
        r = size * 0.26
        for t in (-0.42, 0.0, 0.42):
            rx, ry = cx + ux*size*t + nx*(h + r), cy + uy*size*t + ny*(h + r)
            self.parts.append(f'<circle cx="{rx:.2f}" cy="{ry:.2f}" r="{r:.2f}" fill="none" '
                              f'stroke="{color}" stroke-width="2"/>')
        gx, gy = cx + nx*(h + 2*r), cy + ny*(h + 2*r)
        self.parts.append(f'<line x1="{gx-ux*size*1.25:.2f}" y1="{gy-uy*size*1.25:.2f}" '
                          f'x2="{gx+ux*size*1.25:.2f}" y2="{gy+uy*size*1.25:.2f}" '
                          f'stroke="{color}" stroke-width="2.6" stroke-linecap="round"/>')
        self._hatch(gx, gy, ux, uy, nx, ny, size*1.25, color)

    def support(self, p, kind, ang=0, size=None, color=C["member"]):
        """kind: 'fixed' | 'pin' | 'roller'"""
        f = {"fixed": self.fixed_support, "pin": self.pin_support, "roller": self.roller_support}[kind]
        return f(p, ang, size or (20 if kind == "fixed" else 16), color)

    # ---- 尺寸線 ----
    def dim(self, p0, p1, label, off=0, color=C["dim"], size=14, label_off=13):
        """尺寸線（延伸線＋雙箭頭＋標註）。off 正值為法線 (-dy,dx) 方向偏移（像素）。"""
        import math
        x0, y0 = self.P(p0); x1, y1 = self.P(p1)
        dx, dy = x1 - x0, y1 - y0
        L = math.hypot(dx, dy) or 1
        nx, ny = -dy/L*off, dx/L*off
        a0 = (x0 + nx, y0 + ny); a1 = (x1 + nx, y1 + ny)
        for s, e in (((x0, y0), a0), ((x1, y1), a1)):
            self.parts.append(f'<line x1="{s[0]:.2f}" y1="{s[1]:.2f}" x2="{e[0]+nx*0.18:.2f}" '
                              f'y2="{e[1]+ny*0.18:.2f}" stroke="{color}" stroke-width="1" '
                              f'stroke-dasharray="3 3"/>')
        self.parts.append(f'<line x1="{a0[0]:.2f}" y1="{a0[1]:.2f}" x2="{a1[0]:.2f}" y2="{a1[1]:.2f}" '
                          f'stroke="{color}" stroke-width="1.2"/>')
        for (px, py), sgn in ((a0, 1), (a1, -1)):
            ang = math.atan2(dy*sgn, dx*sgn); hl, hw = 8, 3.2
            pts = [(px, py),
                   (px+hl*math.cos(ang)-hw*math.sin(ang), py+hl*math.sin(ang)+hw*math.cos(ang)),
                   (px+hl*math.cos(ang)+hw*math.sin(ang), py+hl*math.sin(ang)-hw*math.cos(ang))]
            self.parts.append(f'<polygon points="{" ".join(f"{a:.2f},{b:.2f}" for a,b in pts)}" fill="{color}"/>')
        mx, my = (a0[0]+a1[0])/2, (a0[1]+a1[1])/2
        self.math_px(mx - dy/L*label_off, my + dx/L*label_off, label, size, color)

    # ---- 座標軸 ----
    def axes(self, origin, lx=1.0, ly=1.0, labels=("x", "y"), color=C["muted"], w=1.8):
        ox, oy = origin
        self.arrow((ox, oy), (ox + lx, oy), color, w, 9)
        self.arrow((ox, oy), (ox, oy + ly), color, w, 9)
        self.math((ox + lx, oy), labels[0], 14, color, "start", dx=8)
        self.math((ox, oy + ly), labels[1], 14, color, dy=-12)

    # ---- 圖例 ----
    def legend(self, x, y, items, size=12.5, gap=20, swatch=22):
        """items: [(color, '說明'), ...]"""
        for i, (col, lab) in enumerate(items):
            yy = y + i*gap
            self.parts.append(f'<line x1="{x}" y1="{yy}" x2="{x+swatch}" y2="{yy}" '
                              f'stroke="{col}" stroke-width="4" stroke-linecap="round"/>')
            self.text_px(x + swatch + 8, yy, lab, size, C["muted"], "start")

    # ---- 輸出 ----
    def svg(self):
        d = f"<defs>{''.join(self.defs)}</defs>" if self.defs else ""
        return (f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
                f'viewBox="0 0 {self.w} {self.h}">{d}{"".join(self.parts)}</svg>')

    def save(self, path):
        import os
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            f.write(self.svg())
        return path


# ══════════════════════════════════════════════════════════
# 多聯圖組合
# ══════════════════════════════════════════════════════════
def compose(panels, title=None, sub=None, note=None, cols=None,
            pad_top=None, pad_bottom=46, bg="#FFFFFF", path=None):
    """把數個 Canvas 併成一張 SVG（橫向排列或格狀）。
    panels: [Canvas, ...]（每個 Canvas 尺寸須相同）"""
    n = len(panels); cols = cols or n
    rows = (n + cols - 1) // cols
    pw, ph = panels[0].w, panels[0].h
    top = pad_top if pad_top is not None else (76 if title else 0)
    W, H = pw*cols, ph*rows + top + (pad_bottom if note else 0)
    parts = [f'<rect width="{W}" height="{H}" fill="{bg}"/>']
    if title:
        parts.append(f'<text x="{W/2}" y="34" font-family="{FONT}" font-size="17.5" '
                     f'fill="{C["text"]}" text-anchor="middle" font-weight="700">{esc(title)}</text>')
    if sub:
        parts.append(f'<text x="{W/2}" y="58" font-family="{FONT}" font-size="13" '
                     f'fill="{C["muted"]}" text-anchor="middle">{esc(sub)}</text>')
    clips = []
    for i, p in enumerate(panels):
        cid = f"sdclip{i}"
        clips.append(f'<clipPath id="{cid}"><rect x="0" y="0" width="{pw}" height="{ph}"/></clipPath>')
        parts.append(f'<g transform="translate({(i%cols)*pw},{top+(i//cols)*ph})" '
                     f'clip-path="url(#{cid})">{"".join(p.parts)}</g>')
    parts.insert(0, f'<defs>{"".join(clips)}</defs>')
    if note:
        parts.append(f'<text x="{W/2}" y="{H-22}" font-family="{FONT}" font-size="13.5" '
                     f'fill="{C["muted"]}" text-anchor="middle">{esc(note)}</text>')
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" '
           f'viewBox="0 0 {W} {H}">{"".join(parts)}</svg>')
    if path:
        import os
        os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
        open(path, "w", encoding="utf-8").write(svg)
    return svg


# ══════════════════════════════════════════════════════════
# 撓曲形狀（三次 Hermite 形狀函數）
# ══════════════════════════════════════════════════════════
def hermite(v1, t1, v2, t2, Lm, n=60):
    """回傳 [(ξ, w)]。v=端點橫向位移，t=端點斜率 dw/dx（局部座標）。"""
    out = []
    for i in range(n + 1):
        x = i / n
        out.append((x, (1-3*x**2+2*x**3)*v1 + Lm*(x-2*x**2+x**3)*t1
                       + (3*x**2-2*x**3)*v2 + Lm*(x**3-x**2)*t2))
    return out


def column_shape(base, Lm, delta_top, theta_top, delta_bot=0.0, theta_bot=0.0, n=60):
    """垂直柱（base 為底端整體座標）。
    theta 為整體逆時針正之節點轉角；對垂直桿件 du/dy = -theta。
    回傳整體座標點列，可直接餵給 Canvas.poly()。"""
    bx, by = base
    return [(bx + w, by + xi*Lm)
            for xi, w in hermite(delta_bot, -theta_bot, delta_top, -theta_top, Lm, n)]


def beam_shape(left, Lm, theta_L, theta_R, v_L=0.0, v_R=0.0, n=60):
    """水平梁（left 為左端整體座標）。theta 為逆時針正，dv/dx = theta。"""
    lx, ly = left
    return [(lx + xi*Lm, ly + w) for xi, w in hermite(v_L, theta_L, v_R, theta_R, Lm, n)]


def member_shape(p0, p1, w_of_xi, n=60):
    """任意方向構材：w_of_xi(ξ) 為局部橫向撓度函數，法向為 (-dy,dx)/L。"""
    import math
    (x0, y0), (x1, y1) = p0, p1
    dx, dy = x1-x0, y1-y0
    L = math.hypot(dx, dy) or 1
    nx, ny = -dy/L, dx/L
    out = []
    for i in range(n+1):
        xi = i/n; w = w_of_xi(xi)
        out.append((x0 + dx*xi + nx*w, y0 + dy*xi + ny*w))
    return out

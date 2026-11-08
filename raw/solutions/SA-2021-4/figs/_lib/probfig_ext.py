"""probfig_ext — probfig.problem_figure 加上 pre／post 繪圖掛勾（exam-wiki-SA，2026-11-07，SA 剩餘單元批 1 起用）
pre(cv, N)：在構件之前畫（例：剛性區域填色、剪力牆面）；post(cv, N)：在全部元素之後畫（例：構件間彈簧、文字）。
另提供 spring_between（兩點之間的彈簧，不畫地面）。幾何一律由呼叫端 spec（判讀清單）給定。"""
import math
from structdraw import Canvas, C
from frameviz import fit, draw_problem
from probfig import _extent, spring


def spring_between(cv, p, q, n=6, amp=7, color=C["member"]):
    """p、q 兩點（模型座標）之間的鋸齒彈簧。"""
    (x0, y0), (x1, y1) = cv.P(p), cv.P(q)
    dx, dy = x1 - x0, y1 - y0; L = math.hypot(dx, dy); ux, uy = dx / L, dy / L; nx, ny = -uy, ux
    a, b = 0.18 * L, 0.82 * L; seg = (b - a) / n
    pts = [(x0, y0), (x0 + ux * a, y0 + uy * a)]
    for i in range(n):
        s = a + seg * (i + 0.5); k = amp if i % 2 == 0 else -amp
        pts.append((x0 + ux * s + nx * k, y0 + uy * s + ny * k))
    pts += [(x0 + ux * b, y0 + uy * b), (x1, y1)]
    cv.parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>'
                    % (" ".join("%.2f,%.2f" % t for t in pts), color))


def problem_figure_ext(sp, path, W=760, H=520, title=None, note=None, margins=(110, 110, 80, 120),
                       pre=None, post=None):
    sx, ox, oy = fit(_extent(sp), W, H, *margins)
    cv = Canvas(W, H, sx=sx, ox=ox, oy=oy, bg="#FFFFFF")
    N = sp['nodes']
    if pre: pre(cv, N)
    for (a, b) in sp.get('dashed', []):
        cv.line(N[a], N[b], C["muted"], 1.6, dash="10 7")
    for (a, b) in sp.get('truss', []):
        cv.line(N[a], N[b], C["member"], 3.2, cap="round")
    for (a, b) in sp.get('rigid', []):
        cv.line(N[a], N[b], C["member"], 9.0, cap="butt"); cv.line(N[a], N[b], "#FFFFFF", 4.0, cap="butt")
    draw_problem(cv, dict(sp, supports=[s for s in sp.get('supports', []) if len(s) == 2]))
    for (nd, kind, ang) in [s for s in sp.get('supports', []) if len(s) == 3]:
        cv.support(N[nd], kind, ang)
    for (nd, length, lab) in sp.get('springs', []):
        spring(cv, N[nd], length); x, y = cv.P(N[nd])
        cv.math_px(x + 22, y + length * cv.sx * 0.5, lab, 16, C["text"], "start")
    for nd in sp.get('joints', []):
        cv.dot(N[nd], 5.5, fill="#FFFFFF", stroke=C["member"], w=2.2)
    for (p, ccw, lab, lo) in sp.get('couples', []):
        cv.moment_arrow(p, r=20, ccw=ccw, color=C["load"], w=2.6, span=250, start=sp.get('cstart', 110))
        cv.math(p, lab, 15, C["load"], "middle", dx=lo[0], dy=lo[1], weight="700")
    for (p, s, size, col, anchor) in sp.get('ptexts', []):
        x, y = cv.P(p); cv.text_px(x, y, s, size, col or C["muted"], anchor)
    if post: post(cv, N)
    if title: cv.text_px(W / 2, 26, title, 15.5, C["text"], weight="700")
    if note:
        lines = note if isinstance(note, (list, tuple)) else [note]
        for k, s in enumerate(lines):
            cv.text_px(W / 2, H - 18 - 18 * (len(lines) - 1 - k), s, 12.5, C["muted"])
    return cv.save(path)

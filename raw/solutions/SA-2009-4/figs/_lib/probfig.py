"""probfig — 題目附圖重繪的補充繪圖（exam-wiki-SA，2026-11-05，SA-U1-2 批 1 起用）
在 frameviz.draw_problem 之外補上：桁架（細桿＋節點圈）、任意角度支承、彈簧支承、
分布力矩、指定位置的力偶、虛線、雙線剛梁。所有幾何皆由呼叫端 spec（判讀清單）給定。"""
import math
from structdraw import Canvas, C
from frameviz import fit, draw_problem

def _extent(sp):
    pts = list(sp['nodes'].values())
    for ld in sp.get('loads', []):
        p = sp['nodes'][ld[0]]; dx, dy = ld[1]; pts += [(p[0]-dx, p[1]-dy), (p[0]+dx, p[1]+dy)]
    for (a, b, h, lab) in sp.get('udl', []):
        for nd in (a, b):
            p = sp['nodes'][nd]; q = sp['nodes'][b if nd == a else a]
            L = math.hypot(q[0]-p[0], q[1]-p[1]); nx, ny = -(q[1]-p[1])/L, (q[0]-p[0])/L
            if nd == b: nx, ny = -nx, -ny
            pts.append((p[0]+nx*h, p[1]+ny*h))
    pts += sp.get('extra_pts', [])
    return pts

def spring(cv, p, length, n=6, amp=7, color=C["member"]):
    """垂直線彈簧（p 為上端，模型單位長度 length 向下），底端畫固定剖線。"""
    x, y = cv.P(p); L = length * cv.sx; seg = L * 0.7 / n; y0 = y + L * 0.15
    pts = [(x, y), (x, y0)]
    for i in range(n):
        pts.append((x + (amp if i % 2 == 0 else -amp), y0 + seg * (i + 0.5)))
    y1 = y0 + seg * n; pts += [(x, y1), (x, y + L)]
    cv.parts.append('<polyline points="%s" fill="none" stroke="%s" stroke-width="2.2" stroke-linejoin="round"/>'
                    % (" ".join("%.2f,%.2f" % q for q in pts), color))
    g = y + L
    cv.parts.append('<line x1="%.2f" y1="%.2f" x2="%.2f" y2="%.2f" stroke="%s" stroke-width="2.6"/>'
                    % (x - 16, g, x + 16, g, color))
    cv._hatch(x, g, 1, 0, 0, 1, 16, color)

def problem_figure(sp, path, W=760, H=520, title=None, note=None, margins=(110, 110, 80, 120)):
    sx, ox, oy = fit(_extent(sp), W, H, *margins)
    cv = Canvas(W, H, sx=sx, ox=ox, oy=oy, bg="#FFFFFF")
    N = sp['nodes']
    for (a, b) in sp.get('dashed', []):                      # 非桿件的虛線（照考卷）
        cv.line(N[a], N[b], C["muted"], 1.6, dash="10 7")
    for (a, b) in sp.get('truss', []):                       # 二力桿
        cv.line(N[a], N[b], C["member"], 3.2, cap="round")
    for (a, b) in sp.get('rigid', []):                       # 剛梁（雙線）
        cv.line(N[a], N[b], C["member"], 9.0, cap="butt"); cv.line(N[a], N[b], "#FFFFFF", 4.0, cap="butt")
    draw_problem(cv, dict(sp, supports=[s for s in sp.get('supports', []) if len(s) == 2]))
    for (nd, kind, ang) in [s for s in sp.get('supports', []) if len(s) == 3]:
        cv.support(N[nd], kind, ang)
    for (nd, length, lab) in sp.get('springs', []):
        spring(cv, N[nd], length); x, y = cv.P(N[nd])
        cv.math_px(x + 22, y + length * cv.sx * 0.5, lab, 16, C["text"], "start")
    for nd in sp.get('joints', []):                          # 鉸接節點
        cv.dot(N[nd], 5.5, fill="#FFFFFF", stroke=C["member"], w=2.2)
    for (p, ccw, lab, lo) in sp.get('couples', []):          # 指定位置的集中力偶
        cv.moment_arrow(p, r=20, ccw=ccw, color=C["load"], w=2.6, span=250, start=sp.get('cstart', 110))
        cv.math(p, lab, 15, C["load"], "middle", dx=lo[0], dy=lo[1], weight="700")
    for (a, b, n, ccw, lab, lo) in sp.get('dmoment', []):     # 分布力矩
        pa, pb = N[a], N[b]
        for i in range(n):
            t = (i + 0.5) / n; p = (pa[0] + (pb[0]-pa[0])*t, pa[1] + (pb[1]-pa[1])*t + sp.get('dm_up', 0.35))
            cv.moment_arrow(p, r=9, ccw=ccw, color=C["load"], w=2.0, span=230, start=150)
        mid = ((pa[0]+pb[0])/2, (pa[1]+pb[1])/2)
        cv.math(mid, lab, 15, C["load"], "middle", dx=lo[0], dy=lo[1], weight="700")
    for (p, s, size, col, anchor) in sp.get('ptexts', []):
        x, y = cv.P(p); cv.text_px(x, y, s, size, col or C["muted"], anchor)
    if title: cv.text_px(W/2, 26, title, 15.5, C["text"], weight="700")
    if note: cv.text_px(W/2, H-18, note, 12.5, C["muted"])
    return cv.save(path)

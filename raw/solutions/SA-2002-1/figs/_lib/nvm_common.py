"""nvm_common — 靜定剛架軸力／剪力／彎矩圖（畫在構材旁），exam-wiki-SA 2026-11-05
每根構材給 p0→p1 與沿桿取樣的函數 f(s)->(N, V, M)；s 為距 p0 的長度。
彎矩正號＝桿軸「右手側」（由 p0 看向 p1 的右邊）受拉，圖一律畫在受拉側；
軸力、剪力正號也畫在右手側（水平梁可設 vup=True 讓正剪力畫在上方），圖上以 + / − 標記。數值全由呼叫端的函數算出。"""
import math
from structdraw import Canvas, C, compose

def _u(p0, p1):
    dx, dy = p1[0]-p0[0], p1[1]-p0[1]; L = math.hypot(dx, dy); return (dx/L, dy/L), L

def frame_panel(W, H, members, comp, scale, color, fill, title, unit, marks, supports=(), hinges=(),
                labels=None, fit_pad=(90, 90, 92, 70), n=120, fmt="{:.2f}", sign_marks=True):
    pts = [m['p0'] for m in members] + [m['p1'] for m in members]
    xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
    L_, R_, T_, B_ = fit_pad
    xr = (max(xs)-min(xs)) or 1; yr = (max(ys)-min(ys)) or 1
    sx = min((W-L_-R_)/xr, (H-T_-B_)/yr)
    ox = L_ + ((W-L_-R_) - xr*sx)/2 - min(xs)*sx; oy = B_ + ((H-T_-B_) - yr*sx)/2 - min(ys)*sx
    cv = Canvas(W, H, sx=sx, ox=ox, oy=oy)
    cv.panel(title, None)
    if unit: cv.text_px(W-22, 32, unit, 12, C["muted"], "end")
    for m in members:
        p0, p1 = m['p0'], m['p1']; d, L = _u(p0, p1); rn = (d[1], -d[0])   # 右手側法向
        if comp == 1 and m.get('vup'): rn = (-rn[0], -rn[1])            # 水平梁剪力圖：正值畫上方
        breaks = sorted(set([0.0, L] + list(m.get('breaks', []))))
        for a, b in zip(breaks[:-1], breaks[1:]):
            ss = [a + (b-a)*k/n for k in range(n+1)]
            ss[0] += 1e-9; ss[-1] -= 1e-9
            vals = [m['f'](s)[comp] for s in ss]
            if max(abs(v) for v in vals) < 1e-9: continue
            base = [(p0[0]+d[0]*s, p0[1]+d[1]*s) for s in ss]
            curve = [(bx+rn[0]*v*scale, by+rn[1]*v*scale) for (bx, by), v in zip(base, vals)]
            cv.polygon([base[0]] + curve + [base[-1]], fill, color, 2)
            if sign_marks:
                k = len(ss)//4; v = vals[k]
                q = (base[k][0]+rn[0]*v*scale*0.5, base[k][1]+rn[1]*v*scale*0.5)
                if abs(v)*scale*sx > 16:
                    cv.text_px(cv.X(q[0]), cv.Y(q[1]), "+" if v > 0 else "−", 15, color, weight="700")
        cv.line(p0, p1, C["member"], 4.2, cap="butt")
    for p, kind in supports: cv.support(p, kind, 0, 14)
    for p in hinges: cv.dot(p, 6.5, fill="#FFFFFF", stroke=C["member"], w=2.4)
    for nm, (p, dx, dy) in (labels or {}).items():
        cv.text_px(cv.X(p[0])+dx, cv.Y(p[1])+dy, nm, 14, C["text"], weight="700")
    for mi, s, txt, dx, dy in marks:
        m = members[mi]; d, L = _u(m['p0'], m['p1']); rn = (d[1], -d[0])
        if comp == 1 and m.get('vup'): rn = (-rn[0], -rn[1])
        s_ = min(max(s, 1e-9), L-1e-9); v = m['f'](s_)[comp]
        q = (m['p0'][0]+d[0]*s_+rn[0]*v*scale, m['p0'][1]+d[1]*s_+rn[1]*v*scale)
        cv.math_px(cv.X(q[0])+dx, cv.Y(q[1])+dy, txt, 13, color, weight="700")
    return cv

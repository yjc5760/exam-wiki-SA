import os
from structdraw import Canvas, C, FONT, FONT_M, column_shape, beam_shape

OUT = "/home/claude/figs"; os.makedirs(OUT, exist_ok=True)
MW = 7.0

def frame_members(cv, color=C["member"], w=MW, dash=None):
    cv.line((0,0),(0,1), color, w, dash=dash, cap="butt")
    cv.line((0,1),(1,1), color, w, dash=dash, cap="butt")
    cv.line((1,1),(1,0), color, w, dash=dash, cap="butt")

def ghost(cv):
    frame_members(cv, color=C["ghost"], w=3.0, dash="6 5")

# ═══ 圖1 題目重繪 ═══
def fig1():
    cv = Canvas(540, 430, sx=190, ox=155, oy=125, bg="#FFFFFF")
    frame_members(cv)
    cv.fixed_support((0,0)); cv.fixed_support((1,0))
    cv.arrow((1,1),(1.40,1), C["load"], 3.6, 12)
    cv.math((1.40,1), "P", 20, C["load"], "start", dx=10, weight="700")
    for p,lab,ax,ay in ((0,0),"A",-18,17),((0,1),"B",-18,-15),((1,1),"C",17,-15),((1,0),"D",18,17):
        cv.dot(p, 5.5); cv.text(p, lab, 17, C["text"], weight="700", dx=ax, dy=ay)
    cv.math((0.5,1), "EI", 17, C["muted"], dy=-17)
    cv.math((0,0.55), "EI", 17, C["muted"], "end", dx=-13)
    cv.math((1,0.55), "EI", 17, C["muted"], "start", dx=13)
    cv.dim((0,0),(1,0), "L", off=58, label_off=16)
    cv.dim((0,0),(0,1), "L", off=-62, label_off=-15)
    cv.text_px(270, 400, "所有桿件 EI、L 相同；柱底 A、D 固定；B、C 為剛接；忽略軸向變形",
               13.5, C["muted"])
    cv.save(f"{OUT}/SA-2025-1-fig-1-frame.svg")

# ═══ 圖2 自由度辨識 ═══
def fig2():
    cv = Canvas(770, 410, sx=185, ox=140, oy=108, bg="#FFFFFF")
    frame_members(cv, color="#9AA4B2")
    cv.fixed_support((0,0)); cv.fixed_support((1,0))
    # Δ
    cv.arrow((1.07,1),(1.42,1), C["deform"], 3.4, 12)
    cv.math((1.42,1), "Δ", 20, C["deform"], "start", dx=9, weight="700")
    # θB θC（順時針）
    for p, lx, ly in ((0,1), -46, -10), ((1,1), 40, 24):
        cv.moment_arrow(p, r=28, ccw=False, color=C["accent"], w=2.8, span=235, start=205)
        cv.text_px(cv.X(p[0])+lx, cv.Y(p[1])+ly, "θ_{B}" if p[0]==0 else "θ_{C}",
                   19, C["accent"], weight="700", italic=True, font=FONT_M)
    # 被消去之垂直自由度
    def cross(px, py, s=8, col="#C0392B"):
        cv.parts.append(f'<line x1="{px-s}" y1="{py-s}" x2="{px+s}" y2="{py+s}" stroke="{col}" stroke-width="2.6" stroke-linecap="round"/>')
        cv.parts.append(f'<line x1="{px-s}" y1="{py+s}" x2="{px+s}" y2="{py-s}" stroke="{col}" stroke-width="2.6" stroke-linecap="round"/>')
    for bx in (0,1):
        cv.arrow((bx,1.12),(bx,1.30), "#D6AEA6", 2.4, 8)
        cross(cv.X(bx)+17, cv.Y(1.21))
    for p,lab,ax,ay in ((0,0),"A",-18,17),((0,1),"B",20,20),((1,1),"C",-20,20),((1,0),"D",18,17):
        cv.dot(p, 5.5, fill="#4A5568"); cv.text(p, lab, 16, C["text"], weight="700", dx=ax, dy=ay)
    cv.rect_px(478, 92, 274, 74, "#EEF4FF", 12, "#C7D9F5", 1.3)
    cv.text_px(615, 116, "有效自由度只剩 3 個", 14.5, "#1D4ED8", weight="700")
    cv.text_px(615, 144, "{ θ_{B} ,  θ_{C} ,  Δ }", 19, "#1D4ED8", italic=True, font=FONT_M)
    cv.rect_px(478, 196, 274, 106, "#FFF6F1", 12, "#F0C9B8", 1.3)
    cv.text_px(496, 222, "被消去的自由度", 13.5, "#9A3412", "start", weight="700")
    for i, t in enumerate(["柱不縮短 → B、C 垂直位移 = 0",
                           "梁不伸縮 → B、C 水平位移相同",
                           "柱底全固定 → 不貢獻自由度"]):
        cross(504, 248+i*22, 6)
        cv.text_px(518, 248+i*22, t, 12.5, "#9A3412", "start")
    cv.text_px(385, 386, "自由度數目 = 勁度矩陣階數。這一步錯，後面整個矩陣都白算。",
               13.5, C["muted"])
    cv.save(f"{OUT}/SA-2025-1-fig-2-dof.svg")

# ═══ 圖3 勁度矩陣三行 ═══
def panel(tB, tC, dl, title, sub, mB, mBcw, mC, mCcw, hlab, hsgn, PW=362, PH=372):
    cv = Canvas(PW, PH, sx=150, ox=95, oy=92)
    cv.rect_px(6, 6, PW-12, PH-12, C["panel"], 14, "#E1E6ED", 1.2)
    ghost(cv)
    b, c = -tB, -tC
    cv.poly(column_shape((0,0),1.0,dl,b), C["deform"], 5.0)
    cv.poly(column_shape((1,0),1.0,dl,c), C["deform"], 5.0)
    cv.poly(beam_shape((dl,1),1.0,b,c), C["deform"], 5.0)
    cv.fixed_support((0,0), size=17); cv.fixed_support((1,0), size=17)
    cv.dot((dl,1), 4.5, fill=C["deform"]); cv.dot((1+dl,1), 4.5, fill=C["deform"])
    cv.text_px(PW/2, 32, title, 15.5, "#1F2733", weight="700")
    cv.text_px(PW/2, 55, sub, 12.5, C["muted"])
    cv.moment_arrow((dl,1), r=26, ccw=not mBcw, color=C["load"], w=2.8, span=235, start=205)
    cv.text_px(cv.X(dl)-48, cv.Y(1)-38, mB, 14, C["load"], weight="700", italic=True, font=FONT_M)
    cv.moment_arrow((1+dl,1), r=26, ccw=not mCcw, color=C["load"], w=2.8, span=235, start=205)
    cv.text_px(cv.X(1+dl)+6, cv.Y(1)-42, mC, 14, C["load"], "start", weight="700", italic=True, font=FONT_M)
    x0 = 1+dl
    a, b2 = (x0+0.10, x0+0.44) if hsgn > 0 else (x0+0.44, x0+0.10)
    cv.arrow((a,1),(b2,1), C["load"], 3.2, 11)
    cv.text_px(cv.X(x0+0.27), cv.Y(1)+24, hlab, 14, C["load"], weight="700", italic=True, font=FONT_M)
    return cv

def fig3():
    PW, PH = 362, 372
    ps = [panel(1,0,0, "狀態 ①：θ_B = 1（其餘鎖住）", "→ 勁度矩陣第 1 行",
                "8EI/L", True, "2EI/L", True, "−6EI/L^{2}", -1),
          panel(0,1,0, "狀態 ②：θ_C = 1（其餘鎖住）", "→ 勁度矩陣第 2 行",
                "2EI/L", True, "8EI/L", True, "−6EI/L^{2}", -1),
          panel(0,0,0.16, "狀態 ③：Δ = 1（B、C 不轉動）", "→ 勁度矩陣第 3 行",
                "−6EI/L^{2}", False, "−6EI/L^{2}", False, "24EI/L^{3}", +1)]
    W, H = PW*3, PH+112
    p = [f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
         f'<text x="{W/2}" y="34" font-family="{FONT}" font-size="17.5" fill="#1F2733" text-anchor="middle" font-weight="700">勁度矩陣的每一行 ＝ 令該自由度產生單位位移、其餘全部鎖住時，必須施加的節點力</text>',
         f'<text x="{W/2}" y="58" font-family="{FONT}" font-size="13" fill="{C["muted"]}" text-anchor="middle">符號約定：轉角與彎矩以順時針為正，Δ 與水平力以向右為正（與傾角變位法一致）</text>']
    for i, c in enumerate(ps):
        p.append(f'<g transform="translate({i*PW},76)">{"".join(c.parts)}</g>')
    p.append(f'<text x="{W/2}" y="{H-22}" font-family="{FONT}" font-size="13.5" fill="{C["muted"]}" text-anchor="middle">把三個狀態的節點力依序填成三行即為 [K]。灰虛線＝原結構，藍實線＝該狀態之變形，紅色＝為維持該狀態所需施加的力</text>')
    open(f"{OUT}/SA-2025-1-fig-3-unit-states.svg","w",encoding="utf-8").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(p)}</svg>')

# ═══ 圖4 變形形狀 + 彎矩圖 ═══
def fig4():
    PW, PH = 440, 410
    xi = 4/7
    a = Canvas(PW, PH, sx=172, ox=126, oy=96)
    a.rect_px(6,6,PW-12,PH-12, C["panel"], 14, "#E1E6ED", 1.2)
    ghost(a)
    D = 0.185; th = -0.6*D
    a.poly(column_shape((0,0),1.0,D,th), C["deform"], 5.4)
    a.poly(column_shape((1,0),1.0,D,th), C["deform"], 5.4)
    a.poly(beam_shape((D,1),1.0,th,th), C["deform"], 5.4)
    a.fixed_support((0,0), size=18); a.fixed_support((1,0), size=18)
    u = D*(2.4*xi**2 - 1.4*xi**3)
    for bx in (0,1):
        a.dot((bx+u, xi), 5.4, fill="#FFFFFF", stroke=C["accent"], w=2.9)
    a.dot((D+0.5,1), 5.4, fill="#FFFFFF", stroke=C["accent"], w=2.9)
    a.text_px(a.X(u)+16, a.Y(xi), "4L/7", 13, C["accent"], "start", weight="700", italic=True, font=FONT_M)
    a.text_px(a.X(D+0.5), a.Y(1)+24, "L/2", 13, C["accent"], weight="700", italic=True, font=FONT_M)
    a.arrow((1+D,1),(1+D+0.30,1), C["load"], 3.4, 12)
    a.math((1+D+0.30,1), "P", 18, C["load"], "start", dx=8, weight="700")
    a.text_px(PW/2, 32, "變形形狀（側移模式）", 15.5, "#1F2733", weight="700")
    a.text_px(PW/2, 55, "柱：雙曲率　梁：反對稱雙曲率", 12.5, C["muted"])
    a.text_px(PW/2, 352, "○ ＝ 反曲點（M = 0）", 13, C["accent"], weight="700")
    a.text_px(PW/2, 382, "Δ = 5PL^{3}/84EI 　 θ_{B} = θ_{C} = PL^{2}/28EI", 14.5,
              C["deform"], weight="700", italic=True, font=FONT_M)

    b = Canvas(PW, PH, sx=172, ox=126, oy=96)
    b.rect_px(6,6,PW-12,PH-12, C["panel"], 14, "#E1E6ED", 1.2)
    ms = 0.60; Mb, Mt = 2/7*ms, 3/14*ms
    for bx in (0,1):
        b.polygon([(bx,0),(bx-Mb,0),(bx,xi)], C["bmdfill"], C["bmd"], 2)
        b.polygon([(bx,xi),(bx+Mt,1),(bx,1)], C["bmdfill"], C["bmd"], 2)
    b.polygon([(0,1),(0,1-Mt),(0.5,1)], C["bmdfill"], C["bmd"], 2)
    b.polygon([(0.5,1),(1,1+Mt),(1,1)], C["bmdfill"], C["bmd"], 2)
    frame_members(b, color="#4A5568", w=3.4)
    b.fixed_support((0,0), size=18); b.fixed_support((1,0), size=18)
    b.dot((0.5,1), 4.6, fill="#FFFFFF", stroke=C["bmd"], w=2.6)
    b.text_px(b.X(-Mb)-6, b.Y(0.02), "2PL/7", 13, C["bmd"], "end", weight="700", italic=True, font=FONT_M)
    b.text_px(b.X(1+Mt)+6, b.Y(0.97), "3PL/14", 13, C["bmd"], "start", weight="700", italic=True, font=FONT_M)
    b.text_px(b.X(0.5), b.Y(1+Mt)-16, "梁中點 M = 0", 12.5, C["bmd"], weight="700")
    b.text_px(PW/2, 32, "彎矩圖（繪於受拉側）", 15.5, "#1F2733", weight="700")
    b.text_px(PW/2, 55, "節點彎矩平衡與樓層剪力檢核", 12.5, C["muted"])
    b.text_px(PW/2, 352, "M_{BA} + M_{BC} = 0 ✓", 13, C["bmd"], weight="700", italic=True, font=FONT_M)
    b.text_px(PW/2, 382, "每柱剪力 = (2PL/7 + 3PL/14)/L = P/2 → 兩柱合計 = P ✓", 13.5,
              C["bmd"], weight="700")

    W, H = PW*2, PH+48
    p = [f'<rect width="{W}" height="{H}" fill="#FFFFFF"/>',
         f'<text x="{W/2}" y="30" font-family="{FONT}" font-size="17.5" fill="#1F2733" text-anchor="middle" font-weight="700">解出 Δ 之後：用幾何與平衡回頭檢核答案</text>',
         f'<g transform="translate(0,44)">{"".join(a.parts)}</g>',
         f'<g transform="translate({PW},44)">{"".join(b.parts)}</g>']
    open(f"{OUT}/SA-2025-1-fig-4-deflected-bmd.svg","w",encoding="utf-8").write(
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">{"".join(p)}</svg>')

# ═══ 圖5 側向勁度光譜 ═══
def fig5():
    W, H = 1020, 400
    cv = Canvas(W, H, sx=1, bg="#FFFFFF")
    cv.text_px(W/2, 32, "靜態凝縮做了什麼？——梁的束縛能力決定側向勁度折減多少", 17.5, "#1F2733", weight="700")
    cv.text_px(W/2, 57, "旋轉自由度被凝縮掉，代價就是 K_{33} 被扣掉一項；梁越軟，扣得越多", 13, C["muted"])
    cases = [("梁無限剛　EI_{b} → ∞", "θ_{B} = θ_{C} = 0", 24.0, "24EI/L^{3}", "100%", "#1D4ED8"),
             ("本題　梁柱同 EI/L", "θ = 3Δ/5L", 16.8, "84EI/5L^{3} = 16.8EI/L^{3}", "70%", "#B45309"),
             ("梁無勁度　EI_{b} → 0", "兩根獨立懸臂柱", 6.0, "6EI/L^{3}", "25%", "#94A3B8")]
    x0, bw = 320, 400
    for i,(name,note,val,expr,pct,col) in enumerate(cases):
        y = 122 + i*86
        mc = Canvas(1,1, sx=44, ox=32, oy=14); mc.h = 74
        D = 0.30; th = {24.0:0.0, 16.8:-0.6*D, 6.0:-1.5*D}[val]
        for s,e in (((0,0),(0,1)),((0,1),(1,1)),((1,1),(1,0))):
            mc.line(s,e, C["ghost"], 2.2, dash="4 4", cap="butt")
        mc.poly(column_shape((0,0),1.0,D,th), col, 3.2)
        mc.poly(column_shape((1,0),1.0,D,th), col, 3.2)
        mc.poly(beam_shape((D,1),1.0,th,th), col, 3.2)
        cv.parts.append(f'<g transform="translate(20,{y-38})">{"".join(mc.parts)}</g>')
        cv.text_px(150, y-9, name, 14, "#1F2733", "start", weight="700")
        cv.text_px(150, y+14, note, 12.5, C["muted"], "start")
        w = bw*val/24.0
        cv.rect_px(x0, y-17, bw, 34, "#EDF1F6", 8)
        cv.rect_px(x0, y-17, w, 34, col, 8)
        cv.text_px(x0+w-14, y, pct, 14, "#FFFFFF", "end", weight="700")
        cv.text_px(x0+bw+16, y, expr, 14.5, col, "start", weight="700", italic=True, font=FONT_M)
    cv.text_px(W/2, 372, "本題被扣掉的 −36EI/5L^{3} 就是「節點被允許旋轉」所付的勁度代價，不是計算誤差",
               13.5, C["muted"])
    cv.save(f"{OUT}/SA-2025-1-fig-5-stiffness-spectrum.svg")

for f in (fig1, fig2, fig3, fig4, fig5): f()
print("ok")

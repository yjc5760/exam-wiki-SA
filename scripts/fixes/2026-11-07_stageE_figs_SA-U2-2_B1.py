"""SA-U2-2 批 1 階段 E：把解題圖產生函式插入 8 支 gen_<id>.py（在 `if __name__` 前），可重複執行（已插入者略過）。
SA-2009-1 不在本批（解析斜桿畫錯，待勘誤後再補）。
用法：python3 2026-11-07_stageE_figs_SA-U2-2_B1.py <raw/solutions 目錄>"""
import os, re, sys
ROOT = sys.argv[1]

# ── 剛架題共用：frameviz 小補丁（支承可帶角度、二力桿畫直線）與自動倍率 ──
FRAME_COMMON = '''
def _auto_scales(f, span, dfrac=0.12, mfrac=0.17):
    """依解出的位移與彎矩自動取放大倍率（圖形隨輸入改變，不寫死）。"""
    from frameviz import member_moment
    dmax = max(max(abs(v[0]), abs(v[1])) for v in f.d.values()) or 1
    mmax = max(abs(member_moment(f, m, k/40)) for m in f.M for k in range(41)) or 1
    return dfrac*span/dmax, mfrac*span/mmax

def _frame_tools():
    """回傳 frame2d.Frame。並對 frameviz 打兩個本地補丁：
    ① supports 可寫 (節點, 種類, 角度)，牆上鉸支承才畫得對；② 兩端皆鉸、無跨內載重的二力桿，變形畫成直線。"""
    import frameviz
    from frame2d import Frame
    if not getattr(frameviz, "_patch_U22", False):
        _ds, _df = frameviz.draw_supports, frameviz.deformed
        def draw_supports(cv, N, members, supports, size=18):
            _ds(cv, N, members, [s for s in supports if len(s) == 2], size)
            for nd, kind, ang in [s for s in supports if len(s) == 3]:
                cv.support(N[nd], kind, ang, size*0.85)
        def deformed(f, m, scale, n=40):
            if tuple(m["rel"]) == (1, 1) and m["w"] == 0:
                (x0, y0), (x1, y1) = f.N[m["i"]], f.N[m["j"]]; ui, uj = f.d[m["i"]], f.d[m["j"]]
                return [(x0 + (x1-x0)*k/n + (ui[0] + (uj[0]-ui[0])*k/n)*scale,
                         y0 + (y1-y0)*k/n + (ui[1] + (uj[1]-ui[1])*k/n)*scale) for k in range(n + 1)]
            return _df(f, m, scale, n)
        frameviz.draw_supports, frameviz.deformed, frameviz._patch_U22 = draw_supports, deformed, True
    return Frame
'''

# ── 桁架題共用：全節點平衡檢查（含反力），殘差須為 0 才畫 ──
TRUSS_COMMON = '''
class _Fmt:
    """桿力標籤：零桿顯示 0，其餘帶正負號兩位小數。"""
    def format(self, N):
        return "0" if abs(N) < 1e-9 else f"{N:+.2f}"
FMT = _Fmt()

def _truss(nodes, members, **kw):
    """recipes.truss_forces 的包裝：垂直桿的桿力標籤原本置中在桿旁 17 px，文字會壓到桿件；
    這裡暫時包住 Canvas.math_px，把落在垂直桿上的標籤推到桿件外側（依文字長度），其餘不動。"""
    from structdraw import Canvas
    from recipes import truss_forces
    orig = Canvas.math_px
    verts = [(nodes[i], nodes[j]) for i, j, _ in members if abs(nodes[i][0] - nodes[j][0]) < 1e-9]
    def math_px(self, x, y, s, *a, **k):
        for p, q in verts:
            xm = self.X(p[0]); y0, y1 = sorted((self.Y(p[1]), self.Y(q[1])))
            if abs(x - xm) < 22 and y0 < y < y1:
                x = xm + (1 if x >= xm else -1)*(len(s)*4.6 + 10)
        return orig(self, x, y, s, *a, **k)
    Canvas.math_px = math_px
    try:
        return truss_forces(nodes, members, **kw)
    finally:
        Canvas.math_px = orig
def _truss_check(nodes, F, ext):
    """F: {(i, j): N}（拉＋）；ext: {節點: (Fx, Fy)}（外力＋反力）。每個節點 ΣF = 0。"""
    R = {n: [0.0, 0.0] for n in nodes}
    for (i, j), f in F.items():
        (xi, yi), (xj, yj) = nodes[i], nodes[j]; L = math.hypot(xj-xi, yj-yi)
        R[i][0] += f*(xj-xi)/L; R[i][1] += f*(yj-yi)/L; R[j][0] -= f*(xj-xi)/L; R[j][1] -= f*(yj-yi)/L
    for n, (fx, fy) in ext.items():
        R[n][0] += fx; R[n][1] += fy
    assert max(abs(v) for n in R for v in R[n]) < 1e-9, R
'''

SNIP = {}

SNIP["SA-2016-1"] = FRAME_COMMON + '''
# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2016-1.md §4 Step 5–7 ──
from frameviz import solution_figure, end_moments, inflections
SOL = dict(nodes=SPEC["nodes"], supports=[("A", "pin"), ("E", "fixed")], hinges=["C"])

def fig2_solution():
    Frame = _frame_tools(); f = Frame()
    for n, p in SOL["nodes"].items(): f.node(n, *p)
    f.support("A", 1, 1, 0); f.support("E", 1, 1, 1)
    f.member("AB", "A", "B", 1.0); f.member("BC", "B", "C", 1.0, rel=(0, 1))     # C 內鉸
    f.member("CD", "C", "D", 1.0); f.member("ED", "E", "D", 1.0)
    f.load("D", 50, 0, 0); f.solve(); M = end_moments(f)
    assert abs(f.R["A"][0] + 12.5) < 1e-6 and abs(f.R["A"][1] + 12.5) < 1e-6      # §4：A_x = A_y = −12.5
    assert abs(f.R["E"][0] + 37.5) < 1e-6 and abs(f.R["E"][1] - 12.5) < 1e-6      # E_x = −37.5、E_y = +12.5
    assert abs(f.R["E"][2] - 50) < 1e-6                                          # M_E = 50 逆時針
    assert abs(abs(M["AB"][1]) - 25) < 1e-6 and abs(abs(M["CD"][1]) - 25) < 1e-6   # M_B = M_D = 25
    xi = inflections(f, next(m for m in f.M if m["name"] == "ED"))
    assert len(xi) == 1 and abs(xi[0] - 2/3) < 1e-2                              # 反曲點距 E 4/3 m
    ds, ms = _auto_scales(f, 4)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2016-1 變形形狀與彎矩圖（單位 kN·m）", "D 向右側移；C 內鉸兩側斜率不連續",
        "B：柱右、梁下受拉；D：梁上、柱右受拉；E：柱左受拉", fmt="{:.1f}", W=560, H=470,
        notes=("", "DE 柱反曲點距 D 0.67 m；A 反力 12.5 ←、12.5 ↓"))

FIGURES.append((fig2_solution, "B、D、E 受拉側畫反；DE 柱漏畫反曲點；E 當成鉸支承（M_E = 0）"))
'''

SNIP["SA-2014-2"] = FRAME_COMMON + '''
# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2014-2.md §4（T = 34560/503、R_B = 11628/503、M_A = −25776/503）──
from frameviz import solution_figure, end_moments, member_moment
SOL = dict(nodes=SPEC["nodes"], supports=[("A", "fixed"), ("B", "roller"), ("C", "pin", -90)])

def fig2_solution():
    Frame = _frame_tools(); f = Frame()
    for n, p in SOL["nodes"].items(): f.node(n, *p)
    f.support("A", 1, 1, 1); f.support("B", 0, 1, 0); f.support("C", 1, 1, 0)
    f.member("AD", "A", "D", 1e4, w=8); f.member("DB", "D", "B", 1e4, w=8)      # 梁軸向不計（frame2d 預設 EA→∞）
    f.member("CD", "C", "D", 1e-6, rel=(1, 1), EA=4e4)                            # 斜桿 CD，7.5 m
    f.solve(); M = end_moments(f)
    assert abs(-f.end["CD"][0] - 34560/503) < 1e-6                                # T = 68.71 kN（拉）
    assert abs(f.R["B"][1] - 11628/503) < 1e-6                                    # R_B = 23.12 kN
    assert abs(M["AD"][0] + 25776/503) < 1e-6 or abs(abs(M["AD"][0]) - 25776/503) < 1e-6   # |M_A| = 51.24
    ad = next(m for m in f.M if m["name"] == "AD"); db = next(m for m in f.M if m["name"] == "DB")
    assert abs(member_moment(f, ad, 3.957/6) - 11.39) < 0.01                     # §4：x = 3.957 m，+11.39
    assert abs(member_moment(f, db, (9.110 - 6)/6) - 33.40) < 0.01               # §4：x = 9.110 m，+33.40
    ds, ms = _auto_scales(f, 12)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2014-2 變形形狀與彎矩圖（單位 kN·m）", "D 下沉、斜桿 CD 受拉伸長；A 固接不轉",
        "|M|max = 51.24 在 A（上緣受拉）", fmt="{:.1f}", W=600, H=440, skip_mark=(("AD", 1.0), ("DB", 0.0)),
        notes=("", "正彎矩：AD 段 11.39（x = 3.96 m）、DB 段 33.40（x = 9.11 m）"), extra_pts_m=[(-0.8, 5.2)])

FIGURES.append((fig2_solution, "CD 畫成垂直桿；最大彎矩放在跨中（實為固接端 A）；漏掉 AD 段兩個、DB 段一個反曲點"))
'''

SNIP["SA-2009-2"] = FRAME_COMMON + '''
# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2009-2.md §4.3–4.4（X_1 = 75/26、Δ_b = −1161/6500 m）──
# 連桿 100 m 未按比例：沿用題目重繪圖的 LINK 長度，EA 等比縮小，使 AE/L = 1000/100 = 10 kN/m 不變。
from frameviz import solution_figure
SOL = dict(nodes={"c": (0, 0), "b": (0, 6), "a": (0, 10), "d": (LINK, 10)}, supports=[("c", "fixed"), ("d", "pin", 90)])

def fig2_solution():
    Frame = _frame_tools(); f = Frame()
    for n, p in SOL["nodes"].items(): f.node(n, *p)
    f.support("c", 1, 1, 1); f.support("d", 1, 1, 0)
    f.member("cb", "c", "b", 1000, w=-1); f.member("ba", "b", "a", 1000, w=-1)   # 局部 −y＝右，w = −1 即向左 1 kN/m
    f.member("ad", "a", "d", 1e-6, rel=(1, 1), EA=1000*LINK/100)                  # 等效：AE/L = 10 kN/m
    f.solve()
    X1 = 75/26
    assert abs(-f.end["ad"][0] - X1) < 1e-9                                       # 連桿拉力 X_1 = 75/26
    assert abs(f.d["b"][0] + 1161/6500) < 1e-9                                    # Δ_b = 0.1786 m 向左
    assert abs(f.d["a"][0] + X1/10) < 1e-9                                        # a 向左 = 連桿伸長 X_1/10
    ds, ms = _auto_scales(f, 10)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2009-2 變形形狀與彎矩圖（單位 kN·m）", "Δb = 0.1786 m 向左；連桿未按比例（AE/L = 10 kN/m 不變）",
        "c 端受彎最大；a 端連桿只受軸力", fmt="{:.2f}", W=520, H=480,
        notes=("", "連桿拉力 X1 = 75/26 = 2.885 kN"))

FIGURES.append((fig2_solution, "b 點位移方向畫反（向右）；連桿當成受壓"))
'''

SNIP["SA-2006-2"] = FRAME_COMMON + '''
# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2006-2.md §4（T_DB = 86990/7917、T_DC = 80635/15834）──
from frameviz import solution_figure
SOL = dict(nodes=SPEC["nodes"], supports=[("A", "pin", -90), ("D", "pin", -90)])

def fig2_solution():
    Frame = _frame_tools(); f = Frame()
    for n, p in SOL["nodes"].items(): f.node(n, *p)
    f.support("A", 1, 1, 0); f.support("D", 1, 1, 0)
    f.member("AB", "A", "B", 1.0, w=1); f.member("BC", "B", "C", 1.0, w=1)       # 梁在 B 連續；不計軸向
    f.member("DB", "D", "B", 1e-6, rel=(1, 1), EA=1.0); f.member("DC", "D", "C", 1e-6, rel=(1, 1), EA=1.0)
    f.solve()
    assert abs(-f.end["DB"][0] - 86990/7917) < 1e-6                              # T_DB = 10.988 kN
    assert abs(-f.end["DC"][0] - 80635/15834) < 1e-6                             # T_DC = 5.093 kN
    ds, ms = _auto_scales(f, 16)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2006-2 變形形狀與彎矩圖（單位 kN·m）", "兩連桿皆受拉伸長；梁在 B 連續",
        "B 處負彎矩（上緣受拉），不是內鉸", fmt="{:.2f}", W=600, H=470,
        notes=("", "連桿拉力：DB 10.99 kN、DC 5.093 kN"))

FIGURES.append((fig2_solution, "B 當成梁內鉸（結構變靜定）；兩根連桿拉力對調"))
'''

SNIP["SA-2007-1"] = TRUSS_COMMON + '''
# ── 解題圖（階段 E，2026-11-07）：桿力與反力取自 SA-2007-1.md §4 Step 5–6（X = F_DE = 1890/72）──
from recipes import truss_forces
X7 = 1890/72
F7 = {("A", "D"): 4/3*X7, ("D", "E"): X7, ("D", "B"): -5/3*X7, ("B", "E"): 100 - 5/3*X7, ("E", "C"): -80 + 4/3*X7}
R7 = {"A": (0, -35), "B": (-60, -10), "C": (0, 45)}

def fig2_truss():
    _truss_check(N_, F7, {**R7, "E": (60, 0)})
    cv = _truss(N_, [(i, j, v) for (i, j), v in F7.items()],
                        supports=[("A", "pin", 0), ("B", "pin", 0), ("C", "pin", 0)],
                        loads=[], fmt=FMT,
                        title=f"圖 2　{TAG} 桿力（kN，拉＋）",
                        note="反力：A 35↓；B 60←、10↓；C 45↑（A、C 只接垂直桿，水平反力為 0，60 kN 全由 B 承擔）",
                        path=None, W=760, H=560)
    E = N_["E"]; cv.arrow((E[0] + 0.25, E[1]), (E[0] + 1.6, E[1]), C["load"], 3.4, 12)      # 60 kN 自 E 向右（不與 DE 重疊）
    cv.math_px(cv.X(E[0] + 0.95), cv.Y(E[1]) - 16, "60 kN", 16, C["load"], weight="700")
    cv.save(f"{OUT}/{TAG}-fig-2-truss.svg")
    return f"{OUT}/{TAG}-fig-2-truss.svg"

FIGURES.append((fig2_truss, "A、C 也分擔水平反力；B 的水平反力方向畫反"))
'''

SNIP["SA-2008-1"] = TRUSS_COMMON + '''
# ── 解題圖（階段 E，2026-11-07）：桿力與反力取自 SA-2008-1.md §4 步驟 5（X = D_x = (175√5 − 95)/44）──
from recipes import truss_forces
R5 = math.sqrt(5); X8 = (175*R5 - 95)/44
F8 = {("A", "C"): 10 - X8, ("C", "E"): 10 - X8, ("A", "B"): -5*R5 + 0.5*R5*X8, ("B", "C"): 0.0,
      ("B", "E"): -5*R5, ("B", "D"): 0.5*R5*X8, ("D", "E"): -0.5*X8}
R8 = {"A": (0, 5 - 0.5*X8), "D": (X8, 0), "E": (-X8, 5 + 0.5*X8)}

def fig2_truss():
    _truss_check(N_, F8, {**R8, "B": (0, -10)})
    _truss(N_, [(i, j, v) for (i, j), v in F8.items()],
                        supports=[("A", "roller", 0), ("E", "pin", 0), ("D", "roller", 90)],
                        loads=[("B", (0, -2.4), "10 kN")], fmt=FMT,
                        title=f"圖 2　{TAG} 桿力（kN，拉＋）",
                        note="反力：A_y 1.63↑；D_x 6.73→（牆對 D 為拉力）；E_x 6.73←、E_y 8.37↑。CB 為零桿（C 點無垂直力）",
                        path=f"{OUT}/{TAG}-fig-2-truss.svg", W=760, H=560)
    return f"{OUT}/{TAG}-fig-2-truss.svg"

FIGURES.append((fig2_truss, "CB 當成受力桿；D_x 方向畫成向左（受壓）"))
'''

SNIP["SA-2011-1"] = TRUSS_COMMON + '''
# ── 解題圖（階段 E，2026-11-07）：取自 SA-2011-1.md §4 Step 1、3（無外載，基本結構桿力為 0；N = u·X）──
from recipes import truss_forces
X11 = (-0.0285 + 0.016296)/0.000134375                     # Step 3：X = −90.82 kN（A 水平反力，向右為正）
U11 = {("A", "B"): -1/2, ("B", "C"): -1/2, ("D", "E"): 1, ("E", "F"): 0, ("A", "D"): 3/8, ("B", "E"): 0,
       ("C", "F"): -3/8, ("A", "E"): -5/8, ("C", "E"): 5/8}
F11 = {k: u*X11 for k, u in U11.items()}
R11 = {"A": (X11, 0), "D": (-X11, -3/8*X11), "F": (0, 3/8*X11)}

def fig2_truss():
    _truss_check(N_, F11, R11)
    _truss(N_, [(i, j, v) for (i, j), v in F11.items()],
                        supports=[("A", "roller", -90), ("D", "pin", 0), ("F", "roller", 0)],
                        loads=[], fmt=FMT,
                        title=f"圖 2　{TAG} 桿力（kN，拉＋）—— 只由溫度、製造誤差與支承偏位引起",
                        note="反力：A_x 90.82←、D_x 90.82→、D_y 34.06↑、F_y 34.06↓。BE（升溫）、EF（短 1 cm）有初始變形，仍是零桿",
                        path=f"{OUT}/{TAG}-fig-2-truss.svg", W=760, H=520)
    return f"{OUT}/{TAG}-fig-2-truss.svg"

FIGURES.append((fig2_truss, "有溫度或製造誤差的桿（BE、EF）就以為一定受力；A 偏左的符號弄反"))
'''

SNIP["SA-2023-2"] = TRUSS_COMMON + '''
# ── 解題圖（階段 E，2026-11-07）：取自 SA-2023-2.md §4 Step 2–4（S、u 表與 X = F_BD）──
from recipes import truss_forces
R41 = math.sqrt(41); X23 = -(25625 - 1895*R41)/328
S23 = {("A", "B"): 22.5, ("B", "C"): -37.5, ("A", "C"): 7.5*R41, ("D", "C"): -60, ("A", "D"): -100, ("B", "D"): 0}
U23 = {("A", "B"): -2/R41, ("B", "C"): -5/R41, ("A", "C"): 1, ("D", "C"): -8/R41, ("A", "D"): -5/R41, ("B", "D"): 1}
F23 = {k: S23[k] + U23[k]*X23 for k in S23}

def fig2_truss():
    _truss_check(N_, F23, {"A": (0, -50), "D": (0, 80), "B": (0, -30)})
    assert abs(F23[("B", "D")] + 41.13) < 0.005                                   # boxed：41.13 kN 壓力
    _truss(N_, [(i, j, v) for (i, j), v in F23.items()],
                        supports=[("A", "pin", -90), ("D", "roller", 0)],
                        loads=[("B", (0, -1.4), "30 kN")], fmt=FMT,
                        title=f"圖 2　{TAG} 桿力（kN，拉＋）",
                        note="AC 與 BD 交叉處不是節點，兩桿各自受力；BD 受壓 41.13 kN。反力 A_y 50↓、D_y 80↑、A_x 0",
                        path=f"{OUT}/{TAG}-fig-2-truss.svg", W=700, H=560)
    return f"{OUT}/{TAG}-fig-2-truss.svg"

FIGURES.append((fig2_truss, "交叉點當成節點；BD 標成受拉"))
'''

for tag, code in SNIP.items():
    p = os.path.join(ROOT, tag, f"gen_{tag}.py")
    t = open(p, encoding="utf-8").read()
    if "階段 E" in t:
        print("skip", tag); continue
    key = '\nif __name__ == "__main__":'
    assert t.count(key) == 1, tag
    if not re.search(r"^import [^\n]*\bmath\b", t, re.M):
        t = t.replace("import sys, os", "import sys, os, math", 1)
    t = t.replace(key, code + key)
    open(p, "w", encoding="utf-8").write(t)
    print("inserted", tag)

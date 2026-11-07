"""階段 E 修圖：2013-2 副標題、2018-3 纜索改虛線、2022-1 內鉸位置與彈簧、兩張桁架圖標籤位置。"""
import os, sys, re
ROOT = sys.argv[1]

def sub(tag, old, new, count=1):
    p = os.path.join(ROOT, tag, f"gen_{tag}.py"); t = open(p, encoding="utf-8").read()
    assert t.count(old) == count, (tag, old[:60], t.count(old))
    t = t.replace(old, new); open(p, "w", encoding="utf-8").write(t)

# ── 2013-2：B 沒有水平位移 ──
sub("SA-2013-2", '"C 端逆時針轉 625/(7EI)；B 角向右移"', '"C 端逆時針轉 625/(7EI)；BC 不伸縮，B 無水平位移"')
sub("SA-2013-2", '    assert abs(f.d["C"][2] - 625/7) < 1e-4                                     # θ_C·EI，逆時針為正',
    '    assert abs(f.d["C"][2] - 625/7) < 1e-4                                     # θ_C·EI，逆時針為正\n'
    '    assert abs(f.d["B"][0]) < 1e-3*abs(f.d["C"][2])                            # B 無水平位移（副標題依據）')

# ── 2018-3：纜索不進勁度模型，改以解得的 T_BF 作用於 B；圖上另畫虛線纜索 ──
p = os.path.join(ROOT, "SA-2018-3", "gen_SA-2018-3.py"); t = open(p, encoding="utf-8").read()
a = t.index("T_BF = 3750/53"); b = t.index("FIGURES.append((fig2_solution")
t = t[:a] + '''T_BF = 3750/53                                   # §2.2（AE 鬆弛，X_1 = 0）
EA_C, L_C = 500.0, 5.0
SOL = dict(nodes={k: N_[k] for k in "ABCDG"},
           members=[dict(name="AB", ij=("A", "B"), EI=1000), dict(name="BC", ij=("B", "C"), EI=1000),
                    dict(name="CD", ij=("C", "D"), EI=1000), dict(name="GC", ij=("G", "C"), EI=1000)],
           supports=[("G", "fixed")],
           fe_loads=[("D", 0, -100, 0), ("B", 0, -T_BF, 0)])      # 纜索 BF 拉力向下拉住 B

def _with_cables(f, ds):
    """把 frameviz 的 compose 暫時換掉：兩個面板都補畫虛線纜索與 E、F 錨碇。"""
    import frameviz
    orig = frameviz.compose
    def wrapped(panels, **kw):
        a, b = panels
        for cv, deformed_panel in ((a, True), (b, False)):
            for top, bot, ok in (("A", "E", False), ("B", "F", True)):
                pt = N_[top]
                if deformed_panel:
                    pt = (pt[0] + f.d[top][0]*ds, pt[1] + f.d[top][1]*ds)
                col = C["tension"] if ok else C["muted"]
                cv.line(N_[bot], pt, col, 2.6, dash="7 6")
                cv.fixed_support(N_[bot], 0, 15)
            if deformed_panel:
                cv.text(N_["E"], "AE 鬆弛", 13, C["muted"], weight="700", dx=-6, dy=-150)
                cv.text(N_["F"], "BF 受拉", 13, C["tension"], weight="700", dx=40, dy=-60)
        frameviz.compose = orig
        return orig(panels, **kw)
    frameviz.compose = wrapped

def fig2_solution():
    f = build_frame(SOL); M = end_moments(f)
    assert abs(f.d["B"][1] - T_BF*L_C/EA_C) < 1e-6           # 相容：B 上移量＝BF 伸長量 T·L/EA
    assert f.d["A"][1] < 0                                    # A 下移 → AE 縮短 → 鬆弛（§2.3）
    assert abs(abs(M["BC"][1]) - 5*T_BF) < 1e-6 and abs(abs(M["CD"][0]) - 500) < 1e-6
    ds, ms = _auto_scales(f, 15)
    _with_cables(f, ds)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2018-3 變形形狀與彎矩圖（單位 kN·m）", "A 下移→AE 縮短而鬆弛；B 上移→BF 受拉 70.75 kN",
        "梁全長上緣受拉；柱 CG 承擔差額 146.2", fmt="{:.1f}", W=600, H=460,
        notes=("", "虛線＝纜索（只受拉、不受彎）；AB 段彎矩 0"))

''' + t[b:]
open(p, "w", encoding="utf-8").write(t)

# ── 2022-1：內鉸畫在變形後位置，補畫彈簧與 e 點 ──
p = os.path.join(ROOT, "SA-2022-1", "gen_SA-2022-1.py"); t = open(p, encoding="utf-8").read()
t = t.replace('''           supports=[("d", "roller"), ("a", "fixed")], hinges=["b"],''',
              '''           supports=[("d", "roller"), ("a", "fixed")],''')
old = '''    ds, ms = _auto_scales(f, 15)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-3-deflected-bmd.svg", ds, ms,'''
assert t.count(old) == 1
t = t.replace(old, '''    ds, ms = _auto_scales(f, 15)
    _with_spring(f, ds, de_mm/1000)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-3-deflected-bmd.svg", ds, ms,''')
t = t.replace('''        notes=("", "內鉸 b 彎矩為零、斜率不連續"))''',
              '''        notes=("", "內鉸 b 彎矩為零、斜率不連續"), extra_pts_m=[(5, -SPRING_L - 0.4)])''')
helper = '''
SPRING_L = 2.2                                   # 圖上彈簧長度（示意，模型單位 m）

def _with_spring(f, ds, de):
    """補畫：變形後位置的內鉸 b、彈簧 c–e（e 沉陷 de）；彎矩圖面板畫原位置的內鉸。"""
    import frameviz
    orig = frameviz.compose
    def wrapped(panels, **kw):
        a, b = panels
        cx, cy = N_["c"][0], N_["c"][1] + f.d["c"][1]*ds
        ey = -SPRING_L - de*ds
        zz = [(cx, cy)] + [(cx + (0.22 if k % 2 else -0.22), cy + (ey - cy)*(0.15 + 0.7*k/9)) for k in range(10)] + [(cx, ey)]
        a.poly(zz, C["member"], 2.2)
        a.line((cx - 0.55, ey), (cx + 0.55, ey), C["member"], 2.6)
        a.line((cx - 0.55, -SPRING_L), (cx + 0.55, -SPRING_L), C["ghost"], 2.0, dash="5 4")
        a.text((cx, ey), "e", 14, C["text"], weight="700", dx=-22, dy=6)
        a.text((cx, (cy + ey)/2), "k", 14, C["text"], weight="700", dx=-28)
        pb = (N_["b"][0], N_["b"][1] + f.d["b"][1]*ds)
        a.dot(pb, 6, fill="#FFFFFF", stroke=C["deform"], w=2.4)
        a.text(pb, "內鉸 b", 13, C["deform"], weight="700", dy=26)
        b.dot(N_["b"], 6, fill="#FFFFFF", stroke="#4A5568", w=2.4)
        frameviz.compose = orig
        return orig(panels, **kw)
    frameviz.compose = wrapped
'''
t = t.replace("\ndef fig3_solution():", helper + "\ndef fig3_solution():")
open(p, "w", encoding="utf-8").write(t)

# ── 桁架圖：標籤改由腳本放在空白處（不壓粗線） ──
LBL = '''
def _labels(cv, forces, spec, unit_fmt="{:+.2f}"):
    """spec: {(i, j): (t, dx_px, dy_px, anchor)}；t 為自 i 起的桿長比例。"""
    for (i, j), (tt, dx, dy, anc) in spec.items():
        f = forces[(i, j)]; p0, p1 = N_[i], N_[j]
        x, y = p0[0] + (p1[0]-p0[0])*tt, p0[1] + (p1[1]-p0[1])*tt
        col = C["tension"] if f > 0 else C["compr"]
        cv.math_px(cv.X(x) + dx, cv.Y(y) + dy, unit_fmt.format(f).replace("-", "\\u2212"), 14, col, anc, weight="700")
'''
p = os.path.join(ROOT, "SA-2005-4", "gen_SA-2005-4.py"); t = open(p, encoding="utf-8").read()
t = t.replace("\ndef fig2_truss():", LBL + "\ndef fig2_truss():")
t = t.replace('loads=[], fmt="{:+.2f}", title=f"圖 2　{TAG} 桿力（N，拉＋）與應力",', 'loads=[], fmt="", title=f"圖 2　{TAG} 桿力（N，拉＋）與應力",')
t = t.replace('''    D = N_["D"]; cv.arrow(''', '''    _labels(cv, F4, {("A", "C"): (0.5, -14, 0, "end"), ("B", "D"): (0.5, 14, 0, "start"),
                     ("C", "D"): (0.5, 0, -16, "middle"), ("A", "D"): (0.22, 16, 6, "start"),
                     ("B", "C"): (0.22, -16, 6, "end")})
    D = N_["D"]; cv.arrow(''')
open(p, "w", encoding="utf-8").write(t)

p = os.path.join(ROOT, "SA-2012-2", "gen_SA-2012-2.py"); t = open(p, encoding="utf-8").read()
t = t.replace("\ndef fig2_truss():", LBL + "\ndef fig2_truss():")
old = '''    return truss_forces(N_, [(i, j, f) for (i, j), f in F2.items()],
                        supports=[("a", "pin", 0), ("c", "roller", 0)],
                        loads=[("d", (0, -1.3), "40 kN"), ("d", (1.4, 0), "20 kN"), ("b", (0, 1.3), f"S = {S:.2f} kN")],
                        fmt="{:+.2f}",'''
assert t.count(old) == 1
t = t.replace(old, '''    cv = truss_forces(N_, [(i, j, f) for (i, j), f in F2.items()],
                        supports=[("a", "pin", 0), ("c", "roller", 0)],
                        loads=[("d", (0, -1.3), "40 kN"), ("d", (1.4, 0), "20 kN"), ("b", (0, 1.3), "")],
                        fmt="",''')
old2 = '''                        path=f"{OUT}/{TAG}-fig-2-truss.svg", W=720, H=600) and f"{OUT}/{TAG}-fig-2-truss.svg"'''
assert t.count(old2) == 1
t = t.replace(old2, '''                        path=None, W=720, H=600)
    _labels(cv, F2, {("a", "d"): (0.5, -12, -8, "end"), ("d", "c"): (0.5, 12, -8, "start"),
                     ("d", "b"): (0.55, 12, 0, "start"), ("a", "b"): (0.5, 0, -16, "middle"),
                     ("b", "c"): (0.5, 0, -16, "middle")})
    cv.math_px(cv.X(4) + 12, cv.Y(-0.75), f"S = {S:.2f} kN", 15, C["load"], "start", weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-2-truss.svg")''')
open(p, "w", encoding="utf-8").write(t)
print("patched")

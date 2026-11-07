"""把階段 E 的解題圖產生函式插入 7 支 gen_<id>.py（在 `if __name__` 前），只執行一次。"""
import os, sys
ROOT = sys.argv[1]

AUTO = '''
def _auto_scales(f, span, dfrac=0.12, mfrac=0.17):
    """依解出的位移與彎矩自動取放大倍率（圖形隨輸入改變，不寫死）。"""
    from frameviz import member_moment
    dmax = max(max(abs(v[0]), abs(v[1])) for v in f.d.values()) or 1
    mmax = max(abs(member_moment(f, m, k/40)) for m in f.M for k in range(41)) or 1
    return dfrac*span/dmax, mfrac*span/mmax
'''

SNIP = {}

SNIP["SA-2005-1"] = AUTO + '''
# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2005-1.md §4 Step 4–5 ──
from frameviz import solution_figure, build_frame, end_moments
RC = 10*(2 - math.sqrt(2))                     # §4 Step 4：R_C = 10(2−√2) N
SOL = dict(nodes=N_, members=[dict(name="BA", ij=("B", "A"), EI=1), dict(name="CB", ij=("C", "B"), EI=1)],
           supports=[("A", "fixed"), ("C", "roller")], fe_loads=[("B", 0, -10, 0)])

def fig2_solution():
    f = build_frame(SOL); M = end_moments(f)
    assert abs(f.R["C"][1] - RC) < 1e-6                      # §4：R_C
    assert abs(abs(M["BA"][1]) - 40*math.sqrt(2)) < 1e-6     # §4：A 端 40√2 N·m
    assert abs(abs(M["BA"][0]) - 40*(2 - math.sqrt(2))) < 1e-6
    ds, ms = _auto_scales(f, 8)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2005-1 變形形狀與彎矩圖（單位 N·m）", "C 滾支水平滑動；B 下沉並轉動",
        "BA 全長上緣受拉；BC 外側受拉", fmt="{:.2f}", W=560, H=460,
        notes=("", "R_C = 10(2 − √2) = 5.86 N"))

FIGURES.append((fig2_solution, "BA 在 x = 4 處分段、BC 受拉側畫反"))
'''

SNIP["SA-2008-3"] = AUTO + '''
# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2008-3.md §4 步驟 3–4 ──
from frameviz import solution_figure, build_frame, end_moments
RA = 3888/529                                    # §4 步驟 3
SOL = dict(nodes=N_, members=[dict(name="AB", ij=("A", "B"), EI=1, w=2), dict(name="BC", ij=("B", "C"), EI=1)],
           supports=[("A", "roller"), ("C", "fixed")])

def fig2_solution():
    f = build_frame(SOL); M = end_moments(f)
    assert abs(f.R["A"][1] - RA) < 1e-6                       # R_A = 3888/529
    assert abs(abs(M["AB"][1]) - 4284/529) < 1e-6             # M_B = 4284/529
    assert abs(abs(M["BC"][1]) - 6786/529) < 1e-6             # M_C = 6786/529
    ds, ms = _auto_scales(f, 10.5)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2008-3 變形形狀與彎矩圖（單位 kN·m）", "C 無水平反力；BC 只受垂直力",
        "B 角內側受拉、C 端外側受拉", fmt="{:.2f}", W=560, H=470,
        notes=("", "R_A = 3888/529 = 7.35 kN；AB 最大 13.50 @ x = 3.675 m"))

FIGURES.append((fig2_solution, "M_B 受拉側畫反、BC 漏畫反曲點、AB 最大彎矩位置錯"))
'''

SNIP["SA-2013-2"] = AUTO + '''
# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2013-2.md §4（C_x = 45/14 向左、C_y = 55/7、θ_C = 625/(7EI) 逆時針）──
from frameviz import solution_figure, build_frame, end_moments
SOL = dict(nodes=N_, members=[dict(name="AB", ij=("A", "B"), EI=1), dict(name="BP", ij=("B", "P"), EI=1),
                              dict(name="PC", ij=("P", "C"), EI=1)],
           supports=[("A", "fixed"), ("C", "pin")], fe_loads=[("P", 0, -20, 0)])

def fig2_solution():
    f = build_frame(SOL)
    assert abs(f.R["C"][0] + 45/14) < 1e-6 and abs(f.R["C"][1] - 55/7) < 1e-6   # C 反力
    assert abs(f.d["C"][2] - 625/7) < 1e-4                                     # θ_C·EI，逆時針為正
    ds, ms = _auto_scales(f, 10)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2013-2 變形形狀與彎矩圖（單位 kN·m）", "C 端逆時針轉 625/(7EI)；B 角向右移",
        "A 端 10.71、B 角 21.43、載重點 39.29", fmt="{:.2f}", W=540, H=470,
        notes=("θ_C = 625/(7EI)", "C 反力：45/14 = 3.21 kN 向左、55/7 = 7.86 kN 向上"))

FIGURES.append((fig2_solution, "θ_C 轉向寫反、C 水平反力方向寫反"))
'''

SNIP["SA-2018-3"] = AUTO + '''
# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2018-3.md §2（X_2 = 3750/53 kN、AE 鬆弛）──
from frameviz import solution_figure, build_frame, end_moments
T_BF = 3750/53                                   # §2.2
SOL = dict(nodes=N_, members=[dict(name="AB", ij=("A", "B"), EI=1000), dict(name="BC", ij=("B", "C"), EI=1000),
                              dict(name="CD", ij=("C", "D"), EI=1000), dict(name="GC", ij=("G", "C"), EI=1000),
                              dict(name="FB", ij=("F", "B"), EI=1e-6, rel=(1, 1), EA=500),        # 纜索 BF（EA = 500）
                              dict(name="EA", ij=("E", "A"), EI=1e-6, rel=(1, 1), EA=1e-6)],      # 纜索 AE：鬆弛，不傳力
           supports=[("G", "fixed"), ("E", "fixed"), ("F", "fixed")], fe_loads=[("D", 0, -100, 0)])

def fig2_solution():
    f = build_frame(SOL); M = end_moments(f)
    assert abs(-f.end["FB"][0] - T_BF) < 1e-3                 # BF 拉力 3750/53
    assert f.d["A"][1] < 0                                    # A 下移 → AE 縮短 → 鬆弛（驗證 §2.3）
    assert abs(abs(M["BC"][1]) - 5*T_BF) < 1e-3 and abs(abs(M["CD"][0]) - 500) < 1e-6
    ds, ms = _auto_scales(f, 15)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-2-deflected-bmd.svg", ds, ms,
        "圖 2　SA-2018-3 變形形狀與彎矩圖（單位 kN·m）", "A 下移→AE 縮短而鬆弛；B 上移→BF 受拉 70.75 kN",
        "梁全長上緣受拉；柱 CG 承擔差額 146.2", fmt="{:.1f}", W=600, H=460,
        notes=("", "AB 段 0；C 左 353.8、C 右 500；纜索不受彎"))

FIGURES.append((fig2_solution, "把 AE 當成可受壓的桿件（兩索都計入）"))
'''

SNIP["SA-2022-1"] = AUTO + '''
# ── 解題圖（階段 E，2026-11-07）：數值取自 SA-2022-1.md §4 Step 1–4 ──
# 彈簧以 §4 Step 2 解得的彈簧力 F_s = 24 kN（向上）作用於 c 代入，結構其餘部分照原樣建模。
from frameviz import solution_figure, build_frame, end_moments
FS, EI = 24.0, 250000.0
SOL = dict(nodes=N_, members=[dict(name="dc", ij=("d", "c"), EI=EI), dict(name="cb", ij=("c", "b"), EI=EI, rel=(0, 1)),
                              dict(name="ba", ij=("b", "a"), EI=EI)],
           supports=[("d", "roller"), ("a", "fixed")], hinges=["b"],
           fe_loads=[("c", 0, -72 + FS, 0), ("b", 0, -72, 0)])

def fig3_solution():
    f = build_frame(SOL); M = end_moments(f)
    assert abs(f.d["b"][1] + 0.016) < 1e-9 and abs(f.d["c"][1] + 0.012) < 1e-9   # Δ_b = 16 mm、Δ_c = 12 mm
    assert abs(abs(f.R["a"][2]) - 480) < 1e-6 and abs(f.R["d"][1] - 24) < 1e-9    # 與題給彎矩圖一致
    dc_mm = -f.d["c"][1]*1000; de_mm = dc_mm - FS/6000*1000                          # Δ_e = Δ_c − F_s/k
    assert abs(de_mm - 8) < 1e-9
    ds, ms = _auto_scales(f, 15)
    return solution_figure(f, SOL, f"{OUT}/{TAG}-fig-3-deflected-bmd.svg", ds, ms,
        "圖 3　SA-2022-1 變形形狀與彎矩圖（彈簧以 F_s = 24 kN 代入）",
        f"b 下沉 16 mm、c 下沉 {dc_mm:.0f} mm；彈簧縮 4 mm → e 沉陷 {de_mm:.0f} mm",
        "M_c = +120、M_a = −480（與題給圖一致）", fmt="{:.0f}", W=600, H=430,
        notes=("", "內鉸 b 彎矩為零、斜率不連續"))

FIGURES.append((fig3_solution, "c 點位移當成 e 點沉陷、內鉸處畫成連續斜率"))
'''

SNIP["SA-2005-4"] = '''
# ── 解題圖（階段 E，2026-11-07）：桿力取自 SA-2005-4.md §4 最終表（N，拉＋）──
from recipes import truss_forces
F4 = {("A", "C"): 224/15, ("B", "D"): -256/15, ("C", "D"): 56/5, ("A", "D"): 64/3, ("B", "C"): -56/3}
AREA = 10.0                                      # cm²

def _check4():
    """自由節點 C、D 平衡殘差須為 0（D 受 24 N 向右）。"""
    R = {n: [0.0, 0.0] for n in N_}
    for (i, j), f in F4.items():
        (xi, yi), (xj, yj) = N_[i], N_[j]; L = math.hypot(xj-xi, yj-yi)
        R[i][0] += f*(xj-xi)/L; R[i][1] += f*(yj-yi)/L; R[j][0] -= f*(xj-xi)/L; R[j][1] -= f*(yj-yi)/L
    R["D"][0] += 24
    assert max(abs(v) for n in ("C", "D") for v in R[n]) < 1e-9

def fig2_truss():
    _check4()
    cv = truss_forces(N_, [(i, j, f) for (i, j), f in F4.items()], supports=[("A", "pin", 0), ("B", "pin", 0)],
                      loads=[], fmt="{:+.2f}", title=f"圖 2　{TAG} 桿力（N，拉＋）與應力",
                      note="應力 ＝ 內力 ÷ 10 cm²：AC +1.49、BD −1.71、CD +1.12、AD +2.13、BC −1.87 N/cm²",
                      path=None, W=680, H=640)
    D = N_["D"]; cv.arrow(D, (D[0] + 1.5, D[1]), C["load"], 3.4, 12)
    cv.math_px(cv.X(D[0] + 1.5) + 8, cv.Y(D[1]) - 16, "24 N", 16, C["load"], weight="700")
    return cv.save(f"{OUT}/{TAG}-fig-2-truss.svg")

FIGURES.append((fig2_truss, "兩斜桿交叉處當成節點、CD 當零桿、只求內力不換成應力"))
'''

SNIP["SA-2012-2"] = '''
# ── 解題圖（階段 E，2026-11-07）：桿力取自 SA-2012-2.md §4 步驟 5（kN，拉＋）──
from recipes import truss_forces
R2 = math.sqrt(2)
S = (280*R2 - 20)/17                             # 彈簧力（向上）
F2 = {("a", "d"): (280 - 180*R2)/17, ("d", "c"): (280 - 520*R2)/17, ("d", "b"): (20 - 280*R2)/17,
      ("a", "b"): (520 - 140*R2)/17, ("b", "c"): (520 - 140*R2)/17}

def _check2():
    """自由節點 b、d 平衡殘差須為 0（b 受彈簧力 S 向上；d 受 20 kN→、40 kN↓）。"""
    R = {n: [0.0, 0.0] for n in N_}
    for (i, j), f in F2.items():
        (xi, yi), (xj, yj) = N_[i], N_[j]; L = math.hypot(xj-xi, yj-yi)
        R[i][0] += f*(xj-xi)/L; R[i][1] += f*(yj-yi)/L; R[j][0] -= f*(xj-xi)/L; R[j][1] -= f*(yj-yi)/L
    R["b"][1] += S; R["d"][0] += 20; R["d"][1] -= 40
    assert max(abs(v) for n in ("b", "d") for v in R[n]) < 1e-9

def fig2_truss():
    _check2()
    return truss_forces(N_, [(i, j, f) for (i, j), f in F2.items()],
                        supports=[("a", "pin", 0), ("c", "roller", 0)],
                        loads=[("d", (0, -1.3), "40 kN"), ("d", (1.4, 0), "20 kN"), ("b", (0, 1.3), f"S = {S:.2f} kN")],
                        fmt="{:+.2f}", title=f"圖 2　{TAG} 桿力（kN，拉＋）與彈簧力",
                        note="b 點向上箭頭＝彈簧對桁架的力 S = (280√2 − 20)/17（彈簧受壓、b 下沉 8.85 mm）",
                        path=f"{OUT}/{TAG}-fig-2-truss.svg", W=720, H=600)

FIGURES.append((fig2_truss, "漏計彈簧（把 b 當固定或自由）、db 豎桿當零桿"))
'''

for tag, code in SNIP.items():
    p = os.path.join(ROOT, tag, f"gen_{tag}.py")
    t = open(p, encoding="utf-8").read()
    if "階段 E" in t:
        print("skip", tag); continue
    key = '\nif __name__ == "__main__":'
    assert t.count(key) == 1, tag
    import re
    if not re.search(r"^import [^\n]*\bmath\b", t, re.M):
        t = t.replace("import sys, os", "import sys, os, math", 1)
    t = t.replace(key, code + key)
    open(p, "w", encoding="utf-8").write(t)
    print("inserted", tag)

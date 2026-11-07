#!/usr/bin/env python3
"""SA-U2-2 批 1 題目正本確認（2026-11-07，關卡一通過）
1. 9 份 problem.md：待確認 → 已確認；question_index.json problemStatus draft → confirmed
2. 8 題解析 §1 改為指向題目正本＋重繪附圖＋常見誤讀＋本解記號（SA-2014-2 另以勘誤整份改寫，不在此處理）
可重複執行：已處理者略過。用法：python3 scripts/fixes/2026-11-07_confirm_sec1_SA-U2-2_B1.py [repo 根目錄]"""
import sys, os, re, json
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = "2026-11-07"
IDS = ["SA-2002-3", "SA-2006-2", "SA-2007-1", "SA-2008-1", "SA-2009-1", "SA-2009-2", "SA-2011-1", "SA-2014-2", "SA-2023-2"]
CHOICE = {"SA-2014-2": "影響答案項目定案：#3、#5、#6 CD 為斜桿 7.5 m（C 在 A 正上方，使用者確認；解析同日勘誤）。"}

def rd(p): return open(p, encoding="utf-8").read()
def wr(p, s): open(p, "w", encoding="utf-8", newline="\n").write(s)

# ── 1. 題目正本 ──
for i in IDS:
    p = f"{ROOT}/raw/solutions/{i}/{i}-problem.md"; s = rd(p)
    if "**已確認**" in s: print("skip problem", i); continue
    assert "| 判讀狀態 | **待確認**（" in s, i
    s = s.replace("| 判讀狀態 | **待確認**（", f"| 判讀狀態 | **已確認**（{D} 使用者確認；{CHOICE.get(i, '')}原轉錄：", 1)
    s = re.sub(r"\| (確定（解讀）|不確定（解讀）[^|]*) \|\n", lambda m: f"| {m.group(1)}；使用者確認 |\n", s)
    assert s.rstrip().endswith("批 1）*"), i
    s = s.rstrip() + f"\n*確認：{D} 使用者確認*\n"
    wr(p, s); print("confirmed", i)

# ── 1b. 索引 ──
qp = f"{ROOT}/raw/json/question_index.json"; q = rd(qp)
for i in IDS:
    m = re.search(r'"moduleId":\s*"%s"' % i, q); assert m
    nxt = re.search(r'"moduleId":', q[m.end():]); end = m.end() + (nxt.start() if nxt else len(q) - m.end())
    seg = q[m.start():end]
    if '"problemStatus": "confirmed"' in seg: continue
    assert '"problemStatus": "draft"' in seg, i
    q = q[:m.start()] + seg.replace('"problemStatus": "draft"', '"problemStatus": "confirmed"') + q[end:]
json.loads(q); wr(qp, q)

# ── 2. 解析 §1 ──
HEAD = """## 1. 題目（考卷原文見題目正本）

> 考卷原文、公式／附表、附圖與判讀清單（已確認）見 [`{i}-problem.md`]({i}-problem.md)。本節只列解題時最容易讀錯的地方與本解使用的記號；題意以題目正本為準。

![{i} 重繪題目附圖：{alt}](figs/{i}-fig-1-problem.svg)
*重繪自考卷附圖，依判讀清單重繪。攔：{catch}。*

### 常見誤讀
| 項目 | 正確判讀 | 常見誤讀 |
|---|---|---|
{rows}

**本解記號：** {nota}

"""
S1 = {
"SA-2002-3": dict(alt="水平梁 AB 長 λ，A 固定端；B 以鉸接連垂直桿 BC（長 λ），C 鉸支承吊於上方；B 點受 P 向下",
  catch="C 讀成固定端、B 讀成剛接、漏掉桿的軸向變形",
  rows=[("C 支承", "鉸支承（三角形倒掛）", "固定端，或寫成「鉸接或固定端皆可」"),
        ("B 點", "梁端與桿以鉸連接，桿為二力構件", "梁、桿剛接"),
        ("材料", "梁與桿同材料（同一 E）；EI、AE 各為常數，無數值", "假設 EI、AE 數值")],
  nota="梁 AB 長 λ、撓曲剛度 EI；桿 BC 長 λ、軸向剛度 AE；T＝桿拉力；B 點位移向下為正。"),
"SA-2006-2": dict(alt="梁 AC 長 16 m（AB 9 m、BC 7 m），A 鉸接於牆；D 在 A 正上方 12 m 鉸接於同一面牆，連桿 DB、DC；梁全長 1 kN/m",
  catch="B 讀成梁內鉸（變靜定）、D 不在 A 正上方、均佈只算到 B",
  rows=[("D 位置", "A 正上方 12 m，與 A 同一面牆", "D 在 B 或 C 上方"),
        ("B 點", "連桿鉸，梁 AC 在 B 連續（一度靜不定）", "梁內鉸（結構變靜定）"),
        ("載重", "1 kN/m 作用 A 至 C 全長", "只作用 AB 段")],
  nota="DB 長 15 m（sin = 0.8）、DC 長 20 m（sin = 0.6）；EI = 1 kN-m²、AE = 1 kN；贅力 X＝V_C（DC 對梁 C 點的垂直分力，向上）；連桿張力以拉為正；位移向下為正。"),
"SA-2007-1": dict(alt="桁架 A、B、C 在地面鉸支承（A–B、B–C 各 4.5 m），D、E 在 A、C 正上方 6 m；桿 AD、DE、DB、BE、EC；E 點 60 kN 向右",
  catch="支承讀成滾支承（變靜定）、漏掉 B 點兩斜桿交會",
  rows=[("支承", "A、B、C 三個鉸支承（6 個反力）", "其中一個讀成滾支承"),
        ("桿件", "5 根：AD、DE、DB、BE、EC", "多補 A–B、B–C 下弦"),
        ("靜不定度", "m＋r＝11 ＞ 2j＝10，一度", "判為靜定")],
  nota="DB、BE 長 7.5 m（4.5／7.5 = 0.6、6／7.5 = 0.8）；A＝1000 mm²、E＝200 GPa；桿力拉為正。"),
"SA-2008-1": dict(alt="三角形桁架：A(0,0)、C(10,0)、E(20,0)、B(10,5)、D(20,10)；A 滾支承、E 鉸支承、D 滾支承靠右側牆；B 點 10 kN 向下",
  catch="D 讀成垂直反力、E 讀成滾支承",
  rows=[("D 支承", "滾支承靠右側直立牆 → 水平反力", "垂直反力"),
        ("A 支承", "地面滾支承 → 垂直反力", "鉸支承"),
        ("上弦", "A、B、D 共線（斜率 1/2）", "B 不在 AD 線上")],
  nota="座標以 A 為原點（m）；D_x 為贅力（向右為正）；E、A 為常數；桿力拉為正。"),
"SA-2009-1": dict(alt="桁架 a(0,0)、e(4,0)、d(8,0)、b(4,3)、c(8,3)，桿 ab、bc、be、ec、cd、ae、ed；a 地面滾支承，c 鉸支承、d 滾支承皆靠右側牆",
  catch="d 讀成垂直反力、c 讀成滾支承、漏掉 a–b 桿",
  rows=[("d 支承", "滾支承靠右側牆 → 水平反力", "垂直反力"),
        ("c 支承", "鉸支承靠右側牆 → 水平＋垂直反力", "滾支承"),
        ("桿 a–b", "連到 b（考卷圖上有繪圖缺口）", "漏掉此桿"),
        ("作用", "只有 a 向下沉陷 0.1 m，無外加載重", "另加載重")],
  nota="座標以 a 為原點（m）；AE＝10⁴ kN；贅力 X₁＝d 點水平反力；支承沉陷 Δa＝−0.1 m（向下）。"),
"SA-2009-2": dict(alt="垂直梁 ac 高 10 m，c 固定端；b 在 c 上方 6 m；a 頂以鉸接水平連桿 ad（100 m，圖未按比例），d 鉸接於右側牆；梁全高 1 kN/m 向左",
  catch="載重方向讀反、b 讀成鉸、b 高度量錯",
  rows=[("載重方向", "水平向左（背離 d），作用 c 至 a 全高", "向右"),
        ("b 點", "梁上一點（實心點），距 c 6 m", "梁內鉸，或距 a 6 m"),
        ("連桿", "水平，長 100 m，AE＝1000 kN", "忽略連桿變形")],
  nota="梁 ac：L＝10 m、EI＝1000 kN-m²；連桿 ad：100 m、AE＝1000 kN；w＝1 kN/m（←）；y 自 c 向上量；贅力 X₁＝連桿拉力（對梁 a 點向右）；水平位移向右為正。"),
"SA-2011-1": dict(alt="矩形桁架：上弦 A–B–C、下弦 D–E–F 各 4 m，高 3 m，斜桿 AE、CE；A 滾支承靠左側牆、D 鉸支承、F 地面滾支承",
  catch="A 讀成鉸支承、支承位置誤差方向讀錯",
  rows=[("A 支承", "滾支承靠左側直立牆 → 只約束水平", "鉸支承"),
        ("F 支承", "地面滾支承 → 只約束垂直", "鉸支承"),
        ("支承誤差", "A 偏左 2.4 cm（水平）、F 偏低 1.2 cm（垂直），各沿該支承約束方向", "方向對調")],
  nota="座標以 D 為原點（m）；EA＝8×10⁴ kN；α＝1.08×10⁻⁵／℃；贅力 X＝A 點水平反力（向右為正）；支承位移 ΔAx＝−2.4 cm、ΔFy＝−1.2 cm。"),
"SA-2023-2": dict(alt="桁架 A(0,0)、B(8,0)、D(3,−4)、C(5,−4)，桿 AB、AD、AC、BD、BC、DC，AC 與 BD 交叉不相連；A 鉸支承於左牆、D 滾支承；B 點 30 kN 向下",
  catch="交叉點當成節點、D 讀成鉸支承",
  rows=[("交叉處", "AC 與 BD 交叉不相連（無節點）", "當成節點"),
        ("支承", "A 鉸支承（2）、D 滾支承（1）", "D 讀成鉸支承"),
        ("幾何", "AD、BC 長 5 m；AC、BD 長 √41 m；DC 2 m", "AC、BD 長度算錯")],
  nota="座標以 A 為原點（m，向上為正）；EA＝200,000 kN；以 BD 桿力為多餘力 X；桿力拉為正。"),
}
FOOT = {
"SA-2002-3": "、刪除「C 點鉸接或固定端皆可」的保留語（考卷為鉸支承）",
"SA-2008-1": "、刪除圖說佔位字",
"SA-2009-1": "（舊版未引用證據圖）",
}
for i, v in S1.items():
    p = f"{ROOT}/raw/solutions/{i}/{i}.md"; s = rd(p)
    if "## 1. 題目（考卷原文見題目正本）" in s: print("skip sec1", i); continue
    m = re.search(r"^## 1\. .*?(?=^## 2\. )", s, flags=re.S | re.M); assert m, i
    old = m.group(0); prob = rd(f"{ROOT}/raw/solutions/{i}/{i}-problem.md")
    for png in re.findall(r"\(([^)]+\.png)\)", old):
        assert png in prob, (i, png)                       # 舊 §1 的證據圖已在題目正本
    assert not re.search(r"figs/[^)]+\.svg", old), i         # 舊 §1 沒有解析自繪向量圖
    rows = "\n".join(f"| {a} | {b} | {c} |" for a, b, c in v["rows"])
    new = HEAD.format(i=i, alt=v["alt"], catch=v["catch"], rows=rows, nota=v["nota"])
    s = s[:m.start()] + new + s[m.end():]
    s = s.rstrip() + (f"\n\n*修正日期：{D}（§1 改為指向題目正本並放重繪附圖（figs/{i}-fig-1-problem.svg）、加常見誤讀{FOOT.get(i, '')}；"
                      f"圖由 gen_{i}.py 產生，可重跑）*\n")
    wr(p, s); print("sec1", i)
assert "## 1. 題目（考卷原文見題目正本）" in rd(f"{ROOT}/raw/solutions/SA-2014-2/SA-2014-2.md"), "SA-2014-2 勘誤版尚未寫入"
print("done")

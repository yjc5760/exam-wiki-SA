#!/usr/bin/env python3
"""SA 剩餘單元批 1 題目正本確認（2026-11-07，關卡一通過）
範圍：U1-2 尾段 SA-2016-4、2017-1、2023-1、2024-1、2024-2；U2-5 SA-2003-1、2006-3；U3-1 SA-2017-4；
      U3-2 SA-2018-1、2019-2、2020-4、2021-4、2023-4
1. 13 份 problem.md：待確認 → 已確認；question_index.json problemStatus draft → confirmed
2. 10 題解析 §1 改為指向題目正本＋重繪附圖＋常見誤讀＋本解記號
   （SA-2017-1、SA-2021-4、SA-2017-4 已於同日勘誤時整段改寫 §1，此處略過）
可重複執行：已處理者略過。用法：python3 scripts/fixes/2026-11-07_confirm_sec1_SA-REST_B1.py [repo 根目錄]"""
import sys, os, re, json
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
D = "2026-11-07"
IDS = ["SA-2003-1", "SA-2006-3", "SA-2016-4", "SA-2017-1", "SA-2017-4", "SA-2018-1", "SA-2019-2",
       "SA-2020-4", "SA-2021-4", "SA-2023-1", "SA-2023-4", "SA-2024-1", "SA-2024-2"]
CHOICE = {
    "SA-2017-1": "影響答案項目定案：#3、#5 桿件為 AB、BC、BD、AD、CD、DE，無 AC、BE（使用者確認；解析同日勘誤）。",
    "SA-2021-4": "影響答案項目定案：#2 EI_d＝9720、EI_e＝48600 kN-m²（使用者確認；解析同日勘誤）。",
    "SA-2017-4": "影響答案項目定案：#1–#3 (a) 牆位置與方向、#7 (c) 中央開口核心（使用者確認；解析同日勘誤）。",
}
ERRATA_DONE = {"SA-2017-1", "SA-2021-4", "SA-2017-4"}

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
{selfdraw}
### 常見誤讀
| 項目 | 正確判讀 | 常見誤讀 |
|---|---|---|
{rows}

**本解記號：** {nota}

"""
S1 = {
"SA-2003-1": dict(alt="三跨連續梁 a–b–c–d 各 30 ft，a、d 固定端，b、c 中間支承；ab、cd 跨中各 8 k，bc 跨滿佈 1 k/ft 並於三分點各 3 k",
  catch="3 k 放到跨中、均佈只畫半跨、a、d 讀成鉸支承",
  rows=[("b、c 支承", "梁下支承，符號為半圓頂，鉸或滾無法區分；只有垂直載重、不計軸向，對答案無影響", "一定要分出鉸或滾"),
        ("bc 跨 3 k", "兩個 3 k 分別在距 b 10 ft、20 ft（三分點）", "放在跨中"),
        ("a、d 端", "固定端", "鉸支承（漏算固定端彎矩）")],
  nota="跨長 L＝30 ft；EI 常數；FEM 以順時針作用於桿端為正；k＝kip。"),
"SA-2006-3": dict(alt="五跨連續梁 A–F（6、8、4、8、6 m），A 鉸、B～F 滾支承；A 端 5 kN-m 順時針、F 端 5 kN-m 逆時針；BC、DE 跨 1.2 kN/m",
  catch="兩端外加彎矩方向讀反、均佈放錯跨",
  rows=[("A、F 端外加彎矩", "A 順時針、F 逆時針，兩者鏡射對稱", "同向（變反對稱）"),
        ("均佈範圍", "BC、DE 兩跨滿佈；CD、AB、EF 無均佈", "全梁均佈"),
        ("對稱性", "幾何、支承與載重對 CD 跨中點對稱，可取半結構", "—")],
  nota="跨長 $L_1$～$L_5$ = 6、8、4、8、6 m；EI 常數；彎矩以順時針作用於桿端為正（彎矩分配法慣例）；精度取至 0.1 kN-m。"),
"SA-2016-4": dict(alt="左側桁架（A、C 頂部鉸支、D 鉸支，F–G–I–J 與 I–J–K–L 兩格交叉斜桿），L–P、N–P 連到右側 MNO 梁（M 鉸、O 滾），H、M 以彈簧 k 相連；A、D 各 100 kN 向右，E、N 各 100 kN 向下",
  catch="把 E 點載重讀到 I 點、把交叉斜桿的交點當成節點",
  rows=[("向下載重", "只有 E、N 兩處；「100 kN」字樣在 E 點箭頭下端、靠近 I，但 I 點沒有載重", "E、I、N 三處都有載重"),
        ("交叉斜桿", "F–J 與 G–I、I–L 與 J–K 交叉處沒有節點，互不相連", "交點當成節點"),
        ("NP 桿", "N 為梁上節點，NP、LP 在 P 點只接兩根桿", "—")],
  nota="零桿＝在圖示載重下內力為零的桿件；本題不需數值計算（考卷沒有尺寸）。"),
"SA-2018-1": dict(alt="8 層樓，兩側單跨構架以兩端鉸接連桿連到中央貫通全高的剪力牆，各樓層左側受 F 向右",
  catch="把連桿當成剛接（可傳彎矩）、以為外力直接作用在剪力牆",
  rows=[("連桿", "兩端鉸接，只傳軸力（水平力）", "剛接，可傳彎矩"),
        ("勁度比 5 倍", "剪力牆提供的樓層水平勁度為構架的 5 倍（整體平均比）", "每層固定按 5:1 分配外力"),
        ("尺寸", "考卷沒有尺寸，只要示意圖", "自行假設樓高、跨度去精算")],
  nota="F＝各樓層外力；構架以剪力型變形、剪力牆以彎曲型變形為主；樓層水平力分布圖以虛線畫外力 F 作比例基準。"),
"SA-2019-2": dict(alt="四格范倫迪爾桁架：下弦 A–E、上弦 F–J，格寬 4 m、高 6 m，全部剛接；A 鉸支承、E 滾支承；B、C、D 各 100 kN 向下",
  catch="把載重放在上弦、支承型式讀反",
  rows=[("載重位置", "B、C、D 下弦節點各 100 kN 向下", "作用在上弦 G、H、I"),
        ("支承", "A 鉸支承、E 滾支承", "兩端皆鉸"),
        ("反曲點", "題目指定：所有構件反曲點在中點", "只假設弦桿反曲點")],
  nota="格寬 4 m、高 6 m；$R_A$、$R_E$ 為支承反力（向上為正）；各格剪力由上、下弦平分。"),
"SA-2020-4": dict(alt="(a) 二層單跨構架（a、b、d、e、g、h；層高與跨度 3.2 m，梁 I＝∞）以兩端鉸接連桿 bc、ef 連到剪力牆，各層 60 kN 向右；(b) 剪力牆兩個自由度 Δ₁,F₁（頂層）、Δ₂,F₂（一樓）",
  catch="Δ₁、Δ₂ 的樓層對調、把連桿當成可傳彎矩",
  rows=[("剪力牆自由度", "1 號在頂層、2 號在一樓", "1 號在一樓"),
        ("柱 EI", "81920 kN-m²（「m²」的 2 是單位指數）", "讀成 2EI"),
        ("柱底", "g、h 視為固定（圖面無支承符號；使用者確認）", "鉸支")],
  nota="構架節點 a、b、d、e、g、h，ab、de 為剛性梁；柱高 3.2 m；連桿軸力 $N_{bc}$、$N_{ef}$ 以拉為正；位移、力向右為正。"),
"SA-2023-1": dict(alt="水平梁 A–E（2、4、4、2 m），B 滾支承、D 鉸支承，C 處剛接 4 m 高的柱 CF，F 受水平力 P 向右",
  catch="B、D 支承型式對調、CF 位置不在 C",
  rows=[("支承", "B 滾支承、D 鉸支承（靜定）", "對調"),
        ("CF 與梁", "於 C 剛接（T 形）", "鉸接"),
        ("D 下陷", "3 mm 向下，靜定結構只產生剛體位移", "—")],
  nota="EI＝20,000 kN-m²；位移向下為正；P 向右為正；座標以 A 為原點。"),
"SA-2023-4": dict(alt="三層偏心斜撐構架：寬 4＋0.6＋4 m、層高各 4 m；每層斜撐自下緣兩角連到上方梁中央，留 0.6 m 連梁（連梁1～3）；上角三角形為剛性區域；各樓板兩端各標 300、450、600 kN 向右",
  catch="連梁位置放錯樓層、剛性區域畫成下方三角形",
  rows=[("連梁編號", "連梁1 在一樓梁、連梁2 在二樓梁、連梁3 在屋頂梁", "連梁 i 在第 i 層底部"),
        ("載重", "樓板兩端各標一次；每端或合計題文未明說，層剪力比例不受影響", "只取單邊"),
        ("剛性區域", "梁、柱、斜撐圍成的上方兩角三角形", "—")],
  nota="層高 $h = 4$ m；連梁長 $e = 0.6$ m；兩側剛性區底寬 $L_1 = L_2 = 4$ m，總跨 $L = 8.6$ m；$\\Delta_i$＝第 i 層層間位移，$\\theta_i = \\Delta_i/h$，$\\gamma_i$＝連梁端部旋轉變形角。"),
"SA-2024-1": dict(alt="梁 A–B–C–D 各 4 m：A 滾支承並受 200 kN-m 逆時針、B 受 100 kN 向下、C 內鉸、D 固定端",
  catch="A 端彎矩方向讀反、漏讀 C 內鉸",
  rows=[("A 端彎矩", "200 kN-m 逆時針", "順時針"),
        ("C 點", "內鉸（附屬梁 ABC 掛在懸臂 CD 上）", "連續"),
        ("位移限制", "向上、向下最大值皆 ≤ 40 mm（梁長 12 m 的 1/300）", "只檢查向下")],
  nota="座標以 A 為原點；位移向下為正；EI 常數。"),
"SA-2024-2": dict(alt="平行弦桁架 A～G／H～N，節間 4 m、高 3 m，7 根垂直桿＋6 根斜桿；B 滾支承、F 鉸支承；CD 製造誤差 δ、DE 溫差 ΔT",
  catch="漏畫垂直桿、B／F 支承型式對調",
  rows=[("垂直桿", "每個節點都有：HA、IB、JC、KD、LE、MF、NG 共 7 根", "只看斜桿而漏垂直桿"),
        ("斜桿", "H–B、B–J、J–D、D–L、L–F、F–N", "—"),
        ("支承", "B 滾支承、F 鉸支承（靜定，m＋r＝28＝2j）", "對調")],
  nota="$v_F = 12$ mm 向下；C、E 位移向下為正；$\\delta$ 以桿件過長為正；$\\Delta T$ 以升溫為正；$\\alpha = 1.5\\times10^{-5}$/℃、E＝100 GPa、A＝150 mm²。"),
}
SELF = {"SA-2024-2": "\n### 判讀圖解（解析自繪）\n\n![SA-2024-2 完整桁架幾何重繪：下弦6＋上弦6＋垂直7＋斜桿6＝25根桿件](figs/SA-2024-2-fig-1-frame.svg)\n\n*圖 2　題目重繪（向量版）。原圖說僅描述斜桿而漏提垂直桿，本圖將全部 25 根桿件明確畫出，並標示待求誤差桿 CD、DE 與量測點 C、E。*\n"}

for i, d in S1.items():
    p = f"{ROOT}/raw/solutions/{i}/{i}.md"; s = rd(p)
    if "## 1. 題目（考卷原文見題目正本）" in s: print("skip sec1", i); continue
    a = s.index("## 1. 原始題目重述"); b = s.index("\n## 2.", a)
    old = s[a:b]; prob = rd(f"{ROOT}/raw/solutions/{i}/{i}-problem.md")
    for png in re.findall(r"\(([^)/]+\.png)\)", old):
        assert png in prob, (i, png)                                  # 舊 §1 的證據圖都已在題目正本
    for svg in re.findall(r"\((figs/[^)]+\.svg)\)", old):
        assert svg in SELF.get(i, ""), (i, svg)                       # 解析自繪圖要移到判讀圖解小節
    assert os.path.exists(f"{ROOT}/raw/solutions/{i}/figs/{i}-fig-1-problem.svg"), i
    rows = "\n".join(f"| {x} | {y} | {z} |" for x, y, z in d["rows"])
    new = HEAD.format(i=i, alt=d["alt"], catch=d["catch"], rows=rows, nota=d["nota"], selfdraw=SELF.get(i, ""))
    s = s[:a] + new.rstrip("\n") + "\n\n---\n" + s[b:]
    s = s.rstrip() + f"\n\n*修正日期：{D}（§1 改為指向題目正本，補重繪附圖 figs/{i}-fig-1-problem.svg）*\n"
    wr(p, s); print("sec1", i)

for i in ERRATA_DONE:
    assert "## 1. 題目（考卷原文見題目正本）" in rd(f"{ROOT}/raw/solutions/{i}/{i}.md"), i
print("done")

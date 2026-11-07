"""SA-2014-2 刪除副分類 SA-U2-1（使用者決定 2026-11-07；考卷限用諧合變位法）。可重複執行。"""
import json, re
from pathlib import Path
R = Path(__file__).resolve().parents[2]
QID = "SA-2014-2"

# 1 索引
p = R / "raw/json/question_index.json"; raw = p.read_text(encoding="utf-8")
q = json.loads(raw); Q = q["questions"] if isinstance(q, dict) else q
x = next(x for x in Q if x["moduleId"] == QID)
if x.get("secondaryTopicIds"):
    # 只改這一欄，保留檔案其餘格式：以文字替換該題區塊
    i = raw.index(f'"{QID}"'); j = raw.index('"secondaryTopicIds"', i)
    k = raw.index("]", j)
    raw = raw[:j] + '"secondaryTopicIds": [' + raw[k:]
    assert json.loads(raw)
    x2 = next(y for y in (json.loads(raw)["questions"] if isinstance(q, dict) else json.loads(raw)) if y["moduleId"] == QID)
    assert x2["secondaryTopicIds"] == []
    p.write_text(raw, encoding="utf-8")

# 2 解析標頭與頁尾
p = R / f"raw/solutions/{QID}/{QID}.md"; t = p.read_text(encoding="utf-8")
t = t.replace("**副分類：** `SA-U2-1`", "**副分類：** 無", 1)
foot = "*修正日期：2026-11-07（非勘誤）分類更正：刪除副分類 SA-U2-1（考卷限用諧合變位法、「若以其他方法計算不予計分」，與最小功法無交集；使用者決定）*"
if foot not in t:
    t = t.rstrip("\n") + "\n" + foot + "\n"
p.write_text(t, encoding="utf-8")

# 3 dashboard
p = R / "dashboard-data.js"; t = p.read_text(encoding="utf-8")
t = t.replace('["SA-2014-2", "U2-2", ["SA-U2-1"],', '["SA-2014-2", "U2-2", [],')
p.write_text(t, encoding="utf-8")

# 4 單元總覽資料 U2-1
p = R / "study/data/unit-SA-U2-1.json"; d = json.loads(p.read_text(encoding="utf-8"))
d["Q"] = [e for e in d["Q"] if e["id"] != QID]
d["judge"] = d["judge"].replace("12 題主考點 + 1 題副考點。", "12 題主考點（無副考點）。")
for c in d["F"]:
    if "meta" in c:
        c["meta"] = c["meta"].replace("2014 二給 EI = 10000、EA = 40000；", "")
note = " 2026-11-07：SA-2014-2 刪副分類 SA-U2-1（考卷限用諧合變位法、「其他方法不予計分」，不是最小功法），副考點 1 → 0 題；單位力法已無副考點證據，材料數值卡刪 2014 二。"
if "SA-2014-2 刪副分類" not in d["footer"]:
    d["footer"] += note
p.write_text(json.dumps(d, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

# 5 觀念講義 U2-1
p = R / "study/lecture-SA-U2-1.html"; t = p.read_text(encoding="utf-8")
t = t.replace("主分類 12 題、副分類 1 題（2014）", "主分類 12 題、無副分類")
m = re.search(r'<h3>副分類（1 題）</h3>\s*<table>.*?</table>', t, re.S)
if m:
    t = t[:m.start()] + ('<h3>副分類（0 題）</h3>\n\n<p>原列副分類的 <a class="qlink" href="problems-view/SA-2014-2.html" target="_blank">SA-2014-2</a>'
                         '（梁＋軸力桿複合結構）已於 2026-11-07 刪除：考卷明文「請以諧合變位法計算……若以其他方法計算不予計分」，'
                         '與本子項的最小功法沒有交集，改見 SA-U2-2。</p>') + t[m.end():]
p.write_text(t, encoding="utf-8")
print("ok")

# 6 problems-view 表頭（md2view 只換 <main>，表頭手動同步；比照 SA-2009-1）
p = R / f"study/problems-view/{QID}.html"; t = p.read_text(encoding="utf-8")
t = t.replace(' ｜ 副分類 <b>SA-U2-1</b> 靜不定結構最小功法', '')
t = t.replace('<div class="hbtns"><a class="b-study" href="../unit-SA-U2-1.html">🧭 U2-1 單元總覽</a><a class="b-lect" href="../lecture-SA-U2-1.html">📚 U2-1 靜不定結構最小功法 講義</a></div><p class="nomat">本題主分類 SA-U2-2 目前尚無教材，按鈕指向有教材的副分類 SA-U2-1。</p>',
              '<div class="hbtns"></div><p class="nomat">本題主分類 SA-U2-2 目前尚無教材，故不提供教材按鈕。</p>')
p.write_text(t, encoding="utf-8")

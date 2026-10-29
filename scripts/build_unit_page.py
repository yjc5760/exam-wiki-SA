#!/usr/bin/env python3
"""build_unit_page.py — 產生單元總覽頁 study/unit-XX-Un-m.html

一頁整合：命題分析（考什麼）＋主要公式給／背分界＋逐題公式用途總表。
取代舊的 study-XX-Un-m.html 與 formula-given-XX-Un-m.html 兩頁。

資料來源
  study/data/unit-XX-Un-m.json   單元資料（人工／Claude 維護：考點群、逐題公式用途、公式卡、逐年備註、文字段落）
  raw/json/question_index.json   題目索引（題數、主副考點、排名、viz、verified 一律由此計算）
  解題過程影片/<題號>/video/*.mp4  有影片就在題目列加 🎬

用法
  python scripts/build_unit_page.py SA-U2-3          # 單一單元
  python scripts/build_unit_page.py --all            # study/data/ 下全部
  python scripts/build_unit_page.py SA-U2-3 --check  # 只檢查不寫檔

檢查（任何一項失敗即中止，不寫檔）
  * 資料檔的題目集合 ＝ 索引中「主考點或副考點為本單元」的題目集合
  * 每題的 f 索引都存在、考點群代號都存在
  * 「給數值」那一類公式（lv=give）必須位於逐年表最後一欄
"""
import argparse, collections, glob, html, json, os, re, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TPL = os.path.join(ROOT, "scripts", "unit_page_template.html")
SUBJ_NAME = {"SA": "結構學", "SS": "鋼結構", "RC": "鋼筋混凝土", "SD": "結構動力", "SM": "材料力學", "MM": "土壤力學"}


def yr(mid):
    return int(mid.split("-")[1])


def load_index():
    d = json.load(open(os.path.join(ROOT, "raw/json/question_index.json"), encoding="utf-8"))
    return d["questions"] if isinstance(d, dict) else d


def build(unit, check=False):
    dpath = os.path.join(ROOT, "study/data", f"unit-{unit}.json")
    D = json.load(open(dpath, encoding="utf-8"))
    subj = unit.split("-")[0]
    qs = load_index()
    byid = {q["moduleId"]: q for q in qs}
    years = sorted({yr(q["moduleId"]) for q in qs})
    pri_ids = {q["moduleId"] for q in qs if q.get("primaryTopicId") == unit}
    sec_ids = {q["moduleId"] for q in qs if unit in (q.get("secondaryTopicIds") or [])}
    errs = []

    data_ids = [q["id"] for q in D["Q"]]
    if len(set(data_ids)) != len(data_ids):
        errs.append("資料檔有重複題號")
    missing = (pri_ids | sec_ids) - set(data_ids)
    extra = set(data_ids) - (pri_ids | sec_ids)
    if missing:
        errs.append(f"索引有、資料檔沒有：{sorted(missing)}")
    if extra:
        errs.append(f"資料檔有、索引不屬本單元：{sorted(extra)}")
    nF = len(D["F"])
    for q in D["Q"]:
        if q["cl"] not in D["clusters"]:
            errs.append(f"{q['id']} 考點群 {q['cl']} 不存在")
        bad = [i for i in q["f"] if not 0 <= i < nF]
        if bad:
            errs.append(f"{q['id']} 公式索引越界 {bad}")
    gcol = len(D["mxCols"]) - 1
    for i, f in enumerate(D["F"]):
        if f["lv"] == "give" and f["c"] != gcol:
            errs.append(f"F[{i}] give 類必須放在最後一欄 c={gcol}")
        if not 0 <= f["c"] <= gcol:
            errs.append(f"F[{i}] 欄位 c={f['c']} 越界")
    if set(map(int, D["MXR"])) != set(years):
        errs.append("MXR 逐年備註的年份與索引考年不一致")
    if errs:
        print(f"[{unit}] 檢查失敗：\n  " + "\n  ".join(errs))
        return False

    # ---- 由索引計算的欄位 ----
    vdir = os.path.join(ROOT, "解題過程影片")
    for q in D["Q"]:
        x = byid[q["id"]]
        q["pri"] = 1 if q["id"] in pri_ids else 0
        q["secCat"] = "" if q["pri"] else f"{x['primaryTopicId'].split('-',1)[1]} {x.get('primaryTopicName','')}".strip()
        q["viz"] = 1 if x.get("hasViz") else 0
        q["ver"] = 1 if x.get("verificationStatus") == "verified" else 0
        q["video"] = 1 if glob.glob(os.path.join(vdir, q["id"], "video", "*.mp4")) else 0

    cnt = collections.Counter(x["primaryTopicId"] for x in qs if x.get("primaryTopicId"))
    rank = sorted(cnt.values(), reverse=True).index(cnt[unit]) + 1
    pri_years = {yr(i) for i in pri_ids}
    recent = years[-6:]
    rq = [i for i in pri_ids if yr(i) in recent]
    ry = {yr(i) for i in rq}
    pos = (f'<div class="k"><b>#{rank}</b><span>全科出題排名（{len(cnt)} 子項）</span></div>'
           f'<div class="k"><b>{len(pri_ids)}</b><span>主考點題數（＋副考點 {len(sec_ids)}）</span></div>'
           f'<div class="k"><b>{len(pri_years)}/{len(years)}</b><span>有出題的考年</span></div>'
           f'<div class="k"><b>{len(ry)}/6</b><span>近 6 考年（{recent[0]}–{str(recent[-1])[2:]}）共 {len(rq)} 題</span></div>')

    nver = sum(q["ver"] for q in D["Q"])
    rep = {
        "UNIT": unit, "SUBJ": subj, "SUBJ_NAME": SUBJ_NAME.get(subj, subj), "NAME": D["name"], "SHORT": D["short"],
        "DATE": D.get("date") or datetime.date.today().isoformat(), "POS": pos,
        "NPRI": str(len(pri_ids)), "NSEC": str(len(sec_ids)), "NALL": str(len(D["Q"])), "NCAT": str(len(D["clusters"])),
        "NQ": str(len(qs)), "NY": str(len(years)), "Y0": str(years[0]), "Y1": str(years[-1]),
        "DRIFT": D["drift"], "DRIFT_NOTE": D.get("driftNote", ""), "TYPE": D["type"], "RISK": D["risk"],
        "JUDGE": D["judge"], "JUDGE_MORE": D.get("judgeMore", ""), "STRATEGY": D["strategy"], "THREE": D["three"],
        "FOOTER": D.get("footer", ""), "BASE_NOTE": D.get("baseNote", ""),
        "VER_NOTE": f"本單元已驗證 {nver} 題。" if nver else "本單元目前沒有 verificationStatus＝verified 的題目。",
        "MXHEAD": "".join(f"<th>{html.escape(c)}</th>" for c in D["mxCols"]),
    }
    js = {k: D[k] for k in ("Q", "F", "clusters", "MXR", "mxCols")}
    js.update(base=D.get("base", []), baseShort=D.get("baseShort", "基本式"), mxNote=D.get("mxNote", ""),
              refAreaYears=D.get("refAreaYears", 0), NY=len(years))
    rep["DATA"] = json.dumps(js, ensure_ascii=False).replace("</", "<\\/")
    out = open(TPL, encoding="utf-8").read()
    for k, v in rep.items():
        out = out.replace("{{" + k + "}}", v)
    left = re.findall(r"\{\{[A-Z_]+\}\}", out)
    if left:
        print(f"[{unit}] 模板有未替換的欄位：{sorted(set(left))}")
        return False
    msg = (f"[{unit}] OK  主 {len(pri_ids)}＋副 {len(sec_ids)}＝{len(D['Q'])} 題｜排名 #{rank}｜"
           f"公式 {nF} 條｜影片 {sum(q['video'] for q in D['Q'])}｜已驗證 {nver}")
    if check:
        print(msg + "（--check，未寫檔）")
        return True
    dst = os.path.join(ROOT, "study", f"unit-{unit}.html")
    open(dst, "w", encoding="utf-8", newline="\n").write(out)
    print(msg + f" → {os.path.relpath(dst, ROOT)}")
    return True


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("unit", nargs="?")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--check", action="store_true")
    a = ap.parse_args()
    units = ([os.path.basename(p)[5:-5] for p in sorted(glob.glob(os.path.join(ROOT, "study/data/unit-*.json")))]
             if a.all else [a.unit])
    if not units or units == [None]:
        ap.error("請指定單元（如 SA-U2-3）或 --all")
    ok = all([build(u, a.check) for u in units])
    sys.exit(0 if ok else 1)

#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_frequency.py  (subject-frequency-map v1.1)
================================================
產生「全科出題頻率熱圖」單一自包含 HTML：study/frequency-XX.html

一句話：把整科的題目攤在「所有子項 × 所有考年」的格子上，回答「整科該從哪裡開始讀」。

用法（一律在知識庫根目錄執行）：
    python scripts/build_frequency.py            # 自動偵測科目並產頁
    python scripts/build_frequency.py --check    # 只對帳與印摘要，不寫檔

設計鐵律：
    頁面上出現的每個數字都由本檔從 question_index.json 算出，一律不手打、不憑印象。
    科目名稱、子項名稱、單元劃分一律取自 syllabus_taxonomy.json。
    要改頁面內容 → 改本檔再重跑，不要手改產出的 HTML。

v1.1（2026-10-08）相對 v1.0 的變更：
    - 前／後半期比較：每個子項算「前半考年 vs 後半考年」主考點數，標示升溫／退燒／持平，
      並另排一次「後半期排名」——抓出全期排名低估、近年其實很熱的子項（例：SA-U3-2）。
    - 「冷凍」子項（後半期 0 題主考點）取代空泛的「哪些可以不讀：無」，並註明是否仍以副考點出現。
    - 「只剩一個月」改用後半期前三名；「近年趨勢」列出實際領先的子項，不再是固定文案。
    - 熱圖可點：點格子／點子項名稱 → 下方詳情面板列出題號（連 problems-view/）、標籤、
      驗證狀態、解題影片；手機也能用（原本只有 title hover）。
    - 熱圖加每年合計列、十字準線高亮、前後半分界線；自訂 tooltip。
    - 排名表可點欄位排序；新增「前→後半」「後半排名」欄；教材欄偵測 study/decks/ 的記憶片與
      解題過程影片/ 的單元影片、題目影片。
    - 頁面上的複算指令改指本檔（舊版指向不存在的 skills/ 路徑）。
"""

import argparse
import collections
import glob
import json
import os
import re
import sys

MODULE_RE = re.compile(r"^([A-Z]{2})-(\d{4})-(\d+)$")


# ------------------------------------------------------------------ 讀檔
def load_index(path):
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    return d["questions"] if isinstance(d, dict) else d


def load_taxonomy(path, subject):
    """回傳 (科目全名, [(子項id, 子項名, 單元id)], {單元id: 單元名})"""
    with open(path, encoding="utf-8") as f:
        d = json.load(f)
    subj = next((s for s in d.get("subjects", []) if s["id"] == subject), None)
    if subj is None:
        sys.exit(f"錯誤：syllabus_taxonomy.json 裡找不到科目 {subject}。"
                 f"現有科目：{[s['id'] for s in d.get('subjects', [])]}")
    items, unames = [], {}
    for u in subj.get("units", []):
        unames[u["id"]] = u.get("name", u["id"])
        for it in u.get("items", []):
            items.append((it["id"], it["name"], u["id"]))
    return subj.get("name", subject), items, unames


def detect_subject(questions):
    codes = collections.Counter(m.group(1) for q in questions
                                for m in [MODULE_RE.match(q["moduleId"])] if m)
    if not codes:
        sys.exit("錯誤：無法從 moduleId 判斷科目代碼（預期格式 XX-YYYY-N）。")
    if len(codes) > 1:
        print(f"⚠️  索引裡出現多個科目代碼 {dict(codes)}，取最多的那個。")
    return codes.most_common(1)[0][0]


def yr(mid):
    m = MODULE_RE.match(mid)
    return int(m.group(2)) if m else None


def qno(mid):
    m = MODULE_RE.match(mid)
    return int(m.group(3)) if m else None


def rel(path, start):
    return os.path.relpath(path, start).replace(os.sep, "/")


# ------------------------------------------------------------------ 教材偵測
def scan_materials(study_dir, out_dir, tids):
    """掃描 study/，回傳 {子項id: {kind: 相對連結}}。不硬編任何清單。"""
    have = {t: {} for t in tids}
    for t in tids:
        for kind, fn in (("study", f"study-{t}.html"),
                         ("lecture", f"lecture-{t}.html"),
                         ("formula", f"formula-given-{t}.html")):
            p = os.path.join(study_dir, fn)
            if os.path.exists(p):
                have[t][kind] = rel(p, out_dir)
        # 記憶片：study/ 或 study/decks/（檔名含中文主題，用 glob）
        deck = sorted(glob.glob(os.path.join(study_dir, f"{t}_*記憶片.pdf"))
                      + glob.glob(os.path.join(study_dir, "decks", f"{t}_*記憶片.pdf")))
        if deck:
            have[t]["deck"] = rel(deck[0], out_dir)
    return have


def scan_videos(video_dir, out_dir, tids, qids):
    """解題過程影片/<資料夾>/video/*.mp4
       資料夾名＝題號 → 題目影片；資料夾名以子項id開頭（後接空白或 -n）→ 單元影片。"""
    topic_v = {t: [] for t in tids}
    q_v = {}
    if not os.path.isdir(video_dir):
        return topic_v, q_v
    for d in sorted(os.listdir(video_dir)):
        full = os.path.join(video_dir, d)
        if not os.path.isdir(full):
            continue
        mp4s = sorted(glob.glob(os.path.join(full, "video", "*.mp4")))
        if not mp4s:
            continue
        href = rel(mp4s[0], out_dir)
        if d in qids:
            q_v[d] = href
            continue
        # 最長前綴優先（避免 XX-U1-1 吃到 XX-U1-12）
        for t in sorted(tids, key=len, reverse=True):
            if re.match(re.escape(t) + r"(\s|-\d|$)", d):
                title = d[len(t):].strip(" -_") or d
                topic_v[t].append({"name": d, "title": title, "href": href})
                break
    return topic_v, q_v


# ------------------------------------------------------------------ 統計
def drift_label(p, early, late):
    if p == 0:
        return "none"
    if late == 0:
        return "frozen"
    if early == 0:
        return "new"
    d = late - early
    if d >= 3:
        return "up"
    if d <= -3:
        return "down"
    return "flat"


def analyse(questions, items, unames, materials, topic_v, q_v, views):
    years = sorted({yr(q["moduleId"]) for q in questions} - {None})
    recent6 = years[-6:]
    half = len(years) // 2
    early_y, late_y = years[:half], years[half:]
    total = len(questions)
    tids = [t for t, _, _ in items]

    per_year_total = collections.Counter(yr(q["moduleId"]) for q in questions)
    uniform = len(set(per_year_total.values())) == 1
    per_year = per_year_total[years[0]] if uniform else None

    grid = {t: {y: {"p": [], "s": []} for y in years} for t in tids}
    orphan = collections.Counter()
    Q = {}
    for q in sorted(questions, key=lambda q: (yr(q["moduleId"]) or 0, qno(q["moduleId"]) or 0)):
        y, mid = yr(q["moduleId"]), q["moduleId"]
        pt = q.get("primaryTopicId")
        if pt in grid:
            grid[pt][y]["p"].append(mid)
        else:
            orphan[pt] += 1
        secs = [t for t in (q.get("secondaryTopicIds") or []) if t in grid]
        for t in secs:
            grid[t][y]["s"].append(mid)
        Q[mid] = {"y": y, "n": qno(mid), "p": pt, "s": secs,
                  "tags": (q.get("tags") or [])[:6],
                  "v": q.get("verificationStatus") == "verified",
                  "view": mid in views, "vid": q_v.get(mid, "")}

    pri = collections.Counter(q.get("primaryTopicId") for q in questions)
    sec = collections.Counter(t for q in questions for t in (q.get("secondaryTopicIds") or []))
    ordered = [(k, v) for k, v in pri.most_common() if k in grid]
    rank = {k: i + 1 for i, (k, _) in enumerate(ordered)}

    rows = []
    for tid, name, uid in items:
        hits = [y for y in years if grid[tid][y]["p"]]
        best, run, span = 0, [], None
        for y in years:
            if y in hits:
                if len(run) > best:
                    best, span = len(run), (run[0], run[-1])
                run = []
            else:
                run.append(y)
        if len(run) > best:
            best, span = len(run), (run[0], run[-1])
        early = sum(len(grid[tid][y]["p"]) for y in early_y)
        late = sum(len(grid[tid][y]["p"]) for y in late_y)
        late_s = sum(len(grid[tid][y]["s"]) for y in late_y)
        late_s_years = [y for y in late_y if grid[tid][y]["s"]]
        pos = collections.Counter(qno(m) for y in years for m in grid[tid][y]["p"])
        mats = materials.get(tid, {})
        rows.append({
            "id": tid, "short": tid.split("-", 1)[1], "name": name, "unit": uid,
            "p": pri.get(tid, 0), "s": sec.get(tid, 0),
            "share": round(pri.get(tid, 0) / total * 100, 1) if total else 0.0,
            "rank": rank.get(tid), "hit": len(hits), "last": (hits[-1] if hits else None),
            "gap": best, "gapSpan": list(span) if span else None,
            "r6h": sum(1 for y in recent6 if grid[tid][y]["p"]),
            "r6q": sum(len(grid[tid][y]["p"]) for y in recent6),
            "early": early, "late": late, "lateS": late_s, "lateSYears": late_s_years,
            "drift": drift_label(pri.get(tid, 0), early, late),
            "pos": {str(k): v for k, v in sorted(pos.items())},
            "mat": mats, "vids": topic_v.get(tid, []),
            "qvids": sum(1 for y in years for m in grid[tid][y]["p"] if m in q_v),
            "cells": [{"p": grid[tid][y]["p"], "s": grid[tid][y]["s"]} for y in years],
        })

    late_order = sorted([r for r in rows if r["late"] > 0], key=lambda r: (-r["late"], -r["p"]))
    for i, r in enumerate(late_order):
        r["lateRank"] = i + 1
    for r in rows:
        r.setdefault("lateRank", None)

    maxP = max((len(c["p"]) for r in rows for c in r["cells"]), default=1) or 1
    maxA = max((len(c["p"]) + len(c["s"]) for r in rows for c in r["cells"]), default=1) or 1

    unit_tot, unit_early, unit_late = collections.Counter(), collections.Counter(), collections.Counter()
    unit_items = collections.defaultdict(list)
    for r in rows:
        unit_tot[r["unit"]] += r["p"]
        unit_early[r["unit"]] += r["early"]
        unit_late[r["unit"]] += r["late"]
        unit_items[r["unit"]].append(r)

    return {
        "years": years, "recent6": recent6, "early": early_y, "late": late_y,
        "total": total, "rows": rows, "Q": Q,
        "perYear": per_year, "uniform": uniform, "maxP": maxP, "maxA": maxA,
        "ordered": ordered, "lateOrder": late_order,
        "unitTot": dict(unit_tot), "unitEarly": dict(unit_early), "unitLate": dict(unit_late),
        "unitItems": dict(unit_items), "unames": unames, "orphan": dict(orphan),
        "lateTotal": sum(r["late"] for r in rows), "earlyTotal": sum(r["early"] for r in rows),
        "nVerified": sum(1 for q in Q.values() if q["v"]),
        "nQvid": len([1 for q in Q.values() if q["vid"]]),
        "nTvid": sum(len(v) for v in topic_v.values()),
    }


# ------------------------------------------------------------------ 對帳
def check(A):
    errs, warns = [], []
    rows = A["rows"]
    cell_p = sum(len(c["p"]) for r in rows for c in r["cells"])
    if cell_p + sum(A["orphan"].values()) != A["total"]:
        errs.append(f"熱圖主考點格子總和 {cell_p} ＋ 孤兒 {sum(A['orphan'].values())} "
                    f"≠ 題庫總題數 {A['total']}")
    for r in rows:
        if sum(len(c["p"]) for c in r["cells"]) != r["p"]:
            errs.append(f"{r['id']} 列總和 ≠ 主考點數 {r['p']}")
        if sum(len(c["s"]) for c in r["cells"]) != r["s"]:
            errs.append(f"{r['id']} 副考點列總和不符")
        if r["early"] + r["late"] != r["p"]:
            errs.append(f"{r['id']} 前半 {r['early']} ＋ 後半 {r['late']} ≠ {r['p']}")
    if sum(A["unitTot"].values()) != cell_p:
        errs.append("單元小計加總 ≠ 主考點總數")
    if A["earlyTotal"] + A["lateTotal"] != cell_p:
        errs.append("前半＋後半 ≠ 主考點總數")
    if A["orphan"]:
        warns.append(f"索引有 taxonomy 沒有的 primaryTopicId：{A['orphan']}"
                     f"（未畫進熱圖，頁面會顯示紅色警告框）")
    return errs, warns


# ------------------------------------------------------------------ 版型
CSS = """<style>
:root{--ac:#1565c0;--ac2:#e3f2fd;--bg:#f7f9fb;--card:#fff;--ink:#263238;--mut:#78909c;--bd:#e0e6ea;--warn:#c62828;
--up:#c62828;--up2:#ffebee;--dn:#546e7a;--dn2:#eceff1;--hot:#ef6c00}
*{box-sizing:border-box}body{margin:0;font-family:"Microsoft JhengHei","Noto Sans TC",sans-serif;background:var(--bg);color:var(--ink);line-height:1.6}
header{background:linear-gradient(135deg,#0d47a1,#1976d2);color:#fff;padding:28px 24px}
header h1{margin:0 0 6px;font-size:1.5em}header p{margin:0;opacity:.85;font-size:.92em}
nav{position:sticky;top:0;z-index:20;background:#fff;border-bottom:2px solid var(--bd);padding:8px 16px;display:flex;flex-wrap:wrap;gap:6px}
nav a{text-decoration:none;color:var(--ac);font-size:.88em;padding:5px 10px;border-radius:16px;background:var(--ac2)}
nav a:hover{background:var(--ac);color:#fff}
main{max-width:1240px;margin:0 auto;padding:20px 16px 60px}
h2{font-size:1.25em;border-left:5px solid var(--ac);padding-left:10px;margin:26px 0 14px}
h3{font-size:1.05em;margin:34px 0 10px;padding-bottom:5px;border-bottom:2px solid var(--ac2);scroll-margin-top:56px}
code{background:#eceff1;border-radius:4px;padding:0 4px;font-size:.92em}
.role{background:#fffde7;border:1px solid #ffe082;border-left:5px solid #f9a825;border-radius:8px;padding:12px 16px;font-size:.88em;margin-bottom:12px}
.role b{color:#e65100}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(170px,1fr));gap:12px}
.kpi{background:var(--card);border:1px solid var(--bd);border-radius:10px;padding:14px;text-align:center}
.kpi .n{font-size:1.8em;font-weight:700;color:var(--ac);line-height:1.3}.kpi .l{font-size:.82em;color:var(--mut)}
.kpi.hot .n{color:var(--hot)}
.insight{display:grid;gap:10px;margin-top:14px}
.ins{background:#fff;border:1px solid var(--bd);border-left:5px solid var(--hot);border-radius:8px;padding:10px 14px;font-size:.9em}
.ins.cold{border-left-color:var(--dn)}
.ins b.k{color:var(--hot)}.ins.cold b.k{color:var(--dn)}
.note{font-size:.85em;color:var(--mut);background:#fff;border:1px dashed var(--bd);border-radius:8px;padding:10px 14px;margin-top:12px}
.tw{overflow-x:auto;background:#fff;border:1px solid var(--bd);border-radius:10px;padding:10px}
table{border-collapse:collapse;width:100%;background:#fff;font-size:.88em}
th,td{border:1px solid var(--bd);padding:6px 8px;text-align:left;vertical-align:middle}
th{background:var(--ac2)}
td.num,th.num{text-align:center;font-variant-numeric:tabular-nums}
#hm{width:auto;min-width:100%}
#hm td,#hm th{border:1px solid #eceff1;padding:0;text-align:center}
#hm th.rowh{text-align:left;padding:4px 8px;white-space:nowrap;background:#fff;position:sticky;left:0;z-index:3;border-right:2px solid var(--bd);cursor:pointer}
#hm th.rowh:hover,#hm th.rowh.hl{background:#fff3e0}
#hm th.rowh .dr{font-size:.75em;margin-left:4px}
#hm th.yr{font-size:.72em;font-weight:600;color:var(--mut);background:#fff;padding:3px 0;min-width:28px}
#hm th.yr.r6{background:#fff8e1;color:#e65100}
#hm th.yr.hl{background:#ffe0b2;color:#bf360c}
#hm .split{border-left:3px solid #90a4ae !important}
#hm td.c{width:28px;height:28px;font-size:.78em;font-weight:700;cursor:pointer;transition:box-shadow .1s}
#hm td.c.empty{cursor:default}
#hm td.c.r6{outline:1px solid #ffcc80;outline-offset:-1px}
#hm td.c:not(.empty):hover{box-shadow:inset 0 0 0 2px #ff9800}
#hm td.c.sel{box-shadow:inset 0 0 0 3px #e65100 !important}
#hm td.tot{background:#fff;color:#0d47a1;font-weight:700;min-width:42px;font-size:.8em}
#hm tr.usep td{background:#f2f5f8;height:6px;padding:0;border:none}
#hm tr.foot th,#hm tr.foot td{background:#fafbfc;font-size:.72em;color:var(--mut);font-weight:600;height:24px}
#hm tr.half td{font-size:.72em;color:var(--mut);background:#fafbfc;padding:2px 0;height:20px}
.sec-dot{position:absolute;right:2px;bottom:2px;width:5px;height:5px;border-radius:50%;background:#ef6c00}
.cellwrap{position:relative;width:100%;height:100%;display:flex;align-items:center;justify-content:center}
#tip{position:fixed;pointer-events:none;z-index:50;background:#263238;color:#fff;font-size:.8em;padding:6px 10px;border-radius:6px;max-width:320px;display:none;line-height:1.5;box-shadow:0 2px 8px rgba(0,0,0,.2)}
#tip .h{color:#ffcc80;font-weight:700}
.legend{display:flex;flex-wrap:wrap;gap:14px;align-items:center;font-size:.84em;color:var(--mut);margin:10px 0 0}
.sw{display:inline-block;width:20px;height:16px;border:1px solid #cfd8dc;vertical-align:middle;margin-right:4px}
.btns{display:flex;flex-wrap:wrap;gap:8px;margin:12px 0;align-items:center}
.fbtn{border:1px solid var(--bd);background:#fff;border-radius:18px;padding:6px 14px;cursor:pointer;font-size:.88em;font-family:inherit}
.fbtn.on{background:var(--ac);color:#fff;border-color:var(--ac)}
.hint{font-size:.82em;color:var(--mut)}
#detail{margin-top:12px;background:#fff;border:2px solid #ffcc80;border-radius:10px;padding:12px 16px;display:none}
#detail h4{margin:0 0 8px;font-size:1em;display:flex;justify-content:space-between;align-items:center;gap:10px}
#detail .x{border:none;background:#eceff1;border-radius:50%;width:26px;height:26px;cursor:pointer;font-size:.9em}
.ql{list-style:none;margin:0;padding:0}
.ql li{padding:6px 0;border-bottom:1px dashed #eceff1;display:flex;flex-wrap:wrap;gap:6px;align-items:center;font-size:.88em}
.ql li:last-child{border:none}
.ql .qid{font-weight:700;font-variant-numeric:tabular-nums;min-width:86px}
.ql a.qid{color:var(--ac);text-decoration:none}.ql a.qid:hover{text-decoration:underline}
.b{font-size:.72em;border-radius:9px;padding:1px 7px;white-space:nowrap;display:inline-block}
.b-p{background:#1565c0;color:#fff}.b-s{background:#ffe0b2;color:#e65100}
.b-v{background:#e8f5e9;color:#1b5e20}.b-u{background:#f5f5f5;color:#9e9e9e}
.b-t{background:#eceff1;color:#546e7a}
a.b-vid{background:#fce4ec;color:#ad1457;text-decoration:none}a.b-vid:hover{background:#ad1457;color:#fff}
.sub{font-size:.82em;color:var(--mut);margin:10px 0 4px;font-weight:700}
.bar{display:inline-block;height:13px;border-radius:3px;vertical-align:middle;background:var(--ac)}
.bar2{display:inline-block;height:13px;border-radius:3px;vertical-align:middle;background:#ffcc80}
.tag{font-size:.72em;border-radius:9px;padding:1px 7px;margin:1px 3px 1px 0;white-space:nowrap;display:inline-block}
a.tag{text-decoration:none}
.t-y{background:#e8f5e9;color:#1b5e20}a.t-y:hover{background:#1b5e20;color:#fff}
.t-n{background:#fafafa;color:#bdbdbd}
.t-v{background:#fce4ec;color:#ad1457;cursor:pointer;border:none;font-family:inherit}.t-v:hover{background:#ad1457;color:#fff}
.dr-up,.dr-new{color:var(--up);font-weight:700}.dr-down,.dr-frozen{color:var(--dn);font-weight:700}.dr-flat{color:#9e9e9e}
#rank th.sk{cursor:pointer;user-select:none;white-space:nowrap}
#rank th.sk:hover{background:#bbdefb}
#rank th.sk::after{content:" ⇅";color:#90caf9;font-size:.8em}
#rank th.sk.asc::after{content:" ▲";color:var(--ac)}#rank th.sk.desc::after{content:" ▼";color:var(--ac)}
#rank tr.frozen td{background:#f5f7f8;color:#78909c}
.ubar{display:flex;height:14px;border-radius:4px;overflow:hidden;min-width:160px;background:#eceff1}
.ubar span{display:block;height:100%}
.zero{background:#fce4ec !important}
footer{text-align:center;color:var(--mut);font-size:.8em;padding:20px}
@media(max-width:760px){#hm td.c{width:22px;height:24px;font-size:.7em}#hm th.rowh .nm{display:none}header{padding:20px 16px}}
@media print{nav,.btns,#detail,#tip,.hint{display:none !important}body{background:#fff}.tw{border:none;padding:0}
 #hm td.c{-webkit-print-color-adjust:exact;print-color-adjust:exact}h3{break-after:avoid}}
</style>"""

JS = r"""<script>
const D = __DATA__;
const YEARS = D.years, R6 = new Set(D.recent6), SPLIT = D.late[0];
const DR = {up:['▲','升溫'],new:['★','新出現'],down:['▼','退燒'],frozen:['❄','冷凍'],flat:['＝','持平'],none:['','—']};
let MODE = 'p', SEL = null;
const $ = id => document.getElementById(id);
const esc = s => String(s).replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'}[c]));

function shade(v, max){
  if(!v) return '#f7fafc';
  const t = Math.min(1, v / max), a=[227,242,253], b=[13,71,161];
  const c=a.map((x,i)=>Math.round(x+(b[i]-x)*(0.25+0.75*t)));
  return `rgb(${c[0]},${c[1]},${c[2]})`;
}
function fg(v, max){ return (!v) ? '#cfd8dc' : ((v/max)>0.45 ? '#fff' : '#0d47a1'); }
const val = c => MODE==='p' ? c.p.length : c.p.length + c.s.length;

function drawHeat(){
  const max = MODE==='p' ? D.maxP : D.maxA;
  const sp = y => y===SPLIT ? ' split' : '';
  let h = '<table id="hm"><thead><tr><th class="rowh" style="cursor:default">子項</th>';
  YEARS.forEach((y,i)=>{ h += `<th class="yr${R6.has(y)?' r6':''}${sp(y)}" data-yi="${i}">${String(y).slice(2)}</th>`; });
  h += '<th class="yr" style="min-width:42px">合計</th></tr></thead><tbody>';
  let lastUnit = null;
  const colTot = YEARS.map(()=>0);
  D.rows.forEach((r,ri)=>{
    if(lastUnit && r.unit!==lastUnit) h += `<tr class="usep"><td colspan="${YEARS.length+2}"></td></tr>`;
    lastUnit = r.unit;
    const tot = MODE==='p' ? r.p : (r.p + r.s);
    const dr = DR[r.drift];
    h += `<tr data-ri="${ri}"><th class="rowh" data-ri="${ri}" title="點一下看這個子項的全部題目"><b>${r.short}</b> <span class="nm">${esc(r.name)}</span>`
       + (dr[0] ? `<span class="dr dr-${r.drift}" title="前半 ${r.early} 題 → 後半 ${r.late} 題（${dr[1]}）">${dr[0]}</span>` : '') + '</th>';
    r.cells.forEach((c,i)=>{
      const v = val(c), y = YEARS[i];
      colTot[i] += v;
      const sel = SEL && SEL.t==='c' && SEL.ri===ri && SEL.yi===i ? ' sel' : '';
      h += `<td class="c${R6.has(y)?' r6':''}${sp(y)}${v?'':' empty'}${sel}" data-ri="${ri}" data-yi="${i}" style="background:${shade(v,max)};color:${fg(v,max)}">`
         + `<div class="cellwrap">${v||''}${(MODE==='p'&&c.s.length)?'<span class="sec-dot"></span>':''}</div></td>`;
    });
    h += `<td class="tot">${tot||'0'}</td></tr>`;
  });
  h += `<tr class="foot"><th class="rowh" style="cursor:default">每年合計</th>`
     + colTot.map((v,i)=>`<td class="${sp(YEARS[i]).trim()}">${v}</td>`).join('')
     + `<td>${colTot.reduce((a,b)=>a+b,0)}</td></tr>`;
  const eN = D.early.length, lN = D.late.length;
  h += `<tr class="half"><th class="rowh" style="cursor:default;font-size:.72em;color:#78909c">前／後半期</th>`
     + `<td colspan="${eN}">◀ 前半 ${D.early[0]}–${D.early[eN-1]}（${D.earlyTotal} 題）</td>`
     + `<td colspan="${lN}" class="split">後半 ${D.late[0]}–${D.late[lN-1]}（${D.lateTotal} 題）▶</td><td></td></tr>`;
  h += '</tbody></table>';
  $('heat').innerHTML = h;

  let lg = '';
  for(let v=0; v<=max; v++) lg += `<span><span class="sw" style="background:${shade(v,max)}"></span>${v} 題</span>`;
  lg += (MODE==='p' ? '<span>🟠 右下角橘點 ＝ 該年該子項還有副考點</span>' : '<span>此模式的格值 ＝ 主考點 ＋ 副考點</span>');
  lg += `<span>黃框 ＝ 近 ${D.recent6.length} 考年</span><span>粗灰線 ＝ 前／後半期分界</span>`;
  lg += '<span>▲升溫 ★新出現 ▼退燒 ❄冷凍（後半期 0 題）</span>';
  $('lg').innerHTML = lg;
}

function hl(ri, yi, on){
  document.querySelectorAll('#hm .hl').forEach(e=>e.classList.remove('hl'));
  if(!on) return;
  const th = document.querySelector(`#hm th.yr[data-yi="${yi}"]`); if(th) th.classList.add('hl');
  const rh = document.querySelector(`#hm th.rowh[data-ri="${ri}"]`); if(rh) rh.classList.add('hl');
}
function tipFor(r, yi){
  const c = r.cells[yi], y = YEARS[yi];
  const ids = c.p.map(m=>`${m}（第${D.Q[m].n}題）`).concat(c.s.map(m=>`(副) ${m}`));
  return `<span class="h">${r.short} · ${y}</span><br>` + (ids.length ? ids.join('<br>') + '<br><span style="opacity:.7">點一下看題目</span>' : '無');
}
function bindHeat(){
  const tip = $('tip'), hm = $('heat');
  hm.addEventListener('mousemove', e=>{
    const td = e.target.closest('td.c');
    if(!td){ tip.style.display='none'; hl(0,0,false); return; }
    const ri=+td.dataset.ri, yi=+td.dataset.yi;
    hl(ri, yi, true);
    tip.innerHTML = tipFor(D.rows[ri], yi);
    tip.style.display='block';
    const x = Math.min(e.clientX+14, window.innerWidth - tip.offsetWidth - 8);
    const y = e.clientY + 16 + tip.offsetHeight > window.innerHeight ? e.clientY - tip.offsetHeight - 10 : e.clientY + 16;
    tip.style.left = x+'px'; tip.style.top = y+'px';
  });
  hm.addEventListener('mouseleave', ()=>{ tip.style.display='none'; hl(0,0,false); });
  hm.addEventListener('click', e=>{
    const td = e.target.closest('td.c'), rh = e.target.closest('th.rowh[data-ri]');
    if(td && !td.classList.contains('empty')) showCell(+td.dataset.ri, +td.dataset.yi);
    else if(rh) showRow(+rh.dataset.ri);
  });
}

function qItem(m, role){
  const q = D.Q[m];
  const idh = q.view ? `<a class="qid" href="problems-view/${m}.html" target="_blank">${m}</a>` : `<span class="qid">${m}</span>`;
  let h = `<li>${idh}<span class="b ${role==='p'?'b-p':'b-s'}">${role==='p'?'主考點':'副考點'}</span>`
        + `<span style="color:#78909c;font-size:.9em">第 ${q.n} 題</span>`;
  if(role==='s'){ const pr = D.rows.find(r=>r.id===q.p); if(pr) h += `<span style="color:#78909c;font-size:.85em">主＝${pr.short}</span>`; }
  h += q.v ? '<span class="b b-v">✓ 已驗證</span>' : '<span class="b b-u">未驗證</span>';
  if(q.vid) h += `<a class="b b-vid" href="${encodeURI(q.vid)}" target="_blank">🎬 解題影片</a>`;
  h += q.tags.map(t=>`<span class="b b-t">${esc(t)}</span>`).join('');
  if(!q.view) h += '<span style="font-size:.78em;color:#bdbdbd">（尚無 problems-view 頁）</span>';
  return h + '</li>';
}
function openDetail(title, body){
  $('detail').innerHTML = `<h4><span>${title}</span><button class="x" onclick="closeDetail()" aria-label="關閉">✕</button></h4>${body}`;
  $('detail').style.display = 'block';
  drawHeat();
  $('detail').scrollIntoView({behavior:'smooth', block:'nearest'});
}
function closeDetail(){ SEL=null; $('detail').style.display='none'; drawHeat(); }
function showCell(ri, yi){
  SEL = {t:'c', ri, yi};
  const r = D.rows[ri], c = r.cells[yi];
  openDetail(`${r.short} ${esc(r.name)} · ${YEARS[yi]} 年`,
    '<ul class="ql">' + c.p.map(m=>qItem(m,'p')).join('') + c.s.map(m=>qItem(m,'s')).join('') + '</ul>'
    + `<div class="hint" style="margin-top:6px">點左側子項名稱可看這個子項 ${YEARS.length} 年的全部題目</div>`);
}
const LBL = {study:'命題分析',lecture:'講義',formula:'給／背',deck:'記憶片'};
function matTags(r){
  return ['study','lecture','formula','deck'].map(m=> r.mat[m]
     ? `<a class="tag t-y" href="${encodeURI(r.mat[m])}" target="_blank">${LBL[m]}</a>`
     : `<span class="tag t-n">${LBL[m]}</span>`).join('');
}
function showRow(ri){
  SEL = {t:'r', ri};
  const r = D.rows[ri];
  const P = r.cells.flatMap(c=>c.p), S = r.cells.flatMap(c=>c.s);
  const dr = DR[r.drift];
  let b = `<div style="font-size:.88em;margin-bottom:6px">主考點 <b>${r.p}</b> 題、副考點 <b>${r.s}</b> 題｜前半 ${r.early} → 後半 ${r.late}`
        + (dr[0] ? ` <span class="dr-${r.drift}">${dr[0]} ${dr[1]}</span>` : '') + `｜教材：${matTags(r)}</div>`;
  if(r.vids.length) b += '<div class="sub">🎬 單元講解影片</div><ul class="ql">'
      + r.vids.map(v=>`<li><a class="b b-vid" href="${encodeURI(v.href)}" target="_blank">▶ 播放</a>${esc(v.title)}</li>`).join('') + '</ul>';
  b += `<div class="sub">主考點（${P.length}）</div><ul class="ql">` + (P.map(m=>qItem(m,'p')).join('') || '<li>無</li>') + '</ul>';
  if(S.length) b += `<div class="sub">副考點（${S.length}）——這個子項是別題的工具</div><ul class="ql">` + S.map(m=>qItem(m,'s')).join('') + '</ul>';
  openDetail(`${r.short} ${esc(r.name)}`, b);
}
function setMode(m, btn){
  MODE = m;
  document.querySelectorAll('#modebtns .fbtn').forEach(b=>b.classList.remove('on'));
  btn.classList.add('on');
  drawHeat();
}

// ---------------- 排名表（可排序）
const COLS = [
  {k:'rank',  h:'#', f:r=>r.rank||99, num:1, def:'asc'},
  {k:'id',    h:'子項', f:r=>r.id, def:'asc'},
  {k:'p',     h:'主', f:r=>r.p, num:1},
  {k:'bar',   h:'主＋副題量'},
  {k:'s',     h:'副', f:r=>r.s, num:1},
  {k:'share', h:'佔全科', f:r=>r.share, num:1},
  {k:'drift', h:'前→後半', f:r=>r.late-r.early, num:1},
  {k:'lateRank', h:'後半<br>排名', f:r=>r.lateRank||99, num:1, def:'asc'},
  {k:'hit',   h:'出現<br>年數', f:r=>r.hit, num:1},
  {k:'gap',   h:'最長<br>空窗', f:r=>r.gap, num:1},
  {k:'last',  h:'最後<br>出現', f:r=>r.last||0, num:1},
  {k:'r6',    h:'', f:r=>r.r6q, num:1},
  {k:'pos',   h:'常見題號位置'},
  {k:'mat',   h:'現有教材', f:r=>Object.keys(r.mat).length + r.vids.length/100},
];
let SORT = {k:'rank', dir:'asc'};
function drawRank(){
  COLS.find(c=>c.k==='r6').h = `近 ${D.recent6.length}<br>考年`;
  const maxA = Math.max(1, ...D.rows.map(r=>r.p+r.s));
  const col = COLS.find(c=>c.k===SORT.k);
  const sorted = [...D.rows].sort((a,b)=>{
    const x = col.f(a), y = col.f(b);
    const d = (x<y?-1:x>y?1:0) * (SORT.dir==='asc'?1:-1);
    return d || ((a.rank||99)-(b.rank||99));
  });
  let h = '<table><thead><tr>' + COLS.map(c=>{
    const cls = [c.num?'num':'', c.f?'sk':'', SORT.k===c.k?SORT.dir:''].filter(Boolean).join(' ');
    return `<th class="${cls}"${c.f?` data-k="${c.k}"`:''}>${c.h}</th>`;
  }).join('') + '</tr></thead><tbody>';
  sorted.forEach(r=>{
    const ri = D.rows.indexOf(r);
    const w = r.p/maxA*150, w2 = r.s/maxA*150;
    const pos = Object.entries(r.pos).map(([k,v])=>`第${k}題×${v}`).join('、') || '—';
    const nm = r.mat.study
        ? `<a href="${encodeURI(r.mat.study)}" target="_blank" style="color:var(--ac);text-decoration:none"><b>${r.short}</b> ${esc(r.name)}</a>`
        : `<b>${r.short}</b> ${esc(r.name)}`;
    const dr = DR[r.drift];
    const nv = r.vids.length + r.qvids;
    const vt = nv ? `<button class="tag t-v" onclick="showRow(${ri})" title="單元影片 ${r.vids.length} 支、題目解題影片 ${r.qvids} 支">🎬 影片 ${nv}</button>` : '';
    h += `<tr class="${r.p===0?'zero':''}${r.drift==='frozen'?' frozen':''}"><td class="num">${r.p? (r.rank||'') : '—'}</td>`
      + `<td>${nm}</td><td class="num"><b>${r.p}</b></td>`
      + `<td><span class="bar" style="width:${w}px"></span><span class="bar2" style="width:${w2}px"></span></td>`
      + `<td class="num">${r.s}</td><td class="num">${r.share}%</td>`
      + `<td class="num">${r.early} → ${r.late}<br><span class="dr-${r.drift}" style="font-size:.85em">${dr[0]} ${dr[1]}</span></td>`
      + `<td class="num">${r.lateRank||'—'}${r.lateRank && r.rank && r.rank - r.lateRank >= 3 ? ' <span class="dr-up">↑</span>' : ''}</td>`
      + `<td class="num">${r.hit}/${YEARS.length}</td>`
      + `<td class="num">${r.gap?`${r.gap} 年<br><span style="font-size:.82em;color:#90a4ae">${r.gapSpan[0]}–${r.gapSpan[1]}</span>`:'—'}</td>`
      + `<td class="num">${r.last||'—'}</td>`
      + `<td class="num">${r.r6h}/${D.recent6.length}<br><span style="font-size:.82em;color:#90a4ae">${r.r6q} 題</span></td>`
      + `<td style="font-size:.82em;color:#78909c">${pos}</td><td>${matTags(r)}${vt}</td></tr>`;
  });
  h += '</tbody></table>';
  $('rank').innerHTML = h;
  document.querySelectorAll('#rank th.sk').forEach(th=>th.onclick=()=>{
    const k = th.dataset.k, c = COLS.find(x=>x.k===k);
    SORT = SORT.k===k ? {k, dir: SORT.dir==='asc'?'desc':'asc'} : {k, dir: c.def||'desc'};
    drawRank();
  });
}
drawHeat(); bindHeat(); drawRank();
</script>"""


def build_html(subject, subj_name, A, today, script_rel):
    rows, years, N = A["rows"], A["years"], A["total"]
    ordered, late_order = A["ordered"], A["lateOrder"]
    E, L = A["early"], A["late"]
    eT, lT = A["earlyTotal"], A["lateTotal"]
    by_id = {r["id"]: r for r in rows}
    appeared = sum(1 for r in rows if r["p"] > 0)
    top = ordered[0] if ordered else (None, 0)
    topN = lambda n: [k for k, _ in ordered[:n]]
    sumN = lambda n: sum(v for _, v in ordered[:n])
    pct = lambda a, b: round(a / b * 100, 1) if b else 0
    span = lambda ys: f"{ys[0]}–{ys[-1]}"
    zero = [r for r in rows if r["p"] == 0]
    frozen = [r for r in rows if r["drift"] == "frozen"]
    rising = sorted([r for r in rows if r["drift"] in ("up", "new")], key=lambda r: -(r["late"] - r["early"]))
    falling = sorted([r for r in rows if r["drift"] == "down"], key=lambda r: (r["late"] - r["early"]))
    tools = sorted([r for r in rows if r["s"] > r["p"]], key=lambda r: -r["s"])[:4]
    under = [r for r in rows if r["rank"] and r["lateRank"] and r["rank"] - r["lateRank"] >= 3
             and r["late"] >= max(3, lT * 0.08)]
    r6_order = sorted([r for r in rows if r["r6q"]], key=lambda r: (-r["r6q"], -r["r6h"]))
    r6T = sum(r["r6q"] for r in rows)
    nm = lambda r: f'<b>{r["short"]}</b> {r["name"]}'

    # ---- 重點觀察（全部由資料生成）----
    ins = []
    for r in under:
        ins.append(f'<div class="ins">🔥 <b class="k">全期排名低估了 {r["short"]}</b>：{nm(r)} {len(years)} 年總數只排第 {r["rank"]}，'
                   f'但後半期（{span(L)}）以 {r["late"]} 題排第 <b>{r["lateRank"]}</b>——前半期 {r["early"]} 題、後半期 {r["late"]} 題。'
                   f'只看總排名會把它排得太後面。</div>')
    for r in rising:
        if r in under:
            continue
        ins.append(f'<div class="ins">▲ <b class="k">{r["short"]} 升溫</b>：{nm(r)} 前半期 {r["early"]} 題 → 後半期 {r["late"]} 題，'
                   f'近 {len(A["recent6"])} 考年出現 {r["r6h"]} 年、共 {r["r6q"]} 題。</div>')
    for r in frozen:
        s_note = (f'但仍以<b>副考點</b>出現在 {"、".join(map(str, r["lateSYears"]))}——它變成別題的第一步，'
                  f'觀念要懂、不必專門練。' if r["lateS"] else '後半期連副考點都沒有。')
        ins.append(f'<div class="ins cold">❄ <b class="k">{r["short"]} 冷凍</b>：{nm(r)} 最後一次當主考點是 {r["last"]} 年，'
                   f'後半期（{span(L)}）0 題；{s_note}</div>')
    for r in falling:
        ins.append(f'<div class="ins cold">▼ <b class="k">{r["short"]} 退燒</b>：{nm(r)} 前半期 {r["early"]} 題 → 後半期 {r["late"]} 題。</div>')
    ins_html = '<div class="insight">' + "".join(ins) + '</div>' if ins else ""

    # ---- 單元權重列 ----
    ur = ""
    palette = ["#1565c0", "#42a5f5", "#90caf9", "#bbdefb", "#e3f2fd"]
    for uid, name in A["unames"].items():
        t = A["unitTot"].get(uid, 0)
        ue, ul = A["unitEarly"].get(uid, 0), A["unitLate"].get(uid, 0)
        its = A["unitItems"].get(uid, [])
        segs = "".join(f'<span title="{r["short"]} {r["name"]}：{r["p"]} 題" style="width:{pct(r["p"], N)}%;background:{palette[i % len(palette)]}"></span>'
                       for i, r in enumerate(its))
        ur += (f'<tr><td><b>{uid}</b> {name}</td><td class="num">{t}</td><td class="num">{pct(t, N)}%</td>'
               f'<td class="num">{pct(ue, eT)}% → <b>{pct(ul, lT)}%</b></td>'
               f'<td><div class="ubar">{segs}</div></td>'
               f'<td style="font-size:.85em">{"、".join(r["short"] + " " + r["name"] + "（" + str(r["p"]) + "）" for r in its)}</td></tr>\n')
    tot_sorted = sorted(A["unitTot"].items(), key=lambda kv: -kv[1])
    if len(tot_sorted) >= 2 and tot_sorted[-1][1] > 0:
        hi, lo = tot_sorted[0], tot_sorted[-1]
        unit_note = (f'📌 換算成投資：最重的 <b>{hi[0]}</b>（{hi[1]} 題）是最輕的 <b>{lo[0]}</b>（{lo[1]} 題）的 '
                     f'<b>{round(hi[1] / lo[1], 1)} 倍</b>。')
    else:
        unit_note = "📌 各單元題數分布請見上表。"
    moved = sorted(A["unames"], key=lambda u: -abs(pct(A["unitLate"].get(u, 0), lT) - pct(A["unitEarly"].get(u, 0), eT)))
    if moved:
        u = moved[0]
        a, b = pct(A["unitEarly"].get(u, 0), eT), pct(A["unitLate"].get(u, 0), lT)
        if abs(b - a) >= 5:
            unit_note += f'　變動最大的是 <b>{u}</b>：佔比從前半期 {a}% {"升" if b > a else "降"}到後半期 {b}%。'
    if zero:
        unit_note += f'　另外 <b>{"、".join(r["short"] for r in zero)}</b> {len(years)} 個考年 0 題。'

    # ---- 讀書順序表（全部由資料生成）----
    chain = lambda ids: " → ".join(by_id[i]["short"] for i in ids)
    n5 = min(5, len(ordered))
    full5 = sum(1 for i in topN(n5) if len(by_id[i]["mat"]) == 4)
    late3 = late_order[:3]
    late3_sum = sum(r["late"] for r in late3)
    read = ""
    if ordered:
        read += (f'<tr><td><b>時間充裕，要拿高分</b></td><td>{chain(topN(n5))}</td>'
                 f'<td>全期前 {n5} 名，合計 {sumN(n5)} 題、佔 {pct(sumN(n5), N)}%'
                 f'{f"；其中 {full5} 個四種教材都已備齊" if full5 else ""}。</td></tr>\n')
    if late3:
        read += (f'<tr><td><b>只剩一個月</b></td><td>'
                 + "、".join(f'{r["short"]}（後半 {r["late"]} 題）' for r in late3) + '</td>'
                 f'<td>改用<b>後半期</b>（{span(L)}）排名：三者合計 {late3_sum}／{lT} 題、佔 {pct(late3_sum, lT)}%。'
                 f'比全期前三名更貼近現在的出題口味。</td></tr>\n')
    if tools:
        read += ('<tr><td><b>想補「每題都用得到」的基本功</b></td><td>'
                 + "、".join(f'{r["short"]}（主 {r["p"]}／副 {r["s"]}）' for r in tools) + '</td>'
                 '<td>副考點多於主考點——切到「主＋副」模式這幾列會變深，是別題的入口。</td></tr>\n')
    if r6_order:
        top2 = r6_order[:2]
        read += (f'<tr><td><b>想跟上近年走向</b></td><td>'
                 + "、".join(f'{r["short"]}（{r["r6q"]} 題／{r["r6h"]} 年）' for r in r6_order[:3]) + '</td>'
                 f'<td>近 {len(A["recent6"])} 考年（{span(A["recent6"])}）共 {r6T} 題，'
                 f'前兩名就佔 {sum(r["r6q"] for r in top2)} 題（{pct(sum(r["r6q"] for r in top2), r6T)}%）。'
                 f'看熱圖黃框那 {len(A["recent6"])} 欄可驗證。</td></tr>\n')
    if zero:
        read += (f'<tr><td><b>可以跳過</b></td><td>{"、".join(r["short"] for r in zero)}</td>'
                 f'<td>{len(years)} 年 0 題主考點。</td></tr>\n')
    if frozen:
        read += (f'<tr><td><b>放到最後（不是跳過）</b></td><td>'
                 + "、".join(f'{r["short"]}（最後 {r["last"]}）' for r in frozen) + '</td>'
                 f'<td>後半期 0 題主考點。'
                 + "".join(f'{r["short"]} 仍有 {r["lateS"]} 次副考點，觀念不能丟；' for r in frozen if r["lateS"])
                 + '時間不夠時最先砍的就是這幾個。</td></tr>\n')
    if not zero and not frozen:
        read += ('<tr><td><b>想知道哪些可以不讀</b></td><td>（無）</td>'
                 '<td>每個子項在後半期都還當過主考點，沒有可以整段跳過的。</td></tr>\n')

    col_note = (f'每一欄一定剛好 {A["perYear"]} 題，所以某年某子項考了 2 題，就代表那年別的子項被擠掉了。'
                if A["uniform"] else '最下方「每年合計」就是該年題數，可以直接讀出各子項之間的排擠關係。')
    year_desc = (f'{len(years)} 個考年 × 每年 {A["perYear"]} 題 = {N} 題'
                 if A["uniform"] else f'{len(years)} 個考年、共 {N} 題')
    kpi4 = "／".join(str(A["unitTot"].get(u, 0)) for u in A["unames"])
    kpi4l = "／".join(u.split("-")[-1] for u in A["unames"]) + " 各單元題數"
    hot = late_order[0] if late_order else None

    orphan_html = ""
    if A["orphan"]:
        orphan_html = ('<div class="role" style="background:#ffebee;border-color:#ef9a9a;border-left-color:#c62828">'
                       '⚠️ <b>資料異常</b>：索引裡有 taxonomy 找不到的 <code>primaryTopicId</code>：'
                       + "、".join(f"<code>{k}</code>×{v}" for k, v in A["orphan"].items())
                       + '。這些題目<b>沒有</b>畫進熱圖——請先修正 <code>question_index.json</code> 或 '
                         '<code>syllabus_taxonomy.json</code>。</div>')

    data_json = json.dumps({
        "years": years, "recent6": A["recent6"], "early": E, "late": L,
        "earlyTotal": eT, "lateTotal": lT, "rows": rows, "Q": A["Q"],
        "maxP": A["maxP"], "maxA": A["maxA"],
    }, ensure_ascii=False, separators=(",", ":"))

    return f"""<!DOCTYPE html>
<html lang="zh-Hant">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{subject} 全科出題頻率熱圖｜{subj_name}</title>
{CSS}
</head>
<body>
<header>
<h1>{subject} {subj_name} — 全科出題頻率熱圖</h1>
<p>{span(years)}，{year_desc}｜資料來源：raw/json/question_index.json｜更新日期 {today}</p>
</header>
<nav>
<a href="#s-sum">出題概況</a><a href="#s-heat">頻率熱圖</a><a href="#s-rank">排名總表</a><a href="#s-unit">各單元的權重</a><a href="#s-read">讀書順序</a>
</nav>
<main>

{orphan_html}
<div class="role">
📊 <b>這張表只回答一件事：整科該從哪裡開始讀。</b>
它把 {N} 題逐題攤在「{len(rows)} 個子項 × {len(years)} 個考年」的格子上，
並把考年切成前半（{span(E)}）與後半（{span(L)}）比較，讓你同時看到「誰一直重要」與「誰最近才重要」。
各子項的細節（考點結構、風險排序）看該子項的 <code>study-{subject}-Un-m.html</code> 命題分析頁。<br>
本頁由 <code>python {script_rel}</code> 從題庫自動產生；題庫或教材更新後重跑即可，請勿手改。
</div>

<h3 id="s-sum">出題概況</h3>
<div class="kpis">
<div class="kpi"><div class="n">{N}</div><div class="l">總題數（{year_desc}）</div></div>
<div class="kpi"><div class="n">{appeared}/{len(rows)}</div><div class="l">曾當過主考點的子項</div></div>
<div class="kpi"><div class="n">{top[1]}</div><div class="l">全期第一 {by_id[top[0]]["short"] if top[0] else "—"} 的題數（佔 {pct(top[1], N)}%）</div></div>
<div class="kpi hot"><div class="n">{hot["late"] if hot else 0}</div><div class="l">後半期第一 {hot["short"] if hot else "—"} 的題數（佔後半 {pct(hot["late"], lT) if hot else 0}%）</div></div>
<div class="kpi"><div class="n">{kpi4}</div><div class="l">{kpi4l}</div></div>
<div class="kpi"><div class="n">{A["nVerified"]}/{N}</div><div class="l">已人工驗證的解析</div></div>
</div>
{ins_html}

<h3 id="s-heat">頻率熱圖</h3>
<div class="btns" id="modebtns">
  <button class="fbtn on" onclick="setMode('p',this)">只看主考點</button>
  <button class="fbtn" onclick="setMode('a',this)">主考點 ＋ 副考點</button>
  <span class="hint">👆 點格子看該年題目；點子項名稱看它 {len(years)} 年的全部題目、影片與教材</span>
</div>
<div class="tw" id="heat"></div>
<div class="legend" id="lg"></div>
<div id="detail"></div>
<div id="tip"></div>
<div class="note">
📌 <b>看熱圖的四個切入點</b>：
① <b>橫著看</b>——有連續空白就是空窗年段。
② <b>直著看</b>——{col_note}
③ <b>左右比</b>——粗灰線左邊是前半期、右邊是後半期；子項名稱旁的 ▲／❄ 就是比較結果。
④ <b>切到「主＋副」</b>——整列變深的是「工具型子項」：很少單獨成題，卻是別題的第一步。
</div>

<h3 id="s-rank">排名總表</h3>
<div class="hint" style="margin-bottom:6px">點欄位名稱可排序（例如點「後半排名」看現在的強弱順序）</div>
<div class="tw" id="rank"></div>
<div class="note">
藍色＝主考點題數，橘色＝副考點題數。「前→後半」是 {span(E)} 與 {span(L)} 的主考點數比較：
差 3 題以上算升溫／退燒，後半期 0 題算冷凍。「後半排名」旁的 ↑ 代表比全期排名前進 3 名以上。
「常見題號位置」看得出這個子項是短題還是壓軸長計算題。「現有教材」綠色可點、灰色尚未製作；🎬 點開看影片清單。
</div>

<h3 id="s-unit">各單元的權重</h3>
<div class="tw">
<table>
<thead><tr><th>單元</th><th class="num">主考點題數</th><th class="num">佔全科</th><th class="num">前半 → 後半佔比</th><th>子項組成</th><th>包含的子項（題數）</th></tr></thead>
<tbody>
{ur}</tbody>
</table>
</div>
<div class="note">{unit_note}</div>

<h3 id="s-read">怎麼用這張表排讀書順序</h3>
<div class="tw">
<table>
<thead><tr><th>如果你…</th><th>先讀哪幾個子項</th><th>理由（可從熱圖直接驗證）</th></tr></thead>
<tbody>
{read}</tbody>
</table>
</div>
<div class="note">
📌 <b>一句話</b>：這張表告訴你「該讀哪裡」，<code>study-{subject}-Un-m.html</code> 告訴你「那裡該先練哪幾題」，
<code>formula-given-{subject}-Un-m.html</code> 告訴你「那裡哪些公式非背不可」。<br>
⚠️ <b>使用提醒</b>：頻率高不等於一定會再考，冷凍也不等於不會回來——這張表的用途是<b>分配時間</b>，不是預測考題。
押題請看各子項命題分析頁的「命題風險排序」。
</div>

</main>
<footer>{subject} 全科出題頻率熱圖｜exam-wiki-{subject}｜統計基準 raw/json/question_index.json（{N} 題／{len(years)} 考年）｜產生器 <code>{script_rel}</code></footer>
{JS.replace('__DATA__', data_json)}
</body>
</html>
"""


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--subject", help="科目代碼（SS/RC/SA/SD/SM/MM）。不給就從 moduleId 自動偵測")
    ap.add_argument("--index", default="raw/json/question_index.json")
    ap.add_argument("--taxonomy", default="raw/json/syllabus_taxonomy.json")
    ap.add_argument("--study-dir", default="study")
    ap.add_argument("--video-dir", default="解題過程影片")
    ap.add_argument("--out", help="輸出路徑，預設 <study-dir>/frequency-XX.html")
    ap.add_argument("--date", help="頁面上的更新日期，預設今天")
    ap.add_argument("--check", action="store_true", help="只跑對帳與摘要，不寫檔")
    a = ap.parse_args()
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

    for p in (a.index, a.taxonomy):
        if not os.path.exists(p):
            sys.exit(f"錯誤：找不到 {p}。請在知識庫根目錄執行，或用 --index / --taxonomy 指定。")

    qs = load_index(a.index)
    subject = a.subject or detect_subject(qs)
    subj_name, items, unames = load_taxonomy(a.taxonomy, subject)
    out = a.out or os.path.join(a.study_dir, f"frequency-{subject}.html")
    out_dir = os.path.dirname(out) or "."
    tids = [t for t, _, _ in items]
    qids = {q["moduleId"] for q in qs}
    if not os.path.isdir(a.study_dir):
        print(f"⚠️  找不到 {a.study_dir}/，教材欄位會全部顯示為未製作。")
    materials = scan_materials(a.study_dir, out_dir, tids)
    topic_v, q_v = scan_videos(a.video_dir, out_dir, tids, qids)
    pv = os.path.join(a.study_dir, "problems-view")
    views = {os.path.splitext(f)[0] for f in os.listdir(pv)} if os.path.isdir(pv) else set()
    A = analyse(qs, items, unames, materials, topic_v, q_v, views)

    errs, warns = check(A)
    Y, L, E = A["years"], A["late"], A["early"]
    print(f"科目 {subject} {subj_name}｜{len(Y)} 考年（{Y[0]}–{Y[-1]}）｜{A['total']} 題｜"
          f"{len(items)} 個子項（{sum(1 for r in A['rows'] if r['p'])} 個出現過）")
    print("單元權重：" + "　".join(
        f"{u} {A['unitTot'].get(u, 0)} ({round(A['unitTot'].get(u, 0) / A['total'] * 100, 1)}%)" for u in unames))
    if A["ordered"]:
        print("全期前五：" + "、".join(f"{k.split('-', 1)[1]} {v}" for k, v in A["ordered"][:5])
              + f"　合計 {sum(v for _, v in A['ordered'][:5])} 題")
    print(f"後半期（{L[0]}–{L[-1]}）前五：" + "、".join(f"{r['short']} {r['late']}" for r in A["lateOrder"][:5]))
    print("前→後半：" + "　".join(f"{r['short']} {r['early']}→{r['late']}({r['drift']})" for r in A["rows"]))
    tools = [r for r in A["rows"] if r["s"] > r["p"]]
    print("副>主 的工具型子項：" + ("、".join(f"{r['short']}({r['p']}/{r['s']})" for r in tools) or "無"))
    print("0 題子項：" + ("、".join(r["short"] for r in A["rows"] if r["p"] == 0) or "無"))
    print("冷凍子項（後半期 0 題）：" + ("、".join(f"{r['short']}(最後 {r['last']})" for r in A["rows"] if r["drift"] == "frozen") or "無"))
    print(f"教材齊全（四種都有）：{'、'.join(r['short'] for r in A['rows'] if len(r['mat']) == 4) or '無'}")
    print(f"影片：單元 {A['nTvid']} 支、題目 {A['nQvid']} 支｜problems-view 頁 {len(views & qids)} 題｜已驗證 {A['nVerified']} 題")

    for w in warns:
        print("⚠️  " + w)
    if errs:
        print("\n❌ 對帳不通過：")
        for e in errs:
            print("   - " + e)
        sys.exit(1)
    print("\n✅ 對帳通過（格子總和＝題庫總題數、每列總和＝該子項題數、前＋後半＝總數、單元小計相符）"
          + ("　※ 有警告，請看上面" if warns else ""))
    if a.check:
        return

    import datetime
    today = a.date or datetime.date.today().isoformat()
    os.makedirs(out_dir, exist_ok=True)
    script_rel = rel(os.path.abspath(__file__), os.getcwd())
    html = build_html(subject, subj_name, A, today, script_rel)
    with open(out, "w", encoding="utf-8") as f:
        f.write(html)
    print(f"\n寫出 {out}（{len(html):,} 字元）")


if __name__ == "__main__":
    main()

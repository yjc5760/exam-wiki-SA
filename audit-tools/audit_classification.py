#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""exam-wiki 分類一致性稽核（六科通用，唯讀）
用法：python audit_classification.py <repo根目錄> <科目代號> [--out 報告.md]
以 raw/json/question_index.json 為準，比對：
  A 索引自身：主分類代號不存在於大綱、指向他科、名稱與大綱不符、副分類含主分類或他科代號、有題解資料夾但索引無此題
  B 題解正本 raw/solutions/<id>/<id>.md 標頭（主分類／副分類／設計法）
wiki 各層（problems、topics 等）已於 2026-11 封存到 archive/wiki/，不再維護，故不比對。
"""
import argparse, json, re
from collections import defaultdict
from pathlib import Path

UID = re.compile(r"\b([A-Z]{2}-U\d+-\d+)\b")
UNIT = re.compile(r"\b([A-Z]{2}-U\d+)\b(?!-)")
ALIAS = {"主分類": "主分類|科目分類", "副分類": "副分類", "設計法": "設計法|分析方法"}
HDR = {k: re.compile(rf"(?m)^(?:\*\*(?:{a})[：:]\*\*|(?:{a})\s*[:：]|\|\s*(?:{a})\s*\|)\s*(.+)") for k, a in ALIAS.items()}


def load(root, subj):
    q = json.loads((root / "raw/json/question_index.json").read_text(encoding="utf-8"))
    Q = q["questions"] if isinstance(q, dict) else q
    tax = json.loads((root / "raw/json/syllabus_taxonomy.json").read_text(encoding="utf-8"))
    names = {i["id"]: i["name"] for s in tax["subjects"] for u in s["units"] for i in u["items"]}
    qs = {}
    for x in Q:
        mid = x.get("moduleId") or x.get("id") or x.get("questionId")
        if mid and mid.startswith(subj + "-"):
            qs[mid] = x
    return qs, names


def method(x):
    return x.get("designMethod") or x.get("analysisMethod")


def header(path):
    if not path.exists():
        return None
    head = "\n".join(path.read_text(encoding="utf-8", errors="replace").replace("\x00", "").splitlines()[:25])
    out = {}
    for k, rx in HDR.items():
        m = rx.search(head)
        out[k] = (UID.findall(m.group(1)) if k != "設計法" else m.group(1).strip()) if m else None
        if k == "主分類" and m and not out[k] and UNIT.search(m.group(1)):
            out["unit_only"] = UNIT.search(m.group(1)).group(1)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root"); ap.add_argument("subject"); ap.add_argument("--out")
    a = ap.parse_args()
    root, S = Path(a.root), a.subject
    qs, names = load(root, S)
    iss = defaultdict(list)
    norm = lambda s: re.sub(r"[\s（）()]", "", s or "")

    for qid, x in qs.items():
        p, sec = x.get("primaryTopicId"), list(x.get("secondaryTopicIds") or [])
        if p not in names:
            iss[qid].append(("A 索引", f"主分類 {p} 不在命題大綱"))
        elif not p.startswith(S + "-"):
            iss[qid].append(("A 索引", f"主分類 {p} 指向他科"))
        elif x.get("primaryTopicName") and norm(x["primaryTopicName"]) != norm(names[p]):
            iss[qid].append(("A 索引", f"primaryTopicName「{x['primaryTopicName']}」≠ 大綱「{names[p]}」"))
        for s in sec:
            if s == p: iss[qid].append(("A 索引", f"副分類重複列入主分類 {s}"))
            elif not s.startswith(S + "-"): iss[qid].append(("A 索引", f"副分類 {s} 指向他科"))
            elif s not in names: iss[qid].append(("A 索引", f"副分類 {s} 不在命題大綱"))
        lab, path = "B 題解正本", root / f"raw/solutions/{qid}/{qid}.md"
        h = header(path)
        if h is None:
            iss[qid].append((lab, "檔案不存在")); continue
        if not h["主分類"]:
            if h.get("unit_only"):
                iss[qid].append((lab, f"主分類只寫到單元層級 {h['unit_only']}（索引為 {p}）"))
            else:
                iss[qid].append((lab, "標頭缺主分類"))
            continue
        if h["主分類"][:1] != [p]:
            iss[qid].append((lab, f"主分類 {h['主分類']} ≠ 索引 {p}"))
        if h["副分類"] is not None and sorted(h["副分類"]) != sorted(sec):
            iss[qid].append((lab, f"副分類 {h['副分類']} ≠ 索引 {sorted(sec)}"))
        if h["設計法"] and method(x) and len(norm(method(x))) <= 8 and norm(h["設計法"]).split("（")[0] != norm(method(x)):
            if norm(method(x)) not in norm(h["設計法"]):
                iss[qid].append((lab, f"設計法「{h['設計法']}」≠ 索引「{method(x)}」"))

    for d in sorted((root / "raw/solutions").glob(f"{S}-*")):
        if d.is_dir() and re.fullmatch(rf"{S}-\d{{4}}-\d+", d.name) and d.name not in qs:
            iss[d.name].append(("A 索引", "有題解資料夾但索引無此題"))

    cnt = defaultdict(int)
    for v in iss.values():
        for c, _ in v: cnt[c] += 1
    L = [f"# 分類一致性稽核 — {S}", "", f"索引 {len(qs)} 題；有問題 {len(iss)} 題、{sum(cnt.values())} 筆", "",
         "| 檢查 | 筆數 |", "|---|---|"] + [f"| {c} | {n} |" for c, n in sorted(cnt.items())] + [""]
    for q in sorted(iss):
        x = qs.get(q, {})
        L.append(f"## {q}　索引：{x.get('primaryTopicId','—')} 主／{x.get('secondaryTopicIds','—')} 副")
        L += [f"- **{c}**　{d}" for c, d in iss[q]] + [""]
    rep = "\n".join(L)
    if a.out: Path(a.out).write_text(rep, encoding="utf-8")
    print("\n".join(L[:7 + len(cnt)]))


if __name__ == "__main__":
    main()

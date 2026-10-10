"""Phase 4 prototype: aggregate digests -> concept cards (deterministic, no LLM).

Usage: python -I scripts/build_concepts.py [digest-subdir ...]   (default: pages/huayan28)
Writes kb/concepts/<term>.md and kb/concepts/INDEX.md, kb/frameworks/INDEX.md.
A concept = a `term` that appears in some digest's `concepts`. For each, we gather
every definition/explanation, quotes, and every teaching (in any lecture) whose
claim mentions the term, so repetition across lectures becomes visible.
Name variants are NOT merged here (that needs judgment); near-duplicates are listed in INDEX.
"""
import collections, glob, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
subs = sys.argv[1:] or ["pages/huayan28"]
docs = []
for sub in subs:
    for f in glob.glob(f"kb/digests/{sub}/*.json"):
        docs.append(json.load(open(f, encoding="utf8")))
def lec_key(d):
    m = re.search(r"(\d+)$", d["id"]); return int(m.group(1)) if m else 0
docs.sort(key=lec_key)
def short(d): return d["title"] or d["id"].split("/")[-1]
def norm(t): return re.sub(r"[\s·、，,。《》“”\"'（）()]", "", t)
def safe(t): return re.sub(r'[\/:*?"<>|]', "_", t)[:60]

terms = collections.OrderedDict()
for d in docs:
    for c in d["concepts"]:
        k = norm(c["term"])
        if not k: continue
        e = terms.setdefault(k, {"names": collections.Counter(), "entries": []})
        e["names"][c["term"]] += 1
        e["entries"].append((d, c))

cards = []
os.makedirs("kb/concepts", exist_ok=True)
for k, e in terms.items():
    mentions = collections.OrderedDict()
    for d in docs:
        hits = [t for t in d["teachings"] if len(k) >= 2 and k in norm(t["claim"])]  # only single characters are skipped (they match inside other words)
        defs = [c for c in d["concepts"] if norm(c["term"]) == k]
        if hits or defs:
            mentions[d["id"]] = (d, hits, defs)
    name = e["names"].most_common(1)[0][0]
    fws = sorted({f["name"] for d in docs for f in d["frameworks"] if k in norm(f["name"]) or any(k in norm(i) for i in f.get("items", []))})
    n_lect = len(mentions); n_teach = sum(len(v[1]) for v in mentions.values())
    L = [f"# {name}\n"]
    if len(e["names"]) > 1: L.append("别写：" + "、".join(n for n in e["names"] if n != name) + "\n")
    L.append(f"出现于 {n_lect} 讲，相关论述 {n_teach} 条。\n")
    L.append("## 各讲对它的说明\n")
    for did, (d, hits, defs) in mentions.items():
        for c in defs:
            if c["definition"]:
                L.append(f"- **{short(d)}**（{c['role']}）：{c['definition']}")
                if c.get("quote"): L.append(f"  - 原文：「{c['quote']}」")
    L.append("\n## 相关论述（按讲）\n")
    for did, (d, hits, defs) in mentions.items():
        if hits:
            L.append(f"### {short(d)}")
            for t in hits[:6]:
                tag = "（引文）" if t.get("from") == "cited_text" else ""
                L.append(f"- {t['claim']}{tag}")
            if len(hits) > 6: L.append(f"- …另有 {len(hits)-6} 条")
    if fws: L.append("\n## 相关框架\n" + "\n".join(f"- {f}" for f in fws))
    open(f"kb/concepts/{safe(name)}.md", "w", encoding="utf8").write("\n".join(L) + "\n")
    cards.append((n_lect, n_teach, name, len(e["entries"])))

cards.sort(key=lambda x: (-x[0], -x[1]))
I = [f"# 概念索引（{len(cards)} 条，来自 {len(docs)} 篇摘要）\n", "按出现讲数排序。\n", "| 概念 | 讲数 | 论述数 |", "|---|---:|---:|"]
I += [f"| [{n}]({safe(n)}.md) | {a} | {b} |" for a, b, n, _ in cards]
open("kb/concepts/INDEX.md", "w", encoding="utf8").write("\n".join(I) + "\n")

fw = collections.OrderedDict()
for d in docs:
    for f in d["frameworks"]:
        e = fw.setdefault(norm(f["name"]), {"name": f["name"], "lects": [], "items": []})
        e["lects"].append((short(d), f["treatment"]))
        if f.get("items") and len(f["items"]) > len(e["items"]): e["items"] = f["items"]
F = [f"# 框架索引（{len(fw)} 个）\n", "同一框架在不同讲里的命名可能不一致，待合并。\n"]
for k, e in sorted(fw.items(), key=lambda kv: -len(kv[1]["lects"])):
    F.append(f"## {e['name']}\n出现：" + "、".join(f"{l}({t})" for l, t in e["lects"]))
    if e["items"]: F.append("条目（最完整的一次）：" + "；".join(e["items"]))
    F.append("")
os.makedirs("kb/frameworks", exist_ok=True)
open("kb/frameworks/INDEX.md", "w", encoding="utf8").write("\n".join(F) + "\n")
print(len(cards), "concept cards;", len(fw), "frameworks; top:", cards[:10])

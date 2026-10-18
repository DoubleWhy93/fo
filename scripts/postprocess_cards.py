"""Phase 4 step 3 (deterministic): cross-card checks and indexes over kb/consolidated/concepts/*.json.

Usage: python -I scripts/postprocess_cards.py
 - recomputes `pages_consulted` for every card = distinct pages cited in its quotes + where_to_read
 - resolves `related` names against card terms/keys/aliases; unresolved names are recorded in `related_unresolved`
 - reports alias collisions (an alias that is another card's term) and likely duplicate cards
 - writes kb/consolidated/INDEX.md, kb/consolidated/tensions.md, kb/consolidated/checks.md
Cards are only modified for the two derived fields (`pages_consulted`, `related_unresolved`).
"""
import collections, glob, json, os, re, sys
import opencc

sys.stdout.reconfigure(encoding="utf-8")
T2S = opencc.OpenCC("t2s").convert
D = "kb/consolidated"


def norm(t):
    return re.sub(r"[\s·、，,。《》“”\"'（）()：:；;\-—]", "", T2S(t or ""))


cards = {}
for f in sorted(glob.glob(f"{D}/concepts/*.json")):
    c = json.load(open(f, encoding="utf8"))
    c["_file"] = f
    cards[c["key"]] = c

# --- name resolution table
names = {}
for k, c in cards.items():
    names.setdefault(norm(c["term"]), k)
    names.setdefault(norm(k), k)
for k, c in cards.items():
    for a in c.get("aliases", []):
        names.setdefault(norm(a), k)
# frameworks, 华严经 品 names and same-thing variants (kb/consolidated/related-map.json) also count as resolved
for f in glob.glob(f"{D}/frameworks/*.json"):
    names.setdefault(norm(json.load(open(f, encoding="utf8"))["name"]), "framework")
for i in json.load(open("kb/sutra/huayan80/index.json", encoding="utf8")):
    names.setdefault(norm(i["title"]), "pin")
RMAP = {k: v for k, v in json.load(open(f"{D}/related-map.json", encoding="utf8")).items() if not k.startswith("_")}
for var, target in RMAP.items():
    if norm(target) in names:
        names.setdefault(norm(var), names[norm(target)])

changed = 0
unresolved_total = 0
for k, c in cards.items():
    pages = set(c.get("where_to_read", []))
    for q in c.get("definition_basis", []):
        pages.add(q["src"])
    for a in c.get("aspects", []):
        pages.update(q["src"] for q in a.get("quotes", []))
    for t in c.get("tensions", []):
        pages.update(q["src"] for q in t.get("sources", []))
    unres = []
    for r in c.get("related", []):
        if norm(r) not in names and norm(r) != norm(c["term"]):
            unres.append(r)
    unresolved_total += len(unres)
    new = {"pages_consulted": len(pages), "related_unresolved": unres}
    if any(c.get(x) != y for x, y in new.items()):
        c.update(new)
        out = {x: y for x, y in c.items() if not x.startswith("_")}
        json.dump(out, open(c["_file"], "w", encoding="utf8"), ensure_ascii=False, indent=1)
        changed += 1

# --- alias collisions and duplicates
coll = []
for k, c in cards.items():
    for a in c.get("aliases", []):
        o = names.get(norm(a))
        own_term = norm(c["term"])
        for k2, c2 in cards.items():
            if k2 != k and (norm(c2["term"]) == norm(a)):
                coll.append((c["term"], a, c2["term"]))
dups = []
terms = {k: norm(c["term"]) for k, c in cards.items()}
byn = collections.defaultdict(list)
for k, n in terms.items():
    byn[n].append(k)
for n, ks in byn.items():
    if len(ks) > 1:
        dups.append(("same after normalisation", ks))
tl = sorted(terms.items(), key=lambda kv: len(kv[1]))
for i, (k1, n1) in enumerate(tl):
    for k2, n2 in tl[i + 1:]:
        if n1 != n2 and len(n1) >= 3 and n1 in n2 and len(n2) - len(n1) <= 6:
            r1 = {norm(r) for r in cards[k1].get("related", [])}
            r2 = {norm(r) for r in cards[k2].get("related", [])}
            if n2 in r1 and n1 in r2:
                continue        # reviewed pair kept on purpose (see merge-log.md): they cross-link each other
            dups.append(("one contains the other", [k1, k2]))

# --- tensions
tens = []
for k, c in cards.items():
    for t in c.get("tensions", []):
        tens.append((c["term"], t["text"], [s["src"] for s in t.get("sources", [])]))

# --- writing outputs
conf = collections.Counter(c["confidence"] for c in cards.values())
with_t = sum(1 for c in cards.values() if c.get("tensions"))
L = ["# 概念卡索引\n", f"{len(cards)} 张卡；置信度：高 {conf['high']} · 中 {conf['medium']} · 低 {conf['low']}；"
     f"含分歧说明的 {with_t} 张。\n",
     "| 概念 | 摘要 | 页数 | 分歧 | 置信 |", "|---|---|---:|---:|---|"]
for k, c in sorted(cards.items(), key=lambda kv: -len(kv[1].get("by_series", [])) - kv[1].get("pages_consulted", 0) / 100):
    L.append(f"| {c['term']} | {c['summary']} | {c.get('pages_consulted', 0)} | {len(c.get('tensions', []))} | {c['confidence']} |")
open(f"{D}/INDEX.md", "w", encoding="utf8").write("\n".join(L) + "\n")

T = [f"# 讲稿内部的不同说法（{len(tens)} 条）\n",
     "各概念卡中记录的“不同页面说法不一”之处，只汇集，不裁决。每条在对应概念卡里附有原文引用。\n"]
stage = re.compile(r"位|地|住|行|向|信|觉")
for term, text, srcs in sorted(tens):
    T.append(f"- **{term}**：{text}")
open(f"{D}/tensions.md", "w", encoding="utf8").write("\n".join(T) + "\n")

C = ["# 跨卡检查\n", f"- 卡片 {len(cards)} 张；`pages_consulted` 已按引文页重算（改动 {changed} 张）",
     f"- `related` 中无法对应到任何卡的名称：{unresolved_total} 个（记录在各卡的 `related_unresolved`）\n",
     f"## 别名与另一张卡同名（{len(coll)}）\n"]
C += [f"- {a} 的别名「{b}」本身就是卡「{c}」" for a, b, c in coll] or ["- 无"]
C.append(f"\n## 可能重复或应合并的卡（{len(dups)}）\n")
C += [f"- {why}：" + "、".join(cards[k]["term"] for k in ks) for why, ks in dups] or ["- 无"]
open(f"{D}/checks.md", "w", encoding="utf8").write("\n".join(C) + "\n")
print(f"{len(cards)} cards; pages_consulted rewritten on {changed}; unresolved related {unresolved_total}; "
      f"alias collisions {len(coll)}; duplicate/overlap candidates {len(dups)}; tensions {len(tens)}")

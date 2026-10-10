"""Assemble everything the digests know about a concept into one bundle (markdown).

Usage: python -I scripts/kb_bundle.py <name> <alias1,alias2,...> [max_teachings]
Writes kb/bundles/<name>.md. Matching is by simple substring on Simplified text
(aliases), over all digests under kb/digests. This is deliberately dumb: it is the
test of whether the digests alone carry enough to write a good page.
"""
import collections, glob, json, os, re, sys
sys.stdout.reconfigure(encoding="utf-8")
name, aliases = sys.argv[1], [a for a in sys.argv[2].split(",") if a]
max_t = int(sys.argv[3]) if len(sys.argv) > 3 else 70
related = [a for a in (sys.argv[4].split(",") if len(sys.argv) > 4 else []) if a]  # extra aliases, used for examples/how-to only
norm = lambda s: re.sub(r"[\s·、，,。《》“”\"'（）()『』「」]", "", s or "")
hit = lambda s: any(a in norm(s) for a in aliases)
hit2 = lambda s: any(a in norm(s) for a in aliases + related)

def _num(sid):
    m = re.search(r"(\d+)$", sid.split("/")[-1])
    return int(m.group(1)) if m else 0
def label(sid):
    if "/huayan28/" in sid: return f"二十八讲·第{_num(sid)}讲"
    if "/huayan70/" in sid: return f"七十讲·第{_num(sid)}讲" if _num(sid) else "七十讲·目录"
    return sid.split("/")[-1]
def order(sid):
    return (0 if "/huayan28/" in sid else 1, _num(sid))

docs = []
for f in glob.glob("kb/digests/pages/*/*.json"):
    docs.append(json.load(open(f, encoding="utf8")))
docs.sort(key=lambda d: order(d["id"]))

defs, exs, hows, teach, prereq, fws = [], [], [], [], collections.Counter(), []
pages_with = 0
for d in docs:
    L = label(d["id"]); found = False
    for c in d["concepts"]:
        if hit(c["term"]):
            found = True
            if c.get("plain") or c.get("definition"):
                defs.append((L, c["term"], c.get("role", ""), c.get("plain", ""), c.get("definition", ""), c.get("quote", "")))
    for e in d.get("examples", []):
        if hit2(e.get("illustrates", "")) or hit2(e.get("point", "")) or hit2(e.get("setup", "")):
            found = True; exs.append((L, e))
    for h in d.get("how_to", []):
        if hit2(h.get("situation", "")) or any(hit2(s) for s in h.get("steps", [])):
            found = True; hows.append((L, h))
    for t in d["teachings"]:
        if hit(t["claim"]):
            found = True; teach.append((L, t))
    for fw in d["frameworks"]:
        if hit(fw["name"]): fws.append((L, fw["name"], fw.get("treatment", ""), fw.get("items", [])))
    if found:
        pages_with += 1
        for p in d.get("prerequisites", []): prereq[p] += 1

# prefer teachings that define/explain; dedupe by claim prefix
rank = {"definition": 0, "criterion": 1, "method": 2, "warning": 3, "structure": 4, "cross_reference": 5, "fashu": 6, "history": 7, "chronology": 8, "other": 9}
seen = set(); picked = []
for L, t in sorted(teach, key=lambda x: (rank.get(x[1]["kind"], 9), len(x[1]["claim"]) > 260)):
    k = t["claim"][:30]
    if k in seen: continue
    seen.add(k); picked.append((L, t))
picked = picked[:max_t]

out = [f"# Bundle: {name}  (aliases: {', '.join(aliases)})", "",
       f"Matched in {pages_with} of {len(docs)} digested pages. {len(defs)} definition/plain entries, {len(exs)} examples, {len(hows)} how-to, "
       f"{len(teach)} teachings (showing {len(picked)}). Quotes are verbatim Traditional text from the source; prose is Simplified.", ""]
out.append("## Plain definitions / explanations\n")
for L, term, role, plain, df, q in defs[:60]:
    out.append(f"- [{L}] **{term}** ({role}) {plain or df}" + (f"\n  - 原文: 「{q}」" if q else ""))
out.append("\n## Examples (author's analogies, cases, stories, dialogues)\n")
for L, e in exs[:45]:
    out.append(f"- [{L}] ({e['kind']}) illustrates: {e.get('illustrates','')}\n  - setup: {e.get('setup','')}\n  - point: {e.get('point','')}\n  - 原文: 「{e.get('quote','')}」")
out.append("\n## How-to / step-by-step guidance\n")
for L, h in hows[:25]:
    out.append(f"- [{L}] {h.get('situation','')}\n  - steps: " + " → ".join(h.get("steps", [])) + f"\n  - 原文: 「{h.get('quote','')}」")
out.append("\n## Teachings (definitions and criteria first)\n")
for L, t in picked:
    out.append(f"- [{L}] ({t['kind']}{', cited: '+t.get('cited_source','') if t.get('from')=='cited_text' else ''}) {t['claim']}\n  - 原文: 「{t.get('quote','')}」")
out.append("\n## Frameworks that mention it\n")
for L, n, tr, items in fws[:25]:
    out.append(f"- [{L}] {n} ({tr})" + (": " + "；".join(items[:12]) if items else ""))
out.append("\n## Prerequisite terms most often listed on those pages\n")
out.append("、".join(f"{k}({v})" for k, v in prereq.most_common(25)))
open(f"kb/bundles/{name}.md", "w", encoding="utf8").write("\n".join(out) + "\n")
print(name, "pages", pages_with, "defs", len(defs), "ex", len(exs), "how", len(hows), "teach", len(teach), "->", f"{os.path.getsize(f'kb/bundles/{name}.md')//1024} KB")

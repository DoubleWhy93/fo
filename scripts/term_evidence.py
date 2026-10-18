"""Collect what the digests say about a term — for writing a concept card for a term that has few concept entries
(e.g. a stage name like 十住位 that the lectures treat as a stage rather than a defined term).

Usage: python -I scripts/term_evidence.py <out.md> <term> [variant ...]
Searches every digest (kb/digests/**) for: concept entries naming the term, teachings / outline points / frameworks /
Q&A answers whose text mentions it. Prints them grouped by series (round-robin, so every series is represented),
each with its page id and verbatim quote — quotes are verified digest quotes, reusable as card quotes as they stand.
"""
import collections, glob, json, re, sys
import opencc

sys.stdout.reconfigure(encoding="utf-8")
S = opencc.OpenCC("t2s").convert
out, terms = sys.argv[1], [S(t) for t in sys.argv[2:]]
hit = lambda s: any(t in S(s or "") for t in terms)


def series(pid):
    p = pid.split("/")
    return "答疑" if p[1].startswith("dayi") else p[1]


defs, teach, qa, fw = [], [], [], []
for f in sorted(glob.glob("kb/digests/**/*.json", recursive=True)):
    d = json.load(open(f, encoding="utf8"))
    pid = d["id"]
    for c in d.get("concepts", []):
        if hit(c.get("term")) and (c.get("definition") or c.get("plain")):
            defs.append((pid, f"[{c.get('role')}] {c.get('term')}: {c.get('definition') or c.get('plain')}", c.get("quote", "")))
    for t in d.get("teachings", []):
        if hit(t.get("claim")):
            teach.append((pid, t["claim"], t.get("quote", "")))
    for x in d.get("qa", []):
        if hit(x.get("question")) or hit(x.get("answer_summary")):
            qa.append((pid, f"问：{x.get('question')} 答：{x.get('answer_summary')}", x.get("quote", "")))
    for x in d.get("frameworks", []):
        if hit(x.get("name")) or any(hit(i) for i in x.get("items", [])):
            fw.append((pid, f"{x.get('name')}: " + " / ".join(x.get("items", [])), ""))


def spread(items, cap):
    g = collections.OrderedDict()
    for it in items:
        g.setdefault(series(it[0]), []).append(it)
    res = []
    while len(res) < cap and any(g.values()):
        for k in list(g):
            if g[k] and len(res) < cap:
                res.append(g[k].pop(0))
    return res


L = [f"# Evidence for {' / '.join(terms)}\n",
     f"concept entries {len(defs)}, teachings {len(teach)}, Q&A {len(qa)}, frameworks {len(fw)}\n"]
for title, items, cap in (("Concept entries", defs, 40), ("Teachings mentioning it", teach, 60), ("Q&A", qa, 25), ("Frameworks", fw, 15)):
    L.append(f"\n## {title}\n")
    for pid, text, q in spread(items, cap):
        L.append(f"- {pid} | {text}" + (f"\n  quote: 「{q}」" if q else ""))
open(out, "w", encoding="utf8").write("\n".join(L) + "\n")
print(f"{out}: {len(defs)} concept entries, {len(teach)} teachings, {len(qa)} Q&A, {len(fw)} frameworks")

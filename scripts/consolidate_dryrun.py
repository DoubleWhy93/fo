"""Phase 4 dry-run: how well do the digests consolidate? Deterministic, no LLM, read-only.

Usage: python -I scripts/consolidate_dryrun.py
Reads every kb/digests/**/*.json and writes kb/analysis/consolidation-dryrun.md. It does not
touch kb/concepts or any digest. The report answers: how many distinct concepts really exist,
which ones are defined (and which are only ever "used"), where definitions look different
across lectures (candidate contradictions / drift), which terms look like variants of each other,
which frameworks have inconsistent member lists, and how healthy the digest schema usage is.
"""
import collections, glob, itertools, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
OUT = "kb/analysis/consolidation-dryrun.md"


def norm(t):
    return re.sub(r"[\s·、，,。《》“”\"'（）()：:；;\-—]", "", t or "")


def bigrams(s):
    s = norm(s)
    return {s[i:i + 2] for i in range(len(s) - 1)} or {s}


def jacc(a, b):
    A, B = bigrams(a), bigrams(b)
    return len(A & B) / max(1, len(A | B))


def series_of(did):
    p = did.split("/")
    if p[1] == "dayi_all":
        return "dayi_all/" + (p[2] if len(p) > 3 else "")
    return p[1]


docs = []
for f in glob.glob("kb/digests/**/*.json", recursive=True):
    d = json.load(open(f, encoding="utf8"))
    d["_series"] = series_of(d["id"])
    docs.append(d)
docs.sort(key=lambda d: d["id"])

L = []
add = L.append

# ---- 1. inventory
by_series = collections.Counter(d["_series"] for d in docs)
n_teach = sum(len(d.get("teachings", [])) for d in docs)
n_conc = sum(len(d.get("concepts", [])) for d in docs)
add("# Consolidation dry-run\n")
add(f"{len(docs)} digests · {n_teach} teachings · {n_conc} concept entries · "
    f"{sum(len(d.get('frameworks', [])) for d in docs)} framework entries\n")
add("| series | digests |\n|---|---:|")
for s, n in by_series.most_common():
    add(f"| {s} | {n} |")

# ---- 2. term merging
terms = {}
for d in docs:
    for c in d.get("concepts", []):
        k = norm(c.get("term", ""))
        if len(k) < 2:
            continue
        e = terms.setdefault(k, {"names": collections.Counter(), "pages": set(), "series": set(),
                                 "roles": collections.Counter(), "defs": []})
        e["names"][c["term"]] += 1
        e["pages"].add(d["id"])
        e["series"].add(d["_series"])
        e["roles"][c.get("role", "?")] += 1
        txt = (c.get("definition") or "").strip() or (c.get("plain") or "").strip()
        if txt and c.get("role") in ("defined", "explained"):
            e["defs"].append((d["id"], d["_series"], c.get("role"), txt))
n_terms = len(terms)
spread = {k: len(v["pages"]) for k, v in terms.items()}
add(f"\n## Concepts\n\n{n_concepts_str if False else ''}")
add(f"- distinct normalized terms: **{n_terms}** (from {n_conc} entries)")
for th in (2, 3, 5, 10, 20):
    add(f"- terms in ≥{th} pages: {sum(1 for v in spread.values() if v >= th)}")
add(f"- terms in ≥2 series: {sum(1 for v in terms.values() if len(v['series']) >= 2)}")
add(f"- terms with at least one definition/explanation: {sum(1 for v in terms.values() if v['defs'])}")
only_once = sum(1 for v in spread.values() if v == 1)
add(f"- terms seen on a single page only: {only_once} ({only_once * 100 // max(1, n_terms)}%)")

add("\n### Most widespread concepts\n")
add("| term | pages | series | defined | explained | used |\n|---|---:|---:|---:|---:|---:|")
for k, v in sorted(terms.items(), key=lambda kv: -len(kv[1]["pages"]))[:40]:
    r = v["roles"]
    add(f"| {v['names'].most_common(1)[0][0]} | {len(v['pages'])} | {len(v['series'])} | "
        f"{r['defined']} | {r['explained']} | {r['used']} |")

# ---- 3. gaps: widespread but never defined
add("\n### Widely used but never defined or explained anywhere (needs a definition from elsewhere)\n")
gaps = [(k, v) for k, v in terms.items() if len(v["pages"]) >= 5 and not v["defs"]]
for k, v in sorted(gaps, key=lambda kv: -len(kv[1]["pages"]))[:40]:
    add(f"- {v['names'].most_common(1)[0][0]} ({len(v['pages'])} pages)")
if not gaps:
    add("- none")

# ---- 4. definition drift
add("\n### Candidate definition drift (same term, different wording across lectures)\n")
add("Pairs of definitions of one term with low character-bigram overlap, from different pages. "
    "Many are just different aspects; this list tells a reviewer where to look.\n")
drift = []
for k, v in terms.items():
    defs = v["defs"]
    if len(defs) < 2 or len(v["pages"]) < 3:
        continue
    worst = None
    for a, b in itertools.combinations(defs[:12], 2):
        if a[0] == b[0]:
            continue
        s = jacc(a[3], b[3])
        if worst is None or s < worst[0]:
            worst = (s, a, b)
    if worst and worst[0] < 0.12:
        drift.append((worst[0], k, v, worst))
for s, k, v, (sim, a, b) in sorted(drift, key=lambda x: x[0])[:25]:
    add(f"**{v['names'].most_common(1)[0][0]}** — similarity {sim:.2f}, {len(v['defs'])} definitions on "
        f"{len(v['pages'])} pages")
    add(f"- {a[0]}: {a[3][:110]}")
    add(f"- {b[0]}: {b[3][:110]}\n")
add(f"({len(drift)} terms flagged in total)")

# ---- 5. variant names
add("\n### Likely name variants (one term contained in another, both common)\n")
common = [k for k, v in spread.items() if v >= 4 and len(k) >= 3]
cand = []
for a in common:
    for b in common:
        if a != b and a in b and len(b) - len(a) <= 4:
            co = len(terms[a]["pages"] & terms[b]["pages"])
            if co >= 2:
                cand.append((co, a, b))
for co, a, b in sorted(cand, reverse=True)[:30]:
    add(f"- {terms[a]['names'].most_common(1)[0][0]} ⊂ {terms[b]['names'].most_common(1)[0][0]} "
        f"(together on {co} pages; {spread[a]}/{spread[b]} pages each)")
add(f"\n({len(cand)} candidate pairs in total)")

# ---- 6. frameworks
fw = {}
for d in docs:
    for f in d.get("frameworks", []):
        k = norm(f.get("name", ""))
        if not k:
            continue
        e = fw.setdefault(k, {"name": f["name"], "pages": set(), "treat": collections.Counter(), "lists": []})
        e["pages"].add(d["id"])
        e["treat"][f.get("treatment", "?")] += 1
        if f.get("items"):
            e["lists"].append((d["id"], tuple(norm(i) for i in f["items"])))
add(f"\n## Frameworks\n\n- distinct frameworks: **{len(fw)}**")
add(f"- with a full member list on at least one page: {sum(1 for v in fw.values() if v['lists'])}")
add("\n| framework | pages | full | distinct member lists |\n|---|---:|---:|---:|")
for k, v in sorted(fw.items(), key=lambda kv: -len(kv[1]["pages"]))[:30]:
    add(f"| {v['name']} | {len(v['pages'])} | {v['treat']['full']} | {len(set(l for _, l in v['lists']))} |")
add("\n### Frameworks whose member list differs between pages\n")
bad = [(k, v) for k, v in fw.items() if len(set(l for _, l in v["lists"])) >= 2]
for k, v in sorted(bad, key=lambda kv: -len(kv[1]["pages"]))[:20]:
    sizes = sorted({len(l) for _, l in v["lists"]})
    add(f"- {v['name']}: {len(set(l for _, l in v['lists']))} distinct lists, sizes {sizes}, {len(v['pages'])} pages")

# ---- 7. schema health
add("\n## Schema health\n")
miss = collections.Counter()
for d in docs:
    for key in ("examples", "how_to", "prerequisites", "people", "errata", "frameworks", "sutra_refs"):
        if key not in d:
            miss[key] += 1
add("- digests missing optional/v3 fields: " + (", ".join(f"{k}: {n}" for k, n in miss.items()) or "none"))
no_src = sum(1 for d in docs for t in d.get("teachings", []) if t.get("from") == "cited_text" and not t.get("cited_source"))
n_cited = sum(1 for d in docs for t in d.get("teachings", []) if t.get("from") == "cited_text")
add(f"- teachings tagged cited_text: {n_cited}, of which without a cited_source: {no_src}")
vague = sum(1 for d in docs for t in d.get("teachings", []) if t.get("from") == "cited_text"
            and re.search(r"（讲者|讲者所|经典（|不明|未注明", t.get("cited_source", "")))
add(f"- cited_source values that are only a guess/label (heuristic): {vague}")
errs = sum(len(d.get("errata", [])) for d in docs)
add(f"- errata entries: {errs}")
low = [d for d in docs if d.get("teachings") is not None and len(d["teachings"]) == 0]
add(f"- digests with zero teachings (index/TOC pages): {len(low)}")

# ---- 8. versus existing concept cards
cards = {os.path.splitext(f)[0] for f in os.listdir("kb/concepts")} if os.path.isdir("kb/concepts") else set()
cardn = {norm(c) for c in cards}
miss_cards = [(k, v) for k, v in terms.items() if len(v["pages"]) >= 5 and k not in cardn]
add(f"\n## Existing concept cards\n\n- cards on disk: {len(cards)} (built from huayan28 only)")
add(f"- widespread terms (≥5 pages) with no card yet: {len(miss_cards)}")
for k, v in sorted(miss_cards, key=lambda kv: -len(kv[1]["pages"]))[:20]:
    add(f"  - {v['names'].most_common(1)[0][0]} ({len(v['pages'])} pages, {len(v['series'])} series)")

os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, "w", encoding="utf8").write("\n".join(L) + "\n")
print(f"wrote {OUT}: {len(docs)} digests, {n_terms} distinct terms, {len(fw)} frameworks")

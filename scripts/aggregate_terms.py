"""Phase 4 step 1 (deterministic): aggregate concepts, teachings and frameworks across ALL digests.

Usage: python -I scripts/aggregate_terms.py
Writes:
  kb/analysis/terms-aggregated.json   one record per normalized term, with every definition/explanation,
                                      the pages it appears on, roles, and the teachings that mention it
  kb/analysis/frameworks-aggregated.json   one record per normalized framework name with all member lists
  kb/analysis/aggregate-stats.md      sizes and tiers, to plan the consolidation work
No LLM involved. Name variants are only merged where the rule is mechanical (bracketed gloss, core-term
variants); everything else is left for the consolidation agents to judge.
"""
import collections, glob, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
OUT = "kb/analysis"


def norm(t):
    t = re.sub(r"[（(][^）)]*[）)]", "", t or "")          # drop bracketed glosses: 菩萨（菩提萨埵） -> 菩萨
    return re.sub(r"[\s·、，,。《》“”\"'：:；;\-—]", "", t)


def series_of(did):
    p = did.split("/")
    if p[1] == "dayi_all":
        return "dayi_all/" + (p[2] if len(p) > 3 else "")
    return p[1]


core_alias = {}
for c in json.load(open("kb/analysis/core-terms.json", encoding="utf8")):
    core_alias[norm(c["term"])] = c["term"]
    for v in c["variants"]:
        core_alias[norm(v)] = c["term"]

docs = []
for f in glob.glob("kb/digests/**/*.json", recursive=True):
    d = json.load(open(f, encoding="utf8"))
    d["_series"] = series_of(d["id"])
    docs.append(d)
docs.sort(key=lambda d: d["id"])

terms = {}
for d in docs:
    for c in d.get("concepts", []):
        k0 = norm(c.get("term", ""))
        if len(k0) < 2:
            continue
        k = norm(core_alias.get(k0, c["term"]))
        e = terms.setdefault(k, {"names": collections.Counter(), "pages": {}, "roles": collections.Counter()})
        e["names"][c["term"]] += 1
        e["roles"][c.get("role", "?")] += 1
        e["pages"].setdefault(d["id"], []).append({
            "role": c.get("role"), "definition": c.get("definition", ""), "plain": c.get("plain", ""),
            "quote": c.get("quote", "")})

# teachings that mention a term (only for terms on >=2 pages, to keep the file usable)
multi = {k for k, v in terms.items() if len(v["pages"]) >= 2 and len(k) >= 2}
mentions = collections.defaultdict(list)
for d in docs:
    for i, t in enumerate(d.get("teachings", [])):
        cl = norm(t.get("claim", ""))
        for k in multi:
            if k in cl:
                mentions[k].append({"page": d["id"], "i": i, "claim": t["claim"][:200], "from": t.get("from", "lecturer")})

def spread(items, cap=40):
    g = collections.OrderedDict()
    for it in items:
        g.setdefault(series_of(it["page"]), []).append(it)
    out = []
    while len(out) < cap and any(g.values()):
        for k in list(g):
            if g[k]:
                out.append(g[k].pop(0))
                if len(out) >= cap:
                    break
    return out


recs = []
for k, e in terms.items():
    name = e["names"].most_common(1)[0][0]
    recs.append({
        "key": k, "term": name, "variants": [n for n in e["names"] if n != name],
        "n_pages": len(e["pages"]), "series": sorted({series_of(p) for p in e["pages"]}),
        "roles": dict(e["roles"]), "entries": e["pages"], "teachings": spread(mentions.get(k, [])),
        "n_teachings": len(mentions.get(k, []))})
recs.sort(key=lambda r: -r["n_pages"])
json.dump(recs, open(f"{OUT}/terms-aggregated.json", "w", encoding="utf8"), ensure_ascii=False, indent=0)

fw = {}
for d in docs:
    for f in d.get("frameworks", []):
        k = norm(f.get("name", ""))
        if len(k) < 2:
            continue
        e = fw.setdefault(k, {"names": collections.Counter(), "pages": {}})
        e["names"][f["name"]] += 1
        e["pages"].setdefault(d["id"], []).append({"treatment": f.get("treatment"), "items": f.get("items", [])})
frecs = [{"key": k, "name": v["names"].most_common(1)[0][0], "variants": [n for n in v["names"] if n != v["names"].most_common(1)[0][0]],
          "n_pages": len(v["pages"]), "entries": v["pages"]} for k, v in fw.items()]
frecs.sort(key=lambda r: -r["n_pages"])
json.dump(frecs, open(f"{OUT}/frameworks-aggregated.json", "w", encoding="utf8"), ensure_ascii=False, indent=0)

# stats / tiers
def tier(n):
    return "A (>=5 pages)" if n >= 5 else "B (3-4)" if n >= 3 else "C (2)" if n == 2 else "D (1)"
tc = collections.Counter(tier(r["n_pages"]) for r in recs)
fc = collections.Counter(tier(r["n_pages"]) for r in frecs)
sz = lambda p: os.path.getsize(p) // 1024
L = ["# Aggregation stats\n", f"{len(docs)} digests; {len(recs)} normalized terms; {len(frecs)} framework names\n",
     "| tier | terms | frameworks |\n|---|---:|---:|"]
for t in ("A (>=5 pages)", "B (3-4)", "C (2)", "D (1)"):
    L.append(f"| {t} | {tc[t]} | {fc[t]} |")
L.append(f"\nterms-aggregated.json: {sz(OUT + '/terms-aggregated.json')} KB, "
         f"frameworks-aggregated.json: {sz(OUT + '/frameworks-aggregated.json')} KB")
L.append("\n## Top 30 terms\n\n| term | pages | series | teachings mentioning |\n|---|---:|---:|---:|")
for r in recs[:30]:
    L.append(f"| {r['term']} | {r['n_pages']} | {len(r['series'])} | {r['n_teachings']} |")
L.append("\n## Top 25 frameworks\n\n| name | pages |\n|---|---:|")
for r in frecs[:25]:
    L.append(f"| {r['name']} | {r['n_pages']} |")
open(f"{OUT}/aggregate-stats.md", "w", encoding="utf8").write("\n".join(L) + "\n")
print("\n".join(L[:12]))

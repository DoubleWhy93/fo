"""Phase 4 step 2: turn terms-aggregated.json into compact evidence packs for the consolidation agents.

Usage: python -I scripts/build_term_packs.py pilot            # 5 biggest terms -> pack-pilot.json
       python -I scripts/build_term_packs.py plan             # write all batches (tier A singles/groups, tier B groups)
Packs go to kb/analysis/packs/<name>.json (a list of term packs). Each pack keeps: every definition/explanation
(capped, spread across series), a sample of teachings mentioning the term, and the full page list.
"""
import collections, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
recs = json.load(open("kb/analysis/terms-aggregated.json", encoding="utf8"))
OUT = "kb/analysis/packs"
os.makedirs(OUT, exist_ok=True)


def series_of(did):
    p = did.split("/")
    return "答疑" if p[1].startswith("dayi") else p[1]


def spread(items, key, cap):
    """round-robin across groups so every series is represented before any repeats"""
    g = collections.OrderedDict()
    for it in items:
        g.setdefault(key(it), []).append(it)
    out = []
    while len(out) < cap and any(g.values()):
        for k in list(g):
            if g[k]:
                out.append(g[k].pop(0))
                if len(out) >= cap:
                    break
    return out


def pack(r, def_cap=30, teach_cap=15):
    defs = []
    for page, es in r["entries"].items():
        for e in es:
            txt = (e.get("definition") or "").strip() or (e.get("plain") or "").strip()
            if txt and e.get("role") in ("defined", "explained"):
                defs.append({"page": page, "role": e["role"], "definition": e.get("definition", ""),
                             "plain": e.get("plain", ""), "quote": e.get("quote", "")})
    defs.sort(key=lambda d: (d["role"] != "defined", d["page"]))
    defs = spread(defs, lambda d: series_of(d["page"]), def_cap)
    teach = spread(r["teachings"], lambda t: series_of(t["page"]), teach_cap)
    return {"key": r["key"], "term": r["term"], "variants": r["variants"], "n_pages": r["n_pages"],
            "series": r["series"], "roles": r["roles"], "n_definitions": len(defs),
            "definitions": defs, "teachings": teach, "pages_all": sorted(r["entries"])}


mode = sys.argv[1] if len(sys.argv) > 1 else "pilot"
if mode == "pilot":
    names = ["种性", "道种智", "密法言说", "见性", "普光明殿"]
    sel = [r for r in recs if r["term"] in names][:5]
    json.dump([pack(r) for r in sel], open(f"{OUT}/pack-pilot.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    print("pilot terms:", [(r["term"], r["n_pages"]) for r in sel])
else:
    A = [r for r in recs if r["n_pages"] >= 5]
    B = [r for r in recs if 3 <= r["n_pages"] < 5]
    batches = []
    for r in A[:12]:                       # the biggest concepts get a batch each
        batches.append([r])
    rest = A[12:]
    for i in range(0, len(rest), 6):
        batches.append(rest[i:i + 6])
    for i in range(0, len(B), 15):
        batches.append(B[i:i + 15])
    for n, b in enumerate(batches, 1):
        json.dump([pack(r, 30 if r["n_pages"] >= 10 else 20, 15 if r["n_pages"] >= 10 else 8) for r in b],
                  open(f"{OUT}/pack-{n:02d}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    sizes = [os.path.getsize(f"{OUT}/pack-{n:02d}.json") // 1024 for n in range(1, len(batches) + 1)]
    print(len(batches), "batches;", len(A), "tier A,", len(B), "tier B; pack KB max/mean:", max(sizes), sum(sizes) // len(sizes))

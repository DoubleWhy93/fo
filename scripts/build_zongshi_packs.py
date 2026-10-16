"""Evidence packs for folding 《總釋》 (pages/zongshi) into the concept cards.

Usage: python -I scripts/aggregate_terms.py && python -I scripts/build_zongshi_packs.py
Writes kb/analysis/zpacks/upd-NN.json  — existing cards: the card key plus every 總釋 definition/explanation of the term
                                          and 總釋 teachings mentioning it
       kb/analysis/zpacks/new-NN.json  — terms without a card that 總釋 explains and that appear on >= 3 pages overall:
                                          a full evidence pack across all series (same shape as Phase 4 packs)
"""
import glob, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
import opencc

S = opencc.OpenCC("t2s").convert
OUT = "kb/analysis/zpacks"
os.makedirs(OUT, exist_ok=True)
recs = json.load(open("kb/analysis/terms-aggregated.json", encoding="utf8"))
norm = lambda t: re.sub(r"[\s·、，,。《》“”\"'（）()：:；;\-—]", "", S(t or ""))
names = {}
for f in glob.glob("kb/consolidated/concepts/*.json"):
    c = json.load(open(f, encoding="utf8"))
    names.setdefault(norm(c["term"]), c["key"])
    for a in c.get("aliases", []):
        names.setdefault(norm(a), c["key"])
ZS = "pages/zongshi/"


def entries(r, only_zs):
    out = []
    for page, es in sorted(r["entries"].items()):
        if only_zs and not page.startswith(ZS):
            continue
        for e in es:
            if e.get("role") in ("defined", "explained") and ((e.get("definition") or "").strip() or (e.get("plain") or "").strip()):
                out.append({"page": page, "role": e["role"], "definition": e.get("definition", ""), "plain": e.get("plain", ""),
                            "quote": e.get("quote", "")})
    return out


upd, new = {}, []
for r in recs:
    zs_pages = [p for p in r["entries"] if p.startswith(ZS)]
    if not zs_pages:
        continue
    ev = entries(r, True)
    if not ev:
        continue
    k = names.get(norm(r["term"])) or next((names[norm(v)] for v in r["variants"] if norm(v) in names), None)
    zteach = [t for t in r["teachings"] if t["page"].startswith(ZS)][:12]
    if k:
        u = upd.setdefault(k, {"card": k, "zongshi_definitions": [], "zongshi_teachings": [], "zongshi_pages": []})
        u["zongshi_definitions"] += ev
        u["zongshi_teachings"] += zteach
        u["zongshi_pages"] = sorted(set(u["zongshi_pages"]) | set(zs_pages))
    elif r["n_pages"] >= 3:
        new.append({"key": r["key"], "term": r["term"], "variants": r["variants"], "n_pages": r["n_pages"], "series": r["series"],
                    "definitions": entries(r, False)[:30], "teachings": r["teachings"][:15], "pages_all": sorted(r["entries"])})

U = sorted(upd.values(), key=lambda u: u["card"])
for i in range(0, len(U), 15):
    json.dump(U[i:i + 15], open(f"{OUT}/upd-{i // 15 + 1:02d}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
for i in range(0, len(new), 14):
    json.dump(new[i:i + 14], open(f"{OUT}/new-{i // 14 + 1:02d}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(len(U), "cards to update in", (len(U) + 14) // 15, "batches;", len(new), "new-card candidates in", (len(new) + 13) // 14, "batches")

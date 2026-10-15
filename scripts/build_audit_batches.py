"""Phase 4 audit: build batches of claims + the source context around their quotes, for independent re-checking.

Usage: python -I scripts/build_audit_batches.py
Writes kb/analysis/audit-batches/audit-NN.json (list of items) and audit-manifest.json.
Item: {id, card, kind, claim, quotes:[{q, src, context}], why_selected}
`context` is ~500 characters before and after the quote in its source page (the quote itself in 【】).
"""
import glob, json, os, random, re, sys
import opencc

sys.stdout.reconfigure(encoding="utf-8")
T2S = opencc.OpenCC("t2s")
R = 500
OUT = "kb/analysis/audit-batches"
os.makedirs(OUT, exist_ok=True)
_c, _cc = {}, {}


def f1(ch):
    r = _cc.get(ch)
    if r is None:
        if ch.isspace():
            r = ""
        else:
            r = T2S.convert(ch)
            r = r if len(r) == 1 else ch
        _cc[ch] = r
    return r


def page(src):
    if src in _c:
        return _c[src]
    p = os.path.join("kb", "sources", src + ".md")
    if not os.path.exists(p):
        _c[src] = None
        return None
    t = open(p, encoding="utf8").read().split("\n---\n", 1)[1]
    folded, idx = [], []
    for i, ch in enumerate(t):
        r = f1(ch)
        if r:
            folded.append(r)
            idx.append(i)
    _c[src] = (t, "".join(folded), idx)
    return _c[src]


def context(src, q):
    pg = page(src)
    if not pg:
        return None
    t, folded, idx = pg
    fq = "".join(f1(c) for c in q)
    i = folded.find(fq)
    if i < 0:
        return None
    a, b = idx[i], idx[i + len(fq) - 1] + 1
    return (t[max(0, a - R):a] + "【" + t[a:b] + "】" + t[b:b + R]).replace("\n\n", "\n")


def items_of(card, kind_filter=None):
    out = []
    out.append(("definition", card["definition"], card.get("definition_basis", [])))
    for a in card.get("aspects", []):
        out.append(("aspect:" + a.get("label", ""), a.get("text", ""), a.get("quotes", [])))
    for t in card.get("tensions", []):
        out.append(("tension", t.get("text", ""), t.get("sources", [])))
    return out


def mk(card_name, kind, claim, quotes, why, idn):
    qs = []
    for q in quotes:
        ctx = context(q["src"], q["q"])
        qs.append({"q": q["q"], "src": q["src"], "context": ctx})
    return {"id": idn, "card": card_name, "kind": kind, "claim": claim, "quotes": qs, "why_selected": why}


cards = {}
for f in glob.glob("kb/consolidated/concepts/*.json"):
    c = json.load(open(f, encoding="utf8"))
    cards[c["key"]] = c
fws = {}
for f in glob.glob("kb/consolidated/frameworks/*.json"):
    c = json.load(open(f, encoding="utf8"))
    fws[c["key"]] = c

# --- A: low overlap list (recompute with the same rule used for the report)
def bg(s):
    s = re.sub(r"[^一-鿿]", "", T2S.convert(s))
    return {s[i:i + 2] for i in range(len(s) - 1)}


items = []
n = 0
for k, c in cards.items():
    for kind, claim, qs in items_of(c):
        if kind == "definition":
            continue
        claim_bg = bg(claim)
        quote_bg = set().union(*[bg(q["q"]) for q in qs]) if qs else set()
        if len(claim_bg) >= 6 and len(claim_bg & quote_bg) / len(claim_bg) < 0.15:
            n += 1
            items.append(mk(c["term"], kind, claim, qs, "low overlap with its own quotes", f"L{n:03d}"))
n_low = len(items)

# --- B: stratified sample
random.seed(20261015)
deep = [k for k, c in cards.items() if c.get("pages_consulted", 0) >= 12]
shallow = [k for k, c in cards.items() if c.get("pages_consulted", 0) <= 5]
pick = random.sample(deep, 10) + random.sample(shallow, 10)
done = {i["card"] for i in items}
m = 0
for k in pick:
    c = cards[k]
    for kind, claim, qs in items_of(c):
        m += 1
        items.append(mk(c["term"], kind, claim, qs, "sampled concept card", f"S{m:03d}"))
fpick = random.sample(list(fws), 6)
for k in fpick:
    c = fws[k]
    mem = "、".join(x["name"] for x in c["members"])
    m += 1
    items.append(mk(c["name"], "members", f"成员：{mem}（完整度：{c['completeness']}）", c["source_quotes"], "sampled framework card", f"S{m:03d}"))
    for t in c["tensions"]:
        m += 1
        items.append(mk(c["name"], "tension", t["text"], t.get("sources", []), "sampled framework card", f"S{m:03d}"))

# drop items whose quotes could not be located (report them), then batch
missing_ctx = [i["id"] for i in items if any(q["context"] is None for q in i["quotes"])]
batches = [items[i:i + 10] for i in range(0, len(items), 10)]
for n_, b in enumerate(batches, 1):
    json.dump(b, open(f"{OUT}/audit-{n_:02d}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
json.dump({"items": len(items), "low_overlap": n_low, "sampled": len(items) - n_low,
           "sample_concept_cards": [cards[k]["term"] for k in pick], "sample_framework_cards": [fws[k]["name"] for k in fpick],
           "quotes_without_context": missing_ctx},
          open(f"{OUT}/audit-manifest.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(len(items), "items in", len(batches), "batches;", n_low, "low-overlap +", len(items) - n_low, "sampled;",
      len(missing_ctx), "items with a quote whose context could not be located")

"""Map the knowledge base onto 《華嚴經》 (80卷): which pages discuss each 品, and which sutra paragraphs they quote.

Usage: python -I scripts/huayan_coverage.py
Writes kb/sutra/huayan80/coverage.json:
  {"pins": {pin: {"title", "pages": [{"id", "why"}]}},          # pages that name the 品 (sutra_refs / 總釋 essay titles)
   "paragraphs": {para_id: [{"id", "quote"}]}}                    # digest quotes that reproduce lines of that paragraph
A digest quote counts as quoting a paragraph when it shares a run of >= 12 characters with it (after folding to
Simplified and dropping punctuation), so loose citations by 品 name and verbatim quotations are kept apart.
"""
import glob, json, re, sys
import opencc

sys.stdout.reconfigure(encoding="utf-8")
T2S = opencc.OpenCC("t2s").convert
D = "kb/sutra/huayan80"
index = json.load(open(f"{D}/index.json", encoding="utf8"))
fold = lambda s: re.sub(r"[^一-鿿]", "", T2S(s or ""))

paras, grams = {}, {}
for i in index:
    for p in json.load(open(f"{D}/p{i['pin']:02d}.json", encoding="utf8"))["paragraphs"]:
        t = fold(p["text"])
        paras[p["id"]] = t
        for k in range(len(t) - 11):
            grams.setdefault(t[k:k + 12], set()).add(p["id"])

names = {}
for i in index:
    s = T2S(i["title"])
    names[s] = i["pin"]
    names[s.replace("品", "")] = i["pin"]
pin_of = lambda txt: {pin for n, pin in names.items() if len(n) >= 2 and n in T2S(txt or "")}

cov_pins = {str(i["pin"]): {"title": i["title"], "pages": []} for i in index}
cov_par = {}
for f in glob.glob("kb/digests/**/*.json", recursive=True):
    d = json.load(open(f, encoding="utf8"))
    did = d["id"]
    hit = {}
    if did.startswith("pages/zongshi/"):
        for pin in pin_of(d.get("title", "")):
            hit.setdefault(pin, "总释篇名")
    for r in d.get("sutra_refs", []):
        for pin in pin_of(r.get("ref", "")):
            hit.setdefault(pin, "引经：" + T2S(r.get("ref", ""))[:30])
    for pin, why in hit.items():
        cov_pins[str(pin)]["pages"].append({"id": did, "why": why})
    quotes = [r.get("quote", "") for r in d.get("sutra_refs", [])] + [t.get("quote", "") for t in d.get("teachings", [])]
    for q in quotes:
        fq = fold(q)
        found = set()
        for k in range(len(fq) - 11):
            found |= grams.get(fq[k:k + 12], set())
        for pid in found:
            lst = cov_par.setdefault(pid, [])
            if not any(x["id"] == did and x["quote"] == q for x in lst):
                lst.append({"id": did, "quote": q})

for v in cov_pins.values():
    v["pages"].sort(key=lambda x: x["id"])
json.dump({"pins": cov_pins, "paragraphs": dict(sorted(cov_par.items()))}, open(f"{D}/coverage.json", "w", encoding="utf8"),
          ensure_ascii=False, indent=1)
print(f"{sum(1 for v in cov_pins.values() if v['pages'])}/39 品 named by some page; "
      f"{len(cov_par)}/{len(paras)} paragraphs quoted verbatim somewhere")
for pin, v in cov_pins.items():
    q = sum(1 for p in cov_par if p.startswith(f"p{int(pin):02d}-"))
    n = next(i["paragraphs"] for i in index if str(i["pin"]) == pin)
    print(f"{pin:>2} {v['title']:<8} pages {len(v['pages']):>3}  quoted paras {q:>3}/{n}")

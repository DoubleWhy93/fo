"""Audit sample for the page digests (lecture / 总释 / Q&A summaries), same procedure as the concept-card audit.

Usage: python -I scripts/build_digest_audit.py
Draws a stratified random sample of digest claims — teachings (claim + quote) and Q&A answer summaries (summary +
quote) — and writes kb/analysis/digest-audit-batches/dNN.json (10 items each) with ~500 chars of source context around
each quote. Auditors follow kb/consolidated/audit/SPEC-audit.md and write kb/consolidated/audit/dNN.json
(`card` = the digest's page id). Verify with scripts/verify_audit.py.
"""
import glob, json, os, random, sys
import opencc

sys.stdout.reconfigure(encoding="utf-8")
T2S = opencc.OpenCC("t2s")
R = 500
OUT = "kb/analysis/digest-audit-batches"
os.makedirs(OUT, exist_ok=True)
_c, _cc = {}, {}


def f1(ch):
    r = _cc.get(ch)
    if r is None:
        r = "" if ch.isspace() else T2S.convert(ch)
        r = r if len(r) <= 1 else ch
        _cc[ch] = r
    return r


def page(src):
    if src not in _c:
        p = os.path.join("kb", "sources", src + ".md")
        if not os.path.exists(p):
            _c[src] = None
        else:
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
    if i < 0 or not fq:
        return None
    a, b = idx[i], idx[i + len(fq) - 1] + 1
    return (t[max(0, a - R):a] + "【" + t[a:b] + "】" + t[b:b + R]).replace("\n\n", "\n")


def series(pid):
    p = pid.split("/")
    return "答疑" if p[1].startswith("dayi") else p[1]


pool = {}
for f in glob.glob("kb/digests/**/*.json", recursive=True):
    d = json.load(open(f, encoding="utf8"))
    for t in d.get("teachings", []):
        if t.get("quote"):
            pool.setdefault(series(d["id"]), []).append((d["id"], "teaching", t["claim"], t["quote"]))
    for x in d.get("qa", []):
        if x.get("quote"):
            pool.setdefault("答疑-qa", []).append((d["id"], "qa_answer", f"问：{x.get('question', '')}｜答（概括）：{x.get('answer_summary', '')}", x["quote"]))
QUOTA = {"huayan28": 25, "huayan70": 35, "shixin": 20, "swxf": 30, "amtj": 15, "zongshi": 30, "答疑": 45, "答疑-qa": 40}
random.seed(20261018)
items = []
for ser, n in QUOTA.items():
    for pid, kind, claim, q in random.sample(pool.get(ser, []), min(n, len(pool.get(ser, [])))):
        ctx = context(pid, q)
        if ctx:
            items.append({"id": f"D{len(items) + 1:03d}", "card": pid, "kind": kind, "claim": claim,
                          "quotes": [{"q": q, "src": pid, "context": ctx}], "why_selected": f"sample:{ser}"})
random.shuffle(items)
for k in range(0, len(items), 10):
    json.dump(items[k:k + 10], open(f"{OUT}/d{k // 10 + 1:02d}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(len(items), "items in", (len(items) + 9) // 10, "batches; pool sizes:", {k: len(v) for k, v in pool.items()})

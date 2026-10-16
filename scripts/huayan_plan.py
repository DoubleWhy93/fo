"""Cut each 品 of 《華嚴經》 into reading segments (段) for the explanation pages.

Usage: python -I scripts/huayan_plan.py
Writes content/huayan/pNN/PLAN.json for all 39 品:
  {"pin", "title", "segments": [{"seg": "p11-s01", "chunks": [{"id": "p11-0003" | "p11-0005.2", "text", "verse"}],
                                 "chars", "coverage": "quoted" | "pin" | "none", "quoted_by": [page ids]}]}
A chunk is a whole paragraph, or a piece of a long one (> 1200 chars) cut at a sentence or verse-line break; the text
is copied verbatim from kb/sutra/huayan80. Segments collect consecutive chunks up to ~800 chars.
coverage: quoted = some KB page quotes these very lines; pin = the 品 is discussed but these lines are not quoted;
none = nothing in the KB names the 品.
"""
import json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
D = "kb/sutra/huayan80"
index = json.load(open(f"{D}/index.json", encoding="utf8"))
cov = json.load(open(f"{D}/coverage.json", encoding="utf8"))
MAXC, TARGET = 1200, 800
import opencc

_T2S = opencc.OpenCC("t2s").convert
_fold = lambda s: re.sub(r"[^一-鿿]", "", _T2S(s or ""))


def shares12(q, text):
    fq, ft = _fold(q), _fold(text)
    return any(fq[i:i + 12] in ft for i in range(len(fq) - 11))


def pieces(p):
    t = p["text"]
    if len(t) <= MAXC:
        return [(p["id"], t)]
    units = t.split("\n") if p["verse"] else re.split(r"(?<=[。；！？」])", t)
    out, buf = [], ""
    for u in units:
        if buf and len(buf) + len(u) > MAXC:
            out.append(buf)
            buf = ""
        buf += u + ("\n" if p["verse"] else "")
    if buf.strip():
        out.append(buf)
    out = [o.rstrip("\n") for o in out]
    assert ("\n" if p["verse"] else "").join(out) == t, p["id"]
    return [(f"{p['id']}.{k}", o) for k, o in enumerate(out, 1)]


total = 0
for i in index:
    pin = i["pin"]
    paras = json.load(open(f"{D}/p{pin:02d}.json", encoding="utf8"))["paragraphs"]
    chunks = [{"id": cid, "text": txt, "verse": p["verse"]} for p in paras for cid, txt in pieces(p)]
    segs, cur = [], []
    for c in chunks:
        if cur and sum(len(x["text"]) for x in cur) + len(c["text"]) > TARGET:
            segs.append(cur)
            cur = []
        cur.append(c)
    if cur:
        segs.append(cur)
    named = bool(cov["pins"][str(pin)]["pages"])
    out = []
    for k, s in enumerate(segs, 1):
        quoted = set()
        for c in s:
            for x in cov["paragraphs"].get(c["id"].split(".")[0], []):
                # a piece of a split paragraph counts as quoted only if the quote reproduces lines of that piece
                if "." not in c["id"] or shares12(x["quote"], c["text"]):
                    quoted.add(x["id"])
        quoted = sorted(quoted)
        out.append({"seg": f"p{pin:02d}-s{k:03d}", "chunks": s, "chars": sum(len(c["text"]) for c in s),
                    "coverage": "quoted" if quoted else ("pin" if named else "none"), "quoted_by": quoted})
    os.makedirs(f"content/huayan/p{pin:02d}", exist_ok=True)
    json.dump({"pin": pin, "title": i["title"], "segments": out}, open(f"content/huayan/p{pin:02d}/PLAN.json", "w", encoding="utf8"),
              ensure_ascii=False, indent=1)
    total += len(out)
    print(f"{pin:>2} {i['title']:<10} {len(out):>4} 段  quoted {sum(s['coverage'] == 'quoted' for s in out):>3}")
print(total, "segments")

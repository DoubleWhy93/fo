"""Check kb/consolidated/frameworks/*.json: schema, quotes verbatim in their pages, members traceable to the pack.
Usage: python -I scripts/verify_framework_cards.py [file ...]"""
import glob, importlib.util, json, os, re, sys
import opencc
spec = importlib.util.spec_from_file_location("vd", os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_digest.py"))
vd = importlib.util.module_from_spec(spec); spec.loader.exec_module(vd)
T2S = opencc.OpenCC("t2s").convert
MAN = {e["id"] for e in json.load(open("kb/manifest.json", encoding="utf8"))}
FW = {r["key"]: r for r in json.load(open("kb/analysis/frameworks-aggregated.json", encoding="utf8"))}
norm = lambda t: re.sub(r"[\s·、，,。《》“”\"'（）()：:；;\-—]", "", T2S(t or ""))
_c = {}
def src(s):
    if s not in _c: _c[s] = vd.src_text(s) if s in MAN else None
    return _c[s]
def quotes(errs, name, qs, need):
    if need and not qs: errs.append(f"{name}: needs >= 1 quote")
    for i, q in enumerate(qs or []):
        t = src(q.get("src"))
        if t is None: errs.append(f"{name}[{i}]: unknown src {q.get('src')!r}")
        elif len(q.get("q", "")) > 150: errs.append(f"{name}[{i}]: quote > 150 chars")
        elif vd.fold(q.get("q", "")) not in t: errs.append(f"{name}[{i}]: quote not in {q['src']}: {q.get('q','')[:36]}")
def check(f):
    errs = []
    try: d = json.load(open(f, encoding="utf8"))
    except Exception as e: return [f"invalid JSON: {e}"]
    for k in ("name", "key", "summary", "members", "completeness", "views", "tensions", "gaps", "source_quotes", "where_to_read", "confidence"):
        if k not in d: errs.append(f"missing {k}")
    if errs: return errs
    if os.path.splitext(os.path.basename(f))[0] != d["key"]: errs.append("file name != key")
    if d["completeness"] not in ("full", "partial", "fragmentary"): errs.append("bad completeness")
    if d["confidence"] not in ("high", "medium", "low"): errs.append("bad confidence")
    if len(d["summary"]) > 90: errs.append("summary > 90 chars")
    quotes(errs, "source_quotes", d["source_quotes"], True)
    for i, t in enumerate(d["tensions"]): quotes(errs, f"tensions[{i}].sources", t.get("sources"), True)
    for p in d["where_to_read"]:
        if p not in MAN: errs.append(f"where_to_read: unknown page {p!r}")
    if len(d["views"]) > 6: errs.append("views > 6")
    for v in d["views"]:
        for p in v.get("pages", []):
            if p not in MAN: errs.append(f"views: unknown page {p!r}")
    # members traceable: each member must appear (normalised) in some item of the pack, or in a cited quote
    pack = FW.get(d["key"])
    if pack:
        pool = norm("".join(i for es in pack["entries"].values() for e in es for i in e.get("items", [])) + pack["name"]
                    + "".join(pack.get("variants", [])))
        pool += norm("".join(q["q"] for q in d["source_quotes"]))
        for m in d["members"]:
            n = norm(m["name"])
            if n and n not in pool: errs.append(f"member not traceable to the pack: {m['name']!r}")
    return errs
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    fs = sys.argv[1:] or sorted(glob.glob("kb/consolidated/frameworks/*.json"))
    bad = 0
    for f in fs:
        e = check(f); bad += bool(e)
        print(os.path.basename(f), "OK" if not e else f"{len(e)} errors")
        for x in e[:8]: print("   -", x)
    print(f"\n{len(fs)} cards, {bad} with errors"); sys.exit(1 if bad else 0)

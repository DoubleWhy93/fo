"""Check 华严经 白话 pages (content/huayan/pNN/<seg>.json) against content/huayan/SPEC.md.
Usage: python -I scripts/verify_huayan.py [file ...]   (default: all pages)
Checks: schema and limits; `plain` covers every chunk of the segment, in PLAN order, with a plausible length;
coverage copied from PLAN and section counts that fit it; every quote verbatim in the page named by `src`."""
import glob, importlib.util, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
vd_spec = importlib.util.spec_from_file_location("vd", os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_digest.py"))
vd = importlib.util.module_from_spec(vd_spec)
vd_spec.loader.exec_module(vd)
MAN = {e["id"] for e in json.load(open("kb/manifest.json", encoding="utf8"))}
_c = {}


def src(sid):
    if sid not in _c:
        _c[sid] = vd.src_text(sid) if sid in MAN else None
    return _c[sid]


def quotes(errs, name, qs, need):
    if need and not qs:
        errs.append(f"{name}: needs >= 1 quote")
    for i, q in enumerate(qs or []):
        t = src(q.get("src"))
        if t is None:
            errs.append(f"{name}[{i}]: unknown src {q.get('src')!r}")
        elif len(q.get("q", "")) > 150:
            errs.append(f"{name}[{i}]: quote > 150 chars")
        elif vd.fold(q.get("q", "")) not in t:
            errs.append(f"{name}[{i}]: quote not in {q['src']}: {q.get('q', '')[:36]}")


def check(f):
    errs = []
    try:
        d = json.load(open(f, encoding="utf8"))
    except Exception as e:
        return [f"invalid JSON: {e}"]
    seg = d.get("seg", "")
    if os.path.splitext(os.path.basename(f))[0] != seg:
        errs.append("file name != seg")
    if re.match(r"a\d\d$", seg):                      # 阿弥陀经 读本 (content/amituo, same format)
        plan = json.load(open("content/amituo/PLAN.json", encoding="utf8"))
    elif re.match(r"p\d\d-s\d{3}$", seg):
        plan = json.load(open(f"content/huayan/p{int(seg[1:3]):02d}/PLAN.json", encoding="utf8"))
    else:
        return errs + ["bad seg id"]
    ps = next((s for s in plan["segments"] if s["seg"] == seg), None)
    if ps is None:
        return errs + ["seg not in PLAN"]
    for k, lim in (("title", 30), ("hook", 160)):
        if not d.get(k):
            errs.append(f"missing {k}")
        elif len(d[k]) > lim:
            errs.append(f"{k} > {lim} chars")
    want = [c["id"] for c in ps["chunks"]]
    got = [p.get("id") for p in d.get("plain", [])]
    if got != want:
        errs.append(f"plain ids {got} != PLAN chunks {want}")
    else:
        for p, c in zip(d["plain"], ps["chunks"]):
            n, m = len(re.sub(r"\s", "", p.get("t", ""))), len(re.sub(r"\s", "", c["text"]))
            if not 0.6 * m <= n <= 3 * m + 40:
                errs.append(f"plain {c['id']}: {n} chars for a {m}-char chunk (want 0.6x-3x)")
            mn = p.get("meaning") or {}
            if mn.get("basis") not in ("kb", "story"):
                errs.append(f"plain {c['id']}: meaning.basis must be kb|story")
            if not mn.get("t") or len(mn["t"]) > 320:
                errs.append(f"plain {c['id']}: meaning.t missing or > 320")
            quotes(errs, f"plain {c['id']}.meaning.quotes", mn.get("quotes"), mn.get("basis") == "kb")
    g = d.get("gist") or {}
    if not g.get("t") or len(g["t"]) > 420:
        errs.append("gist.t missing or > 420")
    quotes(errs, "gist.quotes", g.get("quotes"), ps["coverage"] != "none")
    terms = d.get("terms", [])
    if not 2 <= len(terms) <= 6:
        errs.append(f"terms: need 2-6, got {len(terms)}")
    for i, t in enumerate(terms):
        if t.get("basis") not in ("kb", "word"):
            errs.append(f"terms[{i}]: basis must be kb|word")
        if len(t.get("term", "")) > 16:
            errs.append(f"terms[{i}]: term > 16 chars")
        lim = 60 if t.get("basis") == "word" else 260
        if not t.get("plain") or len(t["plain"]) > lim:
            errs.append(f"terms[{i}]: plain missing or > {lim} chars")
        quotes(errs, f"terms[{i}].quotes", t.get("quotes"), t.get("basis") == "kb")
    r = d.get("reading", {})
    if r.get("coverage") != ps["coverage"]:
        errs.append(f"reading.coverage {r.get('coverage')!r} != PLAN {ps['coverage']!r}")
    secs = r.get("sections", [])
    lo, hi = {"quoted": (1, 4), "pin": (0, 3), "none": (0, 0)}.get(ps["coverage"], (0, 5))
    if not lo <= len(secs) <= hi:
        errs.append(f"reading.sections: {ps['coverage']} wants {lo}-{hi}, got {len(secs)}")
    for i, s in enumerate(secs):
        if not s.get("head") or len(s["head"]) > 28:
            errs.append(f"sections[{i}]: head missing or > 28")
        if not 1 <= len(s.get("paras", [])) <= 5:
            errs.append(f"sections[{i}]: 1-5 paras")
        for j, p in enumerate(s.get("paras", [])):
            if not p.get("t") or len(p["t"]) > 320:
                errs.append(f"sections[{i}].paras[{j}]: t missing or > 320")
            quotes(errs, f"sections[{i}].paras[{j}].quotes", p.get("quotes"), True)
    if ps["coverage"] == "quoted":
        used = {q["src"] for s in secs for p in s.get("paras", []) for q in p.get("quotes", [])}
        used |= {q["src"] for q in (d.get("gist") or {}).get("quotes", [])}
        used |= {q["src"] for p in d.get("plain", []) for q in (p.get("meaning") or {}).get("quotes", [])}
        if not used & set(ps["quoted_by"]):
            errs.append("coverage quoted: gist, meanings or reading must quote at least one page that quotes these lines (PLAN quoted_by)")
    if not 2 <= len(d.get("think", [])) <= 4:
        errs.append("think: need 2-4")
    if len(d.get("unsure", [])) > 4 or any(len(u) > 150 for u in d.get("unsure", [])):
        errs.append("unsure: <= 4 items of <= 150 chars")
    return errs


def main():
    files = [f for f in sys.argv[1:] if os.path.basename(f) != "PLAN.json"] or sorted(glob.glob("content/huayan/p*/p*-s*.json")) + sorted(glob.glob("content/amituo/a*.json"))
    bad = 0
    for f in files:
        e = check(f)
        if e:
            bad += 1
            print(f"{f}:")
            for x in e:
                print("  -", x)
        else:
            print(f"{os.path.basename(f)} OK")
    print(f"\n{len(files)} pages, {bad} with errors")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()

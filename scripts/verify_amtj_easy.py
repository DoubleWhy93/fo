"""Check content/amtj-easy/*.json (rich "easy" pages): schema, plainness limits, minimum depth, verbatim quotes.
Usage: python -I scripts/verify_amtj_easy.py [file ...]   (default: all content/amtj-easy/[0-9]*.json)"""
import glob, importlib.util, json, os, sys

spec = importlib.util.spec_from_file_location("vd", os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_digest.py"))
vd = importlib.util.module_from_spec(spec); spec.loader.exec_module(vd)
MAN = {e["id"] for e in json.load(open("kb/manifest.json", encoding="utf8"))}
PLAN = {p["slug"] for p in json.load(open("content/amtj/PLAN.json", encoding="utf8"))["pages"]}
_cache = {}


def src(sid):
    if sid not in _cache:
        _cache[sid] = vd.src_text(sid) if sid in MAN else None
    return _cache[sid]


def lim(errs, name, s, n, lo=1):
    if not isinstance(s, str) or len(s.strip()) < lo:
        errs.append(f"{name}: missing/too short")
    elif len(s) > n:
        errs.append(f"{name}: {len(s)} chars > {n}")


def quotes(errs, name, qs, need=True):
    if need and not qs:
        errs.append(f"{name}: needs at least one quote")
    for i, q in enumerate(qs or []):
        t = src(q.get("src"))
        if t is None:
            errs.append(f"{name}[{i}]: unknown src {q.get('src')!r}")
        elif len(q.get("q", "")) > 150:
            errs.append(f"{name}[{i}]: quote > 150 chars")
        elif vd.fold(q.get("q", "")) not in t:
            errs.append(f"{name}[{i}]: quote not in {q['src']}: {q.get('q', '')[:40]}")


def segtxt(ss):
    return "".join(s.get("t", "") for s in ss)


def detailed_len(slug):
    d = json.load(open(f"content/amtj/{slug}.json", encoding="utf8"))
    n = len(d["tldr"]) + len(segtxt(d["lead"]))
    for b in d["blocks"]:
        if "p" in b: n += len(segtxt(b["p"]))
        elif "example" in b: n += len(segtxt(b["example"]["p"]))
        elif "qa" in b: n += len(b["qa"]["q"]) + len(segtxt(b["qa"]["a"]))
        elif "dl" in b: n += sum(len(segtxt(i["dd"])) for i in b["dl"])
    return n


def check(f):
    errs = []
    try:
        d = json.load(open(f, encoding="utf8"))
    except Exception as e:
        return [f"invalid JSON: {e}"]
    slug = d.get("slug")
    if slug not in PLAN or os.path.splitext(os.path.basename(f))[0] != slug:
        errs.append("slug mismatch / not in PLAN")
    lim(errs, "title", d.get("title"), 30)
    lim(errs, "hook", d.get("hook"), 260, 20)
    lim(errs, "surface", d.get("surface"), 700, 20)
    lim(errs, "takeaway", d.get("takeaway"), 90)
    own = len(d.get("hook", "")) + len(d.get("surface", "")) + len(d.get("takeaway", ""))
    terms = d.get("terms", [])
    if not 2 <= len(terms) <= 5: errs.append(f"terms: need 2-5, got {len(terms)}")
    for i, t in enumerate(terms):
        lim(errs, f"terms[{i}].term", t.get("term"), 16)
        lim(errs, f"terms[{i}].plain", t.get("plain"), 300, 20)
        own += len(t.get("plain", ""))
        quotes(errs, f"terms[{i}].quotes", t.get("quotes"))
    secs = d.get("sections", [])
    if not 4 <= len(secs) <= 7: errs.append(f"sections: need 4-7, got {len(secs)}")
    for i, s in enumerate(secs):
        lim(errs, f"sections[{i}].head", s.get("head"), 28)
        ps = s.get("paras", [])
        if not 2 <= len(ps) <= 6: errs.append(f"sections[{i}].paras: need 2-6, got {len(ps)}")
        nq = 0
        for j, p in enumerate(ps):
            lim(errs, f"sections[{i}].paras[{j}].t", p.get("t"), 340, 20)
            own += len(p.get("t", ""))
            quotes(errs, f"sections[{i}].paras[{j}].quotes", p.get("quotes"), need=False)
            nq += len(p.get("quotes", []))
        if nq == 0: errs.append(f"sections[{i}]: no quote anywhere in this section")
        if s.get("example"):
            ex = s["example"]
            lim(errs, f"sections[{i}].example.title", ex.get("title"), 20)
            lim(errs, f"sections[{i}].example.text", ex.get("text"), 560, 30)
            own += len(ex.get("text", ""))
            quotes(errs, f"sections[{i}].example.quotes", ex.get("quotes"))
        if s.get("pause"):
            lim(errs, f"sections[{i}].pause", s["pause"], 90)
            if not s["pause"].rstrip().endswith(("？", "?")): errs.append(f"sections[{i}].pause: should end with ？")
    mis = d.get("misreadings", [])
    if not 2 <= len(mis) <= 4: errs.append(f"misreadings: need 2-4, got {len(mis)}")
    for i, m in enumerate(mis):
        lim(errs, f"misreadings[{i}].wrong", m.get("wrong"), 90, 8)
        lim(errs, f"misreadings[{i}].right", m.get("right"), 240, 20)
        own += len(m.get("right", ""))
        quotes(errs, f"misreadings[{i}].quotes", m.get("quotes"))
    th = d.get("think", [])
    if not 4 <= len(th) <= 6: errs.append(f"think: need 4-6, got {len(th)}")
    for i, s in enumerate(th):
        lim(errs, f"think[{i}]", s, 80, 6)
        if isinstance(s, str) and not s.rstrip().endswith(("？", "?")): errs.append(f"think[{i}]: should end with ？")
    uns = d.get("unsure", [])
    if len(uns) > 4: errs.append("unsure: at most 4")
    for i, s in enumerate(uns): lim(errs, f"unsure[{i}]", s, 150)
    if d.get("coverage") not in ("lecture", "partial", "qa", "none"): errs.append("bad coverage")
    elif d["coverage"] != "lecture" and not d.get("coverage_note"): errs.append("coverage_note required when coverage != lecture")
    if slug in PLAN and os.path.exists(f"content/amtj/{slug}.json"):
        need = max(1600, int(0.8 * detailed_len(slug)))
        if own < need:
            errs.append(f"too thin: {own} chars of own prose, need >= {need} (80% of the detailed page, min 1600)")
    return errs


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    fs = sys.argv[1:] or sorted(glob.glob("content/amtj-easy/[0-9]*.json"))
    bad = 0
    for f in fs:
        e = check(f)
        bad += bool(e)
        print(os.path.basename(f), "OK" if not e else f"{len(e)} errors")
        for x in e[:8]: print("   -", x)
    print(f"\n{len(fs)} pages, {bad} with errors")
    sys.exit(1 if bad else 0)

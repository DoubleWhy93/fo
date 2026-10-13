"""Check content/amtj-easy/*.json pages: schema, length limits, verbatim quotes in sources.
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


def lim(errs, name, s, n):
    if not isinstance(s, str) or not s.strip():
        errs.append(f"{name}: missing/empty")
    elif len(s) > n:
        errs.append(f"{name}: {len(s)} chars > {n}")


def quotes(errs, name, qs):
    if not qs:
        errs.append(f"{name}: needs at least one quote")
    for i, q in enumerate(qs or []):
        t = src(q.get("src"))
        if t is None:
            errs.append(f"{name}[{i}]: unknown src {q.get('src')!r}")
        elif len(q.get("q", "")) > 150:
            errs.append(f"{name}[{i}]: quote > 150 chars")
        elif vd.fold(q.get("q", "")) not in t:
            errs.append(f"{name}[{i}]: quote not in {q['src']}: {q.get('q', '')[:40]}")


def check(f):
    errs = []
    try:
        d = json.load(open(f, encoding="utf8"))
    except Exception as e:
        return [f"invalid JSON: {e}"]
    if d.get("slug") not in PLAN or os.path.splitext(os.path.basename(f))[0] != d.get("slug"):
        errs.append("slug mismatch / not in PLAN")
    lim(errs, "title", d.get("title"), 30)
    lim(errs, "hook", d.get("hook"), 120)
    lim(errs, "surface", d.get("surface"), 260)
    lim(errs, "takeaway", d.get("takeaway"), 48)
    ideas = d.get("ideas", [])
    if not 3 <= len(ideas) <= 5:
        errs.append(f"ideas: need 3-5, got {len(ideas)}")
    for i, it in enumerate(ideas):
        lim(errs, f"ideas[{i}].head", it.get("head"), 16)
        lim(errs, f"ideas[{i}].text", it.get("text"), 120)
        quotes(errs, f"ideas[{i}].quotes", it.get("quotes"))
    if "story" in d:
        lim(errs, "story.title", d["story"].get("title"), 20)
        lim(errs, "story.text", d["story"].get("text"), 280)
        quotes(errs, "story.quotes", d["story"].get("quotes"))
    th = d.get("think", [])
    if not 2 <= len(th) <= 3:
        errs.append(f"think: need 2-3, got {len(th)}")
    for i, s in enumerate(th):
        lim(errs, f"think[{i}]", s, 60)
        if isinstance(s, str) and not s.rstrip().endswith(("？", "?")):
            errs.append(f"think[{i}]: should end with a question mark")
    for i, s in enumerate(d.get("unsure", [])):
        lim(errs, f"unsure[{i}]", s, 100)
    if len(d.get("unsure", [])) > 2:
        errs.append("unsure: at most 2")
    if d.get("coverage") not in ("lecture", "partial", "qa", "none"):
        errs.append("bad coverage")
    elif d["coverage"] != "lecture" and not d.get("coverage_note"):
        errs.append("coverage_note required when coverage != lecture")
    return errs


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    fs = sys.argv[1:] or sorted(glob.glob("content/amtj-easy/[0-9]*.json"))
    bad = 0
    for f in fs:
        e = check(f)
        bad += bool(e)
        print(os.path.basename(f), "OK" if not e else f"{len(e)} errors")
        for x in e[:8]:
            print("   -", x)
    print(f"\n{len(fs)} pages, {bad} with errors")
    sys.exit(1 if bad else 0)

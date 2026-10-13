"""Check content/amtj/*.json pages: schema, quotes verbatim in their source, anchored paragraphs.
Usage: python -I scripts/verify_amtj_pages.py [file ...]   (default: all content/amtj/[0-9]*.json)"""
import glob, importlib.util, json, os, sys

spec = importlib.util.spec_from_file_location("vd", os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_digest.py"))
vd = importlib.util.module_from_spec(spec); spec.loader.exec_module(vd)
MAN = {e["id"]: e for e in json.load(open("kb/manifest.json", encoding="utf8"))}
PLAN = {p["slug"]: p for p in json.load(open("content/amtj/PLAN.json", encoding="utf8"))["pages"]}
_cache = {}


def src(sid):
    if sid not in _cache:
        _cache[sid] = vd.src_text(sid) if sid in MAN else None
    return _cache[sid]


def segs(path, items, errs, anchor_len=None):
    if not isinstance(items, list):
        errs.append(f"{path}: segments must be a list")
        return
    plain, has_q = 0, False
    for i, s in enumerate(items):
        if "q" in s:
            has_q = True
            sid, q = s.get("src"), s["q"]
            if len(q) > 150:
                errs.append(f"{path}[{i}]: quote > 150 chars")
            t = src(sid) if sid else None
            if t is None:
                errs.append(f"{path}[{i}]: unknown src {sid!r}")
            elif vd.fold(q) not in t:
                errs.append(f"{path}[{i}]: quote not in {sid}: {q[:40]}")
        elif "t" in s:
            plain += len(s["t"])
        else:
            errs.append(f"{path}[{i}]: segment needs t or q")
    if anchor_len is not None and plain > anchor_len and not has_q:
        errs.append(f"{path}: paragraph of {plain} chars has no quote anchor")


def check(f):
    errs = []
    try:
        d = json.load(open(f, encoding="utf8"))
    except Exception as e:
        return [f"invalid JSON: {e}"]
    slug = d.get("slug")
    if slug not in PLAN:
        errs.append(f"slug {slug!r} not in PLAN")
    if os.path.splitext(os.path.basename(f))[0] != slug:
        errs.append("file name != slug")
    for k in ("title", "tldr", "lead", "blocks", "coverage"):
        if k not in d:
            errs.append(f"missing {k}")
    if errs:
        return errs
    if d["coverage"] not in ("lecture", "partial", "qa", "none"):
        errs.append("bad coverage")
    if d["coverage"] != "lecture" and not d.get("coverage_note"):
        errs.append("coverage_note required when coverage != lecture")
    segs("lead", d["lead"], errs)
    for i, b in enumerate(d["blocks"]):
        ks = [x for x in b if x in ("h2", "p", "example", "qa", "dl")]
        if len(ks) != 1:
            errs.append(f"blocks[{i}]: needs exactly one of h2/p/example/qa/dl")
            continue
        k = ks[0]
        if k == "p":
            segs(f"blocks[{i}].p", b["p"], errs, 40)
        elif k == "example":
            segs(f"blocks[{i}].example.p", b["example"].get("p", []), errs, 40)
        elif k == "qa":
            if "q" not in b["qa"]:
                errs.append(f"blocks[{i}].qa: missing q")
            segs(f"blocks[{i}].qa.a", b["qa"].get("a", []), errs, 40)
        elif k == "dl":
            for j, it in enumerate(b["dl"]):
                segs(f"blocks[{i}].dl[{j}]", it.get("dd", []), errs)
    nq = json.dumps(d, ensure_ascii=False).count('"q":')
    if d["coverage"] == "lecture" and nq < 6:
        errs.append(f"only {nq} quotes for a lecture-covered passage (need >= 6)")
    return errs


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    fs = sys.argv[1:] or sorted(glob.glob("content/amtj/[0-9]*.json"))
    bad = 0
    for f in fs:
        e = check(f)
        bad += bool(e)
        print(os.path.basename(f), "OK" if not e else f"{len(e)} errors")
        for x in e[:8]:
            print("   -", x)
    print(f"\n{len(fs)} pages, {bad} with errors")
    sys.exit(1 if bad else 0)

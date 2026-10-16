"""Check kb/consolidated/concepts/*.json cards: schema, limits, and every quote verbatim in its source page.
Usage: python -I scripts/verify_concept_cards.py [file ...]   (default: all cards)"""
import glob, importlib.util, json, os, sys

spec = importlib.util.spec_from_file_location("vd", os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_digest.py"))
vd = importlib.util.module_from_spec(spec); spec.loader.exec_module(vd)
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
    for k in ("term", "key", "summary", "definition", "definition_basis", "aspects", "tensions", "gaps", "where_to_read", "confidence"):
        if k not in d:
            errs.append(f"missing {k}")
    if errs:
        return errs
    if os.path.splitext(os.path.basename(f))[0] != d["key"]:
        errs.append("file name != key")
    if len(d["summary"]) > 90:
        errs.append("summary > 90 chars")
    if not 20 <= len(d["definition"]) <= 700:
        errs.append(f"definition length {len(d['definition'])} outside 20-700")
    if d["confidence"] not in ("high", "medium", "low"):
        errs.append("bad confidence")
    quotes(errs, "definition_basis", d["definition_basis"], True)
    if not 1 <= len(d["aspects"]) <= 8:
        errs.append(f"aspects: need 1-8, got {len(d['aspects'])}")
    for i, a in enumerate(d["aspects"]):
        quotes(errs, f"aspects[{i}].quotes", a.get("quotes"), True)
    for i, t in enumerate(d["tensions"]):
        quotes(errs, f"tensions[{i}].sources", t.get("sources"), True)
    ok_series = {"huayan28", "huayan70", "shixin", "swxf", "amtj", "juewu_s", "zongshi", "答疑"}
    for s_ in d.get("by_series", []):
        if s_.get("series") not in ok_series:
            errs.append(f"by_series: unknown series {s_.get('series')!r}")
    if not 1 <= len(d["where_to_read"]) <= 8:
        errs.append("where_to_read: need 1-8")
    for p in d["where_to_read"]:
        if p not in MAN:
            errs.append(f"where_to_read: unknown page {p!r}")
    return errs


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    fs = sys.argv[1:] or sorted(glob.glob("kb/consolidated/concepts/*.json"))
    bad = 0
    for f in fs:
        e = check(f)
        bad += bool(e)
        print(os.path.basename(f), "OK" if not e else f"{len(e)} errors")
        for x in e[:8]:
            print("   -", x)
    print(f"\n{len(fs)} cards, {bad} with errors")
    sys.exit(1 if bad else 0)

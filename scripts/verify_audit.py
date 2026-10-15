"""Check kb/consolidated/audit/audit-NN.json: ids match the batch exactly, verdicts valid, evidence quotes verbatim.
Usage: python -I scripts/verify_audit.py [file ...]"""
import glob, importlib.util, json, os, sys
spec = importlib.util.spec_from_file_location("vd", os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_digest.py"))
vd = importlib.util.module_from_spec(spec); spec.loader.exec_module(vd)
MAN = {e["id"] for e in json.load(open("kb/manifest.json", encoding="utf8"))}
V = {"supported", "partly", "unsupported", "misattributed", "cannot_tell"}
def check(f):
    name = os.path.basename(f)
    bp = f"kb/analysis/audit-batches/{name}"
    errs = []
    try: out = json.load(open(f, encoding="utf8"))
    except Exception as e: return [f"invalid JSON: {e}"]
    if not os.path.exists(bp): return ["no matching batch file"]
    want = [i["id"] for i in json.load(open(bp, encoding="utf8"))]
    got = [o.get("id") for o in out]
    if sorted(got) != sorted(want): errs.append(f"ids differ: missing {sorted(set(want)-set(got))[:5]} extra {sorted(set(got)-set(want))[:5]}")
    for o in out:
        if o.get("verdict") not in V: errs.append(f"{o.get('id')}: bad verdict")
        if not (o.get("reason") or "").strip() or len(o["reason"]) > 260: errs.append(f"{o.get('id')}: reason missing/too long")
        if o.get("verdict") in ("partly", "unsupported", "misattributed") and not (o.get("suggested_text") or "").strip():
            errs.append(f"{o.get('id')}: suggested_text required")
        for q in o.get("evidence", []) or []:
            if q.get("src") not in MAN: errs.append(f"{o['id']}: unknown src"); continue
            if vd.fold(q["q"]) not in vd.src_text(q["src"]): errs.append(f"{o['id']}: evidence quote not in page: {q['q'][:30]}")
    return errs
if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    fs = sys.argv[1:] or sorted(glob.glob("kb/consolidated/audit/audit-[0-9]*.json"))
    bad = 0
    for f in fs:
        e = check(f); bad += bool(e)
        print(os.path.basename(f), "OK" if not e else f"{len(e)} errors")
        for x in e[:8]: print("   -", x)
    print(f"\n{len(fs)} files, {bad} with errors"); sys.exit(1 if bad else 0)

"""Apply audit corrections: partly -> replace text with auditor's suggested_text; unsupported tension -> drop it.
Usage: python -I scripts/apply_audit.py   (reads kb/consolidated/audit/audit-NN.json + kb/analysis/audit-batches)"""
import glob, json, sys
sys.stdout.reconfigure(encoding="utf-8")
B = {}
for f in glob.glob("kb/analysis/audit-batches/audit-[0-9]*.json"):
    for i in json.load(open(f, encoding="utf8")):
        B[i["id"]] = i
cards = {}
for kind, d in (("c", "concepts"), ("f", "frameworks")):
    for f in glob.glob(f"kb/consolidated/{d}/*.json"):
        c = json.load(open(f, encoding="utf8"))
        cards[(kind, c.get("term") or c.get("name"))] = (f, c)
MANUAL = {"S024": ("definition", "从第八回向位以后逐渐生起其行法，四位行法阶段的只是相似的行法。", "从第八回向位以后逐渐生起其行法。")}
touched, log = set(), []
for f in sorted(glob.glob("kb/consolidated/audit/audit-[0-9]*.json")):
    for r in json.load(open(f, encoding="utf8")):
        v = r["verdict"]
        if v == "supported":
            continue
        b = B[r["id"]]
        key = next((k for k in cards if k[1] == b["card"]), None)
        fp, c = cards[key]
        kind, claim = b["kind"], b["claim"]
        new = r.get("suggested_text")
        if r["id"] in MANUAL:
            new = claim.replace(MANUAL[r["id"]][1], MANUAL[r["id"]][2])
        done = False
        if kind == "definition" and c.get("definition") == claim:
            c["definition"] = new; done = True
        elif kind.startswith("aspect:"):
            for a in c.get("aspects", []):
                if a.get("text") == claim:
                    a["text"] = new; done = True
        elif kind == "tension":
            ts = c.get("tensions", [])
            for t in ts:
                if t["text"] == claim:
                    if v == "unsupported":
                        ts.remove(t)
                    else:
                        t["text"] = new
                    done = True
                    break
        log.append((r["id"], v, kind, done))
        if done:
            touched.add(fp)
for fp in touched:
    c = next(c for (_, c2) in [(k, v[1]) for k, v in cards.items()] for c in [c2] if cards and False) if False else None
for k, (fp, c) in cards.items():
    if fp in touched:
        json.dump(c, open(fp, "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(len(log), "items,", sum(1 for x in log if x[3]), "applied; not applied:", [x[0] for x in log if not x[3]])

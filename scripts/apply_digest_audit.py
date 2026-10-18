"""Apply the digest audit (kb/consolidated/audit/dNN.json): replace each partly/unsupported/misattributed claim in its
digest with the auditor's suggested text (teachings[].claim, or qa[].answer_summary for Q&A answers), and record the
change in the digest's `notes`. Usage: python -I scripts/apply_digest_audit.py"""
import glob, json, sys

sys.stdout.reconfigure(encoding="utf-8")
B = {}
for f in glob.glob("kb/analysis/digest-audit-batches/d*.json"):
    for i in json.load(open(f, encoding="utf8")):
        B[i["id"]] = i
done, miss = [], []
for f in sorted(glob.glob("kb/consolidated/audit/d*.json")):
    for r in json.load(open(f, encoding="utf8")):
        if r["verdict"] == "supported":
            continue
        it = B[r["id"]]
        path = f"kb/digests/{it['card']}.json"
        d = json.load(open(path, encoding="utf8"))
        q = it["quotes"][0]["q"]
        new = r["suggested_text"].strip()
        hit = False
        if it["kind"] == "teaching":
            for t in d.get("teachings", []):
                if t.get("claim") == it["claim"] and t.get("quote") == q:
                    t["claim"], hit = new, True
        else:
            for x in d.get("qa", []):
                if x.get("quote") == q and it["claim"].endswith(x.get("answer_summary", "")):
                    x["answer_summary"] = new.split("答（概括）：", 1)[-1].lstrip("：").strip()
                    hit = True
        if hit:
            d["notes"] = (d.get("notes", "") + f" 〔审读修正 {r['id']}：{r['reason'][:80]}〕").strip()
            json.dump(d, open(path, "w", encoding="utf8"), ensure_ascii=False, indent=1)
            done.append(r["id"])
        else:
            miss.append((r["id"], it["card"]))
print(len(done), "applied", done, "; not found:", miss)

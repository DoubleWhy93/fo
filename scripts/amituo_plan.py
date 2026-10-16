"""Plan for the 《佛说阿弥陀经》 白话读本 pages (same format as the 华严经 读本, content/huayan/SPEC.md).

Usage: python -I scripts/amituo_plan.py
Writes content/amituo/PLAN.json: one segment per passage of content/amtj/PLAN.json (a01 … a14), chunks = that
passage's sutra excerpts (ids a01-1, a01-2 …; text verbatim from the PLAN, Traditional). Every passage is covered by
the existing explanation pages, so coverage is "quoted"; quoted_by lists the pages the detailed page quotes.
source_coverage (lecture | partial | qa) says what the explanation rests on; the site shows it on the page.
"""
import json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
P = json.load(open("content/amtj/PLAN.json", encoding="utf8"))["pages"]
segs = []
for p in P:
    sid = f"a{p['order']:02d}"
    det = json.load(open(f"content/amtj/{p['slug']}.json", encoding="utf8"))
    srcs = set(p.get("lecture_sources", []))

    def walk(x):
        if isinstance(x, dict):
            if "src" in x and isinstance(x["src"], str):
                srcs.add(x["src"])
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(det)
    segs.append({"seg": sid, "slug": p["slug"], "chunks": [{"id": f"{sid}-{k}", "text": e["text"], "verse": False}
                                                          for k, e in enumerate(p["sutra_excerpts"], 1)],
                 "chars": sum(len(e["text"]) for e in p["sutra_excerpts"]), "coverage": "quoted", "quoted_by": sorted(srcs),
                 "source_coverage": det.get("coverage", "lecture"), "source_coverage_note": det.get("coverage_note", "")})
os.makedirs("content/amituo", exist_ok=True)
json.dump({"title": "佛說阿彌陀經", "segments": segs}, open("content/amituo/PLAN.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(len(segs), "passages;", sum(len(s["chunks"]) for s in segs), "chunks")

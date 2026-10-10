"""Phase 1b: PDFs in the old site's doc/ -> kb/sources/pdf/<name>.md (one file per PDF, page markers kept).

Usage: python -I scripts/extract_pdf.py [--src <site>/doc] [--out kb]
Appends/updates entries (kind="pdf") in kb/manifest.json.
"""
import argparse, glob, hashlib, json, os, re
import fitz

NAMES = {
    "華嚴經綱要60上": "gangyao60-1", "華嚴經綱要60下": "gangyao60-2",
    "華嚴經綱要80上": "gangyao80-1", "華嚴經綱要80中": "gangyao80-2", "華嚴經綱要80下": "gangyao80-3",
    "華嚴經總釋": "zongshi", "總釋二十八講": "zongshi28", "HuayanCharts": "charts",
    "華嚴書院學員守則": "rules",
}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=r"D:\repos\hyjing-main\hyjing\doc")
    ap.add_argument("--out", default="kb")
    a = ap.parse_args()
    out = os.path.abspath(a.out)
    mpath = os.path.join(out, "manifest.json")
    manifest = [m for m in json.load(open(mpath, encoding="utf8")) if m.get("kind") != "pdf"]
    os.makedirs(os.path.join(out, "sources", "pdf"), exist_ok=True)
    for p in sorted(glob.glob(os.path.join(a.src, "*.pdf"))):
        stem = os.path.splitext(os.path.basename(p))[0]
        slug = NAMES.get(stem, stem)
        d = fitz.open(p)
        parts, chars = [], 0
        for i, page in enumerate(d, 1):
            t = page.get_text().strip()
            t = re.sub(r"[ \t\u3000\xa0]+", " ", t)
            if not t:
                continue
            chars += len(re.sub(r"\s+", "", t))
            parts.append(f"<!-- p{i} -->\n{t}")
        body = "\n\n".join(parts)
        sid = f"pdf/{slug}"
        fm = {"id": sid, "src": f"doc/{os.path.basename(p)}", "kind": "pdf", "title": stem,
              "series": "pdf", "order": -1, "pages": len(d), "chars": chars,
              "sha1": hashlib.sha1(re.sub(r"\s+", "", body).encode("utf8")).hexdigest()}
        outp = os.path.join(out, "sources", "pdf", slug + ".md")
        with open(outp, "w", encoding="utf8", newline="\n") as fh:
            fh.write("---\n" + "".join(f"{k}: {json.dumps(v, ensure_ascii=False)}\n" for k, v in fm.items()) + "---\n\n" + body + "\n")
        fm["out"] = f"sources/pdf/{slug}.md"
        manifest.append(fm)
        print(sid, len(d), "pages", chars, "chars")
    manifest.sort(key=lambda m: (m["series"], m["order"], m["id"]))
    json.dump(manifest, open(mpath, "w", encoding="utf8"), ensure_ascii=False, indent=1)


if __name__ == "__main__":
    main()

"""Split 《覺悟華嚴經·總釋》 (one long web page, pages/juewu_s/jw_hyjzs) into one source file per essay.

Usage: python -I scripts/split_zongshi.py      (run again after scripts/extract.py, which rewrites the manifest)
Writes kb/sources/pages/zongshi/zsP-NN.md (preface = zs0-00; essays 1.1 … 7.35; part 8, the tables, is skipped)
and replaces the `pages/zongshi` entries in kb/manifest.json. Essay text is copied verbatim from the source page.
"""
import hashlib, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
SRC = "kb/sources/pages/juewu_s/jw_hyjzs.md"
OUT = "kb/sources/pages/zongshi"
os.makedirs(OUT, exist_ok=True)
raw = open(SRC, encoding="utf8").read()
body = raw.split("\n---\n", 1)[1]
lines = body.split("\n")

ESSAY = re.compile(r"^#{2,3} ?(\d+)\.(\d+) ?(.*)$")
PART = re.compile(r"^#{2,3} (\d+) +(.+)$")
GROUP = re.compile(r"^## (\D.*)$")

pieces = [{"key": (0, 0), "title": "序文——認識生命，覺悟華嚴", "part": "序文", "group": "", "lines": []}]
part, group = "序文", ""
for ln in lines:
    m, p, g = ESSAY.match(ln), PART.match(ln), GROUP.match(ln)
    if m:
        if int(m.group(1)) >= 8:
            break
        name = m.group(3).strip()
        if group and name in ("十住位", "十行位", "十迴向位", "十地位", "等覺位", "妙覺位"):
            group = name          # e.g. 7.22 十地位 opens its own stage, but the page has no separate "## 十地位" heading
        pieces.append({"key": (int(m.group(1)), int(m.group(2))), "title": f"{m.group(1)}.{m.group(2)} {name}",
                       "part": part, "group": group, "lines": []})
    elif p:
        if int(p.group(1)) >= 8:
            break
        part, group = p.group(2).strip(), ""
    elif g:
        group = g.group(1).strip()
    else:
        pieces[-1]["lines"].append(ln)

man = [e for e in json.load(open("kb/manifest.json", encoding="utf8")) if e["series"] != "pages/zongshi"]
new = []
for order, pc in enumerate(pieces):
    text = "\n".join(pc["lines"]).strip() + "\n"
    a, b = pc["key"]
    sid = f"pages/zongshi/zs{a}-{b:02d}"
    fm = {"id": sid, "src": "pages/juewu_s/jw_hyjzs.html", "kind": "content", "title": pc["title"],
          "head_title": f"華嚴經總釋｜{pc['part']}" + (f"｜{pc['group']}" if pc["group"] else ""),
          "series": "pages/zongshi", "order": order, "date": "", "related_pin": "", "keywords": "",
          "chars": len(re.sub(r"\s", "", text)), "qa_pairs": 0, "images": [],
          "sha1": hashlib.sha1(text.encode("utf8")).hexdigest(), "out": f"sources/{sid}.md",
          "part": pc["part"], "group": pc["group"], "derived_from": "pages/juewu_s/jw_hyjzs"}
    head = "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in fm.items() if k not in ("out",))
    open(f"kb/{fm['out']}", "w", encoding="utf8").write(f"---\n{head}\n---\n\n{text}")
    new.append(fm)
man += new
man.sort(key=lambda m: (m["series"], m["order"], m["id"]))
json.dump(man, open("kb/manifest.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
parts = {}
for fm in new:
    parts.setdefault(fm["part"], 0)
    parts[fm["part"]] += 1
print(len(new), "pieces;", parts, "; chars min/median/max:",
      sorted(f["chars"] for f in new)[0], sorted(f["chars"] for f in new)[len(new) // 2], max(f["chars"] for f in new))

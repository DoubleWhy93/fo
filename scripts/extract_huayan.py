"""Extract 《大方廣佛華嚴經》 80卷 (實叉難陀譯, CBETA T10n0279) into per-品 JSON.

Usage: python -I scripts/extract_huayan.py <path to T10n0279.xml>
       (download: https://raw.githubusercontent.com/cbeta-org/xml-p5/master/T/T10/T10n0279.xml — keep it outside the repo)
Writes kb/sutra/huayan80/pNN.json, one per 品 (39), and kb/sutra/huayan80/index.json.
Paragraph = one <p> (prose) or one <lg> (verse block, lines joined with "\n"). Text stays Traditional, as in CBETA;
gaiji <g> keep their inner text, editorial notes / variant readings (<note>, <rdg>) are dropped, <lem> is kept.
The 御製序 (imperial preface) is skipped.
"""
import json, os, re, sys
import xml.etree.ElementTree as ET

sys.stdout.reconfigure(encoding="utf-8")
NS = {"tei": "http://www.tei-c.org/ns/1.0", "cb": "http://www.cbeta.org/ns/1.0"}
OUT = "kb/sutra/huayan80"
os.makedirs(OUT, exist_ok=True)
SKIP = {"note", "rdg", "anchor", "lb", "pb", "milestone", "mulu", "head", "byline", "docNumber", "juan", "jhead", "space"}


def local(tag):
    return tag.split("}", 1)[-1]


def text_of(el):
    out = [el.text or ""]
    for ch in el:
        name = local(ch.tag)
        if name in SKIP:
            pass
        elif name == "app":
            lem = ch.find("tei:lem", NS)
            if lem is not None:
                out.append(text_of(lem))
        else:
            out.append(text_of(ch))
        out.append(ch.tail or "")
    return "".join(out)


def clean(s):
    return re.sub(r"\s+", "", s)


tree = ET.parse(sys.argv[1])
body = tree.getroot().find(".//tei:body", NS)
pins, cur, juan = [], None, None


def walk(el):
    global cur, juan
    for ch in el:
        name = local(ch.tag)
        if name == "milestone" and ch.get("unit") == "juan":
            juan = int(ch.get("n"))
        elif name == "div" and ch.get("type") == "xu":
            continue                                   # imperial preface
        elif name == "mulu" and ch.get("type") == "品" and ch.get("level") == "1":
            m = re.match(r"\s*(\d+)\s*(.+)", ch.text or "")
            cur = {"pin": int(m.group(1)), "title": m.group(2).strip(), "juan": [], "paragraphs": []}
            pins.append(cur)
        elif name == "p" and cur is not None:
            t = clean(text_of(ch))
            if t:
                cur["paragraphs"].append({"juan": juan, "lb": (ch.get("{http://www.w3.org/XML/1998/namespace}id") or "")[5:], "text": t, "verse": False})
        elif name == "lg" and cur is not None:
            lines = [clean(text_of(l)) for l in ch.findall("tei:l", NS)]
            lines = [l for l in lines if l]
            if lines:
                cur["paragraphs"].append({"juan": juan, "lb": (ch.get("{http://www.w3.org/XML/1998/namespace}id") or "")[5:], "text": "\n".join(lines), "verse": True})
        else:
            walk(ch)
        if cur is not None and juan and juan not in cur["juan"]:
            cur["juan"].append(juan)


walk(body)
index = []
for p in pins:
    for i, para in enumerate(p["paragraphs"], 1):
        para["id"] = f"p{p['pin']:02d}-{i:04d}"
    p["source"] = "CBETA T10n0279《大方廣佛華嚴經》八十卷，唐 實叉難陀譯"
    json.dump(p, open(f"{OUT}/p{p['pin']:02d}.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
    chars = sum(len(x["text"]) for x in p["paragraphs"])
    index.append({"pin": p["pin"], "title": p["title"], "juan": p["juan"], "paragraphs": len(p["paragraphs"]), "chars": chars,
                  "verse_paragraphs": sum(x["verse"] for x in p["paragraphs"])})
json.dump(index, open(f"{OUT}/index.json", "w", encoding="utf8"), ensure_ascii=False, indent=1)
print(len(pins), "品;", sum(i["paragraphs"] for i in index), "paragraphs;", sum(i["chars"] for i in index), "chars")
for i in index[:5] + index[-3:]:
    print(i)

"""Phase 1: HTML -> normalized source files + manifest.

Usage: python -I scripts/extract.py [--src D:/repos/hyjing-main/hyjing] [--out kb]

Reads every .html under <src> (the site root), keeps the main <section>
content (drops nav/header/scripts), and writes one Markdown file per page
under <out>/sources/<series>/<name>.md with YAML-ish frontmatter, plus
<out>/manifest.json. Text stays Traditional (conversion happens at build time).
"""
import argparse, hashlib, json, os, re, sys
from bs4 import BeautifulSoup, NavigableString

DATE_RE = re.compile(r"(20\d\d)[-./年](\d{1,2})(?:[-./月](\d{1,2}))?")
WS_RE = re.compile(r"[ \t\u3000\xa0]+")


def read_html(path):
    raw = open(path, "rb").read()
    for enc in ("utf-8-sig", "utf-8", "gb18030", "big5"):
        try:
            return raw.decode(enc)
        except UnicodeDecodeError:
            continue
    return raw.decode("utf-8", errors="replace")


def clean(s):
    s = s.replace("\r", "")
    s = WS_RE.sub(" ", s)
    s = re.sub(r" *\n *", "\n", s)
    return s.strip()


def block_text(el):
    # <br> -> newline, keep inline text
    for br in el.find_all("br"):
        br.replace_with("\n")
    return clean(el.get_text())


def table_rows(tbl):
    rows = []
    for tr in tbl.find_all("tr"):
        cells = [clean(c.get_text(" ")).replace("\n", " ") for c in tr.find_all(["td", "th"])]
        cells = [c for c in cells if c]
        if cells:
            rows.append(" | ".join(cells))
    return rows


def extract_blocks(root):
    blocks = []  # (kind, text)
    img_notes = []
    seen = set()

    def walk(node):
        for ch in node.children:
            if isinstance(ch, NavigableString):
                continue
            name = ch.name
            if name in ("script", "style", "nav", "noscript"):
                continue
            if name == "table":
                for r in table_rows(ch):
                    blocks.append(("tr", r))
                continue
            if name in ("h1", "h2", "h3", "h4", "h5", "h6"):
                t = block_text(ch)
                if t:
                    blocks.append((name, t))
                continue
            if name in ("p", "li", "blockquote", "pre"):
                if ch.find("table"):
                    walk(ch)
                    continue
                t = block_text(ch)
                if t:
                    blocks.append(("p", t))
                for im in ch.find_all("img"):
                    if im.get("alt"):
                        img_notes.append(im["alt"].strip())
                continue
            if name == "img":
                if ch.get("alt"):
                    img_notes.append(ch["alt"].strip())
                continue
            walk(ch)

    walk(root)
    return blocks, img_notes


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", default=r"D:\repos\hyjing-main\hyjing")
    ap.add_argument("--out", default="kb")
    a = ap.parse_args()

    src = os.path.abspath(a.src)
    out = os.path.abspath(a.out)
    manifest = []
    for d, dirs, files in os.walk(src):
        rel_dir = os.path.relpath(d, src).replace("\\", "/")
        # skip assets / templates / components
        parts = rel_dir.split("/")
        if parts[0] in ("css", "js", "font", "img", "owl-carousel", "Templates", "components", "doc", "assets") or "assets" in parts:
            continue
        for f in sorted(files):
            if not f.lower().endswith(".html"):
                continue
            path = os.path.join(d, f)
            rel = os.path.relpath(path, src).replace("\\", "/")
            html = read_html(path)
            soup = BeautifulSoup(html, "lxml")
            head_title = clean(soup.title.get_text()) if soup.title else ""
            meta_desc = ""
            md = soup.find("meta", attrs={"name": "description"})
            if md and md.get("content"):
                meta_desc = clean(md["content"])
            meta_kw = ""
            mk = soup.find("meta", attrs={"name": "keywords"})
            if mk and mk.get("content"):
                meta_kw = clean(mk["content"])

            root = soup.find("section") or soup.body or soup
            h1 = root.find("h1")
            h1_text = clean(h1.get_text()) if h1 else ""
            blocks, img_notes = extract_blocks(root)
            # drop the h1 block (kept in frontmatter)
            if blocks and blocks[0][0] == "h1":
                blocks = blocks[1:]

            # 相關 / 關鍵字 header (huayan70 etc.)
            related = keywords = ""
            body_blocks = []
            for kind, t in blocks:
                if kind == "h5" and ("相　關" in t or "相關" in t or "關鍵字" in t):
                    m = re.search(r"相\s*關[：:]\s*(.*?)(?:\n|$)", t)
                    k = re.search(r"關鍵字[：:]\s*(.*)", t)
                    related = m.group(1).strip() if m else related
                    keywords = k.group(1).strip() if k else keywords
                    continue
                body_blocks.append((kind, t))

            # link stats (hub detection)
            anchors = root.find_all("a")
            link_chars = sum(len(clean(x.get_text())) for x in anchors)
            text_all = "\n\n".join(t for _, t in body_blocks)
            chars = len(re.sub(r"\s+", "", text_all))
            link_ratio = round(link_chars / max(1, len(re.sub(r"\s+", "", clean(root.get_text())))), 2)
            qa = len(re.findall(r"【問】|【问】", text_all))
            if link_ratio > 0.5 and chars > 1000:
                kind = "hub"
            elif chars < 300 and qa == 0:
                kind = "stub"
            else:
                kind = "content"

            date = ""
            for cand in (h1_text, head_title, text_all[:200]):
                m = DATE_RE.search(cand)
                if m:
                    date = f"{m.group(1)}-{int(m.group(2)):02d}" + (f"-{int(m.group(3)):02d}" if m.group(3) else "")
                    break

            stem = os.path.splitext(f)[0]
            series = rel_dir if rel_dir != "." else "root"
            sid = f"{series}/{stem}"
            lead = re.match(r"(\d+)[.\s]", stem)  # Q&A files: "103.wsmyxhyj"
            nums = re.findall(r"\d+", stem)
            order = int(lead.group(1)) if lead else (int(nums[-1]) if nums else -1)  # lectures: "28jiang10" -> 10
            sha = hashlib.sha1(re.sub(r"\s+", "", text_all).encode("utf8")).hexdigest()

            outp = os.path.join(out, "sources", series, stem + ".md")
            os.makedirs(os.path.dirname(outp), exist_ok=True)
            fm = {
                "id": sid, "src": rel, "kind": kind, "title": h1_text or head_title,
                "head_title": head_title, "series": series, "order": order, "date": date,
                "related_pin": related, "keywords": keywords or meta_kw, "chars": chars,
                "qa_pairs": qa, "images": img_notes, "sha1": sha,
            }
            with open(outp, "w", encoding="utf8", newline="\n") as fh:
                fh.write("---\n")
                for k, v in fm.items():
                    fh.write(f"{k}: {json.dumps(v, ensure_ascii=False)}\n")
                fh.write("---\n\n")
                for kind_, t in body_blocks:
                    if kind_.startswith("h"):
                        fh.write("#" * min(6, int(kind_[1]) + 1) + " " + t + "\n\n")
                    else:
                        fh.write(t + "\n\n")
            fm["out"] = os.path.relpath(outp, out).replace("\\", "/")
            fm["link_ratio"] = link_ratio
            manifest.append(fm)

    manifest.sort(key=lambda m: (m["series"], m["order"], m["id"]))
    with open(os.path.join(out, "manifest.json"), "w", encoding="utf8") as fh:
        json.dump(manifest, fh, ensure_ascii=False, indent=1)
    kinds = {}
    for m in manifest:
        kinds[m["kind"]] = kinds.get(m["kind"], 0) + 1
    print(f"{len(manifest)} pages -> {out}", kinds, "total chars", sum(m["chars"] for m in manifest))


if __name__ == "__main__":
    main()

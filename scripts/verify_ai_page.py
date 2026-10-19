"""Check content/ai/page.json (the 华严与AI page): every quote verbatim in its source page, every linked card exists.
The editor's reflections (`human`, `ai`, meta paragraphs without quotes) are labelled on the page and not checked.
Usage: python -I scripts/verify_ai_page.py"""
import glob, importlib.util, json, os, re, sys

sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("vd", os.path.join(os.path.dirname(os.path.abspath(__file__)), "verify_digest.py"))
vd = importlib.util.module_from_spec(spec)
spec.loader.exec_module(vd)
import opencc

S = opencc.OpenCC("t2s").convert
norm = lambda t: re.sub(r"[\s·、，,。《》“”\"'（）()：:；;\-—]", "", S(t or ""))
MAN = {e["id"] for e in json.load(open("kb/manifest.json", encoding="utf8"))}
CARDS = {norm(json.load(open(f, encoding="utf8"))["term"]) for f in glob.glob("kb/consolidated/concepts/*.json")}
d = json.load(open("content/ai/page.json", encoding="utf8"))
errs, n = [], 0


def check(where, qs, need=True):
    global n
    if need and not qs:
        errs.append(f"{where}: needs a quote")
    for q in qs or []:
        n += 1
        if q.get("src") not in MAN:
            errs.append(f"{where}: unknown src {q.get('src')}")
        elif len(q["q"]) > 150:
            errs.append(f"{where}: quote > 150 chars")
        elif vd.fold(q["q"]) not in vd.src_text(q["src"]):
            errs.append(f"{where}: quote not in {q['src']}: {q['q'][:30]}")


for i, p in enumerate(d["lecturer_on_ai"]["points"]):
    check(f"lecturer_on_ai[{i}]", p.get("quotes"))
items = [it for s in d["sections"] for it in s["items"]]
for t in items:
    check(t["head"], t["lecturer"].get("quotes"))
    for c in t["lecturer"].get("cards", []):
        if norm(c) not in CARDS:
            errs.append(f"{t['head']}: no card named {c}")
    for k in ("train", "try"):
        if not t.get(k):
            errs.append(f"{t['head']}: missing {k}")
for i, p in enumerate(d["meta"]["paras"]):
    check(f"meta[{i}]", p.get("quotes"), need=False)
for e in errs:
    print(" -", e)
print(f"{n} quotes checked, {len(items)} items in {len(d['sections'])} sections, {len(errs)} errors")
sys.exit(1 if errs else 0)

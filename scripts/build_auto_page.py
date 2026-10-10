"""Wrap + verify an agent-written page body.

Usage: python -I scripts/build_auto_page.py <name>
Reads sample/auto/<name>.body.html (HTML fragment). Every <q class="orig">…</q> must be verbatim
Traditional text found somewhere in kb/sources (variant-folded). On success writes
sample/auto/<name>.html with the quotes converted to Simplified and the shared stylesheet.
Exit 1 if any quote is not found.
"""
import glob, html, re, sys
import opencc
sys.stdout.reconfigure(encoding="utf-8")
name = sys.argv[1]
cc = opencc.OpenCC("t2s"); cm = {}
WS = re.compile(r"\s+")
def simp_char(c):
    r = cm.get(c)
    if r is None:
        r = cc.convert(c); r = r if len(r) == 1 else c; cm[c] = r
    return r
def fold(t): return "".join(simp_char(c) for c in WS.sub("", t))
corpus = {}
for f in glob.glob("kb/sources/**/*.md", recursive=True):
    t = open(f, encoding="utf8").read().split("\n---\n", 1)[1]
    corpus[f] = fold(t)
big = "\n".join(corpus.values())
body = open(f"sample/auto/{name}.body.html", encoding="utf8").read()
bad = []
def conv(m):
    inner = html.unescape(re.sub(r"<[^>]+>", "", m.group(2)))
    q = fold(inner)
    if q not in big:
        bad.append(inner[:60])
    return f'<q class="orig">{html.escape(cc.convert(inner))}</q>'
new = re.sub(r'<q( class="orig"[^>]*)>(.*?)</q>', conv, body, flags=re.S)
nq = len(re.findall(r'<q class="orig"', body))
css = open("sample/内在觉知模式-v2.html", encoding="utf8").read().split("<style>")[1].split("</style>")[0]
title = re.search(r"<h1>(.*?)</h1>", body, re.S)
title = re.sub(r"<[^>]+>", "", title.group(1)) if title else name
doc = f'<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{html.escape(title)}</title><style>{css}</style></head><body><main>{new}</main></body></html>'
open(f"sample/auto/{name}.html", "w", encoding="utf8").write(doc)
print(f"{name}: {nq} quotes, {len(bad)} NOT FOUND, {len(re.findall('class=.src.', body))} source tags")
for b in bad: print("  - not found:", b)
sys.exit(1 if bad else 0)

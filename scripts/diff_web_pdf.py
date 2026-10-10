"""Which text in a PDF is NOT on the given web pages? Usage: diff_web_pdf.py <pdf-slug> <web-series-prefix> [min_run]"""
import sys, re, glob, json, opencc
sys.stdout.reconfigure(encoding="utf-8")
slug, prefix = sys.argv[1], sys.argv[2]
minrun = int(sys.argv[3]) if len(sys.argv) > 3 else 40
cc = opencc.OpenCC("t2s"); cm = {}
HAN = re.compile(r"[㐀-䶿一-鿿豈-﫿]")
def norm(t):
    out = []
    for ch in HAN.findall(t):
        r = cm.get(ch)
        if r is None:
            r = cc.convert(ch); r = r if len(r) == 1 else ch; cm[ch] = r
        out.append(r)
    return "".join(out)
def body(p):
    t = open(p, encoding="utf8").read()
    return t.split("\n---\n", 1)[1] if t.startswith("---\n") else t
K = 8
web = set()
for p in glob.glob(f"kb/sources/{prefix}/*.md"):
    s = norm(body(p))
    web.update(s[i:i+K] for i in range(len(s)-K+1))
pdf = open(f"kb/sources/pdf/{slug}.md", encoding="utf8").read().split("\n---\n", 1)[1]
# split by page markers, keep page number
pages = re.split(r"<!-- p(\d+) -->", pdf)
tot = unc = 0; runs = []
for i in range(1, len(pages), 2):
    pg, txt = pages[i], pages[i+1]
    s = norm(txt); n = len(s); tot += n
    cov = bytearray(n)
    for j in range(n-K+1):
        if s[j:j+K] in web:
            for q in range(j, j+K): cov[q] = 1
    unc += n - sum(cov)
    j = 0
    while j < n:
        if not cov[j]:
            k = j
            while k < n and not cov[k]: k += 1
            if k - j >= minrun: runs.append((int(pg), s[j:k]))
            j = k
        else: j += 1
print(f"{slug}: {tot:,} chars, uncovered {unc:,} ({unc/tot:.0%}); runs>= {minrun}: {len(runs)} totalling {sum(len(r[1]) for r in runs):,}")
bypage = {}
for pg, r in runs: bypage[pg] = bypage.get(pg, 0) + len(r)
print("pages with most uncovered text:", sorted(bypage.items(), key=lambda x: -x[1])[:25])
for pg, r in runs[:12]: print(f"  p{pg}: {r[:110]}")

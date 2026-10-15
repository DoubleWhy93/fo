"""Render the consolidated KB (concept cards, framework cards, tensions) to site/kb/ and the landing page site/index.html.
Usage: python -I scripts/build_kb_site.py   (Simplified Chinese; quotes shown simplified, labelled with their source page)"""
import glob, html, json, os, re, sys
import opencc

sys.stdout.reconfigure(encoding="utf-8")
S = opencc.OpenCC("t2s").convert
H = html.escape
MAN = {e["id"]: e for e in json.load(open("kb/manifest.json", encoding="utf8"))}
OUT = "site/kb"
os.makedirs(OUT + "/c", exist_ok=True)
os.makedirs(OUT + "/f", exist_ok=True)
CSS = open("scripts/build_amtj_site.py", encoding="utf8").read().split('CSS = """')[1].split('"""')[0]
CSS += """.card-sum{font-size:1.1rem}.conf{font-size:.8rem;color:var(--mute)}
table.idx{width:100%;border-collapse:collapse;font-size:.95rem}table.idx td,table.idx th{border-bottom:1px solid var(--line);padding:.45rem .4rem;text-align:left;vertical-align:top}
.chips a{display:inline-block;margin:.15rem .3rem .15rem 0;padding:.05rem .6rem;border:1px solid var(--line);border-radius:99px;text-decoration:none;font-size:.9rem}
.tension{background:var(--card);border:1px dashed var(--acc);border-radius:8px;padding:.7rem 1rem;margin:1rem 0}
input#q{width:100%;padding:.6rem .8rem;font-size:1rem;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg)}
"""
SERIES = {"huayan28": "二十八讲", "huayan70": "七十讲", "shixin": "十信位", "swxf": "行法", "amtj": "阿弥陀经大义", "juewu_s": "觉悟", "答疑": "答疑"}


def label(sid):
    e = MAN.get(sid)
    if not e:
        return sid
    t = re.sub(r"[《》]", "", S(e.get("title") or sid))
    p = sid.split("/")
    if p[1] in SERIES:
        return f"{SERIES[p[1]]}·{t[:18]}"
    if p[1].startswith("dayi"):
        return "答疑·" + t[:18] + ("…" if len(t) > 18 else "")
    return t[:22]


def page(title, body, depth=1, kicker="", nav=True):
    up = "../" * depth
    nv = (f'<nav class="top"><a href="{up}index.html">首页</a><span><a href="{up}kb/index.html">概念</a> · '
          f'<a href="{up}kb/frameworks.html">框架</a> · <a href="{up}kb/tensions.html">说法差异</a></span></nav>') if nav else ""
    return f"""<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{H(title)}</title><style>{CSS}</style></head><body><main>
{nv}<div class="kicker">{H(kicker)}</div>{body}
<p class="note">本页整理自华严书院公开讲稿：概念卡汇集各讲稿的说法并附原文引文，不作裁决；整理可能有疏漏，请以引文所在原页为准。</p>
</main></body></html>"""


def quote(q):
    return f'<q class="orig">{H(S(q["q"]))}</q><sup class="src">{H(label(q["src"]))}</sup>'


def quotes(qs):
    return "<ul class='open'>" + "".join(f"<li>{quote(q)}</li>" for q in qs) + "</ul>" if qs else ""


cards = {}
for f in glob.glob("kb/consolidated/concepts/*.json"):
    c = json.load(open(f, encoding="utf8"))
    cards[c["key"]] = c
fws = {}
for f in glob.glob("kb/consolidated/frameworks/*.json"):
    c = json.load(open(f, encoding="utf8"))
    fws[c["key"]] = c


def norm(t):
    return re.sub(r"[\s·、，,。《》“”\"'（）()：:；;\-—]", "", S(t or ""))


cslug = {k: f"{i:03d}" for i, k in enumerate(sorted(cards), 1)}
fslug = {k: f"{i:02d}" for i, k in enumerate(sorted(fws), 1)}
byname = {}
for k, c in cards.items():
    byname.setdefault(norm(c["term"]), ("c", k))
    for a in c.get("aliases", []):
        byname.setdefault(norm(a), ("c", k))
for k, c in fws.items():
    byname.setdefault(norm(c["name"]), ("f", k))


def link(name):
    """from a card page (site/kb/c|f/…): sibling folders are ../c and ../f"""
    r = byname.get(norm(name))
    if not r:
        return H(S(name))
    t, k = r
    return f'<a href="../{t}/{(cslug if t == "c" else fslug)[k]}.html">{H(S(name))}</a>'


CONF = {"high": "置信：高", "medium": "置信：中（多据汇总材料）", "low": "置信：低"}
for k, c in cards.items():
    b = [f"<h1>{H(S(c['term']))}</h1>", f"<p class='card-sum'>{H(S(c['summary']))}</p>"]
    if c.get("aliases"):
        b.append(f"<p class='conf'>又称：{H('、'.join(S(a) for a in c['aliases']))}</p>")
    b.append(f"<div class='tldr'><b>讲者怎么说</b>{H(S(c['definition']))}</div>" + quotes(c.get("definition_basis", [])))
    if c.get("aspects"):
        b.append("<h2>不同的用法</h2>")
        for a in c["aspects"]:
            b.append(f"<div class='ex'><b>{H(S(a['label']))}</b><p>{H(S(a['text']))}</p>{quotes(a.get('quotes', []))}</div>")
    if c.get("by_series"):
        b.append("<h2>各讲稿的讲法</h2><dl class='gl'>" + "".join(
            f"<dt>{H(SERIES.get(s['series'], s['series']))}</dt><dd>{H(S(s['text']))}</dd>" for s in c["by_series"]) + "</dl>")
    if c.get("tensions"):
        b.append("<h2>各页说法不一之处</h2>")
        for t in c["tensions"]:
            b.append(f"<div class='tension'><p>{H(S(t['text']))}</p>{quotes(t.get('sources', []))}</div>")
    if c.get("gaps"):
        b.append("<h2>讲稿中没有讲清的</h2><ul class='open'>" + "".join(f"<li>{H(S(g))}</li>" for g in c["gaps"]) + "</ul>")
    if c.get("related"):
        b.append("<h2>相关</h2><p class='chips'>" + " ".join(f"<span>{link(r)}</span>" for r in c["related"]) + "</p>")
    if c.get("where_to_read"):
        b.append("<h2>建议阅读的原页</h2><ul class='open'>" + "".join(f"<li>{H(label(p))}</li>" for p in c["where_to_read"]) + "</ul>")
    b.append(f"<p class='conf'>{CONF.get(c['confidence'], '')} · 参考 {c.get('pages_consulted', 0)} 页</p>")
    open(f"{OUT}/c/{cslug[k]}.html", "w", encoding="utf8").write(page(S(c["term"]), "".join(b), 2, "概念卡"))

for k, c in fws.items():
    b = [f"<h1>{H(S(c['name']))}</h1>", f"<p class='card-sum'>{H(S(c['summary']))}</p>"]
    b.append("<h2>成员</h2><ol>" + "".join(
        f"<li><b>{link(m['name'])}</b>：{H(S(m.get('note', '')))}</li>" for m in c.get("members", [])) + "</ol>")
    if c.get("order_note"):
        b.append(f"<p>{H(S(c['order_note']))}</p>")
    b.append(f"<p class='conf'>完整度：{H(c.get('completeness', ''))}</p>")
    for v in c.get("views", []):
        b.append(f"<div class='ex'><b>{H(S(v['label']))}</b><p>{H('、'.join(S(m) for m in v.get('members', [])))}</p></div>")
    if c.get("source_quotes"):
        b.append("<h2>原文</h2>" + quotes(c["source_quotes"]))
    if c.get("tensions"):
        b.append("<h2>各页说法不一之处</h2>")
        for t in c["tensions"]:
            b.append(f"<div class='tension'><p>{H(S(t['text']))}</p>{quotes(t.get('sources', []))}</div>")
    if c.get("gaps"):
        b.append("<h2>讲稿中没有讲清的</h2><ul class='open'>" + "".join(f"<li>{H(S(g))}</li>" for g in c["gaps"]) + "</ul>")
    if c.get("related"):
        b.append("<h2>相关</h2><p class='chips'>" + " ".join(f"<span>{link(r)}</span>" for r in c["related"]) + "</p>")
    open(f"{OUT}/f/{fslug[k]}.html", "w", encoding="utf8").write(page(S(c["name"]), "".join(b), 2, "框架卡"))

rows = sorted(cards.values(), key=lambda c: -c.get("pages_consulted", 0))
tbl = "".join(
    f"<tr data-t='{H(S(c['term']) + ' ' + S(c['summary']))}'><td><a href='c/{cslug[c['key']]}.html'>{H(S(c['term']))}</a></td>"
    f"<td>{H(S(c['summary']))}</td></tr>" for c in rows)
js = ("<script>document.getElementById('q').addEventListener('input',e=>{const v=e.target.value.trim();"
      "document.querySelectorAll('tr[data-t]').forEach(r=>r.style.display=!v||r.dataset.t.includes(v)?'':'none')})</script>")
open(f"{OUT}/index.html", "w", encoding="utf8").write(page(
    "概念索引", f"<h1>概念索引</h1><p>{len(cards)} 个概念，按资料页数排序。</p><input id='q' placeholder='搜索概念…'>"
    f"<table class='idx'>{tbl}</table>{js}", 1, "华严知识库"))
ft = "".join(f"<tr><td><a href='f/{fslug[k]}.html'>{H(S(c['name']))}</a></td><td>{H(S(c['summary']))}</td></tr>"
              for k, c in sorted(fws.items(), key=lambda kv: kv[1]["name"]))
open(f"{OUT}/frameworks.html", "w", encoding="utf8").write(page(
    "框架索引", f"<h1>框架索引</h1><p>{len(fws)} 个框架（成员列表与次序）。</p><table class='idx'>{ft}</table>", 1, "华严知识库"))
T = []
for c in sorted(cards.values(), key=lambda c: c["term"]):
    for t in c.get("tensions", []):
        T.append(f"<div class='tension'><b><a href='c/{cslug[c['key']]}.html'>{H(S(c['term']))}</a></b><p>{H(S(t['text']))}</p></div>")
for k, c in sorted(fws.items(), key=lambda kv: kv[1]["name"]):
    for t in c.get("tensions", []):
        T.append(f"<div class='tension'><b><a href='f/{fslug[k]}.html'>{H(S(c['name']))}</a></b><p>{H(S(t['text']))}</p></div>")
open(f"{OUT}/tensions.html", "w", encoding="utf8").write(page(
    "说法差异", f"<h1>讲稿内部的不同说法</h1><p>共 {len(T)} 条。只汇集不裁决，点概念名可看原文引文。</p>" + "".join(T), 1, "华严知识库"))

home = f"""<h1>华严讲稿学习站</h1><p class="lead">整理自华严书院公开讲稿，并附原文引文。</p>
<h2>《佛说阿弥陀经》讲解</h2>
<ol class="toc"><li><a href="amtj-easy/index.html">轻松版</a><span class="t">更口语、带例子和思考题，每页内容不少于详细版。</span></li>
<li><a href="amtj/index.html">详细版</a><span class="t">逐段对照经文，依讲稿与答疑整理。</span></li></ol>
<h2>华严知识库</h2>
<ol class="toc"><li><a href="kb/index.html">概念卡（{len(cards)}）</a><span class="t">每个概念：讲者怎么说、不同用法、各讲稿讲法、说法不一之处、原文引文。</span></li>
<li><a href="kb/frameworks.html">框架卡（{len(fws)}）</a><span class="t">六波罗蜜、三处十会、住行向地等成员列表与次序。</span></li>
<li><a href="kb/tensions.html">说法差异（{len(T)}）</a><span class="t">各页讲法不一致之处，汇集而不裁决。</span></li></ol>"""
open("site/index.html", "w", encoding="utf8").write(page("华严讲稿学习站", home, 0, "", nav=False))
print(len(cards), "concept pages,", len(fws), "framework pages,", len(T), "tensions")

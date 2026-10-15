"""Build the whole site: landing page, 阿弥陀经, 讲座 (lecture digests), 问答 (Q&A digests), 知识库, 关于.
Usage: python -I scripts/build_site.py
Runs the section builders (阿弥陀经 detailed + easy, knowledge base) and then renders the remaining pages from
kb/digests/** and kb/manifest.json. Output: site/ (static HTML, Simplified Chinese)."""
import collections, glob, json, os, re, runpy, sys

sys.path.insert(0, "scripts")
import site_common
from site_common import H, S

sys.stdout.reconfigure(encoding="utf-8")
runpy.run_path("scripts/build_amtj_site.py", run_name="__main__")
runpy.run_path("scripts/build_amtj_easy_site.py", run_name="__main__")
KB = runpy.run_path("scripts/build_kb_site.py")
CSS = KB["CSS"]
byname, cslug, fslug, norm = KB["byname"], KB["cslug"], KB["fslug"], KB["norm"]
MAN = {e["id"]: e for e in json.load(open("kb/manifest.json", encoding="utf8"))}

LECT, QA_GROUPS = site_common.LECT, site_common.QA_GROUPS
URL, LECT_ITEMS, QA_ITEMS = site_common.page_map()
AUTO = ('<p class="auto">本页由整理程序根据原讲稿生成：概括文字是整理者的话，不是讲者原话；带「」的引文逐字取自原稿，'
        '出处见小字。概括可能有疏漏，请以原稿为准。</p>')


def page(path, title, body, on=""):
    depth = path.count("/")
    html = (f'<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>{H(title)}{'' if title == site_common.SITE else ' · ' + site_common.SITE}</title><style>{CSS}</style></head><body>{site_common.bar(depth, on)}<main>{body}"
            '<p class="note">整理自<a href="https://huayan.academy/">华严书院</a>公开讲稿，仅供学习；内容版权归原作者。</p></main></body></html>')
    os.makedirs(os.path.dirname("site/" + path) or "site", exist_ok=True)
    open("site/" + path, "w", encoding="utf8").write(html)


def clean_title(t):
    t = S((t or "").split("\n")[0]).strip()
    return re.sub(r"^《(.*)》$", r"\1", t) or "（无题）"


def q(text):
    return f'<q class="orig">{H(S(text))}</q>'


def ul(items, cls=""):
    items = [i for i in items if i]
    return f"<ul{cls}>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>" if items else ""


def ol(items):
    items = [i for i in items if i]
    return "<ol>" + "".join(f"<li>{i}</li>" for i in items) + "</ol>" if items else ""


def concept_link(name, depth):
    r = byname.get(norm(name))
    if not r:
        return f'<span class="c">{H(S(name))}</span>'
    t, k = r
    return f'<a href="{"../" * depth}kb/{t}/{(cslug if t == "c" else fslug)[k]}.html">{H(S(name))}</a>'


def render_digest(d, depth, qa_first=False):
    b = []
    if d.get("gist"):
        b.append(f'<div class="tldr"><b>要点</b>{H(S(d["gist"]))}</div>')
    qa = ""
    if d.get("qa"):
        qa = "<h2>问与答</h2>" + "".join(
            f'<div class="qa"><b>问：{H(S(x.get("question", "")))}</b><div class="a">答（概括）：{H(S(x.get("answer_summary", "")))}'
            + (f'<br>{q(x["quote"])}' if x.get("quote") else "") + "</div></div>" for x in d["qa"])
    if qa_first:
        b.append(qa)
    if d.get("summary"):
        b.append(f"<h2>概述</h2><p>{H(S(d['summary']))}</p>")
    if d.get("outline"):
        b.append("<h2>结构</h2>" + "".join(
            f"<h3>{H(S(o.get('heading', '')))}</h3>" + ul(H(S(p)) for p in o.get("points", []))
            for o in d["outline"]))
    if d.get("teachings"):
        b.append("<h2>主要观点</h2><ul>" + "".join(
            f"<li>{H(S(t.get('claim', '')))}" + (f"<br>{q(t['quote'])}" if t.get("quote") else "") + "</li>" for t in d["teachings"]) + "</ul>")
    if d.get("frameworks"):
        b.append("<h2>框架</h2>" + "".join(
            f'<div class="ex"><b>{concept_link(f.get("name", ""), depth)}</b>' + ol(H(S(i)) for i in f.get("items", [])) + "</div>"
            for f in d["frameworks"]))
    if d.get("examples"):
        b.append("<h2>例子与比喻</h2>" + "".join(
            f'<div class="ex"><b>{H(S(e.get("illustrates", "例子")))}</b><p>{H(S(e.get("setup", "")))}</p><p>{H(S(e.get("point", "")))}</p>'
            + (q(e["quote"]) if e.get("quote") else "") + "</div>" for e in d["examples"]))
    if d.get("how_to"):
        b.append("<h2>怎么用</h2>" + "".join(
            f'<div class="ex"><b>{H(S(h.get("situation", "")))}</b>' + ol(H(S(s)) for s in h.get("steps", []))
            + (q(h["quote"]) if h.get("quote") else "") + "</div>" for h in d["how_to"]))
    if not qa_first:
        b.append(qa)
    if d.get("sutra_refs"):
        b.append("<h2>涉及的经文</h2><ul class='open'>" + "".join(
            f"<li>{H(S(r.get('ref', '')))}" + (f"：{q(r['quote'])}" if r.get("quote") else "") + "</li>" for r in d["sutra_refs"]) + "</ul>")
    terms = []
    for c in d.get("concepts", []):
        t = c.get("term", "")
        if t and t not in terms:
            terms.append(t)
    if terms:
        b.append("<h2>本页概念</h2><p class='chips'>" + " ".join(concept_link(t, depth) for t in terms) + "</p>")
    if d.get("prerequisites"):
        b.append("<h2>读之前最好先了解</h2><p class='chips'>" + " ".join(concept_link(p, depth) for p in d["prerequisites"]) + "</p>")
    return "".join(b) + AUTO


def digest(pid):
    p = f"kb/digests/{pid}.json"
    return json.load(open(p, encoding="utf8")) if os.path.exists(p) else None


def pager(items, i, label):
    prev = items[i - 1] if i else None
    nxt = items[i + 1] if i + 1 < len(items) else None
    return ('<div class="pager"><span>' + (f'<a href="{prev[0]}">← {H(label(prev))}</a>' if prev else "") + "</span><span>"
            + (f'<a href="{nxt[0]}">{H(label(nxt))} →</a>' if nxt else "") + "</span></div>")


# ---------- 讲座
def orig_link(e):
    return f'<p class="conf"><a href="{site_common.original(e)}">在华严书院看原文 ↗</a></p>'


series_rows = []
for sid, name, desc in LECT:
    items = [(fn, e, digest(e["id"])) for fn, e in LECT_ITEMS[sid]]
    for i, (fn, e, d) in enumerate(items):
        body = (site_common.crumb([("讲座", "../index.html"), (name, "index.html"), (clean_title(e["title"]), None)])
                + f'<p class="kicker">{H(name)}</p><h1>{H(clean_title(e["title"]))}</h1>' + orig_link(e)
                + (f'<p class="more"><a href="../../amituo.html">经文逐段讲解 →</a></p>' if sid == "amtj" else "")
                + render_digest(d, 2) + pager(items, i, lambda x: clean_title(x[1]["title"])))
        page(f"jiang/{sid}/{fn}", f"{clean_title(e['title'])} · {name}", body, "讲座")
    toc = "".join(f'<li><a href="{fn}">{H(clean_title(e["title"]))}</a><span class="t">{H(S(d.get("gist", ""))[:110])}</span></li>'
                  for fn, e, d in items)
    page(f"jiang/{sid}/index.html", name,
         site_common.crumb([("讲座", "../index.html"), (name, None)]) + f"<h1>{H(name)}</h1><p class='lead'>{H(desc)}</p><ol class='toc'>{toc}</ol>", "讲座")
    series_rows.append((sid, name, desc, len(items)))
tiles = "".join(f'<a class="tile" href="{sid}/index.html"><b>{H(n)}</b><span>{H(d)}</span></a>' for sid, n, d, c in series_rows)
page("jiang/index.html", "讲座", "<h1>讲座</h1><p class='lead'>按讲稿系列浏览。每一讲有要点、结构、主要观点（附原文）、例子与本页概念，并可直接打开华严书院的原文。</p>"
     "<p class='conf'>各系列以《华严经》为主线。《华严经》经文与讲稿的逐段对照尚在整理，只会覆盖讲稿明确引用的部分。</p>"
     f"<div class='grid'>{tiles}</div>", "讲座")

# ---------- 问答
LISTING = site_common.qa_listing()
also = collections.defaultdict(list)          # digested page id -> other pages whose content it contains
for rows_ in LISTING.values():
    for e, href, cov in rows_:
        if cov:
            also[cov].append(e)
groups = collections.OrderedDict()
all_rows = []
known = {g[0] for g in QA_GROUPS}
for folder, slug, label, sec in QA_GROUPS:
    items = [(fn, e, digest(e["id"])) for fn, e in QA_ITEMS[slug]]
    listing = LISTING[slug]
    if not listing:
        continue
    groups[slug] = (label, sec, len(listing), len(items))
    for i, (fn, e, d) in enumerate(items):
        t = clean_title(e["title"])
        date = f'<p class="conf">{H(e["date"])}</p>' if e.get("date") else ""
        dup = ""
        if also.get(e["id"]):
            dup = ("<p class='conf'>同一内容也以这些标题出现：" + "；".join(
                f'<a href="{site_common.original(x)}">{H(clean_title(x["title"]))}</a>' for x in also[e["id"]][:8])
                + ("…" if len(also[e["id"]]) > 8 else "") + "</p>")
        body = (site_common.crumb([("问答", "../index.html"), (label, "index.html"), (t, None)])
                + f'<p class="kicker">{H(label)}</p><h1>{H(t)}</h1>{date}' + orig_link(e) + dup + render_digest(d, 2, qa_first=True)
                + pager(items, i, lambda x: clean_title(x[1]["title"])[:20]))
        page(f"wen/{slug}/{fn}", f"{t} · {label}", body, "问答")
    toc = []
    for e, href, cov in listing:
        t = clean_title(e["title"])
        if href and not cov:
            d = digest(e["id"])
            toc.append(f'<li><a href="../../{href}">{H(t)}</a><span class="t">{H(S(d.get("gist", ""))[:110])}</span></li>')
            all_rows.append((href, t, label, S(d.get("gist", ""))))
        elif href:
            ct = clean_title(MAN[cov]["title"])
            toc.append(f'<li><a href="../../{href}">{H(t)}</a><span class="t">与另一篇内容相同，整理在「{H(ct)}」中，点击前往。</span></li>')
            all_rows.append((href, t, label, ""))
        else:
            toc.append(f'<li><a href="{site_common.original(e)}">{H(t)} ↗</a><span class="t">未单独整理，链接到华严书院原文。</span></li>')
            all_rows.append((site_common.original(e), t, label, ""))
    page(f"wen/{slug}/index.html", label, site_common.crumb([("问答", "../index.html"), (label, None)])
         + f"<h1>{H(label)}</h1><p class='lead'>{len(listing)} 篇</p><ol class='toc'>{''.join(toc)}</ol>", "问答")
missing = {e["series"] for e in MAN.values() if "dayi" in e["series"] and e["series"] not in known and e["kind"] == "content"}
secs = collections.OrderedDict()
for slug, (label, sec, n, nd) in groups.items():
    secs.setdefault(sec, []).append(f'<a class="tile" href="{slug}/index.html"><b>{H(label)}</b><span>{n} 篇</span></a>')
rows = "".join(f"<tr data-t='{H(t + ' ' + g)}' style='display:none'><td><a href='{h}'>{H(t)}</a><br><span class='conf'>{H(l)}</span></td></tr>"
               for h, t, l, g in ((h if h.startswith("http") else h[len("wen/"):], t, l, g) for h, t, l, g in all_rows))
js = ("<script>document.getElementById('q').addEventListener('input',e=>{const v=e.target.value.trim();"
      "document.querySelectorAll('tr[data-t]').forEach(r=>r.style.display=v&&r.dataset.t.includes(v)?'':'none')})</script>")
n_digested = len({h for h, *_ in all_rows if not h.startswith("http")})
page("wen/index.html", "问答", f"<h1>问答</h1><p class='lead'>{len(all_rows)} 篇答疑，按分类与年份浏览，或直接搜索标题。</p>"
     f"<input id='q' placeholder='搜索问答标题与要点…'><table class='idx'>{rows}</table>"
     + "".join(f"<h2>{H(s)}</h2><div class='grid'>{''.join(v)}</div>" for s, v in secs.items())
     + "<p class='conf'>分组名称由整理者根据各组标题拟定。许多答疑在不同分组里重复出现，重复的只整理一次，其他标题链接到整理好的那一篇；"
       "少数内容很短或几乎全是重复的页面未整理，直接链接到华严书院原文。</p>" + js, "问答")

# ---------- 阿弥陀经
PLAN = json.load(open("content/amtj/PLAN.json", encoding="utf8"))["pages"]
psg = []
for p in PLAN:
    det = json.load(open(f"content/amtj/{p['slug']}.json", encoding="utf8")) if os.path.exists(f"content/amtj/{p['slug']}.json") else {}
    easy_ok = os.path.exists(f"site/amtj-easy/{p['slug']}.html")
    text = "".join(S(e["text"]) for e in p["sutra_excerpts"])
    links = (f'<a href="amtj-easy/{p["slug"]}.html">轻松读</a> · ' if easy_ok else "") + f'<a href="amtj/{p["slug"]}.html">详细讲解</a>'
    psg.append(f'<div class="sutra"><p class="cap">第 {p["order"]} 段 · {H(det.get("title", S(p["title_trad"])))}</p><p>{H(text)}</p>'
               f'<p class="conf">{links}</p></div>')
page("amituo.html", "佛说阿弥陀经", f"""<h1>《佛说阿弥陀经》</h1>
<p class="lead">鸠摩罗什译。全经分 {len(PLAN)} 段，每段先列经文，再依《佛说阿弥陀经大义》及相关讲稿、答疑讲解。</p>
<div class="grid"><a class="tile" href="amtj-easy/index.html"><b>轻松读</b><span>口语、例子、思考题；不用先懂术语</span></a>
<a class="tile" href="amtj/index.html"><b>详细讲解</b><span>逐段对照，引文逐字可查</span></a>
<a class="tile" href="jiang/amtj/index.html"><b>《佛说阿弥陀经大义》讲稿</b><span>按讲浏览原讲稿的整理</span></a></div>
<h2>经文全文</h2><p class="conf">点每段下方的链接看这一段的讲解。经文取自 CBETA T12n0366。</p>{"".join(psg)}""", "阿弥陀经")

# ---------- 关于
n_cards, n_fw = len(cslug), len(fslug)
page("about.html", "关于", f"""<h1>关于本站</h1>
<p>本站是对<a href="https://huayan.academy/">华严书院</a>（「认识生命，觉悟华严」）公开讲稿与答疑的学习整理，不是新的讲解。讲稿与答疑的内容版权归原作者；本站不代表原作者。</p>
<h2>内容从哪里来</h2><ul>
<li>讲稿：华严经二十八讲、华严七十讲、十信位、别教菩萨四位行法、佛说阿弥陀经大义。</li>
<li>答疑：2018–2022 分类答疑、2023、2024 年答疑及专题答疑。</li>
<li>经文：《佛说阿弥陀经》鸠摩罗什译，取自 <a href="https://www.cbeta.org/">CBETA</a>（T12n0366）。</li></ul>
<h2>怎么整理的</h2><ol>
<li>每一页原稿整理成一份摘要：要点、结构、观点、例子、概念。每条观点都附一段原文；原文逐字核对过，确实出自所标的那一页。</li>
<li>把各页里同一个概念的说法汇成一张概念卡（{n_cards} 张），框架汇成框架卡（{n_fw} 张）。不同页面说法不一时，并列记录，不作裁决。</li>
<li>抽查：另请独立审读者对照原稿上下文，复核 240 条概括文字。约 82% 完全有据，16% 部分有据（已改写），2% 无据（已删除）。</li></ol>
<h2>请注意</h2><ul>
<li>引文（「」内）逐字可靠；概括文字是整理者的话，可能多说或漏说，请以原稿为准。</li>
<li>站内文字一律转为简体；引文原为繁体。</li>
<li>重复或已被其他页面覆盖的答疑页，没有单独收录。</li></ul>""", "关于")

# ---------- 首页
n_lect = sum(c for *_, c in series_rows)
page("index.html", "华严讲稿学习站", f"""<div class="hero"><h1>华严讲稿学习站</h1>
<p>整理华严书院公开讲稿与答疑：按经文读、按讲座读、按问题找、按概念查。每段整理都附原文引文。</p></div>
<h2>从这里开始</h2><div class="grid">
<a class="tile" href="amtj-easy/index.html"><b>《阿弥陀经》轻松读</b><span>第一次接触？从这部短经开始，一段一段读。</span></a>
<a class="tile" href="kb/index.html"><b>查一个概念</b><span>种性、道种智、黄金为地……{n_cards} 个概念，讲者怎么说、各页怎么讲。</span></a>
<a class="tile" href="wen/index.html"><b>找一个问题</b><span>{len(all_rows)} 篇答疑，可搜索标题。</span></a></div>
<h2>全部内容</h2><div class="grid">
<a class="tile" href="amituo.html"><b>佛说阿弥陀经</b><span>经文全文，逐段讲解（轻松版与详细版）</span></a>
<a class="tile" href="jiang/index.html"><b>讲座</b><span>{len(series_rows)} 个讲稿系列，{n_lect} 讲</span></a>
<a class="tile" href="wen/index.html"><b>问答</b><span>{len(groups)} 组答疑</span></a>
<a class="tile" href="kb/index.html"><b>知识库</b><span>概念卡、框架卡、讲稿内部的不同说法</span></a>
<a class="tile" href="about.html"><b>关于</b><span>来源、整理方法与注意事项</span></a></div>""")
print(f"site: {n_lect} lecture pages, {len(all_rows)} Q&A titles ({n_digested} digested pages) in {len(groups)} groups; unmapped Q&A folders: {sorted(missing)}")

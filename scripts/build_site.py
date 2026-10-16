"""Build the whole site: landing page, 阿弥陀经, 讲座 (lecture digests), 答疑 (Q&A digests), 知识库, 关于.
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


def series_concepts(sid, n=18):
    """concepts most often discussed in a series (by number of its pages that define/explain them), with a card"""
    cnt = collections.Counter()
    for fn, e in LECT_ITEMS[sid]:
        seen = set()
        for c in digest(e["id"]).get("concepts", []):
            r = byname.get(norm(c.get("term", "")))
            if r and r[0] == "c" and c.get("role") in ("defined", "explained") and r[1] not in seen:
                seen.add(r[1])
                cnt[r[1]] += 1
    return [k for k, _ in cnt.most_common(n)]


def tags(e):
    """品 / topic tags the original site puts in the page's head title, e.g. 十信位之七｜華嚴經｜十信位｜光明覺品"""
    if e["series"] == "pages/zongshi":
        return []
    segs = [s.strip() for s in re.split(r"[｜|]", e.get("head_title", ""))[2:]]
    return [S(s) for s in segs if s and S(s) not in ("华严经", "十信位", "十住位", "别教菩萨四位行法")]


series_rows = []
for sid, short, name, c0, c1, parts in LECT:
    items = [(fn, e, digest(e["id"])) for fn, e in LECT_ITEMS[sid]]
    home = ("../../amituo.html", "阿弥陀经") if sid == "amtj" else ("index.html", short)
    for i, (fn, e, d) in enumerate(items):
        body = (site_common.crumb([(home[1], home[0]), (clean_title(e["title"]), None)])
                + f'<p class="kicker">{H(name)}</p><h1>{H(clean_title(e["title"]))}</h1>' + orig_link(e)
                + (f'<p class="more"><a href="../../amituo.html">经文逐段讲解 →</a></p>' if sid == "amtj" else "")
                + render_digest(d, 2) + pager(items, i, lambda x: clean_title(x[1]["title"])))
        page(f"jiang/{sid}/{fn}", f"{clean_title(e['title'])} · {name}", body, short)

    def li(fn, e, d):
        tg = "".join(f'<span class="badge">{H(x)}</span>' for x in tags(e))
        return f'<li><a href="{fn}">{H(clean_title(e["title"]))}</a>{tg}<span class="t">{H(S(d.get("gist", ""))[:110])}</span></li>'

    if parts == "by_part":           # 总释: the essay collection's own parts (and 五十三参's stage groups)
        toc, cur = "", None
        for x in items:
            e = x[1]
            if e.get("part") != cur:
                toc += ("</ol>" if cur is not None else "") + f"<h2>{H(S(e.get('part', '')))}</h2><ol class='toc'>"
                cur, grp = e.get("part"), None
            if e.get("group") and e.get("group") != grp:
                grp = e["group"]
                toc += f"<li class='grp'><b>{H(S(grp))}</b></li>"
            toc += li(*x)
        toc += "</ol>"
    elif parts:
        toc = ""
        for lo, hi, label in parts:
            sub = [x for x in items if lo <= x[1]["order"] <= hi]
            toc += f"<h2>{H(label)}</h2><ol class='toc'>" + "".join(li(*x) for x in sub) + "</ol>"
    else:
        toc = "<h2>目录</h2><ol class='toc'>" + "".join(li(*x) for x in items) + "</ol>"
    desc = H(S(site_common.cidi(c0, c1))).replace("\n", "<br>")
    extra = ""
    if sid == "swxf":
        extra = ("<p class='conf'>华严书院目前发布的是其中的十住位部分（本站 {} 篇）；原站注明这部分内容「还在不断拓展」。</p>".format(len(items)))
    if sid == "amtj":
        extra = "<p class='conf'>本节是讲稿本身的整理；经文逐段对照的讲解见<a href='../../amituo.html'>阿弥陀经</a>。</p>"
    keys = series_concepts(sid)
    kc = ("<h2>本系列常讲的概念</h2><p class='chips'>" + " ".join(
        f'<a href="../../kb/c/{cslug[k]}.html">{H(S(KB["cards"][k]["term"]))}</a>' for k in keys) + "</p>") if keys else ""
    first = items[0][0] if items else "#"
    page(f"jiang/{sid}/index.html", name,
         (site_common.crumb([("阿弥陀经", "../../amituo.html"), (name, None)]) if sid == "amtj" else "")
         + f"<h1>{H(name)}</h1><blockquote class='orig-desc'>{desc}<span class='src'>—— 华严书院《华严经学习次第》</span></blockquote>"
         + extra + f"<p class='more'><a href='{first}'>从第一{'篇' if sid == 'zongshi' else '讲'}开始读 →</a></p>" + kc + toc, "阿弥陀经" if sid == "amtj" else short)
    series_rows.append((sid, short, name, len(items)))

# ---------- 答疑
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
        body = (site_common.crumb([("答疑", "../index.html"), (label, "index.html"), (t, None)])
                + f'<p class="kicker">{H(label)}</p><h1>{H(t)}</h1>{date}' + orig_link(e) + dup + render_digest(d, 2, qa_first=True)
                + pager(items, i, lambda x: clean_title(x[1]["title"])[:20]))
        page(f"wen/{slug}/{fn}", f"{t} · {label}", body, "答疑")
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
    page(f"wen/{slug}/index.html", label, site_common.crumb([("答疑", "../index.html"), (label, None)])
         + f"<h1>{H(label)}</h1><p class='lead'>{len(listing)} 篇</p><ol class='toc'>{''.join(toc)}</ol>", "答疑")
missing = {e["series"] for e in MAN.values() if "dayi" in e["series"] and e["series"] not in known and e["kind"] == "content"}
secs = collections.OrderedDict()
for slug, (label, sec, n, nd) in groups.items():
    secs.setdefault(sec, []).append(f'<a class="tile" href="{slug}/index.html"><b>{H(label)}</b><span>{n} 篇</span></a>')
rows = "".join(f"<tr data-t='{H(t + ' ' + g)}' style='display:none'><td><a href='{h}'>{H(t)}</a><br><span class='conf'>{H(l)}</span></td></tr>"
               for h, t, l, g in ((h if h.startswith("http") else h[len("wen/"):], t, l, g) for h, t, l, g in all_rows))
js = ("<script>document.getElementById('q').addEventListener('input',e=>{const v=e.target.value.trim();"
      "document.querySelectorAll('tr[data-t]').forEach(r=>r.style.display=v&&r.dataset.t.includes(v)?'':'none')})</script>")
n_digested = len({h for h, *_ in all_rows if not h.startswith("http")})
page("wen/index.html", "答疑", f"<h1>答疑</h1><p class='lead'>{len(all_rows)} 篇答疑，按分类与年份浏览，或直接搜索标题。</p>"
     f"<input id='q' placeholder='搜索答疑标题与要点…'><table class='idx'>{rows}</table>"
     + "".join(f"<h2>{H(s)}</h2><div class='grid'>{''.join(v)}</div>" for s, v in secs.items())
     + "<p class='conf'>分组名称由整理者根据各组标题拟定。许多答疑在不同分组里重复出现，重复的只整理一次，其他标题链接到整理好的那一篇；"
       "少数内容很短或几乎全是重复的页面未整理，直接链接到华严书院原文。</p>" + js, "答疑")

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
<li>讲稿与论文：华严经总释二十八讲、华严七十讲、华严经·十信位、华严经·十住位（四位行法）、佛说阿弥陀经大义。《觉悟华严经·总释》（132 篇小论文）。</li>
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
zs = MAN["pages/juewu_s/jw_hyjzs"]
row = {sid: (short, name, n) for sid, short, name, n in series_rows}
tile = lambda sid, extra="": f'<a class="tile" href="jiang/{sid}/index.html"><b>{H(row[sid][1])}</b><span>{row[sid][2]} 篇{extra}</span></a>'
page("index.html", site_common.SITE, f"""<div class="hero"><h1>华严讲稿学习站</h1>
<p>整理华严书院公开讲稿与答疑：每一讲有要点、结构和附原文的观点，概念有汇总，答疑可搜索。</p></div>
<h2>学习次第</h2>
<blockquote class="orig-desc">{H(S(site_common.cidi("要全面系統學習華嚴經", "具體經文。")))}<span class="src">—— 华严书院《华严经学习次第》</span></blockquote>
<div class="grid">{tile("huayan28", "：初学入门，从这里开始")}{tile("huayan70", "：逐品解读经文")}
{tile("zongshi", "：一百三十二篇小论文，与七十讲对照读") if row.get("zongshi", (0, 0, 0))[2] else f'<a class="tile" href="{site_common.original(zs)}"><b>觉悟华严经·总释 ↗</b><span>本站尚未整理，链接到华严书院原文</span></a>'}</div>
<h2>行法次第</h2><div class="grid">{tile("shixin", "：自性为行法实践提供的能力")}{tile("swxf", "：别教菩萨四位行法之十住位")}</div>
<h2>经典</h2><div class="grid">
<a class="tile" href="amituo.html"><b>佛说阿弥陀经</b><span>经文全文与逐段讲解（轻松版、详细版）</span></a>
<a class="tile" href="amtj-easy/index.html"><b>《阿弥陀经》轻松读</b><span>第一次接触？不用先懂术语，一段一段读</span></a></div>
<h2>答疑与概念</h2><div class="grid">
<a class="tile" href="wen/index.html"><b>答疑</b><span>{len(all_rows)} 篇，按分类与年份，可搜索标题</span></a>
<a class="tile" href="kb/index.html"><b>概念</b><span>{len(cslug)} 个概念：讲者怎么说、各讲稿怎么讲、说法不一之处</span></a>
<a class="tile" href="kb/frameworks.html"><b>框架</b><span>{len(fslug)} 个：六波罗蜜、三处十会、住行向地……成员与次序</span></a></div>""")
print(f"site: {n_lect} lecture pages, {len(all_rows)} Q&A titles ({n_digested} digested pages) in {len(groups)} groups; unmapped Q&A folders: {sorted(missing)}")

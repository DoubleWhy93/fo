"""Render content/amtj/*.json (+ the sutra excerpts from PLAN.json) to site/amtj/*.html (Simplified Chinese).
Usage: python -I scripts/build_amtj_site.py"""
import glob, html, json, os, re, sys
import opencc
sys.path.insert(0, 'scripts')
import site_common

sys.stdout.reconfigure(encoding="utf-8")
S = opencc.OpenCC("t2s").convert
MAN = {e["id"]: e for e in json.load(open("kb/manifest.json", encoding="utf8"))}
PLAN = json.load(open("content/amtj/PLAN.json", encoding="utf8"))["pages"]
OUT = "site/amtj"
H = html.escape

CSS = """:root{--bg:#fbf8f2;--fg:#2b2622;--mute:#7a6f63;--acc:#8a4b2a;--card:#fff;--line:#e6dccd;--soft:#f3ebdd;--sutra:#f0f4ea}
@media (prefers-color-scheme:dark){:root{--bg:#1d1a17;--fg:#ece5da;--mute:#a79a8a;--acc:#e0a173;--card:#26221e;--line:#3a342d;--soft:#2a2520;--sutra:#232a21}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:18px/1.85 "Noto Serif SC","Songti SC","Source Han Serif SC",serif}
main{max-width:46rem;margin:0 auto;padding:2rem 1.2rem 5rem}
nav.top{font-size:.9rem;color:var(--mute);display:flex;justify-content:space-between;gap:1rem;flex-wrap:wrap}
a{color:var(--acc)}h1{font-size:2rem;line-height:1.3;margin:.2em 0}h2{font-size:1.3rem;margin:2.2em 0 .6em;color:var(--acc)}
.kicker{color:var(--mute);font-size:.9rem;letter-spacing:.08em}.lead{font-size:1.2rem}
.tldr{background:var(--soft);border-left:4px solid var(--acc);padding:.9rem 1.2rem;border-radius:6px;margin:1.4rem 0}
.tldr b{display:block;color:var(--acc);font-size:.85rem;letter-spacing:.1em;margin-bottom:.2rem}
.sutra{background:var(--sutra);border:1px solid var(--line);border-radius:8px;padding:1rem 1.3rem;margin:1.4rem 0}
.sutra .cap{font-size:.82rem;color:var(--mute);margin:0 0 .5rem}.sutra p{margin:.45em 0;font-size:1.08rem}
q.orig{quotes:"「" "」";font-style:normal;background:var(--soft);padding:.05em .3em;border-radius:3px}
sup.src{font-size:.68rem;color:var(--mute);margin-left:.2em;white-space:nowrap}
.cov{border:1px dashed var(--acc);border-radius:8px;padding:.7rem 1rem;margin:1.2rem 0;font-size:.95rem;background:var(--card)}
.cov b{color:var(--acc)}
.ex,.qa{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:.7rem 1.1rem;margin:1rem 0}
.ex>b,.qa>b{color:var(--acc)}.qa .a{margin-top:.3rem}
dl.gl dt{font-weight:700;color:var(--acc);margin-top:1rem}dl.gl dd{margin:.15rem 0 0}
ul.open{font-size:.95rem;color:var(--mute)}
.pager{display:flex;justify-content:space-between;gap:1rem;margin-top:3rem;padding-top:1rem;border-top:1px solid var(--line);font-size:.95rem}
.note{font-size:.85rem;color:var(--mute);border-top:1px solid var(--line);margin-top:2.5rem;padding-top:1rem}
ol.toc{padding-left:0;list-style:none}ol.toc li{margin:1rem 0;padding:.7rem 1rem;background:var(--card);border:1px solid var(--line);border-radius:8px}
ol.toc .n{color:var(--mute);margin-right:.5rem}ol.toc .t{font-size:.92rem;color:var(--mute);display:block;margin-top:.2rem}
.badge{font-size:.72rem;border:1px solid var(--line);border-radius:99px;padding:.05rem .5rem;margin-left:.4rem;color:var(--mute)}
"""

SERIES = {"huayan28": "二十八讲", "huayan70": "七十讲", "shixin": "十信位", "swxf": "行法", "amtj": "阿弥陀经大义"}


URL = site_common.page_map()[0]


def src_link(sid):
    """source label, linked to that page's digest on this site when there is one"""
    return f'<a href="../{URL[sid]}">{H(label(sid))}</a>' if sid in URL else H(label(sid))


def label(sid):
    e = MAN[sid]
    parts = sid.split("/")
    t = S(e.get("title") or sid)
    t = re.sub(r"[《》]", "", t)
    if parts[1] == "amtj":
        m = re.search(r"第(.)讲", t)
        return "阿弥陀经大义·" + (f"第{m.group(1)}讲" if m else "目录")
    if parts[1] in SERIES:
        return f"{SERIES[parts[1]]}·{t[:16]}"
    if parts[1].startswith("dayi"):
        return "答疑·" + (t[:16] + ("…" if len(t) > 16 else ""))
    return t[:20]


def segs(items):
    out = []
    for s in items:
        if "q" in s:
            out.append(f'<q class="orig">{H(S(s["q"]))}</q><sup class="src">{src_link(s["src"])}</sup>')
        else:
            out.append(H(s["t"]))
    return "".join(out)


def render_block(b):
    if "h2" in b:
        return f'<h2>{H(b["h2"])}</h2>'
    if "p" in b:
        return f"<p>{segs(b['p'])}</p>"
    if "example" in b:
        e = b["example"]
        return f'<div class="ex"><b>{H(e.get("title", "例子"))}</b><p>{segs(e["p"])}</p></div>'
    if "qa" in b:
        e = b["qa"]
        return f'<div class="qa"><b>问：{H(e["q"])}</b><div class="a">答：{segs(e["a"])}</div></div>'
    if "dl" in b:
        return '<dl class="gl">' + "".join(f"<dt>{H(i['dt'])}</dt><dd>{segs(i['dd'])}</dd>" for i in b["dl"]) + "</dl>"
    return ""


COVER = {"lecture": "", "partial": "讲稿仅部分涉及本段", "qa": "讲稿未覆盖本段，说明取自答疑与相关讲次", "none": "知识库暂无对本段的讲解"}


def shell(title, body, up=True):
    return (f'<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>{H(title)} · {site_common.SITE}</title><style>{CSS}{site_common.BAR_CSS}</style></head><body>{site_common.bar(1, '阿弥陀经')}<main>{S(body)}</main></body></html>")


def build():
    os.makedirs(OUT, exist_ok=True)
    pages = {}
    for f in sorted(glob.glob("content/amtj/[0-9]*.json")):
        d = json.load(open(f, encoding="utf8"))
        pages[d["slug"]] = d
    order = [p for p in PLAN if p["slug"] in pages]
    for i, p in enumerate(order):
        d = pages[p["slug"]]
        prev = order[i - 1] if i else None
        nxt = order[i + 1] if i + 1 < len(order) else None
        cap = "".join(f"<p>{H(S(e['text']))}</p>" for e in p["sutra_excerpts"])
        cov = ""
        if d["coverage"] != "lecture":
            cov = f'<div class="cov"><b>{H(COVER[d["coverage"]])}</b>　{H(d.get("coverage_note", ""))}</div>'
        openq = ""
        if d.get("open_questions"):
            openq = "<h2>留待核对</h2><ul class=\"open\">" + "".join(f"<li>{H(x)}</li>" for x in d["open_questions"]) + "</ul>"
        pager = '<div class="pager"><span>' + (f'<a href="{prev["slug"]}.html">← {H(S(prev["title_trad"]))}</a>' if prev else "") + \
                '</span><span>' + (f'<a href="{nxt["slug"]}.html">{H(S(nxt["title_trad"]))} →</a>' if nxt else "") + "</span></div>"
        body = (f'<nav class="top"><a href="../amituo.html">阿弥陀经</a> · <a href="index.html">《佛说阿弥陀经》讲解</a><span>{p["order"]} / {len(order)}</span></nav>'
                f'<p class="kicker">{H(d.get("kicker", "佛说阿弥陀经"))}</p><h1>{H(d["title"])}</h1>'
                f'<p class="lead">{segs(d["lead"])}</p>'
                f'<div class="sutra"><p class="cap">经文 · 鸠摩罗什译（CBETA T12n0366）</p>{cap}</div>'
                f'<div class="tldr"><b>一句话</b>{H(d["tldr"])}</div>{cov}'
                + "".join(render_block(b) for b in d["blocks"]) + openq + pager +
                '<p class="note">本页的讲解全部取自公开发布的《佛说阿弥陀经大义》及相关讲稿与答疑；引文逐字核对原稿，右上角小字为出处。这是学习整理，不是新的讲解。</p>')
        open(f"{OUT}/{p['slug']}.html", "w", encoding="utf8").write(shell(f"{d['title']} · 佛说阿弥陀经讲解", body))
    toc = "".join(
        f'<li><span class="n">{p["order"]}.</span><a href="{p["slug"]}.html">{H(pages[p["slug"]]["title"])}</a>'
        f'<span class="badge">{H(COVER[pages[p["slug"]]["coverage"]]) or "有讲稿"}</span><span class="t">{H(pages[p["slug"]]["tldr"])}</span></li>'
        for p in order)
    body = ('<p class="kicker">佛说阿弥陀经大义 · 经文讲解</p><h1>《佛说阿弥陀经》讲解</h1>'
            '<p class="lead">依经文次第，每一段先列原文，再用讲者自己的话解读；每处引文都可回查原稿。</p>'
            f'<ol class="toc">{toc}</ol>'
            '<p class="note">经文：鸠摩罗什译，CBETA T12n0366。讲解：取自《佛说阿弥陀经大义》八讲及知识库中的相关讲稿与答疑，版权归原作者。</p>')
    open(f"{OUT}/index.html", "w", encoding="utf8").write(shell("《佛说阿弥陀经》讲解", body))
    print(f"built {len(order)} pages + index -> {OUT}/")


if __name__ == "__main__":
    build()

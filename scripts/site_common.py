"""Shared shell for the site: global top bar, extra CSS, simplified-Chinese helpers."""
import html, re
import opencc

S = opencc.OpenCC("t2s").convert
H = html.escape

NAV = [("华严经", "huayan/index.html"), ("二十八讲", "jiang/huayan28/index.html"), ("总释", "jiang/zongshi/index.html"), ("七十讲", "jiang/huayan70/index.html"), ("十信位", "jiang/shixin/index.html"),
       ("十住位", "jiang/swxf/index.html"), ("阿弥陀经", "amituo.html"), ("答疑", "wen/index.html"), ("知识库", "kb/index.html"), ("华严与AI", "ai.html"), ("搜索", "search.html"), ("关于", "about.html")]

BAR_CSS = """.gbar{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);display:flex;gap:1rem;align-items:center;
justify-content:space-between;flex-wrap:wrap;padding:.5rem 1.2rem;font:15px/1.5 "Noto Sans SC","PingFang SC",sans-serif}
.gbar .brand{font-weight:700;text-decoration:none;color:var(--fg)}.gbar nav a{margin-left:.85rem;white-space:nowrap;text-decoration:none;color:var(--acc)}
.gbar nav a.on{font-weight:700;border-bottom:2px solid var(--acc)}
.crumb{font-size:.88rem;color:var(--mute);margin:.2rem 0 .6rem}.crumb a{color:var(--mute)}
.hero{padding:1.6rem 0 .4rem}.hero h1{font-size:2.2rem}.hero p{font-size:1.15rem;color:var(--mute)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(15rem,1fr));gap:.9rem;margin:1rem 0}
.tile{display:block;background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.9rem 1.1rem;text-decoration:none;color:var(--fg)}
.tile b{color:var(--acc);display:block;font-size:1.1rem}.tile span{font-size:.92rem;color:var(--mute)}
.tile:hover{border-color:var(--acc)}
table.idx{width:100%;border-collapse:collapse;font-size:.97rem}table.idx td,table.idx th{border-bottom:1px solid var(--line);padding:.45rem .4rem;text-align:left;vertical-align:top}
.chips a,.chips span.c{display:inline-block;margin:.15rem .3rem .15rem 0;padding:.05rem .6rem;border:1px solid var(--line);border-radius:99px;text-decoration:none;font-size:.9rem}
.tension{background:var(--card);border:1px dashed var(--acc);border-radius:8px;padding:.7rem 1rem;margin:1rem 0}
input#q{width:100%;padding:.6rem .8rem;font-size:1rem;border:1px solid var(--line);border-radius:8px;background:var(--card);color:var(--fg)}
.conf{font-size:.8rem;color:var(--mute)}.card-sum{font-size:1.1rem}
.orig-desc{margin:1rem 0;padding:.8rem 1.1rem;border-left:4px solid var(--acc);background:var(--soft);border-radius:6px;font-size:1rem}
.orig-desc .src{display:block;font-size:.8rem;color:var(--mute);margin-top:.4rem}
ol.toc li.grp{background:none;border:none;padding:0;margin:1.2rem 0 .2rem;color:var(--acc)}
.ev{position:relative;display:inline-block;font:12px/1.6 "Noto Sans SC","PingFang SC",sans-serif;color:var(--acc);border:1px solid var(--line);
border-radius:99px;padding:0 .5rem;margin-left:.35rem;cursor:pointer;vertical-align:.12em;user-select:none}
.ev:hover,.ev.open{border-color:var(--acc)}
.ev-pop{display:none;position:absolute;z-index:20;left:0;top:1.9em;width:min(30rem,80vw);background:var(--card);border:1px solid var(--acc);
border-radius:8px;padding:.6rem .85rem;font:16px/1.75 "Noto Serif SC","Songti SC",serif;color:var(--fg);box-shadow:0 6px 20px rgba(0,0,0,.15);cursor:auto;user-select:text}
.ev-pop span.q{display:block;margin:.2rem 0}.ev-pop span.q::before{content:"「"}.ev-pop span.q::after{content:"」"}
.ev-pop small{display:block;font-size:.78rem;color:var(--mute);margin-bottom:.3rem}
@media (hover:hover){.ev:hover .ev-pop{display:block}}
.ev.open .ev-pop{display:block}
@media (max-width:640px){.ev{position:static}.ev-pop{left:1rem;right:1rem;width:auto}}
.jump{font-size:.85rem;color:var(--mute);margin:.4rem 0 1rem;line-height:2}.jump a{white-space:nowrap}
h2[id]{scroll-margin-top:4.5rem}
.sutra-c{background:var(--sutra);border:1px solid var(--line);border-radius:8px 8px 0 0;padding:.7rem 1.1rem;margin:1.2rem 0 0;font-size:1.06rem;white-space:pre-line}
.plain-c{background:var(--card);border:1px solid var(--line);border-top:none;padding:.7rem 1.1rem;margin:0;white-space:pre-line}
.plain-c:last-child,.plain-c+.sutra-c{border-radius:0 0 8px 8px}
.mean-c{background:var(--soft);border:1px solid var(--line);border-top:none;border-left:4px solid var(--acc);border-radius:0 0 8px 8px;padding:.7rem 1.1rem;margin:0 0 1.2rem}
.mean-c .cap{display:block;font-size:.75rem;color:var(--acc);margin-bottom:.2rem}
.sutra-c .cap,.plain-c .cap{display:block;font-size:.75rem;color:var(--mute);margin-bottom:.2rem;white-space:normal}
.cov-q{border-left:4px solid var(--acc)}.badge.ok{border-color:var(--acc);color:var(--acc)}
.ai-theme{border:1px solid var(--line);border-radius:10px;padding:.2rem 1.1rem .8rem;margin:1.6rem 0;background:var(--card)}
.ai-say{background:var(--soft);border-left:4px solid var(--acc);border-radius:6px;padding:.6rem .9rem;margin:.6rem 0}
.ai-say b,.ai-h b,.ai-m b{display:block;font-size:.8rem;letter-spacing:.05em;margin-bottom:.15rem}
.ai-say b{color:var(--acc)}.ai-h,.ai-m{padding:.5rem .9rem;margin:.5rem 0;border-radius:6px;border:1px dashed var(--line)}
.ai-h b,.ai-m b{color:var(--mute)}.ai-think{font-size:.95rem;color:var(--mute);margin:.6rem 0 0}
.auto{font-size:.82rem;color:var(--mute);border-left:3px solid var(--line);padding-left:.7rem;margin:1rem 0}
"""


SITE = "华严讲稿学习站"
LECT = [  # (series id, nav name, section title, start/end of the original site's own description on 学习次第 (root/cidi), parts)
    ("huayan28", "二十八讲", "华严经总释二十八讲", "《覺悟華嚴經·總釋二十八講》（１冊）", "比較詳細的說明。",
     [(1, 6, "第一部分：隋唐时期中国佛教史简介"), (7, 12, "第二部分：佛教经典语言解读"), (13, 99, "第三部分：华严经行法理论和行法次第")]),
    ("zongshi", "总释", "觉悟华严经·总释", "《覺悟華嚴經·總釋》（１冊）", "等七個部分。", "by_part"),
    ("huayan70", "七十讲", "华严七十讲", "《覺悟華嚴經·華嚴七十講》（3冊）", "本來義理。", None),
    ("shixin", "十信位", "华严经·十信位", "《華嚴經·十信位》是對", "怎樣的保證。", None),
    ("swxf", "十住位", "华严经·十住位", "《華嚴經·四位行法》是對", "無上正覺。", None),
    ("amtj", "阿弥陀经", "佛说阿弥陀经大义", "《佛說阿彌陀經大義》以華嚴經", "密法的解讀。", None),
]


def cidi(start, end):
    """verbatim stretch of the original site's 学习次第 page, from `start` through `end`"""
    t = open("kb/sources/root/cidi.md", encoding="utf8").read().split("\n---\n", 1)[1]
    i = t.index(start)
    return t[i:t.index(end, i) + len(end)]


QA_GROUPS = [  # (folder, slug, label, section) — labels written by the editor from each group's page titles
    ("pages/dayi_all/2018-2022dy/flWORD/hyxf", "hyxf", "华严行法", "2018–2022 分类答疑"),
    ("pages/dayi_all/2018-2022dy/flWORD/jtl", "jtl", "教理：大小乘与权、别、圆", "2018–2022 分类答疑"),
    ("pages/dayi_all/2018-2022dy/flWORD/swms-dzz", "swms", "闻法模式与内在觉知", "2018–2022 分类答疑"),
    ("pages/dayi_all/2018-2022dy/flWORD/jdjd", "jdjd", "经典解读", "2018–2022 分类答疑"),
    ("pages/dayi_all/2018-2022dy/flWORD/jx-br", "jxbr", "见性与般若", "2018–2022 分类答疑"),
    ("pages/dayi_all/2018-2022dy/flWORD/wm-lb", "wmlb", "无明与了别", "2018–2022 分类答疑"),
    ("pages/dayi_all/2018-2022dy/flWORD/sz", "sz", "四智十方", "2018–2022 分类答疑"),
    ("pages/dayi_all/2018-2022dy/flWORD/fs-mfjd", "fs", "法数", "2018–2022 分类答疑"),
    ("pages/dayi_all/2018-2022dy/dy", "juewu2021", "《觉悟华严经》答疑（2021）", "2018–2022 分类答疑"),
    ("pages/dayi_all/2023dy/fl", "y2023", "2023 年答疑", "年度答疑"),
    ("pages/dayi_all/2023dy/wz/WORDbb", "y2023w", "2023–2024 答疑文字稿", "年度答疑"),
    ("pages/dayi_all/2024dy/fl", "y2024", "2024 年答疑", "年度答疑"),
    ("pages/dayi_all/2024dy/2024dywd", "y2024w", "2024 年答疑（问答稿）", "年度答疑"),
    ("pages/dayi", "changjian", "常见问题", "专题与其他"),
    ("pages/dayi_all/dyjx", "xuexi", "怎样学习《华严经》", "专题与其他"),
    ("pages/dayi_all/ztjz", "zhuanti", "专题答疑", "专题与其他"),
    ("pages/dayi_all/fjzxlydy/-fjzxly-dywzb", "zhexue", "《华严哲学论义》答疑", "专题与其他"),
]


def page_map():
    """source page id -> its page on this site (path from the site root), for every page that has a digest.
    Also returns the ordered item lists per lecture series / Q&A group (used by build_site)."""
    import json, os
    man = json.load(open("kb/manifest.json", encoding="utf8"))
    has = lambda pid: os.path.exists(f"kb/digests/{pid}.json")
    key = lambda e: (e["order"] if e["order"] >= 0 else 999, e["id"])
    url, lect, qa = {}, {}, {}
    for sid, *_ in LECT:
        ents = sorted((e for e in man if e["series"] == f"pages/{sid}" and e["kind"] == "content" and has(e["id"])), key=key)
        lect[sid] = [(e["id"].split("/")[-1] + ".html", e) for e in ents]
        for fn, e in lect[sid]:
            url[e["id"]] = f"jiang/{sid}/{fn}"
    for folder, slug, *_ in QA_GROUPS:
        ents = sorted((e for e in man if e["series"] == folder and e["kind"] == "content" and has(e["id"])), key=key)
        qa[slug] = [(f"{i:03d}.html", e) for i, e in enumerate(ents, 1)]
        for fn, e in qa[slug]:
            url[e["id"]] = f"wen/{slug}/{fn}"
    return url, lect, qa


def original(e):
    """the page on the original site (huayan.academy serves the same paths as the crawl)"""
    from urllib.parse import quote
    return "https://huayan.academy/" + quote(e["src"])


def qa_listing():
    """every Q&A page per group, digested or not: slug -> [(manifest entry, site path or None, covering page id or None)].
    Pages skipped during digestion (kb/analysis/qa-ledger.json) point to the digested page that contains them."""
    import json
    man = json.load(open("kb/manifest.json", encoding="utf8"))
    url = page_map()[0]
    by = {x["id"]: x.get("by") for x in json.load(open("kb/analysis/qa-ledger.json", encoding="utf8"))}

    def cover(pid):
        seen = 0
        while pid and pid not in url and seen < 10:
            pid, seen = by.get(pid), seen + 1
        return pid if pid in url else None

    key = lambda e: (e["order"] if e["order"] >= 0 else 999, e["id"])
    out = {}
    for folder, slug, *_ in QA_GROUPS:
        rows = []
        for e in sorted((e for e in man if e["series"] == folder and e["kind"] == "content"), key=key):
            if e["id"] in url:
                rows.append((e, url[e["id"]], None))
            else:
                c = cover(e["id"])
                rows.append((e, url[c] if c else None, c))
        out[slug] = rows
    return out


EV_JS = ("<script>document.addEventListener('click',e=>{const t=e.target.closest('.ev');"
         "if(t&&e.target.closest('.ev-pop'))return;document.querySelectorAll('.ev.open').forEach(x=>{if(x!==t)x.classList.remove('open')});"
         "if(t)t.classList.toggle('open')});document.addEventListener('keydown',e=>{const t=e.target.closest&&e.target.closest('.ev');"
         "if(t&&(e.key==='Enter'||e.key===' ')){e.preventDefault();t.classList.toggle('open')}if(e.key==='Escape')"
         "document.querySelectorAll('.ev.open').forEach(x=>x.classList.remove('open'))})</script>")


def ev(items):
    """the original text behind a claim, hidden behind a small 「原文」 tag (hover on desktop, tap on phones).
    items: [(quote html-escaped text, source html or "")]"""
    items = [(q, s) for q, s in items if q]
    if not items:
        return ""
    body = "".join(f'<span class="q">{q}</span>' + (f"<small>—— {s}</small>" if s else "") for q, s in items)
    return f'<span class="ev" tabindex="0" role="button" aria-label="查看原文">原文<span class="ev-pop">{body}</span></span>'


def bar(depth=1, on=""):
    up = "../" * depth
    links = "".join(f'<a href="{up}{h}"{" class=on" if n == on else ""}>{n}</a>' for n, h in NAV)
    return f'<header class="gbar"><a class="brand" href="{up}index.html">华严讲稿学习站</a><nav>{links}</nav></header>{EV_JS}'


def crumb(items, depth=1):
    """items: [(label, href or None)]; href relative to the page"""
    return '<div class="crumb">' + " › ".join(f'<a href="{h}">{H(l)}</a>' if h else H(l) for l, h in items) + "</div>"

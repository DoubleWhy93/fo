"""Shared shell for the site: global top bar, extra CSS, simplified-Chinese helpers."""
import html, re
import opencc

S = opencc.OpenCC("t2s").convert
H = html.escape

NAV = [("阿弥陀经", "amituo.html"), ("讲座", "jiang/index.html"), ("问答", "wen/index.html"), ("知识库", "kb/index.html"), ("关于", "about.html")]

BAR_CSS = """.gbar{position:sticky;top:0;z-index:5;background:var(--bg);border-bottom:1px solid var(--line);display:flex;gap:1rem;align-items:center;
justify-content:space-between;flex-wrap:wrap;padding:.5rem 1.2rem;font:15px/1.5 "Noto Sans SC","PingFang SC",sans-serif}
.gbar .brand{font-weight:700;text-decoration:none;color:var(--fg)}.gbar nav a{margin-left:1rem;text-decoration:none;color:var(--acc)}
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
.auto{font-size:.82rem;color:var(--mute);border-left:3px solid var(--line);padding-left:.7rem;margin:1rem 0}
"""


SITE = "华严讲稿学习站"
LECT = [  # (series id, display name, one-line description written from the series' own titles)
    ("shixin", "华严经·十信位", "十信位行法，17 讲"),
    ("swxf", "华严经·别教菩萨四位行法", "十住、十行、十回向、十地四位行法，36 讲"),
    ("huayan28", "华严经二十八讲", "28 讲"),
    ("huayan70", "华严七十讲", "71 讲"),
    ("amtj", "佛说阿弥陀经大义", "8 讲；经文逐段讲解见「阿弥陀经」栏目"),
]
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


def bar(depth=1, on=""):
    up = "../" * depth
    links = "".join(f'<a href="{up}{h}"{" class=on" if n == on else ""}>{n}</a>' for n, h in NAV)
    return f'<header class="gbar"><a class="brand" href="{up}index.html">华严讲稿学习站</a><nav>{links}</nav></header>'


def crumb(items, depth=1):
    """items: [(label, href or None)]; href relative to the page"""
    return '<div class="crumb">' + " › ".join(f'<a href="{h}">{H(l)}</a>' if h else H(l) for l, h in items) + "</div>"

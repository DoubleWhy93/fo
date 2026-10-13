"""Render content/amtj-easy/*.json (+ sutra excerpts from content/amtj/PLAN.json) to site/amtj-easy/*.html.
Usage: python -I scripts/build_amtj_easy_site.py"""
import glob, html, json, os, re, sys
import opencc

sys.stdout.reconfigure(encoding="utf-8")
S = opencc.OpenCC("t2s").convert
MAN = {e["id"]: e for e in json.load(open("kb/manifest.json", encoding="utf8"))}
PLAN = json.load(open("content/amtj/PLAN.json", encoding="utf8"))["pages"]
OUT = "site/amtj-easy"
H = html.escape

CSS = """:root{--bg:#fffaf1;--fg:#2a2520;--mute:#7b6f62;--acc:#b0542a;--card:#fff;--line:#eadfce;--soft:#fbeedb;--sutra:#eef4e6;--think:#e8f0f8}
@media (prefers-color-scheme:dark){:root{--bg:#1c1916;--fg:#efe8dc;--mute:#a99d8d;--acc:#f0a678;--card:#26221e;--line:#3b342c;--soft:#2c2620;--sutra:#222a20;--think:#202a34}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:19px/1.9 "Noto Sans SC","PingFang SC","Microsoft YaHei",sans-serif}
main{max-width:40rem;margin:0 auto;padding:1.6rem 1.1rem 4rem}
nav.top{font-size:.88rem;color:var(--mute);display:flex;justify-content:space-between;gap:1rem}a{color:var(--acc)}
h1{font-size:1.7rem;line-height:1.4;margin:.6em 0 .3em}.hook{font-size:1.15rem;color:var(--fg);margin:.2em 0 1.2em}
h2{font-size:1.1rem;margin:2.2em 0 .6em;color:var(--acc);letter-spacing:.04em}
.sutra{background:var(--sutra);border:1px solid var(--line);border-radius:12px;padding:.8rem 1.1rem;margin:1rem 0}
.sutra .cap{font-size:.78rem;color:var(--mute);margin:0 0 .3rem}.sutra p{margin:.4em 0;font-size:1rem;line-height:1.85}
.surface{border-left:4px solid var(--line);padding:.2rem 1rem;margin:1rem 0;color:var(--fg)}
.surface .lab{display:block;font-size:.78rem;color:var(--mute);letter-spacing:.06em}
.card{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:.8rem 1.1rem;margin:.9rem 0}
.card b{display:block;color:var(--acc);font-size:1.02rem;margin-bottom:.1rem}.card p{margin:.2rem 0}
details{margin-top:.5rem;font-size:.9rem;color:var(--mute)}summary{cursor:pointer}
q.orig{quotes:"「" "」";font-style:normal;display:block;margin:.3rem 0;padding:.4rem .7rem;background:var(--soft);border-radius:8px;color:var(--fg);line-height:1.7}
.src{font-size:.75rem;color:var(--mute)}
.story{background:var(--soft);border-radius:14px;padding:.9rem 1.2rem;margin:1rem 0}.story b{color:var(--acc)}
.think{background:var(--think);border-radius:14px;padding:.8rem 1.2rem;margin:1rem 0}.think li{margin:.5rem 0}
.take{font-size:1.2rem;font-weight:600;text-align:center;margin:2.2rem 0 1rem;line-height:1.6}
.unsure{font-size:.9rem;color:var(--mute);border-top:1px dashed var(--line);margin-top:2rem;padding-top:.6rem}
.cov{border:1px dashed var(--acc);border-radius:10px;padding:.5rem .9rem;margin:1rem 0;font-size:.9rem}
.pager{display:flex;justify-content:space-between;gap:1rem;margin-top:2.5rem;padding-top:1rem;border-top:1px solid var(--line);font-size:.95rem}
.more{font-size:.9rem;margin-top:1.5rem}
ol.toc{list-style:none;padding:0}ol.toc li{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:.7rem 1rem;margin:.8rem 0}
ol.toc .h{display:block;font-size:.9rem;color:var(--mute);margin-top:.15rem;line-height:1.6}
.note{font-size:.8rem;color:var(--mute);margin-top:2rem}
"""

COVER = {"lecture": "", "partial": "讲稿只部分涉及这一段", "qa": "讲稿没有直接讲到这一段，下面的说明来自答疑与其他讲次", "none": "知识库里暂时没有对这一段的讲解"}


def label(sid):
    e = MAN[sid]
    parts = sid.split("/")
    t = re.sub(r"[《》]", "", S(e.get("title") or sid))
    if parts[1] == "amtj":
        m = re.search(r"第(.)讲", t)
        return "阿弥陀经大义·" + (f"第{m.group(1)}讲" if m else "目录")
    names = {"huayan28": "二十八讲", "huayan70": "七十讲", "shixin": "十信位", "swxf": "行法"}
    if parts[1] in names:
        return f"{names[parts[1]]}·{t[:14]}"
    if parts[1].startswith("dayi"):
        return "答疑·" + t[:14]
    return t[:18]


def quotes_html(qs):
    if not qs:
        return ""
    items = "".join(f'<q class="orig">{H(S(q["q"]))}<span class="src">　—— {H(label(q["src"]))}</span></q>' for q in qs)
    return f"<details><summary>看讲者原话</summary>{items}</details>"


def shell(title, body):
    return (f'<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f"<title>{H(title)}</title><style>{CSS}</style></head><body><main>{body}</main></body></html>")


def build():
    os.makedirs(OUT, exist_ok=True)
    pages = {}
    for f in sorted(glob.glob("content/amtj-easy/[0-9]*.json")):
        d = json.load(open(f, encoding="utf8"))
        pages[d["slug"]] = d
    order = [p for p in PLAN if p["slug"] in pages]
    for i, p in enumerate(order):
        d = pages[p["slug"]]
        prev = order[i - 1] if i else None
        nxt = order[i + 1] if i + 1 < len(order) else None
        cap = "".join(f"<p>{H(S(e['text']))}</p>" for e in p["sutra_excerpts"])
        cards = "".join(f'<div class="card"><b>{H(it["head"])}</b><p>{H(it["text"])}</p>{quotes_html(it.get("quotes"))}</div>' for it in d["ideas"])
        story = ""
        if d.get("story"):
            st = d["story"]
            story = f'<h2>🌱 一个小例子</h2><div class="story"><b>{H(st["title"])}</b><p>{H(st["text"])}</p>{quotes_html(st.get("quotes"))}</div>'
        think = '<h2>💭 想一想</h2><div class="think"><ol>' + "".join(f"<li>{H(q)}</li>" for q in d["think"]) + "</ol></div>"
        cov = ""
        if d["coverage"] != "lecture":
            cov = f'<div class="cov"><b>{H(COVER[d["coverage"]])}。</b>{H(d.get("coverage_note", ""))}</div>'
        uns = ""
        if d.get("unsure"):
            uns = '<div class="unsure"><b>还没定论：</b><ul>' + "".join(f"<li>{H(x)}</li>" for x in d["unsure"]) + "</ul></div>"
        pager = ('<div class="pager"><span>' + (f'<a href="{prev["slug"]}.html">← 上一段</a>' if prev else "") + "</span><span>" +
                 (f'<a href="{nxt["slug"]}.html">下一段 →</a>' if nxt else "") + "</span></div>")
        body = (f'<nav class="top"><a href="index.html">《阿弥陀经》轻松读</a><span>{p["order"]} / {len(order)}</span></nav>'
                f'<h1>{H(d["title"])}</h1><p class="hook">{H(d["hook"])}</p>'
                f'<div class="sutra"><p class="cap">经文 · 鸠摩罗什译</p>{cap}</div>'
                f'<div class="surface"><span class="lab">字面意思（整理者的白话，不是讲者原话）</span>{H(d["surface"])}</div>'
                f'{cov}<h2>🔎 讲者是怎么读的</h2>{cards}{story}{think}'
                f'<p class="take">✨ {H(d["takeaway"])}</p>{uns}'
                f'<p class="more"><a href="../amtj/{p["slug"]}.html">想看完整讲解（含全部原文引用）→</a></p>{pager}'
                '<p class="note">本页是对讲稿的简化整理，“讲者”指《佛说阿弥陀经大义》的讲者；所有“看讲者原话”都可回查原稿。</p>')
        open(f"{OUT}/{p['slug']}.html", "w", encoding="utf8").write(shell(f"{d['title']} · 阿弥陀经轻松读", body))
    toc = "".join(
        f'<li><a href="{p["slug"]}.html">{p["order"]}. {H(pages[p["slug"]]["title"])}</a>'
        f'<span class="h">{H(pages[p["slug"]]["hook"])}</span></li>' for p in order)
    body = ('<h1>《阿弥陀经》轻松读</h1>'
            '<p class="hook">不用背术语。每一段先看经文，再看讲者怎么读，最后留几个问题给你自己想。</p>'
            f'<ol class="toc">{toc}</ol>'
            '<p class="note">想要更完整、逐字可查的版本，请看<a href="../amtj/index.html">详细讲解</a>。经文：鸠摩罗什译，CBETA T12n0366；讲解取自《佛说阿弥陀经大义》及相关讲稿与答疑，版权归原作者。</p>')
    open(f"{OUT}/index.html", "w", encoding="utf8").write(shell("《阿弥陀经》轻松读", body))
    print(f"built {len(order)} pages + index -> {OUT}/")


if __name__ == "__main__":
    build()

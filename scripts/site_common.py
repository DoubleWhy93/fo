"""Shared shell for the site: global top bar, extra CSS, simplified-Chinese helpers."""
import html, re
import opencc

S = opencc.OpenCC("t2s").convert
H = html.escape

NAV = [("经典", "jing.html"), ("讲座", "jiang/index.html"), ("问答", "wen/index.html"), ("知识库", "kb/index.html"), ("关于", "about.html")]

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


def bar(depth=1, on=""):
    up = "../" * depth
    links = "".join(f'<a href="{up}{h}"{" class=on" if n == on else ""}>{n}</a>' for n, h in NAV)
    return f'<header class="gbar"><a class="brand" href="{up}index.html">华严讲稿学习站</a><nav>{links}</nav></header>'


def crumb(items, depth=1):
    """items: [(label, href or None)]; href relative to the page"""
    return '<div class="crumb">' + " › ".join(f'<a href="{h}">{H(l)}</a>' if h else H(l) for l, h in items) + "</div>"

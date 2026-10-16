"""Gather everything the knowledge base has for one 段 of 《華嚴經》, as a Markdown bundle for the explainer.

Usage: python -I scripts/huayan_context.py p11-s02 [out.md]      (default: prints to stdout)
Sections: the segment text (chunk ids) and its neighbours; KB pages that quote these exact lines (with the claims they
make about them); 總釋 essays on this 品; other lectures/Q&A that discuss the 品; concept cards for terms that occur in
the text. Every quote shown is verbatim from the page id next to it (digest quotes are verified), so it can be reused.
"""
import glob, json, re, sys
import opencc

sys.stdout.reconfigure(encoding="utf-8")
T2S = opencc.OpenCC("t2s").convert
seg_id = sys.argv[1]
pin = int(seg_id[1:3])
plan = json.load(open(f"content/huayan/p{pin:02d}/PLAN.json", encoding="utf8"))
segs = plan["segments"]
k = next(i for i, s in enumerate(segs) if s["seg"] == seg_id)
seg = segs[k]
cov = json.load(open("kb/sutra/huayan80/coverage.json", encoding="utf8"))
MAN = {e["id"]: e for e in json.load(open("kb/manifest.json", encoding="utf8"))}
fold = lambda s: re.sub(r"[^一-鿿]", "", T2S(s or ""))
seg_fold = fold("".join(c["text"] for c in seg["chunks"]))
_dig = {}


def dig(pid):
    if pid not in _dig:
        try:
            _dig[pid] = json.load(open(f"kb/digests/{pid}.json", encoding="utf8"))
        except FileNotFoundError:
            _dig[pid] = {}
    return _dig[pid]


def title(pid):
    return T2S(MAN.get(pid, {}).get("title", pid)).split("\n")[0]


def overlaps(q, n=12):
    fq = fold(q)
    return any(fq[i:i + n] in seg_fold for i in range(max(1, len(fq) - n + 1))) if len(fq) >= n else False


L = [f"# {seg_id} · 第{pin}品 {T2S(plan['title'])}（段 {k + 1}/{len(segs)}） · coverage: {seg['coverage']}\n",
     "## 经文（逐段 id，繁体原文）\n"]
for c in seg["chunks"]:
    L.append(f"- **{c['id']}**{'（偈颂）' if c['verse'] else ''}：{c['text']}")
if k:
    L.append(f"\n上一段结尾（{segs[k - 1]['seg']}）：…{segs[k - 1]['chunks'][-1]['text'][-150:]}")
if k + 1 < len(segs):
    L.append(f"下一段开头（{segs[k + 1]['seg']}）：{segs[k + 1]['chunks'][0]['text'][:150]}…")

L.append("\n## 1. 直接引用这几句经文的讲稿（最直接的依据）\n")
quoting = seg.get("quoted_by", [])
if not quoting:
    L.append("（知识库中没有页面逐字引用这一段。）")
for pid in quoting[:14]:
    d = dig(pid)
    L.append(f"### {pid} — {title(pid)}\n要点：{d.get('gist', '')}")
    for r in d.get("sutra_refs", []):
        if overlaps(r.get("quote", "")):
            L.append(f"- 引经：{r.get('ref', '')} ｜ quote: 「{r.get('quote', '')}」")
    for t in d.get("teachings", []):
        if overlaps(t.get("quote", "")):
            L.append(f"- 观点：{t.get('claim', '')} ｜ quote: 「{t.get('quote', '')}」")
    for t in d.get("teachings", [])[:40]:
        txt = T2S(t.get("claim", ""))
        if any(w in txt for w in ("这段", "此段", "经文")) and not overlaps(t.get("quote", "")):
            continue
L.append(f"\n## 2. 《总释》中讲这一品的短文\n")
pin_pages = cov["pins"][str(pin)]["pages"]
zs = [p["id"] for p in pin_pages if p["id"].startswith("pages/zongshi/")]
if not zs:
    L.append("（无）")
for pid in zs[:6]:
    d = dig(pid)
    L.append(f"### {pid} — {title(pid)}\n要点：{d.get('gist', '')}\n概述：{d.get('summary', '')}")
    for t in d.get("teachings", [])[:12]:
        L.append(f"- {t.get('claim', '')} ｜ quote: 「{t.get('quote', '')}」")

L.append(f"\n## 3. 讲到这一品的其他讲稿与答疑（只列名与相关要点）\n")
others = [p for p in pin_pages if not p["id"].startswith("pages/zongshi/") and p["id"] not in quoting]
for p in others[:25]:
    d = dig(p["id"])
    L.append(f"- {p['id']} — {title(p['id'])} ｜ {p['why']} ｜ 要点：{d.get('gist', '')[:120]}")
if len(others) > 25:
    L.append(f"- ……另有 {len(others) - 25} 页")

L.append("\n## 4. 经文中出现、知识库有概念卡的词\n")
cards = []
for f in glob.glob("kb/consolidated/concepts/*.json"):
    c = json.load(open(f, encoding="utf8"))
    names = [c["term"]] + c.get("aliases", [])
    hit = next((n for n in names if len(fold(n)) >= 2 and fold(n) in seg_fold), None)
    if hit:
        cards.append((len(fold(hit)), c, hit))
cards.sort(key=lambda x: -x[0])
for _, c, hit in cards[:15]:
    L.append(f"### {c['term']}（经文中出现为「{hit}」；卡：kb/consolidated/concepts/{c['key']}.json）\n摘要：{c['summary']}\n讲者怎么说：{c['definition']}")
    for q in c.get("definition_basis", [])[:2]:
        L.append(f"- quote: 「{q['q']}」 ({q['src']})")
if not cards:
    L.append("（无）")
out = "\n".join(L) + "\n"
if len(sys.argv) > 2:
    open(sys.argv[2], "w", encoding="utf8").write(out)
    print(f"{seg_id}: {len(out)} chars -> {sys.argv[2]}")
else:
    print(out)

"""Phase 6: where every source page ended up.

Usage: python -I scripts/coverage_report.py
Writes kb/coverage.md: per source page (kb/manifest.json) — kind, digest or why not (qa-ledger: superseded by /
duplicate / low novelty), its page on the site, how many concept cards quote it — plus totals per series and the
pages nobody uses. Read-only over the KB.
"""
import collections, glob, json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, "scripts")
import site_common

MAN = json.load(open("kb/manifest.json", encoding="utf8"))
URL = site_common.page_map()[0]
LEDGER = {x["id"]: x for x in json.load(open("kb/analysis/qa-ledger.json", encoding="utf8"))}
cites = collections.Counter()
for f in glob.glob("kb/consolidated/concepts/*.json") + glob.glob("kb/consolidated/frameworks/*.json"):
    c = json.load(open(f, encoding="utf8"))
    srcs = set()

    def walk(x):
        if isinstance(x, dict):
            if isinstance(x.get("src"), str):
                srcs.add(x["src"])
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)

    walk(c)
    srcs |= set(c.get("where_to_read", []))
    for s in srcs:
        cites[s] += 1


def group(e):
    p = e["id"].split("/")
    if p[0] != "pages":
        return p[0]
    return "答疑" if p[1].startswith("dayi") else p[1]


rows, tot = [], collections.defaultdict(collections.Counter)
for e in MAN:
    pid = e["id"]
    if e["kind"] in ("stub", "hub") or pid.startswith("pages/juewu_s/jw_"):
        status = "（导航/目录页）" if e["kind"] in ("stub", "hub") else "已拆分为 pages/zongshi/*"
        tot[group(e)]["structure"] += 1
    elif os.path.exists(f"kb/digests/{pid}.json"):
        status = "digest"
        tot[group(e)]["digested"] += 1
    elif pid in LEDGER:
        x = LEDGER[pid]
        status = {"superseded": f"内容见 {x.get('by')}", "exact_duplicate": "完全重复", "low_novel_skipped": "几乎全是重复内容，未整理"}.get(x["status"], x["status"])
        tot[group(e)]["covered elsewhere" if x["status"] != "low_novel_skipped" else "skipped"] += 1
    elif e["kind"] == "pdf":
        status = "PDF：已提取文字，未整理"
        tot[group(e)]["not digested"] += 1
    else:
        status = "未整理"
        tot[group(e)]["not digested"] += 1
    rows.append((group(e), pid, e.get("title", "").split("\n")[0][:30], status, URL.get(pid, ""), cites.get(pid, 0)))

L = ["# 来源覆盖报告\n", f"{len(MAN)} 个来源页面。每一页：是否整理、在站上的位置、被多少张概念/框架卡引用。\n",
     "| 系列 | 已整理 | 内容见他页/重复 | 跳过（几乎全重复） | 未整理 | 目录/结构页 |", "|---|---:|---:|---:|---:|---:|"]
for g in sorted(tot):
    t = tot[g]
    L.append(f"| {g} | {t['digested']} | {t['covered elsewhere']} | {t['skipped']} | {t['not digested']} | {t['structure']} |")
unused = [r for r in rows if r[3] == "digest" and r[5] == 0]
L.append(f"\n已整理但没有任何概念卡引用的页面：{len(unused)}（它们仍在讲座/答疑页里可读、可搜索）。\n")
L.append("## 未整理的页面\n")
L += [f"- {r[1]} — {r[2]} — {r[3]}" for r in rows if r[3].startswith(("未整理", "PDF"))] or ["- 无"]
L.append("\n## 全部页面\n\n| 页面 | 标题 | 状态 | 站内页面 | 被卡引用 |\n|---|---|---|---|---:|")
for g, pid, title, status, url, n in sorted(rows):
    L.append(f"| {pid} | {title} | {status} | {url} | {n} |")
open("kb/coverage.md", "w", encoding="utf8").write("\n".join(L) + "\n")
print("\n".join(L[:4 + len(tot)]))
print(f"... unused digests: {len(unused)}; not digested: {sum(1 for r in rows if r[3].startswith(('未整理', 'PDF')))}")

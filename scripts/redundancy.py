"""Phase 2: redundancy map over kb/sources (run extract.py and extract_pdf.py first).

Usage: python -I scripts/redundancy.py [--kb kb]

Text is reduced to Han characters only and mapped Traditional->Simplified per
character (so 爲/為, 纔/才 etc. compare equal). 8-char shingles are sampled by
hash (1 in 4) and indexed. From that:
  * novelty: fraction of each page's characters not already covered by an earlier
    page (ordering = lectures first, then Q&A by year) or repeated inside the page
  * pairwise containment -> duplicate clusters
  * overlap of web text with the PDFs (sutra text vs commentary)
  * repeated whole paragraphs (boilerplate / catch-phrases)
Writes kb/analysis/redundancy.json and kb/analysis/REPORT.md.
"""
import argparse, collections, json, os, re, zlib

K = 8          # shingle length
MOD = 4        # sample 1/MOD of shingles
DF_CAP = 60    # shingles in more docs than this are "common phrases", skipped for pairing
HAN = re.compile(r"[㐀-䶿一-鿿豈-﫿]")

SERIES_RANK = [
    "pages/huayan28", "pages/huayan70", "pages/shixin", "pages/swxf", "pages/juewu_s", "pages/amtj", "pages/dayi/",
    "pages/dayi_all/2018-2022dy", "pages/dayi_all/dyjx", "pages/dayi_all/ztjz", "pages/dayi_all/fjzxlydy",
    "pages/dayi_all/2023dy", "pages/dayi_all/2024dy", "root",
]


def rank(sid):
    for i, p in enumerate(SERIES_RANK):
        if sid.startswith(p):
            return i
    return len(SERIES_RANK)


def group_of(sid):
    s = sid
    if s.startswith("pdf/gangyao"):
        return "pdf-sutra"
    if s.startswith("pdf/"):
        return "pdf-other"
    return "web"


def series_label(sid):
    p = sid.split("/")
    if p[0] == "pdf":
        return "pdf"
    if p[0] == "root":
        return "root"
    if p[1] == "dayi_all":
        return "dayi_all/" + "/".join(x for x in p[2:-1] if x != "flWORD")
    return p[1]


def load_body(path):
    t = open(path, encoding="utf8").read()
    if t.startswith("---\n"):
        t = t.split("\n---\n", 1)[1]
    return t


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kb", default="kb")
    a = ap.parse_args()
    kb = os.path.abspath(a.kb)
    manifest = json.load(open(os.path.join(kb, "manifest.json"), encoding="utf8"))

    try:
        import opencc
        try:
            cc = opencc.OpenCC("t2s")
        except Exception:
            cc = opencc.OpenCC("t2s.json")
    except ImportError:
        cc = None
    cmap = {}

    def to_simp(s):
        out = []
        for ch in s:
            r = cmap.get(ch)
            if r is None:
                r = cc.convert(ch) if cc else ch
                r = r[0] if len(r) == 1 else ch
                cmap[ch] = r
            out.append(r)
        return "".join(out)

    docs = []
    for m in manifest:
        if m["kind"] in ("stub",):
            continue
        body = load_body(os.path.join(kb, m["out"] if "out" in m else os.path.join("sources", m["id"] + ".md")))
        body = re.sub(r"<!-- p\d+ -->", "", body)
        paras = [p for p in body.split("\n\n") if p.strip()]
        han = "".join(HAN.findall(body))
        docs.append({"id": m["id"], "kind": m["kind"], "title": m.get("title", ""), "sha1": m.get("sha1"),
                     "group": group_of(m["id"]), "series": series_label(m["id"]), "order": m.get("order", -1),
                     "rank": rank(m["id"]), "han": to_simp(han), "paras": paras})
    # order: web by (rank, series path, order), pdfs last
    docs.sort(key=lambda d: (d["group"] != "web", d["rank"], d["id"].rsplit("/", 1)[0], d["order"], d["id"]))
    for i, d in enumerate(docs):
        d["idx"] = i
        d["n"] = len(d["han"])

    # ---- index sampled shingles
    postings = collections.defaultdict(list)  # hash -> [doc idx] (unique per doc, increasing)
    doc_sh = []                               # per doc: list of (pos, hash) sampled
    for d in docs:
        s = d["han"].encode("utf-16-le")  # 2 bytes/char, crc over exact slice
        lst = []
        seen = set()
        for p in range(0, max(0, d["n"] - K + 1)):
            h = zlib.crc32(s[2 * p: 2 * (p + K)])
            if h % MOD:
                continue
            lst.append((p, h))
            if h not in seen:
                seen.add(h)
                postings[h].append(d["idx"])
        doc_sh.append(lst)

    # ---- novelty
    def covered_mask(d, pred):
        """chars covered by sampled shingles satisfying pred(h, p)."""
        mask = bytearray(d["n"])
        for p, h in doc_sh[d["idx"]]:
            if pred(h, p):
                for q in range(p, p + K):
                    mask[q] = 1
        return mask

    web = [d for d in docs if d["group"] == "web"]
    for d in docs:
        i = d["idx"]
        # same-doc repeats: shingle seen earlier in this doc at distance >= K
        first_pos = {}
        selfmask = bytearray(d["n"])
        for p, h in doc_sh[i]:
            fp = first_pos.get(h)
            if fp is None:
                first_pos[h] = p
            elif p - fp >= K:
                for q in range(p, p + K):
                    selfmask[q] = 1
        d["self_rep"] = sum(selfmask)
        if d["group"] == "web":
            # earlier = other web docs with smaller idx
            earlier = covered_mask(d, lambda h, p: postings[h][0] < i)
            anyother = covered_mask(d, lambda h, p: any(j != i for j in postings[h] if docs[j]["group"] == "web") if len(postings[h]) < 200 else True)
            by_sutra = covered_mask(d, lambda h, p: any(docs[j]["group"] == "pdf-sutra" for j in postings[h]))
            by_pdfo = covered_mask(d, lambda h, p: any(docs[j]["group"] == "pdf-other" for j in postings[h]))
            novel = sum(1 for q in range(d["n"]) if not (earlier[q] or selfmask[q]))
            d["covered_earlier"] = sum(earlier)
            d["shared_any_web"] = sum(anyother)
            d["in_sutra_pdf"] = sum(by_sutra)
            d["in_other_pdf"] = sum(by_pdfo)
            d["novel"] = novel
            # novel excluding sutra quotation and other-PDF overlap (true "own" new content)
            d["novel_nonquote"] = sum(1 for q in range(d["n"]) if not (earlier[q] or selfmask[q] or by_sutra[q] or by_pdfo[q]))
        else:
            webcov = covered_mask(d, lambda h, p: any(docs[j]["group"] == "web" for j in postings[h]))
            d["in_web"] = sum(webcov)

    # ---- pairwise containment
    pair = collections.Counter()
    for h, lst in postings.items():
        if len(lst) < 2 or len(lst) > DF_CAP:
            continue
        for x in range(len(lst)):
            for y in range(x + 1, len(lst)):
                pair[(lst[x], lst[y])] += 1
    nsamp = [len({h for _, h in doc_sh[d["idx"]]}) or 1 for d in docs]
    edges = []
    for (x, y), c in pair.items():
        if c < 15:
            continue
        cx, cy = c / nsamp[x], c / nsamp[y]
        if max(cx, cy) >= 0.5:
            edges.append((x, y, round(cx, 2), round(cy, 2), c))
    edges.sort(key=lambda e: -max(e[2], e[3]))

    # union-find clusters (web<->web only, strong edges)
    parent = list(range(len(docs)))

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x

    for x, y, cx, cy, c in edges:
        if docs[x]["group"] == "web" and docs[y]["group"] == "web" and max(cx, cy) >= 0.6:
            parent[find(x)] = find(y)
    clusters = collections.defaultdict(list)
    for d in web:
        clusters[find(d["idx"])].append(d["idx"])
    clusters = [sorted(v) for v in clusters.values() if len(v) > 1]
    clusters.sort(key=lambda v: -len(v))

    # directional: page A mostly contained in a larger (or earlier equal-size) web page B
    best = {}
    for x, y, cx, cy, c in edges:
        if docs[x]["group"] != "web" or docs[y]["group"] != "web":
            continue
        for a_i, b_i, cont in ((x, y, cx), (y, x, cy)):
            if cont < 0.7:
                continue
            A, B = docs[a_i], docs[b_i]
            if B["n"] > A["n"] or (B["n"] == A["n"] and b_i < a_i):
                if a_i not in best or cont > best[a_i][1]:
                    best[a_i] = (b_i, cont)
    superseded = {docs[i]["id"]: {"by": docs[b]["id"], "contained": cont} for i, (b, cont) in best.items()}
    sup_by_series = collections.defaultdict(lambda: [0, 0, 0])
    for i in best:
        s = sup_by_series[docs[i]["series"]]
        s[0] += 1
        s[1] += docs[i]["n"]
    for d in web:
        sup_by_series[d["series"]][2] = sup_by_series[d["series"]][2] or 0
    sup_targets = collections.Counter(docs[b]["id"] for b, _ in best.values())

    # exact duplicates by sha1 and by normalised title
    by_sha = collections.defaultdict(list)
    by_title = collections.defaultdict(list)
    for d in web:
        if d["sha1"] and d["n"] > 0:
            by_sha[d["sha1"]].append(d["id"])
        t = re.sub(r"[^一-鿿]", "", to_simp(d["title"]))
        if t and d["kind"] == "content":
            by_title[t].append(d["id"])
    exact = [v for v in by_sha.values() if len(v) > 1]
    same_title = [v for v in by_title.values() if len(v) > 1]

    # repeated paragraphs
    pc = collections.defaultdict(set)
    ptxt = {}
    for d in web:
        for p in d["paras"]:
            k = "".join(HAN.findall(p))
            if len(k) >= 12:
                k = to_simp(k)
                pc[k].add(d["idx"])
                ptxt.setdefault(k, p)
    rep_paras = sorted(((len(v), k) for k, v in pc.items() if len(v) >= 4), reverse=True)

    # ---- aggregate by series
    agg = collections.OrderedDict()
    for d in web:
        s = d["series"]
        a_ = agg.setdefault(s, collections.Counter())
        a_["pages"] += 1
        for k in ("n", "novel", "novel_nonquote", "self_rep", "covered_earlier", "in_sutra_pdf", "in_other_pdf"):
            a_[k] += d[k]
    totals = collections.Counter()
    for v in agg.values():
        totals.update(v)

    # ---- write JSON
    os.makedirs(os.path.join(kb, "analysis"), exist_ok=True)
    out = {
        "params": {"K": K, "MOD": MOD, "DF_CAP": DF_CAP},
        "docs": [{k: d[k] for k in ("id", "kind", "title", "group", "series", "n", "self_rep", "novel", "novel_nonquote",
                                    "covered_earlier", "shared_any_web", "in_sutra_pdf", "in_other_pdf", "in_web") if k in d} for d in docs],
        "clusters": [[docs[i]["id"] for i in c] for c in clusters],
        "edges": [{"a": docs[x]["id"], "b": docs[y]["id"], "a_in_b": cx, "b_in_a": cy, "shared": c} for x, y, cx, cy, c in edges[:3000]],
        "superseded_by": superseded,
        "exact_duplicates": exact,
        "same_title": same_title,
        "repeated_paragraphs": [{"docs": n, "text": ptxt[k]} for n, k in rep_paras[:200]],
    }
    json.dump(out, open(os.path.join(kb, "analysis", "redundancy.json"), "w", encoding="utf8"), ensure_ascii=False, indent=1)

    # ---- report
    def pct(a_, b_):
        return f"{100 * a_ / b_:.0f}%" if b_ else "-"

    L = []
    L.append("# Redundancy report (Phase 2)\n")
    L.append(f"Han characters only, Traditional→Simplified normalized; shingle={K}, sampled 1/{MOD}. Percentages are of Han characters per series; "
             "approximate (±a few %), good for sizing not for exact accounting.\n")
    L.append("Ordering for “novel vs earlier”: lectures (28講, 70講, 十信, 行法, 覺悟華嚴, …) first, then Q&A by year. "
             "So Q&A that repeats a lecture counts as repeated, not the lecture.\n")
    L.append("## By series\n")
    L.append("| series | pages | chars | novel vs earlier | repeats inside page | in sutra PDFs (quote) | in commentary PDFs | **own new content** |")
    L.append("|---|---:|---:|---:|---:|---:|---:|---:|")
    for s, v in agg.items():
        L.append(f"| {s} | {v['pages']} | {v['n']:,} | {pct(v['novel'], v['n'])} | {pct(v['self_rep'], v['n'])} | {pct(v['in_sutra_pdf'], v['n'])} | {pct(v['in_other_pdf'], v['n'])} | {v['novel_nonquote']:,} ({pct(v['novel_nonquote'], v['n'])}) |")
    t = totals
    L.append(f"| **TOTAL** | {t['pages']} | {t['n']:,} | {pct(t['novel'], t['n'])} | {pct(t['self_rep'], t['n'])} | {pct(t['in_sutra_pdf'], t['n'])} | {pct(t['in_other_pdf'], t['n'])} | **{t['novel_nonquote']:,} ({pct(t['novel_nonquote'], t['n'])})** |")
    L.append("\n“own new content” = chars not seen earlier, not repeated inside the page, and not found in the PDFs. "
             "This is the realistic size of what Phase 3 must read closely; the rest is checked against what it duplicates.\n")

    L.append("## PDFs\n")
    L.append("| pdf | chars | share also present on web pages |")
    L.append("|---|---:|---:|")
    for d in docs:
        if d["group"] != "web":
            L.append(f"| {d['id']} | {d['n']:,} | {pct(d.get('in_web', 0), d['n'])} |")

    L.append("\n## Pages mostly contained in another page (≥70% of the page's text appears in a larger page)\n")
    tot_pages = {s: v["pages"] for s, v in agg.items()}
    L.append("| series | pages contained elsewhere | of pages | chars in those pages |")
    L.append("|---|---:|---:|---:|")
    for s, (n_, ch_, _) in sorted(sup_by_series.items()):
        L.append(f"| {s} | {n_} | {tot_pages.get(s, 0)} | {ch_:,} |")
    L.append(f"\nTotal: {len(best)} pages. Most-absorbing pages (long session transcripts / compilations):\n")
    for sid_, n_ in sup_targets.most_common(15):
        L.append(f"- `{sid_}` absorbs {n_} pages")

    L.append(f"\n## Exact duplicates and same-title pages\n")
    L.append(f"- exact-duplicate text (sha1): {len(exact)} groups")
    for g in exact[:30]:
        L.append("  - " + " = ".join(g))
    L.append(f"- same normalized title (content pages): {len(same_title)} groups")
    for g in same_title[:40]:
        L.append("  - " + " ~ ".join(g))

    L.append(f"\n## Duplicate clusters (containment ≥ 60%, web only): {len(clusters)} clusters, {sum(len(c) for c in clusters)} pages\n")
    L.append("(Clusters chain-merge through long transcripts, so treat as a rough grouping; the per-page table above is the actionable one. Full list in redundancy.json.)\n")
    for c in clusters[:12]:
        ids = [docs[i] for i in c]
        canon = max(ids, key=lambda d: d["n"])
        L.append(f"- **{len(c)} pages**, suggested canonical (longest): `{canon['id']}` ({canon['n']:,} chars)")
        for d in ids:
            if d is not canon:
                L.append(f"  - `{d['id']}` ({d['n']:,}) {d['title'][:30]}")

    L.append("\n## Strongest page pairs (containment of one page inside the other)\n")
    L.append("| a | b | a in b | b in a |")
    L.append("|---|---|---:|---:|")
    shown = 0
    for x, y, cx, cy, c in edges:
        if docs[x]["group"] == "web" and docs[y]["group"] == "web":
            L.append(f"| `{docs[x]['id']}` | `{docs[y]['id']}` | {cx:.0%} | {cy:.0%} |")
            shown += 1
            if shown >= 40:
                break

    L.append("\n## Most repeated paragraphs (≥12 Han chars, in ≥4 pages)\n")
    for n, k in rep_paras[:40]:
        L.append(f"- ×{n}: {ptxt[k][:90].replace(chr(10), ' ')}")

    open(os.path.join(kb, "analysis", "REPORT.md"), "w", encoding="utf8").write("\n".join(L) + "\n")
    print("\n".join(L[:30]))


if __name__ == "__main__":
    import sys
    sys.stdout.reconfigure(encoding="utf-8")
    main()

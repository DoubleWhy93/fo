"""Check digests against their sources.

Usage: python -I scripts/verify_digest.py [digest-dir-or-file ...]   (default: kb/digests)
For each digest: valid JSON, required keys, every `quote` found verbatim in the
source page (whitespace-insensitive), and a rough coverage figure: how much of
the source's text is within 'reach' of some quote (a smell test for pages whose
digest only touches a small part of the page).
Exit code 1 if any quote fails or a file is invalid.
"""
import json, os, re, sys

KB = "kb"
REQ = ["id", "title", "gist", "summary", "outline", "concepts", "teachings", "frameworks", "sutra_refs", "vivid", "qa", "repetition", "notes"]
WS = re.compile(r"\s+")
# variant characters the source uses inconsistently; compare quotes with these folded
FOLD = str.maketrans({"髙": "高", "恆": "恒", "內": "内", "爲": "為", "纔": "才", "裏": "裡", "迴": "回", "衆": "眾", "着": "著", "並": "并", "脇": "脅", "寳": "寶", "昩": "昧"})


try:
    import opencc
    _cc = opencc.OpenCC("t2s")
except Exception:  # fall back to the small variant table only
    _cc = None
_cmap = {}


def _simp(ch):
    r = _cmap.get(ch)
    if r is None:
        r = _cc.convert(ch) if _cc else ch
        r = r if len(r) == 1 else ch
        _cmap[ch] = r
    return r


def fold(t):
    """Whitespace removed and every character reduced to its simplified form (plus the variant table),
    so 麼/麽, 說/説, 藴/蘊, 夀/壽 and Traditional-vs-Simplified mixes in the source all compare equal."""
    t = WS.sub("", t).translate(FOLD)
    return "".join(_simp(c) for c in t)


def src_text(sid):
    t = open(os.path.join(KB, "sources", sid + ".md"), encoding="utf8").read()
    return fold(t.split("\n---\n", 1)[1])


def quotes(d):
    for sec in ("concepts", "teachings", "sutra_refs", "vivid", "qa", "examples", "how_to"):
        for i, it in enumerate(d.get(sec, [])):
            q = it.get("quote", "")
            if q:
                yield f"{sec}[{i}]", q


def check(path):
    errs, stats = [], {}
    try:
        d = json.load(open(path, encoding="utf8"))
    except Exception as e:
        return [f"invalid JSON: {e}"], stats
    for k in REQ:
        if k not in d:
            errs.append(f"missing key {k}")
    if errs:
        return errs, stats
    try:
        s = src_text(d["id"])
    except FileNotFoundError:
        return [f"source not found for id {d['id']}"], stats
    covered = bytearray(len(s))
    nq = 0
    for where, q in quotes(d):
        nq += 1
        qn = fold(q)
        i = s.find(qn)
        if i < 0:
            k = len(qn)
            while k > 3 and qn[:k] not in s:
                k -= 1
            errs.append(f"{where}: quote not in source: {q[:50]}  [first {k}/{len(qn)} folded chars match; mismatch near: {qn[k:k+8]}]")
        else:
            for j in range(max(0, i - 150), min(len(s), i + len(qn) + 150)):
                covered[j] = 1
    stats = {"quotes": nq, "teachings": len(d["teachings"]), "concepts": len(d["concepts"]),
             "reach": round(sum(covered) / max(1, len(s)), 2), "src_chars": len(s)}
    return errs, stats


def main():
    targets = sys.argv[1:] or [os.path.join(KB, "digests")]
    files = []
    for t in targets:
        if os.path.isdir(t):
            for d, _, fs in os.walk(t):
                files += [os.path.join(d, f) for f in fs if f.endswith(".json")]
        else:
            files.append(t)
    bad = 0
    print(f"{'file':45s} {'src':>6s} {'quotes':>6s} {'teach':>5s} {'conc':>5s} {'reach':>5s}  errors")
    for f in sorted(files):
        errs, st = check(f)
        bad += bool(errs)
        name = os.path.basename(f)[:44]
        print(f"{name:45s} {st.get('src_chars', 0):6d} {st.get('quotes', 0):6d} {st.get('teachings', 0):5d} {st.get('concepts', 0):5d} {st.get('reach', 0):5.2f}  {len(errs)}")
        for e in errs[:5]:
            print("    -", e)
    print(f"\n{len(files)} digests, {bad} with errors")
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()

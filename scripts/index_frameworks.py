"""Phase 4 step 4: index kb/consolidated/frameworks/*.json, cross-link with concept cards, collect tensions.
Usage: python -I scripts/index_frameworks.py
Writes kb/consolidated/FRAMEWORKS.md and kb/consolidated/framework-tensions.md. Cards are not modified."""
import glob, json, re, sys
import opencc
sys.stdout.reconfigure(encoding="utf-8")
T2S = opencc.OpenCC("t2s").convert
norm = lambda t: re.sub(r"[\s·、，,。《》“”\"'（）()：:；;\-—]", "", T2S(t or ""))
D = "kb/consolidated"
fw = [json.load(open(f, encoding="utf8")) for f in sorted(glob.glob(f"{D}/frameworks/*.json"))]
cc = {}
for f in glob.glob(f"{D}/concepts/*.json"):
    c = json.load(open(f, encoding="utf8"))
    cc[norm(c["term"])] = c["term"]
    cc[norm(c["key"])] = c["term"]
    for a in c.get("aliases", []):
        cc.setdefault(norm(a), c["term"])
rank = {"full": 0, "partial": 1, "fragmentary": 2}
L = ["# 框架卡索引\n", f"{len(fw)} 张框架卡。“完整度”指各页合起来能列出多少，不是理论上应有多少。\n",
     "| 框架 | 成员数 | 完整度 | 分歧 | 置信 | 同名概念卡 |", "|---|---:|---|---:|---|---|"]
tens = []
linked = 0
for c in sorted(fw, key=lambda c: (rank.get(c["completeness"], 3), -len(c["members"]), c["name"])):
    same = cc.get(norm(c["name"])) or cc.get(norm(c["key"]))
    linked += bool(same)
    L.append(f"| {c['name']} | {len(c['members'])} | {c['completeness']} | {len(c['tensions'])} | {c['confidence']} | {'有' if same else ''} |")
    for t in c["tensions"]:
        tens.append((c["name"], t["text"]))
open(f"{D}/FRAMEWORKS.md", "w", encoding="utf8").write("\n".join(L) + "\n")
T = [f"# 框架内部的不同列法（{len(tens)} 条）\n", "各框架卡里记录的成员、数目、顺序不一致之处，只汇集，不裁决。\n"]
T += [f"- **{n}**：{t}" for n, t in sorted(tens)]
open(f"{D}/framework-tensions.md", "w", encoding="utf8").write("\n".join(T) + "\n")
cnt = {k: sum(1 for c in fw if c["completeness"] == k) for k in rank}
print(len(fw), "frameworks;", cnt, "; tensions", len(tens), "; with same-name concept card", linked)

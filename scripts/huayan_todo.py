"""List 《華嚴經》 segments that have no 白话 page yet.

Usage: python -I scripts/huayan_todo.py            # progress per 品
       python -I scripts/huayan_todo.py 11         # undone segments of 品 11
       python -I scripts/huayan_todo.py 11 5       # the next 5 undone segments of 品 11
"""
import json, os, sys

sys.stdout.reconfigure(encoding="utf-8")
index = json.load(open("kb/sutra/huayan80/index.json", encoding="utf8"))


def segs(pin):
    plan = json.load(open(f"content/huayan/p{pin:02d}/PLAN.json", encoding="utf8"))
    return [(s, os.path.exists(f"content/huayan/p{pin:02d}/{s['seg']}.json")) for s in plan["segments"]]


if len(sys.argv) == 1:
    tot = done = 0
    for i in index:
        ss = segs(i["pin"])
        d = sum(x for _, x in ss)
        tot, done = tot + len(ss), done + d
        print(f"{i['pin']:>2} {i['title']:<10} {d:>4}/{len(ss):<4} quoted {sum(s['coverage'] == 'quoted' for s, _ in ss)}")
    print(f"total {done}/{tot}")
else:
    pin = int(sys.argv[1])
    n = int(sys.argv[2]) if len(sys.argv) > 2 else 10 ** 6
    for s, d in segs(pin):
        if not d and n > 0:
            print(s["seg"], s["coverage"], s["chars"], "chars")
            n -= 1

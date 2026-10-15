"""sample/动画-距离不是公里数.html — an animated explainer (3Blue1Brown-style: one picture, built up step by step).
Narration is mine; every author quote is verified verbatim against the lectures."""
import json, re, sys, html, opencc
sys.stdout.reconfigure(encoding="utf-8")
cc = opencc.OpenCC("t2s"); S = cc.convert
WS = re.compile(r"\s+")
FOLD = str.maketrans({"髙": "高", "恆": "恒", "內": "内", "爲": "為", "纔": "才", "迴": "回"})
fold = lambda t: WS.sub("", t).translate(FOLD)
def lec(n): return open(f"kb/sources/pages/huayan28/28jiang{n}.md", encoding="utf8").read().split("\n---\n", 1)[1]
def Q(n, trad):
    assert fold(trad) in fold(lec(n)), f"quote not in lecture {n}: {trad}"
    return S(trad)

Q1 = Q(19, "雖然大家同在念佛，同在禪堂打坐")
Q2 = Q(23, "有人認為宇宙中的某個地方存在那樣一個極樂世界")
Q3 = Q(23, "『十萬億佛土』是指極樂淨土和娑婆世界在種性上的距離，並不是空間上的距離")
Q4 = Q(23, "是按照空間上的距離來建立，還是按照『種性』上的距離來建立，這就成了大問題，二者完全不同")
Q5 = Q(19, "人天外道、二乘聲聞、權教別教修行者和華嚴行法之間，最少是十萬億佛土，乃至於三十二億恒河沙國土的距離")
Q6 = Q(19, "這個距離不是世間法可以跨越的，需要生起內在覺知模式的行法才能跨越")
Q7 = Q(19, "一旦切實生起這樣的行法，就是進入到華嚴行法的初住位，就是跨越了十萬億佛土")
Q8 = Q(19, "當修行者到達第七住位得無生忍，這個距離就已經不是十萬億佛土所能衡量")
Q9 = Q(19, "如果修行者能到達華嚴行法的十迴向位、十地位，這就是跨越了三十二億恒河沙國土")
Q10 = Q(19, "能夠到達金剛種性，這和二乘聲聞行者、權教別教行者之間的距離即是無量億國土")
Q11 = Q(14, "種性之間的距離需要靠智慧跨越，不是靠苦行可以跨越。")

T = lambda n: f"二十八讲·第{n}讲"
captions = [  # (start, end, narration, quote, source)
 (0, 5,   "<b>距离</b>，该用什么来量？", "", ""),
 (5, 14,  "先看一间禅堂：七个人坐在一起，一起念佛，一起打坐。", Q1, T(19)),
 (14, 23, "经里说：“从是西方过十万亿佛土，有世界名曰极乐。”按字面读，这是一段路——向西，很远很远。", Q2, T(23)),
 (23, 34, "但讲者说：这十万亿佛土，不是公里数。它量的是另一个方向。", Q3, T(23)),
 (34, 46, "同一句经文，种性不同的人，读出三个不同的“目的地”。", Q4, T(23)),
 (46, 60, "于是，坐在同一间禅堂里的人，其实相隔很远。", Q5, T(19)),
 (60, 80, "怎样跨过去？不是走路，也不是熬时间。", Q6 + "　" + Q7, T(19)),
 (80, 90, "距离，要用智慧去量，也要用智慧去跨。", Q11, T(14)),
]
data = {"captions": [dict(t0=a, t1=b, text=c, quote=q, src=s) for a, b, c, q, s in captions],
        "q": {"bracket": Q5, "seventh": Q8, "ten": Q9, "vajra": Q10}}

PAGE = open("scripts/anim_juli_template.html", encoding="utf8").read().replace("/*DATA*/", "const DATA=" + json.dumps(data, ensure_ascii=False) + ";")
open("sample/动画-距离不是公里数.html", "w", encoding="utf8").write(PAGE)
print("ok", len(PAGE) // 1024, "KB")

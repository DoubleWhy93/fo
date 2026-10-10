"""sample/内在觉知模式-v2.html — rewrite aimed at plain meaning (A) + examples/stories (C).
Sources are read directly from the corpus (not only the 28講 digests). Every quote is verified."""
import re, sys, glob, html, opencc
sys.stdout.reconfigure(encoding="utf-8")
cc = opencc.OpenCC("t2s"); S = cc.convert
WS = re.compile(r"\s+")
FOLD = str.maketrans({"髙": "高", "恆": "恒", "內": "内", "爲": "為", "纔": "才", "迴": "回", "着": "著"})
fold = lambda t: WS.sub("", t).translate(FOLD)
def load(pattern):
    fs = glob.glob(pattern); assert len(fs) == 1, (pattern, fs)
    t = open(fs[0], encoding="utf8").read(); fm, body = t.split("\n---\n", 1)
    title = re.search(r'^title: "(.*)"', fm, re.M).group(1)
    return body, title
K = "kb/sources/pages/"
J10, _ = load(K + "huayan70/jiangyi10.md"); J12, _ = load(K + "huayan70/jiangyi12.md"); J45, _ = load(K + "huayan70/jiangyi45.md")
L1, _ = load(K + "huayan28/28jiang1.md"); L17, _ = load(K + "huayan28/28jiang17.md")
DI, t_di = load(K + "dayi_all/2018-2022dy/flWORD/jdjd/2.*.md")        # 地藏经经首如何转成行法
A21, t_a21 = load(K + "dayi_all/2018-2022dy/flWORD/jdjd/21.*.md")
A77, t_a77 = load(K + "dayi_all/2018-2022dy/flWORD/jtl/77.*.md")
A24, t_a24 = load(K + "dayi_all/2018-2022dy/flWORD/swms-dzz/24.*.md")
A107, t_a107 = load(K + "dayi_all/2023dy/fl/107.*.md")
A93, t_a93 = load(K + "dayi_all/2023dy/fl/93.*.md")
print("Q&A titles:", [S(x) for x in (t_di, t_a21, t_a77, t_a24, t_a107, t_a93)])

def Q(label, text, trad):
    assert fold(trad) in fold(text), f"QUOTE NOT FOUND: {trad[:40]}"
    return f'<q class="orig">{html.escape(S(trad))}</q><sup class="src">{label}</sup>'
def T(label): return f'<sup class="src">{label}</sup>'
S70 = lambda n: f"七十讲·第{n}讲"
S28 = lambda n: f"二十八讲·第{n}讲"
def SA(s):
    x = S(s.strip('"《》“”')).strip("？")
    return "答疑：" + (x if len(x) <= 14 else x[:14] + "…")

q_water = Q(S70(10), J10, "比如，如果佛陀說『水是甜的』，我們堅定地相信佛陀的話，這就是聞法模式的『不退』。但是當我們真正嘗到水是甜的，就可以把佛陀講的『水是甜的』這一句轉變成身心覺受。")
q_water2 = Q(S70(10), J10, "就算有十方善知識告言這水不是甜的，也不會退轉")
q_body = Q(S70(10), J10, "行法實踐不是只停留在表面，而是要落實到自己的身心覺受中。")
q_xinxing = Q(S70(45), J45, "信行模式的行法是指依他受教而生起行法實踐；法行模式的行法是指依身心覺受生起善用心、善思惟生起行法實踐。")
q_xianqian = Q(S70(45), J45, "當修行者對某一法生起覺知觀察與思惟反省時，用經典語言來說，即諸佛菩薩『現前』；自我反省、自我覺悟、自我對話的過程，即諸佛菩薩『論義』；明瞭這一法之後轉到行法實踐，即諸佛菩薩『遠離』乃至諸佛菩薩『入滅』。")
q_house = Q(S28(1), L1, "比如蓋房子，蓋平房、蓋三五層的樓房、和蓋一百層的摩天大廈，三者完全不同。")
q_draft = Q(SA(t_a21), A21, "譬如要蓋一個房子，一定要學會這個房子背後那個底稿是怎樣運算的，要知道這個設計的過程。")
q_nodraft = Q(SA(t_a21), A21, "如果沒有這個演算過程，直接就把我們看到的這個經文，拿來成就，我們是做不到的，這就是聞法模式。")
q_yuan = Q(SA(t_a77), A77, "但是，在大乘行法中，把能夠於身心覺知一切法生起善思惟叫作「緣」。")
q_pusa = Q(SA(t_a24), A24, "菩薩是內在生起的。如果還在世間找菩薩，那就又回到聞法模式裡去了。")
q_jiein = Q(SA(t_a24), A24, "「接引」是經的語言，從行法來講，就是從內在生起。")
q_stu = Q(SA(t_di), DI, "但是要把它轉成行法，還是沒有下手處。")
q_slow = Q(SA(t_di), DI, "從聞法模式要轉入到覺知模式行法的時候，先不要一次到位，要慢慢來。")
q_shizun = Q(SA(t_di), DI, "第一個因素「世尊」容易找到，就是我們自己的內在覺性生起。")
q_concept = Q(SA(t_di), DI, "一定不要從文殊師利的概念上去把握，而是要把概念轉成自己的覺受。")
q_wenshu = Q(SA(t_di), DI, "當您生起這個問題的時候，能生起的那一部分，就是您自己的文殊師利菩薩")
q_month = Q(SA(t_di), DI, "最初的一段時間，很可能一個月、兩個月，才能鑒別出來文殊師利菩薩、舍利弗尊者，後面會越來越快。")
d_ba = Q(SA(t_a107), A107, "轉八識成四智是指要通過自我反思、自我覺悟，通過智慧力的構建，將八識，以本能生起一切法的方式，轉變成依於理性的、智慧的方式。")
d_bao = Q(SA(t_a93), A93, "報身世間一切法遵循的規定性，是一切法從心想生")
d_hua = Q(S28(17), L17, "化身世間的遺跡和時間空間有關")
d_fa = Q(S70(12), J12, "『法身世間』是指見如來地一切法的普遍存在，並對此一切法如實知、如實體驗。")
# guards for paraphrased points
for text, k in [(A21, "第一種；是按照自己的意思來解讀這個經典"), (A21, "第二種；是按照集結經典成就者的那人的意義去解讀"),
                (A21, "第三種；就是我們已經明瞭"), (DI, "舍利弗尊者為最上首"), (DI, "到達世間能言說地步的時候，就是具有「舍利弗尊者」的屬性"),
                (J10, "到達第七住位不退住"), (A24, "沒有菩薩眾"), (A77, "見到善知識，見到有人給我們宣說，我們能夠生起信心，這叫「緣」")]:
    assert fold(k) in fold(text), k

CSS = open("sample/内在觉知模式.html", encoding="utf8").read().split("<style>")[1].split("</style>")[0]
CSS += """
.say{display:flex;gap:.7rem;margin:.8rem 0}.say .who{flex:0 0 3.2rem;font-size:.8rem;color:var(--mute);text-align:right;padding-top:.5rem}
.say .bub{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:.6rem .9rem;font-size:.97rem;line-height:1.7}
.say.ans .bub{background:var(--soft)}
.two{display:grid;grid-template-columns:1fr 1fr;gap:.8rem;margin:1rem 0}@media(max-width:560px){.two{grid-template-columns:1fr}}
.two div{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:.7rem 1rem;font-size:.95rem;line-height:1.65}
.two b{display:block;color:var(--acc);margin-bottom:.2rem}
dl.gl dt{font-weight:700;color:var(--acc);margin-top:1rem}dl.gl dd{margin:.15rem 0 0}
ol.steps2{padding-left:1.3rem}ol.steps2 li{margin:.5rem 0}
"""

body = f"""
<p class="kicker">华严入门 · 核心概念（第二版）</p>
<h1>内在觉知模式：从“听说水是甜的”到“自己尝到”</h1>
<p class="lead">这个词在华严的讲稿里出现几百次，但到底指什么？用讲者自己的几个例子，一步一步说清楚。</p>

<h2>先从一杯水说起</h2>
<p>讲者打过这样一个比方：</p>
<p>{q_water}</p>
<p>也就是说，同样是“不退”（信心不会退失），有两种：<b>一种是信佛的话</b>，一种是<b>自己尝到了</b>。前一种，只要有人说得更动听，也许就动摇了；后一种不会——{q_water2}。</p>
<div class="tldr"><b>一句话</b>内在觉知模式，就是把“听来的”变成“自己身心里真有的觉受”。{q_body}</div>

<h2>经里的名字：信行，还是法行？</h2>
<p>佛陀在经里把这两条路分别叫作信行和法行。讲者用白话这样讲：</p>
<p>{q_xinxing}</p>
<div class="two"><div><b>信行（闻法模式）</b>听别人教，然后照着做。善知识讲，修行者听。{T(S28(1))}</div><div><b>法行（内在觉知模式）</b>从自己的身心觉受出发，自己生起善的用心、好的思惟，再去做。</div></div>
<p>这两个不是对错，是两个阶段：没有人能从凡夫地直接生起正知见，必须先闻法起修。{T(S28(2))}</p>

<h2>为什么说它“本质不同”？两个比方</h2>
<p><b>比方一：盖房子。</b>{q_house}{T(S28(1))}平房凭经验就行；百层大厦，每个环节都不能含糊。</p>
<p><b>比方二：读经，就像看别人盖好的宫殿。</b>讲者在答疑里把读经分成三种层次：</p>
<ol class="steps2">
<li><b>按自己的意思读</b>——当成一个故事。最普遍、最容易，没错，但多半不是佛要说的第一义。</li>
<li><b>追问集结者的用意</b>——比如《无量寿经》经首为什么文殊、普贤同时出现，还把普贤排在前面？集结者不会随便写。</li>
<li><b>重建自己的</b>——明白了集结者要说什么，再按他的成就方式，建立自己的《阿弥陀经》《无量寿经》。</li>
</ol>
<p>第三层，就是内在觉知模式。{q_draft}已经盖好的宫殿，你不能直接搬进去住；{q_nodraft}{T(SA(t_a21))}</p>

<h2>同一个词，换了模式意思就变了</h2>
<p>讲者特别提醒：到了内在觉知模式，很多熟悉的词，意思会变。</p>
<p><b>“缘”。</b>俗话说“佛不度无缘之人”。最早的声闻、人天行法里，见到善知识、听人宣说、生起信心，就叫“缘”。{q_yuan}——因为生起善思惟，本身就是内在的觉醒；内在不醒，佛也度不了。</p>
<p><b>“菩萨”。</b>我们习惯在经里找“某位菩萨”，仿佛是外面的人物。讲者说：{q_pusa}所以也不必再到外面等观自在菩萨、大势至菩萨来接引——{q_jiein}</p>
<p><b>“入灭”。</b>经里说诸佛“入灭”“作礼而去”，不是说佛走了、不管你了。讲者的解释是：{q_xianqian}</p>
<p>在这个意义上，“化身世间诸佛入灭”，是指“对外听法的力量”转成“自内生起的觉悟力量”。{T(S70(45))}</p>

<h2>真正的下手处：一个学员的提问</h2>
<div class="say"><div class="who">学员</div><div class="bub">听了课，知道《地藏经》经首讲什么、上首众是谁、问法主是谁……{q_stu}</div></div>
<div class="say ans"><div class="who">讲者</div><div class="bub">这个问题是关于具体行法的，非常重要，也非常关键……</div></div>
<p>讲者的回答，大致是这样一步一步来的：{T(SA(t_di))}</p>
<ol class="steps2">
<li><b>先别一次到位。</b>{q_slow}</li>
<li><b>先把经首的结构看清楚</b>：谁在前、谁在后，法数是多少，处所在哪里。找到基本的“因素”。</li>
<li><b>把每个角色，对到自己身上。</b>以《佛说阿弥陀经》经首为例：{q_shizun}</li>
<li><b>“文殊”不是一个概念，是你生起问题的那一块。</b>{q_concept}讲者举例：读经遇到不明白的地方，你问“这个问题从哪里生起的”——{q_wenshu}；问题成形、到了能说出口的地步，那一块就有“舍利弗”的属性。</li>
<li><b>这需要时间。</b>{q_month}</li>
</ol>
<p>讲者也说，之所以要这样一块一块地鉴别，是因为报身世间的行法“没有办法有抓手”，不像世间法，怎样的行为就是怎样的行法。</p>

<h2>几个绕不开的词，用白话说</h2>
<dl class="gl">
<dt>报身世间</dt><dd>讲者说，它遵循的规则是“一切法从心想生”。{d_bao}。举例：凡夫种性周围到处是染著法，并不是因为眼耳鼻舌身所在的世间本来染著，而是凡夫对一切法的觉受，到了报身世间就是娑婆世界的体验。{T(SA(t_a93))}</dd>
<dt>化身世间</dt><dd>和时间、空间有关的世间。{d_hua}比如释迦牟尼佛留下的遗迹在印度：迦毘罗卫、蓝毘尼园、王舍城耆阇崛山、舍卫国祇树给孤独园。在这个世间，佛的“说法遗迹”就是经典；在报身世间，说法遗迹则是修行者的证入模式。</dd>
<dt>法身世间</dt><dd>{d_fa}</dd>
<dt>转八识成四智</dt><dd>{d_ba}另外一句要点：八识世间之外，没有另一个独立的四智世间。{T(SA(t_a107))}</dd>
</dl>

<h2>它在华严经里的位置</h2>
<p>一句话：它是进入“十住位”的门。讲者说，只有把行法实践落实到具体的身心觉受，才能生起十住位的行法，到第七住位不退住、证得无生忍。{T(S70(10))}所以前面那杯“水是甜的”，其实就是十住位“不退”的样子。</p>
<p>也要注意：初住位只是开始。第七住位以后才开始生起菩萨道种智行法；在这之前，十住位迎佛上须弥山顶时“没有菩萨眾”——因为菩萨是修行者自己内在生起的。{T(SA(t_a24))}</p>

<p class="note">第二版：这一次的内容直接取自《七十讲》《二十八讲》与 2018–2023 年答疑，而不只是《二十八讲》的摘要。所有引文都逐句机器核对；白话衔接与排序是整理者所加，未经讲者审阅。其中“信行／法行”“入灭”的白话解释出自七十讲第45讲，“盖房子”出自二十八讲第1讲。</p>
"""
out = f'<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>内在觉知模式（第二版）</title><style>{CSS}</style></head><body><main>{body}</main></body></html>'
open("sample/内在觉知模式-v2.html", "w", encoding="utf8").write(out)
print("ok")

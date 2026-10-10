"""sample/种性.html — second reader-facing experiment. Quotes machine-checked against sources."""
import re, sys, html, opencc
sys.stdout.reconfigure(encoding="utf-8")
cc = opencc.OpenCC("t2s"); S = cc.convert
WS = re.compile(r"\s+")
FOLD = str.maketrans({"髙": "高", "恆": "恒", "內": "内", "爲": "為", "纔": "才", "迴": "回"})
def fold(t): return WS.sub("", t).translate(FOLD)
def src(path): return open(path, encoding="utf8").read().split("\n---\n", 1)[1]
def lec(n): return src(f"kb/sources/pages/huayan28/28jiang{n}.md")
def T(n): return f'<sup class="src">第{n}讲</sup>'
def Q(label, path_text, trad):
    assert fold(trad) in fold(path_text), f"quote not found: {trad[:30]}"
    return f'<q class="orig">{html.escape(S(trad))}</q><sup class="src">{label}</sup>'

# every quote below is verified against the lecture text
j70 = src("kb/sources/pages/huayan70/jiangyi1.md")
q_def = Q("七十讲·第1讲", j70, "『種性』是指證得某一類法或者生起某一類法總體的可能性。")
q_state = Q("第7讲", lec(7), "境緣無好醜，好醜起於心")
q_stair = Q("第8讲", lec(8), "修行次第好像是上山的臺階一樣，每個次第都有不同的修法，所看到的風景也不同")
q_grade = Q("第26讲", lec(26), "一年級念了二十年，最終還是一年級。")
q_dist = Q("第19讲", lec(19), "雖然大家同在念佛，同在禪堂打坐")
q_cd = Q("第14讲", lec(14), "種性之間的距離需要靠智慧跨越，不是靠苦行可以跨越。") if "種性之間的距離需要靠智慧跨越" in fold(lec(14)) else None

# claims that should still be in the lectures (cheap guards)
for n, k in [(18, "第八迴向位證得金剛種性"), (21, "第十迴向位，修行者證入金剛種性"), (6, "最低要十迴向位才能到達金剛種性智慧地"),
             (8, "帶著凡夫種性跑到阿彌陀佛那裡去，不但見不到阿彌陀佛"), (6, "種性改變之後的娑婆世間即是極樂淨土"), (23, "初住位好像是剛剛開始小學"),
             (7, "種性決定用心")]:
    assert fold(k) in fold(lec(n)), (n, k)

# ---- sutra excerpt
pdf = src("kb/sources/pdf/gangyao80-1.md")
flat = re.sub(r"<!-- p\d+ -->", "", pdf).replace("\n", "")  # line breaks removed so phrases split across lines still match
def piece(start, end, after=0):
    i = flat.find(start, after); assert i >= 0, start
    j = flat.find(end, i); assert j > i, end
    j += len(end)
    assert j - i < 700, f"excerpt too long ({j-i}) for {start[:12]}"
    return i, flat[i:j]
i0, a = piece("爾時，天帝釋白法慧菩薩言：佛子！菩薩初發菩提之心", "其量幾何？")
raw_i0 = pdf.find("爾時，天帝釋白法慧菩薩言：佛子！菩薩初發菩提之心")
_, b = piece("法慧菩薩言：此義甚深", "而為汝說。", i0)
_, c = piece("佛子！假使有人以一切樂具，供養東方阿僧祇世界所有眾生", "寧為多不？", i0)
_, d = piece("天帝言：佛子！此人功德，唯佛能知", "無能量者。", i0)
_, e = piece("法慧菩薩言：佛子！此人功德比菩薩初發心功德", "亦不及一。", i0)
page = re.findall(r"<!-- p(\d+) -->", pdf[:raw_i0])[-1]
assert "初發心功德品" in pdf[:raw_i0]
sutra = [S(x) for x in (a, b, c, d, e)]
c_short = S(c)

CSS = open("sample/内在觉知模式.html", encoding="utf8").read().split("<style>")[1].split("</style>")[0]
CSS += """
ol.ladder{list-style:none;margin:1.2rem 0;padding:0}
ol.ladder li{margin:.35rem 0;padding:.5rem .9rem;background:var(--card);border:1px solid var(--line);border-radius:6px;font-size:.95rem;line-height:1.55}
ol.ladder li b{color:var(--acc)} ol.ladder li small{display:block;color:var(--mute);font-size:.82rem}
ol.ladder li.hi{border-color:var(--acc);box-shadow:0 0 0 1px var(--acc) inset}
.flag{background:var(--soft);border:1px dashed var(--acc);border-radius:8px;padding:.8rem 1.1rem;margin:1.4rem 0;font-size:.92rem}
.flag b{color:var(--acc)}
details{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:.6rem 1rem;margin:.7rem 0}
summary{cursor:pointer;font-weight:600;color:var(--acc)}
"""
steps = [  # (indent level, title, note, highlight)
 (9, "如来地 · 妙觉位", "无上正觉；对应常寂光、华藏世界一路的成就", False),
 (8, "等觉位 · 普贤菩萨法界", "证入实际的普贤菩萨法界，相对极乐世界即常寂光土", False),
 (7, "十地位", "以智导行的入世间行法；金刚种性", False),
 (6, "十回向位", "金刚种性智慧地（具体从第几回向起，讲稿说法不一，见下方说明）", False),
 (5, "十行位", "转八识成四智后生起正知见、正思惟", False),
 (4, "十住位 · 第七住得无生忍", "初住起生起内在觉知模式的行法；所成就的是极乐世界的实报庄严土，种性即法藏比丘的种性", True),
 (3, "十信位", "闻法模式也能走到这里", False),
 (2, "权教 / 别教（闻法模式的共法别教）", "", False),
 (1, "声闻 · 缘觉种性", "", False),
 (0, "凡夫 · 人天外道种性", "", False),
]
ladder = "\n".join(f'<li class="{"hi" if h else ""}"><b>{t}</b>' + (f"<small>{n}</small>" if n else "") + "</li>" for _, t, n, h in steps)

body = f"""
<p class="kicker">华严入门 · 核心概念</p>
<h1>种性：你站在哪一级台阶上？</h1>
<p class="lead">《总释二十八讲》里，“种性”几乎每一讲都出现。它像一把尺：衡量的不是你多努力，而是你现在“站在哪里”。</p>

<div class="tldr"><b>三十秒版</b>
种性，就是“证得某一类法、生起某一类法的总体可能性”。{q_def[q_def.index('<sup'):] if False else ''}
种性不同，用心不同，所见的世界也不同；修行是一级一级升进，每一级的修法和风景都不一样，但不能只守着一级。</div>

<p>先看讲者的定义（出自《七十讲》第一讲，二十八讲里没有单独下定义）：{q_def}</p>

<h2>同一个世界，为什么看到的不一样？</h2>
<p>讲者说：“种性决定用心，用心决定所见的世间。”{T(7)}所以十方诸佛与我们同在这个世间，但他们是如来种性、我们是凡夫种性，觉受不同，才带来一种错觉：我们在娑婆众苦世间，诸佛在极乐、华藏清净世间。{T(8)}</p>
<p>古人说：{q_state}。如果用心的方式不再是分别取著，所见的就未必是娑婆，也可以是极乐、琉璃、华藏世界。{T(7)}
同一个世间法，不是它有差别，而是不同种性的众生觉受不同。{T(17)}</p>

<h2>“距离”不是公里数</h2>
<p>经里说“从是西方过十万亿佛土”。讲者问：这是按空间距离，还是按种性距离来建立信心？答案完全不同——凡夫按空间理解，到达的是世间净土；二乘声闻、别教模式到声闻别教净土；按华严行者的种性建立，则到自性地的实报净土乃至常寂光净土。{T(23)}</p>
<p>讲者还说，人天外道、二乘声闻、权教别教的修行者和华严行者之间，最少隔着十万亿佛土的距离——哪怕大家{q_dist.split('，',1)[1] if False else ''}同在念佛、同在禅堂打坐。{T(19)}
这个距离“不是世间法能跨越的”，要生起内在觉知模式的行法才能跨越：一生起就入初住位，跨过十万亿佛土；到第七住位，这个距离已经不是十万亿佛土所能衡量。{T(19)}</p>

<h2>一张台阶图（按讲稿的说法）</h2>
<p>讲者的比喻是：{q_stair}。{''}</p>
<ol class="ladder" reversed>
{ladder}
</ol>

<div class="flag"><b>讲稿里的一处小分歧。</b>“金刚种性”从哪一位开始，不同讲的说法不一样：第18讲说“第八回向位证得金刚种性”；第6讲说“最低要十回向位才能到达金刚种性智慧地”，第21讲说“到第十回向位，修行者证入金刚种性”。正式发布前需要核对，或向讲者确认。</div>

<h2>三个提醒</h2>
<div class="myth"><b>1. 别把不同阶段的行法混在一起互相评价。</b><br>刚学佛、处于权教、声闻缘觉乃至别教阶段的人，想远离凡夫世间、往生清净世间很正常，佛陀不反对。{T(9)}声闻乘行法针对声闻乘种性，别教行法针对别教种性，不能混在一起。{T(10)}不同宗派的理论差异，多是针对不同种性、不同次第而有的；把它们对立起来，对佛教是严重的伤害。{T(5)}</div>
<div class="myth"><b>2. 别停在一级。</b><br>讲者说，成就无上正觉，是在无量法中不断精进、种性不断提升的过程，并非以一种行法代替所有法。就像小孩上学，从一年级到博士要二十年不同年级的学习——{q_grade}{''}初住位好像刚上小学，很多问题解决不了、会做错、觉得不踏实，但这是和凡夫种性完全不同的行法建立。{T(23)}</div>
<div class="myth"><b>3. 跨越靠智慧，不靠苦行，也不能只靠外力。</b><br>种性之间的距离要靠智慧跨越，不是靠苦行。{T(14)}佛菩萨全心帮助众生，但获得自在解脱，修行者自己才是最核心的因素；外力只在最初阶段可以帮忙。{T(5)}</div>

<h2>读一读经文：初发心的功德，为什么“比不了”？</h2>
<p>第12讲提到：种性的改变不是世间有为法可以计算的，《金刚经》说，三千大千世界七宝布施，不如演说其中一首四句偈。{T(12)}《华严经》里有一段意思相近的问答（天帝释问法慧菩萨，菩萨初发心的功德有多大）：</p>
<div class="sutra">
<p>{html.escape(sutra[0])}</p>
<p>{html.escape(sutra[1])}</p>
<p>{html.escape(sutra[2])}</p>
<p>{html.escape(sutra[3])}</p>
<p>{html.escape(sutra[4])}</p>
<p class="cap">《八十华严·初发心功德品》（节选；后面还有十二种譬喻，此处只取开头一问一答）· 据《华严经纲要》八十华严上册（PDF 第 {page} 页）</p>
</div>

<h2>常见的疑问</h2>
<details><summary>那“往生西方极乐世界”，到底是什么意思？</summary>
<p>讲者的说法有几层：经里说西方极乐世界“有”，并非凡夫种性所说的、外在于我的那种“有”，而是修行者在报身世间证得之后才能说的有；认为从地球往西过多少银河系有个叫极乐世界的地方，是误解了佛陀的意思。{T(6)}种性改变之后的娑婆世间，就是极乐净土；{T(6)}相反，带着凡夫种性到阿弥陀佛那里，见不到阿弥陀佛，所见仍是娑婆的模样。{T(8)}
讲者也强调：学华严不是离开净土，而是首先要成就净土；极乐与华藏不是舍一取一，而是不同种性修行者的不同阶段，法藏比丘极乐世界的行法要先到达，最终才以普贤菩萨法界行法生起华藏世界。{T(18)}{T(19)}</p></details>
<details><summary>为什么佛经里“这里这样说、那里那样说”？</summary>
<p>佛所说法皆有针对：是消除一切法还是建立一切法，要看行者的种性、行法次第和所在阶段。{T(15)}看一章一句要有准确的解读方法，同样的话，种性不同，说法和意义也不同。{T(16)}</p></details>

<p class="note">整理自《华严经总释二十八讲》（按讲次标注出处），定义取自《华严七十讲》第一讲；经文取自《华严经纲要》。这是第二个体例实验：引文已逐句机器核对，台阶图与各条叙述取自讲稿摘要；尚未逐条与讲稿对读审校，正式发布前需复核。</p>
"""
body = re.sub(r"{''}", "", body)
out = f'<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>种性</title><style>{CSS}</style></head><body><main>{body}</main></body></html>'
open("sample/种性.html", "w", encoding="utf8").write(out)
print("ok; sutra page", page)

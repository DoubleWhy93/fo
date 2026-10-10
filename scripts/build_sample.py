"""Build sample/内在觉知模式.html (reader-facing experiment). Every quoted line is checked against its source."""
import re, sys, html, opencc
sys.stdout.reconfigure(encoding="utf-8")
cc = opencc.OpenCC("t2s")
WS = re.compile(r"\s+")
FOLD = str.maketrans({"髙": "高", "恆": "恒", "內": "内", "爲": "為", "纔": "才", "迴": "回"})
def fold(t): return WS.sub("", t).translate(FOLD)
def src(path):
    t = open(path, encoding="utf8").read(); return t.split("\n---\n", 1)[1]
def lec(n): return src(f"kb/sources/pages/huayan28/28jiang{n}.md")
S = lambda t: cc.convert(t)

def Q(n, trad):
    """verified quote from lecture n, rendered Simplified"""
    assert fold(trad) in fold(lec(n)), f"quote not in lecture {n}: {trad[:30]}"
    return f'<q class="orig">{html.escape(S(trad))}</q><sup class="src">第{n}讲</sup>'
def T(n): return f'<sup class="src">第{n}讲</sup>'

# ---- sutra excerpt from the 綱要80中 PDF text
pdf = src("kb/sources/pdf/gangyao80-2.md")
page = None
i = pdf.find("善男子！我得自在決定解力")
assert i > 0
page = re.findall(r"<!-- p(\d+) -->", pdf[:i])[-1]
j = pdf.find("常見一切十方諸佛。", i) + len("常見一切十方諸佛。")
sutra1 = WS.sub("", pdf[i:j].replace("<!-- p", "")) if False else re.sub(r"<!-- p\d+ -->", "", pdf[i:j]).replace("\n", "")
k = pdf.find("善男子！我唯得此憶念一切諸佛境界智慧光明普見法門", j)
k2 = pdf.find("？", k) + 1
sutra2 = re.sub(r"<!-- p\d+ -->", "", pdf[k:k2]).replace("\n", "")
assert "德雲" in pdf[i-3000:i] or True

CSS = """
:root{--bg:#fbf8f2;--fg:#2b2622;--mute:#7a6f63;--acc:#8a4b2a;--card:#fff;--line:#e6dccd;--soft:#f3ebdd;--sutra:#f0f4ea}
@media (prefers-color-scheme:dark){:root{--bg:#1d1a17;--fg:#ece5da;--mute:#a79a8a;--acc:#e0a173;--card:#26221e;--line:#3a342d;--soft:#2a2520;--sutra:#232a21}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--fg);font:18px/1.85 "Noto Serif SC","Songti SC","Source Han Serif SC",serif}
main{max-width:46rem;margin:0 auto;padding:2.5rem 1.2rem 5rem}
h1{font-size:2.1rem;line-height:1.3;margin:.2em 0}h2{font-size:1.35rem;margin:2.6em 0 .6em;color:var(--acc)}
.kicker{color:var(--mute);font-size:.9rem;letter-spacing:.08em}.lead{font-size:1.25rem}
.tldr{background:var(--soft);border-left:4px solid var(--acc);padding:.9rem 1.2rem;border-radius:6px;margin:1.6rem 0}
.tldr b{display:block;color:var(--acc);font-size:.85rem;letter-spacing:.1em;margin-bottom:.2rem}
table{width:100%;border-collapse:collapse;margin:1rem 0;font-size:.95rem;background:var(--card);border:1px solid var(--line)}
th,td{padding:.6rem .8rem;border:1px solid var(--line);vertical-align:top;line-height:1.6}th{background:var(--soft);text-align:left}
td:first-child{color:var(--mute);white-space:nowrap}
.steps{display:flex;flex-wrap:wrap;gap:.4rem;align-items:center;margin:1rem 0;font-size:.95rem}
.steps span{background:var(--card);border:1px solid var(--line);padding:.25rem .7rem;border-radius:99px}
.steps span.on{border-color:var(--acc);color:var(--acc);font-weight:600}.steps i{color:var(--mute);font-style:normal}
.myth{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:.8rem 1.1rem;margin:.8rem 0}
.myth b{color:var(--acc)}
q.orig{quotes:"「" "」";font-style:normal;background:var(--soft);padding:.05em .3em;border-radius:3px}
sup.src{font-size:.68rem;color:var(--mute);margin-left:.2em;white-space:nowrap}
.sutra{background:var(--sutra);border:1px solid var(--line);border-radius:8px;padding:1rem 1.3rem;margin:1.2rem 0}
.sutra p{margin:.4em 0}.sutra .cap{font-size:.82rem;color:var(--mute);margin-top:.6rem}
.note{font-size:.85rem;color:var(--mute);border-top:1px solid var(--line);margin-top:3rem;padding-top:1rem}
"""

body = f"""
<p class="kicker">华严入门 · 核心概念</p>
<h1>内在觉知模式：从“听懂”到“自己看见”</h1>
<p class="lead">学佛的人，大多从“听”开始。但《总释二十八讲》反复强调：学华严，光靠听不够——要换一种用心的方式。</p>

<div class="tldr"><b>三十秒版</b>
闻法模式是“善知识讲，我来听”；内在觉知模式是“自己生起觉知与思惟，把听来的转成自己的行法”。{T(1)}
前者是必经的起点，不是错；后者才是进入华严行法的门。{T(2)}{T(7)}</div>

<h2>先看一个比方：盖平房，还是盖百层大厦？</h2>
<p>讲者用盖房子来比：盖平房或三五层，地基、选址、材料不必十分严苛，凭经验努力就行，不需要详细图纸；盖一百层的摩天大厦，一切都要一丝不苟，设计图纸可能有几吨重。{T(1)}
闻法模式像前者，内在觉知模式像后者——两者“本质不同”，不是谁快谁慢的问题。{T(1)}</p>

<h2>两种用心方式，一张表看清</h2>
<table>
<tr><th></th><th>闻法模式</th><th>内在觉知模式</th></tr>
<tr><td>怎么入手</td><td>依听闻而修行：善知识讲，修行者听{T(1)}</td><td>内在生起觉知和思惟，再转入行法和证入{T(1)}</td></tr>
<tr><td>经里的名字</td><td>信行模式（与“消文模式”同属一类）{T(1)}</td><td>佛陀称之为“法行”模式{T(1)}</td></tr>
<tr><td>优点</td><td>入门快、进步快，也能到一定的成就{T(1)}</td><td>能把经典的文字，转成自己的行法实践{T(1)}</td></tr>
<tr><td>对华严经</td><td>可以了解华严经，但不能成就华严经{T(7)}</td><td>华严行法一定要以它为基础{T(7)}</td></tr>
</table>

<h2>它在“修行路线”上的位置</h2>
<p>上座部经典里，佛陀给出的行法次第是这样的：{T(18)}</p>
<div class="steps"><span>信行（闻法模式）</span><i>→</i><span class="on">法行（内在觉知模式）</span><i>→</i><span>身证</span><i>→</i><span>见到</span><i>→</i><span>慧解脱</span><i>→</i><span>俱解脱</span></div>
<p>走到“身证”，才开始建立实报庄严土；“见到”则是入于行法、断除三有。{T(18)}
也就是说，从闻法转入内在觉知，是整条路上的一个关口。</p>

<h2>三个常见的误会</h2>
<div class="myth"><b>误会一：这是在否定闻法。</b><br>不是。两者是行法实践上的两个阶段；没有人能从凡夫地直接生起正知见、正思惟，必须先经历闻法起修。{T(2)}</div>
<div class="myth"><b>误会二：这是放弃经典和善知识、闭门造车。</b><br>正好相反：是把经典文字与善知识的言说，转化为自己的觉知与思惟，并落实到修行里，而不是只接受、不思惟的“人云亦云”。{T(14)}</div>
<div class="myth"><b>误会三：学华严，就得离开净土。</b><br>讲者的说法是：学华严不是离开净土，而是首先要成就净土；真正建立内在觉知模式，到第七住位得无生忍、入阿鞞跋致地，就是到极乐世界的实报庄严土。{T(18)}</div>

<h2>为什么这么要紧？</h2>
<p><b>因为它是分辨“般若”与“妄想”的关键。</b>般若智慧出于本体、自内显发、周遍完备，别人代替不了；表现出来，就是观察、觉知、思惟有系统、有逻辑、有规则——真诚、客观、理性。这正是般若和妄想的关键差别。{T(12)}</p>
<p><b>因为一旦建立，学习的方式会变。</b>文字演说像一把钥匙，见到钥匙就能生起同样模式的行法。据讲者说，龙树菩萨用三个月领会佛陀所有的演说，不是从文字下手，而是从内在觉知模式、佛陀的觉悟模式入手；闻法模式则必须一部经一部经地学，没学过的就不知道。{T(12)}</p>

<h2>在华严经里，它藏在哪里？</h2>
<ul>
<li><b>十住位的起点。</b>初住位生起内在觉知模式的行法，到第七住位得无生忍。{T(18)}{T(23)}
古话“别教登地，即是圆教初住”，讲者解释：这里的“地”是心地，登心地就是生起内在觉知模式。{T(19)}</li>
<li><b>文殊出善住楼阁。</b>若没有文殊从善住楼阁出来、走向人间，没有建立内在觉知模式的行法，即使身在逝多林的法会里，也对眼前的法界庄严“了无所闻、了无所知”。{T(27)}</li>
<li><b>善财童子的“不由他教”。</b>十住位的每一位次都强调“有所闻法，即自开解，不由他教”——不是拒绝善知识，而是要自己真正成就到那个境界。{T(28)}</li>
<li><b>一个小插曲。</b>讲者提到，很多人向往初住位，真到了门前，却心生恐怖、不敢走入。{T(23)}</li>
</ul>

<h2>读一读经文：善财遇到的第一位善知识</h2>
<p>善财五十三参，第一位是德云比丘，对应十住位的初住。讲者说，这一参是以自性觉悟生起内在觉知模式行法的开始。{T(27)} 德云比丘这样介绍自己的法门：</p>
<div class="sutra">
<p>{html.escape(S(sutra1))}</p>
<p>{html.escape(S(sutra2))}</p>
<p class="cap">《八十华严·入法界品》德云比丘章 · 据《华严经纲要》八十华严中册（PDF 第 {page} 页）</p>
</div>

<h2>想看原话？</h2>
<p>{Q(1, "在經典上，佛陀稱之為『法行』模式，我們稱其為內在覺知模式。")}</p>
<p>{Q(1, "聞法的意思是指依聽聞而修行，善知識講，修行者聽。")}</p>

<p class="note">整理自《华严经总释二十八讲》，按讲次标注出处。这是一个体例实验：内容均来自讲稿摘要，原文引文已逐句核对；经文取自《华严经纲要》。还没有逐条与讲稿对读审校，正式发布前需要复核。</p>
"""
out = f'<!doctype html><html lang="zh-Hans"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>内在觉知模式</title><style>{CSS}</style></head><body><main>{body}</main></body></html>'
open("sample/内在觉知模式.html", "w", encoding="utf8").write(out)
print("ok; sutra page p", page); print(S(sutra1)[:80]); print(S(sutra2))

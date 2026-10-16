# 《华严经》白话读本 — page spec (v2)

One page per 段 (reading segment) of the 80-卷 《大方广佛华严经》. A page lets an ordinary reader **read the sutra
itself and understand what it is really talking about**: every line is put into everyday Chinese, and right next to
it the reader is told, in plain words, what that part is getting at — as the 华严书院 lectures read it, with the
original words one tap away. Plain, warm, accurate. Never thin, never preachy, never inventive.

v2 change (reader feedback): a literal translation alone is not enough — readers could follow *what happens* but not
*what it is about*. Meaning now sits at the top of the page (`gist`) and under every piece of 白话 (`plain[].meaning`).
The detailed reading below becomes "再深一点".

Segments are fixed in `content/huayan/pNN/PLAN.json` (do not edit). Write `content/huayan/pNN/<seg>.json`.
Get your evidence with `python -I scripts/huayan_context.py <seg> <out.md>` and read that bundle in full.

## The layers
1. **经文** — shown by the site from PLAN. You do not copy it.
2. **这一段在讲什么 (`gist`)** — the first thing the reader sees after the title. 3–6 plain sentences saying what this
   passage is really about: what is happening, and what it means as the lectures read it (the big idea, not a list of
   details). Write it so a newcomer finishes it with "oh, so that's what this is about". Attributed lightly ("讲者的
   读法是……" / "按讲稿的说法……") and backed by quotes when it gives a reading. Coverage `none`: say what happens and
   where it sits in the 品, and say plainly that the lectures do not explain it — no symbolism.
3. **白话 (`plain[].t`)** — what the sutra *says*, sentence by sentence, in modern everyday Chinese. Literal meaning:
   translate **every** sentence and every list item in order (141 vows get 141 renderings; group them into readable
   paragraphs, skip none). Keep names and say who is speaking. Verse may become short prose lines. Uncertain wording:
   stay close to the text and mention it in `unsure`.
4. **它在说什么 (`plain[].meaning`)** — directly under each chunk's 白话: 1–4 plain sentences on what this part is
   getting at. Two kinds, marked by `basis`:
   - `"kb"`: the lecturer's reading of these lines (or of this item / this kind of item), attributed, with ≥1 quote.
   - `"story"`: no reading in the KB for this part — explain only its role in the passage ("这里是在交代……", "这一串名字
     是……"), no symbolism, no doctrine, no quote needed; if useful add "讲稿没有逐句解释这一部分".
   Give every chunk a `meaning`. For a long chunk (a list of vows, a run of names) summarise what the run as a whole
   is doing and point out one or two items the lectures do explain.
5. **词语 (`terms`)** — the 2–6 words a newcomer will stumble on.
   - `"kb"`: the KB explains it. The lecturer's own plain explanation, attributed, with ≥1 verbatim quote.
   - `"word"`: an ordinary word or object (袈裟、杨枝、璎珞、伽蓝…) or a standard dictionary meaning of a loanword.
     ≤ 60 chars, **no doctrine, no symbolism**, no quote.
6. **再深一点 (`reading`)** — more of what the KB says about these lines or this 品, every paragraph attributed and
   quoted; use it for points that did not fit in `gist`/`meaning`, not to repeat them. Follow `coverage` from PLAN:
   `quoted` (KB quotes these very lines, bundle §1): 1–4 sections; `pin` (the 品 is discussed, these lines are not):
   0–3 sections, saying plainly that the lectures do not explain these lines one by one; `none`: 0 sections.

Never fill gaps with outside Buddhist knowledge. A lecturer's reading is "讲者的读法", not "经文的意思" — but say it
plainly and confidently where the KB supports it; the reader came to understand, not to read disclaimers.

## Style (the whole point)
- Simplified Chinese, short sentences, one idea per paragraph, explain a word before using it, talk to "你".
- Concrete before abstract: lead with the lecturer's own pictures and examples (the child asking "这是什么", the apple…).
- Warm and clear, a little lively; never flippant about the sutra; no slang, no emoji.
- Test: a reader who skips the 经文 and the "再深一点" part should still understand both what the passage says and what
  it is about.

## JSON
```json
{
  "seg": "p11-s002",
  "title": "plain, curious title (<=30 chars)",
  "hook": "1-2 sentences that make the reader want to read on (<=160)",
  "gist": {"t": "这一段在讲什么: 3-6 plain sentences (<=420)", "quotes": [{"q": "verbatim Traditional", "src": "pages/…"}]},
  "plain": [ {"id": "<chunk id from PLAN, every one, in order>", "t": "白话 of that chunk",
              "meaning": {"basis": "kb|story", "t": "它在说什么 (<=320)", "quotes": [{"q": "...", "src": "..."}]}} ],
  "terms": [ {"term": "<=16", "basis": "kb|word", "plain": "<=260 (word: <=60)", "quotes": [...]} ],
  "reading": {
    "coverage": "quoted|pin|none   (copy from PLAN)",
    "sections": [ {"head": "<=28", "paras": [ {"t": "one idea, plain, attributed (<=320)", "quotes": [...]} ]} ]
  },
  "think": ["2-4 open questions a reader can think about from the passage or their own life？"],
  "unsure": ["0-4 things left open: uncertain wording, lines the KB does not explain, sources that differ (<=150 each)"]
}
```
Limits: each `plain[].t` ≥ 0.6× and ≤ 3× the chunk's length; every chunk has a `meaning`; `gist` needs ≥1 quote unless
coverage is `none`; `terms` 2–6; `reading.sections` 1–4 for quoted, 0–3 for pin, 0 for none; 1–5 `paras` per section;
every `reading` para, every `kb` meaning and every `kb` term has ≥1 quote; quotes ≤150 chars, verbatim from the page
named in `src` (an id in `kb/manifest.json`; sutra lines are quoted from the lecture page that quotes them, not from
CBETA). `think` questions must not assert doctrine.

## Verify
`python -I scripts/verify_huayan.py content/huayan/pNN/<seg>.json` → 0 errors.
Exemplar for voice and depth: `content/huayan/p11/p11-s002.json`.

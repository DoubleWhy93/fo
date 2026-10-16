# 《华严经》白话读本 — page spec

One page per 段 (reading segment) of the 80-卷 《大方广佛华严经》. A page lets an ordinary reader **read the sutra
itself**: every line is put into everyday Chinese, the unusual words are explained, and — where the lectures of
华严书院 actually discuss these lines — the reader sees how the lecturer reads them, with the original words one tap
away. Plain, warm, accurate. Never thin, never preachy, never inventive.

Segments are fixed in `content/huayan/pNN/PLAN.json` (do not edit). Write `content/huayan/pNN/<seg>.json`.
Get your evidence with `python -I scripts/huayan_context.py <seg> <out.md>` and read that bundle in full.

## The four layers (keep them apart)
1. **经文** — shown by the site from PLAN. You do not copy it.
2. **白话 (`plain`)** — what the sutra *says*, sentence by sentence, in modern everyday Chinese. Literal meaning only:
   no 行法 reading, no lecture interpretation, no doctrine. Translate **every** sentence and every list item in order
   (a list of 141 vows gets 141 renderings — group them into readable paragraphs, but skip none). Keep names (文殊师利、
   普贤…) and say who is speaking. Verse may be rendered as short prose lines. When the literal sense of a phrase is
   uncertain, stay close to the wording and mention it in `unsure`.
3. **词语 (`terms`)** — the 2–6 words a newcomer will stumble on.
   - `basis: "kb"`: the knowledge base explains it (concept card / lecture / 总释). Give the lecturer's own plain
     explanation, attributed (讲者说… / 《总释》说…), with ≥1 verbatim quote.
   - `basis: "word"`: an ordinary word or object (袈裟、楊枝、瓔珞、伽藍…). Give its plain everyday meaning in ≤ 60 chars,
     **no doctrine, no symbolism**, no quote needed.
4. **讲稿怎么读 (`reading`)** — only what the KB says about these lines or this 品, every paragraph attributed and
   quoted. Follow the segment's `coverage` from PLAN:
   - `quoted`: some lecture/Q&A/总释 page quotes these very lines (bundle §1). Use those first: what does the lecturer
     say these lines mean? 2–5 sections.
   - `pin`: the 品 is discussed (bundle §2–3) but these lines are not. Give at most 2 short sections with the 品-level
     frame, and say plainly that the lectures do not explain these lines one by one.
   - `none`: no sections. The page is translation + words only, and says so.
   Never fill gaps with outside Buddhist knowledge. A lecturer's reading is "讲者的读法", not "经文的意思".

## Style (the whole point)
- Simplified Chinese, short sentences, one idea per paragraph, explain a word before using it, talk to "你".
- Warm and clear, a little lively; never flippant about the sutra; no slang, no emoji.
- The reader should be able to follow the 白话 without the 经文, and understand the reading without knowing the jargon.

## JSON
```json
{
  "seg": "p11-s002",
  "title": "plain, curious title (<=30 chars)",
  "hook": "2-3 sentences: what happens in this passage and why it matters (<=220)",
  "plain": [ {"id": "<chunk id from PLAN, every one, in order>", "t": "白话 of that chunk"} ],
  "terms": [ {"term": "<=16", "basis": "kb|word", "plain": "<=260 (word: <=60)", "quotes": [{"q": "verbatim Traditional", "src": "pages/…"}]} ],
  "reading": {
    "coverage": "quoted|pin|none   (copy from PLAN)",
    "sections": [ {"head": "<=28", "paras": [ {"t": "one idea, plain, attributed (<=320)", "quotes": [{"q": "...", "src": "..."}]} ]} ]
  },
  "think": ["2-4 open questions a reader can think about from the passage or their own life？"],
  "unsure": ["0-4 things left open: uncertain wording, lines the KB does not explain, sources that differ (<=150 each)"]
}
```
Limits: each `plain[].t` ≥ 0.6× and ≤ 3× the chunk's length (completeness check); `terms` 2–6; `reading.sections`
2–5 for quoted, 0–2 for pin, 0 for none; 1–5 `paras` per section; every `reading` para and every `kb` term has ≥1
quote; quotes ≤150 chars, verbatim from the page named in `src` (an id in `kb/manifest.json`; sutra lines are quoted
from the lecture page that quotes them, not from CBETA). `think` questions must not assert doctrine.

## Verify
`python -I scripts/verify_huayan.py content/huayan/pNN/<seg>.json` → 0 errors.
Exemplar for voice and depth: `content/huayan/p11/p11-s002.json`.

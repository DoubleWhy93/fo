# 阿彌陀經 "easy" pages — authoring spec

Goal: a lighter, friendlier companion to the detailed pages in `content/amtj/`. Same 14 passages (see
`content/amtj/PLAN.json`), but each page is about one screen, in everyday words, a little fun, and ends with things
for the reader to think about. The detailed page `content/amtj/<slug>.json` is your **only content source**: simplify
it, do not add to it. The exemplar to match in voice and shape is `content/amtj-easy/08-mingzhu.json`.

## Hard rules
1. **No new doctrine.** Every idea card must be traceable to the detailed page's text and quotes (or the source
   page it quotes). If the detailed page says "the lecturer reads it as…", keep that attribution ("讲者的读法…").
   Do not turn a lecturer's reading into a universal claim. Do not explain what the KB does not explain.
2. **Plain & short.** Simplified Chinese. Short sentences, everyday words; if a technical term is unavoidable,
   explain it in the same sentence in the lecturer's plain words. Limits (enforced): title <= 30 chars; hook <= 120;
   surface <= 260; each idea `head` <= 16 and `text` <= 120; story `text` <= 280; each `think` <= 60 and ends with
   ？; takeaway <= 48; each `unsure` <= 100.
3. **A little fun, never flippant.** Use vivid comparisons (preferably the lecturer's own: his school/house/石头
   examples), direct address ("你"), and a curious tone. No jokes about the sutra, Buddhas, or the teaching; no
   slang; no emoji in the content (the template adds a few icons).
4. **Each idea card (3–5 of them) carries 1–2 verbatim quotes** (`quotes`, Traditional text copied unchanged from a
   source page, <= 150 chars, `src` an id in `kb/manifest.json`). Prefer quotes already used in the detailed page.
   The builder shows them folded under "看讲者原话", so they must really back the card.
5. **`surface`** is the *plain literal meaning of the sutra passage as written* (the "surface meaning"), in your own
   words; the template labels it as such. It must stay faithful to the sutra text in PLAN (do not import the
   lecturer's 行法 reading here — that goes in the idea cards). Cover the whole passage, in order.
6. **`think`: 2–3 questions** that invite the reader to look at their own experience or weigh the lecturer's point.
   They must not assert doctrine or smuggle in a claim the KB does not make; open, concrete, answerable by looking
   inward or by reading the passage. Draw from the detailed page's `open_questions`, `how_to`-style checks and
   examples. Avoid yes/no questions where possible.
7. **`story`** (optional but wanted): retell one of the lecturer's examples so someone who has not read the page can
   follow it in 2–4 sentences. If the passage has none, omit `story`.
8. **`unsure`** (0–2): the most important open points from the detailed page's `open_questions`, in plain words,
   so the reader knows what the sources leave open. For `partial`/`qa`/`none` coverage pages add the honest one-line
   limit of the KB here (and set `coverage` + `coverage_note` as in the detailed page).

## JSON
```json
{
  "slug": "08-mingzhu",
  "title": "catchy plain title (question or hook, Simplified)",
  "hook": "1-2 short sentences that make you want to read on",
  "surface": "plain literal meaning of the passage",
  "ideas": [ {"head": "short label", "text": "one plain idea", "quotes": [{"q": "verbatim Traditional", "src": "pages/amtj/amtj7"}]} ],
  "story": {"title": "...", "text": "...", "quotes": [{"q": "...", "src": "..."}]},
  "think": ["question？", "question？"],
  "takeaway": "one line to remember",
  "unsure": ["..."],
  "coverage": "lecture",
  "coverage_note": "only when coverage is not lecture"
}
```
`coverage` defaults to the detailed page's value; copy it (and its note, shortened) from `content/amtj/<slug>.json`.

## Verify
`python -I scripts/verify_amtj_easy.py content/amtj-easy/<slug>.json` must say 0 errors. Do not run the site builder
and do not edit scripts, PLAN, other pages, sources or digests.

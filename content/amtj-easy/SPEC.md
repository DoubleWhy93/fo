# 阿彌陀經 "easy" pages (rich format) — authoring spec

Goal: a companion to the detailed pages in `content/amtj/` that is **as full in substance but easier to follow**.
"Easy" means: everyday words, short sentences, terms explained before they're used, one idea per paragraph,
concrete examples, small pauses for the reader to think — **not** less content. A previous attempt cut each page to
~600 characters and was rejected as too thin. The rich exemplar to match in voice, depth and shape is
`content/amtj-easy/08-mingzhu.json` (about 2,300 characters of explanation). Each page must carry at least 80% of the
detailed page's explanation (and no less than 1,600 characters), enforced by the verifier.

Your only content source is the detailed page `content/amtj/<slug>.json` (plus the sources it quotes, if you need
to confirm context). **Re-explain it; do not add doctrine.** Keep every idea the detailed page carries, including its
examples, Q&A, glossary entries and open questions — explain them more plainly and in a better order.

## Hard rules
1. **No new doctrine, no stronger claims.** Anything you explain must be traceable to the detailed page's text and
   quotes. Keep attributions ("讲者说/讲者的读法"). Do not turn a lecturer's reading into a universal claim. Do not
   explain what the KB does not explain; say so under `unsure`.
2. **Plain Simplified Chinese.** Short sentences. Define a technical term the first time (in `terms`, using the
   lecturer's own plain explanation). Prefer concrete pictures and the lecturer's own examples. A little warmth and
   humour is welcome ("先停一下", direct address "你"); never flippant about the sutra, the Buddhas or the teaching;
   no slang; no emoji in the text (the template adds icons).
3. **Step by step.** Order sections so a newcomer can follow: what the passage asks → what the words mean → how the
   lecturer reads it → the apparent puzzle and his answer → what it means for the reader.
4. **Quotes**: `quotes` are verbatim Traditional text copied unchanged from a source page (<= 150 chars, `src` an id in
   `kb/manifest.json`); reuse the quotes in the detailed page. They are shown folded under "看讲者原话". Every
   section needs at least one, every term and misreading needs at least one.
5. **`surface`**: the plain *literal* meaning of the sutra passage as written, in your own words, covering the whole
   passage in order. The template labels it as the compiler's paraphrase. Do not import the lecturer's 行法 reading
   there — that belongs in the sections.
6. **`think` and `pause`** questions are open, concrete and answerable from the reader's own experience or from the
   passage. They must not assert doctrine or smuggle in a claim the KB does not make. Avoid yes/no where possible.

## JSON
```json
{
  "slug": "08-mingzhu",
  "title": "plain, curious title (<=30 chars)",
  "hook": "2-3 sentences that make the reader want to continue (<=260)",
  "surface": "plain literal paraphrase of the whole passage (<=700)",
  "terms": [ {"term": "<=16 chars", "plain": "lecturer's plain explanation, 2-4 sentences (<=300)", "quotes": [{"q": "verbatim Traditional", "src": "pages/amtj/amtj7"}]} ],
  "sections": [
    {
      "head": "<=28 chars",
      "paras": [ {"t": "one idea, plain (<=340 chars)", "quotes": [{"q": "...", "src": "..."}]} ],
      "example": {"title": "<=20", "text": "retell the lecturer's example fully (<=560)", "quotes": [{"q": "...", "src": "..."}]},
      "pause": "a small question to stop and think？"
    }
  ],
  "misreadings": [ {"wrong": "a natural wrong reading (<=90)", "right": "what the lecturer says instead (<=240)", "quotes": [{"q": "...", "src": "..."}]} ],
  "think": ["4-6 open questions？"],
  "takeaway": "one line to remember (<=90)",
  "unsure": ["0-4 points the sources leave open, in plain words (<=150 each)"],
  "coverage": "lecture",
  "coverage_note": "only when coverage is not lecture"
}
```
Limits: `terms` 2–5; `sections` 4–7 with 2–6 `paras` each (`example` and `pause` optional per section; use
several of each across the page); `misreadings` 2–4; `think` 4–6.
Copy `coverage` and a shortened `coverage_note` from the detailed page. On partial/qa pages keep the detailed
page's honesty about which parts are only the lecturer's general frame or the writer's inference.

## Verify
`python -I scripts/verify_amtj_easy.py content/amtj-easy/<slug>.json` must say 0 errors. Do not run the site
builder and do not edit scripts, PLAN, other pages, sources or digests. The old short version of your page is in
git history; overwrite `content/amtj-easy/<slug>.json` completely.

# Canonical concept card — authoring spec (Phase 4)

One card per concept: a single reliable entry that gathers what the lectures and Q&A say about a term, keeps the
different ways it is used apart, and flags where sources differ. It replaces reading dozens of per-page digests.

**Input** (given to you): an *evidence pack* for each term — every definition/explanation the digests recorded for it
(page id, role, definition, plain gloss, verbatim quote), a sample of teachings that mention it, and the list of all
pages it appears on. The pack is derived from the verified digests; each `quote` in it is verbatim from the page
named next to it. You may open `kb/sources/<page id>.md` to confirm context or find a better quote.

**Output**: `kb/consolidated/concepts/<key>.json` (the pack's `key` is the filename stem) with exactly these fields:

```json
{
  "term": "canonical name (Simplified), normally the pack's term",
  "key": "pack key",
  "aliases": ["other names the sources use for the same concept"],
  "summary": "one plain line, <= 80 chars",
  "definition": "2-5 sentences, Simplified: what the lecturer means by it. Only what the sources say.",
  "definition_basis": [ {"q": "verbatim Traditional quote", "src": "pages/…"} ],
  "aspects": [
    {"label": "short label for one distinct way it is used/defined",
     "text": "1-3 sentences", "quotes": [ {"q": "...", "src": "pages/…"} ]}
  ],
  "by_series": [ {"series": "huayan28|huayan70|shixin|swxf|amtj|juewu_s|zongshi|答疑", "text": "how this series treats it (1-2 sentences)"} ],
  "related": ["canonical names of related concepts"],
  "tensions": [ {"text": "where sources differ or seem to conflict, stated neutrally",
                 "sources": [ {"q": "...", "src": "pages/…"} ]} ],
  "gaps": ["what the sources do not explain about it"],
  "where_to_read": ["pages/…  (3-6 best pages for a newcomer, clearest first)"],
  "pages_consulted": 0,
  "confidence": "high | medium | low"
}
```

## Rules
1. **Only what the sources say.** No outside Buddhist knowledge, no doctrine added, no attributions or dates not in the
   evidence. Present readings as the lecturer's ("讲者说…") and keep the lecturer's own terminology.
2. **Every quote is verbatim Traditional text from the page named in `src`** (<= 150 chars, one contiguous stretch).
   Prefer quotes already in the evidence pack. `definition` must be supported by `definition_basis`; every aspect and
   tension needs at least one quote.
3. **Keep distinct senses apart.** If the term is used in clearly different ways (e.g. by stage, by series, literal vs
   密法言说 reading), give each its own `aspects` entry rather than blending them into one definition.
4. **Flag, do not resolve, disagreement.** If two pages define it differently, or the same item is placed at different
   stages, put it in `tensions` with quotes from both sides. State what each side says; do not decide which is right
   and do not add your own explanation of why they differ ("所指不同", "侧重不同" are interpretations — leave them out
   unless a page itself says so).
5. **Aliases are only names the evidence clearly shows are the same concept** (a bracketed gloss, a spelling variant,
   a shorter form used interchangeably). Not a related term, not a sentence-level gloss, not something the sources
   themselves leave open. When in doubt leave `aliases` empty and say so under `gaps`.
6. **Confidence**: high = defined explicitly and consistently on several pages; medium = defined but with variation or on
   few pages; low = mostly "used", or definitions conflict.
7. `by_series` uses these series names only: huayan28, huayan70, shixin, swxf, amtj, juewu_s, zongshi (《觉悟华严经·总释》, written essays: say 作者 or 文中, not 讲者), and **答疑** for all
   Q&A (`dayi` and every `dayi_all/…`; name the year or topic series inside the text when it matters).
   `pages_consulted` is how many pages you actually read or drew on (so readers know the card's depth).
8. `related` names should be terms that appear in the evidence (concepts, or frameworks); do not invent names.
9. **Clarifications.** (a) Quotes may be taken straight from the evidence pack — each is already verified verbatim
   against its page — you do not have to open every page. (b) `pages_consulted` = the number of distinct pages whose
   quotes or definitions you actually used or opened. (c) A claim in `tensions` or `aspects` must be shown by its own
   quote: if a quote does not itself say the thing (e.g. it never names the stage you attribute to it), either find a
   quote that does or leave the claim out. (d) For a paired term ("A与B"), list A and B in `related`.
10. Aim for a card a newcomer can use: `summary`, `definition` and `aspects` first, tension and gaps honest.

## Verify
`python -I scripts/verify_concept_cards.py kb/consolidated/concepts/<key>.json` must report 0 errors (schema, quote
verbatim in its source page, page ids exist, length limits). Do not edit sources, digests, scripts or other cards.

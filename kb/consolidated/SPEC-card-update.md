# Folding 《觉悟华严经·总释》 into existing concept cards

《总释》 is 132 short written essays (series name `zongshi`, pages `pages/zongshi/zsP-NN`). The cards were built before it
was digested. Your job: add what 总释 says to each card **without rewriting what is already there**.

Read `kb/consolidated/SPEC-concept-card.md` first — all its rules still hold (only what the sources say, every quote
verbatim Traditional from the page in `src`, ≤150 chars, flag but do not resolve disagreements, no outside knowledge).

**Input**: `kb/analysis/zpacks/upd-NN.json`, a list of `{card, zongshi_definitions, zongshi_teachings, zongshi_pages}`.
`card` is the filename stem of `kb/consolidated/concepts/<card>.json`. Each `quote` in the pack is verbatim from its
`page`; you may open `kb/sources/<page>.md` for context or a better quote.

**For each card**, edit `kb/consolidated/concepts/<card>.json` in place:
1. **Always** add one `by_series` entry `{"series": "zongshi", "text": "1-2 sentences: how 总释 treats it"}` (say 作者 or
   文中 — these are essays, not talks). If 总释 only mentions it in passing, say that plainly.
2. If 总释 explains a **distinct sense or angle** not already covered by an `aspects` entry, add one aspect with a 总释
   quote. If it only repeats an existing aspect, you may append one 总释 quote to that aspect's `quotes` instead. Keep
   `aspects` at 8 or fewer.
3. If 总释 **clearly differs** from what the card already records (e.g. places it at a different stage, defines it
   differently), add a `tensions` entry quoting both 总释 and the existing side. Rule 9c applies: each side's quote must
   itself show its claim. Do not invent tensions from different wording.
4. You may add 1 总释 page to `where_to_read` if it is one of the clearest explanations (keep ≤ 8 entries).
5. Do **not** change `term`, `key`, `aliases`, `summary` or `definition` unless 总释 shows the existing text is wrong
   about the sources — then say so in your final reply instead of editing it.
6. Add any newly relevant names to `related` only if they appear in the evidence.
7. Leave `pages_consulted` and `related_unresolved` alone (recomputed by a script).

**Verify** each edited card: `python -I scripts/verify_concept_cards.py kb/consolidated/concepts/<card>.json` → 0 errors.
Edit only the cards in your batch.

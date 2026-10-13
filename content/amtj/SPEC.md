# 阿彌陀經 explanation pages — authoring spec

Goal: for each sutra passage in `content/amtj/PLAN.json`, write one page `content/amtj/<slug>.json` that
explains the passage using the knowledge base (the lecturer's own words, verbatim-quoted and traced to a
source page) next to the original sutra text. Output is rendered by `scripts/build_amtj_site.py` and
checked by `scripts/verify_amtj_pages.py`.

## Hard rules
1. **Prose is Simplified Chinese.** Quotes (`q`) are **verbatim Traditional text copied from a source page**
   (<=150 chars, one contiguous stretch; whitespace is ignored when matching). The builder converts them to
   Simplified for display; the verifier matches them against `kb/sources/<src>.md`.
2. **Everything explained must come from the KB.** Do not add doctrine, commentary, or traditional (e.g. 净土宗
   祖师) interpretation the sources do not contain. Present the lecturer's reading as the lecturer's
   ("讲者说…"), not as universal fact. Where sources differ or are ambiguous, say so.
3. **Every explanatory paragraph (`p` with more than 40 chars of own prose) must contain at least one quote
   segment**, so each claim is anchored. Short connective sentences are fine without.
4. Use the lecturer's own terminology (种性, 觉知模式, 报身世间, 一切法, 行法 …). Keep 密法言说 / 行法 /
   种性 readings distinct from literal readings, following how the lectures frame them.
5. Be understandable to a newcomer: explain each non-obvious term in plain words **using the lecturer's own
   plain explanations** (digests' `concepts[].plain`, `examples`, `how_to`). Prefer his examples/stories,
   retold so a reader can follow without the source.
6. Synthesise across lectures/Q&A for the passage and cite each piece; do not paste whole paragraphs. Never invent
   a source id: every `src` must be an `id` in `kb/manifest.json`
   (e.g. `pages/amtj/amtj7`, `pages/dayi_all/2018-2022dy/flWORD/jtl/100.rhj-fsamtj-lsdxf-`).

## Page JSON
```json
{
  "slug": "05-qibaochi",
  "title": "七宝池、八功德水",
  "kicker": "阿弥陀经 · 第5段",
  "lead": [ {"t": "1-2 sentences"}, {"q": "verbatim Traditional", "src": "pages/amtj/amtj6"} ],
  "tldr": "one plain sentence: what this passage is about, as the lectures read it",
  "coverage": "lecture",
  "coverage_note": "required unless coverage is lecture: say what the KB does not explain (Simplified)",
  "blocks": [
    {"h2": "heading"},
    {"p": [ {"t": "text"}, {"q": "verbatim Traditional", "src": "pages/amtj/amtj6"}, {"t": "text"} ]},
    {"example": {"title": "short title", "p": [ {"t": "..."}, {"q": "verbatim Traditional", "src": "pages/amtj/amtj6"} ]}},
    {"qa": {"q": "a question a learner asked (Simplified)", "a": [ {"t": "..."} ]}},
    {"dl": [ {"dt": "term", "dd": [ {"t": "..."} ]} ]}
  ],
  "terms": ["concept card names used"],
  "open_questions": ["points the KB leaves unclear or lecturers treat differently (Simplified)"]
}
```
`coverage` is one of `lecture | partial | qa | none` (how well the KB explains this passage).
A segment is `{"t": text}` or `{"q": verbatim_traditional, "src": source_id}`.
Do **not** include the sutra text in the page JSON; the builder inserts the passage's original text from PLAN.
Each block has exactly one of `h2`, `p`, `example`, `qa`, `dl`. Aim for a page a newcomer can read in 5–10 minutes:
a lead, 3–6 `h2` sections, at least 6 distinct quotes for a lecture-covered passage.

## Where to look (in this order)
1. `kb/digests/pages/amtj/amtjN.json` for the lectures named in PLAN, then the full
   `kb/sources/pages/amtj/amtjN.md` to read the lecturer's own wording around the sutra passage.
2. Other series for the same terms (`kb/digests/pages/huayan28|huayan70|shixin/…`, sources under
   `kb/sources/pages/…`): search with Grep for the passage's key terms.
3. Q&A under `kb/sources/pages/dayi_all/**` and `kb/sources/pages/dayi/**` (grep for the sutra phrases, e.g.
   「阿彌陀」「極樂」「執持名號」「一心不亂」) and concept cards `kb/concepts/*.md` (index: `kb/concepts/INDEX.md`).
4. For passages whose PLAN `expected_coverage` is partial/qa: lectures 1–8 do not (fully) cover it, so build the page
   from Q&A and other series, set `coverage` honestly and fill `coverage_note`. If the KB has nothing, say so;
   do not fill the gap with outside knowledge.

## Verify before finishing
`python -I scripts/verify_amtj_pages.py content/amtj/<slug>.json` must report 0 errors (quotes found in their
source, long paragraphs anchored, sources exist, fields valid). Then run `python -I scripts/build_amtj_site.py`
to confirm it renders to `site/amtj/` (do not edit that script).

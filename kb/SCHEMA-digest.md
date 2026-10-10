# Digest schema (Phase 3)

One JSON file per source page: `kb/digests/<same path as the source, .json>`
(e.g. `kb/sources/pages/huayan28/28jiang5.md` → `kb/digests/pages/huayan28/28jiang5.json`).

## Language rules
- All prose fields are written in **Simplified Chinese**.
- All `quote` fields are **verbatim copies from the source page, unchanged (Traditional characters, same punctuation)**, ≤ 120 characters; it may run across adjacent lines/paragraphs (whitespace is ignored when matching) but must be one contiguous stretch. A script checks that each quote occurs in the source; a quote that does not match is an error.
- Use the source's own terminology exactly (种性, 觉知模式, 报身世间, 灭尽定 …). These lectures use a specific vocabulary; do not replace it with textbook Buddhist terms, and do not add doctrine, explanation or interpretation that the page does not contain. If something is unclear, say so in `notes`.

## Fields
```json
{
  "id": "pages/huayan28/28jiang5",          // = manifest id
  "title": "第五讲",
  "gist": "one sentence: what this page is about",
  "summary": "3-6 sentences, faithful, in the order the page argues",
  "outline": [                              // the page's own structure, in order
    {"heading": "…", "points": ["…", "…"]}
  ],
  "concepts": [                             // terms the page defines or leans on
    {"term": "种性",
     "role": "defined | explained | used",  // defined = an explicit definition sentence; explained = clarified in passing/by example without a formal definition; used = assumed known
     "definition": "as THIS page says it (Simplified). empty if role=used",
     "quote": "verbatim source text supporting it (empty if none)"}
  ],
  "teachings": [                            // distinct claims / instructions, one per item, no duplicates within the page
    {"claim": "…",
     "kind": "definition | method | criterion | structure | warning | history | chronology | other",  // history = narrative; chronology = dates/lineages/counts/attributions
     "from": "lecturer | cited_text",       // cited_text = the claim comes from a sutra/commentary/historical text the lecturer quotes, not the lecturer's own statement (optional; default lecturer)
     "quote": "verbatim"}
  ],
  "frameworks": [                           // recurring structures the page invokes (三处十会, 四十位, 五十三参, 五种解脱 …)
    {"name": "…", "treatment": "full | brief | assumed",   // full = explained in detail here
     "items": ["its members/steps/levels as listed on this page, in order (only if treatment is full or brief and the page lists them)"]}
  ],
  "sutra_refs": [                           // every reference to the sutra
    {"ref": "世主妙严品 / 十地品 / 普光明殿 / 第六会 …(as written, Simplified)",
     "kind": "pin | hui | wei | shanzhishi | quote | other",   // 品 / 会 / 位 / 善知识 / quoted lines
     "quote": "verbatim source text containing the reference or the quoted sutra lines"}
  ],
  "vivid": [                               // analogies, stories, examples, memorable phrasings worth reusing on a reader-friendly site
    {"kind": "analogy | story | example | phrase", "text": "short retelling (Simplified)", "quote": "verbatim"}
  ],
  "qa": [                                  // only for Q&A pages: each 问/答 pair
    {"question": "…", "answer_summary": "…", "topic": "…", "quote": "verbatim from the answer"}
  ],
  "people": [                              // persons/figures named (optional but please fill)
    {"name": "…(Simplified, as written)", "note": "who, as the page presents them; if two different people share a name (e.g. two 慧远), give distinguishing detail"}
  ],
  "errata": [                              // apparent typos/garbling/inconsistencies in the SOURCE (quotes stay verbatim)
    {"source_text": "…verbatim", "likely": "…", "why": "…"}
  ],
  "repetition": "where the page repeats itself, restates a framework, or has filler (greetings, transitions); say what could be cut without losing meaning",
  "notes": "uncertainties, apparent errors/typos in the source, anything a reviewer should look at"
}
```

## Schema v2 (applied after the 二十八講 pilot; applies to later shards, old digests stay valid)
- `from` missing means `lecturer`; only set it when `cited_text`. Add `cited_source` (e.g. "无量寿经", "瑜伽师地论") on `cited_text` items when known.
- teachings `kind` also allows `cross_reference` (X corresponds to Y; conflicts between source texts) and `fashu` (number/法数 tables and lists).
- `sutra_refs.kind` also allows `lun` (论/注疏 and other non-sutra citations) and `own_text` (lecture-internal places such as 菩提场/普光明殿/入法界).
- `frameworks.treatment` also allows `partial` (page applies or hints at it without listing the full structure).
- `errata`: real source mistakes only (wrong characters, garbled passages, inconsistent names). Do NOT list character variants such as 髙/高, 恒/恆, 内/內 — these are normalized site-wide, and the verifier folds them when matching quotes.
- `people`: if the page uses one name for different figures, or it is unclear whether two mentions are the same person, say so in `note`.
- Granularity: the pilot averaged ~72 teachings per 12,000-character lecture. That is acceptable; keep each teaching a self-contained point (with its reasoning), do not split into one-clause fragments.

## Schema v3 (added before the 七十講 run) — capture what makes it understandable
Readers told us the first pages were "vague, doesn't explain". The author's explanations live in his **examples, stories, exchanges and step-by-step guidance**, and in his **plain definitions**. Capture them fully.
New fields (add to the JSON; keep `vivid` for short memorable phrases only):
```json
  "examples": [                // EVERY concrete illustration the author gives: analogies, stories, cases, exercises, dialogues
    {"kind": "analogy | story | case | exercise | dialogue",
     "illustrates": "which concept/teaching it explains (Simplified)",
     "setup": "the situation, retold so someone who has not read the page can follow (Simplified, 1-3 sentences)",
     "point": "what the author draws from it (Simplified, 1-2 sentences)",
     "quote": "verbatim, the key sentence(s) of the example (<=120 chars)"}
  ],
  "how_to": [                  // any practical/step-by-step guidance ("how do I do/recognise this")
    {"situation": "what the reader is trying to do / what question is answered",
     "steps": ["…", "…"],
     "quote": "verbatim"}
  ],
  "prerequisites": ["terms/ideas a newcomer must already know to follow this page"]
```
and in each `concepts[]` item add `"plain": "the author's own plain-language explanation of the term if he gives one (1-2 sentences, Simplified; empty if he does not)"`.
Rules: do not invent examples; if the page has none, `examples` is `[]`. An example is only an example if the author uses it to explain something. Do not shrink an example into a bare label — keep enough setup and point that a reader could re-tell it. The verifier checks `examples[].quote` and `how_to[].quote` like the others.

## Optional fields
`from` on quotes, `items` on frameworks, `people` and `errata` are new (added after the first pilot shard); older digests may lack them. The verifier does not require them.

## Rules of thumb
- Completeness over brevity for `teachings` and `concepts`: every distinct point of the page should be traceable to an entry. `summary` is the only place to compress.
- Do not merge across pages; each digest stands alone. Cross-page merging is Phase 4.
- Tables in the source appear as ` | `-separated rows; keep them in mind for `frameworks` and `outline`.

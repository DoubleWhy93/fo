# 華嚴 site rebuild — Knowledge Base Plan

Source: `D:\repos\hyjing-main\hyjing` (static HTML, Traditional Chinese). Target: `D:\repos\hyj-new`.

## 1. What the source actually is (measured)

~4.3M Chinese characters of body text across 974 HTML pages (plus 9 PDFs in `doc/`, which hold the 綱要 and 總釋 and may include sutra text).

| Group | Files | Chars | Nature |
|---|---|---|---|
| huayan70 華嚴七十講 | 72 | 789K | lecture series, walks the sutra by 品 |
| huayan28 總釋二十八講 | 29 | 354K | overview lectures (intro/theory) |
| swxf 十住/十行… 行法 | 37 | 578K | practice-stage lectures |
| shixin 十信 | 17 | 248K | 十信位 lectures |
| juewu_s 覺悟華嚴 | 9 | 491K | long essays, 綱要, 講記 |
| amtj, dayi | 36 | 129K | misc. lectures / FAQ |
| dayi_all 答疑 (Q&A, 2018–2024 + 專題) | ~700 | ~1.9M | the bulk; heavy overlap expected |

Expected redundancy: Q&A repeats across years and categories; lecture series re-explain the same frameworks (三處十會, 四十位, 五十三參, 種性/覺知 模式) in every session; nav/boilerplate on every page.

## 2. Principle

Nothing is "summarised away" without a trace. Every KB entry points to its source pages; every source page is accounted for (mapped to entries, or marked redundant with the page that supersedes it). That is what makes "no loss of meaning" checkable.

## 3. KB shape (what we are building toward)

```
kb/
  sources/        one normalized file per source page: clean text + metadata
  digests/        one structured JSON per source page (LLM output, see Phase 3)
  concepts/       one card per concept/term (三處十會, 種性, 滅盡定, 覺知模式…)
  qa/             deduped Q&A, clustered by topic, canonical answer + variants
  structure/      sutra skeleton: 3處10會, 39品, 40位, 53參 → ids
  sutra/          original 華嚴經 text split by 卷/品, with stable passage ids
  links.json      concept ⇄ passage ⇄ source-page ⇄ Q&A graph
  coverage.md     report: every source page → where its content went
```
Plain Markdown+frontmatter and JSON in git: diffable, reviewable, and later compiled to whatever the site stack needs (search index, pages).

## 4. Phases

**Phase 0 — Decisions (before any code):** see open questions below.

**Phase 1 — Extract & normalize (scripted, no LLM).**
Python script: HTML → clean text, strip nav/footer/scripts, keep headings, preserve 經文 quotes vs. commentary (check how the source marks them), capture title, series, lecture number, 相關品/關鍵字 header fields, date if any. Output `kb/sources/*.md` + `manifest.json` (id, path, series, order, char count, hash). Also extract the PDFs (`doc/*.pdf`) the same way.

**Phase 2 — Redundancy map (scripted).**
Exact-hash and near-duplicate detection (char-shingle / MinHash) at page and paragraph level; boilerplate paragraphs that repeat across many pages; Q&A question clustering. Output: duplicate clusters with a proposed "canonical" page each. This tells us the real volume of unique content before spending LLM effort (my guess: 40–60% of the Q&A shrinks).

**Phase 3 — Per-page digestion (LLM, sharded, parallel).**
~4.3M chars ≈ too much for one pass, so shard by series (~120 shards of ~35K chars), one subagent per shard, strict JSON schema per page:
- one-line gist + 3–5 line summary
- concepts introduced/used (with the page's own definition)
- claims / teachings, each tagged *new* vs *restated* (against concept cards so far)
- 經文 references (品 / 會 / 位 / quoted lines) — the hook for sutra integration
- Q&A pairs normalized (question, answer, topic)
- memorable passages worth quoting verbatim (the "fun" material: analogies, stories, 比喻)
- redundancy notes
Pilot first on one series (suggest `huayan28`, 354K, the foundational one) to lock the schema and measure cost/quality, then run the rest.

**Phase 4 — Consolidation.**
Merge digests into concept cards (one canonical definition + all variants + source pointers), a topic taxonomy, deduped Q&A, and series-level outlines (what each series covers, in what order, and what is unique to it). Flag contradictions or terminology drift between series rather than silently choosing.

**Phase 5 — Sutra integration.**
Ingest the original 華嚴經 (public-domain text; candidates: 80卷 實叉難陀 T10n0279, 60卷 佛馱跋陀羅 T09n0278 via CBETA — check reuse terms, also cross-check against the site's own PDFs). Split into 卷/品/passage ids, build `structure/` skeleton, then link: for each concept and teaching, find the sutra passage it rests on (the lectures cite loosely, so this is semi-automatic: reference extraction → candidate passages → review). Output: each concept card gets "原文" excerpts; sutra browsable with commentary pointing back.

**Phase 6 — Verification.**
- Coverage: script asserts every source page appears in `coverage.md` (mapped / superseded-by-X / boilerplate).
- Fidelity: sample ~5% of digests and concept cards, blind-compare to source, record error rate; re-run shards that fail.
- Link integrity: every passage id / source id resolves.

**Phase 7 (later, separate plan) — Site design** on top of the KB: reading paths by stage, concept pages with sutra excerpts, Q&A by topic, short "story/analogy" cards. Deliberately deferred so the KB shapes it, not the old site's structure.

## 5. Order of work / checkpoints

1. Phase 1+2 → I report real unique-content numbers and the duplicate map. **Checkpoint.**
2. Phase 3 pilot on `huayan28` → review digest quality together; adjust schema. **Checkpoint.**
3. Phase 3 full run → Phase 4 → Phase 5 → Phase 6.

## 6. Open questions

1. **Script:** KB and new site in Traditional (matches source and 經文) or Simplified? (Can store Traditional and convert at build time.)
2. **Sutra version:** 80卷 (the one the lectures mostly quote?) as primary, 60卷 for comparison? Or whatever the site's 綱要 PDFs use?
3. **Location:** OK to put `kb/` and scripts in `D:\repos\hyj-new`? (`D:\repos\fo` currently holds your 十行位之十七 audio/docx and `work/`; I'll leave those alone.)
4. **Cost appetite:** Phase 3 is the expensive step (many parallel agents). Fine to run it after the pilot, or want to approve a budget first?

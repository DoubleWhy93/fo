---
name: huayan-explain
description: Write easy-to-read 白话 pages for 《大方广佛华严经》 (80卷) — a plain modern-Chinese translation of every line, the hard words explained, and how the 华严书院 lectures read the passage, all grounded in this repo's knowledge base with verified quotes. Use when asked to translate, explain, or "do" a 品/段 of 华严经, to continue the 华严经 白话读本, or to check its progress.
---

# 华严经 白话读本

The site has a 华严经 section (`site/huayan/`) built from `content/huayan/`. The sutra is split into 39 品 and
1,020 段 (`content/huayan/pNN/PLAN.json`). Each 段 gets one page: 这一段在讲什么 → 经文 / 白话 / 它在说什么 → 词语 →
再深一点 → 想一想.
The full rules are in `content/huayan/SPEC.md`; the voice and depth to match are in the exemplar
`content/huayan/p11/p11-s002.json`. Read both before writing anything.

## What "easy" means here
- The reader can follow the 白话 without the 经文, and the reading without knowing the jargon.
- Every sentence of the sutra is translated, in order; nothing is skipped or summarised away.
- Short sentences, everyday words, one idea per paragraph, talk to "你". Warm, clear, never flippant.
- **Easy never means invented.** The 白话 is literal meaning only. Interpretation comes only from the knowledge base,
  attributed (讲者说 / 《总释》说 / 答疑中) and backed by a verbatim quote. Where the KB is silent, say so.

## Workflow (one 段)
1. Pick the 段: given by the user, or `python -I scripts/huayan_todo.py <pin> <n>` for the next undone ones
   (`python -I scripts/huayan_todo.py` alone shows progress per 品).
2. Gather the evidence: `python -I scripts/huayan_context.py <seg> <scratch>/ctx-<seg>.md` and read the bundle in full.
   §1 = pages that quote these exact lines (strongest), §2 = 《总释》 essays on the 品, §3 = other pages naming the 品,
   §4 = concept cards for words in the text. Open `kb/sources/<page>.md` or the card JSON when you need more context
   or a better quote. Read files as UTF-8 (the Windows console garbles Chinese: write to a file and open it).
3. Write `content/huayan/pNN/<seg>.json` per the SPEC (v2). Readers must come away knowing what the passage is
   **about**, not only what it says. So:
   `gist` (这一段在讲什么 — the big idea in plain words, top of page) · `plain[].t` (literal 白话 of every line) ·
   `plain[].meaning` (它在说什么 — under every chunk; `kb` = the lecturer's reading + quote, `story` = its role in the
   passage when the KB is silent) · `terms` (kb + quote / word = everyday meaning) · `reading` (再深一点 — extra depth
   only: quoted 1–4 sections / pin 0–3 / none 0) · `think` · `unsure`.
4. Verify: `python -I scripts/verify_huayan.py content/huayan/pNN/<seg>.json` → 0 errors. Fix and re-run.
5. When a batch is done: `python -I scripts/build_site.py` rebuilds the site (progress badges update automatically).

## Doing many 段
Use the `huayan-explainer` agent (`.claude/agents/huayan-explainer.md`), one 品 or ~6–10 consecutive 段 per agent,
so neighbouring 段 are written by the same hand. Give each agent its 段 ids and a private scratch directory. After all
agents finish: run the verifier over everything, rebuild the site, spot-read a few pages against the SPEC, commit.
Suggested order: 品 the lectures cover closely first (7 如来名号, 8 四圣谛, 11 净行, 12 贤首, 15 十住, 21 十行 …),
then 39 入法界 (most quoted), then the rest.

## Rebuilding the inputs (only if the sources change)
- Sutra: `python -I scripts/extract_huayan.py <T10n0279.xml>` (CBETA, see the script header) → `kb/sutra/huayan80/`.
- KB ↔ sutra map: `python -I scripts/huayan_coverage.py` → `kb/sutra/huayan80/coverage.json`.
- Segments: `python -I scripts/huayan_plan.py` → `content/huayan/pNN/PLAN.json`. Re-planning changes 段 ids, so never
  re-plan a 品 that already has pages.

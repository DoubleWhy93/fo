# Claim audit — instructions for auditors

You are an independent auditor. A "card" in this knowledge base states claims about what a lecturer teaches, each
backed by verbatim quotes. The authors worked quickly and may have over-read, mis-attributed or over-generalised a
quote. Your job is to judge, **for each item, whether the claim is actually shown by the passage(s) given**, as
a sceptical reader who has only the source text.

Each item has: `claim` (Simplified Chinese, what the card says), `quotes` (verbatim Traditional quote + `context`:
about 500 characters either side, with the quote marked 【…】), `kind` (definition | aspect:<label> | tension |
members), and the `card` it comes from. You may open the whole page (`kb/sources/<src>.md`, use Python) if the
context is not enough. Judge from the sources only — never from outside Buddhist knowledge, and never because the
claim "sounds right".

## Verdicts
- `supported`: the claim's content is stated, or directly follows, in the quoted passage / its context.
- `partly`: the core is there but the claim adds something not in the passage (an extra stage, a generalisation to
  all lectures, a stronger word) — say exactly what is not supported.
- `unsupported`: nothing in the passage or its context shows the claim.
- `misattributed`: the passage says something like it but about another thing, said by the questioner/another
  speaker rather than the lecturer, or about another stage/term.
- `cannot_tell`: the context is genuinely insufficient (say what would be needed).

Tension claims ("page A says X, page B says Y"): `supported` only if each side's quote actually shows its half; if
one side is not shown, `partly`; if the passages do not conflict at all, say so (`unsupported`).
Claims of the form "series S treats it as …" are `supported` only if the quote is from series S.

## Output
`kb/consolidated/audit/<batch name>.json` — a JSON list with exactly one object per input item, same `id`:
```json
{"id": "L001", "verdict": "partly", "reason": "<=200 chars Simplified: what is / is not shown",
 "suggested_text": "a corrected claim that the passage does support (Simplified) — required for partly/unsupported/misattributed, else empty",
 "evidence": [ {"q": "verbatim Traditional quote from the page that supports your suggested text", "src": "pages/…"} ]}
```
`evidence` is optional (only if you found a better quote than the card's). Quotes must be verbatim (<= 150 chars).
Be concise and consistent; do not rewrite cards, do not edit anything else.

## Verify
`python -I scripts/verify_audit.py kb/consolidated/audit/<batch name>.json`

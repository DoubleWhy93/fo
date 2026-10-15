# Canonical framework card — authoring spec (Phase 4)

A *framework* is a recurring structure the lecturer invokes by name (四十位行法, 三处演说, 普光明殿四个行法阶段 …).
Each page's digest recorded only the part of it that page mentions, so the same framework appears with many partial
or differently worded member lists. Your job: one card per framework that gathers them, says what the full structure
is as far as the sources show, and flags where lists disagree.

**Input**: a pack per framework: its name and variants, and for every page that mentions it the `treatment`
(full | brief | partial | assumed) and the `items` that page lists (digest wording, Simplified).

**Output**: `kb/consolidated/frameworks/<key>.json` (file stem = pack `key`):
```json
{
  "name": "canonical name", "key": "pack key", "aliases": ["same framework under another name (clear cases only)"],
  "summary": "one plain line <= 80 chars",
  "members": [ {"name": "member", "note": "what the pages say it is, <= 60 chars, or empty"} ],
  "order_note": "how the members are ordered and on what basis (or 'sources give no fixed order')",
  "completeness": "full | partial | fragmentary",
  "views": [ {"label": "a distinct way pages list/use it", "members": ["..."], "pages": ["pages/..."]} ],
  "tensions": [ {"text": "where lists differ in members, count or order — state what each side says",
                 "sources": [ {"q": "verbatim Traditional quote", "src": "pages/..."} ]} ],
  "gaps": ["what the sources never spell out"],
  "source_quotes": [ {"q": "verbatim Traditional quote where the lecturer lists or explains it", "src": "pages/..."} ],
  "related": ["names of related frameworks/concepts that appear in the evidence"],
  "where_to_read": ["pages/... (<= 6 best pages, clearest first)"],
  "confidence": "high | medium | low"
}
```
## Rules
1. Members come **only** from the pack's `items` (or from pages you open). Do not complete a list from outside
   knowledge, even if you know the traditional enumeration. If the sources list only 4 of 10 members, `members` has 4,
   `completeness` is "partial" and the rest goes under `gaps`.
2. Merge members that are the same item written differently (e.g. 初住 / 初发心住) only where the pack makes it clear;
   otherwise keep both and mention it in `tensions` or `gaps`.
3. A list that differs in count, membership or order from the others is a `tension` (state each side) — never silently
   pick one. Quotes in `tensions` and `source_quotes` must be verbatim from the page in `src` (<= 150 chars); open
   `kb/sources/<page id>.md` (Python for odd paths) to find them. At least one `source_quotes` entry is required.
4. `views` groups pages that list it the same way; keep to <= 6 views.
5. No doctrine beyond the pages. `tensions` may be empty.
6. Use exact page ids from the pack (they may end in spaces).

## Verify
`python -I scripts/verify_framework_cards.py kb/consolidated/frameworks/<key>.json` must report 0 errors.

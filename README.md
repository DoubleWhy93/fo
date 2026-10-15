# 華嚴 knowledge base (personal study project)

A structured, source-traced knowledge base built from publicly available Huayan (華嚴) lecture and Q&A material, for personal study and for experimenting with how to organize it. It also contains explanation pages for the 《佛說阿彌陀經》 assembled from that material.

## Source and attribution

All teaching content in this repository is derived from material published on a public website:

- **Original site:** [華嚴書院 (Huayan Academy)](https://huayan.academy/) — tagline 「認識生命，覺悟華嚴」
- **Speaker / authors:** the site does not name its lecturer or operator, and I have not added a name it does not give. The lectures and Q&A are the work of the academy's teacher(s) and its community of practitioners.
- **Terms of use:** the site's home page states no copyright notice or reproduction terms.

I do not claim authorship of any of the teaching content. Copyright and credit belong to the original authors and publishers. Please visit the original site for the authoritative versions.

If you are the rights holder and would like content removed or changed, please open an issue and I will act on it promptly.

The sutra text of 《佛說阿彌陀經》 (鳩摩羅什 translation) in `kb/sutra/` comes from [CBETA](https://www.cbeta.org/) (T12n0366, Taishō Tripiṭaka), a public-domain text.

## What is here

| Path | Contents |
|---|---|
| `PLAN-knowledge-base.md` | Project plan and design notes |
| `kb/sources/` | Normalized text of every source page, with metadata |
| `kb/digests/` | One structured digest per source page: summary, concepts, teachings, frameworks, Q&A, each backed by a verbatim quote (see `kb/SCHEMA-digest.md`) |
| `kb/concepts/` | Concept cards (prototype, built from the first series; being rebuilt from all digests) |
| `kb/analysis/` | Redundancy map, consolidation dry-run, core-term list, and a ledger of which pages were skipped and why |
| `kb/sutra/` | The 《佛說阿彌陀經》 text (CBETA) |
| `content/amtj/` | 《阿彌陀經》 explanation pages (detailed), as verified JSON, plus plan and authoring spec |
| `content/amtj-easy/` | The same passages, written step by step in plain language |
| `site/amtj/`, `site/amtj-easy/` | Rendered HTML of the two explanation sets (open `index.html`) |
| `sample/` | Earlier sample pages |
| `scripts/` | Python scripts for extraction, deduplication analysis, verification and page generation (original work) |

## Status

Work in progress.

- **Per-page digestion: done.** 633 of 971 content pages are digested; the rest are recorded in `kb/analysis/qa-ledger.json` as superseded by another page, exact duplicates, or deliberately skipped, so every page is accounted for.
- **阿彌陀經 explanation: built.** 14 passages, in a detailed and an easy version.
- **Next:** consolidation (canonical concept cards, topic taxonomy, merged frameworks, flagged contradictions), then integrating the 華嚴經 text and a coverage/fidelity report.

## How it is kept trustworthy

- Every quote in a digest or explanation page is checked verbatim against its source page (`scripts/verify_digest.py`, `scripts/verify_amtj_pages.py`, `scripts/verify_amtj_easy.py`).
- Explanations attribute readings to the lecturer; they do not add doctrine the sources do not contain.
- Places where the sources are unclear, differ, or have garbled text are recorded (`notes`, `errata`, `open_questions`) and not silently resolved.

To rebuild the whole site into `site/` (landing page, 经典, 讲座, 问答, 知识库, 关于; it runs the 阿弥陀经 and knowledge-base builders too):

```
python -I scripts/build_site.py
```

## Licence

The scripts in `scripts/` are my own work. The teaching content is **not** mine and is **not** licensed by this repository; see the attribution above. Digests and explanation pages are derived study material built from that content, with every quotation traceable to its source page.

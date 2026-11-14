---
name: investment-comic-book
description: Produce a Korean investment education textbook as source-aligned Naver Webtoon episodes, including planning, scripts, art, explanations, and review records.
---

# Investment Comic Textbook Skill

Read `GOAL.md`, `CHARACTER_SHEET.md`, the relevant chapter goal, and the scoped hook output before production. Read `SOURCE_TOC_MAP.md` and `SOURCE_VARIANT_NOTE.md` before changing source mappings or episode content.

## Workflow

1. Verify the source edition, chapter/topic title, printed page range, and PDF physical page range. Visually inspect scanned pages; do not infer the table of contents from a prior adaptation plan.
2. Map each source Topic to its episode ID and record the exact source range in `SOURCE_TOC_MAP.md`, the chapter plan, and the episode metadata. Keep confirmed facts separate from provisional mappings.
3. Set one concrete learning outcome and a relatable character conflict for the episode before writing dialogue.
4. Write the scroll-ordered script and storyboard. Use the recurring cast and build an explanation around what the reader sees happen. Keep examples clearly identified as examples; do not turn the comic into personal investment advice.
5. Add a concise concept explanation only where it helps the episode. Do not add repeated generic review questions, an artificial “reading order” label, or redundant links to the same explanation.
6. Generate sequential vertical-scroll artwork only after script and storyboard are stable. Use the approved character reference `chapters/14/014.png`; reproduce the character sheet consistently. Do not treat another generated episode as a new reference without user approval.
7. Put the episode title in its first cut only when needed. Do not put chapter labels or episode IDs inside the artwork. Name cuts `NN-TT-SSS.png`, for example `08-01-001.png`, under `chapters/<episode-id>/scroll/`.
8. Review every cut at phone width for lettering, contrast, panel order, spacing, and scroll rhythm. Check source accuracy, economic direction, risk language, Korean readability, character consistency, and whether every visual symbol agrees with its label and explanation.
   - Inspect the actual 690px JPG export as well as the PNG master. Regenerate a cut if lettering, bubble attribution, character design, or economic meaning becomes unclear at mobile width.
   - Do not invent share prices, return percentages, asset-allocation ratios, or thresholds. If a fictional numerical example is necessary, label it as an example and keep it separate from sourced facts.
   - Compare every generated label, dialogue bubble, formula, quiz prompt, choice, and answer against the approved script and source. If a source question is adapted or its choices are changed, label it as a reconstructed practice question; never present it as a verbatim source question.
9. Preserve earlier fixed-page drawings as drafts. Do not count them as complete vertical-scroll episodes and do not delete them.
10. Export separate Naver upload files only after checking the current official creator upload requirements. Keep the high-quality PNG scroll masters. Record export files and review status; never claim platform readiness from assumed limits.
11. Run `.codex/hooks/book_hooks.py --scope NN-` for the chapter being produced. Fix scoped errors and warnings before moving to its next Topic. Global legacy warnings may be reported separately and must not be hidden.

## Completion gate

An episode is complete only when its source mapping, learning goal, script, storyboard, explanation, ordered scroll art, mobile review, source/character review, and current Naver export check are present. A conceptually accurate draft may proceed while source mapping is pending, but it must be labeled provisional and cannot be marked source-verified or complete.

## Chapter-specific references

- `GOAL.md` defines the currently authorized chapter scope. Use that chapter's `CHAPTER_NN_PLAN.md` as its authoritative episode map and `CHAPTER_NN_GOAL.md` for its completion criteria.
- Keep printed page numbers separate from PDF physical page numbers. Check the actual selected PDF visually; do not transfer a Topic map from another edition or assume a constant page offset.
- Preserve existing chapter folders and legacy drafts. New episodes use IDs and paths matching their source chapter, such as `05-01/scroll/05-01-001.png`.
- Run the matching scoped check, for example `python .codex/hooks/book_hooks.py --scope 05-`. The hook compares planned Topic order and episode source-topic metadata, checks ordered assets and review status, and validates exported JPG records.
- Chapter 4 is complete at `04-01`–`04-19`; its legacy `chapters/04/` exchange-rate draft remains separate from those episodes.

## Editorial rules

- Naver Webtoon vertical scroll is the sole target format; do not create page-based book variants.
- A chapter is organized in the exact source Topic order. One Topic normally maps to one episode; split a dense Topic only when necessary and retain its source identifier.
- Each chapter should have an opening, development, and closing takeaway across its episodes, without forcing the same episode template repeatedly.
- Keep textbook facts, illustrative examples, and fictional dialogue distinguishable.
- Avoid guaranteed-return claims and personalized recommendations.
- Save source page references for definitions, graphs, formulas, thresholds, and claims, not just for the episode title.
- State whether claims are source facts, illustrative examples, or theoretical assumptions. Keep model conclusions conditional on the assumption that produces them.

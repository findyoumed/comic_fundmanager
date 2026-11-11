---
name: investment-comic-book
description: Write and produce a complete Korean investment education comic book from source textbooks, including planning, scripts, storyboards, artwork, explanations, and review records.
---

# Investment Comic Textbook Skill

Before each chapter, read `GOAL.md`, `CHARACTER_SHEET.md`, and the project hook output.
For Chapters 8 and 9, also read the chapter-specific goal file (`CHAPTER_08_GOAL.md` or `CHAPTER_09_GOAL.md`) before drafting or generating artwork.

Before changing a chapter, also read `SOURCE_TOC_MAP.md` and `SOURCE_VARIANT_NOTE.md`. Treat a chapter title as provisional until its source subsection and page range are verified.

## Naver Webtoon-only textbook workflow

1. Confirm source pages and extract the chapter's claims.
2. Transcribe the source table of contents and map every episode to an exact source subsection and page range.
3. Turn claims into a chapter goal and a character-driven conflict.
3a. Write and lock the episode learning goal before writing dialogue or generating an image.
4. Write a scene outline, scroll-ordered script, concise dialogue, and vertical-scroll storyboard for Naver Webtoon. Plan the reading rhythm for a phone screen; keep each scene focused and leave breathing room between important beats.
5. Add a concise concept explanation with the key term, practical meaning, and relevant caveat. Do not add a generic repeated review-question block or an artificial "reading order" label.
6. Produce artwork only after the manuscript and storyboard are stable. Generate scenes as sequential scroll assets, not a single fixed six-panel page. Keep textbook labels and recap blocks visually distinct from dialogue.
7. Preview the artwork at mobile reading width. Check speech balloon size, line length, text contrast, panel order, spacing, and whether a reader can follow the explanation without zooming.
8. Review source accuracy, economic direction, investment-risk wording, character continuity, Korean readability, and scroll flow.

## Character continuity gate

Before generating any new image, inspect the approved character reference image and repeat the exact character bible in the prompt. The three recurring characters must keep the same face, hairstyle, proportions, clothing colors, and roles across episodes. A new image is not accepted merely because the story content is correct: if the character design drifts, regenerate it before moving to the next Topic.

For this project, the approved reference is the existing three-character reference image supplied by the user. Do not treat a newly generated episode image as a new character reference unless the user explicitly approves it.

## Non-negotiables

- Treat the output as a structured webtoon textbook, not a loose collection of images.
- Separate textbook fact, illustrative example, and fictional dialogue.
- Never imply guaranteed returns or personalized financial advice.
- Each chapter must have an opening hook, a mid-chapter turning point, and a closing takeaway.
- Each episode must have a learning objective, readable scroll scenes, and a concise concept takeaway. Add terminology or risk notes only where they clarify the topic; do not force repeated template sections or generic review questions.
- Never call a thematic outline the official book table of contents until it is mapped to the source PDF.
- When source mapping is incomplete, label the manuscript `adaptation-draft`, continue producing conceptually accurate comics, and leave page citations pending rather than stopping artwork.
- After every chapter change, run the project hook and verify that the reader asset, manuscript files, and metadata remain aligned.
- Keep a source-page record for every definition, graph, formula, and claim.
- Store each approved episode image under its exact episode filename, such as `08-01.png`, and visually compare it with the approved reference before marking the episode complete.
- Naver Webtoon is the only output format for this project. Distinguish a portrait page from a true vertical-scroll episode. Final episode art must be organized as a tall continuous scroll master and then exported to the current Naver upload requirements. Do not create book-page variants or claim platform-ready status based only on portrait orientation or guessed pixel limits; verify the current Naver creator upload guidance when preparing publication exports.
- Preserve all previously generated fixed-page illustrations as drafts/reference assets. Redraw their story content into the Naver vertical-scroll format; do not delete the drafts and do not mark them complete.
- Store final scroll segments in `chapters/<episode-id>/scroll/` with sequential names such as `001.png`, `002.png`, and so on. Keep the episode title in the art and the episode ID in filenames/metadata only.
- Mark an episode complete only when its scroll assets exist, the mobile-readability and character/source reviews are recorded, and the Naver export check is complete. Exact upload constraints must come from current Naver creator guidance, not assumptions.

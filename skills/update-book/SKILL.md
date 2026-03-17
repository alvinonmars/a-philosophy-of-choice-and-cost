---
name: update-book
description: "End-to-end pipeline for adding new chapters to the '人选天选论 — A Philosophy of Choice and Cost' book. Use this skill when the user wants to update the book, add a new chapter, process chapter images, run the book pipeline, do OCR transcription for the book, proofread book chapters, translate book chapters, generate the bilingual edition, or anything related to the 人选天选论 digitization workflow. Also trigger when the user mentions 'update book', 'new chapter', 'process chapter', 'book pipeline', 'book OCR', or refers to the a-philosophy-of-choice-and-cost project."
---

# Update Book — 人选天选论 Chapter Pipeline

Automates the full 6-phase pipeline for adding new chapters to the book project at `~/Desktop/a-philosophy-of-choice-and-cost/`.

## Invocation

```
/update-book <chapter_number> [image_source_path]
```

- `chapter_number` (required): The chapter number, e.g. `3`, `04`, `5`. Normalize to zero-padded two-digit format internally (e.g. `03`, `04`).
- `image_source_path` (optional): Directory containing the source images. Defaults to `~/Desktop/a-philosophy-of-choice-and-cost/images/`.

**Examples:**
- `/update-book 4` — process chapter 4 from images already in `images/`
- `/update-book 5 ~/Downloads/ch5_photos/` — copy images from a custom source directory first

## Project Layout

```
~/Desktop/a-philosophy-of-choice-and-cost/
├── images/                  # Working directory for current chapter images (gitignored)
│   └── processed/chXX/     # Completed images moved here after pipeline
├── zh/src/                  # Chinese source markdown
│   ├── SUMMARY.md
│   ├── preface.md
│   ├── aside.md
│   ├── ch01.md, ch02.md, ...
├── en/src/                  # English translation markdown
│   ├── SUMMARY.md
│   ├── ch01.md, ch02.md, ...
├── bilingual/src/           # Bilingual CN/EN edition
│   ├── SUMMARY.md
│   ├── ch01.md, ch02.md, ...
└── WORKFLOW.md              # Canonical reference
```

## Key Term Glossary

Every translation agent and reviewer MUST use these exact terms. No synonyms, no variations.

| Chinese | English | Notes |
|---------|---------|-------|
| 人选 | Human Choice | Core concept — the choice a person makes |
| 天选 | Heaven's Selection | Core concept — the outcome one cannot control |
| 祸 | Cost | Not "disaster" or "misfortune" |
| 福 | Fortune | Not "blessing" or "happiness" |
| 天权 | Celestial Balance | Not "heavenly power" |
| 天机 | Celestial Insight | Not "heavenly secret" |
| 贪婪 | Greed | |
| 恐惧 | Fear | |
| 自治 | Self-rationalization | NOT "self-governance" or "autonomy" |
| 道痕 | Dao Marks | Not "path marks" in this translation context |
| 两忘 | Double Forgetting | |
| 破画原理 | The Painting Principle | |
| 《剑来》 | "Sword Come" | Novel title — do not translate as other novels |

When encountering terms not in this glossary, preserve the original Chinese in parentheses after the English translation on first occurrence.

## Pipeline Execution

Run each phase sequentially. Do not skip phases. Report progress to the user after each phase completes.

---

### Phase 1: Image Preparation

**Goal:** Get properly named images into `images/` sorted by page order.

1. Set variables:
   ```
   PROJECT=~/Desktop/a-philosophy-of-choice-and-cost
   CH=XX  (zero-padded chapter number)
   ```

2. If a custom `image_source_path` was provided:
   - Copy all image files (jpg, jpeg, png) from that directory to `$PROJECT/images/`
   - Rename them to the pattern `chXX_NN.jpg` (e.g. `ch04_01.jpg`, `ch04_02.jpg`, ...) sorted by original filename or creation date
   - Confirm the count with the user

3. If images are already in `$PROJECT/images/`:
   - List all files matching `chXX_*` pattern
   - Verify they are sorted correctly
   - Report the count to the user

4. Verify: display the sorted file list and total count. Ask the user to confirm before proceeding.

**Checkpoint:** "Found N images for chapter XX. Proceeding to OCR."

---

### Phase 2: OCR Transcription

**Goal:** Produce `zh/src/chXX.md` from the page images.

1. Read ALL images for this chapter from `$PROJECT/images/`
2. For chapters with many pages (>10), split across parallel agents, each handling a segment
3. For smaller chapters, a single agent can handle all pages

Each OCR agent:
- Reads assigned images carefully, zooming in on ambiguous characters
- Transcribes all text to markdown
- Applies formatting: `#` headings, `> ` blockquotes, `**bold**`, `---` page breaks between pages
- The chapter heading format is: `# 第X章 · [chapter title]`
- **CRITICAL: Multi-line blockquotes must have `>` blank lines between each line.** Otherwise markdown merges them into one paragraph. Example:
  ```
  > Line one.
  >
  > Line two.
  ```
- Use `<div class="epigraph">` for chapter opening pages (see WORKFLOW.md Formatting Standards)
- Use `<div class="chapter-footer">` for chapter-end attribution

4. If multiple agents were used, merge their outputs into a single `$PROJECT/zh/src/chXX.md`
5. Display the first 20 lines and last 10 lines for a quick sanity check

**Common OCR pitfalls to watch for:**
- Similar characters: 入/人, 温/逼, 跟/泯, 自洽/自治
- Missing negation words (不)
- Duplicated or dropped characters
- Punctuation ambiguity: 、vs ，vs ；
- Always refer back to the original image for ambiguous characters

**Checkpoint:** "OCR complete. zh/src/chXX.md created (N lines). Starting proofreading."

---

### Phase 3: Multi-Agent Proofreading Loop

**Goal:** Ensure the Chinese transcription is character-perfect against the original images.

#### Round Structure

Launch 3 parallel Opus agents. Each independently compares `zh/src/chXX.md` against ALL original images for this chapter.

Each agent produces an error report:
```
PASS — no errors found

OR

FAIL — errors found:
Line: [line number]
Image: [filename]
Wrong: [current text]
Correct: [text from image]
```

#### Loop Rules

1. Collect all 3 reports
2. If ANY agent reports FAIL: apply all corrections to `zh/src/chXX.md`, then re-launch all 3 agents
3. If ALL 3 report PASS: check round count
4. **Minimum 2 rounds** even if the first round is all-PASS — run a second confirmation round regardless
5. After round 2+, if all 3 PASS, phase is complete
6. Safety limit: if after 5 rounds there are still FAILs, stop and report the remaining issues to the user for manual review

**Report after each round:**
```
Proofreading Round N:
  Agent 1: PASS/FAIL (X errors)
  Agent 2: PASS/FAIL (X errors)
  Agent 3: PASS/FAIL (X errors)
  Status: [continuing / complete]
```

**Checkpoint:** "Proofreading complete after N rounds. All 3 agents PASS. Starting layout polish."

---

### Phase 3.5: Layout Polish

**Goal:** Make the markdown well-formatted for comfortable reading — especially on mobile. No need to match the original images exactly.

Launch 1 agent to review `zh/src/chXX.md` and apply these formatting rules:

#### Rules

1. **Multi-line blockquotes**: Every `> ` line in a multi-line group MUST have a `>` blank line between them. No exceptions.

2. **Chapter epigraph** (if the chapter has an opening poem/title page): Wrap in HTML structure:
   ```html
   <div class="epigraph">
   <div class="book-title">人 选 天 选 论</div>
   <div class="book-author">姜 蓝 著</div>
   <hr>
   <div class="verse">

   verse line 1

   verse line 2

   </div>
   </div>
   ```

3. **Chapter footer** (last line, author attribution): Wrap in:
   ```html
   <div class="chapter-footer">— 姜蓝《人选天选论》· 第X章 标题 —</div>
   ```

4. **Short poetic/rhythmic sentences** that clearly form a list or verse (e.g., "有的人找运气 / 有的人找形势 / ..."): Must be in a blockquote with `>` blank lines between each line. Do NOT merge into one paragraph.

5. **No unnecessary formatting**: Don't add HTML classes to normal body paragraphs. CSS handles indent and spacing automatically.

6. **No unreasonable line breaks**: Only split into separate lines when the text is clearly:
   - A verse or poem (rhythmic, parallel structure)
   - A list of items (每一行是一个独立条目)
   - A repeated pattern (e.g., "有的人...有的人...有的人...")

   Normal prose paragraphs must NEVER be split into multiple lines. If a sentence is long, leave it as one paragraph.

7. **Punctuation cleanup**:
   - Remove unnecessary punctuation that disrupts reading flow
   - Don't add punctuation that isn't in the source text
   - Watch for doubled punctuation (，，or 。。)
   - Ensure quotation marks are properly paired（""not mixing ""and""）
   - Chinese text uses Chinese punctuation（，。、；：""）not English (,.;:"")

8. **Verify `---` placement**: Page break separators should be between major sections, not randomly inserted.

The agent reads the file, applies fixes, and writes it back. Then display a summary of changes made.

**Checkpoint:** "Layout polish complete. N formatting fixes applied. Starting translation."

---

### Phase 4: Translation

**Goal:** Produce `en/src/chXX.md` — a faithful, natural English translation.

#### Step 1: Translate

1. Launch a translation agent (or multiple for long chapters) that receives:
   - The finalized `zh/src/chXX.md`
   - The full glossary table from this skill
   - Instructions: translate paragraph by paragraph, preserve all markdown formatting, use glossary terms exactly, preserve `---` page breaks

2. Save output to `$PROJECT/en/src/chXX.md`

#### Step 2: Translation Review Loop

Launch 3 parallel Opus review agents. Each reviews the full translation checking for:

- **Glossary consistency:** Every glossary term must match exactly. Flag any deviations.
- **Meaning accuracy:** No reversed meanings, no collapsed compound concepts, no added interpretation.
- **Negation:** Verify all negation words (不, 没, 无, 非) are properly reflected.
- **Cultural references:** Book titles, proper nouns, idioms — check each one.
- **Natural English flow:** Should read well as English prose, not as translationese.

**Known pitfalls:**
- 不抬价 = "not raise the price", NOT "lower the price"
- 分裂统一 should not be collapsed into one word
- Check ALL files for variant spellings of key terms

**Loop rules:** Same as proofreading — 3 agents, all must PASS, minimum 2 rounds, safety limit of 5 rounds.

**Report format:** Same as proofreading rounds.

**Checkpoint:** "Translation complete and reviewed. en/src/chXX.md created. Starting bilingual edition."

---

### Phase 5: Bilingual Edition

**Goal:** Produce `bilingual/src/chXX.md` — paragraph-by-paragraph CN/EN comparison.

1. Read both `zh/src/chXX.md` and `en/src/chXX.md`
2. Generate the bilingual file with this format:

```markdown
# Chapter Title EN | 第X章 · 中文标题

> Chinese paragraph text here.

English translation paragraph here.

---

> Next Chinese paragraph.

Next English paragraph.

---
```

Rules:
- Chinese text in blockquotes (`> `)
- English translation as regular text immediately after
- `---` separator between each CN/EN pair
- Preserve all headings (use `# EN Title | 中文标题` format)
- One agent per chapter is sufficient

3. Save to `$PROJECT/bilingual/src/chXX.md`

**Checkpoint:** "Bilingual edition created. Starting final updates."

---

### Phase 6: Finalize and Deploy

**Goal:** Update metadata, archive images, commit, and push.

#### Step 1: Update SUMMARY.md files

Determine the chapter title from the Chinese source (the `# 第X章 · ...` heading) and the English translation.

Append to each SUMMARY.md:

**`zh/src/SUMMARY.md`** — add:
```markdown
- [第X章 · {中文标题}](chXX.md)
```

**`en/src/SUMMARY.md`** — add:
```markdown
- [Chapter X: {English Title}](chXX.md)
```

**`bilingual/src/SUMMARY.md`** — add:
```markdown
- [Chapter X: {English Title} | 第X章 · {中文标题}](chXX.md)
```

Follow the exact pattern of existing entries. Read each SUMMARY.md first to match the style.

#### Step 2: Move processed images

```bash
mkdir -p $PROJECT/images/processed/chXX/
mv $PROJECT/images/chXX_* $PROJECT/images/processed/chXX/
```

#### Step 3: Commit and push

```bash
cd $PROJECT
git add zh/src/chXX.md en/src/chXX.md bilingual/src/chXX.md
git add zh/src/SUMMARY.md en/src/SUMMARY.md bilingual/src/SUMMARY.md
git commit -m "Add Chapter XX: {English Title} ({中文标题})

- Chinese source: zh/src/chXX.md
- English translation: en/src/chXX.md
- Bilingual edition: bilingual/src/chXX.md
- Proofreading: N rounds, all 3 agents PASS
- Translation review: N rounds, all 3 agents PASS"
git push
```

**Checkpoint:** "Chapter XX pipeline complete. All 3 editions updated. Pushed to GitHub — auto-deploy will publish to Pages."

---

## Error Handling

- If any phase fails, stop and report to the user. Do not silently continue.
- If the chapter file already exists in `zh/src/`, warn the user and ask whether to overwrite or skip OCR.
- If images are missing or the count seems wrong, confirm with the user before proceeding.
- If `git push` fails, report the error and let the user resolve it.

## Resume Support

If the user says "resume chapter X" or "continue from phase N":
- Check which output files already exist (`zh/src/chXX.md`, `en/src/chXX.md`, `bilingual/src/chXX.md`)
- Skip completed phases and resume from the first missing output
- Always confirm with the user which phase to start from

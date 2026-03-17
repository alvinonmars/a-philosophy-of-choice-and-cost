# End-to-End Book Digitization Workflow

Complete pipeline: image screenshots → OCR → proofreading → translation → review → bilingual edition → deployment.

## Prerequisites

- Claude Code with Opus model (multi-agent capable)
- mdBook 0.4.52+
- GitHub repo with Pages enabled (Actions workflow)

## Phase 1: Image Preparation

1. Collect PNG screenshots of all book pages
2. Sort by filename/creation date to determine page order
3. Place in `images/` directory

## Phase 2: OCR Transcription

Launch parallel agents, each handling a section of pages:

```
Agent 1: pages 1-8 → preface.md
Agent 2: pages 9-16 → ch01.md
Agent 3: pages 17-end → ch02.md
```

Each agent:
1. Reads assigned images
2. Transcribes all text to markdown
3. Applies formatting: headings, blockquotes, bold, `---` page breaks

## Phase 3: Multi-Agent Proofreading Loop

### Round Structure

Launch 3 parallel Opus agents. Each independently compares markdown against original images.

**Error report format:**
```
Line: [line number]
Image: [filename]
Wrong: [current text]
Correct: [text from image]
```

### Loop Rules

1. Apply all corrections
2. Re-launch 3 review agents
3. Each reviewer: PASS or FAIL
4. If ANY reviewer FAILs → fix errors → re-launch all 3
5. If ALL 3 PASS → phase complete
6. Minimum 2 rounds even if first round passes

### Common OCR Pitfalls

- Similar characters: 入/人, 温/逼, 跟/泯, 自洽/自治
- Missing negation words (不)
- Duplicated or dropped characters
- Punctuation ambiguity (、vs ，vs ；)
- Always use high-res originals for ambiguous characters

## Phase 4: Translation (Multi-Agent Parallel)

### Setup

1. Define key term glossary before starting:
   ```
   人选 = Human Choice
   天选 = Heaven's Selection
   祸 = Cost
   福 = Fortune
   天权 = Celestial Balance
   天机 = Celestial Insight
   贪婪 = Greed
   恐惧 = Fear
   自治 = Self-rationalization
   道痕 = Dao Marks
   两忘 = Double Forgetting
   破画原理 = The Painting Principle
   ```

2. Launch parallel Opus translation agents (one per chapter)
3. Each agent receives the glossary + source text

### Translation Review Loop

Launch 3 parallel Opus review agents. Each reviews ALL translated files for:
- Glossary consistency (key terms must match exactly)
- Meaning accuracy (no reversed meanings, no collapsed concepts)
- Cultural references (book titles, proper nouns)
- Natural English flow

**Loop rules:** Same as proofreading — all 3 must PASS.

### Known Translation Pitfalls

- Book titles: 《剑来》= "Sword Come", not other novels
- Negation reversal: 不抬价 = "not raise the price", not "lower the price"
- Compound concepts: 分裂统一 should not be collapsed into one word
- Term consistency: check ALL files for variant spellings of key terms

## Phase 5: Bilingual Edition

Generate paragraph-by-paragraph CN/EN comparison:
- Chinese text in blockquotes (`> `)
- English translation as regular text
- Separated by `---` between each pair
- One agent per chapter, run in parallel

## Phase 6: Build & Deploy

### Local Verification

```bash
mdbook build zh -d ../build/zh
mdbook build en -d ../build/en
mdbook build bilingual -d ../build/bilingual
```

### GitHub Actions (`.github/workflows/deploy.yml`)

Builds all 3 editions + landing page, deploys to GitHub Pages automatically on push to main.

### Landing Page (`index.html`)

Links to all 3 editions + Discord community.

## Adding New Chapters

When new chapter images are available:

1. Place images in `images/` (sorted by page order, e.g. `ch03_01.jpg` ~ `ch03_07.jpg`)
2. Run OCR agent → new `zh/src/chXX.md`
3. Run proofreading loop (3 agents, until all PASS)
4. Run layout polish agent (blockquote line breaks, epigraph/footer HTML, verse formatting)
5. Run translation agent → new `en/src/chXX.md`
6. Run translation review loop (3 agents, until all PASS)
7. Run layout polish on `en/src/chXX.md`
8. Run bilingual agent → new `bilingual/src/chXX.md`
9. Run layout polish on `bilingual/src/chXX.md`
10. Update all 3 `SUMMARY.md` files
11. Move processed images to `images/processed/chXX/` to avoid reprocessing
12. Commit and push (auto-deploys)

> **Note:** `images/` is gitignored — source images are kept locally for traceability but not committed to the repo.

## Formatting Standards

Custom CSS (`src/custom.css`) is shared across all 3 editions. The styling matches the original book's visual layout.

### Epigraph (Chapter Opening Page)

Each chapter starts with an epigraph page. Use this HTML structure:

```html
<div class="epigraph">
<div class="book-title">人 选 天 选 论</div>
<div class="book-author">姜 蓝 著</div>
<hr>
<div class="verse">

"引言文字"

逐行排列

</div>
</div>
```

### Body Text

- **No special markup needed** — CSS handles first-line indent (`text-indent: 2em`)
- Use `---` for page breaks between sections
- Use `> ` blockquotes for highlighted text boxes (grey background, matching original)
- **CRITICAL: Multi-line blockquotes must have `>` blank lines between each line**, otherwise markdown merges them into one paragraph:

```markdown
WRONG (renders as one line):
> Line one.
> Line two.

CORRECT (renders as separate lines):
> Line one.
>
> Line two.
```

### Chapter Footer

```html
<div class="chapter-footer">— 姜蓝《人选天选论》· 第X章 标题 —</div>
```

### Visual Effects (via CSS)

| Element | Effect |
|---------|--------|
| Body text | Serif font (Noto Serif SC), 2em first-line indent, warm background |
| Headings | Centered, letter-spaced |
| Blockquotes | Light grey background box with left border |
| Page breaks | Thin centered line, 40% width |
| Epigraph | Centered layout, large title, verse text |
| Footer | Centered, small, grey |

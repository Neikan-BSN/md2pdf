---
model: haiku
description: Convert markdown files to PDF/HTML with configurable defaults
---

# md2pdf Skill

Convert markdown files to PDF or HTML using the md2pdf renderer.

## Usage

```
/md2pdf <file-or-pattern>
/md2pdf docs/report.md
/md2pdf "slides/*.md"
/md2pdf file1.md file2.md
```

## Behavior

1. **Parse input** - Extract file path(s) from arguments
2. **Validate files** - Check files exist before prompting
3. **Load config** - Read defaults from `.claude/config/md2pdf-skill.json`
4. **Present settings** - Show file count and current defaults
5. **Prompt if needed** - Ask to proceed or customize
6. **Execute conversion** - Run `md2pdf_batch.py`
7. **Report results** - Show success/failure for each file
8. **Offer to save** - Ask to save settings as new defaults

## Instructions

When this skill is invoked with file arguments:

### Step 1: Extract Pattern
Extract the file pattern from the user's command (everything after `/md2pdf `).
Remove any surrounding quotes from the pattern.

### Step 2: Validate Files Exist
Run validation with `--json-output` to get machine-readable result:
```bash
python md2pdf_batch.py --files <pattern> --format html --json-output
```

**Check the JSON output:**
- If output contains `"error":` key at top level, files not found - report error and stop
- If output contains `"total":` key, files were found - continue

Example error: `{"error": "No files found matching: missing.md"}`
Example success: `{"total": 2, "success": 2, ...}`

### Step 3: Load Config
```bash
cat .claude/config/md2pdf-skill.json 2>/dev/null
```

If file doesn't exist, use defaults: `{"defaults":{"format":"pdf","theme":"academic","output_mode":"same-dir"}}`

### Step 4: Present Settings
Report to user:
```
Found N file(s) to convert:
  - file1.md
  - file2.md

Current settings: <format> format, <theme> theme

Proceed? [Y]es / [n]o / [c]ustomize
```

### Step 5: Handle Response

**If Y or yes (default):** Proceed with current settings

**If n or no:** Cancel and exit

**If c or customize:** Prompt for each setting:
```
Output format:
  1. pdf
  2. html
Select [1-2]:

Theme (run 'python -c "from theme_manager import list_themes; print(list_themes())"' to see current list):
  1. academic
  2. clinical
  3. journal
  4. minimal
  5. modern
  6. presentation
Select [1-6]:
```

### Step 6: Execute Conversion

**For 1-5 files (sequential):**
```bash
python md2pdf_batch.py --files <pattern> --format <format> --theme <theme>
```

**For 6+ files (parallel):** See Parallel Processing section below.

### Step 7: Report Results
Parse output and report:
```
Converted N/M files:
  + file1.md -> file1.pdf
  + file2.md -> file2.pdf
  x file3.md (error message)
```

### Step 8: Offer to Save
If conversion succeeded and settings differ from saved config:
```
Save these settings as defaults? [y/N]
```

**If y or yes:** Write to `.claude/config/md2pdf-skill.json`:
```json
{
  "defaults": {
    "format": "<format>",
    "theme": "<theme>",
    "output_mode": "same-dir"
  }
}
```

Create the `.claude/config/` directory if it doesn't exist.

## Parallel Processing (6+ files)

When batch contains 6 or more files:

1. **Calculate chunk count:** `num_chunks = min(5, ceil(file_count / 4))`
   - 6-8 files → 2 chunks
   - 9-12 files → 3 chunks
   - 13-16 files → 4 chunks
   - 17+ files → 5 chunks
2. Distribute files evenly across chunks
3. Spawn parallel Task agents with `model: haiku`
4. Each agent runs: `python md2pdf_batch.py --files <chunk> --format <format> --theme <theme> --json-output`
5. Collect JSON results from all agents
6. Merge results and report consolidated summary

Example for 12 files (3 chunks):
```
Agent 1: file1.md file2.md file3.md file4.md
Agent 2: file5.md file6.md file7.md file8.md
Agent 3: file9.md file10.md file11.md file12.md
```

## Error Handling

| Error | Action |
|-------|--------|
| Files not found | Report error with pattern, do not proceed |
| Invalid theme | Report: "Theme 'X' not found. Available: academic, clinical, ..." |
| Renderer timeout | Report which file failed, continue with remaining files |
| Partial failure | Report summary showing successes and failures |

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
2. **Resolve files** - Expand globs, validate files exist
3. **Load config** - Read defaults from `.claude/config/md2pdf-skill.json`
4. **Present settings** - Show current defaults
5. **Prompt if needed** - Ask to override defaults
6. **Execute conversion** - Run `md2pdf_batch.py`
7. **Report results** - Show success/failure summary
8. **Offer to save** - Ask to save settings as new defaults

## Instructions

When this skill is invoked with file arguments:

1. Extract the file pattern from the user's command (everything after `/md2pdf `)

2. Run file resolution:
   ```bash
   python md2pdf_batch.py --files "<pattern>" --json-output --format pdf --theme academic 2>&1 | head -1
   ```
   Check if this returns an error. If files not found, report and stop.

3. Load skill config if exists:
   ```bash
   cat .claude/config/md2pdf-skill.json 2>/dev/null || echo '{"defaults":{"format":"pdf","theme":"academic"}}'
   ```

4. Report to user:
   ```
   Found N file(s) to convert
   Current settings: PDF format, academic theme

   Proceed with these settings? [Y/n/customize]
   ```

5. If user says customize (c), prompt for:
   - Format: pdf or html
   - Theme: academic, clinical, journal, minimal, modern, or presentation

6. Execute conversion:
   ```bash
   python md2pdf_batch.py --files "<pattern>" --format <format> --theme <theme>
   ```

7. Report results from output

8. If successful, ask:
   ```
   Save these settings as defaults? [y/N]
   ```
   If yes, update `.claude/config/md2pdf-skill.json`

## Parallel Processing (6+ files)

When batch contains 6 or more files:

1. Split files into chunks of ~4 files each
2. Spawn parallel Task agents (max 5) with model=haiku
3. Each agent runs: `python md2pdf_batch.py --files <chunk> --json-output ...`
4. Collect JSON results from all agents
5. Report consolidated summary

Example parallel dispatch:
```
Files: doc1.md doc2.md doc3.md doc4.md doc5.md doc6.md doc7.md doc8.md

Agent 1: doc1.md doc2.md doc3.md doc4.md
Agent 2: doc5.md doc6.md doc7.md doc8.md
```

## Error Handling

- File not found: Report error, do not proceed
- Invalid theme: Report available themes
- Renderer failure: Report which files failed, continue with others
- Partial batch failure: Report summary with successes and failures

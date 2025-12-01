# md2pdf Skill Design

**Date:** 2025-12-01
**Status:** Approved

## Overview

A Claude Code skill that wraps md2pdf with configurable defaults, interactive prompts, and parallel batch processing.

## Requirements

| Requirement | Decision |
|-------------|----------|
| Input method | Explicit path argument (single file or glob) |
| Prompting | Configurable defaults, prompt only when overriding |
| Config storage | Skill-specific in `.claude/config/md2pdf-skill.json` |
| Output location | Same directory as source, same filename |
| Renderer | Auto-managed (start/stop automatically) |
| Batch behavior | Uniform settings for all files |
| Parallel processing | Spawn agents for batches > 5 files |
| Model | Haiku (fast, cost-effective for straightforward tasks) |
| Result | Simple success message |

## Architecture

### Approach: Skill + Python Wrapper Script

Create a non-interactive `md2pdf_batch.py` script with CLI flags. The skill invokes it.

**Rationale:**
- Clean separation: script handles conversion, skill handles UX
- Script reusable outside Claude
- Easy to add `--config` flag for defaults

## Components

### 1. Python Wrapper Script (`md2pdf_batch.py`)

Non-interactive CLI alongside existing `md2pdf.py`:

```bash
python md2pdf_batch.py \
  --files "docs/*.md" \
  --format pdf \
  --theme academic \
  --output-mode same-dir \
  --json-output  # For parallel agent result collection
```

**Flags:**

| Flag | Purpose | Default |
|------|---------|---------|
| `--files` | Glob pattern or file path(s) | Required |
| `--format` | `pdf` or `html` | `pdf` |
| `--theme` | Theme name | `academic` |
| `--output-mode` | `same-dir` or `custom` | `same-dir` |
| `--output-dir` | Custom output directory | None |
| `--json-output` | Machine-readable output | False |

**Behavior:**
- Accepts multiple `--files` arguments or glob patterns
- Validates files exist before starting
- Starts renderer automatically, stops when done
- Outputs each file to its source directory with same stem name

**Imports from existing code:**
- `document_builder.build_html_document()`
- `renderer_client.RendererClient`
- `theme_manager.list_themes()`
- `config_loader.load_config()`

### 2. Skill Configuration (`.claude/config/md2pdf-skill.json`)

```json
{
  "defaults": {
    "format": "pdf",
    "theme": "academic",
    "output_mode": "same-dir"
  },
  "prompt_behavior": {
    "always_confirm": false,
    "prompt_on_batch": true
  }
}
```

**Behavior:**
- Auto-created with sensible defaults on first run
- Skill announces current defaults: "Using: pdf, academic theme"
- Offers "Save these as defaults?" after conversion

### 3. Skill File (`.claude/commands/md2pdf.md`)

**Invocation:**
```
/md2pdf docs/report.md
/md2pdf "slides/*.md"
/md2pdf file1.md file2.md file3.md
```

**Model:** Haiku (specified in frontmatter)

**Flow:**
1. Parse arguments - extract file path(s)
2. Resolve files - expand globs, validate existence
3. Load config - read defaults from md2pdf-skill.json
4. Present settings - "Converting 3 files to PDF (academic theme)"
5. Prompt if needed - "Override defaults? [y/N]"
6. Execute - run md2pdf_batch.py (sequential or parallel)
7. Report - "Created: docs/report.pdf"
8. Offer save - "Save these settings as defaults? [y/N]"

## Parallel Processing

**Thresholds:**

| Batch Size | Strategy |
|------------|----------|
| 1-5 files | Sequential - single script invocation |
| 6+ files | Parallel - spawn Haiku subagents |

**Chunk strategy:**
- ~4 files per agent
- Max 5 concurrent agents
- Each agent runs `md2pdf_batch.py --json-output` on its chunk

**Consolidated output:**
```
Converted 12/12 files (3 parallel agents)
  Agent 1: 4 files in 3.2s
  Agent 2: 4 files in 2.8s
  Agent 3: 4 files in 3.1s
  Total time: 3.2s
```

## Error Handling

**File validation:**
```
/md2pdf nonexistent.md
→ "File not found: nonexistent.md"

/md2pdf "empty-dir/*.md"
→ "No markdown files match: empty-dir/*.md"
```

**Batch partial failures:**
```
Converted 4/5 files
  doc1.md → doc1.pdf
  doc2.md → doc2.pdf
  doc3.md (renderer timeout)
  doc4.md → doc4.pdf
  doc5.md → doc5.pdf
```

**Edge cases:**

| Case | Behavior |
|------|----------|
| File already exists | Overwrite silently |
| Non-.md file | Warn, proceed if confirmed |
| No write permission | Fail with clear error |
| Renderer already running | Reuse instance |
| Large batch (20+) | Show progress indicator |

## File Structure

```
md2pdf-repo/
├── md2pdf_batch.py              # New: non-interactive CLI
├── .claude/
│   ├── commands/
│   │   └── md2pdf.md            # New: skill file
│   └── config/
│       └── md2pdf-skill.json    # Auto-created on first run
```

No changes to existing files - purely additive.

## Implementation Notes

- Use `superpowers:writing-skills` when creating the skill file
- Test with `superpowers:testing-skills-with-subagents` to refine
- Script estimated at ~100-150 lines (argparse + existing imports)
- Skill estimated at ~50-80 lines of markdown instructions

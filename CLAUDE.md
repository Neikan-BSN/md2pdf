# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

md2pdf is a Python CLI tool that converts Markdown files to PDF/HTML with support for Mermaid diagrams, KaTeX math equations, and syntax highlighting. It uses a two-tier architecture: Python handles the CLI and HTML generation, while a Node.js/Puppeteer service handles PDF rendering.

## Development Commands

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js renderer dependencies
cd renderer && npm install && cd ..

# Run the interactive CLI
python md2pdf.py

# Run all tests
pytest tests/ -v

# Run single test file
pytest tests/test_cli.py -v

# Run tests with coverage
pytest tests/ --cov=. --cov-report=html

# Start renderer service manually (for debugging)
cd renderer && npm start

# Lint with ruff
ruff check .

# Format with black
black .
```

## Architecture

### Two-Tier Rendering Pipeline

1. **Python Layer** (`md2pdf.py` → `document_builder.py` → `markdown_renderer.py`)
   - CLI prompts user for file selection, format, and theme
   - `markdown_renderer.py` converts Markdown to HTML using markdown-it-py
   - `document_builder.py` assembles complete HTML document with Jinja2 template, theme CSS, and Mermaid/KaTeX scripts

2. **Node.js Renderer Service** (`renderer/server.js`)
   - Express server with Puppeteer for PDF generation
   - `RendererClient` (Python) manages server lifecycle automatically via context manager
   - Server starts on port 3000, has `/health`, `/render/pdf`, `/render/html` endpoints
   - Concurrency limited to 3 simultaneous renders

### Key Data Flow

```
Markdown File → markdown_renderer.render_markdown() → HTML content
                                    ↓
            document_builder.build_html_document() → Complete HTML (with CSS, scripts)
                                    ↓
            RendererClient.render_pdf() → HTTP POST to Node.js → PDF bytes
```

### Theme System

- CSS themes in `themes/` directory (academic, clinical, journal, minimal, modern, presentation)
- `theme_manager.py` discovers themes dynamically and loads CSS
- Each theme has an associated Mermaid theme configured in `md2pdf.config.yaml`

### Configuration

`md2pdf.config.yaml` controls:
- Default output format and theme
- PDF page size and margins
- Math engine (katex/mathjax)
- Mermaid theme per CSS theme
- Syntax highlighting toggle

## Testing Patterns

- Tests use `pytest` with Click's `CliRunner` for CLI testing
- `unittest.mock.patch` for mocking file selection and renderer
- `tmp_path` fixture for filesystem tests
- Tests are organized by module: `test_cli.py`, `test_document_builder.py`, etc.

## Docker Support

Dockerfile and docker-compose.yml available. Renderer detects Docker environment and disables Puppeteer sandbox automatically.

## Skills

### /md2pdf

Convert markdown files to PDF/HTML:

```bash
/md2pdf docs/report.md          # Single file
/md2pdf "slides/*.md"           # Batch with glob
/md2pdf file1.md file2.md       # Multiple files
```

Configuration stored in `.claude/config/md2pdf-skill.json`.

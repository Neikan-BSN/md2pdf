# md2pdf - Markdown to PDF/HTML Converter

Interactive CLI tool for converting markdown with diagrams and math to PDF/HTML.

## Features

- ✅ Interactive CLI with guided prompts
- ✅ PDF and HTML output formats
- ✅ Multiple themes (academic, modern, minimal, presentation)
- ✅ Mermaid diagram support
- ✅ KaTeX math equation rendering
- ✅ Syntax highlighting for code blocks
- ✅ Custom output filenames
- ✅ Batch file processing

## Installation

### Prerequisites

- Python 3.9+
- Node.js 16+ (for PDF generation)

### Setup

```bash
# Install Python dependencies
pip install -r requirements.txt

# Install Node.js dependencies (for PDF rendering)
cd renderer
npm install
cd ..
```

## Usage

### Interactive Mode

```bash
python md2pdf.py
```

Follow the prompts to:
1. Select markdown file(s)
2. Choose output format (PDF or HTML)
3. Select theme
4. Specify output filename

### Example

```bash
$ python md2pdf.py

=== md2pdf: Markdown to PDF/HTML Converter ===

📄 File Selection
Enter a file path or glob pattern (e.g., *.md, docs/**/*.md)
Files: document.md

✓ Found 1 markdown file(s):
  - document.md

Proceed with these files? [Y/n]: y

📄 Output Format Selection
1. PDF (portable document)
2. HTML (web page)
Select format [1-2] (default: 1): 1

🎨 Theme Selection
1. academic (default)
2. minimal
3. modern
4. presentation
Select theme [1-4] (default: 1): 1

💾 Output Filename
Default: document.pdf
Output filename (default: document.pdf):

📄 Processing: document.md
  ⚙️  Converting to PDF...
  ✅ Saved: document.pdf

✓ Conversion complete!
```

## Configuration

Edit `md2pdf.config.yaml` to customize:

- Default output format and theme
- PDF page size and margins
- Math rendering engine
- Mermaid diagram theme
- Code syntax highlighting

## Themes

- **academic** - Clean, professional style for academic papers
- **modern** - Contemporary design with accent colors
- **minimal** - Simple, distraction-free layout
- **presentation** - High-contrast for slides/presentations

## Architecture

- **Python CLI** (`md2pdf.py`) - Interactive user interface
- **Document Builder** (`document_builder.py`) - HTML generation
- **Renderer Client** (`renderer_client.py`) - HTTP client for Node.js service
- **Node.js Service** (`renderer/server.js`) - Puppeteer-based PDF generation

## Development

### Running Tests

```bash
# All tests
pytest tests/ -v

# With coverage
pytest tests/ --cov=. --cov-report=html

# Specific test file
pytest tests/test_cli.py -v
```

### Test Results

- **55 tests** across 7 test categories
- **92% code coverage**
- All tests passing

### Project Structure

```
md2pdf/
├── md2pdf.py              # Main CLI
├── document_builder.py    # HTML document builder
├── markdown_renderer.py   # Markdown to HTML
├── theme_manager.py       # Theme management
├── config_loader.py       # Configuration
├── renderer_client.py     # HTTP client
├── md2pdf.config.yaml     # Configuration file
├── templates/             # Jinja2 templates
│   └── base.html
├── themes/                # CSS themes
│   ├── academic.css
│   ├── minimal.css
│   ├── modern.css
│   └── presentation.css
├── renderer/              # Node.js service
│   ├── server.js
│   └── package.json
└── tests/                 # Test suite
```

## Known Issues

- PDF generation occasionally experiences server timing issues under heavy load
- Retry logic automatically handles most transient failures

## License

MIT

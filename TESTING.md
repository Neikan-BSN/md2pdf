# Testing Checklist

Manual testing guide for md2pdf functionality.

## Prerequisites

- [ ] Python 3.9+ installed (`python3 --version`)
- [ ] Node.js 16+ installed (`node --version`)
- [ ] Dependencies installed (`pip install -r requirements.txt`)
- [ ] Renderer dependencies installed (`cd renderer && npm install`)

## Unit Tests

```bash
pytest tests/ -v
```

**Expected:** 54/54 tests passing

## Manual Testing

### Test 1: Single File to PDF (Academic Theme)

**Steps:**
1. Create test file: `echo "# Test Document\n\nThis is a **test**." > test1.md`
2. Run: `python3 md2pdf.py`
3. Select: `test1.md`
4. Format: `1` (PDF)
5. Theme: `1` (Academic)
6. Filename: `y` (accept default)

**Expected:**
- Output: `converted/test1.pdf`
- File size: ~30-60 KB
- PDF opens correctly
- Contains formatted text

### Test 2: Single File to HTML (Modern Theme)

**Steps:**
1. Run: `python3 md2pdf.py`
2. Select: `test1.md`
3. Format: `2` (HTML)
4. Theme: `3` (Modern)
5. Filename: `y`

**Expected:**
- Output: `converted/test1.html`
- Opens in browser
- Modern styling applied

### Test 3: Batch Processing

**Steps:**
1. Create multiple files:
   ```bash
   echo "# Doc 1" > test1.md
   echo "# Doc 2" > test2.md
   echo "# Doc 3" > test3.md
   ```
2. Run: `python3 md2pdf.py`
3. Files: `test*.md`
4. Format: `1` (PDF)
5. Theme: `2` (Minimal)

**Expected:**
- 3 PDFs created in `converted/`
- No filename prompt (batch mode)
- All files converted successfully

### Test 4: Mathematical Equations

**Steps:**
1. Create: `math_test.md`
   ```markdown
   # Math Test
   
   Inline: $E = mc^2$
   
   Block:
   $$
   \int_{-\infty}^{\infty} e^{-x^2} dx = \sqrt{\pi}
   $$
   ```
2. Convert to PDF (Academic theme)

**Expected:**
- Equations render correctly
- Proper LaTeX formatting

### Test 5: Mermaid Diagrams

**Steps:**
1. Create: `mermaid_test.md`
   ```markdown
   # Diagram Test
   
   ```mermaid
   graph LR
       A[Start] --> B[Process]
       B --> C[End]
   ```
   ```
2. Convert to PDF (Modern theme)

**Expected:**
- Diagram renders correctly
- Modern theme colors applied

### Test 6: Code Syntax Highlighting

**Steps:**
1. Create: `code_test.md`
   ```markdown
   # Code Test
   
   ```python
   def hello(name):
       print(f"Hello, {name}!")
   ```
   
   ```javascript
   function greet(name) {
       console.log(`Hello, ${name}!`);
   }
   ```
   ```
2. Convert to PDF (Presentation theme)

**Expected:**
- Syntax highlighting applied
- Different colors for keywords, strings, etc.

### Test 7: Custom Filename

**Steps:**
1. Run: `python3 md2pdf.py`
2. Select: `test1.md`
3. Format: `1` (PDF)
4. Theme: `1` (Academic)
5. Filename: `n` → Enter: `my_custom_file.pdf`

**Expected:**
- Output: `converted/my_custom_file.pdf`
- Custom name used

### Test 8: Error Handling

**Steps:**
1. Run: `python3 md2pdf.py`
2. Files: `nonexistent.md`

**Expected:**
- Error message: "No files found"
- Prompt to retry

### Test 9: Non-Markdown File Warning

**Steps:**
1. Create: `echo "test" > test.txt`
2. Run: `python3 md2pdf.py`
3. Select: `test.txt`

**Expected:**
- Warning: "not a markdown file"
- Confirmation prompt

### Test 10: Comprehensive Features

**Steps:**
1. Create: `comprehensive.md` with:
   - Headings (H1-H3)
   - Text formatting (bold, italic, code)
   - Lists (ordered, unordered, nested)
   - Tables
   - Code blocks (Python, JavaScript)
   - Math equations
   - Mermaid diagram
   - Blockquotes
2. Convert to PDF (all 4 themes)

**Expected:**
- 4 PDFs with different styling
- All features render correctly
- No errors

## Performance Testing

### Test 11: Large Document

**Steps:**
1. Create document with 50+ pages of content
2. Convert to PDF

**Expected:**
- Completes in <30 seconds
- No memory errors
- PDF file size reasonable (<5 MB)

### Test 12: Batch Processing (10 files)

**Steps:**
1. Create 10 markdown files
2. Convert all to PDF

**Expected:**
- All files converted
- Single renderer instance reused
- Total time <30 seconds

## Edge Cases

### Test 13: Empty Markdown File

**Steps:**
1. Create empty file: `touch empty.md`
2. Convert to PDF

**Expected:**
- PDF created (may be mostly blank)
- No errors

### Test 14: Unicode Characters

**Steps:**
1. Create file with emoji and international characters
   ```markdown
   # Test 测试 テスト 🎉
   
   Content with café, naïve, and 日本語
   ```
2. Convert to PDF

**Expected:**
- Characters render correctly
- No encoding errors

## Checklist Summary

- [ ] All unit tests pass (54/54)
- [ ] Single file PDF conversion works
- [ ] Single file HTML conversion works
- [ ] Batch processing works
- [ ] Mathematical equations render
- [ ] Mermaid diagrams render
- [ ] Code syntax highlighting works
- [ ] Custom filenames work
- [ ] Error handling graceful
- [ ] All 4 themes work correctly
- [ ] Large documents process successfully
- [ ] Unicode handling correct

## Bug Reporting

If you find issues:
1. Note the exact error message
2. Include the markdown source (if possible)
3. Note your environment (Python version, Node.js version, OS)
4. Report as GitHub issue or bug report

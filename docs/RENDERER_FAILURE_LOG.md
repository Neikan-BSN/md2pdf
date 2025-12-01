# Renderer Failure Log

**Date:** 2025-12-01
**Context:** Setting up worktree for md2pdf-skill implementation
**Status:** Blocking - PDF rendering fails

## Summary

The Puppeteer-based PDF renderer returns HTTP 500 errors. The root cause is Chrome/Chromium failing to launch with Windows error code `3221225477` (`0xC0000005` = `STATUS_ACCESS_VIOLATION`).

## Environment

| Component | Version                      |
| --------- | ---------------------------- |
| OS        | Windows 11 Pro (Build 26100) |
| Node.js   | v24.1.0                      |
| npm       | 11.4.1                       |
| Puppeteer | 24.30.0                      |
| Python    | 3.12.10                      |

## Symptoms

### Test Failures

```
FAILED tests/test_renderer_client.py::test_render_pdf
FAILED tests/test_renderer_client.py::test_context_manager
FAILED tests/test_renderer_client.py::test_render_pdf_with_options
========================= 3 failed, 5 passed in 2.39s =========================
```

### Direct API Test

```bash
curl -X POST http://localhost:3000/render/pdf \
  -H "Content-Type: application/json" \
  -d '{"html": "<html><body><h1>Test</h1></body></html>"}'
```

**Response:**

```json
{
  "error": "PDF rendering failed",
  "message": "Failed to launch the browser process:  Code: 3221225477\n\nstderr:\n\n\nTROUBLESHOOTING: https://pptr.dev/troubleshooting\n"
}
```

### Health Check (Works)

```bash
curl http://localhost:3000/health
```

```json
{
  "status": "healthy",
  "service": "md2pdf-renderer",
  "version": "1.0.0",
  "timestamp": "2025-12-01T15:52:47.516Z"
}
```

## Root Cause Analysis

### Error Code 3221225477

- Hex: `0xC0000005`
- Windows status: `STATUS_ACCESS_VIOLATION`
- Meaning: Memory access violation when launching Chrome

### Puppeteer Browser Cache

Browsers are installed in the Puppeteer cache:

```
C:\Users\Administrator\.cache\puppeteer\chrome\win64-142.0.7444.162\chrome-win64\chrome.exe
C:\Users\Administrator\.cache\puppeteer\chrome-headless-shell\win64-142.0.7444.162\chrome-headless-shell-win64\chrome-headless-shell.exe
```

### Manual Browser Tests

| Executable                | Command       | Result                                            |
| ------------------------- | ------------- | ------------------------------------------------- |
| chrome.exe                | Direct launch | Works (opens GUI with GCM warnings)               |
| chrome-headless-shell.exe | `--version`   | Works: "Google Chrome for Testing 142.0.7444.162" |

**Conclusion:** The Chrome executables work when launched directly, but fail when launched by Puppeteer.

## Current Server Configuration

From `renderer/server.js` (lines 88-93):

```javascript
browser = await puppeteer.launch({
  headless: "new",
  args: isDocker ? ["--no-sandbox", "--disable-setuid-sandbox"] : [],
});
```

**Issue:** The `args` array is empty on Windows (non-Docker), but Windows may require sandbox flags or other arguments.

## Potential Fixes to Investigate

### 1. Add Windows-Specific Launch Args

```javascript
const isWindows = process.platform === "win32";
browser = await puppeteer.launch({
  headless: "new",
  args:
    isDocker || isWindows
      ? [
          "--no-sandbox",
          "--disable-setuid-sandbox",
          "--disable-dev-shm-usage",
          "--disable-gpu",
        ]
      : [],
});
```

### 2. Use chrome-headless-shell Explicitly

Puppeteer 24.x uses `chrome-headless-shell` by default for headless mode. Verify this is being used:

```javascript
browser = await puppeteer.launch({
  headless: true, // or 'shell' for explicit chrome-headless-shell
  args: ["--no-sandbox"],
});
```

### 3. Check Puppeteer Permissions

The user cache directory permissions may prevent Chrome from accessing required files:

```bash
icacls "C:\Users\Administrator\.cache\puppeteer" /T
```

### 4. Reinstall Puppeteer Browsers

```bash
cd renderer
npx puppeteer browsers uninstall chrome
npx puppeteer browsers install chrome
```

### 5. Try Older Puppeteer Version

Puppeteer 24.x is very recent. Try downgrading:

```bash
npm install puppeteer@22.0.0
```

### 6. Use System Chrome

Point Puppeteer to a system-installed Chrome:

```javascript
browser = await puppeteer.launch({
  headless: "new",
  executablePath: "C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe",
  args: ["--no-sandbox"],
});
```

## Files Affected

- `renderer/server.js` - Browser launch configuration
- `renderer/package.json` - Puppeteer version

## Test Commands

```bash
# Run only renderer tests
cd .worktrees/md2pdf-skill
PYTHONPATH=. pytest tests/test_renderer_client.py -v

# Test renderer directly
curl -X POST http://localhost:3000/render/pdf \
  -H "Content-Type: application/json" \
  -d '{"html": "<html><body><h1>Test</h1></body></html>"}'

# Check Puppeteer browsers
cd renderer && npx puppeteer browsers list
```

## References

- Puppeteer Troubleshooting: https://pptr.dev/troubleshooting
- Windows sandbox issues: https://github.com/puppeteer/puppeteer/issues/1837
- Chrome headless on Windows: https://github.com/nicekiwi/puppeteer-on-windows

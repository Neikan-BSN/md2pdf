# Gemini Recommendations Automation

Automated workflow for capturing and dispositioning Gemini Code Assist review comments.

## Overview

Two scripts work together to streamline Gemini recommendation management:

1. **`capture_gemini_recommendations.py`** - Fetch Gemini review comments from a PR
2. **`disposition_gemini_recommendations.py`** - Interactive review and disposition

## Workflow

### Step 1: Capture Recommendations from PR

When Gemini Code Assist reviews a PR, capture the recommendations:

```bash
# From workspace root
python workspace-infrastructure/scripts/capture_gemini_recommendations.py <PR_NUMBER>

# Example: Capture recommendations from PR #23
python workspace-infrastructure/scripts/capture_gemini_recommendations.py 23
```

**What it does:**
- Fetches all Gemini bot review comments from the specified PR
- Extracts severity levels (HIGH, MEDIUM, LOW)
- Appends to `.user/nursing-consolidation/gemini-recommendations.md`
- Adds items under "Not Addressed (Needs Review)" section
- Groups by PR number
- Avoids duplicates (warns if PR already has items)

**Output:**
```
📥 Fetching Gemini review comments for PR #23...
   Found 4 Gemini comments
   Severity breakdown: HIGH=1, MEDIUM=3, LOW=0
✅ Added 4 recommendations for PR #23
   File: /home/user01/projects/.user/nursing-consolidation/gemini-recommendations.md
```

### Step 2: Review and Disposition

Interactively review all "Not Addressed" recommendations:

```bash
# Review ALL pending recommendations
python workspace-infrastructure/scripts/disposition_gemini_recommendations.py

# Review recommendations for specific PR only
python workspace-infrastructure/scripts/disposition_gemini_recommendations.py --pr 23
```

**Interactive prompts:**

For each recommendation, you'll see:
```
================================================================================
PR #23 - Item 1
================================================================================

**[HIGH]** The logic for detecting which component's documentation needs...
  - File: `.githooks/pre-commit:228`

Disposition Options:
  [I] Implement - Approved for implementation
  [D] Defer - Defer to future phase
  [R] Reject - YAGNI / Over-engineering / Not applicable
  [A] Already Implemented - Feature already exists
  [S] Skip - Keep in 'Not Addressed' for now
  [Q] Quit - Stop reviewing and save progress

Your choice [I/D/R/A/S/Q]:
```

**After choosing disposition, you'll be prompted for:**

1. **Rationale** (required) - Why this decision was made
2. **Scope** (optional, for "Implement" only) - What work is involved

**Example interaction:**
```
Your choice [I/D/R/A/S/Q]: I

Rationale (one line, concise):
> Fixes critical bug that causes hook to miss documentation updates

Implementation scope (optional, one line):
> Refactor component detection to use associative arrays

✅ Moved to 'approved' section
```

### Step 3: Review Changes

The script automatically:
- Moves items from "Not Addressed" to appropriate sections
- Adds decision metadata (emoji, rationale, scope)
- Updates "Last Review" date
- Saves changes to file

**Result in gemini-recommendations.md:**
```markdown
## Approved for Implementation

### PR #23
1. ✅ **[HIGH]** The logic for detecting which component's documentation needs...
   **Decision:** IMPLEMENT
   - **Rationale:** Fixes critical bug that causes hook to miss documentation updates
   - **Scope:** Refactor component detection to use associative arrays
   - File: `.githooks/pre-commit:228`
```

## File Structure

**`.user/nursing-consolidation/gemini-recommendations.md`** sections:

1. **Not Addressed (Needs Review)** - Newly captured, awaiting disposition
2. **Already Implemented** - Feature already exists in codebase
3. **Approved for Implementation** - Approved, will be implemented
4. **Deferred to Phase C** - Good idea, but not now
5. **Rejected (YAGNI / Over-Engineering)** - Won't implement

## Advanced Usage

### Batch Processing

Review all pending recommendations in one session:
```bash
python workspace-infrastructure/scripts/disposition_gemini_recommendations.py
```

The script will:
- Show total count across all PRs
- Process each PR's items sequentially
- Allow you to quit anytime (saves progress)
- Track dispositioned vs. skipped counts

### PR-Specific Review

Focus on a single PR's recommendations:
```bash
python workspace-infrastructure/scripts/disposition_gemini_recommendations.py --pr 23
```

### Skip vs. Quit

- **Skip [S]**: Keep item in "Not Addressed", continue to next item
- **Quit [Q]**: Stop review, save all dispositioned items, exit

This allows you to:
1. Quickly disposition the obvious items
2. Skip complex items for later review
3. Quit when you need a break
4. Resume later with another run

## Integration with Git Workflow

**Recommended workflow after PR review:**

```bash
# 1. Capture Gemini recommendations
python workspace-infrastructure/scripts/capture_gemini_recommendations.py 23

# 2. Review and disposition
python workspace-infrastructure/scripts/disposition_gemini_recommendations.py --pr 23

# 3. If implementing any recommendations, create tracking issue/PR
# (Use "Approved for Implementation" section as spec)

# 4. Update gemini-recommendations.md as work progresses
# (Move from "Approved" to "Already Implemented" when done)
```

## Error Handling

**Duplicate PR detection:**
```
⚠️  PR #23 already has recommendations in file.
   Please review and disposition existing items first.
```
→ Run `disposition_gemini_recommendations.py --pr 23` to clear existing items

**No Gemini comments found:**
```
ℹ️  No Gemini review comments found for PR #23
```
→ Gemini hasn't reviewed this PR yet, or all comments were resolved

**GitHub API errors:**
```
❌ Error running gh command: ...
```
→ Ensure `gh` CLI is installed and authenticated: `gh auth status`

## Examples

### Example 1: Quick Capture and Review

```bash
# After PR #24 gets Gemini review
$ python workspace-infrastructure/scripts/capture_gemini_recommendations.py 24
📥 Fetching Gemini review comments for PR #24...
   Found 3 Gemini comments
   Severity breakdown: HIGH=0, MEDIUM=2, LOW=1
✅ Added 3 recommendations for PR #24

# Review immediately
$ python workspace-infrastructure/scripts/disposition_gemini_recommendations.py --pr 24
# [Interactive session...]
📊 Review Complete!
   Dispositioned: 2
   Skipped: 1
💾 Saving changes...
```

### Example 2: Bulk Review Across Multiple PRs

```bash
# Accumulated recommendations from PRs #21, #22, #23
$ python workspace-infrastructure/scripts/disposition_gemini_recommendations.py

📋 Found 15 recommendations across 3 PRs

================================================================================
Reviewing PR #21 (5 items)
================================================================================
# [Interactive review of all PR #21 items...]

================================================================================
Reviewing PR #22 (6 items)
================================================================================
# [Interactive review continues...]

# User decides to take a break
Your choice [I/D/R/A/S/Q]: Q

💾 Saving progress...
   Dispositioned: 8
   Skipped: 3
```

## Dependencies

- Python 3.11+
- `gh` CLI (GitHub CLI) - authenticated with repo access
- Repository: `Neikan-BSN/projects`

## Troubleshooting

**Script can't find gemini-recommendations.md:**
- Ensure file exists at `.user/nursing-consolidation/gemini-recommendations.md`
- Script creates file if missing (first run only)

**Can't parse recommendations:**
- Gemini comment format may have changed
- Check `extract_recommendation()` function in capture script
- File an issue with example comment JSON

**Items not moving to correct section:**
- Check section headers match exactly (case-sensitive)
- Ensure file format hasn't been manually modified
- Verify no duplicate section headers

## Future Enhancements

Potential improvements:
- [ ] Auto-detect already implemented (scan commits since review)
- [ ] Integration with GitHub issues (create tracking issues)
- [ ] Summary report generation (by severity, by disposition)
- [ ] Email/Slack notifications for new recommendations
- [ ] CLI argument to show statistics without reviewing

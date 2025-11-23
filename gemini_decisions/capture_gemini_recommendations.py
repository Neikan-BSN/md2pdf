#!/usr/bin/env python3
"""
Capture Gemini Code Review Recommendations

Fetches Gemini code review comments from a GitHub PR and appends them
to .user/nursing-consolidation/gemini-recommendations.md in the
"Not Addressed (Needs Review)" section.

Usage:
    python capture_gemini_recommendations.py <pr_number>
    python capture_gemini_recommendations.py 23
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


def run_gh_command(args: list[str]) -> dict[str, Any] | list[Any]:
    """Run gh CLI command and return JSON output."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def fetch_gemini_review_comments(pr_number: int) -> list[dict[str, Any]]:
    """Fetch Gemini code review comments from a PR."""
    comments = run_gh_command([
        "api",
        f"repos/Neikan-BSN/projects/pulls/{pr_number}/comments",
    ])

    # Filter for Gemini bot comments only
    gemini_comments = [
        c for c in comments
        if c["user"]["login"] == "gemini-code-assist[bot]"
    ]

    return gemini_comments


def parse_severity(comment_body: str) -> str:
    """Extract severity level from comment body."""
    if "high" in comment_body.lower():
        return "HIGH"
    elif "medium" in comment_body.lower():
        return "MEDIUM"
    elif "low" in comment_body.lower():
        return "LOW"
    return "UNSPECIFIED"


def extract_recommendation(comment: dict[str, Any]) -> dict[str, str]:
    """Extract recommendation details from comment."""
    body = comment["body"]

    # Remove severity badge markup
    body = body.replace("![high](https://www.gstatic.com/codereviewagent/high-priority.svg)", "")
    body = body.replace("![medium](https://www.gstatic.com/codereviewagent/medium-priority.svg)", "")
    body = body.replace("![low](https://www.gstatic.com/codereviewagent/low-priority.svg)", "")

    # Remove suggestion blocks (code suggestions)
    lines = body.split("\n")
    cleaned_lines = []
    in_suggestion = False
    for line in lines:
        if line.strip().startswith("```suggestion"):
            in_suggestion = True
        elif line.strip() == "```" and in_suggestion:
            in_suggestion = False
        elif not in_suggestion:
            cleaned_lines.append(line)

    body = "\n".join(cleaned_lines).strip()

    return {
        "severity": parse_severity(comment["body"]),
        "body": body,
        "file": comment.get("path", "Unknown"),
        "line": comment.get("line", 0),
    }


def append_to_recommendations(
    pr_number: int,
    recommendations: list[dict[str, str]],
    recommendations_file: Path,
) -> None:
    """Append recommendations to gemini-recommendations.md."""

    # Read existing content
    if recommendations_file.exists():
        content = recommendations_file.read_text()
    else:
        content = """# Gemini Recommendations by PR

**Last Review:** {date}
**Reviewer:** Claude Code Review Agent

---

## Not Addressed (Needs Review)

---

## Already Implemented (No Action Required)

---

## Approved for Implementation

---

## Deferred to Phase C

---

## Rejected (YAGNI / Over-Engineering)

---

## Implementation Status
""".format(date=datetime.now().strftime("%Y-%m-%d"))

    # Find or create PR section in "Not Addressed"
    pr_section = f"### PR #{pr_number}"

    # Check if recommendations already exist (avoid duplicates)
    if pr_section in content:
        print(f"⚠️  PR #{pr_number} already has recommendations in file.")
        print("   Please review and disposition existing items first.")
        return

    # Find insertion point (after "## Not Addressed (Needs Review)")
    lines = content.split("\n")
    insertion_idx = None

    for i, line in enumerate(lines):
        if line.strip() == "## Not Addressed (Needs Review)":
            # Find next blank line after header
            for j in range(i + 1, len(lines)):
                if lines[j].strip() == "":
                    insertion_idx = j + 1
                    break
            break

    if insertion_idx is None:
        print("❌ Could not find 'Not Addressed' section in file")
        return

    # Build new section
    new_section = [f"\n{pr_section}\n"]
    for i, rec in enumerate(recommendations, 1):
        severity_marker = f"**[{rec['severity']}]** " if rec['severity'] != "UNSPECIFIED" else ""
        new_section.append(f"{i}. {severity_marker}{rec['body']}")
        new_section.append(f"   - File: `{rec['file']}:{rec['line']}`")
        new_section.append("")

    # Insert new section
    lines[insertion_idx:insertion_idx] = new_section

    # Update last review date
    for i, line in enumerate(lines):
        if line.startswith("**Last Review:**"):
            lines[i] = f"**Last Review:** {datetime.now().strftime('%Y-%m-%d')}"
            break

    # Write back
    recommendations_file.write_text("\n".join(lines))
    print(f"✅ Added {len(recommendations)} recommendations for PR #{pr_number}")
    print(f"   File: {recommendations_file}")


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python capture_gemini_recommendations.py <pr_number>")
        sys.exit(1)

    pr_number = int(sys.argv[1])

    print(f"📥 Fetching Gemini review comments for PR #{pr_number}...")

    try:
        comments = fetch_gemini_review_comments(pr_number)

        if not comments:
            print(f"ℹ️  No Gemini review comments found for PR #{pr_number}")
            return

        print(f"   Found {len(comments)} Gemini comments")

        # Parse recommendations
        recommendations = [extract_recommendation(c) for c in comments]

        # Group by severity
        high = [r for r in recommendations if r["severity"] == "HIGH"]
        medium = [r for r in recommendations if r["severity"] == "MEDIUM"]
        low = [r for r in recommendations if r["severity"] == "LOW"]

        print(f"   Severity breakdown: HIGH={len(high)}, MEDIUM={len(medium)}, LOW={len(low)}")

        # Determine file path
        workspace_root = Path(__file__).parent.parent.parent
        recommendations_file = workspace_root / ".user" / "nursing-consolidation" / "gemini-recommendations.md"

        # Append to file
        append_to_recommendations(pr_number, recommendations, recommendations_file)

    except subprocess.CalledProcessError as e:
        print(f"❌ Error running gh command: {e}")
        print(f"   Stdout: {e.stdout}")
        print(f"   Stderr: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

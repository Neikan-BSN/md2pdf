#!/usr/bin/env python3
"""
Analyze Gemini Code Review Recommendations

Fetches Gemini code review comments from a GitHub PR and outputs them
in a format optimized for Claude Code to analyze and provide disposition
recommendations.

This script is meant to be run as part of an interactive Claude Code session
where Claude will evaluate each recommendation and provide disposition advice.

Usage:
    python analyze_gemini_recommendations.py <pr_number>
    python analyze_gemini_recommendations.py 1
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# Repository configuration
GITHUB_REPO = "Neikan-BSN/md2pdf"


def run_gh_command(args: list[str]) -> dict[str, Any] | list[Any]:
    """Run gh CLI command and return JSON output."""
    result = subprocess.run(
        ["gh"] + args,
        capture_output=True,
        text=True,
        check=True,
    )
    return json.loads(result.stdout)


def fetch_pr_context(pr_number: int) -> dict[str, Any]:
    """Fetch PR metadata for context."""
    pr = run_gh_command([
        "api",
        f"repos/{GITHUB_REPO}/pulls/{pr_number}",
    ])
    return {
        "number": pr_number,
        "title": pr["title"],
        "state": pr["state"],
        "body": pr["body"][:500] if pr.get("body") else "",  # First 500 chars
        "created_at": pr["created_at"],
        "files_changed": pr.get("changed_files", 0),
    }


def fetch_gemini_review_comments(pr_number: int) -> list[dict[str, Any]]:
    """Fetch Gemini code review comments from a PR."""
    comments = run_gh_command([
        "api",
        f"repos/{GITHUB_REPO}/pulls/{pr_number}/comments",
    ])

    # Filter for Gemini bot comments only
    gemini_comments = [
        c for c in comments
        if c["user"]["login"] == "gemini-code-assist[bot]"
    ]

    return gemini_comments


def fetch_gemini_review_summary(pr_number: int) -> str:
    """Fetch overall review comment from Gemini."""
    reviews = run_gh_command([
        "api",
        f"repos/{GITHUB_REPO}/pulls/{pr_number}/reviews",
    ])

    for review in reviews:
        if review["user"]["login"] == "gemini-code-assist[bot]":
            return review.get("body", "")

    return ""


def fetch_gemini_issue_comments(pr_number: int) -> list[dict[str, Any]]:
    """
    Fetch Gemini issue comments (the complete review summary).

    These are different from PR review comments (inline code comments).
    Issue comments contain the overall review with all issues and recommendations.

    Gemini reviews can be posted by:
    - gemini-code-assist[bot] (direct Gemini bot)
    - github-actions[bot] (Gemini Code Review GitHub Action)
    """
    comments = run_gh_command([
        "api",
        f"repos/{GITHUB_REPO}/issues/{pr_number}/comments",
    ])

    # Filter for Gemini-related comments
    gemini_comments = []
    for c in comments:
        login = c["user"]["login"].lower()
        body = c.get("body", "")

        # Check if it's from Gemini bot or GitHub Actions posting Gemini review
        is_gemini_bot = "gemini" in login or "google" in login
        is_gemini_action = "github-actions" in login and "Gemini Code Review" in body

        if is_gemini_bot or is_gemini_action:
            gemini_comments.append(c)

    return gemini_comments


def parse_severity(comment_body: str) -> str:
    """Extract severity level from comment body."""
    body_lower = comment_body.lower()
    if "![high]" in body_lower or "high-priority" in body_lower:
        return "HIGH"
    elif "![medium]" in body_lower or "medium-priority" in body_lower:
        return "MEDIUM"
    elif "![low]" in body_lower or "low-priority" in body_lower:
        return "LOW"
    return "UNSPECIFIED"


def clean_comment_body(body: str) -> str:
    """Remove markup and extract core recommendation text."""
    # Remove severity badges
    body = body.replace("![high](https://www.gstatic.com/codereviewagent/high-priority.svg)", "")
    body = body.replace("![medium](https://www.gstatic.com/codereviewagent/medium-priority.svg)", "")
    body = body.replace("![low](https://www.gstatic.com/codereviewagent/low-priority.svg)", "")

    # Split by suggestion blocks
    lines = body.split("\n")
    recommendation = []
    suggestion = []
    in_suggestion = False

    for line in lines:
        if line.strip().startswith("```suggestion"):
            in_suggestion = True
            suggestion = []
        elif line.strip() == "```" and in_suggestion:
            in_suggestion = False
        elif in_suggestion:
            suggestion.append(line)
        else:
            recommendation.append(line)

    return {
        "recommendation": "\n".join(recommendation).strip(),
        "suggested_code": "\n".join(suggestion).strip() if suggestion else None,
    }


def format_for_claude_analysis(
    pr_context: dict[str, Any],
    review_summary: str,
    issue_comments: list[dict[str, Any]],
    inline_comments: list[dict[str, Any]]
) -> str:
    """Format recommendations in a way that's easy for Claude to analyze."""

    output = []

    # PR Context
    output.append("# Gemini Code Review Analysis Request")
    output.append("")
    output.append(f"**PR #{pr_context['number']}: {pr_context['title']}**")
    output.append("")
    output.append("## PR Context")
    output.append("")
    output.append(f"- **Status:** {pr_context['state']}")
    output.append(f"- **Files Changed:** {pr_context['files_changed']}")
    output.append(f"- **Created:** {pr_context['created_at']}")
    output.append("")
    if pr_context['body']:
        output.append("**PR Description (excerpt):**")
        output.append(f"> {pr_context['body']}")
        output.append("")

    # Issue Comments (Complete Review)
    if issue_comments:
        output.append("## Gemini's Complete Review")
        output.append("")
        output.append("**Source:** Issue comments (complete review with all issues/recommendations)")
        output.append("")
        for comment in issue_comments:
            output.append(comment["body"])
            output.append("")

    # Review Summary
    if review_summary:
        output.append("## Gemini's Overall Review")
        output.append("")
        output.append("**Source:** PR review summary")
        output.append("")
        output.append(review_summary)
        output.append("")

    # Individual Inline Recommendations (if any)
    if inline_comments:
        output.append("## Inline Code Recommendations")
        output.append("")
        output.append("**Source:** PR review inline comments")
        output.append("")
        output.append(f"**Total:** {len(inline_comments)} inline recommendations")
        output.append("")

        # Group by severity
        high = [c for c in inline_comments if parse_severity(c["body"]) == "HIGH"]
        medium = [c for c in inline_comments if parse_severity(c["body"]) == "MEDIUM"]
        low = [c for c in inline_comments if parse_severity(c["body"]) == "LOW"]

        output.append(f"**Severity Breakdown:** HIGH={len(high)}, MEDIUM={len(medium)}, LOW={len(low)}")
        output.append("")
        output.append("---")
        output.append("")

        # Output each recommendation
        for i, comment in enumerate(inline_comments, 1):
            severity = parse_severity(comment["body"])
            cleaned = clean_comment_body(comment["body"])

            output.append(f"### Inline Recommendation {i} [{severity}]")
            output.append("")
            output.append(f"**Location:** `{comment.get('path', 'N/A')}:{comment.get('line', 'N/A')}`")
            output.append("")
            output.append("**Gemini's Feedback:**")
            output.append("")
            output.append(cleaned["recommendation"])
            output.append("")

            if cleaned["suggested_code"]:
                output.append("**Suggested Code Change:**")
                output.append("```")
                output.append(cleaned["suggested_code"])
                output.append("```")
                output.append("")

            output.append("---")
            output.append("")

    # Analysis prompt for Claude
    output.append("## Analysis Request")
    output.append("")
    output.append("For each recommendation above, please provide:")
    output.append("")
    output.append("1. **Your Evaluation:**")
    output.append("   - Technical validity of the recommendation")
    output.append("   - Relevance to current phase/goals")
    output.append("   - Alignment with project architecture decisions")
    output.append("")
    output.append("2. **Disposition Recommendation:**")
    output.append("   - **IMPLEMENT** - Valid, should be implemented now or soon")
    output.append("   - **DEFER** - Valid, but defer to future phase")
    output.append("   - **REJECT** - YAGNI, over-engineering, or conflicts with design")
    output.append("   - **ALREADY_IMPLEMENTED** - Feature/fix already exists")
    output.append("")
    output.append("3. **Rationale:** One-sentence reasoning for your recommendation")
    output.append("")
    output.append("4. **Scope** (if IMPLEMENT): Brief description of implementation work")
    output.append("")
    output.append("Format your response as structured recommendations that we can directly")
    output.append("transfer to the decision record (.user/gemini-decisions/gemini-recommendations.md).")

    return "\n".join(output)


def main():
    """Main entry point."""
    if len(sys.argv) != 2:
        print("Usage: python analyze_gemini_recommendations.py <pr_number>")
        sys.exit(1)

    pr_number = int(sys.argv[1])

    print(f"Fetching Gemini review for PR #{pr_number}...")

    try:
        # Fetch data
        pr_context = fetch_pr_context(pr_number)
        review_summary = fetch_gemini_review_summary(pr_number)
        issue_comments = fetch_gemini_issue_comments(pr_number)
        inline_comments = fetch_gemini_review_comments(pr_number)

        # Check if we have any Gemini feedback
        if not issue_comments and not inline_comments and not review_summary:
            print(f"No Gemini review found for PR #{pr_number}")
            print("   Either Gemini hasn't reviewed this PR yet, or all comments were resolved.")
            sys.exit(0)

        # Report what we found
        found_items = []
        if issue_comments:
            found_items.append(f"{len(issue_comments)} issue comment(s)")
        if inline_comments:
            found_items.append(f"{len(inline_comments)} inline comment(s)")
        if review_summary:
            found_items.append("review summary")

        print(f"Found Gemini review: {', '.join(found_items)}")
        print("")

        # Format for Claude analysis
        analysis_request = format_for_claude_analysis(
            pr_context, review_summary, issue_comments, inline_comments
        )

        # Output to stdout for Claude to read
        print(analysis_request)

        # Save to temp file for easy reference
        workspace_root = Path(__file__).parent.parent
        temp_file = workspace_root / ".user" / "gemini-decisions" / f"gemini-review-pr{pr_number}.md"
        temp_file.parent.mkdir(parents=True, exist_ok=True)
        temp_file.write_text(analysis_request)

        print("")
        print(f"Analysis request saved to: {temp_file}")
        print("")
        print("Next step: Review the recommendations above and provide your disposition analysis.")

    except subprocess.CalledProcessError as e:
        print(f"Error running gh command: {e}")
        print(f"   Stdout: {e.stdout}")
        print(f"   Stderr: {e.stderr}")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

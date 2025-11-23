#!/usr/bin/env python3
"""
Record Gemini Recommendation Decisions

Takes structured decision data (from Claude's analysis) and updates
the gemini-recommendations.md file with the dispositions.

This script is designed to work with Claude Code - Claude analyzes
recommendations and outputs structured decisions, which this script
records to the decision log.

Usage:
    python record_gemini_decisions.py <pr_number> <decisions_file>

    Where decisions_file is a JSON file with structure:
    {
        "pr_number": 23,
        "decisions": [
            {
                "number": 1,
                "recommendation": "Fix multiple component detection...",
                "severity": "HIGH",
                "disposition": "IMPLEMENT",
                "rationale": "Critical bug causing hook to miss updates",
                "scope": "Refactor to use associative arrays",
                "file": ".githooks/pre-commit",
                "line": 228
            },
            ...
        ]
    }
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Any


class DecisionRecorder:
    """Records disposition decisions to gemini-recommendations.md."""

    SECTION_HEADERS = {
        "IMPLEMENT": "## Approved for Implementation",
        "DEFER": "## Deferred to Phase C",
        "REJECT": "## Rejected (YAGNI / Over-Engineering)",
        "ALREADY_IMPLEMENTED": "## Already Implemented (No Action Required)",
    }

    SECTION_EMOJI = {
        "IMPLEMENT": "✅",
        "DEFER": "⚠️",
        "REJECT": "❌",
        "ALREADY_IMPLEMENTED": "✅",
    }

    def __init__(self, recommendations_file: Path):
        self.recommendations_file = recommendations_file
        if recommendations_file.exists():
            self.content = recommendations_file.read_text()
            self.lines = self.content.split("\n")
        else:
            # Create initial file structure
            self.lines = self._create_initial_structure()

    def _create_initial_structure(self) -> list[str]:
        """Create initial file structure if file doesn't exist."""
        return [
            "# Gemini Recommendations by PR",
            "",
            f"**Last Review:** {datetime.now().strftime('%Y-%m-%d')}",
            "**Reviewer:** Claude Code Review Agent",
            "",
            "---",
            "",
            "## Not Addressed (Needs Review)",
            "",
            "---",
            "",
            "## Already Implemented (No Action Required)",
            "",
            "---",
            "",
            "## Approved for Implementation",
            "",
            "---",
            "",
            "## Deferred to Phase C",
            "",
            "---",
            "",
            "## Rejected (YAGNI / Over-Engineering)",
            "",
            "---",
            "",
            "## Implementation Status",
            "",
        ]

    def _find_section_insertion_point(self, section_header: str, pr_number: int) -> int:
        """Find where to insert items for a given section and PR."""
        # Find the section
        section_idx = None
        for i, line in enumerate(self.lines):
            if line.strip() == section_header:
                section_idx = i
                break

        if section_idx is None:
            raise ValueError(f"Section not found: {section_header}")

        # Look for existing PR subsection
        pr_header = f"### PR #{pr_number}"
        for i in range(section_idx + 1, len(self.lines)):
            if self.lines[i].strip() == pr_header:
                # Found existing PR section, insert after existing items
                for j in range(i + 1, len(self.lines)):
                    if self.lines[j].startswith("###") or self.lines[j].startswith("##"):
                        return j
                return len(self.lines)  # End of file

            elif self.lines[i].startswith("##"):
                # Hit next section without finding PR, insert here
                return i

        # Reached end without finding anything
        return len(self.lines)

    def record_decisions(self, pr_number: int, decisions: list[dict[str, Any]]) -> None:
        """Record all decisions for a PR."""
        # Group by disposition
        by_disposition = {}
        for decision in decisions:
            disposition = decision["disposition"]
            if disposition not in by_disposition:
                by_disposition[disposition] = []
            by_disposition[disposition].append(decision)

        # Add to each section
        for disposition, items in by_disposition.items():
            section_header = self.SECTION_HEADERS[disposition]
            emoji = self.SECTION_EMOJI[disposition]

            # Find insertion point
            insertion_idx = self._find_section_insertion_point(section_header, pr_number)

            # Build content to insert
            new_lines = []

            # Add PR header if this is first item in section for this PR
            pr_header = f"### PR #{pr_number}"
            needs_header = True
            if insertion_idx > 0:
                # Check if previous non-empty line is our PR header
                for i in range(insertion_idx - 1, -1, -1):
                    if self.lines[i].strip():
                        if self.lines[i].strip() == pr_header:
                            needs_header = False
                        break

            if needs_header:
                new_lines.append("")
                new_lines.append(pr_header)

            # Add each decision
            for item in items:
                new_lines.append(f"{item['number']}. {emoji} **[{item['severity']}]** {item['recommendation']}")
                new_lines.append(f"   **Decision:** {disposition}")
                new_lines.append(f"   - **Rationale:** {item['rationale']}")
                if item.get('scope'):
                    new_lines.append(f"   - **Scope:** {item['scope']}")
                if item.get('file'):
                    new_lines.append(f"   - **File:** `{item['file']}:{item.get('line', 'N/A')}`")
                new_lines.append("")

            # Insert
            self.lines[insertion_idx:insertion_idx] = new_lines

        # Update last review date
        for i, line in enumerate(self.lines):
            if line.startswith("**Last Review:**"):
                self.lines[i] = f"**Last Review:** {datetime.now().strftime('%Y-%m-%d')}"
                break

    def save(self) -> None:
        """Save changes to file."""
        self.recommendations_file.write_text("\n".join(self.lines))


def main():
    """Main entry point."""
    if len(sys.argv) != 3:
        print("Usage: python record_gemini_decisions.py <pr_number> <decisions_file>")
        sys.exit(1)

    pr_number = int(sys.argv[1])
    decisions_file = Path(sys.argv[2])

    if not decisions_file.exists():
        print(f"❌ Decisions file not found: {decisions_file}")
        sys.exit(1)

    print(f"📝 Recording decisions for PR #{pr_number}...")

    try:
        # Load decisions
        with open(decisions_file) as f:
            data = json.load(f)

        decisions = data.get("decisions", [])

        if not decisions:
            print("⚠️  No decisions found in file")
            sys.exit(0)

        # Determine file path
        workspace_root = Path(__file__).parent.parent.parent
        recommendations_file = (
            workspace_root / ".user" / "nursing-consolidation" / "gemini-recommendations.md"
        )

        # Record decisions
        recorder = DecisionRecorder(recommendations_file)
        recorder.record_decisions(pr_number, decisions)
        recorder.save()

        # Summary
        by_disposition = {}
        for d in decisions:
            disposition = d["disposition"]
            by_disposition[disposition] = by_disposition.get(disposition, 0) + 1

        print(f"✅ Recorded {len(decisions)} decisions:")
        for disposition, count in sorted(by_disposition.items()):
            print(f"   - {disposition}: {count}")

        print(f"\n📄 Updated: {recommendations_file}")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()

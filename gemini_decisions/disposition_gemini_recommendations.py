#!/usr/bin/env python3
"""
Interactive Disposition of Gemini Recommendations

Reviews "Not Addressed" Gemini recommendations and allows the user to
disposition them in aggregate (Implement, Defer, Reject, Already Implemented).

Usage:
    python disposition_gemini_recommendations.py
    python disposition_gemini_recommendations.py --pr 23
"""

import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class RecommendationDispositioner:
    """Interactive tool for dispositioning Gemini recommendations."""

    SECTIONS = {
        "not_addressed": "## Not Addressed (Needs Review)",
        "already_implemented": "## Already Implemented (No Action Required)",
        "approved": "## Approved for Implementation",
        "deferred": "## Deferred to Phase C",
        "rejected": "## Rejected (YAGNI / Over-Engineering)",
    }

    def __init__(self, recommendations_file: Path):
        self.recommendations_file = recommendations_file
        self.content = recommendations_file.read_text()
        self.lines = self.content.split("\n")

    def parse_not_addressed_items(
        self, pr_filter: Optional[int] = None
    ) -> dict[str, list[dict]]:
        """Parse all items in 'Not Addressed' section."""
        items_by_pr = {}
        current_pr = None
        current_item = None
        in_section = False

        for i, line in enumerate(self.lines):
            # Detect section boundaries
            if line.strip() == self.SECTIONS["not_addressed"]:
                in_section = True
                continue
            elif line.startswith("##") and in_section:
                # End of Not Addressed section
                break

            if not in_section:
                continue

            # Detect PR subsection
            pr_match = re.match(r"^### PR #(\d+)", line)
            if pr_match:
                current_pr = int(pr_match.group(1))
                if pr_filter is None or current_pr == pr_filter:
                    items_by_pr[current_pr] = []
                else:
                    current_pr = None
                continue

            if current_pr is None:
                continue

            # Detect recommendation item
            item_match = re.match(r"^(\d+)\.\s+(.+)", line)
            if item_match:
                # Save previous item if exists
                if current_item:
                    items_by_pr[current_pr].append(current_item)

                # Start new item
                item_num = int(item_match.group(1))
                body = item_match.group(2)
                current_item = {
                    "pr": current_pr,
                    "number": item_num,
                    "body": body,
                    "details": [],
                    "start_line": i,
                    "end_line": i,
                }
            elif current_item and line.strip().startswith("-"):
                # Additional details for current item
                current_item["details"].append(line.strip())
                current_item["end_line"] = i
            elif current_item and not line.strip():
                # End of current item
                current_item["end_line"] = i
                items_by_pr[current_pr].append(current_item)
                current_item = None

        # Add final item if exists
        if current_item:
            items_by_pr[current_pr].append(current_item)

        return items_by_pr

    def get_disposition_choice(self, item: dict) -> tuple[str, str]:
        """Prompt user for disposition choice."""
        print("\n" + "=" * 80)
        print(f"PR #{item['pr']} - Item {item['number']}")
        print("=" * 80)
        print(f"\n{item['body']}")
        for detail in item["details"]:
            print(f"  {detail}")

        print("\n\nDisposition Options:")
        print("  [I] Implement - Approved for implementation")
        print("  [D] Defer - Defer to future phase")
        print("  [R] Reject - YAGNI / Over-engineering / Not applicable")
        print("  [A] Already Implemented - Feature already exists")
        print("  [S] Skip - Keep in 'Not Addressed' for now")
        print("  [Q] Quit - Stop reviewing and save progress")

        while True:
            choice = input("\nYour choice [I/D/R/A/S/Q]: ").strip().upper()

            if choice in ["I", "D", "R", "A", "S", "Q"]:
                break
            print("Invalid choice. Please enter I, D, R, A, S, or Q.")

        if choice == "Q":
            return "QUIT", ""

        if choice == "S":
            return "SKIP", ""

        # Get rationale for non-skip choices
        print("\nRationale (one line, concise):")
        rationale = input("> ").strip()

        # Get scope for implementation items
        scope = ""
        if choice == "I":
            print("\nImplementation scope (optional, one line):")
            scope = input("> ").strip()

        # Build decision text
        disposition_map = {
            "I": "IMPLEMENT",
            "D": "DEFER",
            "R": "REJECT",
            "A": "ALREADY_IMPLEMENTED",
        }

        decision_text = f"**Decision:** {disposition_map[choice]}"
        if rationale:
            decision_text += f"\n   - **Rationale:** {rationale}"
        if scope:
            decision_text += f"\n   - **Scope:** {scope}"

        return disposition_map[choice], decision_text

    def move_item_to_section(
        self, item: dict, target_section: str, decision_text: str
    ) -> None:
        """Move item from 'Not Addressed' to target section."""
        # Remove from current location
        del self.lines[item["start_line"] : item["end_line"] + 1]

        # Find target section insertion point
        target_header = self.SECTIONS[target_section]
        insertion_idx = None

        for i, line in enumerate(self.lines):
            if line.strip() == target_header:
                # Find subsection for this PR
                pr_header = f"### PR #{item['pr']}"
                for j in range(i + 1, len(self.lines)):
                    if self.lines[j].strip() == pr_header:
                        # Insert after existing PR items
                        for k in range(j + 1, len(self.lines)):
                            if self.lines[k].startswith("###") or self.lines[k].startswith("##"):
                                insertion_idx = k
                                break
                        if insertion_idx is None:
                            insertion_idx = len(self.lines)
                        break
                    elif self.lines[j].startswith("##"):
                        # No existing PR section, create one
                        insertion_idx = j
                        break

                if insertion_idx is None:
                    # Section exists but no content
                    insertion_idx = i + 2

                break

        if insertion_idx is None:
            print(f"⚠️  Could not find section: {target_header}")
            return

        # Build new item text
        emoji_map = {
            "IMPLEMENT": "✅",
            "DEFER": "⚠️",
            "REJECT": "❌",
            "ALREADY_IMPLEMENTED": "✅",
        }

        new_item = [
            f"\n### PR #{item['pr']}",
            f"{item['number']}. {emoji_map.get(target_section.upper(), '•')} {item['body']}",
        ]

        # Add decision text
        for line in decision_text.split("\n"):
            new_item.append(f"   {line}")

        # Add original details
        for detail in item["details"]:
            new_item.append(f"   {detail}")

        new_item.append("")

        # Insert
        self.lines[insertion_idx:insertion_idx] = new_item

    def save(self) -> None:
        """Save changes to file."""
        # Update last review date
        for i, line in enumerate(self.lines):
            if line.startswith("**Last Review:**"):
                self.lines[i] = f"**Last Review:** {datetime.now().strftime('%Y-%m-%d')}"
                break

        self.recommendations_file.write_text("\n".join(self.lines))

    def review_items(self, pr_filter: Optional[int] = None) -> None:
        """Interactive review of all 'Not Addressed' items."""
        items_by_pr = self.parse_not_addressed_items(pr_filter)

        if not items_by_pr:
            print("✅ No items in 'Not Addressed' section!")
            return

        total_items = sum(len(items) for items in items_by_pr.values())
        print(f"\n📋 Found {total_items} recommendations across {len(items_by_pr)} PRs")

        dispositioned_count = 0
        skipped_count = 0

        for pr, items in sorted(items_by_pr.items()):
            print(f"\n{'='*80}")
            print(f"Reviewing PR #{pr} ({len(items)} items)")
            print(f"{'='*80}")

            for item in items:
                disposition, decision_text = self.get_disposition_choice(item)

                if disposition == "QUIT":
                    print(f"\n💾 Saving progress...")
                    print(f"   Dispositioned: {dispositioned_count}")
                    print(f"   Skipped: {skipped_count}")
                    self.save()
                    return

                if disposition == "SKIP":
                    skipped_count += 1
                    continue

                # Move to appropriate section
                section_map = {
                    "IMPLEMENT": "approved",
                    "DEFER": "deferred",
                    "REJECT": "rejected",
                    "ALREADY_IMPLEMENTED": "already_implemented",
                }

                self.move_item_to_section(item, section_map[disposition], decision_text)
                dispositioned_count += 1
                print(f"✅ Moved to '{section_map[disposition]}' section")

        print(f"\n{'='*80}")
        print(f"📊 Review Complete!")
        print(f"{'='*80}")
        print(f"   Dispositioned: {dispositioned_count}")
        print(f"   Skipped: {skipped_count}")

        if dispositioned_count > 0:
            print(f"\n💾 Saving changes...")
            self.save()
            print(f"   File updated: {self.recommendations_file}")


def main():
    """Main entry point."""
    pr_filter = None
    if len(sys.argv) > 1:
        if sys.argv[1] == "--pr" and len(sys.argv) == 3:
            pr_filter = int(sys.argv[2])
        else:
            print("Usage: python disposition_gemini_recommendations.py [--pr PR_NUMBER]")
            sys.exit(1)

    # Determine file path
    workspace_root = Path(__file__).parent.parent.parent
    recommendations_file = (
        workspace_root / ".user" / "nursing-consolidation" / "gemini-recommendations.md"
    )

    if not recommendations_file.exists():
        print(f"❌ File not found: {recommendations_file}")
        sys.exit(1)

    print("🔍 Interactive Gemini Recommendation Disposition")
    print("=" * 80)

    dispositioner = RecommendationDispositioner(recommendations_file)
    dispositioner.review_items(pr_filter)


if __name__ == "__main__":
    main()

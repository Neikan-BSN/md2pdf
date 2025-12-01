#!/usr/bin/env python3
"""
md2pdf_batch - Non-interactive batch Markdown to PDF/HTML converter

Batch processing CLI for converting multiple markdown files with configurable
settings (format, theme, output directory).
"""

import argparse
import sys
from pathlib import Path
from typing import List, Optional


def parse_args(args=None):
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Convert markdown files to PDF or HTML in batch mode",
        prog="md2pdf_batch"
    )

    parser.add_argument(
        "--files",
        required=True,
        nargs="+",
        help="File paths or glob patterns to convert"
    )

    parser.add_argument(
        "--format",
        default="pdf",
        choices=["pdf", "html"],
        help="Output format (default: pdf)"
    )

    parser.add_argument(
        "--theme",
        default="academic",
        help="Theme name (default: academic)"
    )

    parser.add_argument(
        "--output-mode",
        default="same-dir",
        choices=["same-dir", "custom"],
        help="Output directory mode (default: same-dir)"
    )

    parser.add_argument(
        "--output-dir",
        type=str,
        default=None,
        help="Custom output directory (required if --output-mode is custom)"
    )

    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as JSON for parallel processing"
    )

    return parser.parse_args(args)


def main(args=None):
    """Main entry point for batch conversion CLI."""
    parsed = parse_args(args)

    # Placeholder: validate arguments
    if parsed.output_mode == "custom" and not parsed.output_dir:
        print("Error: --output-dir required when --output-mode is custom", file=sys.stderr)
        return 1

    # Placeholder: actual conversion logic
    print(f"Batch conversion initialized")
    print(f"  Files: {parsed.files}")
    print(f"  Format: {parsed.format}")
    print(f"  Theme: {parsed.theme}")
    print(f"  Output mode: {parsed.output_mode}")
    if parsed.output_dir:
        print(f"  Output dir: {parsed.output_dir}")
    print(f"  JSON output: {parsed.json_output}")

    return 0


if __name__ == "__main__":
    sys.exit(main())

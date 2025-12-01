#!/usr/bin/env python3
"""
md2pdf_batch - Non-interactive batch Markdown to PDF/HTML converter

Batch processing CLI for converting multiple markdown files with configurable
settings (format, theme, output directory).
"""

import argparse
import glob
import json as json_module
import sys
from pathlib import Path
from typing import List, Optional, Dict, Any

from document_builder import build_html_document
from renderer_client import RendererClient
from config_loader import load_config
from theme_manager import list_themes


def resolve_files(patterns: List[str]) -> List[Path]:
    """
    Resolve file patterns to actual file paths.

    Args:
        patterns: List of file paths or glob patterns

    Returns:
        List of resolved Path objects

    Raises:
        FileNotFoundError: If no files found
    """
    resolved = []

    for pattern in patterns:
        path = Path(pattern)

        # Direct file path
        if path.is_file():
            resolved.append(path)
            continue

        # Glob pattern
        matches = glob.glob(pattern, recursive=True)
        files = [Path(m) for m in matches if Path(m).is_file()]

        if not files and not path.is_file():
            raise FileNotFoundError(f"No files found matching: {pattern}")

        resolved.extend(files)

    if not resolved:
        raise FileNotFoundError("No files found")

    return sorted(set(resolved))


def validate_theme(theme: str) -> None:
    """
    Validate theme exists.

    Raises:
        ValueError: If theme not found
    """
    available = list_themes()
    if theme not in available:
        raise ValueError(
            f"Theme '{theme}' not found. Available: {', '.join(available)}"
        )


def convert_file(
    input_file: Path,
    format: str,
    theme: str,
    output_dir: Optional[Path] = None
) -> Dict[str, Any]:
    """
    Convert a single markdown file.

    Args:
        input_file: Path to markdown file
        format: Output format ('pdf' or 'html')
        theme: Theme name
        output_dir: Custom output directory (None = same as input)

    Returns:
        Dict with success, input, output, error keys
    """
    try:
        # Determine output path
        if output_dir:
            output_path = output_dir / f"{input_file.stem}.{format}"
        else:
            output_path = input_file.parent / f"{input_file.stem}.{format}"

        # Read markdown
        md_content = input_file.read_text(encoding="utf-8")

        # Load config
        config = load_config()

        # Build HTML
        html = build_html_document(md_content, theme, config)

        # Convert based on format
        if format == "pdf":
            pdf_opts = config.get("pdf_options", {})
            render_options = {
                "format": pdf_opts.get("page_size", "letter"),
                "printBackground": pdf_opts.get("print_background", True),
                "margin": pdf_opts.get("margins", {
                    "top": "1in", "bottom": "1in",
                    "left": "1in", "right": "1in"
                })
            }

            with RendererClient() as client:
                pdf_bytes = client.render_pdf(html, render_options)

            output_path.write_bytes(pdf_bytes)
        else:
            output_path.write_text(html, encoding="utf-8")

        return {
            "success": True,
            "input": input_file,
            "output": output_path,
            "error": None
        }

    except Exception as e:
        return {
            "success": False,
            "input": input_file,
            "output": None,
            "error": str(e)
        }


def process_batch(
    files: List[Path],
    format: str,
    theme: str,
    output_dir: Optional[Path] = None
) -> List[Dict[str, Any]]:
    """
    Process multiple files sequentially.

    Args:
        files: List of markdown files
        format: Output format
        theme: Theme name
        output_dir: Custom output directory

    Returns:
        List of result dicts from convert_file
    """
    results = []
    for f in files:
        result = convert_file(f, format, theme, output_dir)
        results.append(result)
    return results


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

    try:
        # Validate theme first
        validate_theme(parsed.theme)

        # Resolve files
        files = resolve_files(parsed.files)

        # Determine output directory
        output_dir = Path(parsed.output_dir) if parsed.output_mode == "custom" else None

        # Process files
        results = process_batch(
            files=files,
            format=parsed.format,
            theme=parsed.theme,
            output_dir=output_dir
        )

        # Calculate summary
        success_count = sum(1 for r in results if r["success"])

        # Output results
        if parsed.json_output:
            output = {
                "total": len(results),
                "success": success_count,
                "failed": len(results) - success_count,
                "results": [
                    {
                        "input": str(r["input"]),
                        "output": str(r["output"]) if r["output"] else None,
                        "success": r["success"],
                        "error": r["error"]
                    }
                    for r in results
                ]
            }
            print(json_module.dumps(output, indent=2))
        else:
            # Human-readable output
            print(f"Converted {success_count}/{len(results)} files")
            for r in results:
                status = "+" if r["success"] else "x"
                if r["success"]:
                    print(f"  {status} {r['input'].name} -> {r['output'].name}")
                else:
                    print(f"  {status} {r['input'].name} ({r['error']})")

        return 0 if success_count == len(results) else 1

    except (FileNotFoundError, ValueError) as e:
        if parsed.json_output:
            print(json_module.dumps({"error": str(e)}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())

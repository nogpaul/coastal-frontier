"""Build the Coastal Frontier PDF brief from its Markdown source.

Required system dependencies:
    pandoc       https://pandoc.org/installing.html
    wkhtmltopdf  https://wkhtmltopdf.org/downloads.html

Both have Windows .msi/.exe installers and are available via apt, brew, etc.

Usage:
    python scripts/build_brief.py
"""

from __future__ import annotations

import shutil
import subprocess
import sys
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parent.parent
BRIEF_MD = PROJECT_ROOT / "reports" / "coastal_frontier_brief.md"
BRIEF_PDF = PROJECT_ROOT / "reports" / "coastal_frontier_brief.pdf"
BRIEF_CSS = PROJECT_ROOT / "reports" / "brief_style.css"


def check_dependencies() -> None:
    """Verify pandoc and wkhtmltopdf are installed and discoverable on PATH."""
    missing = [tool for tool in ("pandoc", "wkhtmltopdf") if shutil.which(tool) is None]
    if missing:
        raise SystemExit(
            f"ERROR: required tool(s) not on PATH: {', '.join(missing)}\n"
            f"       Install pandoc and wkhtmltopdf, then re-run.\n"
            f"       See module docstring for installer links."
        )


def build_pdf() -> None:
    """Render the Markdown brief to PDF using pandoc + wkhtmltopdf."""
    if not BRIEF_MD.exists():
        raise SystemExit(f"ERROR: Markdown source not found at {BRIEF_MD}")
    if not BRIEF_CSS.exists():
        raise SystemExit(f"ERROR: CSS stylesheet not found at {BRIEF_CSS}")

    cmd = [
        "pandoc",
        str(BRIEF_MD),
        "--css", str(BRIEF_CSS),
        "--pdf-engine=wkhtmltopdf",
        "--pdf-engine-opt=--enable-local-file-access",
        "--metadata", "title=Coastal Frontier",
        "-o", str(BRIEF_PDF),
    ]

    print(f"Rendering {BRIEF_MD.name} -> {BRIEF_PDF.name} ...")
    result = subprocess.run(cmd, capture_output=True, text=True)

    if result.returncode != 0:
        print("pandoc stderr:\n", result.stderr, file=sys.stderr)
        raise SystemExit(f"PDF build failed (pandoc exit code {result.returncode})")

    size_kb = BRIEF_PDF.stat().st_size / 1024
    print(f"Wrote {BRIEF_PDF.relative_to(PROJECT_ROOT)} ({size_kb:.1f} KB)")


def main() -> None:
    check_dependencies()
    build_pdf()


if __name__ == "__main__":
    main()

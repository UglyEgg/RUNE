#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2025 Richard Majewski <uglyegg@entropy.quest>
# SPDX-License-Identifier: AGPL-3.0

"""
Automate release version bumps by updating CHANGELOG.md, pyproject.toml, and _version.py.

Usage examples:
    python scripts/bump_version.py                # bump patch version
    python scripts/bump_version.py --part minor   # bump minor version
    python scripts/bump_version.py --set 1.2.0    # set explicit version

The script:
1. Calculates the new version based on the previous release entry.
2. Moves "Unreleased" notes into a dated release section.
3. Refreshes comparison links at the bottom of the changelog.
4. Updates the version in pyproject.toml.
5. Updates the version in src/spdx_headers/_version.py.

After running this script, commit the changes and tag the release:
    git commit -am 'Release vX.Y.Z'
    git tag vX.Y.Z
    git push origin main --tags
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import sys
from pathlib import Path
from typing import List, Tuple, Optional

REPO_ROOT = Path(__file__).resolve().parents[1]
CHANGELOG_PATH = REPO_ROOT / "CHANGELOG.md"
VERSION_FILE = REPO_ROOT / "src" / "spdx_headers" / "_version.py"
PYPROJECT_PATH = REPO_ROOT / "pyproject.toml"


def detect_license_info() -> tuple[str, str]:
    """
    Detect license information from multiple sources.

    Returns:
        tuple: (copyright_text, license_identifier)

    Raises:
        SystemExit: If license cannot be detected and no reasonable fallback is available
    """
    # Try to get info from pyproject.toml first
    copyright_text, license_id = _get_license_from_pyproject()

    if not copyright_text or not license_id:
        # Fallback to existing file headers
        alt_copyright, alt_license = _get_license_from_existing_headers()
        copyright_text = copyright_text or alt_copyright
        license_id = license_id or alt_license

    # Generate sensible defaults if still missing
    current_year = dt.datetime.now().year
    if not copyright_text:
        copyright_text = f"SPDX-FileCopyrightText: {current_year} Copyright Holder"

    if not license_id:
        # Cannot detect license - provide helpful error message
        _print_license_detection_error()
        raise SystemExit(
            "Unable to detect license identifier. Please specify a license in pyproject.toml:\n"
            "  [project]\n"
            "  license = { text = &quot;MIT&quot; }  # or your preferred license\n"
            "\n"
            "Or add SPDX headers to your Python files:\n"
            "  # SPDX-FileCopyrightText: 2025 Your Name <your@email.com>\n"
            "  # SPDX-License-Identifier: MIT\n"
        )

    return copyright_text, license_id


def _get_license_from_pyproject() -> tuple[Optional[str], Optional[str]]:
    """Extract license info from pyproject.toml."""
    try:
        import tomllib
    except ImportError:
        # Python < 3.11
        try:
            import tomli as tomllib
        except ImportError:
            return None, None

    try:
        content = PYPROJECT_PATH.read_text(encoding="utf-8")
        data = tomllib.loads(content)

        project = data.get("project", {})

        # Get license identifier
        license_id = None
        license_info = project.get("license", {})
        if isinstance(license_info, dict):
            license_id = license_info.get("text")
        elif isinstance(license_info, str):
            license_id = license_info

        # Get copyright info from authors/maintainers
        copyright_text = None
        current_year = dt.datetime.now().year

        for field in ["authors", "maintainers"]:
            people = project.get(field, [])
            if people and isinstance(people, list):
                person = people[0]  # Use first author/maintainer
                if isinstance(person, dict):
                    name = person.get("name", "Copyright Holder")
                    email = person.get("email")
                    if email:
                        copyright_text = f"SPDX-FileCopyrightText: {current_year} {name} <{email}>"
                    else:
                        copyright_text = f"SPDX-FileCopyrightText: {current_year} {name}"
                    break

        return copyright_text, license_id
    except Exception:
        return None, None


def _get_license_from_existing_headers() -> tuple[Optional[str], Optional[str]]:
    """Extract license info by scanning existing Python files for SPDX headers."""
    try:
        src_path = REPO_ROOT / "src"
        if not src_path.exists():
            return None, None

        copyright_patterns = []
        license_patterns = []

        # Scan Python files for SPDX headers
        for py_file in src_path.rglob("*.py"):
            try:
                content = py_file.read_text(encoding="utf-8")
                lines = content.splitlines()[:10]  # Check first 10 lines

                for line in lines:
                    line = line.strip()
                    if line.startswith("# SPDX-FileCopyrightText:"):
                        copyright_patterns.append(line[2:].strip())  # Remove "# "
                    elif line.startswith("# SPDX-License-Identifier:"):
                        license_patterns.append(line[2:].strip())  # Remove "# "
            except Exception:
                continue

        # Use most common patterns
        if copyright_patterns:
            copyright_text = max(set(copyright_patterns), key=copyright_patterns.count)
        else:
            copyright_text = None

        if license_patterns:
            license_id = max(set(license_patterns), key=license_patterns.count)
        else:
            license_id = None

        return copyright_text, license_id
    except Exception:
        return None, None


def _print_license_detection_error() -> None:
    """Print helpful error message for license detection failure."""
    print("❌ License Detection Error", file=sys.stderr)
    print("=" * 50, file=sys.stderr)
    print("Unable to automatically detect the license for this project.", file=sys.stderr)
    print("", file=sys.stderr)
    print("To fix this, please choose ONE of the following options:", file=sys.stderr)
    print("", file=sys.stderr)
    print("1. 📝 Add license to pyproject.toml (RECOMMENDED):", file=sys.stderr)
    print("   [project]", file=sys.stderr)
    print("   license = { text = &quot;MIT&quot; }  # Replace with your license", file=sys.stderr)
    print("   authors = [", file=sys.stderr)
    print(
        "       { name = &quot;Your Name&quot;, email = &quot;your@email.com&quot; }",
        file=sys.stderr,
    )
    print("   ]", file=sys.stderr)
    print("", file=sys.stderr)
    print("2. 📄 Add SPDX headers to Python files:", file=sys.stderr)
    print("   # SPDX-FileCopyrightText: 2025 Your Name <your@email.com>", file=sys.stderr)
    print("   # SPDX-License-Identifier: MIT", file=sys.stderr)
    print("", file=sys.stderr)
    print("3. 📋 Common license identifiers:", file=sys.stderr)
    print("   MIT, Apache-2.0, GPL-3.0-or-later, AGPL-3.0-or-later,", file=sys.stderr)
    print("   BSD-3-Clause, BSD-2-Clause, 0BSD, ISC", file=sys.stderr)
    print("", file=sys.stderr)
    print("See: https://spdx.org/licenses/ for complete list", file=sys.stderr)
    print("=" * 50, file=sys.stderr)


def get_header_block() -> str:
    """Generate the header block based on detected license information."""
    copyright_text, license_id = detect_license_info()

    header_lines = [
        f"# {copyright_text}",
        f"# SPDX-License-Identifier: {license_id}",
        "",
    ]

    return "\n".join(header_lines)


def semver_bump(version: str, part: str) -> str:
    major, minor, patch = version.split(".")
    major_i, minor_i, patch_i = int(major), int(minor), int(patch)

    if part == "major":
        major_i += 1
        minor_i = 0
        patch_i = 0
    elif part == "minor":
        minor_i += 1
        patch_i = 0
    else:
        patch_i += 1

    return f"{major_i}.{minor_i}.{patch_i}"


def parse_changelog() -> Tuple[List[str], int, int, str]:
    """Read the changelog and return lines, start/end indexes, and previous version."""
    lines = CHANGELOG_PATH.read_text(encoding="utf-8").splitlines(keepends=True)

    try:
        unreleased_idx = next(
            i for i, line in enumerate(lines) if line.startswith("## [Unreleased]")
        )
    except StopIteration as exc:
        raise RuntimeError("Changelog must contain '## [Unreleased]' section.") from exc

    try:
        next_heading_idx = next(
            i for i in range(unreleased_idx + 1, len(lines)) if lines[i].startswith("## [")
        )
    except StopIteration:
        next_heading_idx = len(lines)

    previous_version_line = lines[next_heading_idx].strip()
    if not previous_version_line.startswith("## ["):
        raise RuntimeError("Unable to determine previous release from changelog.")
    previous_version = previous_version_line.split("]")[0].split("[", 1)[1]

    return lines, unreleased_idx, next_heading_idx, previous_version


def sanitize_unreleased_section(section: List[str]) -> List[str]:
    """Trim leading/trailing blank lines from the section."""
    start = 0
    while start < len(section) and section[start].strip() == "":
        start += 1
    end = len(section)
    while end > start and section[end - 1].strip() == "":
        end -= 1
    return section[start:end]


def filter_empty_sections(section: List[str]) -> List[str]:
    """Remove empty sections (those with only a heading and a single dash)."""
    if not section:
        return section

    filtered = []
    i = 0
    n = len(section)

    while i < n:
        line = section[i]

        # Check if this is a section header (### Added, ### Changed, ### Fixed)
        if line.strip().startswith("### ") and (
            "Added" in line or "Changed" in line or "Fixed" in line
        ):
            # Look ahead to see if this section has content beyond just "-"
            section_has_content = False
            j = i + 1

            # Skip blank lines after heading
            while j < n and section[j].strip() == "":
                j += 1

            # Check if there's a list item
            if j < n and section[j].strip().startswith("-"):
                # Check if the list item has actual content (not just "-")
                list_content = section[j].strip()[1:].strip()
                if list_content:  # Has content beyond just "-"
                    section_has_content = True
                    # Include this section
                    filtered.extend(section[i : j + 1])

                    # Include any following lines that belong to this section
                    j += 1
                    while j < n and not section[j].strip().startswith("### "):
                        filtered.append(section[j])
                        j += 1

                    i = j - 1  # Will be incremented by the loop
                else:
                    # Skip this empty section including the following blank line
                    i = j + 1  # Skip past the empty list item and the following blank line
            else:
                # No list item found, include the heading as-is
                filtered.append(line)
        else:
            # Include non-section lines
            filtered.append(line)

        i += 1

    return filtered


def build_unreleased_template() -> List[str]:
    """Return a default scaffold for the Unreleased section."""
    return [
        "### Added\n",
        "\n",
        "-\n",
        "\n",
        "### Changed\n",
        "\n",
        "-\n",
        "\n",
        "### Fixed\n",
        "\n",
        "-\n",
    ]


def update_changelog(new_version: str) -> str:
    lines, unreleased_idx, next_heading_idx, previous_version = parse_changelog()
    unreleased_section = sanitize_unreleased_section(lines[unreleased_idx + 1 : next_heading_idx])

    # Filter out empty sections that only have a heading and a single dash
    filtered_section = filter_empty_sections(unreleased_section)

    new_unreleased = build_unreleased_template()

    if filtered_section:
        # Has content, include with proper spacing
        release_heading = [f"\n## [{new_version}] - {dt.date.today():%Y-%m-%d}\n", "\n"]
        release_block = release_heading + filtered_section + ["\n"]
    else:
        # No content, just the heading with a blank line for proper markdown separation between headings
        release_block = [f"\n## [{new_version}] - {dt.date.today():%Y-%m-%d}\n", "\n"]

    updated_lines = (
        lines[: unreleased_idx + 1]
        + ["\n"]
        + new_unreleased
        + release_block
        + lines[next_heading_idx:]
    )

    # Update link references
    link_inserted = False
    for i, line in enumerate(updated_lines):
        if line.startswith("[unreleased]:"):
            updated_lines[i] = (
                f"[unreleased]: https://github.com/uglyegg/spdx-tools/compare/v{new_version}...HEAD\n"
            )
            if not link_inserted:
                updated_lines.insert(
                    i + 1,
                    f"[{new_version}]: https://github.com/uglyegg/spdx-tools/compare/v{previous_version}...v{new_version}\n",
                )
                link_inserted = True
            break

    CHANGELOG_PATH.write_text("".join(updated_lines), encoding="utf-8")
    return previous_version


def update_pyproject_toml(new_version: str) -> None:
    """Update the version in pyproject.toml."""
    content = PYPROJECT_PATH.read_text(encoding="utf-8")
    lines = content.splitlines(keepends=True)

    for i, line in enumerate(lines):
        if line.strip().startswith("version ="):
            # Preserve the quote style used
            quote = '"' if '"' in line else "'"
            lines[i] = f"version = {quote}{new_version}{quote}\n"
            break

    PYPROJECT_PATH.write_text("".join(lines), encoding="utf-8")


def update_version_file(new_version: str) -> None:
    """Update the _version.py file with the new version."""
    content = VERSION_FILE.read_text(encoding="utf-8")
    header_block = get_header_block()

    # Check if file already has proper SPDX header
    has_spdx_header = any(line.strip().startswith("# SPDX-") for line in content.splitlines()[:10])

    if not has_spdx_header:
        content = header_block + content.lstrip()

    lines = content.splitlines(keepends=True)

    # Determine quote style
    quote = '"'
    for line in lines:
        if line.strip().startswith("__version__ = version ="):
            quote = '"' if '"' in line else "'"
            break

    # Update the version line
    for i, line in enumerate(lines):
        if line.strip().startswith("__version__ = version ="):
            lines[i] = f"__version__ = version = {quote}{new_version}{quote}\n"
            break

    VERSION_FILE.write_text("".join(lines), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare a new project version.")
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--part",
        choices=("major", "minor", "patch"),
        help="Semantic version part to bump (default: patch).",
    )
    group.add_argument(
        "--set",
        dest="explicit",
        help="Set an explicit version (e.g., 1.2.0).",
    )
    args = parser.parse_args()

    _, _, _, previous_version = parse_changelog()
    current_version = previous_version

    if args.explicit:
        new_version = args.explicit
    else:
        part = args.part or "patch"
        new_version = semver_bump(current_version, part)

    prev = update_changelog(new_version)
    update_pyproject_toml(new_version)
    update_version_file(new_version)
    print(f"Prepared release notes for {new_version} (previous: {prev}).")
    print("Next steps:")
    print(f"  git commit -am 'Release v{new_version}'")
    print(f"  git tag v{new_version}")
    print("  git push origin main --tags")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Create simple browsable indexes for generated example repositories."""

from __future__ import annotations

import argparse
import html
from pathlib import Path


def write_index(directory: Path) -> None:
    entries = sorted(directory.iterdir(), key=lambda path: (path.is_file(), path.name.lower()))
    links = []
    if directory.parent != directory:
        links.append('<li><a href="../">../</a></li>')
    for entry in entries:
        if entry.name == "index.html":
            continue
        suffix = "/" if entry.is_dir() else ""
        name = html.escape(entry.name + suffix)
        href = html.escape(entry.name + suffix, quote=True)
        links.append(f'<li><a href="{href}">{name}</a></li>')
    title = html.escape(directory.name or "examples")
    directory.joinpath("index.html").write_text(
        "<!doctype html>\n"
        '<meta charset="utf-8">\n'
        f"<title>{title}</title>\n"
        f"<h1>{title}</h1>\n"
        "<ul>\n" + "\n".join(links) + "\n</ul>\n",
        encoding="utf-8",
    )


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    parser.add_argument("--preserve-root-index", action="store_true")
    args = parser.parse_args()

    root = args.directory.resolve()
    directories = [root, *(path for path in root.rglob("*") if path.is_dir())]
    for directory in sorted(directories, key=lambda path: len(path.parts), reverse=True):
        if directory == root and args.preserve_root_index and (root / "index.html").exists():
            continue
        write_index(directory)


if __name__ == "__main__":
    main()

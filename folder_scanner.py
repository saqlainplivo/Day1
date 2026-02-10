#!/usr/bin/env python3
"""Command-line tool to scan a folder and generate a summary report."""

import argparse
import os
import sys
from collections import Counter
from datetime import datetime


def parse_size(size_str):
    """Parse a human-readable size string (e.g. '10KB', '5MB') into bytes."""
    size_str = size_str.strip().upper()
    units = {"B": 1, "KB": 1024, "MB": 1024**2, "GB": 1024**3, "TB": 1024**4}
    for suffix, multiplier in sorted(units.items(), key=lambda x: -len(x[0])):
        if size_str.endswith(suffix):
            number = size_str[:-len(suffix)].strip()
            try:
                return float(number) * multiplier
            except ValueError:
                break
    try:
        return float(size_str)
    except ValueError:
        print(f"Error: Invalid size format '{size_str}'. Use e.g. 10KB, 5MB, 1GB.", file=sys.stderr)
        sys.exit(1)


def scan_folder(folder_path, filter_exts=None, min_size=None, max_size=None):
    """Scan all files in the folder and collect stats."""
    file_sizes = []
    extensions = Counter()

    for entry in os.scandir(folder_path):
        if entry.is_file(follow_symlinks=False):
            ext = os.path.splitext(entry.name)[1].lower() or "(no extension)"
            if filter_exts and ext not in filter_exts:
                continue
            size = entry.stat().st_size
            if min_size is not None and size < min_size:
                continue
            if max_size is not None and size > max_size:
                continue
            file_sizes.append((entry.name, size))
            extensions[ext] += 1

    return file_sizes, extensions


def format_size(size_bytes):
    """Format byte count using binary units (KiB=1024)."""
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PiB"


def build_report(folder_path, file_sizes, extensions, filter_exts=None, min_size=None, max_size=None):
    """Build the summary report as a string."""
    total_files = len(file_sizes)
    total_size = sum(size for _, size in file_sizes)
    largest_name, largest_size = max(file_sizes, key=lambda x: x[1]) if file_sizes else ("N/A", 0)

    size_filter = "None"
    if min_size is not None or max_size is not None:
        parts = []
        if min_size is not None:
            parts.append(f">= {format_size(min_size)}")
        if max_size is not None:
            parts.append(f"<= {format_size(max_size)}")
        size_filter = " and ".join(parts)

    lines = [
        f"Folder Scan Report",
        f"==================",
        f"Scanned folder : {os.path.abspath(folder_path)}",
        f"Date           : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Filter (ext)   : {', '.join(sorted(filter_exts)) if filter_exts else 'None (all files)'}",
        f"Filter (size)  : {size_filter}",
        f"",
        f"Total files    : {total_files}",
        f"Total size     : {format_size(total_size)}",
        f"Largest file   : {largest_name} ({format_size(largest_size)})",
        f"",
        f"File Types Breakdown",
        f"--------------------",
    ]

    for ext, count in extensions.most_common():
        lines.append(f"  {ext:<20} {count} file(s)")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Scan a folder and generate a summary report.")
    parser.add_argument("folder", help="Path to the folder to scan")
    parser.add_argument("-o", "--output", default="folder_report.txt", help="Output report file (default: folder_report.txt)")
    parser.add_argument("-e", "--ext", nargs="+", help="Filter by file extension(s), e.g. -e .py .txt")
    parser.add_argument("--min-size", help="Minimum file size, e.g. 1KB, 500B, 2MB")
    parser.add_argument("--max-size", help="Maximum file size, e.g. 10MB, 1GB")
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print(f"Error: '{args.folder}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    filter_exts = None
    if args.ext:
        filter_exts = {e if e.startswith(".") else f".{e}" for e in args.ext}

    min_size = parse_size(args.min_size) if args.min_size else None
    max_size = parse_size(args.max_size) if args.max_size else None

    file_sizes, extensions = scan_folder(args.folder, filter_exts, min_size, max_size)

    if not file_sizes:
        print(f"No files found in '{args.folder}'.")
        sys.exit(0)

    report = build_report(args.folder, file_sizes, extensions, filter_exts, min_size, max_size)

    print(report)

    with open(args.output, "w") as f:
        f.write(report + "\n")

    print(f"\nReport saved to: {os.path.abspath(args.output)}")


if __name__ == "__main__":
    main()

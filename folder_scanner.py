#!/usr/bin/env python3
"""Command-line tool to scan a folder and generate a summary report."""

import argparse
import os
import sys
from collections import Counter
from datetime import datetime


def scan_folder(folder_path, filter_exts=None):
    """Scan all files in the folder and collect stats."""
    file_sizes = []
    extensions = Counter()

    for entry in os.scandir(folder_path):
        if entry.is_file(follow_symlinks=False):
            ext = os.path.splitext(entry.name)[1].lower() or "(no extension)"
            if filter_exts and ext not in filter_exts:
                continue
            size = entry.stat().st_size
            file_sizes.append((entry.name, size))
            extensions[ext] += 1

    return file_sizes, extensions


<<<<<<< HEAD (main branch - uses 1000-based SI units)
def format_size(size_bytes):
    """Format byte count using SI units (KB=1000)."""
    for unit, threshold in (("B", 1000), ("KB", 1000), ("MB", 1000), ("GB", 1000), ("TB", 1000)):
        if size_bytes < threshold:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= threshold
    return f"{size_bytes:.1f} PB"
=======
def format_size(size_bytes):
    """Format byte count using binary units (KiB=1024)."""
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PiB"
>>>>>>> feature/binary-units (feature branch - uses 1024-based binary units)


def build_report(folder_path, file_sizes, extensions, filter_exts=None):
    """Build the summary report as a string."""
    total_files = len(file_sizes)
    total_size = sum(size for _, size in file_sizes)
    largest_name, largest_size = max(file_sizes, key=lambda x: x[1]) if file_sizes else ("N/A", 0)

    lines = [
        f"Folder Scan Report",
        f"==================",
        f"Scanned folder : {os.path.abspath(folder_path)}",
        f"Date           : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"Filter         : {', '.join(sorted(filter_exts)) if filter_exts else 'None (all files)'}",
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
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print(f"Error: '{args.folder}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    filter_exts = None
    if args.ext:
        filter_exts = {e if e.startswith(".") else f".{e}" for e in args.ext}

    file_sizes, extensions = scan_folder(args.folder, filter_exts)

    if not file_sizes:
        print(f"No files found in '{args.folder}'.")
        sys.exit(0)

    report = build_report(args.folder, file_sizes, extensions, filter_exts)

    print(report)

    with open(args.output, "w") as f:
        f.write(report + "\n")

    print(f"\nReport saved to: {os.path.abspath(args.output)}")


if __name__ == "__main__":
    main()

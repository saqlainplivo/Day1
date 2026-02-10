#!/usr/bin/env python3
"""Command-line tool to scan a folder and generate a summary report."""

import argparse
import os
import sys
from collections import Counter
from datetime import datetime


def scan_folder(folder_path):
    """Scan all files in the folder and collect stats."""
    file_sizes = []
    extensions = Counter()

    for entry in os.scandir(folder_path):
        if entry.is_file(follow_symlinks=False):
            size = entry.stat().st_size
            file_sizes.append((entry.name, size))
            ext = os.path.splitext(entry.name)[1].lower() or "(no extension)"
            extensions[ext] += 1

    return file_sizes, extensions


def format_size(size_bytes):
    """Format byte count into a human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def build_report(folder_path, file_sizes, extensions):
    """Build the summary report as a string."""
    total_files = len(file_sizes)
    total_size = sum(size for _, size in file_sizes)
    largest_name, largest_size = max(file_sizes, key=lambda x: x[1]) if file_sizes else ("N/A", 0)

    lines = [
        f"Folder Scan Report",
        f"==================",
        f"Scanned folder : {os.path.abspath(folder_path)}",
        f"Date           : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
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
    args = parser.parse_args()

    if not os.path.isdir(args.folder):
        print(f"Error: '{args.folder}' is not a valid directory.", file=sys.stderr)
        sys.exit(1)

    file_sizes, extensions = scan_folder(args.folder)

    if not file_sizes:
        print(f"No files found in '{args.folder}'.")
        sys.exit(0)

    report = build_report(args.folder, file_sizes, extensions)

    print(report)

    with open(args.output, "w") as f:
        f.write(report + "\n")

    print(f"\nReport saved to: {os.path.abspath(args.output)}")


if __name__ == "__main__":
    main()

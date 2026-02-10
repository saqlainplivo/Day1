#!/bin/bash
# Run this script to create a real git merge conflict in folder_scanner.py
# Usage: bash create_conflict.sh

set -e
cd "$(dirname "$0")"

echo "=== Step 1: Initializing git repo ==="
git init
git add folder_scanner.py
git commit -m "Initial commit: folder scanner tool"

echo ""
echo "=== Step 2: Creating feature/binary-units branch ==="
git checkout -b feature/binary-units

# Change to binary units (KiB = 1024)
cat > /tmp/patch_binary.py << 'PYEOF'
import re, sys
with open("folder_scanner.py") as f:
    content = f.read()
content = content.replace(
    '''def format_size(size_bytes):
    """Format byte count into a human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"''',
    '''def format_size(size_bytes):
    """Format byte count using binary units (KiB=1024)."""
    for unit in ("B", "KiB", "MiB", "GiB", "TiB"):
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PiB"'''
)
with open("folder_scanner.py", "w") as f:
    f.write(content)
PYEOF
python3 /tmp/patch_binary.py

git add folder_scanner.py
git commit -m "Use binary units (KiB, MiB, GiB)"

echo ""
echo "=== Step 3: Back to main, making conflicting changes ==="
git checkout main

# Change to SI units (KB = 1000) with 1 decimal place
cat > /tmp/patch_si.py << 'PYEOF'
with open("folder_scanner.py") as f:
    content = f.read()
content = content.replace(
    '''def format_size(size_bytes):
    """Format byte count into a human-readable string."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"''',
    '''def format_size(size_bytes):
    """Format byte count using SI units (KB=1000)."""
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if size_bytes < 1000:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1000
    return f"{size_bytes:.1f} PB"'''
)
with open("folder_scanner.py", "w") as f:
    f.write(content)
PYEOF
python3 /tmp/patch_si.py

git add folder_scanner.py
git commit -m "Use SI units with 1000 divisor and 1 decimal place"

echo ""
echo "=== Step 4: Merging — this will CONFLICT ==="
git merge feature/binary-units || true

echo ""
echo "=== Done! ==="
echo "A merge conflict has been created in folder_scanner.py"
echo "Open the file to see the conflict markers."
echo "Use 'git status' to confirm the conflicted state."

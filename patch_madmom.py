"""
Patch madmom for Python 3.12+ / NumPy 2.x compatibility.
Fixes:
  - np.float -> np.float64
  - np.int -> np.int64 (or np.intp)
  - np.complex -> np.complex128
  - np.bool -> np.bool_
  - np.str -> np.str_
  - np.object -> np.object_
  - from collections import MutableSequence -> from collections.abc import MutableSequence
"""

import os
import re
import glob

MADMOM_DIR = os.path.join("venv", "Lib", "site-packages", "madmom")

# Replacements for numpy deprecated types
NUMPY_REPLACEMENTS = [
    (r'\bnp\.float\b(?!16|32|64|128|_)', 'np.float64'),
    (r'\bnp\.int\b(?!8|16|32|64|_|p)', 'np.intp'),
    (r'\bnp\.complex\b(?!64|128|256|_)', 'np.complex128'),
    (r'\bnp\.bool\b(?!_)', 'np.bool_'),
    (r'\bnp\.str\b(?!_)', 'np.str_'),
    (r'\bnp\.object\b(?!_)', 'np.object_'),
]

patched_files = 0
total_replacements = 0

for root, dirs, files in os.walk(MADMOM_DIR):
    for fname in files:
        if not fname.endswith('.py'):
            continue
        fpath = os.path.join(root, fname)
        with open(fpath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        
        new_content = content
        file_replacements = 0
        
        for pattern, replacement in NUMPY_REPLACEMENTS:
            new_content, count = re.subn(pattern, replacement, new_content)
            file_replacements += count
        
        if new_content != content:
            with open(fpath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            patched_files += 1
            total_replacements += file_replacements
            print(f"  Patched: {os.path.relpath(fpath, MADMOM_DIR)} ({file_replacements} replacements)")

print(f"\nDone: {patched_files} files patched, {total_replacements} total replacements.")

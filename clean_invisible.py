#!/usr/bin/env python3
# clean_invisible.py

import re
import sys

INVISIBLE_CHARS = re.compile(r"[\u200B-\u200D\uFEFF\u00A0]")


def clean_file(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    cleaned = INVISIBLE_CHARS.sub("", content)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(cleaned)
    print(f"✅ Cleaned: {filepath}")


if __name__ == "__main__":
    for filepath in sys.argv[1:]:
        clean_file(filepath)

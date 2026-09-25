#!/usr/bin/env python3
"""Write chapter 02."""
from pathlib import Path
text = open(Path(__file__).parent / "ch02_body.txt", encoding="utf-8").read()
Path(__file__).parents[1] / "docs/novel/02-空位.md"
Path(__file__).resolve().parents[1].joinpath("docs/novel/02-空位.md").write_text(text, encoding="utf-8")
print(len(text))

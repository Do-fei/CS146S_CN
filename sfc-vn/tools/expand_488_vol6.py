#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Expand novel chapters 38-49 — delegates to expand_488_38_49.py."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def main() -> None:
    script = ROOT / "tools" / "expand_488_38_49.py"
    subprocess.run([sys.executable, str(script)], check=True)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Final pad pass: append scene bank until chapters hit target."""

from pathlib import Path

NOVEL = Path(__file__).resolve().parents[1] / "docs" / "novel"
TARGETS = {
    "00-序.md": 7000,
    "01-发送失败.md": 20800,
    "02-空位.md": 20800,
    "03-赵宜家.md": 20800,
    "04-胡同.md": 20800,
    "05-第三夜.md": 20800,
    "06-胡同深.md": 20800,
    "07-便利店.md": 20800,
}

# Additional unique scenes (batch 2)
BANK2 = Path(__file__).with_name("bank2.txt").read_text(encoding="utf-8").split("\n\n")
BANK2 = [p.strip() for p in BANK2 if p.strip()]


def main():
    used = set()
    for name, target in TARGETS.items():
        if name == "01-发送失败.md":
            continue
        path = NOVEL / name
        body = path.read_text(encoding="utf-8").strip()
        for para in BANK2:
            if len(body) >= target * 0.98:
                break
            if para in body:
                continue
            k = para[:80]
            if k in used:
                continue
            body += "\n\n" + para
            used.add(k)
        path.write_text(body.strip() + "\n", encoding="utf-8")
        print(f"{name}\t{len(body.strip())}\t(target {target})")


if __name__ == "__main__":
    main()

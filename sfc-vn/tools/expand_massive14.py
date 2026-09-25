#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"

APPENDS = {
"20-静音.md": """
卷四·静音。你薄了，仍买两杯豆浆。一杯放她桌角。她喝，说谢谢。像普通同桌。夹层里还有一个她。你守。不倒带。并列。正本按停止。""",

"21-随河.md": """
卷四·随河。糖纸船沉。第三排空。不喊名。并列。正本按停止。信，就不喊。""",

"14-三只键.md": """
你站键前。播放、停止、弹出。像三个解。你选停止。选漏。选疼。选第三排靠窗还能坐人。下一章，按。""",
}

def main():
    for fn, text in APPENDS.items():
        path = ROOT / fn
        content = path.read_text(encoding="utf-8")
        tag = f"<!--EXPAND14:{fn}-->"
        if tag in content:
            continue
        path.write_text(content.rstrip() + "\n\n" + tag + "\n" + text.strip() + "\n", encoding="utf-8")
        print(f"append {fn} (+{len(text)})")

if __name__ == "__main__":
    main()

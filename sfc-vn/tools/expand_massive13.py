#!/usr/bin/env python3
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1] / "docs" / "novel"

text = """
你读到这里，应该知道正本怎么走：发送失败，空位，赵宜家，胡同，天桥，西单，食街，三楼，倒带馆，磁带，三只键，停止，爬回，小的路，漏句。赵宜从「我选——」后面漏回来。不完整。能抓袖口。方程两个解。你们选漏的那一个。疼就抓袖口。袖口在，人在。卷四是另八个早晨。并列。不判对错。够了。"""

def main():
    path = ROOT / "00-序.md"
    content = path.read_text(encoding="utf-8")
    if "<!--FINAL-->" in content:
        print("skip")
        return
    path.write_text(content.rstrip() + "\n\n<!--FINAL-->\n" + text.strip() + "\n", encoding="utf-8")
    print(f"append 00-序 (+{len(text)})")

if __name__ == "__main__":
    main()

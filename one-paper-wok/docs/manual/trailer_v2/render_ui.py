#!/usr/bin/env python3
"""Render promotional (not shipping) phone UIs for the Apple-style trailer."""

from __future__ import annotations

import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parent
UI = ROOT / "ui"
UI.mkdir(parents=True, exist_ok=True)
FONT = Path("/tmp/trailer2/NotoSansSC.ttf")
PLATES = ROOT / "plates"

CSS = f"""
@font-face {{
  font-family: NotoSC;
  src: url("file://{FONT}");
  font-weight: 100 900;
}}
:root {{
  --orange: #E8734A;
  --cream: #F4EDE3;
  --ink: #F6F3EE;
  --dim: rgba(246,243,238,.55);
  --line: rgba(255,255,255,.08);
  --glass: rgba(255,255,255,.06);
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html, body {{
  width: 390px; height: 844px; overflow: hidden;
  background: #070708;
  color: var(--ink);
  font-family: NotoSC, sans-serif;
}}
.screen {{
  width: 390px; height: 844px; position: relative;
  background:
    radial-gradient(1200px 480px at 50% -10%, rgba(232,115,74,.16), transparent 55%),
    radial-gradient(900px 500px at 80% 120%, rgba(74,144,217,.10), transparent 50%),
    #070708;
}}
.status {{
  height: 54px; padding: 16px 28px 0;
  display: flex; justify-content: space-between; font-size: 13px; font-weight: 600;
  letter-spacing: .04em;
}}
.island {{
  position: absolute; top: 12px; left: 50%; transform: translateX(-50%);
  width: 118px; height: 34px; background: #000; border-radius: 20px;
}}
.kicker {{
  color: var(--orange); font-size: 12px; font-weight: 600;
  letter-spacing: .28em; text-transform: uppercase;
}}
h1 {{ font-size: 34px; font-weight: 280; letter-spacing: .04em; line-height: 1.2; }}
h2 {{ font-size: 22px; font-weight: 400; letter-spacing: .02em; }}
p {{ color: var(--dim); font-size: 14px; line-height: 1.65; }}
.pad {{ padding: 8px 22px 0; }}
.card {{
  background: var(--glass);
  border: 1px solid var(--line);
  border-radius: 22px;
  padding: 16px 18px;
}}
.row {{ display: flex; gap: 10px; }}
.nav {{
  position: absolute; left: 18px; right: 18px; bottom: 18px;
  height: 58px; border-radius: 20px;
  background: rgba(20,18,16,.72);
  border: 1px solid var(--line);
  display: flex; align-items: center; justify-content: space-around;
  font-size: 11px; letter-spacing: .16em; color: var(--dim);
}}
.nav .on {{ color: var(--orange); }}
.cover {{
  height: 168px; border-radius: 16px; padding: 14px;
  display: flex; flex-direction: column; justify-content: flex-end;
  font-size: 15px; font-weight: 500; color: #fff;
}}
.pill {{
  display: inline-flex; align-items: center; gap: 6px;
  border-radius: 999px; padding: 6px 12px; font-size: 12px;
  background: rgba(232,115,74,.14); color: var(--orange);
  letter-spacing: .08em;
}}
.bar {{
  height: 4px; border-radius: 4px; background: rgba(255,255,255,.08); overflow: hidden;
}}
.bar > i {{ display: block; height: 100%; width: 68%; background: var(--orange); }}
.chat {{ display: flex; flex-direction: column; gap: 10px; }}
.bubble {{
  max-width: 78%; padding: 12px 14px; border-radius: 18px; font-size: 14px; line-height: 1.55;
}}
.me {{ align-self: flex-end; background: var(--orange); color: #fff; border-bottom-right-radius: 6px; }}
.ai {{
  align-self: flex-start; background: var(--glass); border: 1px solid var(--line);
  border-bottom-left-radius: 6px; color: var(--ink);
}}
.feed {{ display: flex; flex-direction: column; gap: 10px; }}
.tiny {{ font-size: 11px; letter-spacing: .18em; color: var(--dim); }}
"""


def page(body: str, extra: str = "") -> str:
    return f"""<!doctype html><meta charset="utf-8">
<style>{CSS}{extra}</style>
<body><div class="island"></div>
<div class="screen">
  <div class="status"><span>9:41</span><span>⬤⬤⬤</span></div>
  {body}
</div></body>"""


PAGES = {
    "home": page(
        """
<div class="pad" style="padding-top:18px">
  <div class="kicker">CLAYPOT</div>
  <h1 style="margin-top:10px">今夜烹制哪一本</h1>
  <p style="margin:8px 0 18px">纸书入煲，文火成纸。</p>
  <div class="row">
    <div class="cover" style="flex:1;background:linear-gradient(160deg,#8b3a24,#e8734a)">万历十五年</div>
    <div class="cover" style="flex:1;background:linear-gradient(160deg,#1c3d4a,#4a90d9)">百年孤独</div>
  </div>
  <div class="card" style="margin-top:12px">
    <div class="tiny">SLOW FIRE</div>
    <h2 style="margin:6px 0 8px">静静的顿河 · 72%</h2>
    <div class="bar"><i></i></div>
    <p style="margin-top:8px;font-size:12px">OCR 完成 · 正在提炼一纸精华</p>
  </div>
</div>
<div class="nav"><span class="on">煲</span><span>食堂</span><span>搭子</span><span>我的</span></div>
"""
    ),
    "scan": page(
        f"""
<div style="position:absolute;inset:0;background:
  linear-gradient(180deg,rgba(0,0,0,.35),rgba(0,0,0,.55)),
  url('file://{PLATES / 'plate_glyphs.png'}') center/cover"></div>
<div style="position:absolute;inset:118px 42px 190px;border:1.5px solid rgba(232,115,74,.85);border-radius:28px;box-shadow:0 0 0 1px rgba(255,255,255,.08),0 0 80px rgba(232,115,74,.18)"></div>
<div style="position:absolute;top:132px;left:56px;width:22px;height:22px;border-top:3px solid #fff;border-left:3px solid #fff;border-radius:4px 0 0 0"></div>
<div style="position:absolute;top:132px;right:56px;width:22px;height:22px;border-top:3px solid #fff;border-right:3px solid #fff;border-radius:0 4px 0 0"></div>
<div style="position:absolute;bottom:206px;left:56px;width:22px;height:22px;border-bottom:3px solid #fff;border-left:3px solid #fff"></div>
<div style="position:absolute;bottom:206px;right:56px;width:22px;height:22px;border-bottom:3px solid #fff;border-right:3px solid #fff"></div>
<div class="pad" style="position:absolute;left:0;right:0;top:64px">
  <div class="kicker">SCAN</div>
  <h1 style="font-size:28px;margin-top:8px">对准纸面</h1>
</div>
<div style="position:absolute;left:22px;right:22px;bottom:96px" class="card">
  <div class="pill">LIVE OCR</div>
  <h2 style="margin:10px 0 4px">正在捕捉文字</h2>
  <p>章节、页码、批注位置会自动对齐。</p>
</div>
""",
        extra=".screen{background:#000}",
    ),
    "cook": page(
        """
<div class="pad" style="padding-top:12px;text-align:center">
  <div class="kicker">SLOW FIRE</div>
  <h1 style="margin:12px 0 6px">文火烹制中</h1>
  <p>模型在煲中烹饪，你可以离开。</p>
  <div style="margin:28px auto 8px;width:228px;height:228px;border-radius:50%;
    background:conic-gradient(#E8734A 0 250deg, rgba(255,255,255,.08) 0 360deg);
    display:grid;place-items:center">
    <div style="width:188px;height:188px;border-radius:50%;background:#0b0b0c;display:flex;flex-direction:column;align-items:center;justify-content:center">
      <div style="font-size:48px;font-weight:250;letter-spacing:.04em">72</div>
      <div class="tiny">PERCENT</div>
    </div>
  </div>
  <div class="row" style="margin-top:22px;text-align:left">
    <div class="card" style="flex:1"><div class="tiny">01</div><h2 style="font-size:16px;margin-top:6px">OCR</h2><p style="font-size:12px">文字已醒来</p></div>
    <div class="card" style="flex:1"><div class="tiny">02</div><h2 style="font-size:16px;margin-top:6px">章节</h2><p style="font-size:12px">结构已分好</p></div>
    <div class="card" style="flex:1"><div class="tiny">03</div><h2 style="font-size:16px;margin-top:6px">一纸</h2><p style="font-size:12px">精华提炼中</p></div>
  </div>
</div>
"""
    ),
    "paper": page(
        """
<div class="pad" style="padding-top:10px">
  <div class="kicker">ONE PAPER</div>
  <h1 style="margin:10px 0 4px">一纸看懂</h1>
  <p style="margin-bottom:16px">《万历十五年》</p>
  <div class="card" style="padding:20px 18px">
    <div class="tiny">INSIGHT</div>
    <h2 style="margin:8px 0 10px;line-height:1.45;font-size:20px">制度的裂缝，比个人的善恶更安静。</h2>
    <p>一纸把整本书收成可带走的结构：论点、人物对照、可回翻的段落。</p>
  </div>
  <div class="row" style="margin-top:10px">
    <div class="card" style="flex:1"><div class="tiny">01</div><p style="color:#fff;margin-top:8px;font-size:13px">海瑞不是例外，是对照。</p></div>
    <div class="card" style="flex:1"><div class="tiny">02</div><p style="color:#fff;margin-top:8px;font-size:13px">张居正把火候操之过急。</p></div>
  </div>
</div>
"""
    ),
    "reader": page(
        """
<div class="pad" style="padding-top:8px">
  <div class="kicker">READER</div>
  <h1 style="font-size:26px;margin:8px 0 14px">对照阅读</h1>
  <div class="card" style="margin-bottom:10px">
    <div class="tiny">中文</div>
    <p style="color:#f6f3ee;margin-top:8px;font-size:15px;line-height:1.7">万历十五年，表面上风平浪静，其实裂缝已经沿着制度的纹理慢慢张开。</p>
  </div>
  <div class="card" style="border-color:rgba(232,115,74,.28);background:rgba(232,115,74,.08)">
    <div class="tiny" style="color:var(--orange)">EN</div>
    <p style="color:#f6f3ee;margin-top:8px;font-size:15px;line-height:1.7">The year 1587 looks still. The cracks, though, have already opened along the grain of the system.</p>
  </div>
  <div class="row" style="margin-top:12px">
    <div class="pill">搜索</div>
    <div class="pill">翻译</div>
    <div class="pill">EPUB</div>
  </div>
</div>
"""
    ),
    "companion": page(
        """
<div class="pad" style="padding-top:8px">
  <div class="kicker">AI COMPANION</div>
  <h1 style="font-size:28px;margin:8px 0 4px">一纸搭子</h1>
  <p style="margin-bottom:16px">围着这本书，慢慢问。</p>
  <div class="chat">
    <div class="bubble me">这一章为什么突然写海瑞？</div>
    <div class="bubble ai">作者把他放入煲中当对照。不是要你崇拜清官，是让你看见制度本身难以烹透的地方。</div>
    <div class="bubble me">那张居正呢？</div>
    <div class="bubble ai">效率很高，火也太旺。一纸里把他标成「火候」那一段。</div>
  </div>
</div>
<div class="nav"><span>煲</span><span>食堂</span><span class="on">搭子</span><span>我的</span></div>
"""
    ),
    "canteen": page(
        """
<div class="pad" style="padding-top:8px">
  <div class="kicker">CANTEEN</div>
  <h1 style="margin:8px 0 14px">一纸食堂</h1>
  <div class="feed">
    <div class="card">
      <div class="tiny">今日热煲</div>
      <h2 style="margin:6px 0 4px">百年孤独</h2>
      <p>32 人正在同烹 · 一纸被加了 18 味批注</p>
    </div>
    <div class="card">
      <div class="tiny">新出煲</div>
      <h2 style="margin:6px 0 4px">寂静的春天</h2>
      <p>有人把第 3 章收成一张「毒物年表」。</p>
    </div>
    <div class="card">
      <div class="tiny">可回煲</div>
      <h2 style="margin:6px 0 4px">万历十五年</h2>
      <p>把你的旁注，加进别人的煲底。</p>
    </div>
  </div>
</div>
<div class="nav"><span>煲</span><span class="on">食堂</span><span>搭子</span><span>我的</span></div>
"""
    ),
    "note": page(
        """
<div class="pad" style="padding-top:8px">
  <div class="kicker">RETURN</div>
  <h1 style="font-size:28px;margin:8px 0 14px">回煲加料</h1>
  <div class="card" style="height:210px;position:relative;overflow:hidden">
    <p style="color:#E8734A;font-size:18px;line-height:2.1;transform:rotate(-4deg);margin:18px 8px">
      制度 &nbsp;≠&nbsp;道德<br>裂缝在页边
    </p>
    <p style="position:absolute;right:16px;bottom:12px;color:rgba(246,243,238,.4);font-size:12px">手写 · 已识别</p>
  </div>
  <div class="card" style="margin-top:10px">
    <div class="tiny">ALIGNED</div>
    <h2 style="margin:8px 0 6px">已对齐到第 112 页</h2>
    <p>你的旁注成为一纸的新一层。下次打开，还在原处。</p>
  </div>
</div>
"""
    ),
}


def render() -> None:
    chrome = "google-chrome"
    for name, html in PAGES.items():
        html_path = UI / f"{name}.html"
        png_path = UI / f"{name}.png"
        html_path.write_text(html, encoding="utf-8")
        if png_path.exists() and png_path.stat().st_size > 10000:
            print("skip", name)
            continue
        cmd = [
            chrome,
            "--headless",
            "--no-sandbox",
            "--disable-gpu",
            "--hide-scrollbars",
            "--allow-file-access-from-files",
            f"--user-data-dir=/tmp/trailer2-chrome-{name}",
            "--force-device-scale-factor=3",
            "--window-size=390,844",
            f"--screenshot={png_path}",
            f"file://{html_path}",
        ]
        try:
            subprocess.run(cmd, check=True, capture_output=True, timeout=12)
        except subprocess.TimeoutExpired:
            if not (png_path.exists() and png_path.stat().st_size > 10000):
                raise
        print("ui", name, png_path.stat().st_size)


if __name__ == "__main__":
    render()

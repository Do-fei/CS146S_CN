#!/usr/bin/env python3
"""Render phone-UI HTML mockups matching the current APK copy, then screenshot them."""

from pathlib import Path
import subprocess

ROOT = Path("/workspace/one-paper-wok/docs/manual")
SHOTS = ROOT / "_shots"
IMAGES = ROOT / "images"
SHOTS.mkdir(parents=True, exist_ok=True)
IMAGES.mkdir(parents=True, exist_ok=True)

CSS = """
@font-face {
  font-family: "ManualCjk";
  src: url("cjk.ttf") format("truetype");
  font-weight: 400 800;
}
:root {
  --orange: #E8734A;
  --orange-soft: #F4A261;
  --cream: #FFF8F0;
  --ink: #2D2D2D;
  --muted: #888888;
  --blue: #4A90D9;
  --purple: #8B6FD4;
  --green: #2D9D5C;
  --line: #F0EBE4;
}
* { box-sizing: border-box; margin: 0; padding: 0; }
html, body {
  width: 390px; height: 844px; overflow: hidden;
  background: var(--cream);
  color: var(--ink);
  font-family: "ManualCjk", "Noto Sans SC", "WenQuanYi Micro Hei", sans-serif;
}
.screen { width: 390px; height: 844px; background: var(--cream); display: flex; flex-direction: column; }
.status {
  height: 48px; padding: 14px 22px 0;
  display: flex; justify-content: space-between; font-size: 13px; font-weight: 600;
}
.appbar {
  padding: 8px 16px 12px; display: flex; align-items: center; gap: 8px;
}
.appbar h1 { font-size: 26px; font-weight: 800; flex: 1; }
.appbar .icons { display: flex; gap: 6px; color: var(--ink); font-size: 20px; }
.back { font-size: 22px; width: 28px; }
.body { flex: 1; padding: 0 16px 24px; overflow: hidden; }
.hero { padding: 12px 24px 0; }
.emoji { font-size: 48px; line-height: 1.1; }
.title { font-size: 32px; font-weight: 800; margin-top: 8px; }
.tagline { color: var(--muted); margin-top: 4px; font-size: 15px; }
.field {
  background: #fff; border: 1px solid #d9d3cc; border-radius: 14px;
  padding: 12px 14px; margin-top: 16px;
}
.field label { display: block; font-size: 12px; color: var(--muted); margin-bottom: 4px; }
.field .value { font-size: 15px; word-break: break-all; }
.help { font-size: 12px; color: var(--muted); margin: 6px 4px 0; line-height: 1.4; }
.link { color: var(--orange); font-weight: 600; font-size: 15px; margin: 10px 4px 0; }
.ok { color: var(--green); font-size: 14px; margin: 8px 4px 0; }
.hint { color: var(--blue); font-weight: 700; margin-top: 10px; }
.btn {
  margin: 28px 24px 0; background: var(--orange); color: #fff;
  border-radius: 14px; text-align: center; padding: 14px;
  font-weight: 700; font-size: 16px;
}
.btn.ghost {
  background: transparent; color: var(--ink);
  border: 1px solid #d9d3cc;
}
.fab {
  position: absolute; right: 20px; bottom: 28px;
  width: 56px; height: 56px; border-radius: 16px;
  background: var(--orange); color: #fff;
  display: flex; align-items: center; justify-content: center; font-size: 24px;
}
.chips { display: flex; gap: 8px; margin: 8px 0 16px; }
.chip {
  border-radius: 20px; padding: 6px 12px; font-size: 13px; font-weight: 600;
  background: #fff; color: var(--muted); border: 1px solid var(--line);
}
.chip.on { background: #FFF0EA; color: var(--orange); border-color: #FFD8C8; }
.empty { text-align: center; color: var(--muted); margin-top: 48px; font-size: 15px; }
.banner {
  margin: 8px 0 12px; padding: 18px; border-radius: 20px;
  background: linear-gradient(90deg, var(--orange), var(--orange-soft)); color: #fff;
}
.banner h2 { font-size: 18px; }
.banner p { color: rgba(255,255,255,.75); margin: 4px 0 12px; font-size: 13px; }
.bar { height: 6px; background: rgba(255,255,255,.25); border-radius: 99px; overflow: hidden; }
.bar > i { display: block; height: 100%; width: 46%; background: #fff; }
.card {
  background: #fff; border: 1px solid var(--line); border-radius: 18px;
  padding: 12px; display: flex; gap: 12px; margin-bottom: 12px;
}
.cover {
  width: 48px; height: 64px; border-radius: 8px;
  background: linear-gradient(#4A90D9, #2A6CB0);
  display: flex; align-items: center; justify-content: center; font-size: 22px;
}
.card h3 { font-size: 16px; }
.card p { color: var(--muted); font-size: 12px; margin-top: 2px; }
.tags { display: flex; gap: 6px; margin-top: 6px; }
.tag { font-size: 11px; font-weight: 700; padding: 3px 8px; border-radius: 20px; }
.tag.o { background: rgba(232,115,74,.12); color: var(--orange); }
.tag.b { background: rgba(74,144,217,.12); color: var(--blue); }
.tag.g { background: rgba(45,157,92,.12); color: var(--green); }
.seg { display: flex; border: 1px solid #e6dfd6; border-radius: 12px; overflow: hidden; margin: 16px 0; }
.seg span { flex: 1; text-align: center; padding: 10px; font-size: 14px; background: #fff; }
.seg span.on { background: #FFF0EA; color: var(--orange); font-weight: 700; }
.outline {
  display: inline-flex; align-items: center; gap: 6px;
  border: 1px solid #d9d3cc; border-radius: 12px; padding: 8px 12px;
  margin-right: 8px; font-size: 14px;
}
.muted { color: var(--muted); }
.row { display: flex; align-items: center; justify-content: space-between; }
.list-card {
  background: #fff; border: 1px solid var(--line); border-radius: 18px;
  padding: 14px 16px; margin-bottom: 10px;
  display: flex; align-items: center; gap: 12px;
}
.list-card .ico { color: var(--orange); font-size: 22px; width: 28px; }
.list-card .arrow { color: #c4bbb3; margin-left: auto; }
.progress {
  height: 8px; background: #f0e6dd; border-radius: 99px; overflow: hidden; margin: 16px 0 8px;
}
.progress i { display: block; height: 100%; width: 46%; background: var(--orange); }
.pill {
  display: inline-block; background: var(--orange); color: #fff;
  border-radius: 20px; padding: 4px 10px; font-size: 12px; font-weight: 700;
}
.insight { display: flex; gap: 10px; align-items: flex-start; margin-top: 12px; }
.num {
  width: 28px; height: 28px; border-radius: 50%;
  background: #FFF0EA; color: var(--orange); font-weight: 800; font-size: 12px;
  display: flex; align-items: center; justify-content: center; flex-shrink: 0;
}
.mine {
  margin-top: 10px; background: #F3EEFF; border-left: 3px solid var(--purple);
  padding: 12px; color: #5A3FA0; font-size: 14px; line-height: 1.5;
}
.search {
  display: flex; gap: 6px; align-items: center; padding: 8px 16px 8px;
}
.search input {
  flex: 1; border: 1px solid #e6dfd6; border-radius: 10px; padding: 8px 10px; font-size: 14px;
  background: #fff;
}
.page {
  padding: 8px 16px 0; font-size: 16px; line-height: 1.7;
}
.pager { display: flex; justify-content: space-between; align-items: center; padding: 12px 24px; color: var(--muted); }
.src { color: var(--muted); font-size: 14px; }
.abs { position: relative; }
"""


def page(body: str) -> str:
    return f"""<!doctype html>
<meta charset="utf-8">
<style>{CSS}</style>
{body}
"""


screens = {
    "01_login": """
<div class="screen">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="hero">
    <div class="emoji">🍲</div>
    <div class="title">一纸读书煲</div>
    <div class="tagline">一个有趣的精神庇护所</div>
    <div class="field"><label>服务器地址</label><div class="value">https://backend-production-9191.up.railway.app</div></div>
    <div class="help">Railway 填 https 公网地址；本地调试填电脑局域网 IP，不要填 127.0.0.1</div>
    <div class="link">测试连接</div>
    <div class="field"><label>邮箱</label><div class="value muted">任意邮箱即可</div></div>
    <div class="help">未配置 SMTP 时，验证码会直接显示在本页</div>
  </div>
  <div class="btn">获取验证码</div>
</div>
""",
    "02_login_connected": """
<div class="screen">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="hero">
    <div class="emoji">🍲</div>
    <div class="title">一纸读书煲</div>
    <div class="tagline">一个有趣的精神庇护所</div>
    <div class="field"><label>服务器地址</label><div class="value">https://backend-production-9191.up.railway.app</div></div>
    <div class="help">Railway 填 https 公网地址；本地调试填电脑局域网 IP，不要填 127.0.0.1</div>
    <div class="link">测试连接</div>
    <div class="ok">已连通 · OCR mock · 邮件 mock</div>
    <div class="field"><label>邮箱</label><div class="value">reader@example.com</div></div>
    <div class="help">未配置 SMTP 时，验证码会直接显示在本页</div>
  </div>
  <div class="btn">获取验证码</div>
</div>
""",
    "03_login_code": """
<div class="screen">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="hero">
    <div class="emoji">🍲</div>
    <div class="title">一纸读书煲</div>
    <div class="tagline">一个有趣的精神庇护所</div>
    <div class="field"><label>服务器地址</label><div class="value">https://backend-production-9191.up.railway.app</div></div>
    <div class="link">测试连接</div>
    <div class="ok">已连通 · OCR mock · 邮件 mock</div>
    <div class="field"><label>邮箱</label><div class="value">reader@example.com</div></div>
    <div class="field"><label>6 位验证码</label><div class="value">482917</div></div>
    <div class="hint">开发模式验证码：482917</div>
  </div>
  <div class="btn">登录</div>
</div>
""",
    "04_library_empty": """
<div class="screen abs">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="appbar"><h1>我的锅</h1><div class="icons">🌐 &nbsp; ↻ &nbsp; ⎋</div></div>
  <div class="body">
    <div class="chips"><span class="chip on">全部</span><span class="chip">电子书</span><span class="chip">一纸项目</span></div>
    <div class="empty">锅还是空的。点右下角开始自炊。</div>
  </div>
  <div class="fab">📷</div>
</div>
""",
    "05_library_cooking": """
<div class="screen abs">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="appbar"><h1>我的锅</h1><div class="icons">🌐 &nbsp; ↻ &nbsp; ⎋</div></div>
  <div class="body">
    <div class="banner"><h2>🍳 慢炖中</h2><p>正在识别第 3 页…</p><div class="bar"><i></i></div></div>
    <div class="chips"><span class="chip on">全部</span><span class="chip">电子书</span><span class="chip">一纸项目</span></div>
    <div class="card">
      <div class="cover">📘</div>
      <div>
        <h3>思考，快与慢</h3>
        <p>丹尼尔·卡尼曼 · 12 页 · cooking</p>
        <div class="tags"><span class="tag o">一纸项目</span><span class="tag b">电子书</span></div>
      </div>
    </div>
  </div>
  <div class="fab">📷</div>
</div>
""",
    "06_library_books": """
<div class="screen abs">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="appbar"><h1>我的锅</h1><div class="icons">🌐 &nbsp; ↻ &nbsp; ⎋</div></div>
  <div class="body">
    <div class="chips"><span class="chip on">全部</span><span class="chip">电子书</span><span class="chip">一纸项目</span></div>
    <div class="card">
      <div class="cover">📘</div>
      <div>
        <h3>思考，快与慢</h3>
        <p>丹尼尔·卡尼曼 · 12 页 · done</p>
        <div class="tags"><span class="tag o">一纸项目</span><span class="tag b">电子书</span><span class="tag g">EPUB</span></div>
      </div>
    </div>
  </div>
  <div class="fab">📷</div>
</div>
""",
    "07_scan": """
<div class="screen">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="appbar"><div class="back">‹</div><h1 style="font-size:20px">自炊台</h1></div>
  <div class="body">
    <div class="field"><label>书名</label><div class="value">思考，快与慢</div></div>
    <div class="field"><label>作者（可选）</label><div class="value">丹尼尔·卡尼曼</div></div>
    <div class="seg"><span class="on">全书自炊</span><span>轻摘录</span></div>
    <div class="outline">📷 拍摄</div>
    <div class="outline">🖼 相册</div>
    <p class="help" style="margin-top:12px">已选 3 页</p>
    <div class="btn" style="margin:24px 0 0">🔥 开始慢炖（3 页）</div>
  </div>
</div>
""",
    "08_scan_annotation": """
<div class="screen">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="appbar"><div class="back">‹</div><h1 style="font-size:18px">批注扫描 · 回锅加料</h1></div>
  <div class="body">
    <div class="field"><label>对应页码（从 0 起，可空）</label><div class="value">3</div></div>
    <div class="outline" style="margin-top:16px">📷 拍摄</div>
    <div class="outline">🖼 相册</div>
    <p class="help" style="margin-top:12px">已选 1 页</p>
    <div class="btn" style="margin:24px 0 0">上传批注并去笔记本</div>
  </div>
</div>
""",
    "09_cooking": """
<div class="screen">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="appbar"><div class="back">‹</div><h1 style="font-size:20px">慢炖中</h1></div>
  <div class="body" style="padding:24px">
    <div style="font-size:18px;font-weight:700">正在识别文字、整理章节…</div>
    <div class="progress"><i></i></div>
    <div class="muted">46% · ocr</div>
    <div style="flex:1;height:420px"></div>
    <div class="btn ghost" style="margin:0">回我的锅，后台继续</div>
  </div>
</div>
""",
    "10_book_home": """
<div class="screen">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="appbar"><div class="back">‹</div><h1 style="font-size:20px">思考，快与慢</h1><div class="icons">🗑</div></div>
  <div class="body">
    <p class="muted">丹尼尔·卡尼曼 · 12 页 · done</p>
    <div style="height:16px"></div>
    <div class="list-card"><div class="ico">📖</div><div>阅读电子书</div><div class="arrow">›</div></div>
    <div class="list-card"><div class="ico">✨</div><div>一纸项目</div><div class="arrow">›</div></div>
    <div class="list-card"><div class="ico">📝</div><div>一纸笔记本</div><div class="arrow">›</div></div>
    <div class="list-card"><div class="ico">📠</div><div>回锅加料（扫描批注）</div><div class="arrow">›</div></div>
  </div>
</div>
""",
    "11_reader": """
<div class="screen">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="appbar"><div class="back">‹</div><h1 style="font-size:18px">思考，快与慢</h1><div class="icons">PDF &nbsp; EPUB</div></div>
  <div class="search"><input value="全文搜索"><span>🔍</span><span style="color:#ccc">○</span><span>EN</span></div>
  <div class="page">系统1自动、快速，几乎不费力气。系统2把注意力分配给费力的大脑活动，包括复杂的计算。<br><br>当你读完这一页，不妨停下来想想：哪些判断其实是系统1替你做的？</div>
  <div class="pager"><span>‹</span><span>第 0 / 11 页</span><span>›</span></div>
</div>
""",
    "12_reader_translate": """
<div class="screen">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="appbar"><div class="back">‹</div><h1 style="font-size:18px">思考，快与慢</h1><div class="icons">PDF &nbsp; EPUB</div></div>
  <div class="search"><input value="全文搜索"><span>🔍</span><span style="color:var(--orange);font-weight:700">●</span><span>EN</span></div>
  <div class="page">
    <div class="src">系统1自动、快速，几乎不费力气。</div>
    <div style="margin:4px 0 14px">System 1 is automatic, fast, and almost effortless.</div>
    <div class="src">系统2把注意力分配给费力的大脑活动，包括复杂的计算。</div>
    <div style="margin:4px 0 14px">System 2 allocates attention to effortful mental activities, including complex calculations.</div>
  </div>
  <div class="pager"><span>‹</span><span>第 0 / 11 页</span><span>›</span></div>
</div>
""",
    "13_project": """
<div class="screen">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="appbar"><div class="back">‹</div><h1 style="font-size:20px">一纸项目</h1></div>
  <div class="body">
    <div class="chips"><span class="chip on">全书</span><span class="chip">启发式</span></div>
    <div class="card" style="display:block;padding:16px">
      <span class="pill">一纸精华 · v2</span>
      <p style="margin-top:12px;line-height:1.7;font-size:15px">快思考负责直觉，慢思考负责费力的推理。认识这两种系统，是少被偏见带走的第一步。</p>
      <div class="insight"><div class="num">1</div><div>直觉很快，但不等于正确</div></div>
      <div class="insight"><div class="num">2</div><div>注意力是稀缺资源，系统2很容易偷懒</div></div>
      <div class="insight"><div class="num">3</div><div>用一纸笔记把偏见「回锅」一次，印象会更深</div></div>
      <div class="mine">我的批注 · P.3<br>我开会时的第一反应，多半是系统1。</div>
    </div>
    <div class="row" style="gap:8px;margin-top:4px">
      <div class="btn ghost" style="flex:1;margin:0">回锅加料</div>
      <div class="btn" style="flex:1;margin:0;opacity:.45">分享到食堂（即将开放）</div>
    </div>
  </div>
</div>
""",
    "14_notebook": """
<div class="screen">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="appbar"><div class="back">‹</div><h1 style="font-size:20px">一纸笔记本</h1><div class="link" style="margin:0">回锅加料</div></div>
  <div class="body">
    <div class="field"><label>打字记录一条批注</label><div class="value muted">写下你的想法…</div></div>
    <div class="outline" style="margin-top:12px">📠 扫描手写批注</div>
    <div class="card" style="display:block;margin-top:16px">
      <h3>第一反应多半是系统1。</h3>
      <p>P.3 · typed · ready · 已对齐到第 3 页</p>
    </div>
  </div>
</div>
""",
    "15_server_dialog": """
<div class="screen" style="background:rgba(45,45,45,.35);position:relative">
  <div class="status"><span>9:41</span><span>☁︎  100%</span></div>
  <div class="appbar"><h1>我的锅</h1></div>
  <div style="background:#fff;border-radius:22px;margin:160px 24px 0;padding:20px">
    <div style="font-size:18px;font-weight:800;margin-bottom:12px">服务器地址</div>
    <div class="field" style="margin-top:0"><div class="value">https://backend-production-9191.up.railway.app</div></div>
    <div class="help">云端填 https；本地填局域网 IP</div>
    <div class="row" style="margin-top:18px;justify-content:flex-end;gap:12px">
      <span class="muted">取消</span>
      <span class="btn" style="margin:0;padding:8px 16px">保存</span>
    </div>
  </div>
</div>
""",
}

for name, body in screens.items():
    html_path = SHOTS / f"{name}.html"
    html_path.write_text(page(body), encoding="utf-8")
    out = IMAGES / f"{name}.png"
    profile = f"/tmp/chrome-manual-shots/{name}"
    cmd = [
        "timeout",
        "8",
        "google-chrome",
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--force-device-scale-factor=2",
        "--window-size=390,844",
        "--no-sandbox",
        "--remote-debugging-port=0",
        f"--user-data-dir={profile}",
        f"--screenshot={out}",
        html_path.as_uri(),
    ]
    subprocess.run(cmd, check=False, capture_output=True)
    size = out.stat().st_size if out.exists() else 0
    print("wrote", out.name, size)
    if size < 8000:
        raise SystemExit(f"screenshot too small: {out}")

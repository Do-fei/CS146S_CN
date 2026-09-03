# 一纸读书煲 One Paper Wok

一个有趣的精神庇护所：把实体书扫进锅里，用 OCR + AI 慢炖成可搜索电子书和「一纸项目」，再把手写批注回锅加料。数据跟账号走，换设备登录即可同步。

当前 MVP **不调用付费云 API**。未配置密钥时，OCR / 摘要 / 邮件全部走本地 Mock，手机上可以完整体验登录、扫描、出锅、翻译、回锅和同步流程。

## 在安卓手机上安装使用

1. 电脑安装 Python 3.10+ 和 Poetry，启动后端（必须监听 `0.0.0.0`，否则手机连不上）：

```bash
cd one-paper-wok/backend
poetry install
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. 电脑和手机连**同一个 Wi-Fi**。在电脑上查局域网 IP（Windows：`ipconfig` 看无线网卡 IPv4；macOS/Linux：`ifconfig` 或 `ip a`），例如 `192.168.1.8`。

3. 安装 APK（debug 包，需允许「未知来源」）。APK 在本仓库 CI / PR 附件，或本地执行：

```bash
cd one-paper-wok/app
flutter build apk --debug
# 产物：build/app/outputs/flutter-apk/app-debug.apk
```

4. 打开 App → 服务器地址填 `http://192.168.1.8:8000`（换成你的 IP）→「测试连接」应显示已连通。

5. 邮箱填任意地址 → 获取验证码。当前 Mock 邮件不会真发信，验证码会直接显示在登录页。

6. 点右下角相机开始自炊。

如果测试连接失败：确认后端已启动、防火墙放行 8000 端口、IP 没写成 `127.0.0.1`。

## 功能（MVP）

- 邮箱验证码登录（JWT）；服务器地址可在登录页和「我的锅」里修改
- 自炊扫描 → 慢炖（OCR + 章节结构 + 一纸精华）→ 可搜索 PDF
- EPUB 导出
- 阅读页按段翻译（带缓存）
- 一纸笔记本 / 回锅加料（手写 OCR + 对齐 + 版本）
- 多设备增量同步

暂不包含：一纸食堂社区、AI 搭子自由对话、付费云 OCR/大模型。

## 目录

```
one-paper-wok/
├── backend/     FastAPI
├── app/         Flutter 客户端
└── README.md
```

## 可选云服务（默认不需要）

写入 `backend/.env` 才会启用真实服务，否则保持 Mock：

| 变量 | 说明 |
|------|------|
| `JWT_SECRET` | JWT 签名密钥 |
| `BAIDU_OCR_API_KEY` / `BAIDU_OCR_SECRET_KEY` | 百度 OCR |
| `DASHSCOPE_API_KEY` | 通义千问 |
| `SMTP_HOST` `SMTP_PORT` `SMTP_USER` `SMTP_PASSWORD` `SMTP_FROM` | 发验证码邮件 |
| `OCR_PROVIDER` / `LLM_PROVIDER` / `EMAIL_PROVIDER` | `auto`（默认）/`mock`/`baidu`/`qwen`/`smtp` |

## 主题

暖橙 `#E8734A`、米白 `#FFF8F0`、锅蓝 `#4A90D9`。

# 一纸读书煲 One Paper Wok

一个有趣的精神庇护所：把实体书扫进锅里，用 OCR + AI 慢炖成可搜索电子书和「一纸项目」，再把手写批注回锅加料。数据跟账号走，换设备登录即可同步。

当前 MVP **不调用付费云 API**。未配置密钥时，OCR / 摘要 / 邮件全部走本地 Mock，手机上可以完整体验登录、扫描、出锅、翻译、回锅和同步流程。

**图文使用说明书（配当前 APK）：** [docs/使用说明书.md](docs/使用说明书.md) · 浏览版 [docs/manual/index.html](docs/manual/index.html)

**产品预告片（MP4，约 49 秒）：** [docs/manual/一纸读书煲-产品预告.mp4](docs/manual/一纸读书煲-产品预告.mp4)

## 在安卓手机上安装使用

1. 把后端部署到 **Railway**（推荐，见下方），或在电脑上启动：

```bash
cd one-paper-wok/backend
poetry install
poetry run uvicorn app.main:app --host 0.0.0.0 --port 8000
```

2. 安装 APK（需允许「未知来源」）。本地执行：

```bash
cd one-paper-wok/app
flutter build apk --release
# 产物：build/app/outputs/flutter-apk/app-release.apk
```

3. 打开 App → 填服务器地址 →「测试连接」应显示已连通。
   - **Railway**：填 `https://你的服务.up.railway.app`（可省略 `https://`，App 会自动补上）
   - **电脑调试**：和手机同一 Wi-Fi，填 `http://192.168.x.x:8000`，不要填 `127.0.0.1`

4. 邮箱填任意地址 → 获取验证码。未配置 SMTP 时，验证码会直接显示在登录页。

5. 点右下角相机开始自炊。

## 部署后端：选 Railway，而不是 Cloudflare Workers

这套后端是 FastAPI + SQLite + 本地磁盘（扫描图、PDF、EPUB）。手机只是客户端，需要一个**长期在线、带持久盘**的服务器。

| | Railway | Cloudflare |
|---|---|---|
| 跑 FastAPI / Docker | 原生支持，改动小 | Workers 跑不了这套栈；Containers 可以，但磁盘默认会丢 |
| SQLite + 上传文件 | Volume 挂 `/data` 即可 | 需要再接 R2 / D1，工作量大 |
| 公网 HTTPS | 一键 Generate Domain | 域名和 CDN 很强 |
| 适合现在 | **推荐，直接用** | 以后可把自定义域名 / CDN 放在前面 |

备选 Cloudflare 仍然有价值：自定义域名、国内访问加速。计算层先放 Railway。

### Railway 步骤

1. 打开 [railway.com](https://railway.com)，用 GitHub 登录，New Project → Deploy from GitHub repo → 选本仓库。
2. 服务 Settings → **Root Directory** 填 `one-paper-wok/backend`（必须，否则找不到 Dockerfile）。
3. Variables 至少加一项：`JWT_SECRET` = 一段足够长的随机字符串（不要用默认值，否则进程会拒绝启动）。
4. 在画布上给该服务 **New Volume**，挂载路径填 `/data`（SQLite 和扫描文件都写这里，重启不丢）。
5. Settings → Networking → **Generate Domain**，得到 `https://xxx.up.railway.app`。
6. 浏览器打开 `https://xxx.up.railway.app/health`，应看到 `"ok": true`。
7. 手机 App 把服务器地址改成这个 https 地址。

未配百度 OCR / 通义 / SMTP 时，云端同样走 Mock，验证码仍会返回给 App。配好密钥后自动切换真实服务，无需改代码。

SQLite 只能单进程写，镜像里固定 `--workers 1`，也不要给这个服务开多个 replica。

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
├── backend/     FastAPI（含 Dockerfile / railway.toml）
├── app/         Flutter 客户端
└── README.md
```

## 可选云服务（默认不需要）

写入 `backend/.env` 或 Railway Variables 才会启用真实服务，否则保持 Mock：

| 变量 | 说明 |
|------|------|
| `JWT_SECRET` | JWT 签名密钥（Railway 上必填） |
| `BAIDU_OCR_API_KEY` / `BAIDU_OCR_SECRET_KEY` | 百度 OCR |
| `DASHSCOPE_API_KEY` | 通义千问 |
| `SMTP_HOST` `SMTP_PORT` `SMTP_USER` `SMTP_PASSWORD` `SMTP_FROM` | 发验证码邮件 |
| `OCR_PROVIDER` / `LLM_PROVIDER` / `EMAIL_PROVIDER` | `auto`（默认）/`mock`/`baidu`/`qwen`/`smtp` |

## 主题

暖橙 `#E8734A`、米白 `#FFF8F0`、锅蓝 `#4A90D9`。

# 一纸读书煲 One Paper Wok

一个有趣的精神庇护所：把实体书扫进锅里，用 OCR + AI 慢炖成可搜索电子书和「一纸项目」，再把手写批注回锅加料。数据跟账号走，换设备登录即可同步。

## 功能（MVP）

- 邮箱验证码登录（JWT）
- 自炊扫描 → 慢炖（OCR + 章节结构 + 一纸精华）→ 可搜索 PDF
- EPUB 导出
- 阅读页按段翻译（带缓存）
- 一纸笔记本 / 回锅加料（手写 OCR + 对齐 + 版本）
- 多设备增量同步

暂不包含：一纸食堂社区、AI 搭子自由对话、付费。

## 目录

```
one-paper-wok/
├── backend/     FastAPI
├── app/         Flutter 客户端
└── README.md
```

## 后端

Python 3.10+，依赖用 Poetry 管理。未配置云服务密钥时自动使用 Mock（验证码会打印到日志，并在 API 的 `debug_code` 字段返回）。

```bash
cd backend
poetry install
poetry run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
poetry run pytest
```

可选环境变量（写入 `backend/.env` 或系统 Secrets）：

| 变量 | 说明 |
|------|------|
| `JWT_SECRET` | JWT 签名密钥 |
| `BAIDU_OCR_API_KEY` / `BAIDU_OCR_SECRET_KEY` | 百度 OCR |
| `DASHSCOPE_API_KEY` | 通义千问 |
| `SMTP_HOST` `SMTP_PORT` `SMTP_USER` `SMTP_PASSWORD` `SMTP_FROM` | 发验证码邮件 |
| `OCR_PROVIDER` / `LLM_PROVIDER` / `EMAIL_PROVIDER` | `auto`（默认）/`mock`/`baidu`/`qwen`/`smtp` |

## 客户端

需要 [Flutter 3.x](https://flutter.dev) 稳定版。把 `app/lib/core/config.dart` 里的 `apiBaseUrl` 改成后端地址（真机请用电脑局域网 IP，不要用 `localhost`）。

```bash
cd app
flutter pub get
flutter run
flutter test
```

登录：开发环境发送验证码后，后端响应里的 `debug_code` 会显示在登录页提示中（仅 Mock 邮件时）。

## 主题

暖橙 `#E8734A`、米白 `#FFF8F0`、锅蓝 `#4A90D9`。

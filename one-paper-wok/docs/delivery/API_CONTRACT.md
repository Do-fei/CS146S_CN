# API 契约草案（仅用户触发云能力时）

首版默认可空鉴权。若有额度账号则 Bearer。每个请求 `X-Request-Id`。写操作 `Idempotency-Key`。

错误体：`{ "code", "message", "retryable", "requestId" }`。

## 端点

- `POST /v1/uploads/intents` 短期对象上传
- `POST /v1/jobs` · `GET /v1/jobs/{id}` · `POST /v1/jobs/{id}/cancel`
- `POST /v1/conversations/{id}/messages` → SSE（token delta + final citations + usage）
- `POST /v1/citations/resolve`（可选；多数解析在本地）
- `POST /v1/projects/generate`
- `POST /v1/projects/{id}/proposals`
- `POST /v1/proposals/{id}/items/{itemId}/decide`（accept / reject / edit）
- `GET /v1/usage`

食堂端点未入选，不实现。

客户端持久化 `localJobId ↔ jobId` 对照。这不是同步协议。

本轮 Android 客户端内置 `FakeAiProvider` 与同一 JSON 形状，便于无网验收。正式后端另立，不沿用旧 `recook.py` 整份重写。

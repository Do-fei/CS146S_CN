# ADR-004 首版 AI 为用户自备 DeepSeek Key（BYOK）

- 状态：Accepted
- 日期：2026-09-05

## 决策

产品只提供软件，不提供 AI 服务。用户在设置里填写自己的 DeepSeek API Key。不填则走 `FakeAiProvider`。

- 端点：`https://api.deepseek.com/chat/completions`
- 文本模型：`deepseek-v4-flash`
- Key 存 Android Keystore / EncryptedSharedPreferences；不进备份、不进日志、不进 git
- 请求从手机直连 DeepSeek；只送当前提问的检索片段或选区，不默认送全书或私人笔记
- 印刷 OCR 仍为端侧 ML Kit。DeepSeek 不当全书 OCR。看图实验模型不进第一版主路径

## 后果

我们不代扣费、不经手他人 Key。费用与内容去向由用户的 Key 决定。设置与搭子面板必须写明这一点。

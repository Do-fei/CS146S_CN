# 数据模型（交付版）

原则：作品 ≠ 版本 ≠ 文件 ≠ 个人项目。稳定 UUID。软删带影响说明。引用用 Locator。

本地 Room 是个人权威副本。

## 实体

- `Book` 用户书架上的书（不按标题去重）
- `BookEdition` / `SourceDocument` 一次导入的文件或扫描集
- `Asset` 原图/文件 checksum
- `Page` `TextBlock` `Chapter` `ReadingPosition`
- `Annotation` `Note` `NoteRevision`（`userDraft` 与 `recognitionDraft` 分列）
- `Conversation` `Message` `Citation`
- `Project` `ProjectSection`（稳定 `sectionId`）`ProjectRevision` `ChangeProposal` `ChangeProposalItem`
- `ImportJob` `ProcessingJob` `JobStep` `ProviderUsage` `BackupManifest`

## Citation

最少字段：`sourceDocumentId`、`contentVersion`、`locatorType`、`locatorJson`、`quote`、`context`、`stale`。

## 任务状态

`queued | running | waiting_for_network | retryable_failed | failed | cancelled | completed`

幂等键 = `clientJobId`。无可靠 ETA 时显示「第 12/40 页 · OCR」。用户强停后数据在，可手动恢复，不承诺自动续跑。

## 知识三层

`source`（原书）/ `ai`（模型）/ `user`（用户）。UI 与导出必须标层，不可互相冒充。

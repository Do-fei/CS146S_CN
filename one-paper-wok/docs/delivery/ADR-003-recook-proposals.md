# ADR-003 回煲只出 ChangeProposal，禁止整份重写

- 状态：Accepted
- 日期：2026-09-05

## 背景

原型 `backend/app/services/recook.py` 会整份重写 `OnePaperProject`。这与「用户编辑不被再生成覆盖」冲突，不可沿用行为。

## 决策

- 模型只许输出校验过的结构化操作：`insert` / `replace` / `noop`，必须带稳定 `sectionId`。
- 合并公式：`baseRevision + proposedItems + currentRevision`。
- 用户在计算期间又编辑：接受旧建议时走三路合并；冲突项回到审阅，禁止覆盖最新用户稿。
- 禁止后台整份重写。逐条接受 / 拒绝 / 改后接受。
- 引用用 Locator（`epub_locator` / `pdf_page_rect` / `image_quad`），不用屏幕页码。过期只标记 `stale`，不伪装成功。

## 后果

- P5 的 Fake Provider 必须遵守同一契约，便于与 P3 同期做契约测试。
- 旧 Flutter「回锅」演示不能当验收基准。

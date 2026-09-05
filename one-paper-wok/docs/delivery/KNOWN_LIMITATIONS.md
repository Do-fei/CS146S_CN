# 已知限制（随交付版分发）

1. **手写 OCR** 不是印刷体，也不是 Digital Ink。识别稿必须校对；识别不能当无误原文。
2. **复杂 PDF**（扫描件、双栏、表格）：系统 `PdfRenderer` 只保证看见页面，不保证文本选择/重排。搜索依赖 OCR 层。超过 32MB 的 PDF 不整本抽文本层，可按页识别，不当原文。
3. **扫描生成 EPUB** 未承诺。纯文字样本达标后另开评估门。
4. **自动翻页检测拍摄** 未实测，不承诺。
5. **Readium 官方 Navigator** 尚未在目标真机关闭门禁。当前 EPUB 走抽出文本 + Locator（quote/progression）。
6. **无实时同步、无云备份账号。** 换机必须先导出完整 zip（含原书文件）。旧版 JSON 只能恢复目录。WebDAV 同路径后写覆盖。
7. **食堂** 本版只有预告和系统分享，没有社区。
8. **AI** 使用用户自己的 DeepSeek Key；未填写时走 Fake。我们不提供模型服务。印刷 OCR 不是 DeepSeek。
9. **ML Kit bundled** 增加包体（debug 全 ABI 约 60MB+）；无 GMS 真机准确率待测。
10. **16KB 页大小 / Pdfium `.so`：** 本轮不链入开源 Pdfium，避免未核 ABI 的崩溃。

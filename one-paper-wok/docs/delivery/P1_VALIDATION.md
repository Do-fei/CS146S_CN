# P1 高风险验证记录

批准：方案 v0.1。本轮在无客户授权样书、无指定目标真机的约束下执行 **JVM 夹具 + 接口实验**。真机项保持门禁开启，不关闭「已在客户机验收」。

| 实验 | 方法 | 结果 | Go / No-go |
|---|---|---|---|
| EPUB Locator 改字号后回跳 | `LocatorResolver`：quote + progression，不用屏幕页码 | 单测通过 | **Go**（文本/抽出 EPUB）。Readium Fragment 集成仍待真机 |
| PDF 选择/搜索/跳转 | 评估 Android `PdfRenderer` + 坐标模型 | 能渲染页面位图；**无文本选择层** | **Conditional Go**：阅读走固定版式预览；选择/搜索走 OCR 层。PSPDFKit 未采购 |
| OCR 框到原图 | `OcrBox` 归一化四边形映射 | 单测通过 | **Go**（几何）。印刷体准确率待样页 |
| 中文搜索 | trigram + 精确子串，不依赖 FTS5 默认分词 | 单测通过 | **Go** |
| 无 GMS 上 ML Kit bundled | 依赖写入 catalog：`text-recognition-chinese` | 编译期纳入；未在无 GMS 真机跑 | **Hold**（代码路径在，真机未关） |
| WorkManager 被杀后文件不丢 | 先复制私有目录再改任务状态；状态机单测 | 单测通过 | **Go**（契约）。进程被杀待真机 |
| 回煲 JSON 合并 | `RecookMerger` 三路合并夹具 | 单测通过 | **Go** |

## 阶段门

- **进入 P2–P7：** 允许。文本阅读、合并、搜索、任务契约已有夹具。`:domain:test` 与 `:app:assembleDebug` 已在本环境通过。
- **进入客户签字：** 不允许，直到目标真机补齐 Readium/PDF 选择/无 GMS OCR。
- **P8 食堂：** 未批准，不开工。

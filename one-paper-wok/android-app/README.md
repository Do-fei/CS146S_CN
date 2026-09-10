# 一纸书煲 · Android 客户交付版

Kotlin + Jetpack Compose，本地优先。Flutter 目录 `../app` 已冻结为原型，不要在那边继续堆交付功能。

包名暂定 `com.onepaper.app`（方案 v0.1）。minSdk 26。

## 本机构建

```bash
# 在 android-app/ 下创建 local.properties
echo "sdk.dir=$ANDROID_HOME" > local.properties

./gradlew :domain:test
./gradlew :app:assembleDebug
```

产物：`app/build/outputs/apk/debug/app-debug.apk`（不要提交）。

## 范围

- 底栏：书架 / 一纸 / 食堂 / 我的。食堂本版只有预告和系统分享。
- 无登录。导入、阅读、笔记、导出、备份均在本地完成。完整备份是 zip（含原书/划线/进度），不含 DeepSeek Key。
- 回煲是 ChangeProposal 逐条审阅，不是整份重写。
- AI：设置里填自己的 DeepSeek Key（本机密钥库）。不填则 Fake；只导入一章时拒绝全书结论。
- 食堂：底栏预告页 + 系统分享，无社区后端。
- 反馈：`nuannuan.dean@gmail.com`
- 印刷 OCR：ML Kit bundled 中文适配器 + Fake 夹具。手写必须校对。
- EPUB 当前走抽出文本 + Locator（quote / progression）。Readium Navigator 仍待目标真机。
- PDF 用系统 `PdfRenderer` 翻页预览，不假装可重排；文本检索走 OCR 层。
- 导入按 MIME / 文件头识别，不依赖 content URI 是否带扩展名。随包说明书与样页可一键导入。

决策与限制见 `../docs/delivery/`。

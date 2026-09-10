# ADR-001 交付客户端用 Kotlin + Compose，冻结 Flutter

- 状态：Accepted
- 日期：2026-09-05

## 背景

仓库内 `one-paper-wok/app` 是 Flutter + 强制登录 + Mock 云同步的演示。Readium、CameraX、WorkManager、Room FTS、端侧 ML Kit 在原生栈上更稳。本文无近期 iOS/桌面/Web 承诺。

## 决策

- 客户交付版新建 `one-paper-wok/android-app/`。
- Flutter 应用冻结为原型，只读对照，不作为交付骨架增量修补。
- 基础：Kotlin、Jetpack Compose、Material 3（品牌主题覆盖，不套默认紫）。
- 架构：ViewModel / Coroutines / Flow / Repository / Hilt / Navigation。
- minSdk 26；compileSdk/targetSdk 锁在工程 Version Catalog（现为 35），不在规划散文里写死「最新」。

## 后果

- 近期不做 KMP。
- Compose 托管 Readium `EpubNavigatorFragment` 须用 `AndroidFragment`；P1 记为设备集成项。

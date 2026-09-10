package com.onepaper.domain.citation

/** 续读进度：用 Locator，不用屏幕页码。 */
data class ProgressSnapshot(
    val percent: Int,
    val label: String,
)

object ReadingProgress {
    fun of(
        locator: ContentLocator?,
        unitTotal: Int,
    ): ProgressSnapshot {
        if (locator == null || unitTotal <= 0) {
            return ProgressSnapshot(0, "未读")
        }
        return when (locator) {
            is ContentLocator.Epub -> {
                val pct = (locator.progression.coerceIn(0.0, 1.0) * 100).toInt()
                ProgressSnapshot(pct, if (pct <= 0) "已打开" else "读到 $pct%")
            }
            is ContentLocator.PdfPageRect -> {
                val page = locator.pageIndex.coerceAtLeast(0) + 1
                val pct = ((page.toDouble() / unitTotal.coerceAtLeast(1)) * 100).toInt().coerceIn(1, 100)
                ProgressSnapshot(pct, "第 $page / $unitTotal 页")
            }
            is ContentLocator.ImageQuad -> ProgressSnapshot(0, "扫描页")
        }
    }
}

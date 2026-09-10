package com.onepaper.domain.citation

/** 从一纸 / 搭子 / 笔记带回阅读器。 */
data class ReaderJump(
    val quote: String,
    val href: String?,
    val pageIndex: Int?,
)

object LocatorJump {
    fun from(locator: ContentLocator): ReaderJump = when (locator) {
        is ContentLocator.Epub -> ReaderJump(
            quote = locator.quote.exact,
            href = locator.href,
            pageIndex = null,
        )
        is ContentLocator.PdfPageRect -> ReaderJump(
            quote = locator.quote.exact,
            href = null,
            pageIndex = locator.pageIndex,
        )
        is ContentLocator.ImageQuad -> ReaderJump(
            quote = locator.quote.exact,
            href = null,
            pageIndex = null,
        )
    }

    fun fromJson(raw: String?): ReaderJump? {
        if (raw.isNullOrBlank()) return null
        return runCatching { from(LocatorCodec.decode(raw)) }.getOrNull()
    }
}

package com.onepaper.domain.citation

import kotlinx.serialization.SerialName
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json

enum class LocatorType {
    EPUB_LOCATOR,
    PDF_PAGE_RECT,
    IMAGE_QUAD,
}

@Serializable
data class TextQuote(
    val exact: String,
    val prefix: String = "",
    val suffix: String = "",
)

/**
 * 稳定定位：EPUB 用文档内 progression + 文本引文，不用屏幕页码。
 * PDF / 扫描页用归一化坐标（0..1）。
 */
@Serializable
sealed class ContentLocator {
    abstract val type: LocatorType

    @Serializable
    @SerialName("epub_locator")
    data class Epub(
        val href: String,
        /** 0.0 章首 → 1.0 章末，与字号无关。 */
        val progression: Double,
        val quote: TextQuote,
        val cfi: String? = null,
    ) : ContentLocator() {
        override val type: LocatorType = LocatorType.EPUB_LOCATOR
    }

    @Serializable
    @SerialName("pdf_page_rect")
    data class PdfPageRect(
        val pageIndex: Int,
        val left: Double,
        val top: Double,
        val right: Double,
        val bottom: Double,
        val quote: TextQuote,
    ) : ContentLocator() {
        override val type: LocatorType = LocatorType.PDF_PAGE_RECT
    }

    @Serializable
    @SerialName("image_quad")
    data class ImageQuad(
        val pageId: String,
        val points: List<NormPoint>,
        val quote: TextQuote,
    ) : ContentLocator() {
        override val type: LocatorType = LocatorType.IMAGE_QUAD
    }
}

@Serializable
data class NormPoint(val x: Double, val y: Double)

@Serializable
data class Citation(
    val sourceDocumentId: String,
    val contentVersion: String,
    val locator: ContentLocator,
    val quote: String,
    val context: String = "",
    val stale: Boolean = false,
)

object LocatorCodec {
    val json = Json {
        ignoreUnknownKeys = true
        classDiscriminator = "kind"
    }

    fun encode(locator: ContentLocator): String = json.encodeToString(locator)

    fun decode(raw: String): ContentLocator = json.decodeFromString(raw)
}

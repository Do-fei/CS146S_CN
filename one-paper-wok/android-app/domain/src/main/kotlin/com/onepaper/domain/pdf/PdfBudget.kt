package com.onepaper.domain.pdf

/** 大 PDF 不整文件读进内存。抽不出文本层就老实说。 */
object PdfBudget {
    const val MAX_EXTRACT_BYTES = 32L * 1024 * 1024

    fun canExtractInMemory(sizeBytes: Long): Boolean = sizeBytes in 1..MAX_EXTRACT_BYTES

    fun tooLargeMessage(): String =
        "这份 PDF 超过 32MB，本机未整本抽文本层。可在阅读器里按页识别，不当原文。"
}

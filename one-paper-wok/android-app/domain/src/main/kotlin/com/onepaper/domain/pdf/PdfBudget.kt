package com.onepaper.domain.pdf

/** 大 PDF 不整文件读进内存。抽不出文本层就老实说。 */
object PdfBudget {
    const val MAX_EXTRACT_BYTES = 32L * 1024 * 1024

    fun canExtractInMemory(sizeBytes: Long): Boolean = sizeBytes in 1..MAX_EXTRACT_BYTES

    fun tooLargeMessage(): String =
        "文件比较大，按页识别。"
}

package com.onepaper.domain.citation

import org.junit.Assert.assertEquals
import org.junit.Test

class ReadingProgressTest {
    @Test
    fun unreadWhenMissing() {
        val snap = ReadingProgress.of(null, 10)
        assertEquals(0, snap.percent)
        assertEquals("未读", snap.label)
    }

    @Test
    fun epubUsesProgressionNotScreenPage() {
        val locator = ContentLocator.Epub("ch2", 0.4, TextQuote("慢烹"))
        val snap = ReadingProgress.of(locator, 5)
        assertEquals(40, snap.percent)
        assertEquals("读到 40%", snap.label)
    }

    @Test
    fun pdfUsesPageIndex() {
        val locator = ContentLocator.PdfPageRect(2, 0.0, 0.0, 1.0, 1.0, TextQuote("页"))
        val snap = ReadingProgress.of(locator, 10)
        assertEquals(30, snap.percent)
        assertEquals("第 3 / 10 页", snap.label)
    }
}

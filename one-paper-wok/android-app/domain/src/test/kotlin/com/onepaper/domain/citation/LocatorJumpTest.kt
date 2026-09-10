package com.onepaper.domain.citation

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class LocatorJumpTest {
    @Test
    fun epubJumpKeepsHrefAndQuote() {
        val jump = LocatorJump.from(ContentLocator.Epub("ch-2", 0.2, TextQuote("把书读薄")))
        assertEquals("把书读薄", jump.quote)
        assertEquals("ch-2", jump.href)
        assertNull(jump.pageIndex)
    }

    @Test
    fun pdfJumpKeepsPage() {
        val jump = LocatorJump.from(
            ContentLocator.PdfPageRect(4, 0.0, 0.0, 1.0, 1.0, TextQuote("样页")),
        )
        assertEquals("样页", jump.quote)
        assertEquals(4, jump.pageIndex)
        assertNull(jump.href)
    }

    @Test
    fun jsonRoundTrip() {
        val locator = ContentLocator.Epub("href-a", 0.1, TextQuote("原文"))
        val jump = LocatorJump.fromJson(LocatorCodec.encode(locator))
        assertEquals("原文", jump?.quote)
        assertEquals("href-a", jump?.href)
    }
}

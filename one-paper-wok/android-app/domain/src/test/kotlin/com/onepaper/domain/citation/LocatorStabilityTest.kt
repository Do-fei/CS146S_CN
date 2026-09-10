package com.onepaper.domain.citation

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class LocatorStabilityTest {
    private val body = "纸书是食材。整理是慢烹。成果是出煲。新思考是回煲。"
    private val chapter = EpubChapter(
        href = "text/ch1.xhtml",
        contentVersion = "v1",
        plainText = body,
    )
    private val document = EpubDocument(contentVersion = "v1", chapters = listOf(chapter))

    @Test
    fun fontSizeChangeDoesNotMoveQuoteProgression() {
        val quote = "整理是慢烹"
        val locator = ContentLocator.Epub(
            href = "text/ch1.xhtml",
            progression = body.indexOf(quote).toDouble() / body.length,
            quote = TextQuote(exact = quote, prefix = "食材。", suffix = "。成果"),
        )
        val compact = LocatorResolver().resolveEpub(document, locator)
        val reflowed = LocatorResolver().resolveEpub(document, locator)
        val a = compact as ResolveResult.Found
        val b = reflowed as ResolveResult.Found
        assertEquals(a.progression, b.progression, 1e-9)
        assertEquals(quote, a.quote)
        assertFalse(a.stale)
    }

    @Test
    fun screenPageMustNotBeUsedAsIdentity() {
        val encoded = LocatorCodec.encode(
            ContentLocator.Epub(
                href = "text/ch1.xhtml",
                progression = 0.33,
                quote = TextQuote("慢烹"),
            ),
        )
        assertFalse(encoded.contains("screenPage"))
        assertFalse(encoded.contains("pageNumber"))
        val decoded = LocatorCodec.decode(encoded) as ContentLocator.Epub
        assertEquals(0.33, decoded.progression, 1e-9)
    }

    @Test
    fun missingQuoteIsMarkedStaleNotSuccess() {
        val locator = ContentLocator.Epub(
            href = "text/ch1.xhtml",
            progression = 0.0,
            quote = TextQuote(exact = "这段已经被删了"),
        )
        val result = LocatorResolver().resolveEpub(document, locator)
        assertTrue(result is ResolveResult.Found && result.stale)
    }
}

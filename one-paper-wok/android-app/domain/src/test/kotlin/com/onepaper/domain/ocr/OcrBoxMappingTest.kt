package com.onepaper.domain.ocr

import com.onepaper.domain.citation.LocatorResolver
import com.onepaper.domain.citation.ContentLocator
import com.onepaper.domain.citation.NormPoint
import com.onepaper.domain.citation.TextQuote
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Test

class OcrBoxMappingTest {
    @Test
    fun normalizedQuadMapsToPixels() {
        val box = OcrBox(
            points = listOf(
                NormPoint(0.0, 0.0),
                NormPoint(0.5, 0.0),
                NormPoint(0.5, 0.25),
                NormPoint(0.0, 0.25),
            ),
            text = "慢烹",
            confidence = 0.9f,
        )
        val pixels = OcrGeometry.boxToPixels(box, width = 4000, height = 2000)
        assertEquals(listOf(0 to 0, 2000 to 0, 2000 to 500, 0 to 500), pixels)
    }

    @Test
    fun handwritingResultIsNeverAuthoritativeOriginal() = runBlocking {
        val engine = FakeOcrEngine()
        val result = engine.recognize("page-1".toByteArray(), OcrKind.HANDWRITING)
        assertFalse(result.isAuthoritativeOriginal)
        assertEquals(OcrKind.HANDWRITING, result.kind)
    }

    @Test
    fun imageQuadLocatorRoundTrip() {
        val locator = ContentLocator.ImageQuad(
            pageId = "page-1",
            points = listOf(NormPoint(0.1, 0.2), NormPoint(0.4, 0.2), NormPoint(0.4, 0.3), NormPoint(0.1, 0.3)),
            quote = TextQuote("慢烹"),
        )
        val pixels = LocatorResolver().mapImageQuad(locator, 1000, 2000)
        assertEquals(100, pixels[0].x)
        assertEquals(400, pixels[0].y)
        assertEquals(600, pixels[2].y)
    }
}

package com.onepaper.domain.tts

import com.onepaper.domain.model.KnowledgeLayer
import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Assert.assertTrue
import org.junit.Test

class TtsPolicyTest {
    @Test
    fun epubReadsChapterText() {
        val passage = TtsPolicy.passage("EPUB", "把书读薄", null, null)
        assertEquals(KnowledgeLayer.SOURCE, passage?.layer)
        assertEquals("把书读薄", passage?.text)
    }

    @Test
    fun pdfPrefersTextLayerOverOcr() {
        val passage = TtsPolicy.passage("PDF", null, "原书句", "识别稿")
        assertEquals(KnowledgeLayer.SOURCE, passage?.layer)
        assertEquals("原书句", passage?.text)
    }

    @Test
    fun scannedPageUsesDraftAndSaysSo() {
        val passage = TtsPolicy.passage("IMAGES", null, null, "识别出来的字")
        assertEquals(KnowledgeLayer.AI, passage?.layer)
        assertTrue(passage?.label?.contains("识别稿") == true)
    }

    @Test
    fun silentWhenNoText() {
        assertNull(TtsPolicy.passage("PDF", null, "  ", null))
    }
}

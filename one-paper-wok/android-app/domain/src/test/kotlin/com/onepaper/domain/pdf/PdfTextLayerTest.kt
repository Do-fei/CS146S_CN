package com.onepaper.domain.pdf

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class PdfTextLayerTest {
    @Test
    fun extractsLiteralTj() {
        val page = PdfTextLayer.extractPages(minimalPdf("(SlowCook) Tj"), pageCount = 1).single()
        assertTrue(page.hasTextOperators)
        assertTrue(page.text.contains("SlowCook"))
    }

    @Test
    fun imageOnlyHasNoLayer() {
        val bytes = "%PDF-1.4\n1 0 obj<< /Type /Page >>endobj\nstream\n/Image Do\nendstream\n".toByteArray()
        val page = PdfTextLayer.extractPages(bytes, 1).single()
        assertFalse(page.hasTextOperators)
        assertEquals("", page.text)
    }

    @Test
    fun detectsOperatorsWithoutPretendingReflow() {
        assertTrue(PdfTextLayer.hasTextOperators("BT /F1 12 Tf (甲) Tj ET"))
        assertFalse(PdfTextLayer.hasTextOperators("/Image Do"))
        assertEquals("甲乙", PdfTextLayer.extractStrings("(甲) Tj (乙) Tj"))
    }

    private fun minimalPdf(content: String): ByteArray {
        val stream = "BT\n$content\nET\n"
        return buildString {
            append("%PDF-1.4\n")
            append("1 0 obj<< /Type /Catalog /Pages 2 0 R >>endobj\n")
            append("2 0 obj<< /Type /Pages /Kids [3 0 R] /Count 1 >>endobj\n")
            append("3 0 obj<< /Type /Page /Parent 2 0 R /Contents 4 0 R >>endobj\n")
            append("4 0 obj<< /Length ${stream.length} >>stream\n")
            append(stream)
            append("endstream\nendobj\n")
        }.toByteArray()
    }
}

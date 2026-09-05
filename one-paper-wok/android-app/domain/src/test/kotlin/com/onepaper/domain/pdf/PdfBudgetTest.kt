package com.onepaper.domain.pdf

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class PdfBudgetTest {
    @Test
    fun refusesEmptyAndHuge() {
        assertFalse(PdfBudget.canExtractInMemory(0))
        assertFalse(PdfBudget.canExtractInMemory(PdfBudget.MAX_EXTRACT_BYTES + 1))
        assertTrue(PdfBudget.canExtractInMemory(1024))
        assertTrue(PdfBudget.tooLargeMessage().contains("32MB"))
    }
}

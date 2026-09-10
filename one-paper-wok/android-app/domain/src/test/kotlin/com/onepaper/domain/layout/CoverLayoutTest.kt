package com.onepaper.domain.layout

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class CoverLayoutTest {
    @Test
    fun coverScreenIsNarrowestWidth() {
        assertTrue(CoverLayout.isCoverLike(312))
        assertFalse(CoverLayout.isCoverLike(411))
    }

    @Test
    fun phoneIsCompactInnerIsWide() {
        assertTrue(CoverLayout.isCompact(360))
        assertFalse(CoverLayout.isCompact(412))
        assertTrue(CoverLayout.isWide(600))
        assertFalse(CoverLayout.isWide(411))
    }
}

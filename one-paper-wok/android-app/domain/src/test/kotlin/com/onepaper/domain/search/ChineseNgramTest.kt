package com.onepaper.domain.search

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class ChineseNgramTest {
    private val page = "把书当食材，整理当慢烹，成果当出煲，新思考当回煲。"

    @Test
    fun exactSubstringHits() {
        assertTrue(ChineseNgram.matches(page, "慢烹"))
        assertTrue(ChineseNgram.matches(page, "回煲"))
    }

    @Test
    fun trigramRecallsWithoutWhitespaceWords() {
        assertTrue(ChineseNgram.matches(page, "整理当慢烹"))
        assertFalse(ChineseNgram.matches(page, "量子纠缠"))
    }

    @Test
    fun tokensAreCharacterNgramsNotEnglishWords() {
        val tokens = ChineseNgram.tokens("慢烹回煲")
        assertTrue(tokens.contains("慢烹回"))
        assertTrue(tokens.contains("烹回煲"))
        assertFalse(tokens.contains("慢烹回煲"))
    }
}

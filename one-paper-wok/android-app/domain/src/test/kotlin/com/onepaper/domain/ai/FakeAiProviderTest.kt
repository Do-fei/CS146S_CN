package com.onepaper.domain.ai

import com.onepaper.domain.citation.Citation
import com.onepaper.domain.citation.ContentLocator
import com.onepaper.domain.citation.TextQuote
import kotlinx.coroutines.runBlocking
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class FakeAiProviderTest {
    private val provider = FakeAiProvider()

    @Test
    fun refusesWholeBookWhenOnlyOneChapterImported() = runBlocking {
        val answer = provider.answer(
            CompanionRequest(
                bookId = "b1",
                question = "全书在讲什么？给完整结论。",
                scope = ScopeBar(importedChapterCount = 1, importedPageCount = 8, claimsWholeBook = false),
                evidence = listOf(
                    Citation(
                        sourceDocumentId = "ed1",
                        contentVersion = "v1",
                        locator = ContentLocator.Epub("ch1", 0.1, TextQuote("慢烹")),
                        quote = "慢烹",
                    ),
                ),
            ),
        )
        assertTrue(answer.refusedWholeBookConclusion)
        assertTrue(answer.insufficientEvidence)
        assertTrue(answer.text.contains("部分"))
    }

    @Test
    fun wholeBookPdfScopeAllowsPagesWithoutChapters() = runBlocking {
        val scope = ScopeBar(importedChapterCount = 0, importedPageCount = 43, claimsWholeBook = true)
        val answer = provider.answer(
            CompanionRequest(
                bookId = "pdf",
                question = "这一页在讲什么？",
                scope = scope,
                evidence = listOf(
                    Citation(
                        sourceDocumentId = "ed-pdf",
                        contentVersion = "v1",
                        locator = ContentLocator.PdfPageRect(0, 0.0, 0.0, 1.0, 1.0, TextQuote("慢烹")),
                        quote = "慢烹",
                    ),
                ),
            ),
        )
        assertTrue(!answer.refusedWholeBookConclusion)
        assertTrue(answer.text.contains("慢烹"))
    }

    @Test
    fun streamingEmitsThenCompletes() = runBlocking {
        val deltas = mutableListOf<String>()
        val answer = provider.answerStreaming(
            CompanionRequest(
                bookId = "b1",
                question = "这一句在讲什么？",
                scope = ScopeBar(1, 0, false),
                evidence = listOf(
                    Citation(
                        sourceDocumentId = "ed1",
                        contentVersion = "v1",
                        locator = ContentLocator.Epub("ch1", 0.1, TextQuote("慢烹")),
                        quote = "慢烹",
                    ),
                ),
            ),
        ) { deltas.add(it) }
        assertTrue(deltas.isNotEmpty())
        assertEquals(answer.text, deltas.last())
    }
}

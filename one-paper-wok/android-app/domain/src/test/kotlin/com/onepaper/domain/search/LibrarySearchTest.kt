package com.onepaper.domain.search

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class LibrarySearchTest {
    private val docs = listOf(
        SearchDocument("b1", LibraryHitKind.BOOK, "慢烹之书", "项目组"),
        SearchDocument("c1", LibraryHitKind.CHAPTER, "第一章", "把书读薄，把思考养厚", bookId = "b1", editionId = "e1"),
        SearchDocument("n1", LibraryHitKind.NOTE, "我的稿", "只记下这一句。", noteId = "n1"),
        SearchDocument("h1", LibraryHitKind.HIGHLIGHT, "划线", "成果带走。", bookId = "b1"),
    )

    @Test
    fun findsAcrossKindsWithoutPretendingVectors() {
        val hits = LibrarySearch.rank(docs, "思考养厚")
        assertEquals(listOf("c1"), hits.map { it.id })
        assertTrue(hits.single().snippet.contains("思考养厚"))
    }

    @Test
    fun titleBoostsBookHit() {
        val hits = LibrarySearch.rank(docs, "慢烹之书")
        assertEquals("b1", hits.first().id)
        assertEquals(LibraryHitKind.BOOK, hits.first().kind)
    }

    @Test
    fun blankQueryIsEmpty() {
        assertTrue(LibrarySearch.rank(docs, "   ").isEmpty())
    }
}

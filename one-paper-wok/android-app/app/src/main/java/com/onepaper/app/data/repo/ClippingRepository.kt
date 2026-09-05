package com.onepaper.app.data.repo

import android.content.ContentResolver
import android.net.Uri
import com.onepaper.app.data.local.BookDao
import com.onepaper.domain.clipping.ClippingParser
import com.onepaper.domain.model.Coverage
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ClippingRepository @Inject constructor(
    private val library: LibraryRepository,
    private val notes: NoteRepository,
    private val projects: ProjectRepository,
    private val books: BookDao,
) {
    suspend fun importUri(resolver: ContentResolver, uri: Uri): ImportOutcome {
        val raw = resolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() }
            ?: return ImportOutcome("", "", "无法读取这份文件。")
        return importText(raw)
    }

    suspend fun importText(raw: String): ImportOutcome {
        val items = ClippingParser.parse(raw)
        if (items.isEmpty()) {
            return ImportOutcome(
                "",
                "",
                "无法识别这份书摘。请用 Kindle「我的剪贴」或微信读书导出的笔记文本，不要登录它们的账号。",
            )
        }
        val grouped = items.groupBy { it.bookTitle.trim() }.filterKeys { it.isNotBlank() }
        var lastBook = ""
        var lastEdition = ""
        var highlightCount = 0
        grouped.forEach { (title, rows) ->
            val author = rows.firstOrNull { it.author.isNotBlank() }?.author.orEmpty()
            val existing = books.findActiveByTitle(title)
            val bookId: String
            val editionId: String
            if (existing != null) {
                bookId = existing.id
                editionId = library.editionsOf(bookId).firstOrNull()?.id ?: return@forEach
                if (existing.author.isBlank() && author.isNotBlank()) {
                    library.updateAuthor(bookId, author)
                }
            } else {
                val body = rows.map { it.quote }.filter { it.isNotBlank() }
                    .joinToString("\n\n") { "「${it.trim()}」" }
                    .ifBlank { rows.map { it.note }.filter { it.isNotBlank() }.joinToString("\n") }
                    .ifBlank { "书摘摘录" }
                val created = library.importPlainText(
                    title = title,
                    author = author,
                    body = body,
                    coverage = Coverage.EXCERPT,
                    originalName = "clippings.txt",
                )
                bookId = created.bookId
                editionId = created.editionId
                val chapter = library.chaptersOf(editionId).firstOrNull()?.plainText.orEmpty()
                projects.ensureForBook(bookId, title, chapter)
            }
            rows.forEach { row ->
                if (row.quote.isNotBlank()) {
                    library.addHighlight(bookId, editionId, "clippings.txt", row.quote, 0.0)
                    highlightCount += 1
                }
                val draft = row.note.ifBlank { row.quote }
                if (draft.isNotBlank()) {
                    notes.save(
                        id = null,
                        bookId = bookId,
                        title = draft.take(24).ifBlank { "书摘" },
                        userDraft = draft,
                        recognitionDraft = null,
                        imageRelPath = null,
                        sourceBound = row.quote.isNotBlank(),
                        locatorJson = null,
                    )
                }
            }
            lastBook = bookId
            lastEdition = editionId
        }
        if (lastBook.isBlank()) {
            return ImportOutcome("", "", "书摘没有落到任何一本书上。")
        }
        return ImportOutcome(
            bookId = lastBook,
            editionId = lastEdition,
            detail = "已汇入 ${grouped.size} 本书的书摘，划线 $highlightCount 条。按摘录建档，不是全书。",
        )
    }
}

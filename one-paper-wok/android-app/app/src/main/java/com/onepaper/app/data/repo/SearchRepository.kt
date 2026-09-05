package com.onepaper.app.data.repo

import com.onepaper.app.data.local.AnnotationDao
import com.onepaper.app.data.local.BookDao
import com.onepaper.app.data.local.ChapterDao
import com.onepaper.app.data.local.EditionDao
import com.onepaper.app.data.local.NoteDao
import com.onepaper.app.data.local.ProjectDao
import com.onepaper.app.data.local.SectionDao
import com.onepaper.domain.search.LibraryHit
import com.onepaper.domain.search.LibraryHitKind
import com.onepaper.domain.search.LibrarySearch
import com.onepaper.domain.search.SearchDocument
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SearchRepository @Inject constructor(
    private val books: BookDao,
    private val editions: EditionDao,
    private val chapters: ChapterDao,
    private val notes: NoteDao,
    private val annotations: AnnotationDao,
    private val projects: ProjectDao,
    private val sections: SectionDao,
) {
    suspend fun search(query: String): List<LibraryHit> {
        if (query.isBlank()) return emptyList()
        val editionById = editions.all().associateBy { it.id }
        val projectById = projects.all().associateBy { it.id }
        val docs = mutableListOf<SearchDocument>()
        books.active().forEach { book ->
            docs += SearchDocument(
                id = "book-${book.id}",
                kind = LibraryHitKind.BOOK,
                title = book.title,
                body = book.author,
                bookId = book.id,
            )
        }
        chapters.all().forEach { chapter ->
            val edition = editionById[chapter.editionId]
            docs += SearchDocument(
                id = "chapter-${chapter.id}",
                kind = LibraryHitKind.CHAPTER,
                title = chapter.title,
                body = chapter.plainText,
                bookId = edition?.bookId,
                editionId = chapter.editionId,
                href = chapter.href,
            )
        }
        notes.all().forEach { note ->
            docs += SearchDocument(
                id = "note-${note.id}",
                kind = LibraryHitKind.NOTE,
                title = note.title.ifBlank { "我的稿" },
                body = note.userDraft,
                bookId = note.bookId,
                noteId = note.id,
                locatorJson = note.locatorJson,
            )
        }
        annotations.all().forEach { mark ->
            docs += SearchDocument(
                id = "mark-${mark.id}",
                kind = LibraryHitKind.HIGHLIGHT,
                title = mark.quote.take(24).ifBlank { "划线" },
                body = mark.quote,
                bookId = mark.bookId,
                editionId = mark.editionId,
                locatorJson = mark.locatorJson,
            )
        }
        sections.all().forEach { section ->
            val project = projectById[section.projectId]
            docs += SearchDocument(
                id = "section-${section.id}",
                kind = LibraryHitKind.PAPER,
                title = section.title,
                body = section.body,
                bookId = project?.bookId,
                projectId = section.projectId,
            )
        }
        return LibrarySearch.rank(docs, query)
    }
}

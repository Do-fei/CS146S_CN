package com.onepaper.domain.search

/** 库内本机检索：n-gram + 子串。不是向量语义，不加模型。 */
enum class LibraryHitKind {
    BOOK,
    CHAPTER,
    NOTE,
    HIGHLIGHT,
    PAPER,
}

data class SearchDocument(
    val id: String,
    val kind: LibraryHitKind,
    val title: String,
    val body: String,
    val bookId: String? = null,
    val editionId: String? = null,
    val projectId: String? = null,
    val noteId: String? = null,
    val locatorJson: String? = null,
    val href: String? = null,
    val pageIndex: Int? = null,
)

data class LibraryHit(
    val id: String,
    val kind: LibraryHitKind,
    val title: String,
    val snippet: String,
    val score: Int,
    val bookId: String? = null,
    val editionId: String? = null,
    val projectId: String? = null,
    val noteId: String? = null,
    val locatorJson: String? = null,
    val href: String? = null,
    val pageIndex: Int? = null,
)

object LibrarySearch {
    const val DEFAULT_CAP = 24

    fun rank(
        documents: List<SearchDocument>,
        query: String,
        cap: Int = DEFAULT_CAP,
    ): List<LibraryHit> {
        val q = query.trim()
        if (q.isEmpty()) return emptyList()
        return documents
            .mapNotNull { doc ->
                val hay = doc.title + "\n" + doc.body
                if (!ChineseNgram.matches(hay, q)) return@mapNotNull null
                val score = ChineseNgram.rank(hay, q) + if (ChineseNgram.matches(doc.title, q)) 80 else 0
                LibraryHit(
                    id = doc.id,
                    kind = doc.kind,
                    title = doc.title.ifBlank { kindLabel(doc.kind) },
                    snippet = snippet(doc.body.ifBlank { doc.title }, q),
                    score = score,
                    bookId = doc.bookId,
                    editionId = doc.editionId,
                    projectId = doc.projectId,
                    noteId = doc.noteId,
                    locatorJson = doc.locatorJson,
                    href = doc.href,
                    pageIndex = doc.pageIndex,
                )
            }
            .sortedWith(compareByDescending<LibraryHit> { it.score }.thenBy { it.title })
            .take(cap)
    }

    fun kindLabel(kind: LibraryHitKind): String = when (kind) {
        LibraryHitKind.BOOK -> "书"
        LibraryHitKind.CHAPTER -> "原文"
        LibraryHitKind.NOTE -> "我的稿"
        LibraryHitKind.HIGHLIGHT -> "划线"
        LibraryHitKind.PAPER -> "一纸"
    }

    private fun snippet(body: String, query: String): String {
        val compact = body.replace(Regex("\\s+"), " ").trim()
        if (compact.isEmpty()) return ""
        val idx = compact.indexOf(query.trim())
        if (idx < 0) return compact.take(80)
        val start = (idx - 16).coerceAtLeast(0)
        return compact.substring(start).take(80)
    }
}

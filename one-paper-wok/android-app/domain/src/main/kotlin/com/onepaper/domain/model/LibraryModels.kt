package com.onepaper.domain.model

enum class Coverage {
    WHOLE_BOOK,
    EXCERPT,
}

enum class SourceKind {
    EPUB,
    PDF,
    IMAGES,
    PLAIN_TEXT,
}

data class BookRecord(
    val id: String,
    val title: String,
    val author: String,
    val coverage: Coverage,
    val createdAtEpochMs: Long,
)

data class EditionRecord(
    val id: String,
    val bookId: String,
    val sourceKind: SourceKind,
    val originalName: String,
    val checksum: String,
    val contentVersion: String,
    val relativePath: String,
    val pageCount: Int,
    val drmOrEncrypted: Boolean,
)

data class NoteRecord(
    val id: String,
    val bookId: String?,
    val title: String,
    val userDraft: String,
    val recognitionDraft: String?,
    val imageRelPath: String?,
    val sourceBound: Boolean,
    val updatedAtEpochMs: Long,
)

data class IdempotencyKey(val clientJobId: String)

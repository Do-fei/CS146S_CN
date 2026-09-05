package com.onepaper.app.data.local

import androidx.room.Entity
import androidx.room.Index
import androidx.room.PrimaryKey
import kotlinx.serialization.Serializable

@Serializable
@Entity(tableName = "books", indices = [Index("title")])
data class BookEntity(
    @PrimaryKey val id: String,
    val title: String,
    val author: String,
    val coverage: String,
    val createdAt: Long,
    val deletedAt: Long? = null,
    val coverRelPath: String? = null,
)

@Serializable
@Entity(tableName = "editions", indices = [Index("bookId"), Index("checksum")])
data class EditionEntity(
    @PrimaryKey val id: String,
    val bookId: String,
    val sourceKind: String,
    val originalName: String,
    val checksum: String,
    val contentVersion: String,
    val relativePath: String,
    val pageCount: Int,
    val drmOrEncrypted: Boolean,
)

@Serializable
@Entity(tableName = "chapters", indices = [Index("editionId")])
data class ChapterEntity(
    @PrimaryKey val id: String,
    val editionId: String,
    val href: String,
    val title: String,
    val plainText: String,
    val sortIndex: Int,
    val contentVersion: String,
)

@Serializable
@Entity(tableName = "pages", indices = [Index("editionId")])
data class PageEntity(
    @PrimaryKey val id: String,
    val editionId: String,
    val index: Int,
    val imageRelPath: String?,
    val ocrText: String?,
    val recognitionDraft: String?,
    val embeddedText: String? = null,
    val hasTextLayer: Boolean = false,
    val ocrBoxesJson: String? = null,
)

@Serializable
@Entity(tableName = "notes")
data class NoteEntity(
    @PrimaryKey val id: String,
    val bookId: String?,
    val title: String,
    val userDraft: String,
    val recognitionDraft: String?,
    val imageRelPath: String?,
    val sourceBound: Boolean,
    val locatorJson: String?,
    val updatedAt: Long,
)

@Serializable
@Entity(tableName = "annotations")
data class AnnotationEntity(
    @PrimaryKey val id: String,
    val bookId: String,
    val editionId: String,
    val locatorJson: String,
    val quote: String,
    val note: String,
    val layer: String,
    val createdAt: Long,
)

@Serializable
@Entity(tableName = "reading_positions")
data class ReadingPositionEntity(
    @PrimaryKey val editionId: String,
    val locatorJson: String,
    val updatedAt: Long,
)

@Serializable
@Entity(tableName = "projects")
data class ProjectEntity(
    @PrimaryKey val id: String,
    val bookId: String,
    val title: String,
    val revisionId: String,
    val revision: Long,
)

@Serializable
@Entity(tableName = "project_sections", indices = [Index("projectId")])
data class ProjectSectionEntity(
    @PrimaryKey val id: String,
    val projectId: String,
    val sectionId: String,
    val kind: String,
    val title: String,
    val body: String,
    val revision: Long,
    val userLocked: Boolean,
    val sortIndex: Int,
)

@Entity(tableName = "proposals")
data class ProposalEntity(
    @PrimaryKey val id: String,
    val projectId: String,
    val baseRevisionId: String,
    val createdAt: Long,
    val status: String,
)

@Entity(tableName = "proposal_items")
data class ProposalItemEntity(
    @PrimaryKey val id: String,
    val proposalId: String,
    val sectionId: String,
    val op: String,
    val proposedTitle: String?,
    val proposedBody: String?,
    val basedOnSectionRevision: Long,
    val decision: String?,
    val editedBody: String?,
)

@Serializable
@Entity(tableName = "conversations")
data class ConversationEntity(
    @PrimaryKey val id: String,
    val bookId: String,
    val title: String,
    val updatedAt: Long,
)

@Serializable
@Entity(tableName = "messages")
data class MessageEntity(
    @PrimaryKey val id: String,
    val conversationId: String,
    val role: String,
    val text: String,
    val insufficientEvidence: Boolean,
    val createdAt: Long,
    val quote: String? = null,
    val locatorJson: String? = null,
    val editionId: String? = null,
)

@Entity(tableName = "jobs")
data class JobEntity(
    @PrimaryKey val clientJobId: String,
    val bookId: String?,
    val kind: String,
    val status: String,
    val stage: String,
    val unitDone: Int,
    val unitTotal: Int,
    val message: String,
    val durableFilesPresent: Boolean,
    val attempt: Int,
    val updatedAt: Long,
)

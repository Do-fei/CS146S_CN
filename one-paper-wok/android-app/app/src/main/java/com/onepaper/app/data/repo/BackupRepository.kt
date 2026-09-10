package com.onepaper.app.data.repo

import android.content.ContentResolver
import android.net.Uri
import com.onepaper.app.data.files.PrivateStore
import com.onepaper.app.data.local.AnnotationDao
import com.onepaper.app.data.local.AnnotationEntity
import com.onepaper.app.data.local.BackupDao
import com.onepaper.app.data.local.BookDao
import com.onepaper.app.data.local.BookEntity
import com.onepaper.app.data.local.ChapterDao
import com.onepaper.app.data.local.ChapterEntity
import com.onepaper.app.data.local.ConversationDao
import com.onepaper.app.data.local.ConversationEntity
import com.onepaper.app.data.local.EditionDao
import com.onepaper.app.data.local.EditionEntity
import com.onepaper.app.data.local.MessageEntity
import com.onepaper.app.data.local.NoteDao
import com.onepaper.app.data.local.NoteEntity
import com.onepaper.app.data.local.PageDao
import com.onepaper.app.data.local.PageEntity
import com.onepaper.app.data.local.PositionDao
import com.onepaper.app.data.local.ProjectDao
import com.onepaper.app.data.local.ProjectEntity
import com.onepaper.app.data.local.ProjectSectionEntity
import com.onepaper.app.data.local.ReadingPositionEntity
import com.onepaper.app.data.local.SectionDao
import com.onepaper.domain.backup.BackupFileRef
import com.onepaper.domain.backup.BackupManifest
import com.onepaper.domain.backup.BackupPaths
import com.onepaper.domain.backup.BackupPolicy
import com.onepaper.domain.backup.BackupZip
import com.onepaper.domain.backup.RestoreOutcome
import com.onepaper.domain.paper.PaperDraftInput
import com.onepaper.domain.paper.PaperShareDraft
import com.onepaper.domain.recook.SectionKind
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

@Serializable
data class LibraryBackup(
    val manifest: BackupManifest,
    val books: List<BookEntity>,
    val editions: List<EditionEntity>,
    val chapters: List<ChapterEntity>,
    val notes: List<NoteEntity>,
    val projects: List<ProjectEntity>,
    val sections: List<ProjectSectionEntity>,
    val annotations: List<AnnotationEntity> = emptyList(),
    val positions: List<ReadingPositionEntity> = emptyList(),
    val pages: List<PageEntity> = emptyList(),
    val conversations: List<ConversationEntity> = emptyList(),
    val messages: List<MessageEntity> = emptyList(),
    val files: List<BackupFileRef> = emptyList(),
)

@Singleton
class BackupRepository @Inject constructor(
    private val backupDao: BackupDao,
    private val books: BookDao,
    private val editions: EditionDao,
    private val chapters: ChapterDao,
    private val notes: NoteDao,
    private val projects: ProjectDao,
    private val sections: SectionDao,
    private val annotations: AnnotationDao,
    private val pages: PageDao,
    private val positions: PositionDao,
    private val conversations: ConversationDao,
    private val store: PrivateStore,
) {
    private val json = Json { prettyPrint = true; ignoreUnknownKeys = true; encodeDefaults = true }

    suspend fun exportArchive(): File {
        val payload = snapshot()
        check(!payload.manifest.includesTokens)
        val dest = store.exportFile("onepaper-backup.zip")
        val filePairs = payload.files.mapNotNull { ref ->
            val file = store.file(ref.relativePath)
            if (file.isFile) ref.relativePath to file else null
        }
        BackupZip.write(dest, json.encodeToString(payload), filePairs)
        return dest
    }

    suspend fun exportJson(): File {
        val payload = snapshot()
        check(!payload.manifest.includesTokens)
        val file = store.exportFile("onepaper-backup.json")
        file.writeText(json.encodeToString(payload))
        return file
    }

    suspend fun exportToUri(resolver: ContentResolver, uri: Uri): String {
        val file = exportArchive()
        resolver.openOutputStream(uri)?.use { out ->
            file.inputStream().use { input -> input.copyTo(out) }
        } ?: error("无法写入所选文件")
        return uri.toString()
    }

    suspend fun restoreFromUri(resolver: ContentResolver, uri: Uri): RestoreOutcome {
        val incoming = store.exportFile("restore-incoming.bin")
        resolver.openInputStream(uri)?.use { input ->
            incoming.outputStream().use { input.copyTo(it) }
        } ?: error("无法读取所选文件")
        return restoreFile(incoming)
    }

    suspend fun preview(raw: String): BackupManifest {
        val parsed = json.decodeFromString<LibraryBackup>(raw)
        check(!parsed.manifest.includesTokens) { "拒绝含 token 的备份" }
        return parsed.manifest
    }

    fun stagingFile(name: String): File = store.exportFile(name)

    suspend fun restore(raw: String): RestoreOutcome {
        val parsed = decodeCatalog(raw)
        applyCatalog(parsed)
        return RestoreOutcome(
            parsed.manifest,
            oldCatalogOnly = true,
            restoredFileCount = 0,
            missingFileCount = parsed.files.size,
        )
    }

    suspend fun restoreFile(file: File): RestoreOutcome {
        return if (BackupZip.looksLikeZip(file)) {
            val parsed = decodeCatalog(BackupZip.readCatalog(file))
            applyCatalog(parsed)
            val written = BackupZip.extractFiles(file, store.filesDir())
            val missing = parsed.files.count { !store.file(it.relativePath).isFile }
            RestoreOutcome(parsed.manifest, oldCatalogOnly = false, restoredFileCount = written, missingFileCount = missing)
        } else {
            restore(file.readText())
        }
    }

    suspend fun exportProjectMarkdown(projectId: String, includePrivateNotes: Boolean = false): File {
        val draft = paperDraft(projectId, includePrivateNotes)
        val file = store.exportFile("onepaper-${projectId.take(8)}.md")
        file.writeText(PaperShareDraft.markdown(draft))
        return file
    }

    suspend fun exportProjectPlain(projectId: String, includePrivateNotes: Boolean): File {
        val draft = paperDraft(projectId, includePrivateNotes)
        val file = store.exportFile("onepaper-${projectId.take(8)}.txt")
        file.writeText(PaperShareDraft.plain(draft))
        return file
    }

    suspend fun paperDraft(projectId: String, includePrivateNotes: Boolean): PaperDraftInput {
        val project = projects.get(projectId)
        val rows = sections.forProject(projectId)
        val quotes = project?.bookId?.let { annotations.forBook(it) }?.map { it.quote }?.filter { it.isNotBlank() }.orEmpty()
        val excerpt = rows.firstOrNull { it.kind == SectionKind.EXCERPT.name }?.body.orEmpty()
        val source = (listOf(excerpt).filter { it.isNotBlank() } + quotes).distinct()
        val private = if (includePrivateNotes) {
            notes.all().filter { it.bookId == project?.bookId }.map { it.userDraft }.filter { it.isNotBlank() }
        } else {
            emptyList()
        }
        return PaperDraftInput(
            title = project?.title ?: "一纸",
            sourceQuotes = source,
            aiSections = rows.filter { it.kind == SectionKind.ESSENCE.name || it.kind == SectionKind.CHAPTER.name }
                .map { it.title to it.body },
            userSections = rows.filter { it.kind == SectionKind.UNDERSTANDING.name }
                .map { it.title to it.body },
            explore = rows.firstOrNull { it.kind == SectionKind.EXPLORE.name }?.body.orEmpty(),
            changelog = rows.firstOrNull { it.kind == SectionKind.CHANGELOG.name }?.body.orEmpty(),
            privateNotes = private,
        )
    }

    private suspend fun snapshot(): LibraryBackup {
        val bookRows = backupDao.allBooks()
        val editionRows = backupDao.allEditions()
        val pageRows = pages.all()
        val noteRows = backupDao.allNotes()
        val annotationRows = annotations.all()
        val paths = BackupPaths.collect(
            editionRows.map { it.relativePath } +
                bookRows.map { it.coverRelPath } +
                pageRows.map { it.imageRelPath } +
                noteRows.map { it.imageRelPath },
        )
        val fileRefs = paths.map { relative ->
            val file = store.file(relative)
            BackupFileRef(
                relativePath = relative,
                size = if (file.isFile) file.length() else 0,
                sha256 = if (file.isFile) store.sha256(file) else null,
            )
        }
        val present = fileRefs.count { it.size > 0 }
        return LibraryBackup(
            manifest = BackupPolicy.sanitize(
                BackupManifest(
                    formatVersion = 2,
                    createdAtEpochMs = System.currentTimeMillis(),
                    appVersion = "0.1.0-delivery",
                    bookCount = bookRows.size,
                    noteCount = noteRows.size,
                    projectCount = backupDao.allProjects().size,
                    includesTokens = false,
                    includesPrivateNotes = true,
                    includesLibraryFiles = present > 0,
                    fileCount = present,
                    annotationCount = annotationRows.size,
                ),
            ),
            books = bookRows,
            editions = editionRows,
            chapters = chapters.all(),
            notes = noteRows,
            projects = backupDao.allProjects(),
            sections = backupDao.allSections(),
            annotations = annotationRows,
            positions = positions.all(),
            pages = pageRows,
            conversations = conversations.allConversations(),
            messages = conversations.allMessages(),
            files = fileRefs,
        )
    }

    private fun decodeCatalog(raw: String): LibraryBackup {
        val parsed = json.decodeFromString<LibraryBackup>(raw)
        check(!parsed.manifest.includesTokens) { "拒绝含 token 的备份" }
        return parsed
    }

    private suspend fun applyCatalog(parsed: LibraryBackup) {
        parsed.books.forEach { books.upsert(it) }
        parsed.editions.forEach { editions.upsert(it) }
        if (parsed.chapters.isNotEmpty()) chapters.upsertAll(parsed.chapters)
        parsed.notes.forEach { notes.upsert(it) }
        parsed.projects.forEach { projects.upsert(it) }
        if (parsed.sections.isNotEmpty()) sections.upsertAll(parsed.sections)
        parsed.annotations.forEach { annotations.upsert(it) }
        parsed.positions.forEach { positions.upsert(it) }
        if (parsed.pages.isNotEmpty()) pages.upsertAll(parsed.pages)
        parsed.conversations.forEach { conversations.upsert(it) }
        parsed.messages.forEach { conversations.upsertMessage(it) }
    }
}

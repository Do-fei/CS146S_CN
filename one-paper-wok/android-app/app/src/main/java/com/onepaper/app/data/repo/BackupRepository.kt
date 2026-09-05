package com.onepaper.app.data.repo

import com.onepaper.app.data.files.PrivateStore
import com.onepaper.app.data.local.BackupDao
import com.onepaper.app.data.local.BookDao
import com.onepaper.app.data.local.BookEntity
import com.onepaper.app.data.local.ChapterDao
import com.onepaper.app.data.local.ChapterEntity
import com.onepaper.app.data.local.EditionDao
import com.onepaper.app.data.local.EditionEntity
import com.onepaper.app.data.local.NoteDao
import com.onepaper.app.data.local.NoteEntity
import com.onepaper.app.data.local.ProjectDao
import com.onepaper.app.data.local.ProjectEntity
import com.onepaper.app.data.local.ProjectSectionEntity
import com.onepaper.app.data.local.SectionDao
import android.content.ContentResolver
import android.net.Uri
import com.onepaper.app.data.local.AnnotationDao
import com.onepaper.domain.backup.BackupManifest
import com.onepaper.domain.backup.BackupPolicy
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
    private val store: PrivateStore,
) {
    private val json = Json { prettyPrint = true; ignoreUnknownKeys = true }

    suspend fun exportJson(): File {
        val payload = LibraryBackup(
            manifest = BackupPolicy.sanitize(
                BackupManifest(
                    createdAtEpochMs = System.currentTimeMillis(),
                    appVersion = "0.1.0-delivery",
                    bookCount = backupDao.allBooks().size,
                    noteCount = backupDao.allNotes().size,
                    projectCount = backupDao.allProjects().size,
                    includesTokens = false, // DeepSeek Key 在 EncryptedSharedPreferences，不在此包
                    includesPrivateNotes = true,
                ),
            ),
            books = backupDao.allBooks(),
            editions = backupDao.allEditions(),
            chapters = chapters.all(),
            notes = backupDao.allNotes(),
            projects = backupDao.allProjects(),
            sections = backupDao.allSections(),
        )
        check(!payload.manifest.includesTokens)
        val file = store.exportFile("onepaper-backup.json")
        file.writeText(json.encodeToString(payload))
        return file
    }

    suspend fun exportToUri(resolver: ContentResolver, uri: Uri): String {
        val file = exportJson()
        resolver.openOutputStream(uri)?.use { out ->
            file.inputStream().use { input -> input.copyTo(out) }
        } ?: error("无法写入所选文件")
        return uri.toString()
    }

    suspend fun restoreFromUri(resolver: ContentResolver, uri: Uri): BackupManifest {
        val raw = resolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() }
            ?: error("无法读取所选文件")
        restore(raw)
        return preview(raw)
    }

    suspend fun preview(raw: String): BackupManifest {
        val parsed = json.decodeFromString<LibraryBackup>(raw)
        check(!parsed.manifest.includesTokens) { "拒绝含 token 的备份" }
        return parsed.manifest
    }

    suspend fun restore(raw: String) {
        val parsed = json.decodeFromString<LibraryBackup>(raw)
        check(!parsed.manifest.includesTokens) { "拒绝含 token 的备份" }
        parsed.books.forEach { books.upsert(it) }
        parsed.editions.forEach { editions.upsert(it) }
        chapters.upsertAll(parsed.chapters)
        parsed.notes.forEach { notes.upsert(it) }
        parsed.projects.forEach { projects.upsert(it) }
        sections.upsertAll(parsed.sections)
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
}

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
import com.onepaper.domain.backup.BackupManifest
import com.onepaper.domain.backup.BackupPolicy
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
                    includesTokens = false,
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

    suspend fun exportProjectMarkdown(projectId: String): File {
        val project = projects.get(projectId)
        val body = buildString {
            appendLine("# ${project?.title ?: "一纸项目"}")
            appendLine()
            appendLine("_导出默认不含阅读器私人批注。_")
            appendLine()
            sections.forProject(projectId).forEach { section ->
                appendLine("## ${section.title}")
                appendLine()
                appendLine(section.body)
                appendLine()
            }
        }
        val file = store.exportFile("onepaper-${projectId.take(8)}.md")
        file.writeText(body)
        return file
    }
}

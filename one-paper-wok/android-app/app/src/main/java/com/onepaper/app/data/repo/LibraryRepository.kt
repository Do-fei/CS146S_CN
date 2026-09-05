package com.onepaper.app.data.repo

import android.content.Context
import android.content.Intent
import android.net.Uri
import com.onepaper.app.data.files.PrivateStore
import com.onepaper.app.data.importing.EpubTextExtractor
import com.onepaper.app.data.importing.ImportType
import com.onepaper.app.data.importing.PdfGuard
import com.onepaper.app.data.importing.PdfPages
import com.onepaper.app.data.local.AnnotationDao
import com.onepaper.app.data.local.AnnotationEntity
import com.onepaper.app.data.local.BookDao
import com.onepaper.app.data.local.BookEntity
import com.onepaper.app.data.local.ChapterDao
import com.onepaper.app.data.local.ChapterEntity
import com.onepaper.app.data.local.EditionDao
import com.onepaper.app.data.local.EditionEntity
import com.onepaper.app.data.local.JobDao
import com.onepaper.app.data.local.JobEntity
import com.onepaper.app.data.local.PageDao
import com.onepaper.app.data.local.PageEntity
import com.onepaper.app.data.local.PositionDao
import com.onepaper.app.data.local.ReadingPositionEntity
import com.onepaper.domain.citation.ContentLocator
import com.onepaper.domain.citation.LocatorCodec
import com.onepaper.domain.citation.TextQuote
import com.onepaper.domain.job.JobState
import com.onepaper.domain.job.JobStateMachine
import com.onepaper.domain.job.JobStatus
import com.onepaper.domain.model.Coverage
import com.onepaper.domain.model.SourceKind
import com.onepaper.domain.search.ChineseNgram
import dagger.hilt.android.qualifiers.ApplicationContext
import com.onepaper.domain.citation.ProgressSnapshot
import com.onepaper.domain.citation.ReadingProgress
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.combine
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

data class ImportOutcome(
    val bookId: String,
    val editionId: String,
    val rejectedReason: String? = null,
)

data class ShelfItem(
    val book: BookEntity,
    val editionId: String?,
    val progress: ProgressSnapshot,
)

@Singleton
class LibraryRepository @Inject constructor(
    @ApplicationContext private val context: Context,
    private val books: BookDao,
    private val editions: EditionDao,
    private val chapters: ChapterDao,
    private val pages: PageDao,
    private val annotations: AnnotationDao,
    private val positions: PositionDao,
    private val jobs: JobDao,
    private val store: PrivateStore,
) {
    private val machine = JobStateMachine()

    fun observeBooks(): Flow<List<BookEntity>> = books.observeActive()
    fun observeJobs(): Flow<List<JobEntity>> = jobs.observeAll()
    fun observeEditions(): Flow<List<EditionEntity>> = editions.observeAll()
    fun observePositions(): Flow<List<ReadingPositionEntity>> = positions.observeAll()

    fun observeShelfItems(): Flow<List<ShelfItem>> = combine(
        books.observeActive(),
        editions.observeAll(),
        positions.observeAll(),
    ) { bookList, editionList, positionList ->
        bookList.map { book ->
            val edition = editionList.firstOrNull { it.bookId == book.id }
            val position = edition?.let { item -> positionList.firstOrNull { it.editionId == item.id } }
            val locator = position?.locatorJson?.let { raw ->
                runCatching { LocatorCodec.decode(raw) }.getOrNull()
            }
            val total = edition?.pageCount?.takeIf { it > 0 } ?: 1
            ShelfItem(book, edition?.id, ReadingProgress.of(locator, total))
        }
    }

    suspend fun book(id: String) = books.get(id)
    suspend fun editionsOf(bookId: String) = editions.forBook(bookId)
    suspend fun edition(id: String) = editions.get(id)
    suspend fun chaptersOf(editionId: String) = chapters.forEdition(editionId)
    suspend fun pagesOf(editionId: String) = pages.forEdition(editionId)
    fun observeChapters(editionId: String) = chapters.observeForEdition(editionId)

    suspend fun ensureSeeded(): ImportOutcome? {
        if (books.activeCount() > 0) return null
        val text = context.assets.open("samples/excerpt.txt").bufferedReader().use { it.readText() }
        return importPlainText(
            title = "一纸书煲 · 授权摘录样本",
            author = "项目组",
            body = text,
            coverage = Coverage.EXCERPT,
            originalName = "excerpt.txt",
        )
    }

    suspend fun importFromUri(
        uri: Uri,
        displayName: String,
        coverage: Coverage,
        markExcerpt: Boolean,
    ): ImportOutcome {
        val editionId = UUID.randomUUID().toString()
        val jobId = "import-$editionId"
        var state = JobState(clientJobId = jobId, status = JobStatus.QUEUED)
        persistJob(state, null, "import")
        state = machine.start(state)
        persistJob(state, null, "import")

        persistReadPermission(uri)
        val incoming = ImportType.resolve(context, uri, displayName)
        val dest = context.contentResolver.openInputStream(uri)?.use { input ->
            store.copyIncoming(editionId, incoming.displayName, input)
        } ?: return ImportOutcome("", editionId, "无法读取文件")

        state = state.copy(durableFilesPresent = true)
        persistJob(state, null, "import")

        val kind = when {
            incoming.kind == SourceKind.EPUB -> SourceKind.EPUB
            incoming.kind == SourceKind.PDF -> SourceKind.PDF
            incoming.kind == SourceKind.IMAGES -> SourceKind.IMAGES
            incoming.displayName.endsWith(".epub", true) -> SourceKind.EPUB
            incoming.displayName.endsWith(".zip", true) && ImportType.sniffZipIsEpub(dest) -> SourceKind.EPUB
            dest.name.endsWith(".zip", true) && ImportType.sniffZipIsEpub(dest) -> SourceKind.EPUB
            else -> incoming.kind
        }
        val name = incoming.displayName
        val outcome = when (kind) {
            SourceKind.EPUB -> ingestEpub(dest, name, coverage, markExcerpt, editionId)
            SourceKind.PDF -> ingestPdf(dest, name, coverage, markExcerpt, editionId)
            SourceKind.PLAIN_TEXT -> ingestTextFile(dest, name, coverage, editionId)
            SourceKind.IMAGES -> ingestImage(dest, name, editionId)
        }
        if (outcome.rejectedReason != null) {
            persistJob(machine.fail(state, retryable = false, message = outcome.rejectedReason), outcome.bookId, "import")
        } else {
            persistJob(machine.complete(state.copy(unitDone = 1, unitTotal = 1, stage = "导入")), outcome.bookId, "import")
        }
        return outcome
    }

    suspend fun importPlainText(
        title: String,
        author: String,
        body: String,
        coverage: Coverage,
        originalName: String,
    ): ImportOutcome {
        val bookId = UUID.randomUUID().toString()
        val editionId = UUID.randomUUID().toString()
        val file = store.writeText(editionId, originalName, body)
        persistImported(
            bookId = bookId,
            editionId = editionId,
            title = title,
            author = author,
            coverage = coverage,
            kind = SourceKind.PLAIN_TEXT,
            originalName = originalName,
            fileRel = store.relative(file),
            checksum = store.sha256(file),
            chapterList = listOf(
                ChapterEntity(
                    id = UUID.randomUUID().toString(),
                    editionId = editionId,
                    href = originalName,
                    title = title,
                    plainText = body,
                    sortIndex = 0,
                    contentVersion = "v1",
                ),
            ),
            pageCount = 1,
        )
        return ImportOutcome(bookId, editionId)
    }

    private suspend fun ingestTextFile(
        file: java.io.File,
        name: String,
        coverage: Coverage,
        editionId: String,
    ): ImportOutcome {
        val body = file.readText()
        val bookId = UUID.randomUUID().toString()
        persistImported(
            bookId = bookId,
            editionId = editionId,
            title = name,
            author = "",
            coverage = coverage,
            kind = SourceKind.PLAIN_TEXT,
            originalName = name,
            fileRel = store.relative(file),
            checksum = store.sha256(file),
            chapterList = listOf(
                ChapterEntity(
                    id = UUID.randomUUID().toString(),
                    editionId = editionId,
                    href = name,
                    title = name,
                    plainText = body,
                    sortIndex = 0,
                    contentVersion = "v1",
                ),
            ),
            pageCount = 1,
        )
        return ImportOutcome(bookId, editionId)
    }

    private suspend fun ingestEpub(
        file: java.io.File,
        name: String,
        coverage: Coverage,
        markExcerpt: Boolean,
        editionId: String,
    ): ImportOutcome {
        if (EpubTextExtractor.isEncrypted(file)) {
            return ImportOutcome("", editionId, "拒绝绕过 DRM / 加密 EPUB")
        }
        val extracted = EpubTextExtractor.extract(file)
        if (extracted.isEmpty()) {
            return ImportOutcome("", editionId, "EPUB 里没有可抽出的文本")
        }
        val bookId = UUID.randomUUID().toString()
        val title = if (name.contains("onepaper-guide")) {
            "一纸书煲使用说明书"
        } else {
            extracted.first().title.ifBlank { prettyTitle(name, ".epub") }
        }
        persistImported(
            bookId = bookId,
            editionId = editionId,
            title = title,
            author = "",
            coverage = if (markExcerpt) Coverage.EXCERPT else coverage,
            kind = SourceKind.EPUB,
            originalName = name,
            fileRel = store.relative(file),
            checksum = store.sha256(file),
            chapterList = extracted.mapIndexed { idx, ch ->
                ChapterEntity(
                    id = UUID.randomUUID().toString(),
                    editionId = editionId,
                    href = ch.href,
                    title = ch.title,
                    plainText = ch.plainText,
                    sortIndex = idx,
                    contentVersion = "v1",
                )
            },
            pageCount = extracted.size,
        )
        return ImportOutcome(bookId, editionId)
    }

    private suspend fun ingestPdf(
        file: java.io.File,
        name: String,
        coverage: Coverage,
        markExcerpt: Boolean,
        editionId: String,
    ): ImportOutcome {
        if (PdfGuard.looksEncrypted(file)) {
            return ImportOutcome("", editionId, "拒绝绕过加密 PDF")
        }
        val pageCount = PdfPages.count(file)
        val bookId = UUID.randomUUID().toString()
        persistImported(
            bookId = bookId,
            editionId = editionId,
            title = prettyTitle(name, ".pdf"),
            author = "",
            coverage = if (markExcerpt) Coverage.EXCERPT else coverage,
            kind = SourceKind.PDF,
            originalName = name,
            fileRel = store.relative(file),
            checksum = store.sha256(file),
            chapterList = emptyList(),
            pageCount = pageCount,
        )
        if (pageCount > 0) {
            pages.upsertAll(
                (0 until pageCount).map { idx ->
                    PageEntity(
                        id = UUID.randomUUID().toString(),
                        editionId = editionId,
                        index = idx,
                        imageRelPath = store.relative(file),
                        ocrText = null,
                        recognitionDraft = null,
                    )
                },
            )
        }
        return ImportOutcome(bookId, editionId)
    }

    suspend fun importBundledEpub(): ImportOutcome {
        val editionId = UUID.randomUUID().toString()
        val dest = openAsset("samples/onepaper-guide.epub", editionId, "onepaper-guide.epub")
            ?: return ImportOutcome("", editionId, "随包说明书缺失")
        return ingestEpub(dest, "onepaper-guide.epub", Coverage.WHOLE_BOOK, markExcerpt = false, editionId)
    }

    suspend fun importBundledPdf(): ImportOutcome {
        val editionId = UUID.randomUUID().toString()
        val dest = openAsset("samples/onepaper-sample.pdf", editionId, "onepaper-sample.pdf")
            ?: return ImportOutcome("", editionId, "随包样页缺失")
        return ingestPdf(dest, "onepaper-sample.pdf", Coverage.WHOLE_BOOK, markExcerpt = false, editionId)
    }

    suspend fun importImages(uris: List<Uri>): ImportOutcome {
        if (uris.isEmpty()) return ImportOutcome("", "", "没有选择图片")
        val editionId = UUID.randomUUID().toString()
        val dests = uris.mapIndexedNotNull { idx, uri ->
            persistReadPermission(uri)
            val incoming = ImportType.resolve(context, uri, "page-${idx + 1}.jpg")
            context.contentResolver.openInputStream(uri)?.use { input ->
                store.copyIncoming(editionId, incoming.displayName.ifBlank { "page-${idx + 1}.jpg" }, input)
            }
        }
        if (dests.isEmpty()) return ImportOutcome("", editionId, "无法读取图片")
        val bookId = UUID.randomUUID().toString()
        persistImported(
            bookId = bookId,
            editionId = editionId,
            title = "自炊页 · ${dests.size} 张",
            author = "",
            coverage = Coverage.EXCERPT,
            kind = SourceKind.IMAGES,
            originalName = dests.first().name,
            fileRel = store.relative(dests.first()),
            checksum = store.sha256(dests.first()),
            chapterList = emptyList(),
            pageCount = dests.size,
        )
        pages.upsertAll(
            dests.mapIndexed { idx, file ->
                PageEntity(
                    id = UUID.randomUUID().toString(),
                    editionId = editionId,
                    index = idx,
                    imageRelPath = store.relative(file),
                    ocrText = null,
                    recognitionDraft = null,
                )
            },
        )
        return ImportOutcome(bookId, editionId)
    }

    private suspend fun ingestImage(file: java.io.File, name: String, editionId: String): ImportOutcome {
        val bookId = UUID.randomUUID().toString()
        persistImported(
            bookId = bookId,
            editionId = editionId,
            title = name,
            author = "",
            coverage = Coverage.EXCERPT,
            kind = SourceKind.IMAGES,
            originalName = name,
            fileRel = store.relative(file),
            checksum = store.sha256(file),
            chapterList = emptyList(),
            pageCount = 1,
        )
        pages.upsertAll(
            listOf(
                PageEntity(
                    id = UUID.randomUUID().toString(),
                    editionId = editionId,
                    index = 0,
                    imageRelPath = store.relative(file),
                    ocrText = null,
                    recognitionDraft = null,
                ),
            ),
        )
        return ImportOutcome(bookId, editionId)
    }

    private suspend fun persistImported(
        bookId: String,
        editionId: String,
        title: String,
        author: String,
        coverage: Coverage,
        kind: SourceKind,
        originalName: String,
        fileRel: String,
        checksum: String,
        chapterList: List<ChapterEntity>,
        pageCount: Int,
    ) {
        books.upsert(
            BookEntity(
                id = bookId,
                title = title,
                author = author,
                coverage = coverage.name,
                createdAt = System.currentTimeMillis(),
            ),
        )
        editions.upsert(
            EditionEntity(
                id = editionId,
                bookId = bookId,
                sourceKind = kind.name,
                originalName = originalName,
                checksum = checksum,
                contentVersion = "v1",
                relativePath = fileRel,
                pageCount = pageCount,
                drmOrEncrypted = false,
            ),
        )
        if (chapterList.isNotEmpty()) chapters.upsertAll(chapterList)
    }

    suspend fun softDeleteBook(bookId: String) {
        books.softDelete(bookId, System.currentTimeMillis())
    }

    suspend fun searchChapters(query: String): List<ChapterEntity> {
        if (query.isBlank()) return emptyList()
        return chapters.all().filter { ChineseNgram.matches(it.plainText + it.title, query) }
            .sortedByDescending { ChineseNgram.rank(it.plainText, query) }
    }

    suspend fun addHighlight(bookId: String, editionId: String, href: String, quote: String, progression: Double) {
        persistAnnotation(bookId, editionId, ContentLocator.Epub(href, progression, TextQuote(exact = quote)), quote)
    }

    suspend fun addHighlightPdf(bookId: String, editionId: String, pageIndex: Int, quote: String) {
        persistAnnotation(
            bookId,
            editionId,
            ContentLocator.PdfPageRect(pageIndex, 0.0, 0.0, 1.0, 1.0, TextQuote(exact = quote)),
            quote,
        )
    }

    private suspend fun persistAnnotation(bookId: String, editionId: String, locator: ContentLocator, quote: String) {
        annotations.upsert(
            AnnotationEntity(
                id = UUID.randomUUID().toString(),
                bookId = bookId,
                editionId = editionId,
                locatorJson = LocatorCodec.encode(locator),
                quote = quote,
                note = "",
                layer = "USER",
                createdAt = System.currentTimeMillis(),
            ),
        )
    }

    suspend fun highlights(bookId: String) = annotations.forBook(bookId)

    suspend fun savePosition(editionId: String, locator: ContentLocator) {
        positions.upsert(
            ReadingPositionEntity(
                editionId = editionId,
                locatorJson = LocatorCodec.encode(locator),
                updatedAt = System.currentTimeMillis(),
            ),
        )
    }

    suspend fun position(editionId: String) = positions.get(editionId)

    suspend fun updatePageOcr(page: PageEntity) = pages.update(page)

    suspend fun addImagePage(editionId: String, uri: Uri, name: String) {
        val dest = context.contentResolver.openInputStream(uri)?.use {
            store.copyIncoming(editionId, name.ifBlank { "page-${System.currentTimeMillis()}.jpg" }, it)
        } ?: return
        val existing = pages.forEdition(editionId)
        pages.upsertAll(
            listOf(
                PageEntity(
                    id = UUID.randomUUID().toString(),
                    editionId = editionId,
                    index = existing.size,
                    imageRelPath = store.relative(dest),
                    ocrText = null,
                    recognitionDraft = null,
                ),
            ),
        )
    }

    private fun persistReadPermission(uri: Uri) {
        runCatching {
            context.contentResolver.takePersistableUriPermission(
                uri,
                Intent.FLAG_GRANT_READ_URI_PERMISSION,
            )
        }
    }

    private fun openAsset(assetPath: String, editionId: String, name: String): java.io.File? {
        return runCatching {
            context.assets.open(assetPath).use { input -> store.copyIncoming(editionId, name, input) }
        }.getOrNull()
    }

    private fun prettyTitle(name: String, suffix: String): String {
        val trimmed = name.substringAfterLast('/').removeSuffix(suffix).ifBlank { name }
        return when (trimmed) {
            "onepaper-sample" -> "一纸书煲 · 随包样页"
            "onepaper-guide" -> "一纸书煲使用说明书"
            else -> trimmed
        }
    }

    private suspend fun persistJob(state: JobState, bookId: String?, kind: String) {
        jobs.upsert(
            JobEntity(
                clientJobId = state.clientJobId,
                bookId = bookId,
                kind = kind,
                status = state.status.name,
                stage = state.stage,
                unitDone = state.unitDone,
                unitTotal = state.unitTotal,
                message = state.message,
                durableFilesPresent = state.durableFilesPresent,
                attempt = state.attempt,
                updatedAt = System.currentTimeMillis(),
            ),
        )
    }
}

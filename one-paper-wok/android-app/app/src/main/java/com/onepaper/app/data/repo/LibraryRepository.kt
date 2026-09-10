package com.onepaper.app.data.repo

import android.content.Context
import android.content.Intent
import android.net.Uri
import com.onepaper.app.data.files.PrivateStore
import com.onepaper.app.data.image.CoverFactory
import com.onepaper.app.data.importing.EpubMeta
import com.onepaper.app.data.importing.EpubTextExtractor
import com.onepaper.app.data.importing.ImportType
import com.onepaper.app.data.importing.PdfGuard
import com.onepaper.app.data.importing.PdfPages
import com.onepaper.domain.pdf.PdfBudget
import com.onepaper.domain.pdf.PdfTextLayer
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
    val detail: String? = null,
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
    private val covers: CoverFactory,
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
    suspend fun activeBooks() = books.active()
    suspend fun editionsOf(bookId: String) = editions.forBook(bookId)
    suspend fun edition(id: String) = editions.get(id)
    suspend fun chaptersOf(editionId: String) = chapters.forEdition(editionId)
    suspend fun pagesOf(editionId: String) = pages.forEdition(editionId)
    fun observeChapters(editionId: String) = chapters.observeForEdition(editionId)

    suspend fun ensureSeeded(): ImportOutcome? {
        if (books.activeCount() > 0) return null
        val text = context.assets.open("samples/excerpt.txt").bufferedReader().use { it.readText() }
        return importPlainText(
            title = "说明书",
            author = "",
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
        } ?: return ImportOutcome("", editionId, "无法读取这份文件。")

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
            coverRelPath = covers.fromTitle(editionId, title, author),
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
            coverRelPath = covers.fromTitle(editionId, prettyTitle(name, ""), ""),
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
            return ImportOutcome("", editionId, "加密的书加不进来。")
        }
        val extracted = EpubTextExtractor.extract(file)
        if (extracted.isEmpty()) {
            return ImportOutcome("", editionId, "这份文件里没有文字。")
        }
        val bookId = UUID.randomUUID().toString()
        val meta = EpubMeta.read(file)
        val title = if (name.contains("onepaper-guide")) {
            "说明书"
        } else {
            meta.title?.takeIf { it.isNotBlank() }
                ?: extracted.first().title.ifBlank { prettyTitle(name, ".epub") }
        }
        val author = meta.author.orEmpty()
        val cover = meta.coverBytes?.let { covers.writeBytes(editionId, it) }
            ?: covers.fromTitle(editionId, title, author)
        persistImported(
            bookId = bookId,
            editionId = editionId,
            title = title,
            author = author,
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
            coverRelPath = cover,
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
            return ImportOutcome("", editionId, "加密的书加不进来。")
        }
        val pageCount = PdfPages.count(file)
        val bookId = UUID.randomUUID().toString()
        val title = prettyTitle(name, ".pdf")
        val tooLarge = !PdfBudget.canExtractInMemory(file.length())
        val layers = if (tooLarge) {
            emptyList()
        } else {
            runCatching { PdfTextLayer.extractPages(file.readBytes(), pageCount) }.getOrDefault(emptyList())
        }
        persistImported(
            bookId = bookId,
            editionId = editionId,
            title = title,
            author = "",
            coverage = if (markExcerpt) Coverage.EXCERPT else coverage,
            kind = SourceKind.PDF,
            originalName = name,
            fileRel = store.relative(file),
            checksum = store.sha256(file),
            chapterList = emptyList(),
            pageCount = pageCount,
            coverRelPath = covers.fromPdf(editionId, file) ?: covers.fromTitle(editionId, title, ""),
        )
        if (pageCount > 0) {
            pages.upsertAll(
                (0 until pageCount).map { idx ->
                    val layer = layers.getOrNull(idx)
                    PageEntity(
                        id = UUID.randomUUID().toString(),
                        editionId = editionId,
                        index = idx,
                        imageRelPath = store.relative(file),
                        ocrText = null,
                        recognitionDraft = null,
                        embeddedText = layer?.text.orEmpty(),
                        hasTextLayer = layer?.hasTextOperators == true,
                    )
                },
            )
        }
        return ImportOutcome(
            bookId,
            editionId,
            detail = if (tooLarge) PdfBudget.tooLargeMessage() else null,
        )
    }

    suspend fun importBundledEpub(): ImportOutcome {
        val editionId = UUID.randomUUID().toString()
        val dest = openAsset("samples/onepaper-guide.epub", editionId, "onepaper-guide.epub")
            ?: return ImportOutcome("", editionId, "说明书找不到。")
        return ingestEpub(dest, "onepaper-guide.epub", Coverage.WHOLE_BOOK, markExcerpt = false, editionId)
    }

    suspend fun importBundledPdf(): ImportOutcome {
        val editionId = UUID.randomUUID().toString()
        val dest = openAsset("samples/onepaper-sample.pdf", editionId, "onepaper-sample.pdf")
            ?: return ImportOutcome("", editionId, "样页找不到。")
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
            title = "扫描 · ${dests.size} 页",
            author = "",
            coverage = Coverage.EXCERPT,
            kind = SourceKind.IMAGES,
            originalName = dests.first().name,
            fileRel = store.relative(dests.first()),
            checksum = store.sha256(dests.first()),
            chapterList = emptyList(),
            pageCount = dests.size,
            coverRelPath = covers.writeBytes(editionId, dests.first().readBytes())
                ?: covers.fromTitle(editionId, "扫描 · ${dests.size} 页", ""),
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
            coverRelPath = covers.writeBytes(editionId, file.readBytes())
                ?: covers.fromTitle(editionId, name, ""),
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
        coverRelPath: String? = null,
    ) {
        books.upsert(
            BookEntity(
                id = bookId,
                title = title,
                author = author,
                coverage = coverage.name,
                createdAt = System.currentTimeMillis(),
                coverRelPath = coverRelPath,
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

    suspend fun updateAuthor(bookId: String, author: String) {
        val current = books.get(bookId) ?: return
        books.upsert(current.copy(author = author.trim()))
    }

    suspend fun ensureCover(book: BookEntity): BookEntity {
        if (!book.coverRelPath.isNullOrBlank()) return book
        val edition = editions.forBook(book.id).firstOrNull() ?: return book
        val file = store.file(edition.relativePath)
        val cover = when (edition.sourceKind) {
            "PDF" -> if (file.exists()) covers.fromPdf(edition.id, file) else null
            "EPUB" -> if (file.exists()) {
                EpubMeta.read(file).coverBytes?.let { covers.writeBytes(edition.id, it) }
            } else {
                null
            }
            "IMAGES" -> if (file.exists()) covers.writeBytes(edition.id, file.readBytes()) else null
            else -> null
        } ?: covers.fromTitle(edition.id, book.title, book.author)
        val next = book.copy(coverRelPath = cover)
        books.upsert(next)
        return next
    }

    fun observeAnnotations() = annotations.observeAll()

    suspend fun ensurePdfTextLayers(editionId: String) {
        val edition = editions.get(editionId) ?: return
        if (edition.sourceKind != "PDF") return
        val existing = pages.forEdition(editionId)
        if (existing.isEmpty() || existing.none { it.embeddedText == null }) return
        val file = store.file(edition.relativePath)
        if (!file.exists()) return
        val skipExtract = !PdfBudget.canExtractInMemory(file.length())
        val layers = if (skipExtract) {
            emptyList()
        } else {
            runCatching { PdfTextLayer.extractPages(file.readBytes(), existing.size) }.getOrDefault(emptyList())
        }
        existing.forEach { page ->
            if (page.embeddedText != null) return@forEach
            val layer = layers.getOrNull(page.index)
            pages.update(
                page.copy(
                    embeddedText = if (skipExtract) "" else layer?.text.orEmpty(),
                    hasTextLayer = !skipExtract && layer?.hasTextOperators == true,
                ),
            )
        }
    }

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
            "onepaper-sample" -> "样页"
            "onepaper-guide" -> "说明书"
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

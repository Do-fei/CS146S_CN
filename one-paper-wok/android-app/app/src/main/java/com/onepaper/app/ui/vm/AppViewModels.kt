package com.onepaper.app.ui.vm

import android.app.Application
import android.net.Uri
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.onepaper.app.data.files.PrivateStore
import com.onepaper.app.data.importing.PdfPages
import com.onepaper.app.data.local.BookEntity
import com.onepaper.app.data.local.ChapterEntity
import com.onepaper.app.data.local.JobEntity
import com.onepaper.app.data.local.MessageEntity
import com.onepaper.app.data.local.NoteEntity
import com.onepaper.app.data.local.PageEntity
import com.onepaper.app.data.local.ProjectEntity
import com.onepaper.app.data.local.ProjectSectionEntity
import com.onepaper.app.data.local.ProposalItemEntity
import com.onepaper.app.data.prefs.UserPrefs
import com.onepaper.app.data.secure.SecretStore
import com.onepaper.app.data.repo.BackupRepository
import com.onepaper.app.data.repo.CompanionRepository
import com.onepaper.app.data.repo.ImportOutcome
import com.onepaper.app.data.repo.LibraryRepository
import com.onepaper.app.data.repo.NoteRepository
import com.onepaper.app.data.repo.ProjectRepository
import com.onepaper.domain.citation.ContentLocator
import com.onepaper.domain.citation.LocatorCodec
import com.onepaper.domain.citation.LocatorResolver
import com.onepaper.domain.citation.EpubChapter
import com.onepaper.domain.citation.EpubDocument
import com.onepaper.domain.citation.TextQuote
import com.onepaper.domain.model.Coverage
import com.onepaper.domain.ocr.OcrEngine
import com.onepaper.domain.ocr.OcrKind
import com.onepaper.domain.recook.ItemDecision
import com.onepaper.domain.recook.ProposalDecision
import dagger.hilt.android.lifecycle.HiltViewModel
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.SharingStarted
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.combine
import kotlinx.coroutines.flow.stateIn
import kotlinx.coroutines.launch
import javax.inject.Inject

@HiltViewModel
class ShelfViewModel @Inject constructor(
    private val library: LibraryRepository,
    private val projects: ProjectRepository,
    prefs: UserPrefs,
) : ViewModel() {
    val books: StateFlow<List<BookEntity>> = library.observeBooks()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
    val jobs: StateFlow<List<JobEntity>> = library.observeJobs()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
    val query = MutableStateFlow("")
    val hits = MutableStateFlow<List<ChapterEntity>>(emptyList())
    val onboardingDone = prefs.onboardingDone
        .stateIn(viewModelScope, SharingStarted.Eagerly, null as Boolean?)

    init {
        viewModelScope.launch {
            val seeded = library.ensureSeeded()
            if (seeded != null) {
                val chapter = library.chaptersOf(seeded.editionId).firstOrNull()?.plainText.orEmpty()
                projects.ensureForBook(seeded.bookId, "一纸书煲 · 授权摘录样本", chapter)
            }
        }
    }

    fun search(q: String) {
        query.value = q
        viewModelScope.launch { hits.value = library.searchChapters(q) }
    }
}

@HiltViewModel
class BookViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val library: LibraryRepository,
    private val projects: ProjectRepository,
) : ViewModel() {
    val bookId: String = checkNotNull(savedStateHandle["bookId"])
    val book = MutableStateFlow<BookEntity?>(null)
    val editionId = MutableStateFlow<String?>(null)
    val projectId = MutableStateFlow<String?>(null)
    val deleteNotice = MutableStateFlow("删除会软删书架条目，原文件仍在私有目录，可用备份恢复前请先导出。")

    init {
        viewModelScope.launch {
            book.value = library.book(bookId)
            editionId.value = library.editionsOf(bookId).firstOrNull()?.id
            val seed = editionId.value?.let { library.chaptersOf(it).firstOrNull()?.plainText }.orEmpty()
            projectId.value = projects.ensureForBook(bookId, book.value?.title ?: "一纸", seed).id
        }
    }

    fun delete() {
        viewModelScope.launch { library.softDeleteBook(bookId) }
    }
}

@HiltViewModel
class ReaderViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val library: LibraryRepository,
    private val store: PrivateStore,
    private val ocr: OcrEngine,
) : ViewModel() {
    val editionId: String = checkNotNull(savedStateHandle["editionId"])
    val chapters = MutableStateFlow<List<ChapterEntity>>(emptyList())
    val pages = MutableStateFlow<List<PageEntity>>(emptyList())
    val fontSp = MutableStateFlow(18f)
    val selected = MutableStateFlow("")
    val jumpQuote = MutableStateFlow<String?>(null)
    val stale = MutableStateFlow(false)
    val kind = MutableStateFlow("TEXT")
    val pdfPath = MutableStateFlow<String?>(null)
    val bookId = MutableStateFlow<String?>(null)
    val pageIndex = MutableStateFlow(0)
    val chapterIndex = MutableStateFlow(0)
    val notice = MutableStateFlow<String?>(null)

    init {
        viewModelScope.launch {
            val edition = library.edition(editionId)
            bookId.value = edition?.bookId
            kind.value = edition?.sourceKind ?: "PLAIN_TEXT"
            pdfPath.value = edition?.relativePath
            chapters.value = library.chaptersOf(editionId)
            pages.value = library.pagesOf(editionId)
            restorePosition()
        }
    }

    fun setFont(sp: Float) {
        fontSp.value = sp
    }

    fun select(quote: String) {
        selected.value = quote
    }

    fun next() {
        if (kind.value == "PDF" || kind.value == "IMAGES") {
            pageIndex.value = (pageIndex.value + 1).coerceAtMost((pages.value.size - 1).coerceAtLeast(0))
        } else {
            chapterIndex.value = (chapterIndex.value + 1).coerceAtMost((chapters.value.size - 1).coerceAtLeast(0))
        }
        persistPosition()
    }

    fun prev() {
        if (kind.value == "PDF" || kind.value == "IMAGES") {
            pageIndex.value = (pageIndex.value - 1).coerceAtLeast(0)
        } else {
            chapterIndex.value = (chapterIndex.value - 1).coerceAtLeast(0)
        }
        persistPosition()
    }

    fun highlight() {
        val quote = selected.value.trim()
        val book = bookId.value
        if (quote.isBlank() || book == null) {
            notice.value = "先粘贴或输入一段原文，再记笔记。"
            return
        }
        viewModelScope.launch {
            if (kind.value == "PDF" || kind.value == "IMAGES") {
                library.addHighlightPdf(book, editionId, pageIndex.value, quote)
                notice.value = "已按第 ${pageIndex.value + 1} 页记下选区。"
                persistPosition()
                return@launch
            }
            val chapter = chapters.value.firstOrNull { it.plainText.contains(quote) }
            if (chapter == null) {
                notice.value = "选区不在当前抽出文本中，没有记上。"
                return@launch
            }
            val progression = chapter.plainText.indexOf(quote).toDouble() / chapter.plainText.length.coerceAtLeast(1)
            library.addHighlight(book, editionId, chapter.href, quote, progression)
            val doc = EpubDocument(
                chapter.contentVersion,
                chapters.value.map { EpubChapter(it.href, it.contentVersion, it.plainText) },
            )
            val found = LocatorResolver().resolveEpub(
                doc,
                ContentLocator.Epub(chapter.href, progression, TextQuote(quote)),
            )
            stale.value = found !is com.onepaper.domain.citation.ResolveResult.Found || found.stale
            jumpQuote.value = quote
            notice.value = "已记下选区。"
            persistPosition()
        }
    }

    fun ocrCurrentPage() {
        viewModelScope.launch {
            val page = pages.value.getOrNull(pageIndex.value)
            if (page == null) {
                notice.value = "这一页还没有可识别的图像。"
                return@launch
            }
            val bytes = pageBytes(page) ?: run {
                notice.value = "无法渲染此页。"
                return@launch
            }
            val result = ocr.recognize(bytes, OcrKind.PRINT)
            library.updatePageOcr(page.copy(ocrText = result.fullText, recognitionDraft = result.fullText))
            pages.value = library.pagesOf(editionId)
            if (selected.value.isBlank() && result.fullText.isNotBlank()) {
                selected.value = result.fullText.take(80)
            }
            notice.value = if (result.fullText.isBlank()) "没有识别到文字。" else "识别稿已写入本页，请校对。"
        }
    }

    private fun pageBytes(page: PageEntity): ByteArray? {
        val rel = page.imageRelPath ?: pdfPath.value ?: return null
        val file = store.file(rel)
        return if (kind.value == "PDF" || file.name.endsWith(".pdf", true)) {
            PdfPages.pngBytes(file, page.index)
        } else {
            runCatching { file.readBytes() }.getOrNull()
        }
    }

    private fun persistPosition() {
        viewModelScope.launch {
            val locator = if (kind.value == "PDF" || kind.value == "IMAGES") {
                ContentLocator.PdfPageRect(pageIndex.value, 0.0, 0.0, 1.0, 1.0, TextQuote(selected.value))
            } else {
                val chapter = chapters.value.getOrNull(chapterIndex.value) ?: return@launch
                ContentLocator.Epub(chapter.href, 0.0, TextQuote(selected.value))
            }
            library.savePosition(editionId, locator)
        }
    }

    private suspend fun restorePosition() {
        val raw = library.position(editionId)?.locatorJson ?: return
        runCatching {
            when (val locator = LocatorCodec.decode(raw)) {
                is ContentLocator.PdfPageRect -> pageIndex.value = locator.pageIndex.coerceAtLeast(0)
                is ContentLocator.Epub -> {
                    val idx = chapters.value.indexOfFirst { it.href == locator.href }
                    if (idx >= 0) chapterIndex.value = idx
                }
                else -> Unit
            }
        }
    }
}

@HiltViewModel
class PapersViewModel @Inject constructor(
    private val projects: ProjectRepository,
    notes: NoteRepository,
) : ViewModel() {
    val projectsFlow = projects.observeProjects()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
    val notesFlow = notes.observeAll()
        .stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), emptyList())
}

@HiltViewModel
class ProjectViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val projects: ProjectRepository,
) : ViewModel() {
    val projectId: String = checkNotNull(savedStateHandle["projectId"])
    val project = MutableStateFlow<ProjectEntity?>(null)
    val sections = MutableStateFlow<List<ProjectSectionEntity>>(emptyList())
    val proposalId = MutableStateFlow<String?>(null)

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch {
            project.value = projects.project(projectId)
            sections.value = projects.sectionsOf(projectId)
            proposalId.value = projects.proposalsOf(projectId).firstOrNull()?.id
        }
    }

    fun saveSection(sectionId: String, body: String) {
        viewModelScope.launch {
            projects.updateSection(projectId, sectionId, body)
            refresh()
        }
    }

    fun regenerate(sectionId: String) {
        viewModelScope.launch {
            projects.regenerateSection(projectId, sectionId)
            refresh()
        }
    }

    fun recook(notes: List<String>) {
        viewModelScope.launch {
            proposalId.value = projects.createProposalFromNotes(projectId, notes)
        }
    }
}

@HiltViewModel
class RecookViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val projects: ProjectRepository,
) : ViewModel() {
    val proposalId: String = checkNotNull(savedStateHandle["proposalId"])
    val items = MutableStateFlow<List<ProposalItemEntity>>(emptyList())
    val currentBodies = MutableStateFlow<Map<String, String>>(emptyMap())
    val banner = MutableStateFlow<String?>(null)

    init {
        viewModelScope.launch {
            val proposal = projects.proposal(proposalId)
            items.value = projects.proposalItems(proposalId)
            if (proposal != null) {
                currentBodies.value = projects.sectionsOf(proposal.projectId).associate { it.sectionId to it.body }
            }
        }
    }

    fun decideAll(decision: ProposalDecision, edits: Map<String, String> = emptyMap()) {
        viewModelScope.launch {
            val map = items.value.associate { item ->
                item.id to ItemDecision(decision, editedBody = edits[item.id])
            }
            projects.decide(proposalId, map)
            val proposal = projects.proposal(proposalId)
            banner.value = if (proposal?.status == "conflicts") "计算期间文稿已变，冲突项未覆盖你的最新编辑。" else "已按逐条决定合并。"
            items.value = projects.proposalItems(proposalId)
        }
    }
}

@HiltViewModel
class CompanionVm @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val companion: CompanionRepository,
    secrets: SecretStore,
) : ViewModel() {
    val bookId: String = checkNotNull(savedStateHandle["bookId"])
    val seedQuote: String = savedStateHandle.get<String>("quote").orEmpty()
    val conversationId = MutableStateFlow<String?>(null)
    val messages = MutableStateFlow<List<MessageEntity>>(emptyList())
    val usingDeepSeek = MutableStateFlow(secrets.hasDeepSeekKey())
    val offline = MutableStateFlow(true)

    init {
        viewModelScope.launch {
            val id = companion.conversationId(bookId)
            conversationId.value = id
            companion.messages(id).collect { messages.value = it }
        }
    }

    fun ask(question: String, quote: String?) {
        viewModelScope.launch { companion.ask(bookId, question, quote) }
    }
}

@HiltViewModel
class NoteViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val notes: NoteRepository,
) : ViewModel() {
    val noteId: String? = savedStateHandle.get<String>("noteId")?.takeIf { it != "new" }
    val note = MutableStateFlow<NoteEntity?>(null)
    private val persistedId = MutableStateFlow(noteId)

    init {
        viewModelScope.launch {
            if (noteId != null) note.value = notes.get(noteId)
        }
    }

    fun save(title: String, userDraft: String, recognition: String?) {
        viewModelScope.launch {
            val id = notes.save(
                persistedId.value,
                note.value?.bookId,
                title,
                userDraft,
                recognition,
                note.value?.imageRelPath,
                false,
                note.value?.locatorJson,
            )
            persistedId.value = id
        }
    }
}

@HiltViewModel
class SettingsViewModel @Inject constructor(
    private val prefs: UserPrefs,
    private val store: PrivateStore,
    private val secrets: SecretStore,
    application: Application,
) : ViewModel() {
    val uploadPages = prefs.uploadPagesAllowed.stateIn(viewModelScope, SharingStarted.Eagerly, false)
    val uploadNotes = prefs.uploadNotesAllowed.stateIn(viewModelScope, SharingStarted.Eagerly, false)
    val dark = prefs.darkTheme.stateIn(viewModelScope, SharingStarted.Eagerly, false)
    val usage = MutableStateFlow(0L)
    val maskedKey = MutableStateFlow(secrets.maskedDeepSeekKey())
    val savedMessage = MutableStateFlow<String?>(null)

    init {
        usage.value = store.usageBytes()
        application.packageName
    }

    fun setUploadPages(v: Boolean) = viewModelScope.launch { prefs.setUploadPages(v) }
    fun setUploadNotes(v: Boolean) = viewModelScope.launch { prefs.setUploadNotes(v) }
    fun setDark(v: Boolean) = viewModelScope.launch { prefs.setDarkTheme(v) }

    fun saveDeepSeekKey(raw: String) {
        secrets.setDeepSeekKey(raw)
        maskedKey.value = secrets.maskedDeepSeekKey()
        savedMessage.value = if (secrets.hasDeepSeekKey()) "已保存在本机密钥库，不进备份。" else "已清除。"
    }

    fun clearDeepSeekKey() {
        secrets.setDeepSeekKey(null)
        maskedKey.value = null
        savedMessage.value = "已清除。"
    }
}

@HiltViewModel
class ImportViewModel @Inject constructor(
    private val library: LibraryRepository,
    private val projects: ProjectRepository,
    private val prefs: UserPrefs,
) : ViewModel() {
    val last = MutableStateFlow<ImportOutcome?>(null)
    val excerpt = MutableStateFlow(false)

    fun import(uri: Uri, name: String) {
        viewModelScope.launch {
            last.value = attachProject(
                library.importFromUri(
                    uri = uri,
                    displayName = name,
                    coverage = if (excerpt.value) Coverage.EXCERPT else Coverage.WHOLE_BOOK,
                    markExcerpt = excerpt.value,
                ),
            )
        }
    }

    fun importBundledEpub() {
        viewModelScope.launch { last.value = attachProject(library.importBundledEpub()) }
    }

    fun importBundledPdf() {
        viewModelScope.launch { last.value = attachProject(library.importBundledPdf()) }
    }

    fun finishOnboarding() = viewModelScope.launch { prefs.setOnboardingDone() }

    private suspend fun attachProject(outcome: ImportOutcome): ImportOutcome {
        if (outcome.rejectedReason != null || outcome.bookId.isBlank()) return outcome
        val book = library.book(outcome.bookId)
        val seed = library.chaptersOf(outcome.editionId).firstOrNull()?.plainText.orEmpty()
        projects.ensureForBook(outcome.bookId, book?.title ?: "一纸", seed)
        return outcome
    }
}

@HiltViewModel
class CaptureViewModel @Inject constructor(
    private val library: LibraryRepository,
    private val projects: ProjectRepository,
) : ViewModel() {
    val last = MutableStateFlow<ImportOutcome?>(null)

    fun importImages(uris: List<Uri>) {
        viewModelScope.launch {
            val outcome = library.importImages(uris)
            if (outcome.rejectedReason == null && outcome.bookId.isNotBlank()) {
                val book = library.book(outcome.bookId)
                projects.ensureForBook(outcome.bookId, book?.title ?: "自炊页", "")
            }
            last.value = outcome
        }
    }
}

@HiltViewModel
class BackupViewModel @Inject constructor(
    private val backup: BackupRepository,
) : ViewModel() {
    val message = MutableStateFlow<String?>(null)
    val filePath = MutableStateFlow<String?>(null)

    fun exportLibrary() {
        viewModelScope.launch {
            val file = backup.exportJson()
            filePath.value = file.absolutePath
            message.value = "已写出备份（不含 token）：${file.name}"
        }
    }

    fun exportMarkdown(projectId: String) {
        viewModelScope.launch {
            val file = backup.exportProjectMarkdown(projectId)
            filePath.value = file.absolutePath
            message.value = "已导出 Markdown：${file.name}"
        }
    }

    fun restore(raw: String) {
        viewModelScope.launch {
            runCatching {
                val manifest = backup.preview(raw)
                backup.restore(raw)
                message.value = "已恢复 ${manifest.bookCount} 本书、${manifest.noteCount} 则笔记。"
            }.onFailure { message.value = it.message }
        }
    }
}

@HiltViewModel
class PagesViewModel @Inject constructor(
    savedStateHandle: SavedStateHandle,
    private val library: LibraryRepository,
    private val ocr: OcrEngine,
    private val store: PrivateStore,
) : ViewModel() {
    val editionId: String = checkNotNull(savedStateHandle["editionId"])
    val pages = MutableStateFlow<List<PageEntity>>(emptyList())

    init {
        refresh()
    }

    fun refresh() {
        viewModelScope.launch { pages.value = library.pagesOf(editionId) }
    }

    fun addPage(uri: Uri, name: String) {
        viewModelScope.launch {
            library.addImagePage(editionId, uri, name)
            refresh()
        }
    }

    fun ocrPage(page: PageEntity) {
        viewModelScope.launch {
            val rel = page.imageRelPath ?: return@launch
            val file = store.file(rel)
            val bytes = if (file.name.endsWith(".pdf", ignoreCase = true)) {
                PdfPages.pngBytes(file, page.index)
            } else {
                runCatching { file.readBytes() }.getOrNull()
            } ?: return@launch
            val result = ocr.recognize(bytes, OcrKind.PRINT)
            library.updatePageOcr(page.copy(ocrText = result.fullText, recognitionDraft = result.fullText))
            refresh()
        }
    }

    fun proofread(page: PageEntity, userText: String) {
        viewModelScope.launch {
            library.updatePageOcr(page.copy(ocrText = userText))
            refresh()
        }
    }
}

@HiltViewModel
class OnboardingViewModel @Inject constructor(
    private val prefs: UserPrefs,
) : ViewModel() {
    fun done() = viewModelScope.launch { prefs.setOnboardingDone() }
}

@HiltViewModel
class MeViewModel @Inject constructor(
    notes: NoteRepository,
    library: LibraryRepository,
) : ViewModel() {
    val summary = combine(notes.observeAll(), library.observeBooks(), library.observeJobs()) { n, b, j ->
        Triple(b.size, n.size, j.size)
    }.stateIn(viewModelScope, SharingStarted.WhileSubscribed(5_000), Triple(0, 0, 0))
}

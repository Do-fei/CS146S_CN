package com.onepaper.app.ui.vm

import android.app.Application
import android.net.Uri
import androidx.lifecycle.SavedStateHandle
import androidx.lifecycle.ViewModel
import androidx.lifecycle.viewModelScope
import com.onepaper.app.data.files.PrivateStore
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
import com.onepaper.app.data.repo.BackupRepository
import com.onepaper.app.data.repo.CompanionRepository
import com.onepaper.app.data.repo.ImportOutcome
import com.onepaper.app.data.repo.LibraryRepository
import com.onepaper.app.data.repo.NoteRepository
import com.onepaper.app.data.repo.ProjectRepository
import com.onepaper.domain.citation.ContentLocator
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
        viewModelScope.launch { library.ensureSeeded() }
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
    val deleteNotice = MutableStateFlow("删除会软删书架条目，原文件仍在私有目录，可用备份恢复前请先导出。")

    init {
        viewModelScope.launch {
            book.value = library.book(bookId)
            editionId.value = library.editionsOf(bookId).firstOrNull()?.id
            val seed = editionId.value?.let { library.chaptersOf(it).firstOrNull()?.plainText }.orEmpty()
            projects.ensureForBook(bookId, book.value?.title ?: "一纸", seed)
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

    init {
        viewModelScope.launch {
            val edition = library.edition(editionId)
            bookId.value = edition?.bookId
            kind.value = edition?.sourceKind ?: "PLAIN_TEXT"
            pdfPath.value = edition?.relativePath
            chapters.value = library.chaptersOf(editionId)
            pages.value = library.pagesOf(editionId)
        }
    }

    fun setFont(sp: Float) {
        fontSp.value = sp
    }

    fun select(quote: String) {
        selected.value = quote
    }

    fun highlight() {
        val quote = selected.value
        val chapter = chapters.value.firstOrNull { it.plainText.contains(quote) } ?: return
        val book = bookId.value ?: return
        val progression = chapter.plainText.indexOf(quote).toDouble() / chapter.plainText.length.coerceAtLeast(1)
        viewModelScope.launch {
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
) : ViewModel() {
    val bookId: String = checkNotNull(savedStateHandle["bookId"])
    val conversationId = MutableStateFlow<String?>(null)
    val messages = MutableStateFlow<List<MessageEntity>>(emptyList())
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
    val noteId: String? = savedStateHandle["noteId"]?.takeIf { it != "new" }
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
    application: Application,
) : ViewModel() {
    val uploadPages = prefs.uploadPagesAllowed.stateIn(viewModelScope, SharingStarted.Eagerly, false)
    val uploadNotes = prefs.uploadNotesAllowed.stateIn(viewModelScope, SharingStarted.Eagerly, false)
    val dark = prefs.darkTheme.stateIn(viewModelScope, SharingStarted.Eagerly, false)
    val usage = MutableStateFlow(0L)

    init {
        usage.value = store.usageBytes()
        application.packageName
    }

    fun setUploadPages(v: Boolean) = viewModelScope.launch { prefs.setUploadPages(v) }
    fun setUploadNotes(v: Boolean) = viewModelScope.launch { prefs.setUploadNotes(v) }
    fun setDark(v: Boolean) = viewModelScope.launch { prefs.setDarkTheme(v) }
}

@HiltViewModel
class ImportViewModel @Inject constructor(
    private val library: LibraryRepository,
    private val prefs: UserPrefs,
) : ViewModel() {
    val last = MutableStateFlow<ImportOutcome?>(null)
    val excerpt = MutableStateFlow(false)

    fun import(uri: Uri, name: String) {
        viewModelScope.launch {
            last.value = library.importFromUri(
                uri = uri,
                displayName = name,
                coverage = if (excerpt.value) Coverage.EXCERPT else Coverage.WHOLE_BOOK,
                markExcerpt = excerpt.value,
            )
        }
    }

    fun finishOnboarding() = viewModelScope.launch { prefs.setOnboardingDone() }
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
            val bytes = store.file(rel).readBytes()
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

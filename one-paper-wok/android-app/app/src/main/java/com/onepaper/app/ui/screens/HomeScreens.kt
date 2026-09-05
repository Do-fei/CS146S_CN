package com.onepaper.app.ui.screens

import android.content.Intent
import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.Image
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Switch
import androidx.compose.material3.SwitchDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.onepaper.app.AppConstants
import com.onepaper.app.data.share.ExportShare
import com.onepaper.app.ui.components.Banner
import com.onepaper.app.ui.components.BookSpineCard
import com.onepaper.app.ui.components.EmptyState
import com.onepaper.app.ui.components.Kicker
import com.onepaper.app.ui.components.PaperCard
import com.onepaper.app.ui.components.PaperScaffold
import com.onepaper.app.ui.components.QuietButton
import com.onepaper.app.ui.components.QuietField
import com.onepaper.app.ui.components.QuietIconButton
import com.onepaper.app.ui.components.QuietNavBar
import com.onepaper.app.ui.components.QuietNavRail
import com.onepaper.app.ui.components.QuietProgress
import com.onepaper.app.ui.reader.SelectableReaderText
import com.onepaper.app.ui.components.QuietTone
import com.onepaper.app.ui.components.QuietTopBar
import com.onepaper.app.ui.components.SectionTitle
import com.onepaper.app.ui.components.StatCell
import com.onepaper.app.ui.graphics.ZenGlyph
import com.onepaper.app.ui.graphics.ZenMark
import com.onepaper.app.ui.vm.BackupViewModel
import com.onepaper.app.ui.vm.BookViewModel
import com.onepaper.app.ui.vm.CaptureViewModel
import com.onepaper.app.ui.vm.ImportViewModel
import com.onepaper.app.ui.vm.MeViewModel
import com.onepaper.app.ui.vm.OnboardingViewModel
import com.onepaper.app.ui.vm.PapersViewModel
import com.onepaper.app.ui.vm.ReaderViewModel
import com.onepaper.app.ui.vm.SettingsViewModel
import com.onepaper.app.ui.vm.ShelfViewModel
import com.onepaper.app.ui.layout.LocalWindowFit
import com.onepaper.domain.citation.LocatorJump
import com.onepaper.domain.search.LibraryHitKind
import com.onepaper.domain.search.LibrarySearch
import java.io.File

@Composable
fun OnboardingScreen(
    onImport: () -> Unit,
    onCapture: () -> Unit,
    onLater: () -> Unit,
    vm: OnboardingViewModel = hiltViewModel(),
) {
    PaperScaffold(title = "一纸书煲") { padding ->
        Column(
            Modifier
                .padding(padding)
                .padding(horizontal = 24.dp)
                .fillMaxSize()
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Spacer(Modifier.height(12.dp))
            Box(contentAlignment = Alignment.Center) {
                ZenMark(ZenGlyph.Enso, Modifier.height(168.dp).fillMaxWidth())
                ZenMark(ZenGlyph.Wok, Modifier.height(88.dp).fillMaxWidth(), tint = MaterialTheme.colorScheme.onSurface)
            }
            Text("导入一本书，开始读。", style = MaterialTheme.typography.bodyLarge)
            QuietButton("导入电子书", { vm.done(); onImport() }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Import, tone = QuietTone.Ink)
            QuietButton("拍摄", { vm.done(); onCapture() }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Camera)
            QuietButton("稍后", { vm.done(); onLater() }, Modifier.fillMaxWidth(), tone = QuietTone.Ghost)
            Spacer(Modifier.height(12.dp))
        }
    }
}

@Composable
fun HomePager(
    onOpenBook: (String) -> Unit,
    onContinueRead: (String) -> Unit,
    onImport: () -> Unit,
    onCapture: () -> Unit,
    onOpenProject: (String) -> Unit,
    onOpenNote: (String) -> Unit,
    onOpenLocator: (editionId: String, quote: String, href: String?, page: Int?) -> Unit,
    onSettings: () -> Unit,
    onBackup: () -> Unit,
    onTask: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    var tab by remember { mutableIntStateOf(0) }
    val wide = LocalWindowFit.current.wide
    val pane: @Composable () -> Unit = {
        when (tab) {
            0 -> ShelfPane(
                Modifier.fillMaxSize(),
                onOpenBook,
                onContinueRead,
                onImport,
                onCapture,
                onTask,
                onOpenProject,
                onOpenNote,
                onOpenLocator,
            )
            1 -> PapersPane(Modifier.fillMaxSize(), onOpenProject, onOpenNote, onOpenLocator)
            2 -> CanteenPane(Modifier.fillMaxSize(), onBackup)
            else -> MePane(Modifier.fillMaxSize(), onSettings, onBackup, onOpenNote)
        }
    }
    if (wide) {
        Row(modifier.fillMaxSize()) {
            QuietNavRail(selected = tab, onSelect = { tab = it })
            Box(Modifier.weight(1f).fillMaxSize()) { pane() }
        }
    } else {
        PaperScaffold(
            bottomBar = { QuietNavBar(selected = tab, onSelect = { tab = it }) },
            contentWindowInsets = WindowInsets(0, 0, 0, 0),
        ) { padding ->
            Box(modifier.padding(padding).fillMaxSize()) { pane() }
        }
    }
}

@Composable
private fun ShelfPane(
    modifier: Modifier,
    onOpenBook: (String) -> Unit,
    onContinueRead: (String) -> Unit,
    onImport: () -> Unit,
    onCapture: () -> Unit,
    onTask: (String) -> Unit,
    onOpenProject: (String) -> Unit,
    onOpenNote: (String) -> Unit,
    onOpenLocator: (editionId: String, quote: String, href: String?, page: Int?) -> Unit,
    vm: ShelfViewModel = hiltViewModel(),
) {
    val shelf by vm.shelf.collectAsStateWithLifecycle()
    val jobs by vm.jobs.collectAsStateWithLifecycle()
    val hits by vm.hits.collectAsStateWithLifecycle()
    val query by vm.query.collectAsStateWithLifecycle()
    Column(modifier.fillMaxSize()) {
        QuietTopBar(
            title = "书架",
            actions = {
                QuietIconButton(ZenGlyph.Camera, "拍摄", onCapture)
                QuietIconButton(ZenGlyph.Plus, "导入", onImport)
            },
        )
        QuietField(
            value = query,
            onValueChange = vm::search,
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            label = "搜索",
        )
        if (jobs.any { it.status != "COMPLETED" }) {
            jobs.take(2).forEach { job ->
                PaperCard(
                    Modifier
                        .padding(16.dp)
                        .fillMaxWidth(),
                    onClick = { onTask(job.clientJobId) },
                ) {
                    Row(verticalAlignment = Alignment.CenterVertically, horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                        ZenMark(ZenGlyph.Flame, Modifier.height(28.dp).padding(end = 4.dp), tint = MaterialTheme.colorScheme.tertiary)
                        Column(verticalArrangement = Arrangement.spacedBy(6.dp)) {
                            Kicker("处理中")
                            Text(job.stage.ifBlank { job.kind }, style = MaterialTheme.typography.titleMedium)
                            Text("第 ${job.unitDone}/${job.unitTotal} 页", style = MaterialTheme.typography.bodySmall)
                            if (job.unitTotal > 0) {
                                QuietProgress(job.unitDone.toFloat() / job.unitTotal)
                            }
                        }
                    }
                }
            }
        }
        if (hits.isNotEmpty()) {
            val pad = LocalWindowFit.current.pagePad
            hits.take(8).forEach { hit ->
                PaperCard(
                    Modifier
                        .padding(horizontal = pad, vertical = 4.dp)
                        .fillMaxWidth(),
                    onClick = {
                        when (hit.kind) {
                            LibraryHitKind.BOOK -> hit.bookId?.let(onOpenBook)
                            LibraryHitKind.PAPER -> hit.projectId?.let(onOpenProject)
                            LibraryHitKind.NOTE -> hit.noteId?.let(onOpenNote)
                            LibraryHitKind.HIGHLIGHT -> {
                                val jump = LocatorJump.fromJson(hit.locatorJson)
                                val editionId = hit.editionId
                                if (editionId != null) {
                                    onOpenLocator(editionId, jump?.quote ?: hit.snippet, jump?.href, jump?.pageIndex)
                                }
                            }
                            LibraryHitKind.CHAPTER -> {
                                val editionId = hit.editionId
                                if (editionId != null) {
                                    onOpenLocator(editionId, query.take(80), hit.href, hit.pageIndex)
                                } else {
                                    hit.bookId?.let(onOpenBook)
                                }
                            }
                        }
                    },
                ) {
                    Kicker(LibrarySearch.kindLabel(hit.kind))
                    Text(hit.title, style = MaterialTheme.typography.titleSmall)
                    Text(hit.snippet, style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                }
            }
        }
        if (shelf.isEmpty()) {
            EmptyState("还没有书", "导入或拍摄。", glyph = ZenGlyph.Books)
        } else {
            LazyColumn(
                contentPadding = androidx.compose.foundation.layout.PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                items(shelf, key = { it.book.id }) { item ->
                    val cover = rememberCover(item.book.coverRelPath)
                    BookSpineCard(
                        title = item.book.title,
                        subtitle = listOfNotNull(
                            item.book.author.takeIf { it.isNotBlank() } ?: "未知作者",
                            if (item.book.coverage == "EXCERPT") "摘录" else "全书",
                        ).joinToString(" · "),
                        progressLabel = item.progress.label,
                        progressPercent = item.progress.percent,
                        cover = cover,
                        onClick = { onOpenBook(item.book.id) },
                        onContinue = item.editionId?.let { id -> { onContinueRead(id) } },
                    )
                }
            }
        }
    }
}

@Composable
private fun PapersPane(
    modifier: Modifier,
    onOpenProject: (String) -> Unit,
    onOpenNote: (String) -> Unit,
    onOpenLocator: (editionId: String, quote: String, href: String?, page: Int?) -> Unit,
    vm: PapersViewModel = hiltViewModel(),
) {
    val projects by vm.projectsFlow.collectAsStateWithLifecycle()
    val notes by vm.notesFlow.collectAsStateWithLifecycle()
    val ember by vm.ember.collectAsStateWithLifecycle()
    Column(modifier.fillMaxSize()) {
        QuietTopBar(title = "一纸")
        LazyColumn(
            Modifier.padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
        item { SectionTitle("回看", glyph = ZenGlyph.Flame) }
        item {
            if (ember.isEmpty()) {
                Text(
                    "今天没有要回看的。",
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                    modifier = Modifier.padding(bottom = 8.dp),
                )
            }
        }
        items(ember, key = { it.id }) { row ->
            PaperCard(
                Modifier.fillMaxWidth(),
                onClick = {
                    val jump = com.onepaper.domain.citation.LocatorJump.fromJson(row.locatorJson)
                    val editionId = row.editionId
                    if (row.kind == com.onepaper.domain.review.EmberKind.HIGHLIGHT && editionId != null) {
                        onOpenLocator(editionId, jump?.quote ?: row.body, jump?.href, jump?.pageIndex)
                    } else if (row.kind == com.onepaper.domain.review.EmberKind.DRAFT) {
                        onOpenNote(row.id)
                    }
                },
            ) {
                Kicker(if (row.kind == com.onepaper.domain.review.EmberKind.HIGHLIGHT) "划线" else "我的稿")
                Text(row.title, style = MaterialTheme.typography.titleMedium)
                Text(row.body.take(120), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
        if (ember.isNotEmpty()) {
            item {
                QuietButton("今日已回看", vm::dismissEmberToday, Modifier.fillMaxWidth(), glyph = ZenGlyph.Enso)
            }
        }
        item { SectionTitle("一纸", glyph = ZenGlyph.Sheet) }
        if (projects.isEmpty()) {
            item { EmptyState("还没有一纸", "读过书之后会出现在这里。", glyph = ZenGlyph.Sheet) }
        }
        items(projects, key = { it.id }) { project ->
            PaperCard(Modifier.fillMaxWidth(), onClick = { onOpenProject(project.id) }) {
                Text(project.title, style = MaterialTheme.typography.titleMedium)
            }
        }
        item { SectionTitle("笔记", glyph = ZenGlyph.Note) }
        items(notes, key = { it.id }) { note ->
            PaperCard(Modifier.fillMaxWidth(), onClick = { onOpenNote(note.id) }) {
                Text(note.title.ifBlank { "未命名笔记" }, style = MaterialTheme.typography.titleMedium)
                Text(note.userDraft.take(80), style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
            }
        }
        item {
            QuietButton("新建笔记", { onOpenNote("new") }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Brush)
        }
        }
    }
}

@Composable
private fun MePane(
    modifier: Modifier,
    onSettings: () -> Unit,
    onBackup: () -> Unit,
    onOpenNote: (String) -> Unit,
    vm: MeViewModel = hiltViewModel(),
) {
    val summary by vm.summary.collectAsStateWithLifecycle()
    Column(modifier.fillMaxSize()) {
        QuietTopBar(title = "我的")
        Column(
            Modifier
                .verticalScroll(rememberScrollState())
                .padding(24.dp),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            StatCell("书", summary.first.toString())
            StatCell("笔记", summary.second.toString())
            StatCell("任务", summary.third.toString())
        }
        QuietButton("备份", onBackup, Modifier.fillMaxWidth(), glyph = ZenGlyph.Stack, tone = QuietTone.Ink)
        QuietButton("设置", onSettings, Modifier.fillMaxWidth(), glyph = ZenGlyph.Sliders)
        QuietButton("写笔记", { onOpenNote("new") }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Note)
        }
    }
}

@Composable
private fun CanteenPane(modifier: Modifier, onBackup: () -> Unit) {
    val context = LocalContext.current
    Column(modifier.fillMaxSize()) {
        QuietTopBar(title = "食堂")
        Column(
            Modifier
                .padding(24.dp)
                .verticalScroll(rememberScrollState()),
            horizontalAlignment = Alignment.CenterHorizontally,
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
        ZenMark(ZenGlyph.Bowl, Modifier.height(120.dp).fillMaxWidth())
        Text(
            "还没开放。",
            style = MaterialTheme.typography.bodyLarge,
        )
        QuietButton(
            "分享",
            {
                val send = Intent(Intent.ACTION_SEND).apply {
                    type = "text/plain"
                    putExtra(Intent.EXTRA_TEXT, AppConstants.SHARE_BLURB)
                }
                context.startActivity(Intent.createChooser(send, "分享一纸书煲"))
            },
            Modifier.fillMaxWidth(),
            glyph = ZenGlyph.Share,
            tone = QuietTone.Ink,
        )
        QuietButton("备份", onBackup, Modifier.fillMaxWidth(), glyph = ZenGlyph.Stack)
        }
    }
}

@Composable
fun BookScreen(
    onOpenReader: (String) -> Unit,
    onOpenCompanion: (String) -> Unit,
    onOpenProject: (String) -> Unit,
    onOpenPages: (String) -> Unit,
    onBack: () -> Unit,
    vm: BookViewModel = hiltViewModel(),
) {
    val book by vm.book.collectAsStateWithLifecycle()
    val editionId by vm.editionId.collectAsStateWithLifecycle()
    val project = vm.projectId.collectAsStateWithLifecycle().value
    PaperScaffold(title = book?.title ?: "书", onBack = onBack) { padding ->
        Column(
            Modifier
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            if (book?.coverage == "EXCERPT") {
                Kicker("摘录")
            }
            var authorDraft by remember(book?.id, book?.author) { mutableStateOf(book?.author.orEmpty()) }
            QuietField(
                value = authorDraft,
                onValueChange = { authorDraft = it },
                label = "作者",
                modifier = Modifier.fillMaxWidth(),
            )
            QuietButton("保存作者", { vm.saveAuthor(authorDraft) }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Brush)
            QuietButton("阅读", { editionId?.let(onOpenReader) }, Modifier.fillMaxWidth(), enabled = editionId != null, glyph = ZenGlyph.Book, tone = QuietTone.Ink)
            QuietButton("搭子", { onOpenCompanion(vm.bookId) }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Chat)
            QuietButton("一纸", { project?.let(onOpenProject) }, Modifier.fillMaxWidth(), enabled = project != null, glyph = ZenGlyph.Sheet)
            QuietButton("页面", { editionId?.let(onOpenPages) }, Modifier.fillMaxWidth(), enabled = editionId != null, glyph = ZenGlyph.Scan)
            QuietButton("删除", { vm.delete(); onBack() }, Modifier.fillMaxWidth(), tone = QuietTone.Danger)
        }
    }
}

@Composable
fun ReaderScreen(
    onCompanion: (bookId: String, quote: String, locator: String, editionId: String) -> Unit,
    onBack: () -> Unit,
    vm: ReaderViewModel = hiltViewModel(),
) {
    val chapters by vm.chapters.collectAsStateWithLifecycle()
    val font by vm.fontSp.collectAsStateWithLifecycle()
    val selected by vm.selected.collectAsStateWithLifecycle()
    val kind by vm.kind.collectAsStateWithLifecycle()
    val pdfPath by vm.pdfPath.collectAsStateWithLifecycle()
    val bookId by vm.bookId.collectAsStateWithLifecycle()
    val stale by vm.stale.collectAsStateWithLifecycle()
    val pages by vm.pages.collectAsStateWithLifecycle()
    val pageIndex by vm.pageIndex.collectAsStateWithLifecycle()
    val chapterIndex by vm.chapterIndex.collectAsStateWithLifecycle()
    val notice by vm.notice.collectAsStateWithLifecycle()
    val jumpQuote by vm.jumpQuote.collectAsStateWithLifecycle()
    val currentChapter = chapters.getOrNull(chapterIndex)
    val currentPage = pages.getOrNull(pageIndex)
    val scheme = MaterialTheme.colorScheme
    val ask: (String) -> Unit = { quote ->
        vm.select(quote)
        bookId?.let { onCompanion(it, quote, vm.currentLocatorJson(), vm.editionId) }
    }
    PaperScaffold(title = "阅读", onBack = onBack) { padding ->
        Column(
            Modifier
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text("字号", style = MaterialTheme.typography.bodySmall, color = scheme.onSurfaceVariant)
            Slider(
                value = font,
                onValueChange = vm::setFont,
                valueRange = 14f..28f,
                colors = SliderDefaults.colors(
                    thumbColor = scheme.onSurface,
                    activeTrackColor = scheme.onSurface,
                    inactiveTrackColor = scheme.outlineVariant,
                ),
            )
            if (stale) Banner("找不到上次读到的位置。")
            notice?.let { Banner(it) }
            if (kind == "PDF") {
                Text("第 ${pageIndex + 1} / ${pages.size.coerceAtLeast(1)} 页", style = MaterialTheme.typography.labelMedium)
                val context = LocalContext.current
                val pageBitmap = remember(pdfPath, pageIndex) {
                    pdfPath?.let { path ->
                        com.onepaper.app.data.importing.PdfPages.renderBitmap(File(context.filesDir, path), pageIndex)
                    }
                }
                val boxes = remember(currentPage?.ocrBoxesJson) {
                    com.onepaper.app.data.ocr.OcrBoxCodec.decode(currentPage?.ocrBoxesJson)
                }
                if (currentPage?.hasTextLayer == true && !currentPage.embeddedText.isNullOrBlank()) {
                    pageBitmap?.let { Image(it.asImageBitmap(), contentDescription = "PDF 页", modifier = Modifier.fillMaxWidth().height(280.dp)) }
                    SelectableReaderText(
                        text = currentPage.embeddedText.orEmpty(),
                        fontSp = font,
                        highlight = jumpQuote,
                        onNote = { vm.highlight(it) },
                        onAsk = ask,
                    )
                } else {
                    if (pageBitmap != null && boxes.isNotEmpty()) {
                        com.onepaper.app.ui.reader.OcrOverlayPage(
                            bitmap = pageBitmap,
                            boxes = boxes,
                            onPick = { vm.select(it) },
                        )
                    } else {
                        pdfPath?.let { PdfPreview(it, pageIndex) }
                    }
                    currentPage?.recognitionDraft?.takeIf { it.isNotBlank() }?.let { draft ->
                        Text("识别文字", style = MaterialTheme.typography.labelMedium)
                        SelectableReaderText(
                            text = draft,
                            fontSp = font,
                            highlight = jumpQuote,
                            onNote = { vm.highlight(it) },
                            onAsk = ask,
                        )
                    } ?: Text("先识别本页。", style = MaterialTheme.typography.bodySmall)
                }
            } else if (kind == "IMAGES") {
                Text("第 ${pageIndex + 1} / ${pages.size.coerceAtLeast(1)} 页", style = MaterialTheme.typography.labelMedium)
                currentPage?.imageRelPath?.let { ImagePreview(it) }
                currentPage?.recognitionDraft?.takeIf { it.isNotBlank() }?.let { draft ->
                    Text("识别文字", style = MaterialTheme.typography.labelMedium)
                    SelectableReaderText(
                        text = draft,
                        fontSp = font,
                        highlight = jumpQuote,
                        onNote = { vm.highlight(it) },
                        onAsk = ask,
                    )
                } ?: Text("先识别本页。", style = MaterialTheme.typography.bodySmall)
            } else {
                currentChapter?.let { chapter ->
                    Text("${chapter.title} · ${chapterIndex + 1}/${chapters.size.coerceAtLeast(1)}", style = MaterialTheme.typography.titleMedium)
                    SelectableReaderText(
                        text = chapter.plainText,
                        fontSp = font,
                        highlight = jumpQuote,
                        onNote = { vm.highlight(it) },
                        onAsk = ask,
                    )
                } ?: Text("没有可显示的文字。")
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                QuietButton("上一页", vm::prev, Modifier.weight(1f), glyph = ZenGlyph.ChevronLeft)
                QuietButton("下一页", vm::next, Modifier.weight(1f), glyph = ZenGlyph.ChevronRight)
            }
            val speaking by vm.speaking.collectAsStateWithLifecycle()
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                if (speaking) {
                    QuietButton("停止朗读", vm::stopListening, Modifier.weight(1f), glyph = ZenGlyph.Speak, tone = QuietTone.Danger)
                } else {
                    QuietButton("听本页", vm::listenCurrent, Modifier.weight(1f), glyph = ZenGlyph.Speak)
                }
            }
            if (kind == "PDF" || kind == "IMAGES") {
                QuietButton("识别本页", vm::ocrCurrentPage, Modifier.fillMaxWidth(), glyph = ZenGlyph.Scan)
            }
            QuietField(
                value = selected,
                onValueChange = vm::select,
                label = "选中的文字",
                modifier = Modifier.fillMaxWidth(),
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.horizontalScroll(rememberScrollState())) {
                QuietButton("笔记", { vm.highlight() }, glyph = ZenGlyph.Note)
                QuietButton("提问", { bookId?.let { ask(selected) } }, glyph = ZenGlyph.Chat)
            }
        }
    }
}

@Composable
private fun PdfPreview(relativePath: String, pageIndex: Int) {
    val context = LocalContext.current
    val bitmap = remember(relativePath, pageIndex) {
        com.onepaper.app.data.importing.PdfPages.renderBitmap(File(context.filesDir, relativePath), pageIndex)
    }
    if (bitmap != null) {
        Image(
            bitmap.asImageBitmap(),
            contentDescription = "PDF 第 ${pageIndex + 1} 页",
            modifier = Modifier.fillMaxWidth().height(420.dp),
        )
    } else {
        Text("未能渲染这一页。")
    }
}

@Composable
private fun rememberCover(relativePath: String?): androidx.compose.ui.graphics.ImageBitmap? {
    val context = LocalContext.current
    return remember(relativePath) {
        val rel = relativePath ?: return@remember null
        runCatching {
            val file = File(context.filesDir, rel)
            if (!file.exists()) return@runCatching null
            android.graphics.BitmapFactory.decodeFile(file.absolutePath)?.asImageBitmap()
        }.getOrNull()
    }
}

@Composable
private fun ImagePreview(relativePath: String) {
    val context = LocalContext.current
    val bitmap = remember(relativePath) {
        runCatching {
            val file = File(context.filesDir, relativePath)
            if (!file.exists()) return@runCatching null
            android.graphics.BitmapFactory.decodeFile(file.absolutePath)
        }.getOrNull()
    }
    if (bitmap != null) {
        Image(bitmap.asImageBitmap(), contentDescription = "扫描页", modifier = Modifier.fillMaxWidth().height(360.dp))
    } else {
        Text("未能打开图像页。")
    }
}

@Composable
fun ImportScreen(
    onDone: () -> Unit,
    onOpenBook: (String) -> Unit,
    vm: ImportViewModel = hiltViewModel(),
) {
    val last by vm.last.collectAsStateWithLifecycle()
    val excerpt by vm.excerpt.collectAsStateWithLifecycle()
    val context = LocalContext.current
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) vm.import(uri, uri.lastPathSegment ?: "file")
    }
    val scheme = MaterialTheme.colorScheme
    PaperScaffold(title = "导入", onBack = onDone) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("标记为摘录")
                Spacer(Modifier.weight(1f))
                Switch(
                    checked = excerpt,
                    onCheckedChange = { vm.excerpt.value = it },
                    colors = SwitchDefaults.colors(
                        checkedThumbColor = scheme.surface,
                        checkedTrackColor = scheme.onSurface,
                        uncheckedThumbColor = scheme.onSurfaceVariant,
                        uncheckedTrackColor = scheme.outlineVariant,
                    ),
                )
            }
            val clipPicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
                if (uri != null) vm.importClippings(context.contentResolver, uri)
            }
            QuietButton("选择文件", { picker.launch(arrayOf("*/*")) }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Sheet, tone = QuietTone.Ink)
            QuietButton(
                "导入书摘",
                { clipPicker.launch(arrayOf("text/plain", "text/*", "*/*")) },
                Modifier.fillMaxWidth(),
                glyph = ZenGlyph.Note,
            )
            QuietButton("导入说明书", vm::importBundledEpub, Modifier.fillMaxWidth(), glyph = ZenGlyph.Book)
            QuietButton("导入样页", vm::importBundledPdf, Modifier.fillMaxWidth(), glyph = ZenGlyph.Scan)
            last?.let { outcome ->
                if (outcome.rejectedReason != null) {
                    Banner(outcome.rejectedReason)
                } else {
                    Banner(outcome.detail ?: "已加入书架。")
                    QuietButton("打开", { onOpenBook(outcome.bookId) }, Modifier.fillMaxWidth(), enabled = outcome.bookId.isNotBlank(), glyph = ZenGlyph.Book, tone = QuietTone.Ink)
                    QuietButton("完成", onDone, Modifier.fillMaxWidth(), tone = QuietTone.Ghost)
                }
            }
        }
    }
}

@Composable
fun CaptureScreen(
    onDone: () -> Unit,
    onImport: () -> Unit,
    onOpenBook: (String) -> Unit,
    vm: CaptureViewModel = hiltViewModel(),
) {
    val last by vm.last.collectAsStateWithLifecycle()
    PaperScaffold(title = "拍摄", onBack = onDone) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            CaptureStudio(bitmaps = vm.bitmaps, onImported = vm::importImages)
            QuietButton("改为导入文件", onImport, Modifier.fillMaxWidth(), glyph = ZenGlyph.Import)
            last?.let { outcome ->
                if (outcome.rejectedReason != null) {
                    Banner(outcome.rejectedReason)
                } else {
                    Banner("已加入书架。")
                    QuietButton("打开", { onOpenBook(outcome.bookId) }, Modifier.fillMaxWidth(), enabled = outcome.bookId.isNotBlank(), glyph = ZenGlyph.Book, tone = QuietTone.Ink)
                }
            }
        }
    }
}

@Composable
fun SettingsScreen(onBack: () -> Unit, vm: SettingsViewModel = hiltViewModel()) {
    val pages by vm.uploadPages.collectAsStateWithLifecycle()
    val notes by vm.uploadNotes.collectAsStateWithLifecycle()
    val dark by vm.dark.collectAsStateWithLifecycle()
    val usage by vm.usage.collectAsStateWithLifecycle()
    val masked by vm.maskedKey.collectAsStateWithLifecycle()
    val saved by vm.savedMessage.collectAsStateWithLifecycle()
    var keyDraft by remember { mutableStateOf("") }
    val context = LocalContext.current
    val scheme = MaterialTheme.colorScheme
    PaperScaffold(title = "设置", onBack = onBack) { padding ->
        Column(
            Modifier
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text("DeepSeek", style = MaterialTheme.typography.titleMedium)
            Text("提问用，存在本机。", style = MaterialTheme.typography.bodySmall, color = scheme.onSurfaceVariant)
            if (masked != null) Text("已保存 $masked", style = MaterialTheme.typography.bodySmall)
            QuietField(
                value = keyDraft,
                onValueChange = { keyDraft = it },
                label = "API Key",
                visualTransformation = PasswordVisualTransformation(),
                modifier = Modifier.fillMaxWidth(),
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                QuietButton("保存", { vm.saveDeepSeekKey(keyDraft); keyDraft = "" }, Modifier.weight(1f), tone = QuietTone.Ink)
                QuietButton("清除", { vm.clearDeepSeekKey(); keyDraft = "" }, Modifier.weight(1f))
            }
            saved?.let { Banner(it) }
            SettingsSwitch("提问时附带选中的原文", pages, vm::setUploadPages)
            SettingsSwitch("回煲时附带私人笔记", notes, vm::setUploadNotes)
            SettingsSwitch("深色主题", dark, vm::setDark)
            QuietButton(
                "反馈",
                {
                    val intent = Intent(Intent.ACTION_SENDTO).apply {
                        data = Uri.parse("mailto:${AppConstants.FEEDBACK_EMAIL}")
                        putExtra(Intent.EXTRA_SUBJECT, "一纸书煲反馈")
                    }
                    context.startActivity(intent)
                },
                Modifier.fillMaxWidth(),
                glyph = ZenGlyph.Brush,
            )
            Text("一纸书煲  0.1.0", style = MaterialTheme.typography.bodySmall, color = scheme.onSurfaceVariant)
            Text("占用 ${usage / 1024} KB", style = MaterialTheme.typography.bodySmall, color = scheme.onSurfaceVariant)
        }
    }
}

@Composable
private fun SettingsSwitch(label: String, checked: Boolean, onChange: (Boolean) -> Unit) {
    val scheme = MaterialTheme.colorScheme
    Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
        Text(label, modifier = Modifier.weight(1f), style = MaterialTheme.typography.bodyMedium)
        Switch(
            checked = checked,
            onCheckedChange = onChange,
            colors = SwitchDefaults.colors(
                checkedThumbColor = scheme.surface,
                checkedTrackColor = scheme.onSurface,
                uncheckedThumbColor = scheme.onSurfaceVariant,
                uncheckedTrackColor = scheme.outlineVariant,
            ),
        )
    }
}

@Composable
fun BackupScreen(onBack: () -> Unit, vm: BackupViewModel = hiltViewModel()) {
    val message by vm.message.collectAsStateWithLifecycle()
    val filePath by vm.filePath.collectAsStateWithLifecycle()
    val davUrl by vm.davUrl.collectAsStateWithLifecycle()
    val davUser by vm.davUser.collectAsStateWithLifecycle()
    val davPassword by vm.davPassword.collectAsStateWithLifecycle()
    val davPath by vm.davPath.collectAsStateWithLifecycle()
    val davSaved by vm.davSaved.collectAsStateWithLifecycle()
    var restoreText by remember { mutableStateOf("") }
    val context = LocalContext.current
    val createDoc = rememberLauncherForActivityResult(ActivityResultContracts.CreateDocument("application/zip")) { uri ->
        if (uri != null) vm.exportToUri(context.contentResolver, uri)
    }
    val restorePicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) vm.restoreFromUri(context.contentResolver, uri)
    }
    PaperScaffold(title = "备份", onBack = onBack) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text("导出后换机可以恢复。", style = MaterialTheme.typography.bodyMedium)
            QuietButton(
                "导出",
                { createDoc.launch("onepaper-backup.zip") },
                Modifier.fillMaxWidth(),
                glyph = ZenGlyph.Stack,
                tone = QuietTone.Ink,
            )
            QuietButton(
                "恢复",
                { restorePicker.launch(arrayOf("application/zip", "application/json", "*/*")) },
                Modifier.fillMaxWidth(),
                glyph = ZenGlyph.Import,
            )
            QuietButton("分享备份", vm::exportLibrary, Modifier.fillMaxWidth(), glyph = ZenGlyph.Share)
            if (filePath != null) {
                QuietButton(
                    "用系统分享",
                    { ExportShare.sendFile(context, File(filePath!!), "application/zip", "分享备份") },
                    Modifier.fillMaxWidth(),
                    glyph = ZenGlyph.Share,
                )
            }
            QuietField(
                value = restoreText,
                onValueChange = { restoreText = it },
                label = "粘贴备份",
                modifier = Modifier.fillMaxWidth().height(120.dp),
                minLines = 4,
            )
            QuietButton("从粘贴恢复", { vm.restore(restoreText) }, Modifier.fillMaxWidth(), tone = QuietTone.Ghost)
            SectionTitle("网盘", glyph = ZenGlyph.Cloud)
            Text(
                "坚果云等，请用应用专用密码。",
                style = MaterialTheme.typography.bodySmall,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            QuietField(value = davUrl, onValueChange = { vm.davUrl.value = it }, label = "地址", modifier = Modifier.fillMaxWidth())
            QuietField(value = davUser, onValueChange = { vm.davUser.value = it }, label = "用户名", modifier = Modifier.fillMaxWidth())
            QuietField(
                value = davPassword,
                onValueChange = { vm.davPassword.value = it },
                label = if (davSaved) "密码（留空则沿用）" else "密码",
                modifier = Modifier.fillMaxWidth(),
                visualTransformation = PasswordVisualTransformation(),
            )
            QuietField(value = davPath, onValueChange = { vm.davPath.value = it }, label = "路径", modifier = Modifier.fillMaxWidth())
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                QuietButton("保存", vm::saveWebDav, Modifier.weight(1f), tone = QuietTone.Ink)
                QuietButton("清除", vm::clearWebDav, Modifier.weight(1f))
            }
            QuietButton("上传到网盘", vm::uploadWebDav, Modifier.fillMaxWidth(), glyph = ZenGlyph.Cloud, enabled = davSaved)
            QuietButton("从网盘恢复", vm::restoreWebDav, Modifier.fillMaxWidth(), glyph = ZenGlyph.Import, enabled = davSaved)
            message?.let { Banner(it) }
        }
    }
}

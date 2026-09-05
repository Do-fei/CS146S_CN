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
import androidx.compose.ui.unit.sp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.onepaper.app.AppConstants
import com.onepaper.app.data.share.ExportShare
import com.onepaper.app.ui.components.Banner
import com.onepaper.app.ui.components.BookSpineCard
import com.onepaper.app.ui.components.EmptyState
import com.onepaper.app.ui.components.Kicker
import com.onepaper.app.ui.components.LayerChip
import com.onepaper.app.ui.components.PaperCard
import com.onepaper.app.ui.components.PaperScaffold
import com.onepaper.app.ui.components.QuietButton
import com.onepaper.app.ui.components.QuietField
import com.onepaper.app.ui.components.QuietIconButton
import com.onepaper.app.ui.components.QuietNavBar
import com.onepaper.app.ui.components.QuietProgress
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
import com.onepaper.domain.model.KnowledgeLayer
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
            Kicker("文火")
            Text("把书读薄，把思考养厚", style = MaterialTheme.typography.headlineSmall)
            Text(
                "先在这台设备建立书房。无登录、不同步。换机请先备份。",
                style = MaterialTheme.typography.bodyMedium,
                color = MaterialTheme.colorScheme.onSurfaceVariant,
            )
            QuietButton("导入电子书", { vm.done(); onImport() }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Import, tone = QuietTone.Ink)
            QuietButton("拍摄纸书", { vm.done(); onCapture() }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Camera)
            QuietButton("稍后", { vm.done(); onLater() }, Modifier.fillMaxWidth(), tone = QuietTone.Ghost)
            Spacer(Modifier.height(12.dp))
        }
    }
}

@Composable
fun HomePager(
    onOpenBook: (String) -> Unit,
    onImport: () -> Unit,
    onCapture: () -> Unit,
    onOpenProject: (String) -> Unit,
    onOpenNote: (String) -> Unit,
    onSettings: () -> Unit,
    onBackup: () -> Unit,
    onTask: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    var tab by remember { mutableIntStateOf(0) }
    PaperScaffold(
        bottomBar = { QuietNavBar(selected = tab, onSelect = { tab = it }) },
        contentWindowInsets = WindowInsets(0, 0, 0, 0),
    ) { padding ->
        Box(modifier.padding(padding).fillMaxSize()) {
            when (tab) {
                0 -> ShelfPane(Modifier.fillMaxSize(), onOpenBook, onImport, onCapture, onTask)
                1 -> PapersPane(Modifier.fillMaxSize(), onOpenProject, onOpenNote)
                2 -> CanteenPane(Modifier.fillMaxSize(), onBackup)
                else -> MePane(Modifier.fillMaxSize(), onSettings, onBackup, onOpenNote)
            }
        }
    }
}

@Composable
private fun ShelfPane(
    modifier: Modifier,
    onOpenBook: (String) -> Unit,
    onImport: () -> Unit,
    onCapture: () -> Unit,
    onTask: (String) -> Unit,
    vm: ShelfViewModel = hiltViewModel(),
) {
    val books by vm.books.collectAsStateWithLifecycle()
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
            label = "搜索原文",
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
                            Kicker("文火")
                            Text(job.stage.ifBlank { job.kind }, style = MaterialTheme.typography.titleMedium)
                            Text("${job.status} · 第 ${job.unitDone}/${job.unitTotal} 页", style = MaterialTheme.typography.bodySmall)
                            if (job.unitTotal > 0) {
                                QuietProgress(job.unitDone.toFloat() / job.unitTotal)
                            }
                        }
                    }
                }
            }
        }
        if (hits.isNotEmpty()) {
            hits.take(5).forEach { hit ->
                Text(
                    "命中：${hit.title} · ${hit.plainText.take(40)}",
                    modifier = Modifier.padding(horizontal = 16.dp, vertical = 4.dp),
                    style = MaterialTheme.typography.bodySmall,
                    color = MaterialTheme.colorScheme.onSurfaceVariant,
                )
            }
        }
        if (books.isEmpty()) {
            EmptyState("还没有书", "导入 EPUB / PDF / 文本，或拍摄书页。不同文件不会按书名合并。", glyph = ZenGlyph.Books)
        } else {
            LazyColumn(
                contentPadding = androidx.compose.foundation.layout.PaddingValues(16.dp),
                verticalArrangement = Arrangement.spacedBy(12.dp),
            ) {
                items(books, key = { it.id }) { book ->
                    BookSpineCard(
                        title = book.title,
                        subtitle = listOfNotNull(
                            book.author.takeIf { it.isNotBlank() },
                            if (book.coverage == "EXCERPT") "摘录" else "全书",
                        ).joinToString(" · "),
                        onClick = { onOpenBook(book.id) },
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
    vm: PapersViewModel = hiltViewModel(),
) {
    val projects by vm.projectsFlow.collectAsStateWithLifecycle()
    val notes by vm.notesFlow.collectAsStateWithLifecycle()
    Column(modifier.fillMaxSize()) {
        QuietTopBar(title = "一纸")
        LazyColumn(
            Modifier.padding(horizontal = 16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
        item { SectionTitle("一纸项目", glyph = ZenGlyph.Sheet) }
        if (projects.isEmpty()) {
            item { EmptyState("还没有一纸", "打开一本书后会自动建立档案。", glyph = ZenGlyph.Sheet) }
        }
        items(projects, key = { it.id }) { project ->
            PaperCard(Modifier.fillMaxWidth(), onClick = { onOpenProject(project.id) }) {
                Text(project.title, style = MaterialTheme.typography.titleMedium)
                Text("修订 ${project.revision}", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
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
        Kicker("本机")
        Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.SpaceBetween) {
            StatCell("书", summary.first.toString())
            StatCell("笔记", summary.second.toString())
            StatCell("任务", summary.third.toString())
        }
        Banner("无登录。换机请先做完整备份。私人笔记默认不上传。")
        QuietButton("备份与恢复", onBackup, Modifier.fillMaxWidth(), glyph = ZenGlyph.Stack, tone = QuietTone.Ink)
        QuietButton("设置", onSettings, Modifier.fillMaxWidth(), glyph = ZenGlyph.Sliders)
        QuietButton("写一则笔记", { onOpenNote("new") }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Note)
        Text(
            "食堂本版只有预告和分享。反馈：设置 → 反馈。",
            style = MaterialTheme.typography.bodySmall,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
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
        Kicker("预告")
        Banner("下一版才会开放发布、列表和互动。本页没有假动态。")
        Text(
            "下一版计划：受邀群里分享一纸、收藏与评论、撤回，以及最小管理。这一版先把成果带走。",
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
        QuietButton(
            "系统分享",
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
        QuietButton("导出 / 备份", onBackup, Modifier.fillMaxWidth(), glyph = ZenGlyph.Stack)
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
            Kicker(if (book?.coverage == "EXCERPT") "摘录" else "全书")
            Text(
                if (book?.coverage == "EXCERPT") "状态：摘录，不是全书。" else "状态：按全书导入。",
                style = MaterialTheme.typography.bodyMedium,
            )
            Text(vm.deleteNotice.collectAsStateWithLifecycle().value, style = MaterialTheme.typography.bodySmall)
            QuietButton("继续读", { editionId?.let(onOpenReader) }, Modifier.fillMaxWidth(), enabled = editionId != null, glyph = ZenGlyph.Book, tone = QuietTone.Ink)
            QuietButton("AI 搭子", { onOpenCompanion(vm.bookId) }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Chat)
            QuietButton("一纸项目", { project?.let(onOpenProject) }, Modifier.fillMaxWidth(), enabled = project != null, glyph = ZenGlyph.Sheet)
            QuietButton("页面整理 / OCR", { editionId?.let(onOpenPages) }, Modifier.fillMaxWidth(), enabled = editionId != null, glyph = ZenGlyph.Scan)
            QuietButton("从书架删除", { vm.delete(); onBack() }, Modifier.fillMaxWidth(), tone = QuietTone.Danger)
        }
    }
}

@Composable
fun ReaderScreen(
    onCompanion: (String, String) -> Unit,
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
    val currentChapter = chapters.getOrNull(chapterIndex)
    val currentPage = pages.getOrNull(pageIndex)
    val scheme = MaterialTheme.colorScheme
    PaperScaffold(title = "阅读", onBack = onBack) { padding ->
        Column(
            Modifier
                .padding(padding)
                .padding(16.dp)
                .verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text("字号（改排版不应改定位）", style = MaterialTheme.typography.bodySmall, color = scheme.onSurfaceVariant)
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
            if (stale) Banner("定位已过期，只标记 stale，不伪装成功。")
            notice?.let { Banner(it) }
            if (kind == "PDF") {
                Banner("PDF 为固定版式预览。文本选择/搜索走 OCR 层，不假装可重排。")
                Text("第 ${pageIndex + 1} / ${pages.size.coerceAtLeast(1)} 页", style = MaterialTheme.typography.labelMedium)
                pdfPath?.let { PdfPreview(it, pageIndex) }
                currentPage?.recognitionDraft?.takeIf { it.isNotBlank() }?.let {
                    Text("识别稿：$it", style = MaterialTheme.typography.bodySmall)
                }
            } else if (kind == "IMAGES") {
                Banner("扫描页按图像阅读。印刷 OCR 写识别稿，不当原文。")
                Text("第 ${pageIndex + 1} / ${pages.size.coerceAtLeast(1)} 页", style = MaterialTheme.typography.labelMedium)
                currentPage?.imageRelPath?.let { ImagePreview(it) }
                currentPage?.recognitionDraft?.takeIf { it.isNotBlank() }?.let {
                    Text("识别稿：$it", style = MaterialTheme.typography.bodySmall)
                }
            } else {
                currentChapter?.let { chapter ->
                    Text("${chapter.title} · ${chapterIndex + 1}/${chapters.size.coerceAtLeast(1)}", style = MaterialTheme.typography.titleMedium)
                    Text(chapter.plainText, fontSize = font.sp, lineHeight = (font * 1.7f).sp, modifier = Modifier.padding(vertical = 8.dp))
                } ?: Text("这一版没有可抽出的文本。")
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                QuietButton("上一页", vm::prev, Modifier.weight(1f), glyph = ZenGlyph.ChevronLeft)
                QuietButton("下一页", vm::next, Modifier.weight(1f), glyph = ZenGlyph.ChevronRight)
            }
            if (kind == "PDF" || kind == "IMAGES") {
                QuietButton("识别本页（印刷 OCR）", vm::ocrCurrentPage, Modifier.fillMaxWidth(), glyph = ZenGlyph.Scan)
            }
            QuietField(
                value = selected,
                onValueChange = vm::select,
                label = "选区（粘贴或输入原文片段）",
                modifier = Modifier.fillMaxWidth(),
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.horizontalScroll(rememberScrollState())) {
                QuietButton("记笔记", { vm.highlight() }, glyph = ZenGlyph.Note)
                QuietButton("解释 / 提问", { bookId?.let { onCompanion(it, selected) } }, glyph = ZenGlyph.Chat)
            }
            LayerChip(KnowledgeLayer.SOURCE)
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
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) vm.import(uri, uri.lastPathSegment ?: "file")
    }
    val scheme = MaterialTheme.colorScheme
    PaperScaffold(title = "导入确认", onBack = onDone) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            ZenMark(ZenGlyph.Import, Modifier.height(72.dp).fillMaxWidth(), tint = scheme.outline)
            Text("文件会复制到应用私有目录。加密 / DRM 会被拒绝，不会尝试绕过。", style = MaterialTheme.typography.bodyMedium)
            Text("选择器给的 content URI 常常没有扩展名，会按 MIME / 文件头识别 EPUB、PDF、图片和文本。", style = MaterialTheme.typography.bodySmall, color = scheme.onSurfaceVariant)
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("按摘录而不是全书")
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
            QuietButton("选择文件", { picker.launch(arrayOf("*/*")) }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Sheet, tone = QuietTone.Ink)
            QuietButton("导入随包说明书（EPUB）", vm::importBundledEpub, Modifier.fillMaxWidth(), glyph = ZenGlyph.Book)
            QuietButton("导入随包样页（PDF）", vm::importBundledPdf, Modifier.fillMaxWidth(), glyph = ZenGlyph.Scan)
            last?.let { outcome ->
                if (outcome.rejectedReason != null) {
                    Banner("未导入：${outcome.rejectedReason}")
                } else {
                    Banner("已复制并建档。书与文件一对一，不按书名合并。")
                    QuietButton("打开这本书", { onOpenBook(outcome.bookId) }, Modifier.fillMaxWidth(), enabled = outcome.bookId.isNotBlank(), glyph = ZenGlyph.Book, tone = QuietTone.Ink)
                    QuietButton("返回书架", onDone, Modifier.fillMaxWidth(), tone = QuietTone.Ghost)
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
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.GetMultipleContents()) { uris ->
        if (uris.isNotEmpty()) vm.importImages(uris)
    }
    PaperScaffold(title = "自炊台", onBack = onDone) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            ZenMark(ZenGlyph.Camera, Modifier.height(72.dp).fillMaxWidth())
            Banner("拒相机时仍可用相册。选中的页会复制进私有目录并建成摘录书。自动翻页检测未承诺。")
            QuietButton("从相册选页", { picker.launch("image/*") }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Camera, tone = QuietTone.Ink)
            QuietButton("改为导入文件", onImport, Modifier.fillMaxWidth(), glyph = ZenGlyph.Import)
            last?.let { outcome ->
                if (outcome.rejectedReason != null) {
                    Banner("未导入：${outcome.rejectedReason}")
                } else {
                    Banner("已建立自炊页档案。请到页面整理做印刷 OCR。")
                    QuietButton("打开这本自炊页", { onOpenBook(outcome.bookId) }, Modifier.fillMaxWidth(), enabled = outcome.bookId.isNotBlank(), glyph = ZenGlyph.Book, tone = QuietTone.Ink)
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
            Kicker("BYOK")
            Text("DeepSeek（我们不提供 AI 服务）", style = MaterialTheme.typography.titleMedium)
            Text("填你自己的 API Key。提问时只发送当前选区或检索片段到 DeepSeek，费用由你的 Key 承担。Key 存在本机密钥库，不进备份。", style = MaterialTheme.typography.bodySmall, color = scheme.onSurfaceVariant)
            if (masked != null) Text("已保存：$masked", style = MaterialTheme.typography.bodySmall)
            QuietField(
                value = keyDraft,
                onValueChange = { keyDraft = it },
                label = "DeepSeek API Key",
                visualTransformation = PasswordVisualTransformation(),
                modifier = Modifier.fillMaxWidth(),
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                QuietButton("保存", { vm.saveDeepSeekKey(keyDraft); keyDraft = "" }, Modifier.weight(1f), tone = QuietTone.Ink)
                QuietButton("清除", { vm.clearDeepSeekKey(); keyDraft = "" }, Modifier.weight(1f))
            }
            saved?.let { Banner(it) }
            SettingsSwitch("提问时允许发送指定书页/选区", pages, vm::setUploadPages)
            SettingsSwitch("回煲时附带私人笔记（默认关）", notes, vm::setUploadNotes)
            SettingsSwitch("深色主题", dark, vm::setDark)
            QuietButton(
                "反馈（${AppConstants.FEEDBACK_EMAIL}）",
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
            Text("本地占用约 ${usage / 1024} KB", style = MaterialTheme.typography.bodySmall, color = scheme.onSurfaceVariant)
            Text("一纸书煲 / OnePaper  0.1.0-delivery", style = MaterialTheme.typography.bodySmall, color = scheme.onSurfaceVariant)
            Text("无 Key 时阅读、笔记、导出仍可用。印刷 OCR 走端侧 ML Kit。", style = MaterialTheme.typography.bodySmall, color = scheme.onSurfaceVariant)
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
    var restoreText by remember { mutableStateOf("") }
    val context = LocalContext.current
    val restorePicker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri == null) return@rememberLauncherForActivityResult
        runCatching {
            context.contentResolver.openInputStream(uri)?.bufferedReader()?.use { it.readText() }
        }.getOrNull()?.let { raw ->
            restoreText = raw.take(8_000)
            vm.restore(raw)
        }
    }
    PaperScaffold(title = "备份恢复", onBack = onBack) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            ZenMark(ZenGlyph.Stack, Modifier.height(72.dp).fillMaxWidth())
            Text("无账号可用。备份不含 DeepSeek Key / token。", style = MaterialTheme.typography.bodyMedium)
            QuietButton("导出完整备份", vm::exportLibrary, Modifier.fillMaxWidth(), glyph = ZenGlyph.Stack, tone = QuietTone.Ink)
            if (filePath != null) {
                QuietButton(
                    "系统分享备份文件",
                    { ExportShare.sendFile(context, File(filePath!!), "application/json", "分享备份") },
                    Modifier.fillMaxWidth(),
                    glyph = ZenGlyph.Share,
                )
            }
            QuietButton(
                "从文件恢复",
                { restorePicker.launch(arrayOf("application/json", "text/*", "*/*")) },
                Modifier.fillMaxWidth(),
                glyph = ZenGlyph.Import,
            )
            QuietField(
                value = restoreText,
                onValueChange = { restoreText = it },
                label = "粘贴备份 JSON 预览后恢复",
                modifier = Modifier.fillMaxWidth().height(160.dp),
                minLines = 6,
            )
            QuietButton("预览并恢复", { vm.restore(restoreText) }, Modifier.fillMaxWidth())
            message?.let { Banner(it) }
        }
    }
}

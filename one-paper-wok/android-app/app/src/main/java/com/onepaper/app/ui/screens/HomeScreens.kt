package com.onepaper.app.ui.screens

import android.graphics.Bitmap
import android.graphics.pdf.PdfRenderer
import android.os.ParcelFileDescriptor
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.clickable
import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Add
import androidx.compose.material.icons.outlined.AutoStories
import androidx.compose.material.icons.outlined.CameraAlt
import androidx.compose.material.icons.outlined.Description
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material.icons.outlined.PhotoLibrary
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.FilterChip
import androidx.compose.material3.FloatingActionButton
import androidx.compose.material3.Icon
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Slider
import androidx.compose.material3.Switch
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
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
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.Image
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.onepaper.app.ui.components.Banner
import com.onepaper.app.ui.components.EmptyState
import com.onepaper.app.ui.components.LayerChip
import com.onepaper.app.ui.vm.BackupViewModel
import com.onepaper.app.ui.vm.BookViewModel
import com.onepaper.app.ui.vm.ImportViewModel
import com.onepaper.app.ui.vm.MeViewModel
import com.onepaper.app.ui.vm.OnboardingViewModel
import com.onepaper.app.ui.vm.PapersViewModel
import com.onepaper.app.ui.vm.ReaderViewModel
import com.onepaper.app.ui.vm.SettingsViewModel
import com.onepaper.app.ui.vm.ShelfViewModel
import com.onepaper.domain.model.KnowledgeLayer
import java.io.File

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun OnboardingScreen(
    onImport: () -> Unit,
    onCapture: () -> Unit,
    onLater: () -> Unit,
    vm: OnboardingViewModel = hiltViewModel(),
) {
    Scaffold(topBar = { TopAppBar(title = { Text("一纸书煲") }) }) { padding ->
        Column(
            Modifier
                .padding(padding)
                .padding(24.dp)
                .fillMaxSize(),
            verticalArrangement = Arrangement.spacedBy(16.dp),
        ) {
            Text("把书读薄，把思考养厚", style = MaterialTheme.typography.headlineSmall)
            Text("先在这台设备建立书房。无登录、不同步。换机请先备份。")
            Button(onClick = { vm.done(); onImport() }, modifier = Modifier.fillMaxWidth()) {
                Text("导入电子书")
            }
            OutlinedButton(onClick = { vm.done(); onCapture() }, modifier = Modifier.fillMaxWidth()) {
                Text("拍摄纸书")
            }
            TextButton(onClick = { vm.done(); onLater() }) { Text("稍后") }
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
    Scaffold(
        modifier = modifier,
        floatingActionButton = {
            if (tab == 0) {
                FloatingActionButton(onClick = onImport) {
                    Icon(Icons.Outlined.Add, contentDescription = "导入")
                }
            }
        },
        bottomBar = {
            NavigationBar {
                NavigationBarItem(
                    selected = tab == 0,
                    onClick = { tab = 0 },
                    icon = { Icon(Icons.Outlined.AutoStories, null) },
                    label = { Text("书架") },
                )
                NavigationBarItem(
                    selected = tab == 1,
                    onClick = { tab = 1 },
                    icon = { Icon(Icons.Outlined.Description, null) },
                    label = { Text("一纸") },
                )
                NavigationBarItem(
                    selected = tab == 2,
                    onClick = { tab = 2 },
                    icon = { Icon(Icons.Outlined.Person, null) },
                    label = { Text("我的") },
                )
            }
        },
    ) { padding ->
        when (tab) {
            0 -> ShelfPane(Modifier.padding(padding), onOpenBook, onCapture, onTask)
            1 -> PapersPane(Modifier.padding(padding), onOpenProject, onOpenNote)
            else -> MePane(Modifier.padding(padding), onSettings, onBackup, onOpenNote)
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
private fun ShelfPane(
    modifier: Modifier,
    onOpenBook: (String) -> Unit,
    onCapture: () -> Unit,
    onTask: (String) -> Unit,
    vm: ShelfViewModel = hiltViewModel(),
) {
    val books by vm.books.collectAsStateWithLifecycle()
    val jobs by vm.jobs.collectAsStateWithLifecycle()
    val hits by vm.hits.collectAsStateWithLifecycle()
    val query by vm.query.collectAsStateWithLifecycle()
    Column(modifier.fillMaxSize()) {
        TopAppBar(title = { Text("书架") }, actions = {
            TextButton(onClick = onCapture) {
                Icon(Icons.Outlined.CameraAlt, contentDescription = null)
                Text("拍摄")
            }
        })
        OutlinedTextField(
            value = query,
            onValueChange = vm::search,
            modifier = Modifier
                .fillMaxWidth()
                .padding(horizontal = 16.dp),
            label = { Text("搜索原文（中文 n-gram）") },
        )
        if (jobs.any { it.status != "COMPLETED" }) {
            jobs.take(2).forEach { job ->
                Card(
                    Modifier
                        .padding(16.dp)
                        .fillMaxWidth()
                        .clickable { onTask(job.clientJobId) },
                ) {
                    Column(Modifier.padding(12.dp)) {
                        Text(job.stage.ifBlank { job.kind })
                        Text("${job.status} · 第 ${job.unitDone}/${job.unitTotal} 页")
                        if (job.unitTotal > 0) {
                            LinearProgressIndicator(
                                progress = { job.unitDone.toFloat() / job.unitTotal },
                                modifier = Modifier.fillMaxWidth(),
                            )
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
                )
            }
        }
        if (books.isEmpty()) {
            EmptyState("还没有书", "导入 EPUB / PDF / 文本，或拍摄书页。不同文件不会按书名合并。")
        } else {
            LazyColumn {
                items(books, key = { it.id }) { book ->
                    Card(
                        Modifier
                            .padding(horizontal = 16.dp, vertical = 8.dp)
                            .fillMaxWidth()
                            .clickable { onOpenBook(book.id) },
                    ) {
                        Column(Modifier.padding(16.dp)) {
                            Text(book.title, style = MaterialTheme.typography.titleMedium)
                            Text(
                                listOfNotNull(
                                    book.author.takeIf { it.isNotBlank() },
                                    if (book.coverage == "EXCERPT") "摘录" else "全书",
                                ).joinToString(" · "),
                            )
                            LayerChip(KnowledgeLayer.SOURCE)
                        }
                    }
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
    LazyColumn(modifier.padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        item { Text("一纸项目", style = MaterialTheme.typography.titleLarge) }
        if (projects.isEmpty()) {
            item { EmptyState("还没有一纸", "打开一本书后会自动建立档案。") }
        }
        items(projects, key = { it.id }) { project ->
            Card(Modifier.clickable { onOpenProject(project.id) }.fillMaxWidth()) {
                Column(Modifier.padding(16.dp)) {
                    Text(project.title, style = MaterialTheme.typography.titleMedium)
                    Text("修订 ${project.revision}")
                }
            }
        }
        item { Text("笔记", style = MaterialTheme.typography.titleLarge) }
        items(notes, key = { it.id }) { note ->
            Card(Modifier.clickable { onOpenNote(note.id) }.fillMaxWidth()) {
                Column(Modifier.padding(16.dp)) {
                    Text(note.title.ifBlank { "未命名笔记" })
                    Text(note.userDraft.take(80), style = MaterialTheme.typography.bodySmall)
                }
            }
        }
        item {
            OutlinedButton(onClick = { onOpenNote("new") }) { Text("新建笔记") }
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
    Column(modifier.padding(24.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("我的", style = MaterialTheme.typography.headlineSmall)
        Text("书 ${summary.first} · 笔记 ${summary.second} · 任务 ${summary.third}")
        Banner("无登录。换机请先做完整备份。私人笔记默认不上传。")
        Button(onClick = onBackup, modifier = Modifier.fillMaxWidth()) { Text("备份与恢复") }
        OutlinedButton(onClick = onSettings, modifier = Modifier.fillMaxWidth()) { Text("设置") }
        OutlinedButton(onClick = { onOpenNote("new") }, modifier = Modifier.fillMaxWidth()) { Text("写一则笔记") }
        Text("食堂未进入首版，请用系统分享或导出。", style = MaterialTheme.typography.bodySmall)
    }
}

@OptIn(ExperimentalMaterial3Api::class)
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
    Scaffold(topBar = {
        TopAppBar(title = { Text(book?.title ?: "书") }, navigationIcon = {
            TextButton(onClick = onBack) { Text("返回") }
        })
    }) { padding ->
        Column(Modifier.padding(padding).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text(if (book?.coverage == "EXCERPT") "状态：摘录，不是全书。" else "状态：按全书导入。")
            Text(vm.deleteNotice.collectAsStateWithLifecycle().value, style = MaterialTheme.typography.bodySmall)
            Button(
                onClick = { editionId?.let(onOpenReader) },
                enabled = editionId != null,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("继续读") }
            OutlinedButton(onClick = { onOpenCompanion(vm.bookId) }, modifier = Modifier.fillMaxWidth()) {
                Text("AI 搭子")
            }
            OutlinedButton(
                onClick = { project?.let(onOpenProject) },
                enabled = project != null,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("一纸项目") }
            OutlinedButton(
                onClick = { editionId?.let(onOpenPages) },
                enabled = editionId != null,
                modifier = Modifier.fillMaxWidth(),
            ) { Text("页面整理 / OCR") }
            TextButton(onClick = { vm.delete(); onBack() }) { Text("从书架删除") }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
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
    Scaffold(topBar = {
        TopAppBar(title = { Text("阅读") }, navigationIcon = { TextButton(onClick = onBack) { Text("返回") } })
    }) { padding ->
        Column(Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState())) {
            Text("字号（改排版不应改定位）")
            Slider(value = font, onValueChange = vm::setFont, valueRange = 14f..28f)
            if (stale) Banner("定位已过期，只标记 stale，不伪装成功。")
            if (kind == "PDF") {
                Banner("PDF 为固定版式预览。文本选择/搜索走 OCR 层，不假装可重排。")
                pdfPath?.let { PdfPreview(it) }
            } else {
                chapters.forEach { chapter ->
                    Text(chapter.title, style = MaterialTheme.typography.titleMedium)
                    Text(chapter.plainText, fontSize = font.sp, modifier = Modifier.padding(vertical = 8.dp))
                }
            }
            OutlinedTextField(
                value = selected,
                onValueChange = vm::select,
                label = { Text("选区（粘贴或输入原文片段）") },
                modifier = Modifier.fillMaxWidth(),
            )
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.horizontalScroll(rememberScrollState())) {
                FilterChip(selected = false, onClick = { vm.highlight() }, label = { Text("记笔记") })
                FilterChip(selected = false, onClick = {
                    bookId?.let { onCompanion(it, selected) }
                }, label = { Text("解释 / 提问") })
            }
            LayerChip(KnowledgeLayer.SOURCE)
        }
    }
}

@Composable
private fun PdfPreview(relativePath: String) {
    val context = LocalContext.current
    val bitmap = remember(relativePath) {
        runCatching {
            val file = File(context.filesDir, relativePath)
            if (!file.exists()) return@runCatching null
            val pfd = ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY)
            val renderer = PdfRenderer(pfd)
            val page = renderer.openPage(0)
            val bmp = Bitmap.createBitmap(page.width, page.height, Bitmap.Config.ARGB_8888)
            page.render(bmp, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY)
            page.close()
            renderer.close()
            pfd.close()
            bmp
        }.getOrNull()
    }
    if (bitmap != null) {
        Image(bitmap.asImageBitmap(), contentDescription = "PDF 第 1 页", modifier = Modifier.fillMaxWidth().height(360.dp))
    } else {
        Text("未能渲染 PDF 首页。")
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ImportScreen(onDone: () -> Unit, vm: ImportViewModel = hiltViewModel()) {
    val last by vm.last.collectAsStateWithLifecycle()
    val excerpt by vm.excerpt.collectAsStateWithLifecycle()
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.OpenDocument()) { uri ->
        if (uri != null) vm.import(uri, uri.lastPathSegment ?: "file")
    }
    Scaffold(topBar = { TopAppBar(title = { Text("导入确认") }, navigationIcon = { TextButton(onClick = onDone) { Text("返回") } }) }) { padding ->
        Column(Modifier.padding(padding).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text("文件会复制到应用私有目录。加密 / DRM 会被拒绝，不会尝试绕过。")
            Row(verticalAlignment = Alignment.CenterVertically) {
                Text("按摘录而不是全书")
                Spacer(Modifier.weight(1f))
                Switch(checked = excerpt, onCheckedChange = { vm.excerpt.value = it })
            }
            Button(onClick = { picker.launch(arrayOf("*/*")) }, modifier = Modifier.fillMaxWidth()) {
                Text("选择文件")
            }
            last?.let { outcome ->
                if (outcome.rejectedReason != null) {
                    Banner("未导入：${outcome.rejectedReason}")
                } else {
                    Banner("已复制并建档。书与文件一对一，不按书名合并。")
                    Button(onClick = onDone) { Text("完成") }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CaptureScreen(onDone: () -> Unit, onImport: () -> Unit) {
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.GetMultipleContents()) { }
    Scaffold(topBar = { TopAppBar(title = { Text("自炊台") }, navigationIcon = { TextButton(onClick = onDone) { Text("返回") } }) }) { padding ->
        Column(Modifier.padding(padding).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Banner("拒相机时仍可用相册。存储满时停止连拍。自动翻页检测未承诺。")
            Button(onClick = { picker.launch("image/*") }, modifier = Modifier.fillMaxWidth()) {
                Icon(Icons.Outlined.PhotoLibrary, null)
                Text(" 从相册选页")
            }
            OutlinedButton(onClick = onImport, modifier = Modifier.fillMaxWidth()) { Text("改为导入文件") }
            Text("连拍、双页拆分、质量提示在相机权限可用后进入同一整理台。")
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun SettingsScreen(onBack: () -> Unit, vm: SettingsViewModel = hiltViewModel()) {
    val pages by vm.uploadPages.collectAsStateWithLifecycle()
    val notes by vm.uploadNotes.collectAsStateWithLifecycle()
    val dark by vm.dark.collectAsStateWithLifecycle()
    val usage by vm.usage.collectAsStateWithLifecycle()
    Scaffold(topBar = { TopAppBar(title = { Text("设置") }, navigationIcon = { TextButton(onClick = onBack) { Text("返回") } }) }) { padding ->
        Column(Modifier.padding(padding).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                Text("允许上传指定书页（默认关）")
                Spacer(Modifier.weight(1f))
                Switch(checked = pages, onCheckedChange = vm::setUploadPages)
            }
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                Text("允许上传私人笔记（默认关）")
                Spacer(Modifier.weight(1f))
                Switch(checked = notes, onCheckedChange = vm::setUploadNotes)
            }
            Row(verticalAlignment = Alignment.CenterVertically, modifier = Modifier.fillMaxWidth()) {
                Text("深色主题")
                Spacer(Modifier.weight(1f))
                Switch(checked = dark, onCheckedChange = vm::setDark)
            }
            Text("本地占用约 ${usage / 1024} KB")
            Text("一纸书煲 / OnePaper  0.1.0-delivery")
            Text("生产 Key 不进 APK。无额度时仍可阅读、笔记、导出。")
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun BackupScreen(onBack: () -> Unit, vm: BackupViewModel = hiltViewModel()) {
    val message by vm.message.collectAsStateWithLifecycle()
    var restoreText by remember { mutableStateOf("") }
    Scaffold(topBar = { TopAppBar(title = { Text("备份恢复") }, navigationIcon = { TextButton(onClick = onBack) { Text("返回") } }) }) { padding ->
        Column(Modifier.padding(padding).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text("无账号可用。备份不含 token。")
            Button(onClick = vm::exportLibrary, modifier = Modifier.fillMaxWidth()) { Text("导出完整备份") }
            OutlinedTextField(
                value = restoreText,
                onValueChange = { restoreText = it },
                label = { Text("粘贴备份 JSON 预览后恢复") },
                modifier = Modifier.fillMaxWidth().height(160.dp),
            )
            OutlinedButton(onClick = { vm.restore(restoreText) }, modifier = Modifier.fillMaxWidth()) { Text("预览并恢复") }
            message?.let { Banner(it) }
        }
    }
}

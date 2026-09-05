package com.onepaper.app.ui.screens

import android.net.Uri
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.onepaper.app.data.share.ExportShare
import com.onepaper.app.ui.components.Banner
import com.onepaper.app.ui.components.Kicker
import com.onepaper.app.ui.components.LayerChip
import com.onepaper.app.ui.components.PaperCard
import com.onepaper.app.ui.components.PaperScaffold
import com.onepaper.app.ui.components.QuietButton
import com.onepaper.app.ui.components.QuietField
import com.onepaper.app.ui.components.QuietTone
import com.onepaper.app.ui.graphics.ZenGlyph
import com.onepaper.app.ui.graphics.ZenMark
import com.onepaper.app.ui.vm.BackupViewModel
import com.onepaper.app.ui.vm.CompanionVm
import com.onepaper.app.ui.vm.NoteViewModel
import com.onepaper.app.ui.vm.PagesViewModel
import com.onepaper.app.ui.vm.ProjectViewModel
import com.onepaper.app.ui.vm.RecookViewModel
import com.onepaper.app.ui.vm.ShelfViewModel
import com.onepaper.domain.model.KnowledgeLayer
import com.onepaper.domain.recook.ProposalDecision
import java.io.File

@Composable
fun ProjectScreen(
    onRecook: (String) -> Unit,
    onExport: (String) -> Unit,
    onBack: () -> Unit,
    vm: ProjectViewModel = hiltViewModel(),
) {
    val project by vm.project.collectAsStateWithLifecycle()
    val sections by vm.sections.collectAsStateWithLifecycle()
    val proposalId by vm.proposalId.collectAsStateWithLifecycle()
    LaunchedEffect(Unit) { vm.refresh() }
    PaperScaffold(title = project?.title ?: "一纸", onBack = onBack) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text("用户编辑会锁定该段，再生成不会覆盖。", style = MaterialTheme.typography.bodyMedium)
            sections.forEach { section ->
                var body by remember(section.id, section.revision) { mutableStateOf(section.body) }
                PaperCard(Modifier.fillMaxWidth()) {
                    Text(section.title, style = MaterialTheme.typography.titleMedium)
                    LayerChip(if (section.userLocked) KnowledgeLayer.USER else KnowledgeLayer.AI)
                    QuietField(
                        value = body,
                        onValueChange = { body = it },
                        modifier = Modifier.fillMaxWidth(),
                        minLines = 3,
                    )
                    Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                        QuietButton("保存为我的理解", { vm.saveSection(section.sectionId, body) }, Modifier.weight(1f), glyph = ZenGlyph.Brush, tone = QuietTone.Ink)
                        QuietButton("再生成此段", { vm.regenerate(section.sectionId) }, Modifier.weight(1f), enabled = !section.userLocked, glyph = ZenGlyph.Chat)
                    }
                }
            }
            QuietButton(
                "回煲（生成建议，不直接覆盖）",
                { vm.recook(listOf("根据笔记回煲")) },
                Modifier.fillMaxWidth(),
                glyph = ZenGlyph.Wok,
                tone = QuietTone.Ink,
            )
            if (proposalId != null) {
                QuietButton("打开审阅", { onRecook(proposalId!!) }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Sheet)
            }
            QuietButton("导出", { onExport(vm.projectId) }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Share)
        }
    }
}

@Composable
fun RecookScreen(onBack: () -> Unit, vm: RecookViewModel = hiltViewModel()) {
    val items by vm.items.collectAsStateWithLifecycle()
    val current by vm.currentBodies.collectAsStateWithLifecycle()
    val banner by vm.banner.collectAsStateWithLifecycle()
    var edits by remember { mutableStateOf<Map<String, String>>(emptyMap()) }
    PaperScaffold(title = "回煲审阅", onBack = onBack) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            ZenMark(ZenGlyph.Wok, Modifier.height(72.dp).fillMaxWidth())
            Text("逐条接受 / 拒绝 / 改后接受。禁止整份重写。", style = MaterialTheme.typography.bodyMedium)
            banner?.let { Banner(it) }
            items.forEach { item ->
                PaperCard(Modifier.fillMaxWidth()) {
                    Kicker("操作 ${item.op}")
                    Text(item.sectionId, style = MaterialTheme.typography.titleSmall)
                    Text("当前：${current[item.sectionId].orEmpty()}", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
                    Text("建议：${item.proposedBody.orEmpty()}", style = MaterialTheme.typography.bodyMedium)
                    QuietField(
                        value = edits[item.id] ?: item.proposedBody.orEmpty(),
                        onValueChange = { edits = edits + (item.id to it) },
                        label = "改后接受",
                        modifier = Modifier.fillMaxWidth(),
                    )
                }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
                QuietButton("全部接受", { vm.decideAll(ProposalDecision.ACCEPT) }, Modifier.weight(1f), tone = QuietTone.Ink)
                QuietButton("全部拒绝", { vm.decideAll(ProposalDecision.REJECT) }, Modifier.weight(1f))
            }
            QuietButton("按改稿接受", { vm.decideAll(ProposalDecision.ACCEPT_EDITED, edits) }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Brush)
        }
    }
}

@Composable
fun CompanionScreen(
    onBack: () -> Unit,
    vm: CompanionVm = hiltViewModel(),
) {
    val items by vm.messages.collectAsStateWithLifecycle()
    val usingDeepSeek by vm.usingDeepSeek.collectAsStateWithLifecycle()
    var draft by remember { mutableStateOf("") }
    var quote by remember { mutableStateOf(vm.seedQuote) }
    PaperScaffold(title = "AI 搭子", onBack = onBack) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Banner(
                if (usingDeepSeek) "将用你保存在本机的 DeepSeek Key 提问，只发送当前证据片段。"
                else "未填写 DeepSeek Key，当前走本地说明。阅读不受影响。",
            )
            items.forEach { msg ->
                PaperCard(Modifier.fillMaxWidth()) {
                    Kicker(if (msg.role == "user") "我" else "搭子")
                    Text(msg.text, style = MaterialTheme.typography.bodyMedium)
                    if (msg.insufficientEvidence) {
                        Text("证据不足", style = MaterialTheme.typography.bodySmall, color = MaterialTheme.colorScheme.tertiary)
                    }
                }
            }
            QuietField(value = quote, onValueChange = { quote = it }, label = "引用原文（可点回）", modifier = Modifier.fillMaxWidth())
            QuietField(value = draft, onValueChange = { draft = it }, label = "提问", modifier = Modifier.fillMaxWidth())
            QuietButton(
                "发送（可停于无额度/离线）",
                { vm.ask(draft, quote.ifBlank { null }); draft = "" },
                Modifier.fillMaxWidth(),
                glyph = ZenGlyph.Chat,
                tone = QuietTone.Ink,
            )
            LayerChip(KnowledgeLayer.AI)
        }
    }
}

@Composable
fun NoteScreen(
    onBack: () -> Unit,
    onHandwriting: (String) -> Unit,
    vm: NoteViewModel = hiltViewModel(),
) {
    val note by vm.note.collectAsStateWithLifecycle()
    var title by remember { mutableStateOf("") }
    var body by remember { mutableStateOf("") }
    var recognition by remember { mutableStateOf("") }
    LaunchedEffect(note) {
        title = note?.title.orEmpty()
        body = note?.userDraft.orEmpty()
        recognition = note?.recognitionDraft.orEmpty()
    }
    PaperScaffold(title = "笔记", onBack = onBack) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            QuietField(value = title, onValueChange = { title = it; vm.save(title, body, recognition.ifBlank { null }) }, label = "标题", modifier = Modifier.fillMaxWidth())
            QuietField(value = body, onValueChange = { body = it; vm.save(title, body, recognition.ifBlank { null }) }, label = "我的稿", modifier = Modifier.fillMaxWidth(), minLines = 6)
            QuietField(value = recognition, onValueChange = {}, enabled = false, label = "识别稿（只读，不当原文）", modifier = Modifier.fillMaxWidth())
            LayerChip(KnowledgeLayer.USER)
            if (vm.noteId != null) {
                QuietButton("手写校对", { onHandwriting(vm.noteId) }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Brush)
            }
        }
    }
}

@Composable
fun HandwritingScreen(onBack: () -> Unit, vm: NoteViewModel = hiltViewModel()) {
    val note by vm.note.collectAsStateWithLifecycle()
    var user by remember { mutableStateOf("") }
    LaunchedEffect(note) { user = note?.userDraft.orEmpty() }
    PaperScaffold(title = "手写校对", onBack = onBack) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text("左：识别稿。右：你改的是用户稿。", style = MaterialTheme.typography.bodyMedium)
            Text("识别：${note?.recognitionDraft ?: "（无）"}", style = MaterialTheme.typography.bodySmall)
            QuietField(value = user, onValueChange = { user = it }, label = "用户稿", modifier = Modifier.fillMaxWidth(), minLines = 6)
            QuietButton("保存用户稿", { vm.save(note?.title.orEmpty(), user, note?.recognitionDraft) }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Brush, tone = QuietTone.Ink)
        }
    }
}

@Composable
fun ExportScreen(onBack: () -> Unit, vm: BackupViewModel = hiltViewModel(), projectVm: ProjectViewModel = hiltViewModel()) {
    val message by vm.message.collectAsStateWithLifecycle()
    val filePath by vm.filePath.collectAsStateWithLifecycle()
    val context = LocalContext.current
    PaperScaffold(title = "导出预览", onBack = onBack) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text("默认不含阅读器私人批注。可勾选范围后导出 Markdown。", style = MaterialTheme.typography.bodyMedium)
            QuietButton("导出 Markdown", { vm.exportMarkdown(projectVm.projectId) }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Sheet, tone = QuietTone.Ink)
            if (filePath != null) {
                QuietButton(
                    "系统分享 Markdown",
                    { ExportShare.sendFile(context, File(filePath!!), "text/markdown", "分享一纸") },
                    Modifier.fillMaxWidth(),
                    glyph = ZenGlyph.Share,
                )
            }
            message?.let { Banner(it) }
        }
    }
}

@Composable
fun PagesScreen(onBack: () -> Unit, vm: PagesViewModel = hiltViewModel()) {
    val pages by vm.pages.collectAsStateWithLifecycle()
    var proof by remember { mutableStateOf("") }
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        if (uri != null) vm.addPage(uri, uri.lastPathSegment ?: "page.jpg")
    }
    PaperScaffold(title = "页面整理", onBack = onBack) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Banner("缩略图失败、补拍、旋转裁切都在此台处理。识别稿与原图分列。")
            QuietButton("补拍 / 加入相册页", { picker.launch("image/*") }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Camera, tone = QuietTone.Ink)
            pages.forEach { page ->
                PaperCard(Modifier.fillMaxWidth()) {
                    Text("第 ${page.index + 1} 页", style = MaterialTheme.typography.titleMedium)
                    Text("识别稿：${page.recognitionDraft ?: "尚未识别"}", style = MaterialTheme.typography.bodySmall)
                    Text("用户校对：${page.ocrText ?: "—"}", style = MaterialTheme.typography.bodySmall)
                    QuietButton("印刷 OCR", { vm.ocrPage(page) }, glyph = ZenGlyph.Scan)
                    QuietField(value = proof, onValueChange = { proof = it }, label = "校对写入用户稿", modifier = Modifier.fillMaxWidth())
                    QuietButton("保存校对", { vm.proofread(page, proof) }, glyph = ZenGlyph.Brush, tone = QuietTone.Ink)
                }
            }
        }
    }
}

@Composable
fun TaskScreen(onBack: () -> Unit, shelf: ShelfViewModel = hiltViewModel()) {
    val jobs by shelf.jobs.collectAsStateWithLifecycle()
    PaperScaffold(title = "任务", onBack = onBack) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
        ) {
            Text("强停后文件仍在，可手动恢复，不承诺自动续跑。", style = MaterialTheme.typography.bodyMedium)
            jobs.forEach { job ->
                PaperCard(Modifier.fillMaxWidth()) {
                    Kicker(job.status)
                    Text(job.clientJobId, style = MaterialTheme.typography.titleSmall)
                    Text("${job.stage} · 第 ${job.unitDone}/${job.unitTotal} 页", style = MaterialTheme.typography.bodySmall)
                    Text(job.message, style = MaterialTheme.typography.bodyMedium)
                }
            }
        }
    }
}

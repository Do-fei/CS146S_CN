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
import androidx.compose.material3.Button
import androidx.compose.material3.Card
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedButton
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.material3.TopAppBar
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.ui.platform.LocalContext
import com.onepaper.app.data.share.ExportShare
import java.io.File
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.onepaper.app.ui.components.Banner
import com.onepaper.app.ui.components.LayerChip
import com.onepaper.app.ui.vm.BackupViewModel
import com.onepaper.app.ui.vm.CompanionVm
import com.onepaper.app.ui.vm.NoteViewModel
import com.onepaper.app.ui.vm.PagesViewModel
import com.onepaper.app.ui.vm.ProjectViewModel
import com.onepaper.app.ui.vm.RecookViewModel
import com.onepaper.app.ui.vm.ShelfViewModel
import com.onepaper.domain.model.KnowledgeLayer
import com.onepaper.domain.recook.ProposalDecision

@OptIn(ExperimentalMaterial3Api::class)
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
    Scaffold(topBar = {
        TopAppBar(title = { Text(project?.title ?: "一纸") }, navigationIcon = { TextButton(onClick = onBack) { Text("返回") } })
    }) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Text("用户编辑会锁定该段，再生成不会覆盖。")
            sections.forEach { section ->
                var body by remember(section.id, section.revision) { mutableStateOf(section.body) }
                Card(Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text(section.title, style = MaterialTheme.typography.titleMedium)
                        LayerChip(if (section.userLocked) KnowledgeLayer.USER else KnowledgeLayer.AI)
                        OutlinedTextField(
                            value = body,
                            onValueChange = { body = it },
                            modifier = Modifier.fillMaxWidth(),
                            minLines = 3,
                        )
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            Button(onClick = { vm.saveSection(section.sectionId, body) }) { Text("保存为我的理解") }
                            OutlinedButton(
                                onClick = { vm.regenerate(section.sectionId) },
                                enabled = !section.userLocked,
                            ) { Text("再生成此段") }
                        }
                    }
                }
            }
            Button(
                onClick = {
                    vm.recook(listOf("根据笔记回煲"))
                },
                modifier = Modifier.fillMaxWidth(),
            ) { Text("回煲（生成建议，不直接覆盖）") }
            if (proposalId != null) {
                OutlinedButton(onClick = { onRecook(proposalId!!) }, modifier = Modifier.fillMaxWidth()) {
                    Text("打开审阅")
                }
            }
            OutlinedButton(onClick = { onExport(vm.projectId) }, modifier = Modifier.fillMaxWidth()) {
                Text("导出")
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun RecookScreen(onBack: () -> Unit, vm: RecookViewModel = hiltViewModel()) {
    val items by vm.items.collectAsStateWithLifecycle()
    val current by vm.currentBodies.collectAsStateWithLifecycle()
    val banner by vm.banner.collectAsStateWithLifecycle()
    var edits by remember { mutableStateOf<Map<String, String>>(emptyMap()) }
    Scaffold(topBar = { TopAppBar(title = { Text("回煲审阅") }, navigationIcon = { TextButton(onClick = onBack) { Text("返回") } }) }) { padding ->
        Column(Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text("逐条接受 / 拒绝 / 改后接受。禁止整份重写。")
            banner?.let { Banner(it) }
            items.forEach { item ->
                Card(Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(12.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        Text("操作 ${item.op} · ${item.sectionId}")
                        Text("当前：${current[item.sectionId].orEmpty()}", style = MaterialTheme.typography.bodySmall)
                        Text("建议：${item.proposedBody.orEmpty()}")
                        OutlinedTextField(
                            value = edits[item.id] ?: item.proposedBody.orEmpty(),
                            onValueChange = { edits = edits + (item.id to it) },
                            label = { Text("改后接受") },
                            modifier = Modifier.fillMaxWidth(),
                        )
                    }
                }
            }
            Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                Button(onClick = { vm.decideAll(ProposalDecision.ACCEPT) }) { Text("全部接受") }
                OutlinedButton(onClick = { vm.decideAll(ProposalDecision.REJECT) }) { Text("全部拒绝") }
            }
            Button(onClick = { vm.decideAll(ProposalDecision.ACCEPT_EDITED, edits) }, modifier = Modifier.fillMaxWidth()) {
                Text("按改稿接受")
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun CompanionScreen(
    onBack: () -> Unit,
    vm: CompanionVm = hiltViewModel(),
) {
    val items by vm.messages.collectAsStateWithLifecycle()
    val usingDeepSeek by vm.usingDeepSeek.collectAsStateWithLifecycle()
    var draft by remember { mutableStateOf("") }
    var quote by remember { mutableStateOf(vm.seedQuote) }
    Scaffold(topBar = { TopAppBar(title = { Text("AI 搭子") }, navigationIcon = { TextButton(onClick = onBack) { Text("返回") } }) }) { padding ->
        Column(Modifier.padding(padding).padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Banner(
                if (usingDeepSeek) "将用你保存在本机的 DeepSeek Key 提问，只发送当前证据片段。"
                else "未填写 DeepSeek Key，当前走本地说明。阅读不受影响。",
            )
            items.forEach { msg ->
                Card(Modifier.fillMaxWidth().padding(vertical = 4.dp)) {
                    Column(Modifier.padding(12.dp)) {
                        Text(if (msg.role == "user") "我" else "搭子")
                        Text(msg.text)
                        if (msg.insufficientEvidence) Text("证据不足", style = MaterialTheme.typography.bodySmall)
                    }
                }
            }
            OutlinedTextField(value = quote, onValueChange = { quote = it }, label = { Text("引用原文（可点回）") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = draft, onValueChange = { draft = it }, label = { Text("提问") }, modifier = Modifier.fillMaxWidth())
            Button(onClick = { vm.ask(draft, quote.ifBlank { null }); draft = "" }, modifier = Modifier.fillMaxWidth()) {
                Text("发送（可停于无额度/离线）")
            }
            LayerChip(KnowledgeLayer.AI)
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
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
    Scaffold(topBar = { TopAppBar(title = { Text("笔记") }, navigationIcon = { TextButton(onClick = onBack) { Text("返回") } }) }) { padding ->
        Column(Modifier.padding(padding).padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            OutlinedTextField(value = title, onValueChange = { title = it; vm.save(title, body, recognition.ifBlank { null }) }, label = { Text("标题") }, modifier = Modifier.fillMaxWidth())
            OutlinedTextField(value = body, onValueChange = { body = it; vm.save(title, body, recognition.ifBlank { null }) }, label = { Text("我的稿") }, modifier = Modifier.fillMaxWidth(), minLines = 6)
            OutlinedTextField(value = recognition, onValueChange = {}, enabled = false, label = { Text("识别稿（只读，不当原文）") }, modifier = Modifier.fillMaxWidth())
            LayerChip(KnowledgeLayer.USER)
            if (vm.noteId != null) {
                OutlinedButton(onClick = { onHandwriting(vm.noteId) }) { Text("手写校对") }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun HandwritingScreen(onBack: () -> Unit, vm: NoteViewModel = hiltViewModel()) {
    val note by vm.note.collectAsStateWithLifecycle()
    var user by remember { mutableStateOf("") }
    LaunchedEffect(note) { user = note?.userDraft.orEmpty() }
    Scaffold(topBar = { TopAppBar(title = { Text("手写校对") }, navigationIcon = { TextButton(onClick = onBack) { Text("返回") } }) }) { padding ->
        Column(Modifier.padding(padding).padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("左：识别稿。右：你改的是用户稿。")
            Text("识别：${note?.recognitionDraft ?: "（无）"}")
            OutlinedTextField(value = user, onValueChange = { user = it }, label = { Text("用户稿") }, modifier = Modifier.fillMaxWidth(), minLines = 6)
            Button(onClick = { vm.save(note?.title.orEmpty(), user, note?.recognitionDraft) }) { Text("保存用户稿") }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun ExportScreen(onBack: () -> Unit, vm: BackupViewModel = hiltViewModel(), projectVm: ProjectViewModel = hiltViewModel()) {
    val message by vm.message.collectAsStateWithLifecycle()
    val filePath by vm.filePath.collectAsStateWithLifecycle()
    val context = LocalContext.current
    Scaffold(topBar = { TopAppBar(title = { Text("导出预览") }, navigationIcon = { TextButton(onClick = onBack) { Text("返回") } }) }) { padding ->
        Column(Modifier.padding(padding).padding(16.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
            Text("默认不含阅读器私人批注。可勾选范围后导出 Markdown。")
            Button(onClick = { vm.exportMarkdown(projectVm.projectId) }, modifier = Modifier.fillMaxWidth()) {
                Text("导出 Markdown")
            }
            if (filePath != null) {
                OutlinedButton(
                    onClick = { ExportShare.sendFile(context, File(filePath!!), "text/markdown", "分享一纸") },
                    modifier = Modifier.fillMaxWidth(),
                ) { Text("系统分享 Markdown") }
            }
            message?.let { Banner(it) }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun PagesScreen(onBack: () -> Unit, vm: PagesViewModel = hiltViewModel()) {
    val pages by vm.pages.collectAsStateWithLifecycle()
    var proof by remember { mutableStateOf("") }
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.GetContent()) { uri: Uri? ->
        if (uri != null) vm.addPage(uri, uri.lastPathSegment ?: "page.jpg")
    }
    Scaffold(topBar = { TopAppBar(title = { Text("页面整理") }, navigationIcon = { TextButton(onClick = onBack) { Text("返回") } }) }) { padding ->
        Column(Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Banner("缩略图失败、补拍、旋转裁切都在此台处理。识别稿与原图分列。")
            Button(onClick = { picker.launch("image/*") }) { Text("补拍 / 加入相册页") }
            pages.forEach { page ->
                Card(Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(12.dp)) {
                        Text("第 ${page.index + 1} 页")
                        Text("识别稿：${page.recognitionDraft ?: "尚未识别"}")
                        Text("用户校对：${page.ocrText ?: "—"}")
                        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                            OutlinedButton(onClick = { vm.ocrPage(page) }) { Text("印刷 OCR") }
                        }
                        OutlinedTextField(value = proof, onValueChange = { proof = it }, label = { Text("校对写入用户稿") }, modifier = Modifier.fillMaxWidth())
                        Button(onClick = { vm.proofread(page, proof) }) { Text("保存校对") }
                    }
                }
            }
        }
    }
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun TaskScreen(onBack: () -> Unit, shelf: ShelfViewModel = hiltViewModel()) {
    val jobs by shelf.jobs.collectAsStateWithLifecycle()
    Scaffold(topBar = { TopAppBar(title = { Text("任务") }, navigationIcon = { TextButton(onClick = onBack) { Text("返回") } }) }) { padding ->
        Column(Modifier.padding(padding).padding(16.dp), verticalArrangement = Arrangement.spacedBy(8.dp)) {
            Text("强停后文件仍在，可手动恢复，不承诺自动续跑。")
            jobs.forEach { job ->
                Card(Modifier.fillMaxWidth()) {
                    Column(Modifier.padding(12.dp)) {
                        Text(job.clientJobId)
                        Text("${job.status} · ${job.stage} · 第 ${job.unitDone}/${job.unitTotal} 页")
                        Text(job.message)
                    }
                }
            }
        }
    }
}

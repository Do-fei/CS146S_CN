package com.onepaper.app.ui.screens

import androidx.compose.foundation.horizontalScroll
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
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.unit.dp
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.onepaper.app.data.local.ProjectSectionEntity
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
import com.onepaper.app.ui.vm.ProjectViewModel
import com.onepaper.domain.model.KnowledgeLayer
import com.onepaper.domain.recook.SectionKind

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
    val quotes by vm.quotes.collectAsStateWithLifecycle()
    val wide = LocalConfiguration.current.screenWidthDp >= 600
    var focus by remember { mutableStateOf("map") }
    LaunchedEffect(Unit) { vm.refresh() }
    val excerpt = sections.firstOrNull { it.kind == SectionKind.EXCERPT.name }
    val essence = sections.firstOrNull { it.kind == SectionKind.ESSENCE.name }
    val mine = sections.firstOrNull { it.kind == SectionKind.UNDERSTANDING.name }
    val explore = sections.firstOrNull { it.kind == SectionKind.EXPLORE.name }
    val log = sections.firstOrNull { it.kind == SectionKind.CHANGELOG.name }
    PaperScaffold(title = project?.title ?: "一纸", onBack = onBack) { padding ->
        Column(
            Modifier.padding(padding).padding(16.dp).verticalScroll(rememberScrollState()),
            verticalArrangement = Arrangement.spacedBy(12.dp),
        ) {
            Column(horizontalAlignment = Alignment.CenterHorizontally, modifier = Modifier.fillMaxWidth()) {
                ZenMark(ZenGlyph.Wok, Modifier.height(88.dp).fillMaxWidth())
                Kicker("出煲")
                Text("成果带走。这是一纸，不是全书。", style = MaterialTheme.typography.bodyMedium)
            }
            Banner("分节地图只标层，不把三层混成一段。你改过的段会锁定。")
            Row(
                Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                QuietButton("地图", { focus = "map" }, tone = if (focus == "map") QuietTone.Ink else QuietTone.Line)
                QuietButton("原书", { focus = "source" }, tone = if (focus == "source") QuietTone.Ink else QuietTone.Line)
                QuietButton("精华", { focus = "ai" }, tone = if (focus == "ai") QuietTone.Ink else QuietTone.Line)
                QuietButton("我的", { focus = "me" }, tone = if (focus == "me") QuietTone.Ink else QuietTone.Line)
                QuietButton("待探索", { focus = "explore" }, tone = if (focus == "explore") QuietTone.Ink else QuietTone.Line)
            }
            if (focus == "map" && wide) {
                Row(Modifier.fillMaxWidth(), horizontalArrangement = Arrangement.spacedBy(8.dp)) {
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        SourceColumn(excerpt, quotes.map { it.quote })
                    }
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        essence?.let { SectionEditor(it, KnowledgeLayer.AI, vm) }
                    }
                    Column(Modifier.weight(1f), verticalArrangement = Arrangement.spacedBy(8.dp)) {
                        mine?.let { SectionEditor(it, KnowledgeLayer.USER, vm) }
                    }
                }
            } else {
                when (focus) {
                    "source" -> SourceColumn(excerpt, quotes.map { it.quote })
                    "ai" -> essence?.let { SectionEditor(it, KnowledgeLayer.AI, vm) }
                    "me" -> mine?.let { SectionEditor(it, KnowledgeLayer.USER, vm) }
                    "explore" -> {
                        explore?.let { SectionEditor(it, KnowledgeLayer.USER, vm) }
                        log?.let { SectionEditor(it, KnowledgeLayer.USER, vm) }
                    }
                    else -> {
                        SourceColumn(excerpt, quotes.map { it.quote })
                        essence?.let { SectionEditor(it, KnowledgeLayer.AI, vm) }
                        mine?.let { SectionEditor(it, KnowledgeLayer.USER, vm) }
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
            QuietButton("出煲", { onExport(vm.projectId) }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Share, tone = QuietTone.Ink)
        }
    }
}

@Composable
private fun SourceColumn(excerpt: ProjectSectionEntity?, quotes: List<String>) {
    PaperCard(Modifier.fillMaxWidth()) {
        Text("原书", style = MaterialTheme.typography.titleMedium)
        LayerChip(KnowledgeLayer.SOURCE)
        val body = excerpt?.body.orEmpty()
        if (body.isNotBlank()) {
            Text(body, style = MaterialTheme.typography.bodyMedium)
        }
        quotes.distinct().take(8).forEach { quote ->
            Text("「$quote」", style = MaterialTheme.typography.bodySmall)
        }
        if (body.isBlank() && quotes.isEmpty()) {
            Text("还没有摘录或划线。", style = MaterialTheme.typography.bodySmall)
        }
    }
}

@Composable
private fun SectionEditor(
    section: ProjectSectionEntity,
    layer: KnowledgeLayer,
    vm: ProjectViewModel,
) {
    var body by remember(section.id, section.revision) { mutableStateOf(section.body) }
    PaperCard(Modifier.fillMaxWidth()) {
        Text(section.title, style = MaterialTheme.typography.titleMedium)
        LayerChip(if (section.userLocked) KnowledgeLayer.USER else layer)
        QuietField(
            value = body,
            onValueChange = { body = it },
            modifier = Modifier.fillMaxWidth(),
            minLines = 3,
        )
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp), modifier = Modifier.fillMaxWidth()) {
            QuietButton("保存此段", { vm.saveSection(section.sectionId, body) }, Modifier.weight(1f), glyph = ZenGlyph.Brush, tone = QuietTone.Ink)
            QuietButton("再生成此段", { vm.regenerate(section.sectionId) }, Modifier.weight(1f), enabled = !section.userLocked, glyph = ZenGlyph.Chat)
        }
    }
}

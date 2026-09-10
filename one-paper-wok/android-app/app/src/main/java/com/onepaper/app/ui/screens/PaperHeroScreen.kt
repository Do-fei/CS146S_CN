package com.onepaper.app.ui.screens

import androidx.compose.foundation.horizontalScroll
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.fillMaxWidth
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
import androidx.compose.ui.unit.dp
import com.onepaper.app.ui.layout.LocalWindowFit
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.onepaper.app.data.local.ProjectSectionEntity
import com.onepaper.app.ui.components.Banner
import com.onepaper.app.ui.components.LayerChip
import com.onepaper.app.ui.components.PaperCard
import com.onepaper.app.ui.components.PaperScaffold
import com.onepaper.app.ui.components.QuietButton
import com.onepaper.app.ui.components.QuietField
import com.onepaper.app.ui.components.QuietTone
import com.onepaper.app.ui.graphics.ZenGlyph
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
    val notice by vm.notice.collectAsStateWithLifecycle()
    val wide = LocalWindowFit.current.wide
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
            Row(
                Modifier.fillMaxWidth().horizontalScroll(rememberScrollState()),
                horizontalArrangement = Arrangement.spacedBy(8.dp),
            ) {
                QuietButton("总览", { focus = "map" }, tone = if (focus == "map") QuietTone.Ink else QuietTone.Line)
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
            notice?.let { Banner(it) }
            QuietButton(
                "回煲",
                { vm.recook(emptyList()) },
                Modifier.fillMaxWidth(),
                glyph = ZenGlyph.Wok,
                tone = QuietTone.Ink,
            )
            if (proposalId != null) {
                QuietButton("查看建议", { onRecook(proposalId!!) }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Sheet)
            }
            QuietButton("导出", { onExport(vm.projectId) }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Share, tone = QuietTone.Ink)
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
            QuietButton("保存", { vm.saveSection(section.sectionId, body) }, Modifier.weight(1f), glyph = ZenGlyph.Brush, tone = QuietTone.Ink)
            QuietButton("重写", { vm.regenerate(section.sectionId) }, Modifier.weight(1f), enabled = !section.userLocked, glyph = ZenGlyph.Chat)
        }
    }
}

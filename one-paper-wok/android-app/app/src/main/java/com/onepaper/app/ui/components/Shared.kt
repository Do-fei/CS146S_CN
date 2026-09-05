package com.onepaper.app.ui.components

import androidx.compose.foundation.BorderStroke
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.ColumnScope
import androidx.compose.foundation.layout.IntrinsicSize
import androidx.compose.foundation.layout.PaddingValues
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.RowScope
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.defaultMinSize
import androidx.compose.foundation.layout.fillMaxHeight
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.WindowInsets
import androidx.compose.foundation.layout.navigationBarsPadding
import androidx.compose.foundation.layout.statusBarsPadding
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.layout.size
import androidx.compose.foundation.layout.width
import androidx.compose.foundation.shape.CircleShape
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.foundation.text.KeyboardOptions
import androidx.compose.material3.ExperimentalMaterial3Api
import androidx.compose.material3.IconButton
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.OutlinedTextField
import androidx.compose.material3.OutlinedTextFieldDefaults
import androidx.compose.material3.Scaffold
import androidx.compose.material3.ScaffoldDefaults
import androidx.compose.material3.Text
import androidx.compose.material3.TopAppBar
import androidx.compose.material3.TopAppBarDefaults
import androidx.compose.runtime.Composable
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.draw.clip
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.input.VisualTransformation
import androidx.compose.ui.unit.dp
import com.onepaper.app.ui.graphics.ZenGlyph
import com.onepaper.app.ui.graphics.ZenIcon
import com.onepaper.app.ui.graphics.ZenMark
import com.onepaper.app.ui.layout.LocalWindowFit
import com.onepaper.app.ui.theme.Seal
import com.onepaper.domain.model.KnowledgeLayer

private val PaperCorner = RoundedCornerShape(2.dp)

enum class QuietTone { Ink, Line, Ghost, Danger }

@Composable
fun QuietButton(
    text: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    enabled: Boolean = true,
    glyph: ZenGlyph? = null,
    tone: QuietTone = QuietTone.Line,
) {
    val scheme = MaterialTheme.colorScheme
    val shape = PaperCorner
    val colors = when (tone) {
        QuietTone.Ink -> scheme.onSurface.copy(alpha = if (enabled) 1f else 0.35f) to scheme.surface
        QuietTone.Line -> Color.Transparent to scheme.onSurface.copy(alpha = if (enabled) 0.92f else 0.35f)
        QuietTone.Ghost -> Color.Transparent to scheme.onSurfaceVariant.copy(alpha = if (enabled) 1f else 0.4f)
        QuietTone.Danger -> Color.Transparent to scheme.tertiary.copy(alpha = if (enabled) 1f else 0.4f)
    }
    val border = when (tone) {
        QuietTone.Ink -> BorderStroke(1.dp, scheme.onSurface.copy(alpha = if (enabled) 0.92f else 0.25f))
        QuietTone.Line -> BorderStroke(1.dp, scheme.outline.copy(alpha = if (enabled) 0.95f else 0.35f))
        QuietTone.Ghost, QuietTone.Danger -> null
    }
    val minH = if (LocalWindowFit.current.coverLike) 44.dp else 48.dp
    Row(
        modifier
            .defaultMinSize(minHeight = minH)
            .clip(shape)
            .then(if (border != null) Modifier.border(border, shape) else Modifier)
            .background(colors.first, shape)
            .clickable(enabled = enabled, onClick = onClick)
            .padding(horizontal = 16.dp, vertical = 10.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.Center,
    ) {
        if (glyph != null) {
            ZenIcon(glyph, tint = colors.second, size = 18.dp)
            Spacer(Modifier.width(8.dp))
        }
        Text(text, style = MaterialTheme.typography.labelLarge, color = colors.second)
    }
}

@Composable
fun QuietField(
    value: String,
    onValueChange: (String) -> Unit,
    modifier: Modifier = Modifier,
    label: String? = null,
    enabled: Boolean = true,
    minLines: Int = 1,
    visualTransformation: VisualTransformation = VisualTransformation.None,
    keyboardOptions: KeyboardOptions = KeyboardOptions.Default,
) {
    val scheme = MaterialTheme.colorScheme
    OutlinedTextField(
        value = value,
        onValueChange = onValueChange,
        modifier = modifier,
        enabled = enabled,
        minLines = minLines,
        label = label?.let { { Text(it) } },
        visualTransformation = visualTransformation,
        keyboardOptions = keyboardOptions,
        shape = PaperCorner,
        colors = OutlinedTextFieldDefaults.colors(
            focusedBorderColor = scheme.onSurface,
            unfocusedBorderColor = scheme.outline,
            disabledBorderColor = scheme.outline.copy(alpha = 0.4f),
            focusedLabelColor = scheme.onSurface,
            cursorColor = scheme.onSurface,
            focusedContainerColor = Color.Transparent,
            unfocusedContainerColor = Color.Transparent,
        ),
    )
}

@OptIn(ExperimentalMaterial3Api::class)
@Composable
fun QuietTopBar(
    title: String,
    onBack: (() -> Unit)? = null,
    actions: @Composable RowScope.() -> Unit = {},
) {
    val scheme = MaterialTheme.colorScheme
    TopAppBar(
        title = { Text(title, style = MaterialTheme.typography.titleLarge) },
        navigationIcon = {
            if (onBack != null) {
                IconButton(onClick = onBack) {
                    ZenIcon(ZenGlyph.Back, contentDescription = "返回", tint = scheme.onSurface)
                }
            }
        },
        actions = actions,
        colors = TopAppBarDefaults.topAppBarColors(
            containerColor = Color.Transparent,
            titleContentColor = scheme.onSurface,
            navigationIconContentColor = scheme.onSurface,
            actionIconContentColor = scheme.onSurface,
        ),
    )
}

@Composable
fun PaperScaffold(
    title: String? = null,
    onBack: (() -> Unit)? = null,
    actions: @Composable RowScope.() -> Unit = {},
    bottomBar: @Composable () -> Unit = {},
    contentWindowInsets: WindowInsets = ScaffoldDefaults.contentWindowInsets,
    content: @Composable (PaddingValues) -> Unit,
) {
    Scaffold(
        containerColor = MaterialTheme.colorScheme.background,
        contentColor = MaterialTheme.colorScheme.onBackground,
        contentWindowInsets = contentWindowInsets,
        topBar = { if (title != null) QuietTopBar(title, onBack, actions) },
        bottomBar = bottomBar,
        content = content,
    )
}

@Composable
fun QuietIconButton(
    glyph: ZenGlyph,
    contentDescription: String,
    onClick: () -> Unit,
) {
    IconButton(onClick = onClick) {
        ZenIcon(glyph, contentDescription = contentDescription)
    }
}

@Composable
fun QuietNavBar(selected: Int, onSelect: (Int) -> Unit) {
    val cover = LocalWindowFit.current.coverLike
    val items = listOf(
        Triple(ZenGlyph.Books, if (cover) "架" else "书架", 0),
        Triple(ZenGlyph.Sheet, if (cover) "纸" else "一纸", 1),
        Triple(ZenGlyph.Bowl, if (cover) "堂" else "食堂", 2),
        Triple(ZenGlyph.Seal, if (cover) "我" else "我的", 3),
    )
    val scheme = MaterialTheme.colorScheme
    Column(
        Modifier
            .background(scheme.background)
            .navigationBarsPadding(),
    ) {
        Hairline()
        Row(
            Modifier
                .fillMaxWidth()
                .height(if (cover) 52.dp else 64.dp),
            horizontalArrangement = Arrangement.SpaceEvenly,
        ) {
            items.forEach { (glyph, label, index) ->
                val on = selected == index
                Column(
                    Modifier
                        .weight(1f)
                        .fillMaxHeight()
                        .clickable { onSelect(index) },
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.Center,
                ) {
                    ZenIcon(
                        glyph,
                        tint = if (on) scheme.onSurface else scheme.onSurfaceVariant,
                        contentDescription = label,
                    )
                    Spacer(Modifier.height(4.dp))
                    Text(
                        label,
                        style = MaterialTheme.typography.labelSmall,
                        color = if (on) scheme.onSurface else scheme.onSurfaceVariant,
                    )
                    Spacer(Modifier.height(4.dp))
                    Box(
                        Modifier
                            .size(3.dp)
                            .clip(CircleShape)
                            .background(if (on) scheme.tertiary else Color.Transparent),
                    )
                }
            }
        }
    }
}

@Composable
fun PaperCard(
    modifier: Modifier = Modifier,
    onClick: (() -> Unit)? = null,
    content: @Composable ColumnScope.() -> Unit,
) {
    val scheme = MaterialTheme.colorScheme
    val shape = PaperCorner
    Column(
        modifier
            .clip(shape)
            .border(1.dp, scheme.outline.copy(alpha = 0.7f), shape)
            .background(scheme.surface, shape)
            .then(if (onClick != null) Modifier.clickable(onClick = onClick) else Modifier)
            .padding(16.dp),
        verticalArrangement = Arrangement.spacedBy(8.dp),
        content = content,
    )
}

@Composable
fun QuietNavRail(selected: Int, onSelect: (Int) -> Unit, modifier: Modifier = Modifier) {
    val items = listOf(
        Triple(ZenGlyph.Books, "书架", 0),
        Triple(ZenGlyph.Sheet, "一纸", 1),
        Triple(ZenGlyph.Bowl, "食堂", 2),
        Triple(ZenGlyph.Seal, "我的", 3),
    )
    val scheme = MaterialTheme.colorScheme
    Row(
        modifier
            .fillMaxHeight()
            .statusBarsPadding()
            .navigationBarsPadding(),
    ) {
        Column(
            Modifier
                .width(88.dp)
                .fillMaxHeight()
                .background(scheme.background)
                .padding(vertical = 16.dp),
            verticalArrangement = Arrangement.spacedBy(8.dp),
            horizontalAlignment = Alignment.CenterHorizontally,
        ) {
            items.forEach { (glyph, label, index) ->
                val on = selected == index
                Column(
                    Modifier
                        .fillMaxWidth()
                        .clip(PaperCorner)
                        .clickable { onSelect(index) }
                        .padding(vertical = 12.dp),
                    horizontalAlignment = Alignment.CenterHorizontally,
                    verticalArrangement = Arrangement.spacedBy(6.dp),
                ) {
                    ZenIcon(
                        glyph,
                        tint = if (on) scheme.onSurface else scheme.onSurfaceVariant,
                        contentDescription = label,
                    )
                    Text(
                        label,
                        style = MaterialTheme.typography.labelSmall,
                        color = if (on) scheme.onSurface else scheme.onSurfaceVariant,
                    )
                    Box(
                        Modifier
                            .size(3.dp)
                            .clip(CircleShape)
                            .background(if (on) scheme.tertiary else Color.Transparent),
                    )
                }
            }
        }
        Box(
            Modifier
                .width(1.dp)
                .fillMaxHeight()
                .background(scheme.outline.copy(alpha = 0.55f)),
        )
    }
}

@Composable
fun BookSpineCard(
    title: String,
    subtitle: String,
    onClick: () -> Unit,
    modifier: Modifier = Modifier,
    layer: KnowledgeLayer = KnowledgeLayer.SOURCE,
    progressLabel: String? = null,
    progressPercent: Int = 0,
    cover: androidx.compose.ui.graphics.ImageBitmap? = null,
    onContinue: (() -> Unit)? = null,
) {
    val scheme = MaterialTheme.colorScheme
    val spine = spineInk(title)
    val fit = LocalWindowFit.current
    Row(
        modifier
            .fillMaxWidth()
            .clip(PaperCorner)
            .border(1.dp, scheme.outline.copy(alpha = 0.7f), PaperCorner)
            .clickable(onClick = onClick)
            .padding(end = 14.dp),
        verticalAlignment = Alignment.CenterVertically,
    ) {
        if (cover != null) {
            androidx.compose.foundation.Image(
                cover,
                contentDescription = "封面",
                modifier = Modifier
                    .width(fit.coverW)
                    .height(fit.coverH)
                    .background(scheme.surfaceVariant),
            )
        } else {
            Box(
                Modifier
                    .width(3.dp)
                    .height(fit.coverH)
                    .background(spine),
            )
        }
        Column(
            Modifier
                .weight(1f)
                .padding(horizontal = if (fit.coverLike) 10.dp else 14.dp, vertical = if (fit.coverLike) 8.dp else 14.dp),
            verticalArrangement = Arrangement.spacedBy(6.dp),
        ) {
            Text(title, style = MaterialTheme.typography.titleMedium)
            if (subtitle.isNotBlank()) {
                Text(subtitle, style = MaterialTheme.typography.bodySmall, color = scheme.onSurfaceVariant)
            }
            if (!progressLabel.isNullOrBlank()) {
                Text(progressLabel, style = MaterialTheme.typography.labelSmall, color = scheme.onSurfaceVariant)
            }
            QuietProgress(progressPercent / 100f)
            LayerChip(layer)
            if (onContinue != null) {
                Text(
                    "继续",
                    style = MaterialTheme.typography.labelLarge,
                    color = scheme.onSurface,
                    modifier = Modifier.clickable(onClick = onContinue),
                )
            }
        }
    }
}

@Composable
private fun spineInk(title: String): Color {
    val tones = listOf(
        Color(0xFF8A7560),
        Color(0xFF6B705C),
        Color(0xFF7A5C58),
        Color(0xFF5C6B73),
        Color(0xFF7A6A4E),
    )
    val index = (title.hashCode().toLong() and 0x7fff_ffff) % tones.size
    return tones[index.toInt()]
}

@Composable
fun LayerChip(layer: KnowledgeLayer, modifier: Modifier = Modifier) {
    val (label, color) = when (layer) {
        KnowledgeLayer.SOURCE -> "原书" to Color(0xFF5B6B4E)
        KnowledgeLayer.AI -> "AI" to Color(0xFF6A5B8A)
        KnowledgeLayer.USER -> "我的" to Seal
    }
    Row(
        modifier
            .border(1.dp, color.copy(alpha = 0.45f), PaperCorner)
            .padding(horizontal = 8.dp, vertical = 4.dp),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(6.dp),
    ) {
        Box(
            Modifier
                .size(6.dp)
                .clip(CircleShape)
                .background(color),
        )
        Text(label, style = MaterialTheme.typography.labelSmall, color = color)
    }
}

@Composable
fun EmptyState(
    title: String,
    body: String,
    modifier: Modifier = Modifier,
    glyph: ZenGlyph = ZenGlyph.Enso,
) {
    Column(
        modifier.padding(horizontal = 24.dp, vertical = 36.dp),
        horizontalAlignment = Alignment.CenterHorizontally,
        verticalArrangement = Arrangement.spacedBy(12.dp),
    ) {
        ZenMark(glyph, tint = MaterialTheme.colorScheme.outline.copy(alpha = 0.7f))
        Text(title, style = MaterialTheme.typography.titleLarge)
        Text(
            body,
            style = MaterialTheme.typography.bodyMedium,
            color = MaterialTheme.colorScheme.onSurfaceVariant,
        )
    }
}

@Composable
fun Banner(text: String, modifier: Modifier = Modifier) {
    Row(
        modifier
            .fillMaxWidth()
            .height(IntrinsicSize.Min)
            .border(1.dp, MaterialTheme.colorScheme.outline.copy(alpha = 0.55f), PaperCorner)
            .background(MaterialTheme.colorScheme.surfaceVariant),
    ) {
        Box(
            Modifier
                .width(2.dp)
                .fillMaxHeight()
                .background(MaterialTheme.colorScheme.tertiary.copy(alpha = 0.85f)),
        )
        Text(
            text,
            modifier = Modifier.padding(horizontal = 12.dp, vertical = 10.dp),
            style = MaterialTheme.typography.bodyMedium,
        )
    }
}

@Composable
fun Kicker(text: String, modifier: Modifier = Modifier) {
    Text(
        text,
        modifier = modifier,
        style = MaterialTheme.typography.labelSmall,
        color = MaterialTheme.colorScheme.onSurfaceVariant,
    )
}

@Composable
fun SectionTitle(text: String, modifier: Modifier = Modifier, glyph: ZenGlyph? = null) {
    Row(
        modifier.fillMaxWidth(),
        verticalAlignment = Alignment.CenterVertically,
        horizontalArrangement = Arrangement.spacedBy(8.dp),
    ) {
        if (glyph != null) {
            ZenIcon(glyph, tint = MaterialTheme.colorScheme.onSurfaceVariant, size = 18.dp)
        }
        Text(text, style = MaterialTheme.typography.titleLarge)
        Spacer(Modifier.weight(1f))
        Hairline(Modifier.weight(1.4f))
    }
}

@Composable
fun Hairline(modifier: Modifier = Modifier) {
    Box(
        modifier
            .fillMaxWidth()
            .height(1.dp)
            .background(MaterialTheme.colorScheme.outline.copy(alpha = 0.55f)),
    )
}

@Composable
fun QuietProgress(progress: Float, modifier: Modifier = Modifier) {
    LinearProgressIndicator(
        progress = { progress.coerceIn(0f, 1f) },
        modifier = modifier
            .fillMaxWidth()
            .height(2.dp),
        color = MaterialTheme.colorScheme.onSurface,
        trackColor = MaterialTheme.colorScheme.outlineVariant,
        gapSize = 0.dp,
        drawStopIndicator = {},
    )
}

@Composable
fun StatCell(label: String, value: String, modifier: Modifier = Modifier) {
    Column(
        modifier.padding(vertical = 4.dp),
        verticalArrangement = Arrangement.spacedBy(4.dp),
    ) {
        Text(value, style = MaterialTheme.typography.headlineSmall)
        Text(label, style = MaterialTheme.typography.labelSmall, color = MaterialTheme.colorScheme.onSurfaceVariant)
    }
}

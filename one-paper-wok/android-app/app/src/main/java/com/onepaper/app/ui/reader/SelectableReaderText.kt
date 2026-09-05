package com.onepaper.app.ui.reader

import android.text.SpannableString
import android.text.Spanned
import android.text.method.ArrowKeyMovementMethod
import android.text.style.BackgroundColorSpan
import android.view.ActionMode
import android.view.Menu
import android.view.MenuItem
import android.widget.TextView
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.rememberUpdatedState
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.viewinterop.AndroidView

/**
 * 划选走系统 TextView ActionMode。Compose SelectionContainer 拿不到选区文本。
 */
@Composable
fun SelectableReaderText(
    text: String,
    fontSp: Float,
    modifier: Modifier = Modifier,
    highlight: String? = null,
    onNote: (String) -> Unit,
    onAsk: (String) -> Unit,
) {
    val scheme = MaterialTheme.colorScheme
    val textColor = scheme.onSurface.toArgb()
    val highlightColor = scheme.tertiary.copy(alpha = 0.28f).toArgb()
    val noteHandler = rememberUpdatedState(onNote)
    val askHandler = rememberUpdatedState(onAsk)
    AndroidView(
        factory = { context ->
            TextView(context).apply {
                setTextIsSelectable(true)
                movementMethod = ArrowKeyMovementMethod.getInstance()
                setTextColor(textColor)
                customSelectionActionModeCallback = object : ActionMode.Callback {
                    override fun onCreateActionMode(mode: ActionMode, menu: Menu): Boolean {
                        menu.clear()
                        menu.add(0, MENU_NOTE, 0, "记笔记")
                        menu.add(0, MENU_ASK, 1, "问搭子")
                        return true
                    }

                    override fun onPrepareActionMode(mode: ActionMode, menu: Menu): Boolean = false

                    override fun onActionItemClicked(mode: ActionMode, item: MenuItem): Boolean {
                        val start = selectionStart.coerceAtLeast(0)
                        val end = selectionEnd.coerceAtLeast(start)
                        val selected = text.substring(start, end).trim()
                        if (selected.isBlank()) return false
                        when (item.itemId) {
                            MENU_NOTE -> noteHandler.value(selected)
                            MENU_ASK -> askHandler.value(selected)
                            else -> return false
                        }
                        mode.finish()
                        return true
                    }

                    override fun onDestroyActionMode(mode: ActionMode) = Unit
                }
            }
        },
        update = { view ->
            view.textSize = fontSp
            view.setLineSpacing(0f, 1.7f)
            view.setTextColor(textColor)
            val rendered = highlighted(text, highlight, highlightColor)
            val stamp = "${text.hashCode()}|${highlight.orEmpty()}"
            if (view.tag != stamp) {
                view.text = rendered
                view.tag = stamp
            }
        },
        modifier = modifier.fillMaxWidth(),
    )
}

private fun highlighted(text: String, highlight: String?, color: Int): CharSequence {
    if (highlight.isNullOrBlank()) return text
    val start = text.indexOf(highlight)
    if (start < 0) return text
    return SpannableString(text).apply {
        setSpan(
            BackgroundColorSpan(color),
            start,
            start + highlight.length,
            Spanned.SPAN_EXCLUSIVE_EXCLUSIVE,
        )
    }
}

private const val MENU_NOTE = 1
private const val MENU_ASK = 2

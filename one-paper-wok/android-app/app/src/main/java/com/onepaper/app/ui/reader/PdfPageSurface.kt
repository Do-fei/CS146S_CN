package com.onepaper.app.ui.reader

import androidx.compose.foundation.Image
import androidx.compose.foundation.background
import androidx.compose.foundation.border
import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.BoxWithConstraints
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.offset
import androidx.compose.foundation.layout.size
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.layout.ContentScale
import androidx.compose.ui.unit.dp
import com.onepaper.domain.ocr.OcrBox

@Composable
fun OcrOverlayPage(
    bitmap: android.graphics.Bitmap,
    boxes: List<OcrBox>,
    onPick: (String) -> Unit,
    modifier: Modifier = Modifier,
) {
    val scheme = MaterialTheme.colorScheme
    BoxWithConstraints(modifier.fillMaxWidth().height(420.dp)) {
        Image(
            bitmap.asImageBitmap(),
            contentDescription = "固定版式页",
            modifier = Modifier.fillMaxWidth().height(420.dp),
            contentScale = ContentScale.Fit,
        )
        val srcAspect = bitmap.width.toFloat().coerceAtLeast(1f) / bitmap.height.coerceAtLeast(1)
        val dstAspect = maxWidth / maxHeight
        val drawnWidth = if (srcAspect > dstAspect) maxWidth else maxHeight * srcAspect
        val drawnHeight = if (srcAspect > dstAspect) maxWidth / srcAspect else maxHeight
        val originX = (maxWidth - drawnWidth) / 2
        val originY = (maxHeight - drawnHeight) / 2
        boxes.filter { it.points.size >= 2 && it.text.isNotBlank() }.forEach { box ->
            val xs = box.points.map { it.x }
            val ys = box.points.map { it.y }
            val left = (xs.minOrNull() ?: 0.0).toFloat()
            val top = (ys.minOrNull() ?: 0.0).toFloat()
            val right = (xs.maxOrNull() ?: 1.0).toFloat()
            val bottom = (ys.maxOrNull() ?: 1.0).toFloat()
            Box(
                Modifier
                    .offset(
                        x = originX + drawnWidth * left,
                        y = originY + drawnHeight * top,
                    )
                    .size(
                        width = drawnWidth * (right - left).coerceAtLeast(0.04f),
                        height = drawnHeight * (bottom - top).coerceAtLeast(0.03f),
                    )
                    .background(scheme.tertiary.copy(alpha = 0.18f))
                    .border(1.dp, scheme.tertiary.copy(alpha = 0.7f))
                    .clickable { onPick(box.text) },
            )
        }
    }
}

@Composable
fun LayerCaption(text: String, modifier: Modifier = Modifier) {
    Text(
        text,
        modifier = modifier,
        style = MaterialTheme.typography.bodySmall,
        color = Color(0xFF5B6B4E),
    )
}

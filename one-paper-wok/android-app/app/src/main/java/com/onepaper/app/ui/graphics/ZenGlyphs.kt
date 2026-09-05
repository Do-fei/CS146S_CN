package com.onepaper.app.ui.graphics

import androidx.compose.foundation.Canvas
import androidx.compose.foundation.layout.size
import androidx.compose.material3.MaterialTheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.Modifier
import androidx.compose.ui.geometry.Offset
import androidx.compose.ui.geometry.Rect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.Path
import androidx.compose.ui.graphics.StrokeCap
import androidx.compose.ui.graphics.StrokeJoin
import androidx.compose.ui.graphics.drawscope.DrawScope
import androidx.compose.ui.graphics.drawscope.Stroke
import androidx.compose.ui.semantics.contentDescription
import androidx.compose.ui.semantics.semantics
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp

/** 细线功能图形。每笔对应一个动作或层，不作装饰插画。 */
enum class ZenGlyph {
    Enso,
    Books,
    Book,
    Sheet,
    Bowl,
    Seal,
    Plus,
    Camera,
    Search,
    Back,
    Flame,
    Wok,
    Brush,
    Chat,
    Share,
    Stack,
    Sliders,
    Scan,
    Note,
    Import,
    ChevronLeft,
    ChevronRight,
}

@Composable
fun ZenIcon(
    glyph: ZenGlyph,
    modifier: Modifier = Modifier,
    tint: Color = MaterialTheme.colorScheme.onSurface,
    size: Dp = 22.dp,
    contentDescription: String? = null,
) {
    val semantics = if (contentDescription != null) {
        Modifier.semantics { this.contentDescription = contentDescription }
    } else {
        Modifier
    }
    Canvas(modifier.size(size).then(semantics)) {
        val stroke = Stroke(
            width = (this.size.minDimension * 0.068f).coerceAtLeast(1.4f),
            cap = StrokeCap.Round,
            join = StrokeJoin.Round,
        )
        drawZenGlyph(glyph, tint, stroke)
    }
}

@Composable
fun ZenMark(
    glyph: ZenGlyph,
    modifier: Modifier = Modifier.size(112.dp),
    tint: Color = MaterialTheme.colorScheme.outline,
) {
    Canvas(modifier) {
        val stroke = Stroke(
            width = (this.size.minDimension * 0.026f).coerceIn(1.3f, 3.4f),
            cap = StrokeCap.Round,
            join = StrokeJoin.Round,
        )
        drawZenGlyph(glyph, tint, stroke)
    }
}

internal fun DrawScope.drawZenGlyph(glyph: ZenGlyph, color: Color, stroke: Stroke) {
    val pad = size.minDimension * 0.10f
    val box = size.minDimension - pad * 2
    val ox = (size.width - box) / 2f
    val oy = (size.height - box) / 2f
    fun x(v: Float) = ox + v / 24f * box
    fun y(v: Float) = oy + v / 24f * box
    fun p(px: Float, py: Float) = Offset(x(px), y(py))
    fun line(x1: Float, y1: Float, x2: Float, y2: Float) {
        drawLine(color, p(x1, y1), p(x2, y2), strokeWidth = stroke.width, cap = StrokeCap.Round)
    }
    fun path(build: Path.() -> Unit) {
        drawPath(Path().apply(build), color, style = stroke)
    }

    when (glyph) {
        ZenGlyph.Enso -> path {
            arcTo(Rect(x(2.2f), y(2.4f), x(21.6f), y(21.8f)), -28f, 302f, true)
        }
        ZenGlyph.Books -> {
            path {
                moveTo(x(5f), y(7f)); lineTo(x(19f), y(7f)); lineTo(x(19f), y(11f)); lineTo(x(5f), y(11f)); close()
            }
            path {
                moveTo(x(4.4f), y(12.2f)); lineTo(x(18.4f), y(12.2f)); lineTo(x(18.4f), y(16.2f)); lineTo(x(4.4f), y(16.2f)); close()
            }
            path {
                moveTo(x(5.6f), y(17.4f)); lineTo(x(19.6f), y(17.4f)); lineTo(x(19.6f), y(21.2f)); lineTo(x(5.6f), y(21.2f)); close()
            }
        }
        ZenGlyph.Book -> {
            line(12f, 4.2f, 12f, 19.6f)
            path {
                moveTo(x(12f), y(4.2f)); lineTo(x(4.2f), y(6.2f)); lineTo(x(4.2f), y(19.8f)); lineTo(x(12f), y(18f))
            }
            path {
                moveTo(x(12f), y(4.2f)); lineTo(x(19.8f), y(6.2f)); lineTo(x(19.8f), y(19.8f)); lineTo(x(12f), y(18f))
            }
        }
        ZenGlyph.Sheet -> {
            path {
                moveTo(x(7f), y(3.6f))
                lineTo(x(14.6f), y(3.6f))
                lineTo(x(18.4f), y(7.4f))
                lineTo(x(18.4f), y(20.4f))
                lineTo(x(7f), y(20.4f))
                close()
            }
            path {
                moveTo(x(14.6f), y(3.6f)); lineTo(x(14.6f), y(7.4f)); lineTo(x(18.4f), y(7.4f))
            }
        }
        ZenGlyph.Bowl -> {
            path {
                arcTo(Rect(x(4f), y(8.5f), x(20f), y(21.2f)), 8f, 164f, true)
            }
            line(4.6f, 11.4f, 19.4f, 11.4f)
            path {
                moveTo(x(9.2f), y(6.2f)); quadraticTo(x(10.2f), y(4.4f), x(11.4f), y(6.4f))
            }
            path {
                moveTo(x(12.6f), y(5.6f)); quadraticTo(x(13.6f), y(3.8f), x(14.8f), y(5.8f))
            }
        }
        ZenGlyph.Seal -> {
            path {
                moveTo(x(7.2f), y(7.2f)); lineTo(x(16.8f), y(7.2f)); lineTo(x(16.8f), y(16.8f)); lineTo(x(7.2f), y(16.8f)); close()
            }
            line(9.4f, 10.2f, 14.6f, 10.2f)
            line(9.4f, 13.6f, 13.2f, 13.6f)
        }
        ZenGlyph.Plus -> {
            path {
                moveTo(x(5f), y(5f)); lineTo(x(19f), y(5f)); lineTo(x(19f), y(19f)); lineTo(x(5f), y(19f)); close()
            }
            line(12f, 8.2f, 12f, 15.8f)
            line(8.2f, 12f, 15.8f, 12f)
        }
        ZenGlyph.Camera -> {
            path {
                moveTo(x(4.2f), y(8.2f)); lineTo(x(19.8f), y(8.2f)); lineTo(x(19.8f), y(19.2f)); lineTo(x(4.2f), y(19.2f)); close()
            }
            path {
                addOval(Rect(x(9.1f), y(11.1f), x(14.9f), y(16.9f)))
            }
            line(8.4f, 8.2f, 9.8f, 5.8f)
            line(9.8f, 5.8f, 14.2f, 5.8f)
            line(14.2f, 5.8f, 15.6f, 8.2f)
        }
        ZenGlyph.Search -> {
            path { addOval(Rect(x(5.2f), y(5.2f), x(15.6f), y(15.6f))) }
            line(14.8f, 14.8f, 19.4f, 19.4f)
        }
        ZenGlyph.Back -> {
            line(13.6f, 5.6f, 7.2f, 12f)
            line(7.2f, 12f, 13.6f, 18.4f)
        }
        ZenGlyph.Flame -> {
            path {
                moveTo(x(8.2f), y(19.2f))
                quadraticTo(x(8.8f), y(13.2f), x(11.8f), y(10.2f))
                quadraticTo(x(10.6f), y(14.4f), x(12.2f), y(19.2f))
            }
            path {
                moveTo(x(12.4f), y(19.2f))
                quadraticTo(x(13.6f), y(12.6f), x(16.2f), y(9.6f))
                quadraticTo(x(15.2f), y(14.8f), x(15.8f), y(19.2f))
            }
            path {
                moveTo(x(10.6f), y(19.2f))
                quadraticTo(x(11.4f), y(15.6f), x(12.8f), y(13.8f))
            }
        }
        ZenGlyph.Wok -> {
            line(5.2f, 11.2f, 18.8f, 11.2f)
            path {
                arcTo(Rect(x(5.2f), y(9.4f), x(18.8f), y(18.8f)), 12f, 156f, true)
            }
            line(18.6f, 10.4f, 20.6f, 8.2f)
            path {
                moveTo(x(9.2f), y(20.4f)); quadraticTo(x(10.4f), y(18.2f), x(11.6f), y(20.4f))
            }
            path {
                moveTo(x(12.2f), y(20.6f)); quadraticTo(x(13.2f), y(18.0f), x(14.6f), y(20.4f))
            }
        }
        ZenGlyph.Brush -> {
            line(6.2f, 17.8f, 16.4f, 6.4f)
            path {
                moveTo(x(16.4f), y(6.4f)); lineTo(x(18.6f), y(5.2f)); lineTo(x(17.6f), y(7.8f)); close()
            }
            line(5.4f, 19.2f, 8.2f, 16.6f)
        }
        ZenGlyph.Chat -> {
            path {
                arcTo(Rect(x(3.6f), y(5.2f), x(14.4f), y(16.0f)), -20f, 250f, true)
            }
            path {
                arcTo(Rect(x(10.0f), y(8.4f), x(20.6f), y(19.2f)), 40f, 250f, true)
            }
        }
        ZenGlyph.Share -> {
            path {
                moveTo(x(5.4f), y(7.2f)); lineTo(x(14.2f), y(7.2f)); lineTo(x(14.2f), y(18.6f)); lineTo(x(5.4f), y(18.6f)); close()
            }
            path {
                moveTo(x(9.8f), y(5.0f)); lineTo(x(18.6f), y(5.0f)); lineTo(x(18.6f), y(16.2f)); lineTo(x(14.2f), y(16.2f))
            }
        }
        ZenGlyph.Stack -> {
            line(7f, 6.2f, 17f, 6.2f)
            line(6f, 9.0f, 18f, 9.0f)
            path {
                moveTo(x(5.2f), y(12f)); lineTo(x(18.8f), y(12f)); lineTo(x(18.8f), y(20.4f)); lineTo(x(5.2f), y(20.4f)); close()
            }
        }
        ZenGlyph.Sliders -> {
            line(4.8f, 8f, 19.2f, 8f)
            line(4.8f, 12f, 14.6f, 12f)
            line(4.8f, 16f, 17.4f, 16f)
        }
        ZenGlyph.Scan -> {
            path {
                moveTo(x(6.4f), y(4.4f)); lineTo(x(17.6f), y(4.4f)); lineTo(x(17.6f), y(19.6f)); lineTo(x(6.4f), y(19.6f)); close()
            }
            line(6.4f, 12f, 17.6f, 12f)
            line(8.6f, 8.2f, 13.4f, 8.2f)
        }
        ZenGlyph.Note -> {
            path {
                moveTo(x(6.6f), y(4.2f)); lineTo(x(16.2f), y(4.2f)); lineTo(x(16.2f), y(19.8f)); lineTo(x(6.6f), y(19.8f)); close()
            }
            line(8.6f, 8.4f, 14.0f, 8.4f)
            line(8.6f, 12.0f, 13.0f, 12.0f)
            path {
                moveTo(x(14.8f), y(15.6f)); lineTo(x(18.6f), y(18.8f))
            }
        }
        ZenGlyph.Import -> {
            line(12f, 4.4f, 12f, 13.2f)
            line(12f, 13.2f, 8.8f, 10.0f)
            line(12f, 13.2f, 15.2f, 10.0f)
            path {
                arcTo(Rect(x(4.4f), y(11.2f), x(19.6f), y(21.4f)), 12f, 156f, true)
            }
            line(4.8f, 13.8f, 19.2f, 13.8f)
        }
        ZenGlyph.ChevronLeft -> {
            line(14.2f, 6.2f, 8.6f, 12f)
            line(8.6f, 12f, 14.2f, 17.8f)
        }
        ZenGlyph.ChevronRight -> {
            line(9.8f, 6.2f, 15.4f, 12f)
            line(15.4f, 12f, 9.8f, 17.8f)
        }
    }
}

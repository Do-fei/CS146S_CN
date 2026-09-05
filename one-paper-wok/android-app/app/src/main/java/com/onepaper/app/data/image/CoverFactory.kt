package com.onepaper.app.data.image

import android.graphics.Bitmap
import android.graphics.Canvas
import android.graphics.Paint
import android.graphics.Rect
import android.graphics.Typeface
import com.onepaper.app.data.files.PrivateStore
import com.onepaper.app.data.importing.PdfPages
import java.io.File
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class CoverFactory @Inject constructor(
    private val store: PrivateStore,
) {
    fun writeJpeg(editionId: String, bitmap: Bitmap): String {
        val file = File(store.editionDir(editionId), "cover.jpg")
        file.outputStream().use { bitmap.compress(Bitmap.CompressFormat.JPEG, 86, it) }
        return store.relative(file)
    }

    fun writeBytes(editionId: String, bytes: ByteArray): String? {
        val decoded = android.graphics.BitmapFactory.decodeByteArray(bytes, 0, bytes.size) ?: return null
        val scaled = scale(decoded, 360)
        return writeJpeg(editionId, scaled)
    }

    fun fromPdf(editionId: String, pdf: File): String? {
        val page = PdfPages.renderBitmap(pdf, 0, maxWidth = 360) ?: return null
        return writeJpeg(editionId, page)
    }

    fun fromTitle(editionId: String, title: String, author: String): String {
        val bitmap = Bitmap.createBitmap(240, 360, Bitmap.Config.ARGB_8888)
        val canvas = Canvas(bitmap)
        canvas.drawColor(0xFFF7F3EA.toInt())
        val ink = Paint(Paint.ANTI_ALIAS_FLAG).apply {
            color = 0xFF302D29.toInt()
            textSize = 28f
            typeface = Typeface.create(Typeface.SERIF, Typeface.NORMAL)
        }
        val muted = Paint(ink).apply {
            color = 0xFF6B645A.toInt()
            textSize = 18f
        }
        val line = Paint().apply { color = 0xFF8A7560.toInt(); strokeWidth = 6f }
        canvas.drawRect(0f, 0f, 8f, 360f, line)
        drawWrapped(canvas, title.ifBlank { "一纸" }, ink, Rect(24, 48, 216, 240))
        if (author.isNotBlank()) {
            canvas.drawText(author.take(16), 24f, 300f, muted)
        }
        return writeJpeg(editionId, bitmap)
    }

    private fun scale(src: Bitmap, maxEdge: Int): Bitmap {
        val longest = maxOf(src.width, src.height).coerceAtLeast(1)
        if (longest <= maxEdge) return src
        val ratio = maxEdge.toFloat() / longest
        return Bitmap.createScaledBitmap(
            src,
            (src.width * ratio).toInt().coerceAtLeast(1),
            (src.height * ratio).toInt().coerceAtLeast(1),
            true,
        )
    }

    private fun drawWrapped(canvas: Canvas, text: String, paint: Paint, box: Rect) {
        val words = text.toList().map { it.toString() }
        var line = ""
        var y = box.top.toFloat() + paint.textSize
        for (ch in words) {
            val probe = line + ch
            if (paint.measureText(probe) > box.width() && line.isNotBlank()) {
                canvas.drawText(line, box.left.toFloat(), y, paint)
                line = ch
                y += paint.textSize * 1.35f
                if (y > box.bottom) return
            } else {
                line = probe
            }
        }
        if (line.isNotBlank() && y <= box.bottom) {
            canvas.drawText(line, box.left.toFloat(), y, paint)
        }
    }
}

package com.onepaper.app.data.importing

import android.graphics.Bitmap
import android.graphics.pdf.PdfRenderer
import android.os.ParcelFileDescriptor
import java.io.ByteArrayOutputStream
import java.io.File

object PdfPages {
    fun count(file: File): Int = withRenderer(file) { it.pageCount } ?: 0

    fun renderBitmap(file: File, pageIndex: Int, maxWidth: Int = 1200): Bitmap? {
        return withRenderer(file) { renderer ->
            if (pageIndex !in 0 until renderer.pageCount) return@withRenderer null
            renderer.openPage(pageIndex).use { page ->
                val scale = (maxWidth.toFloat() / page.width.coerceAtLeast(1)).coerceAtMost(2.5f)
                val width = (page.width * scale).toInt().coerceAtLeast(1)
                val height = (page.height * scale).toInt().coerceAtLeast(1)
                val bitmap = Bitmap.createBitmap(width, height, Bitmap.Config.ARGB_8888)
                page.render(bitmap, null, null, PdfRenderer.Page.RENDER_MODE_FOR_DISPLAY)
                bitmap
            }
        }
    }

    fun pngBytes(file: File, pageIndex: Int): ByteArray? {
        val bitmap = renderBitmap(file, pageIndex) ?: return null
        return ByteArrayOutputStream().use { out ->
            bitmap.compress(Bitmap.CompressFormat.PNG, 100, out)
            bitmap.recycle()
            out.toByteArray()
        }
    }

    private fun <T> withRenderer(file: File, block: (PdfRenderer) -> T): T? {
        if (!file.exists()) return null
        return runCatching {
            ParcelFileDescriptor.open(file, ParcelFileDescriptor.MODE_READ_ONLY).use { pfd ->
                PdfRenderer(pfd).use(block)
            }
        }.getOrNull()
    }
}

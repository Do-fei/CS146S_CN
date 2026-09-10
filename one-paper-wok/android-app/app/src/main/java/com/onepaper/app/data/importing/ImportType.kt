package com.onepaper.app.data.importing

import android.content.ContentResolver
import android.content.Context
import android.net.Uri
import android.provider.OpenableColumns
import com.onepaper.domain.model.SourceKind
import java.io.File

data class IncomingFile(
    val displayName: String,
    val kind: SourceKind,
    val mime: String?,
)

object ImportType {
    fun resolve(context: Context, uri: Uri, fallbackName: String): IncomingFile {
        val queried = queryDisplayName(context, uri)
        val mime = context.contentResolver.getType(uri)
        val magic = peekKind(context, uri)
        val nameHint = (queried ?: fallbackName).substringAfterLast('/')
        val extKind = kindFromName(nameHint) ?: kindFromMime(mime)
        val kind = magic ?: extKind ?: SourceKind.PLAIN_TEXT
        val name = ensureExtension(nameHint.ifBlank { "source" }, kind)
        return IncomingFile(displayName = name, kind = kind, mime = mime)
    }

    fun kindFromName(name: String): SourceKind? {
        val lower = name.lowercase()
        return when {
            lower.endsWith(".epub") -> SourceKind.EPUB
            lower.endsWith(".pdf") -> SourceKind.PDF
            lower.endsWith(".txt") || lower.endsWith(".md") -> SourceKind.PLAIN_TEXT
            lower.endsWith(".png") || lower.endsWith(".jpg") || lower.endsWith(".jpeg") || lower.endsWith(".webp") ->
                SourceKind.IMAGES
            else -> null
        }
    }

    fun kindFromMime(mime: String?): SourceKind? = when (mime) {
        "application/epub+zip", "application/epub" -> SourceKind.EPUB
        "application/pdf" -> SourceKind.PDF
        "text/plain", "text/markdown" -> SourceKind.PLAIN_TEXT
        "image/png", "image/jpeg", "image/webp", "image/jpg" -> SourceKind.IMAGES
        else -> null
    }

    private fun peekKind(context: Context, uri: Uri): SourceKind? {
        return runCatching {
            context.contentResolver.openInputStream(uri)?.use { input ->
                val buf = ByteArray(8)
                val n = input.read(buf)
                if (n <= 0) return@use null
                val head = buf.copyOf(n)
                when {
                    head.size >= 4 && head[0] == 0x25.toByte() && head[1] == 0x50.toByte() &&
                        head[2] == 0x44.toByte() && head[3] == 0x46.toByte() -> SourceKind.PDF
                    head.size >= 4 && head[0] == 0x50.toByte() && head[1] == 0x4B.toByte() -> {
                        // zip: epub or other; sniff later on file
                        null
                    }
                    head.size >= 3 && head[0] == 0xFF.toByte() && head[1] == 0xD8.toByte() -> SourceKind.IMAGES
                    head.size >= 8 && head.copyOfRange(0, 8).contentEquals(
                        byteArrayOf(0x89.toByte(), 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A),
                    ) -> SourceKind.IMAGES
                    else -> null
                }
            }
        }.getOrNull()
    }

    fun sniffZipIsEpub(file: File): Boolean {
        return runCatching {
            java.util.zip.ZipFile(file).use { zip ->
                zip.getEntry("mimetype") != null ||
                    zip.entries().toList().any { it.name.contains("META-INF/container.xml") }
            }
        }.getOrDefault(false)
    }

    private fun queryDisplayName(context: Context, uri: Uri): String? {
        if (uri.scheme != ContentResolver.SCHEME_CONTENT) return uri.lastPathSegment
        return context.contentResolver.query(uri, arrayOf(OpenableColumns.DISPLAY_NAME), null, null, null)?.use { c ->
            if (!c.moveToFirst()) return@use null
            val idx = c.getColumnIndex(OpenableColumns.DISPLAY_NAME)
            if (idx < 0) null else c.getString(idx)
        }
    }

    private fun ensureExtension(name: String, kind: SourceKind): String {
        if (kindFromName(name) != null) return name
        val ext = when (kind) {
            SourceKind.EPUB -> ".epub"
            SourceKind.PDF -> ".pdf"
            SourceKind.PLAIN_TEXT -> ".txt"
            SourceKind.IMAGES -> ".jpg"
        }
        return name + ext
    }
}

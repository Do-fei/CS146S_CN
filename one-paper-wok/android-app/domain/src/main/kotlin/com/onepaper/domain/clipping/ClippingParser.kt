package com.onepaper.domain.clipping

/** 用户自己导出的书摘。不登录、不爬微信读书 / Kindle 云。 */
data class Clipping(
    val bookTitle: String,
    val author: String,
    val quote: String,
    val note: String = "",
    val source: ClippingSource,
)

enum class ClippingSource {
    KINDLE,
    WEIXIN_EXPORT,
    GENERIC,
}

object ClippingParser {
    fun parse(raw: String): List<Clipping> {
        val text = raw.replace("\r\n", "\n").trim()
        if (text.isBlank()) return emptyList()
        val kindle = parseKindle(text)
        if (kindle.isNotEmpty()) return kindle
        val weixin = parseWeixin(text)
        if (weixin.isNotEmpty()) return weixin
        return parseGeneric(text)
    }

    private fun parseKindle(text: String): List<Clipping> {
        if (!text.contains("==========")) return emptyList()
        return text.split("==========").mapNotNull { block ->
            val lines = block.trim().lines().map { it.trim() }.filter { it.isNotEmpty() }
            if (lines.size < 2) return@mapNotNull null
            val (title, author) = splitTitleAuthor(lines.first())
            val meta = lines.getOrNull(1).orEmpty()
            val body = lines.drop(2).joinToString("\n").trim()
            if (title.isBlank() || body.isBlank()) return@mapNotNull null
            if (!looksLikeKindleMeta(meta)) return@mapNotNull null
            val isNote = meta.contains("笔记") || meta.contains("Note", ignoreCase = true)
            if (isNote) {
                Clipping(title, author, quote = "", note = body, source = ClippingSource.KINDLE)
            } else {
                Clipping(title, author, quote = body, source = ClippingSource.KINDLE)
            }
        }
    }

    private fun looksLikeKindleMeta(line: String): Boolean {
        val lower = line.lowercase()
        return line.startsWith("-") && (
            lower.contains("highlight") ||
                lower.contains("note") ||
                line.contains("标注") ||
                line.contains("笔记") ||
                line.contains("书签")
            )
    }

    private fun parseWeixin(text: String): List<Clipping> {
        val titled = Regex("""^《([^》]+)》\s*$""", RegexOption.MULTILINE).find(text)
        val hasMarker = text.contains("原文") || text.contains("划线") || text.contains("想法")
        if (titled == null || !hasMarker) return emptyList()
        var title = titled.groupValues[1].trim()
        var author = ""
        val out = mutableListOf<Clipping>()
        var quote = ""
        var collecting: String? = null
        fun flush() {
            val q = quote.trim()
            if (title.isNotBlank() && q.isNotBlank()) {
                out += Clipping(title, author, q, source = ClippingSource.WEIXIN_EXPORT)
            }
            quote = ""
            collecting = null
        }
        text.lineSequence().forEach { rawLine ->
            val line = rawLine.trim()
            when {
                line.matches(Regex("""《([^》]+)》""")) -> {
                    flush()
                    title = line.removePrefix("《").removeSuffix("》")
                }
                line.startsWith("作者") -> author = line.substringAfter("：").substringAfter(":").trim()
                line.startsWith("原文") || line.startsWith("划线") -> {
                    flush()
                    collecting = "quote"
                    val inline = line.substringAfter("：", "").substringAfter(":", "").trim()
                    if (inline.isNotBlank()) quote = inline
                }
                line.startsWith("想法") || line.startsWith("笔记") -> collecting = "skip-note-header"
                line.startsWith("#") -> Unit
                collecting == "quote" && line.isNotBlank() -> {
                    quote = if (quote.isBlank()) line else "$quote\n$line"
                }
            }
        }
        flush()
        return out
    }

    private fun parseGeneric(text: String): List<Clipping> {
        var title = "书摘"
        var author = ""
        val out = mutableListOf<Clipping>()
        var quote = ""
        fun flush() {
            val q = quote.trim().removePrefix("「").removeSuffix("」").trim()
            if (q.isNotBlank()) {
                out += Clipping(title, author, q, source = ClippingSource.GENERIC)
            }
            quote = ""
        }
        text.lineSequence().forEach { rawLine ->
            val line = rawLine.trim()
            when {
                line.startsWith("# ") -> {
                    flush()
                    title = line.removePrefix("# ").trim().ifBlank { title }
                }
                line.startsWith("作者") -> author = line.substringAfter("：").substringAfter(":").trim()
                line.startsWith(">") -> {
                    flush()
                    quote = line.removePrefix(">").trim()
                }
                line.startsWith("「") && line.endsWith("」") -> {
                    flush()
                    quote = line
                    flush()
                }
                quote.isNotBlank() && line.isNotBlank() -> quote += "\n$line"
                line.isBlank() -> flush()
            }
        }
        flush()
        return out
    }

    internal fun splitTitleAuthor(line: String): Pair<String, String> {
        val match = Regex("""^(.+?)\s*[（(]([^）)]+)[）)]$""").find(line.trim())
        return if (match != null) {
            match.groupValues[1].trim() to match.groupValues[2].trim()
        } else {
            line.trim() to ""
        }
    }
}

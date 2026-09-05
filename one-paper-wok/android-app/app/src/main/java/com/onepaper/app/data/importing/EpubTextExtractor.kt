package com.onepaper.app.data.importing

import java.io.File
import java.util.zip.ZipFile

data class ExtractedChapter(val href: String, val title: String, val plainText: String)

object EpubTextExtractor {
    fun isEncrypted(file: File): Boolean {
        ZipFile(file).use { zip ->
            val names = zip.entries().toList().map { it.name.lowercase() }
            if (names.any { it.endsWith("encryption.xml") || it.contains("meta-inf/encryption") }) {
                return true
            }
        }
        return false
    }

    fun extract(file: File): List<ExtractedChapter> {
        ZipFile(file).use { zip ->
            val htmlEntries = zip.entries().toList()
                .filter { it.name.endsWith(".xhtml", true) || it.name.endsWith(".html", true) }
                .sortedBy { it.name }
            if (htmlEntries.isEmpty()) {
                val textEntries = zip.entries().toList().filter { it.name.endsWith(".txt", true) }
                return textEntries.mapIndexed { idx, entry ->
                    zip.getInputStream(entry).bufferedReader().use { reader ->
                        ExtractedChapter(entry.name, "章节 ${idx + 1}", reader.readText())
                    }
                }
            }
            return htmlEntries.mapIndexed { idx, entry ->
                val raw = zip.getInputStream(entry).bufferedReader().use { it.readText() }
                ExtractedChapter(
                    href = entry.name,
                    title = extractTitle(raw) ?: "章节 ${idx + 1}",
                    plainText = stripHtml(raw),
                )
            }
        }
    }

    fun stripHtml(raw: String): String {
        val withoutScripts = raw
            .replace(Regex("(?is)<script[^>]*>.*?</script>"), " ")
            .replace(Regex("(?is)<style[^>]*>.*?</style>"), " ")
        val text = withoutScripts.replace(Regex("(?is)<[^>]+>"), " ")
        return text.replace("&nbsp;", " ")
            .replace("&amp;", "&")
            .replace("&lt;", "<")
            .replace("&gt;", ">")
            .replace(Regex("[ \\t]+"), " ")
            .replace(Regex("\\n{3,}"), "\n\n")
            .trim()
    }

    private fun extractTitle(raw: String): String? {
        val match = Regex("(?is)<title[^>]*>(.*?)</title>").find(raw)
            ?: Regex("(?is)<h1[^>]*>(.*?)</h1>").find(raw)
        return match?.groupValues?.get(1)?.let { stripHtml(it) }?.takeIf { it.isNotBlank() }
    }
}

object PdfGuard {
    fun looksEncrypted(file: File): Boolean {
        val probe = file.inputStream().use { input ->
            val buf = ByteArray(2_000_000)
            val n = input.read(buf)
            if (n <= 0) "" else String(buf, 0, n)
        }
        return probe.contains("/Encrypt")
    }
}

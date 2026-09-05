package com.onepaper.app.data.importing

import java.io.File
import java.util.zip.ZipFile

data class EpubBookMeta(
    val title: String?,
    val author: String?,
    val coverBytes: ByteArray?,
)

object EpubMeta {
    fun read(file: File): EpubBookMeta {
        return runCatching {
            ZipFile(file).use { zip ->
                val container = zip.bytes("META-INF/container.xml")?.decodeToString().orEmpty()
                val opfPath = Regex("""full-path="([^"]+)"""").find(container)?.groupValues?.get(1)
                    ?: zip.entries().toList().firstOrNull { it.name.endsWith(".opf", true) }?.name
                    ?: return EpubBookMeta(null, null, null)
                val opf = zip.bytes(opfPath)?.decodeToString().orEmpty()
                val title = firstDc(opf, "title")
                val author = firstDc(opf, "creator")
                val coverId = Regex("""name="cover"\s+content="([^"]+)"""").find(opf)?.groupValues?.get(1)
                    ?: Regex("""content="([^"]+)"\s+name="cover"""").find(opf)?.groupValues?.get(1)
                val href = coverId?.let { id ->
                    Regex("""id="${Regex.escape(id)}"[^>]*href="([^"]+)"""").find(opf)?.groupValues?.get(1)
                        ?: Regex("""href="([^"]+)"[^>]*id="${Regex.escape(id)}"""").find(opf)?.groupValues?.get(1)
                } ?: Regex("""media-type="image/[^"]+"[^>]*href="([^"]+)"""").find(opf)?.groupValues?.get(1)
                val coverBytes = href?.let { name ->
                    val resolved = resolve(opfPath, name)
                    zip.bytes(resolved)
                }
                EpubBookMeta(title, author, coverBytes)
            }
        }.getOrDefault(EpubBookMeta(null, null, null))
    }

    private fun firstDc(opf: String, tag: String): String? {
        val match = Regex("""<(?:dc:)?$tag[^>]*>([^<]+)</(?:dc:)?$tag>""", RegexOption.IGNORE_CASE).find(opf)
        return match?.groupValues?.get(1)?.trim()?.takeIf { it.isNotBlank() }
    }

    private fun resolve(opfPath: String, href: String): String {
        val base = opfPath.substringBeforeLast('/', "")
        val clean = href.substringBefore('#')
        return if (base.isBlank()) clean else "$base/$clean"
    }

    private fun ZipFile.bytes(name: String): ByteArray? {
        val entry = getEntry(name) ?: entries().toList().firstOrNull { it.name.equals(name, true) } ?: return null
        return getInputStream(entry).use { it.readBytes() }
    }
}

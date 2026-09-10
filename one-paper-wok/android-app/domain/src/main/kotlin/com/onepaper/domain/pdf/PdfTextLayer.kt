package com.onepaper.domain.pdf

import java.io.ByteArrayOutputStream
import java.util.zip.Inflater

/** 从 PDF 内容流抽出文本层。抽不出就诚实说没有，去走 OCR 叠页。 */
data class PdfPageText(
    val pageIndex: Int,
    val hasTextOperators: Boolean,
    val text: String,
)

object PdfTextLayer {
    fun extractPages(bytes: ByteArray, pageCount: Int): List<PdfPageText> {
        if (pageCount <= 0) return emptyList()
        val streams = contentStreams(bytes)
        return (0 until pageCount).map { index ->
            val raw = streams.getOrNull(index).orEmpty()
            val hasOps = hasTextOperators(raw)
            PdfPageText(index, hasOps, if (hasOps) extractStrings(raw).trim() else "")
        }
    }

    internal fun hasTextOperators(content: String): Boolean {
        return Regex("""(?<![A-Za-z])(?:Tj|TJ|'|")(?![A-Za-z])""").containsMatchIn(content)
    }

    internal fun extractStrings(content: String): String {
        val out = StringBuilder()
        var i = 0
        while (i < content.length) {
            val ch = content[i]
            if (ch == '(') {
                val parsed = readLiteral(content, i)
                out.append(parsed.first)
                i = parsed.second
                continue
            }
            if (ch == '<') {
                val parsed = readHex(content, i)
                out.append(parsed.first)
                i = parsed.second
                continue
            }
            i++
        }
        return out.toString().replace(Regex("[ \\t\\r\\n]{2,}"), " ")
    }

    private fun contentStreams(bytes: ByteArray): List<String> {
        val latin = bytes.toString(Charsets.ISO_8859_1)
        val found = mutableListOf<String>()
        var cursor = 0
        while (true) {
            val startToken = latin.indexOf("stream", cursor)
            if (startToken < 0) break
            val after = startToken + 6
            val bodyStart = when {
                latin.startsWith("\r\n", after) -> after + 2
                latin.getOrNull(after) == '\n' -> after + 1
                latin.getOrNull(after) == '\r' -> after + 1
                else -> after
            }
            val end = latin.indexOf("endstream", bodyStart)
            if (end < 0) break
            val header = latin.substring(0, startToken).takeLast(240)
            val raw = bytes.copyOfRange(
                bodyStart.coerceAtMost(bytes.size),
                end.coerceAtMost(bytes.size),
            )
            val decoded = if (header.contains("FlateDecode") || header.contains("/FlateDecode")) {
                inflate(raw) ?: raw.toString(Charsets.ISO_8859_1)
            } else {
                raw.toString(Charsets.ISO_8859_1)
            }
            if (hasTextOperators(decoded) || decoded.contains("BT")) {
                found += decoded
            }
            cursor = end + 9
        }
        return found
    }

    private fun inflate(raw: ByteArray): String? = runCatching {
        val inflater = Inflater()
        inflater.setInput(raw)
        val out = ByteArrayOutputStream()
        val buf = ByteArray(2048)
        while (!inflater.finished()) {
            val n = inflater.inflate(buf)
            if (n == 0 && inflater.needsInput()) break
            out.write(buf, 0, n)
        }
        inflater.end()
        out.toString("ISO-8859-1")
    }.getOrNull()

    private fun readLiteral(source: String, start: Int): Pair<String, Int> {
        val out = StringBuilder()
        var i = start + 1
        var depth = 1
        while (i < source.length && depth > 0) {
            val ch = source[i]
            when {
                ch == '\\' && i + 1 < source.length -> {
                    val next = source[i + 1]
                    out.append(
                        when (next) {
                            'n' -> '\n'
                            'r' -> '\r'
                            't' -> '\t'
                            '(' -> '('
                            ')' -> ')'
                            '\\' -> '\\'
                            else -> next
                        },
                    )
                    i += 2
                }
                ch == '(' -> {
                    depth++
                    out.append(ch)
                    i++
                }
                ch == ')' -> {
                    depth--
                    if (depth > 0) out.append(ch)
                    i++
                }
                else -> {
                    out.append(ch)
                    i++
                }
            }
        }
        return utf16IfBom(out.toString()) to i
    }

    private fun readHex(source: String, start: Int): Pair<String, Int> {
        val end = source.indexOf('>', start + 1).takeIf { it > 0 } ?: return "" to start + 1
        val hex = source.substring(start + 1, end).replace(Regex("\\s"), "")
        if (hex.isEmpty() || hex.length % 2 != 0) return "" to end + 1
        val data = hex.chunked(2).mapNotNull { runCatching { it.toInt(16).toByte() }.getOrNull() }.toByteArray()
        val text = if (data.size >= 2 && data[0] == 0xFE.toByte() && data[1] == 0xFF.toByte()) {
            String(data, Charsets.UTF_16BE)
        } else {
            data.toString(Charsets.ISO_8859_1)
        }
        return text to end + 1
    }

    private fun utf16IfBom(raw: String): String {
        val bytes = raw.toByteArray(Charsets.ISO_8859_1)
        return if (bytes.size >= 2 && bytes[0] == 0xFE.toByte() && bytes[1] == 0xFF.toByte()) {
            String(bytes, Charsets.UTF_16BE)
        } else {
            raw
        }
    }
}

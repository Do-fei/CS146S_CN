package com.onepaper.app.data.importing

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import java.util.zip.ZipEntry
import java.util.zip.ZipOutputStream

class EpubTextExtractorTest {
    @Test
    fun extractsXhtmlAndRejectsEncryption() {
        val file = File.createTempFile("sample", ".epub")
        ZipOutputStream(file.outputStream()).use { zip ->
            zip.putNextEntry(ZipEntry("mimetype"))
            zip.write("application/epub+zip".toByteArray())
            zip.closeEntry()
            zip.putNextEntry(ZipEntry("OEBPS/ch1.xhtml"))
            zip.write(
                """
                <html><head><title>慢烹</title></head>
                <body><h1>慢烹</h1><p>纸书是食材。</p></body></html>
                """.trimIndent().toByteArray(),
            )
            zip.closeEntry()
        }
        val chapters = EpubTextExtractor.extract(file)
        assertTrue(chapters.any { it.plainText.contains("纸书是食材") })
        assertFalse(EpubTextExtractor.isEncrypted(file))
        file.delete()
    }
}

package com.onepaper.domain.backup

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test
import java.io.File
import kotlin.io.path.createTempDirectory

class BackupPathsTest {
    @Test
    fun onlyLibraryPathsAreSafe() {
        assertTrue(BackupPaths.isSafe("library/e1/book.epub"))
        assertFalse(BackupPaths.isSafe("../library/e1/book.epub"))
        assertFalse(BackupPaths.isSafe("exports/onepaper-backup.json"))
        assertFalse(BackupPaths.isSafe("/library/e1/book.epub"))
    }

    @Test
    fun collectDropsBlankAndDupes() {
        val paths = BackupPaths.collect(
            listOf("library/a/cover.jpg", "library/a/cover.jpg", "", null, "cache/x"),
        )
        assertEquals(listOf("library/a/cover.jpg"), paths)
    }

    @Test
    fun zipRoundTripWritesOnlySafeFiles() {
        val root = createTempDirectory("onepaper-backup").toFile()
        val filesDir = File(root, "filesDir").apply { mkdirs() }
        val book = File(filesDir, "library/e1/book.txt").apply {
            parentFile.mkdirs()
            writeText("把书读薄")
        }
        val dest = File(root, "pack.zip")
        val catalog = """{"manifest":{"includesTokens":false}}"""
        BackupZip.write(dest, catalog, listOf("library/e1/book.txt" to book, "../evil" to book))
        assertTrue(BackupZip.looksLikeZip(dest))
        assertTrue(BackupZip.readCatalog(dest).contains("includesTokens"))
        val out = File(root, "out").apply { mkdirs() }
        assertEquals(1, BackupZip.extractFiles(dest, out))
        assertEquals("把书读薄", File(out, "library/e1/book.txt").readText())
        assertFalse(File(out, "evil").exists())
    }

    @Test
    fun restoreMessageDistinguishesOldJson() {
        val manifest = BackupManifest(
            createdAtEpochMs = 0,
            appVersion = "0.1.0-delivery",
            bookCount = 2,
            noteCount = 3,
            projectCount = 1,
            annotationCount = 4,
        )
        val old = RestoreOutcome(manifest, oldCatalogOnly = true, restoredFileCount = 0, missingFileCount = 0)
        assertTrue(old.userMessage().contains("没有书文件"))
        val full = RestoreOutcome(manifest, oldCatalogOnly = false, restoredFileCount = 5, missingFileCount = 0)
        assertTrue(full.userMessage().contains("已恢复 2 本书"))
        val missing = RestoreOutcome(manifest, oldCatalogOnly = false, restoredFileCount = 1, missingFileCount = 2)
        assertTrue(missing.userMessage().contains("缺失"))
    }
}

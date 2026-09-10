package com.onepaper.domain.backup

import java.io.File
import java.io.InputStream
import java.util.zip.ZipEntry
import java.util.zip.ZipFile
import java.util.zip.ZipOutputStream

object BackupZip {
    fun looksLikeZip(file: File): Boolean {
        if (!file.exists() || file.length() < 4) return false
        file.inputStream().use { input ->
            return input.read() == 0x50 && input.read() == 0x4B
        }
    }

    fun write(dest: File, catalogJson: String, files: List<Pair<String, File>>) {
        dest.parentFile?.mkdirs()
        ZipOutputStream(dest.outputStream().buffered()).use { zip ->
            zip.putNextEntry(ZipEntry(BackupPaths.ZIP_CATALOG))
            zip.write(catalogJson.toByteArray(Charsets.UTF_8))
            zip.closeEntry()
            files.forEach { (relative, file) ->
                if (!BackupPaths.isSafe(relative) || !file.isFile) return@forEach
                zip.putNextEntry(ZipEntry(BackupPaths.zipEntryName(relative)))
                file.inputStream().buffered().use { it.copyTo(zip) }
                zip.closeEntry()
            }
        }
    }

    fun readCatalog(zip: File): String {
        ZipFile(zip).use { archive ->
            val entry = archive.getEntry(BackupPaths.ZIP_CATALOG)
                ?: error("备份包里没有 library.json")
            return archive.getInputStream(entry).bufferedReader().use { it.readText() }
        }
    }

    fun extractFiles(zip: File, filesDir: File): Int {
        var written = 0
        ZipFile(zip).use { archive ->
            archive.entries().asSequence().filter { !it.isDirectory }.forEach { entry ->
                val relative = BackupPaths.relativeFromZipEntry(entry.name) ?: return@forEach
                val dest = File(filesDir, relative)
                dest.parentFile?.mkdirs()
                archive.getInputStream(entry).use { input: InputStream ->
                    dest.outputStream().use { input.copyTo(it) }
                }
                written += 1
            }
        }
        return written
    }
}

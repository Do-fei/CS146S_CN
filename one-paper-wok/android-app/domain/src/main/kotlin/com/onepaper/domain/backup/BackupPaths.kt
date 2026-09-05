package com.onepaper.domain.backup

import kotlinx.serialization.Serializable

/** 备份只收书房私有文件，拒绝路径穿越。 */
@Serializable
data class BackupFileRef(
    val relativePath: String,
    val size: Long = 0,
    val sha256: String? = null,
)

object BackupPaths {
    const val LIBRARY_PREFIX = "library/"
    const val ZIP_CATALOG = "library.json"
    const val ZIP_FILES_PREFIX = "files/"

    fun normalize(relative: String): String = relative.replace('\\', '/').trim().trimStart('/')

    fun isSafe(relative: String): Boolean {
        val n = normalize(relative)
        if (n.isBlank() || n.contains("..") || n.startsWith("/")) return false
        return n.startsWith(LIBRARY_PREFIX)
    }

    fun collect(paths: Iterable<String?>): List<String> {
        return paths.mapNotNull { it?.trim()?.takeIf { path -> path.isNotBlank() } }
            .map(::normalize)
            .filter(::isSafe)
            .distinct()
            .sorted()
    }

    fun zipEntryName(relative: String): String = ZIP_FILES_PREFIX + normalize(relative)

    fun relativeFromZipEntry(entryName: String): String? {
        val name = normalize(entryName)
        if (!name.startsWith(ZIP_FILES_PREFIX)) return null
        return name.removePrefix(ZIP_FILES_PREFIX).takeIf(::isSafe)
    }
}

data class RestoreOutcome(
    val manifest: BackupManifest,
    val oldCatalogOnly: Boolean,
    val restoredFileCount: Int,
    val missingFileCount: Int,
) {
    fun userMessage(): String {
        val head = "已恢复 ${manifest.bookCount} 本书、${manifest.noteCount} 则笔记、${manifest.annotationCount} 条划线。"
        return when {
            oldCatalogOnly ->
                head + " 这是目录 JSON，不含原书文件。请把书再导入一次。"
            missingFileCount > 0 ->
                head + " 已写入 $restoredFileCount 个文件，另有 $missingFileCount 个文件在包里缺失。"
            else ->
                head + " 已写入 $restoredFileCount 个书房文件。"
        }
    }
}

package com.onepaper.domain.backup

import kotlinx.serialization.Serializable

@Serializable
data class BackupManifest(
    val formatVersion: Int = 2,
    val createdAtEpochMs: Long,
    val appVersion: String,
    val bookCount: Int,
    val noteCount: Int,
    val projectCount: Int,
    val includesTokens: Boolean = false,
    val includesPrivateNotes: Boolean = true,
    val includesLibraryFiles: Boolean = false,
    val fileCount: Int = 0,
    val annotationCount: Int = 0,
)

object BackupPolicy {
    fun sanitize(manifest: BackupManifest): BackupManifest {
        check(!manifest.includesTokens) { "backup must never include tokens" }
        return manifest.copy(includesTokens = false)
    }
}

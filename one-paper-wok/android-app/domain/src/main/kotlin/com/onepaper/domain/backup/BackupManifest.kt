package com.onepaper.domain.backup

import kotlinx.serialization.Serializable

@Serializable
data class BackupManifest(
    val formatVersion: Int = 1,
    val createdAtEpochMs: Long,
    val appVersion: String,
    val bookCount: Int,
    val noteCount: Int,
    val projectCount: Int,
    val includesTokens: Boolean = false,
    val includesPrivateNotes: Boolean = true,
)

object BackupPolicy {
    fun sanitize(manifest: BackupManifest): BackupManifest {
        check(!manifest.includesTokens) { "backup must never include tokens" }
        return manifest.copy(includesTokens = false)
    }
}

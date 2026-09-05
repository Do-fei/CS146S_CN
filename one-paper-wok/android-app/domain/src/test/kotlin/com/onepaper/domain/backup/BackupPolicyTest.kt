package com.onepaper.domain.backup

import org.junit.Assert.assertFalse
import org.junit.Test

class BackupPolicyTest {
    @Test
    fun refusesTokenFlag() {
        val clean = BackupPolicy.sanitize(
            BackupManifest(
                createdAtEpochMs = 0,
                appVersion = "0.1.0-delivery",
                bookCount = 1,
                noteCount = 1,
                projectCount = 1,
                includesTokens = false,
            ),
        )
        assertFalse(clean.includesTokens)
    }

    @Test(expected = IllegalStateException::class)
    fun rejectsTokenBackup() {
        BackupPolicy.sanitize(
            BackupManifest(
                createdAtEpochMs = 0,
                appVersion = "0.1.0-delivery",
                bookCount = 0,
                noteCount = 0,
                projectCount = 0,
                includesTokens = true,
            ),
        )
    }
}

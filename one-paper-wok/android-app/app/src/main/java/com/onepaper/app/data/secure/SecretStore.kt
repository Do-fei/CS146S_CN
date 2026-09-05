package com.onepaper.app.data.secure

import android.content.Context
import android.content.SharedPreferences
import androidx.security.crypto.EncryptedSharedPreferences
import androidx.security.crypto.MasterKey
import dagger.hilt.android.qualifiers.ApplicationContext
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class SecretStore @Inject constructor(
    @ApplicationContext context: Context,
) {
    private val prefs: SharedPreferences = EncryptedSharedPreferences.create(
        context,
        "onepaper_secrets",
        MasterKey.Builder(context).setKeyScheme(MasterKey.KeyScheme.AES256_GCM).build(),
        EncryptedSharedPreferences.PrefKeyEncryptionScheme.AES256_SIV,
        EncryptedSharedPreferences.PrefValueEncryptionScheme.AES256_GCM,
    )

    fun deepSeekKey(): String? = prefs.getString(KEY_DEEPSEEK, null)?.takeIf { it.isNotBlank() }

    fun hasDeepSeekKey(): Boolean = !deepSeekKey().isNullOrBlank()

    fun maskedDeepSeekKey(): String? {
        val raw = deepSeekKey() ?: return null
        if (raw.length <= 4) return "••••"
        return "••••${raw.takeLast(4)}"
    }

    fun setDeepSeekKey(value: String?) {
        prefs.edit().putString(KEY_DEEPSEEK, value?.trim().orEmpty().ifBlank { null }).apply()
    }

    companion object {
        private const val KEY_DEEPSEEK = "deepseek_api_key"
    }
}

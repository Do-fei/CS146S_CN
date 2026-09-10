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

    fun webDavUrl(): String? = prefs.getString(KEY_DAV_URL, null)?.takeIf { it.isNotBlank() }
    fun webDavUser(): String? = prefs.getString(KEY_DAV_USER, null)?.takeIf { it.isNotBlank() }
    fun webDavPassword(): String? = prefs.getString(KEY_DAV_PASS, null)?.takeIf { it.isNotBlank() }
    fun webDavPath(): String = prefs.getString(KEY_DAV_PATH, null)?.ifBlank { null }
        ?: com.onepaper.domain.backup.WebDavPath.DEFAULT_REMOTE

    fun hasWebDav(): Boolean = !webDavUrl().isNullOrBlank() && !webDavPassword().isNullOrBlank()

    fun setWebDav(url: String?, user: String?, password: String?, path: String?) {
        prefs.edit()
            .putString(KEY_DAV_URL, url?.trim().orEmpty().ifBlank { null })
            .putString(KEY_DAV_USER, user?.trim().orEmpty().ifBlank { null })
            .putString(KEY_DAV_PASS, password?.trim().orEmpty().ifBlank { null })
            .putString(KEY_DAV_PATH, path?.trim().orEmpty().ifBlank { null })
            .apply()
    }

    fun clearWebDav() {
        setWebDav(null, null, null, null)
    }

    companion object {
        private const val KEY_DEEPSEEK = "deepseek_api_key"
        private const val KEY_DAV_URL = "webdav_url"
        private const val KEY_DAV_USER = "webdav_user"
        private const val KEY_DAV_PASS = "webdav_password"
        private const val KEY_DAV_PATH = "webdav_path"
    }
}

package com.onepaper.app.data.prefs

import android.content.Context
import androidx.datastore.preferences.core.booleanPreferencesKey
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import javax.inject.Inject
import javax.inject.Singleton

private val Context.dataStore by preferencesDataStore("onepaper_prefs")

@Singleton
class UserPrefs @Inject constructor(
    @ApplicationContext private val context: Context,
) {
    private val onboarding = booleanPreferencesKey("onboarding_done")
    private val uploadPages = booleanPreferencesKey("upload_pages_allowed")
    private val uploadNotes = booleanPreferencesKey("upload_notes_allowed")
    private val dark = booleanPreferencesKey("dark_theme")
    private val backend = stringPreferencesKey("backend_url")
    private val emberDay = stringPreferencesKey("ember_day")
    private val emberDismissed = stringPreferencesKey("ember_dismissed")

    val onboardingDone: Flow<Boolean> = context.dataStore.data.map { it[onboarding] ?: false }
    val uploadPagesAllowed: Flow<Boolean> = context.dataStore.data.map { it[uploadPages] ?: false }
    val uploadNotesAllowed: Flow<Boolean> = context.dataStore.data.map { it[uploadNotes] ?: false }
    val darkTheme: Flow<Boolean> = context.dataStore.data.map { it[dark] ?: false }
    val backendUrl: Flow<String> = context.dataStore.data.map { it[backend] ?: "" }
    val emberDismissedIds: Flow<Pair<String, Set<String>>> = context.dataStore.data.map { prefs ->
        val day = prefs[emberDay].orEmpty()
        val ids = prefs[emberDismissed].orEmpty().split(',').filter { it.isNotBlank() }.toSet()
        day to ids
    }

    suspend fun setOnboardingDone() {
        context.dataStore.edit { it[onboarding] = true }
    }

    suspend fun setUploadPages(value: Boolean) {
        context.dataStore.edit { it[uploadPages] = value }
    }

    suspend fun setUploadNotes(value: Boolean) {
        context.dataStore.edit { it[uploadNotes] = value }
    }

    suspend fun setDarkTheme(value: Boolean) {
        context.dataStore.edit { it[dark] = value }
    }

    suspend fun setBackendUrl(value: String) {
        context.dataStore.edit { it[backend] = value }
    }

    suspend fun dismissEmber(dayKey: String, ids: Set<String>) {
        context.dataStore.edit {
            it[emberDay] = dayKey
            it[emberDismissed] = ids.joinToString(",")
        }
    }
}

package com.onepaper.app.data.repo

import com.onepaper.app.data.local.NoteDao
import com.onepaper.app.data.local.NoteEntity
import com.onepaper.domain.search.ChineseNgram
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class NoteRepository @Inject constructor(
    private val notes: NoteDao,
) {
    fun observeAll(): Flow<List<NoteEntity>> = notes.observeAll()

    fun observeSearch(query: String): Flow<List<NoteEntity>> = notes.observeAll().map { list ->
        if (query.isBlank()) list
        else list.filter { ChineseNgram.matches(it.title + it.userDraft + (it.recognitionDraft ?: ""), query) }
    }

    suspend fun get(id: String) = notes.get(id)

    suspend fun save(
        id: String?,
        bookId: String?,
        title: String,
        userDraft: String,
        recognitionDraft: String?,
        imageRelPath: String?,
        sourceBound: Boolean,
        locatorJson: String?,
    ): String {
        val noteId = id ?: UUID.randomUUID().toString()
        notes.upsert(
            NoteEntity(
                id = noteId,
                bookId = bookId,
                title = title,
                userDraft = userDraft,
                recognitionDraft = recognitionDraft,
                imageRelPath = imageRelPath,
                sourceBound = sourceBound,
                locatorJson = locatorJson,
                updatedAt = System.currentTimeMillis(),
            ),
        )
        return noteId
    }

    suspend fun delete(id: String) = notes.delete(id)
}

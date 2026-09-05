package com.onepaper.app.data.repo

import com.onepaper.app.data.local.ConversationDao
import com.onepaper.app.data.local.ConversationEntity
import com.onepaper.app.data.local.EditionDao
import com.onepaper.app.data.local.MessageEntity
import com.onepaper.domain.ai.AiProvider
import com.onepaper.domain.ai.CompanionRequest
import com.onepaper.domain.ai.ScopeBar
import com.onepaper.domain.citation.Citation
import com.onepaper.domain.citation.ContentLocator
import com.onepaper.domain.citation.TextQuote
import com.onepaper.domain.model.Coverage
import kotlinx.coroutines.flow.Flow
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class CompanionRepository @Inject constructor(
    private val conversations: ConversationDao,
    private val editions: EditionDao,
    private val library: LibraryRepository,
    private val ai: AiProvider,
) {
    suspend fun conversationId(bookId: String): String {
        conversations.forBook(bookId)?.let { return it.id }
        val id = UUID.randomUUID().toString()
        conversations.upsert(ConversationEntity(id, bookId, "搭子", System.currentTimeMillis()))
        return id
    }

    fun messages(conversationId: String): Flow<List<MessageEntity>> =
        conversations.observeMessages(conversationId)

    suspend fun ask(bookId: String, question: String, selectedQuote: String?) {
        val conversationId = conversationId(bookId)
        conversations.upsertMessage(
            MessageEntity(UUID.randomUUID().toString(), conversationId, "user", question, false, System.currentTimeMillis()),
        )
        val eds = editions.forBook(bookId)
        val chapterCount = eds.sumOf { library.chaptersOf(it.id).size }
        val pageCount = eds.sumOf { it.pageCount }
        val book = library.book(bookId)
        val whole = book?.coverage == Coverage.WHOLE_BOOK.name
        val first = eds.firstOrNull()?.let { library.chaptersOf(it.id).firstOrNull() }
        val quote = selectedQuote ?: first?.plainText?.trim()?.take(24).orEmpty()
        val evidence = if (quote.isBlank()) {
            emptyList()
        } else {
            listOf(
                Citation(
                    sourceDocumentId = first?.editionId ?: bookId,
                    contentVersion = first?.contentVersion ?: "v1",
                    locator = ContentLocator.Epub(first?.href ?: "unknown", 0.0, TextQuote(quote)),
                    quote = quote,
                ),
            )
        }
        val answer = ai.answer(
            CompanionRequest(
                bookId = bookId,
                question = question,
                scope = ScopeBar(chapterCount, pageCount, whole),
                evidence = evidence,
            ),
        )
        conversations.upsertMessage(
            MessageEntity(
                id = UUID.randomUUID().toString(),
                conversationId = conversationId,
                role = "ai",
                text = answer.text,
                insufficientEvidence = answer.insufficientEvidence,
                createdAt = System.currentTimeMillis(),
            ),
        )
    }
}

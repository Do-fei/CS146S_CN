package com.onepaper.app.data.repo

import com.onepaper.app.data.local.ConversationDao
import com.onepaper.app.data.local.ConversationEntity
import com.onepaper.app.data.local.EditionDao
import com.onepaper.app.data.local.MessageEntity
import com.onepaper.app.data.prefs.UserPrefs
import com.onepaper.domain.ai.AiProvider
import com.onepaper.domain.ai.CompanionRequest
import com.onepaper.domain.ai.ScopeBar
import com.onepaper.domain.citation.Citation
import com.onepaper.domain.citation.ContentLocator
import com.onepaper.domain.citation.LocatorCodec
import com.onepaper.domain.citation.TextQuote
import com.onepaper.domain.model.Coverage
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.first
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class CompanionRepository @Inject constructor(
    private val conversations: ConversationDao,
    private val editions: EditionDao,
    private val library: LibraryRepository,
    private val ai: AiProvider,
    private val prefs: UserPrefs,
) {
    suspend fun conversationId(bookId: String): String {
        conversations.forBook(bookId)?.let { return it.id }
        val id = UUID.randomUUID().toString()
        conversations.upsert(ConversationEntity(id, bookId, "搭子", System.currentTimeMillis()))
        return id
    }

    fun messages(conversationId: String): Flow<List<MessageEntity>> =
        conversations.observeMessages(conversationId)

    suspend fun ask(
        bookId: String,
        question: String,
        selectedQuote: String?,
        locatorJson: String? = null,
        editionId: String? = null,
        onDelta: (String) -> Unit = {},
    ) {
        val conversationId = conversationId(bookId)
        val sendPages = prefs.uploadPagesAllowed.first()
        val eds = editions.forBook(bookId)
        val chosenEdition = editionId?.let { id -> eds.firstOrNull { it.id == id } } ?: eds.firstOrNull()
        val chapterCount = eds.sumOf { library.chaptersOf(it.id).size }
        val pageCount = eds.sumOf { it.pageCount }
        val book = library.book(bookId)
        val hasRange = chapterCount > 0 || pageCount > 0
        val whole = book?.coverage == Coverage.WHOLE_BOOK.name && hasRange
        val firstChapter = chosenEdition?.let { library.chaptersOf(it.id).firstOrNull() }
        val firstPage = chosenEdition?.let { library.pagesOf(it.id).firstOrNull() }
        val quote = selectedQuote?.trim().orEmpty().ifBlank {
            if (!sendPages) {
                ""
            } else {
                firstChapter?.plainText?.trim()?.take(24)
                    ?: firstPage?.ocrText?.trim()?.take(24)
                    ?: firstPage?.recognitionDraft?.trim()?.take(24)
                    ?: ""
            }
        }
        val locator = locatorJson?.let { raw -> runCatching { LocatorCodec.decode(raw) }.getOrNull() }
        val evidence = if (quote.isBlank()) {
            emptyList()
        } else {
            val resolved = locator ?: when {
                firstChapter != null -> ContentLocator.Epub(firstChapter.href, 0.0, TextQuote(quote))
                firstPage != null -> ContentLocator.PdfPageRect(firstPage.index, 0.0, 0.0, 1.0, 1.0, TextQuote(quote))
                else -> null
            }
            if (resolved == null) {
                emptyList()
            } else {
                listOf(
                    Citation(
                        sourceDocumentId = chosenEdition?.id ?: firstChapter?.editionId ?: firstPage?.editionId.orEmpty(),
                        contentVersion = firstChapter?.contentVersion ?: "v1",
                        locator = resolved,
                        quote = quote,
                    ),
                )
            }
        }
        val encodedLocator = evidence.firstOrNull()?.let { LocatorCodec.encode(it.locator) }
        val evidenceEdition = chosenEdition?.id ?: evidence.firstOrNull()?.sourceDocumentId
        conversations.upsertMessage(
            MessageEntity(
                id = UUID.randomUUID().toString(),
                conversationId = conversationId,
                role = "user",
                text = question,
                insufficientEvidence = false,
                createdAt = System.currentTimeMillis(),
                quote = quote.takeIf { it.isNotBlank() },
                locatorJson = encodedLocator,
                editionId = evidenceEdition,
            ),
        )
        val answer = ai.answerStreaming(
            CompanionRequest(
                bookId = bookId,
                question = question,
                scope = ScopeBar(chapterCount, pageCount, whole),
                evidence = evidence,
            ),
            onDelta = onDelta,
        )
        conversations.upsertMessage(
            MessageEntity(
                id = UUID.randomUUID().toString(),
                conversationId = conversationId,
                role = "ai",
                text = answer.text,
                insufficientEvidence = answer.insufficientEvidence,
                createdAt = System.currentTimeMillis(),
                quote = evidence.firstOrNull()?.quote,
                locatorJson = encodedLocator,
                editionId = evidenceEdition,
            ),
        )
    }
}

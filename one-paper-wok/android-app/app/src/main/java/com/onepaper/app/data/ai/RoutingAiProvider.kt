package com.onepaper.app.data.ai

import com.onepaper.app.data.secure.SecretStore
import com.onepaper.domain.ai.AiProvider
import com.onepaper.domain.ai.CompanionAnswer
import com.onepaper.domain.ai.CompanionRequest
import com.onepaper.domain.recook.ChangeProposal
import com.onepaper.domain.recook.ProjectSnapshot
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class RoutingAiProvider @Inject constructor(
    private val secrets: SecretStore,
    private val deepSeek: DeepSeekClient,
) : AiProvider {

    override suspend fun answer(request: CompanionRequest): CompanionAnswer {
        if (!secrets.hasDeepSeekKey()) return needKey()
        return runCatching { deepSeek.answer(request) }
            .getOrElse { error -> failure(request, error) }
    }

    override suspend fun answerStreaming(
        request: CompanionRequest,
        onDelta: (String) -> Unit,
    ): CompanionAnswer {
        if (!secrets.hasDeepSeekKey()) {
            val answer = needKey()
            onDelta(answer.text)
            return answer
        }
        return try {
            deepSeek.answerStreaming(request, onDelta)
        } catch (cancelled: kotlinx.coroutines.CancellationException) {
            throw cancelled
        } catch (error: Throwable) {
            val answer = failure(request, error)
            onDelta(answer.text)
            answer
        }
    }

    private fun needKey(): CompanionAnswer =
        CompanionAnswer(
            text = "先到设置里填提问用的 Key。",
            citations = emptyList(),
            insufficientEvidence = true,
            refusedWholeBookConclusion = false,
        )

    private fun failure(request: CompanionRequest, error: Throwable): CompanionAnswer =
        CompanionAnswer(
            text = safeMessage(error),
            citations = request.evidence,
            insufficientEvidence = true,
            refusedWholeBookConclusion = false,
        )

    override suspend fun proposeRecook(base: ProjectSnapshot, userNotes: List<String>): ChangeProposal {
        if (!secrets.hasDeepSeekKey()) error("先到设置里填提问用的 Key。")
        return deepSeek.proposeRecook(base, userNotes)
    }

    private fun safeMessage(error: Throwable): String {
        val text = error.message.orEmpty()
        if (text.contains("Key", ignoreCase = true) && text.length > 40) {
            return "密钥或网络错误"
        }
        return text.ifBlank { "网络或服务错误" }
    }
}

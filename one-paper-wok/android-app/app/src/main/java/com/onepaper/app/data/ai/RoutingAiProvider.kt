package com.onepaper.app.data.ai

import com.onepaper.app.data.secure.SecretStore
import com.onepaper.domain.ai.AiProvider
import com.onepaper.domain.ai.CompanionAnswer
import com.onepaper.domain.ai.CompanionRequest
import com.onepaper.domain.ai.FakeAiProvider
import com.onepaper.domain.recook.ChangeProposal
import com.onepaper.domain.recook.ProjectSnapshot
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class RoutingAiProvider @Inject constructor(
    private val secrets: SecretStore,
    private val fake: FakeAiProvider,
    private val deepSeek: DeepSeekClient,
) : AiProvider {

    override suspend fun answer(request: CompanionRequest): CompanionAnswer {
        if (!secrets.hasDeepSeekKey()) return fake.answer(request)
        return runCatching { deepSeek.answer(request) }
            .getOrElse { error ->
                CompanionAnswer(
                    text = "DeepSeek 不可用：${safeMessage(error)}。阅读和笔记仍可继续。",
                    citations = request.evidence,
                    insufficientEvidence = true,
                    refusedWholeBookConclusion = false,
                )
            }
    }

    override suspend fun proposeRecook(base: ProjectSnapshot, userNotes: List<String>): ChangeProposal {
        if (!secrets.hasDeepSeekKey()) return fake.proposeRecook(base, userNotes)
        return runCatching { deepSeek.proposeRecook(base, userNotes) }
            .getOrElse { fake.proposeRecook(base, userNotes) }
    }

    private fun safeMessage(error: Throwable): String {
        val text = error.message.orEmpty()
        if (text.contains("Key", ignoreCase = true) && text.length > 40) {
            return "密钥或网络错误"
        }
        return text.ifBlank { "网络或服务错误" }
    }
}

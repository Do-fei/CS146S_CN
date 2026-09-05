package com.onepaper.app.data.ai

import com.onepaper.app.data.secure.SecretStore
import com.onepaper.domain.ai.CompanionAnswer
import com.onepaper.domain.ai.CompanionRequest
import com.onepaper.domain.ai.RecookJsonParser
import com.onepaper.domain.recook.ChangeProposal
import com.onepaper.domain.recook.ProjectSnapshot
import kotlinx.serialization.Serializable
import kotlinx.serialization.encodeToString
import kotlinx.serialization.json.Json
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class DeepSeekClient @Inject constructor(
    private val secrets: SecretStore,
) {
    private val json = Json { ignoreUnknownKeys = true; explicitNulls = false }
    private val http = OkHttpClient.Builder()
        .connectTimeout(20, TimeUnit.SECONDS)
        .readTimeout(90, TimeUnit.SECONDS)
        .writeTimeout(30, TimeUnit.SECONDS)
        .build()

    fun answer(request: CompanionRequest): CompanionAnswer {
        val key = secrets.deepSeekKey() ?: error("missing key")
        if (looksLikeWholeBook(request.question) && !request.scope.claimsWholeBook) {
            return CompanionAnswer(
                text = "目前只导入了部分章节/页，不能给出全书结论。请把问题限制在已导入范围内。",
                citations = request.evidence,
                insufficientEvidence = true,
                refusedWholeBookConclusion = true,
            )
        }
        if (request.evidence.isEmpty()) {
            return CompanionAnswer(
                text = "证据不足：当前提问没有可点回的原文定位。",
                citations = emptyList(),
                insufficientEvidence = true,
                refusedWholeBookConclusion = false,
            )
        }
        val evidenceBlock = request.evidence.joinToString("\n") { "- 「${it.quote}」" }
        val system = """
            你是一纸书煲的阅读搭子。只根据用户已导入范围内的引用回答。
            不要假装读过未导入的部分。不要输出全书结论，除非范围标明是全书。
            不要索要或重复 API Key。引用必须来自下列证据。
            用简体中文。
        """.trimIndent()
        val user = """
            问题：${request.question}
            已导入章节数：${request.scope.importedChapterCount}，页数：${request.scope.importedPageCount}，是否全书：${request.scope.claimsWholeBook}
            证据：
            $evidenceBlock
        """.trimIndent()
        val text = complete(key, listOf(Msg("system", system), Msg("user", user)), jsonMode = false)
        return CompanionAnswer(
            text = text,
            citations = request.evidence,
            insufficientEvidence = false,
            refusedWholeBookConclusion = false,
        )
    }

    fun proposeRecook(base: ProjectSnapshot, userNotes: List<String>): ChangeProposal {
        val key = secrets.deepSeekKey() ?: error("missing key")
        val sections = base.sections.joinToString("\n") {
            "- ${it.sectionId} (${it.kind}) ${it.title}: ${it.body.take(400)}"
        }
        val system = """
            你只输出 JSON，对象形如 {"items":[...]}。
            每项必须是 insert、replace 或 noop，且带稳定 sectionId。
            禁止整份重写项目。replace 只能改已有 sectionId。
            用户笔记默认不要整段覆盖用户已写内容。
        """.trimIndent()
        val user = """
            请给出回煲建议 JSON。
            当前分节：
            $sections
            用户补充：${userNotes.joinToString("；").ifBlank { "无" }}
        """.trimIndent()
        val raw = complete(key, listOf(Msg("system", system), Msg("user", user)), jsonMode = true)
        return RecookJsonParser.parse(raw, base)
    }

    private fun complete(apiKey: String, messages: List<Msg>, jsonMode: Boolean): String {
        val body = ChatRequest(
            model = MODEL,
            messages = messages,
            stream = false,
            response_format = if (jsonMode) ResponseFormat("json_object") else null,
        )
        val req = Request.Builder()
            .url(ENDPOINT)
            .addHeader("Authorization", "Bearer $apiKey")
            .addHeader("Content-Type", "application/json")
            .post(json.encodeToString(body).toRequestBody(JSON))
            .build()
        http.newCall(req).execute().use { resp ->
            val raw = resp.body?.string().orEmpty()
            if (!resp.isSuccessful) {
                if (resp.code == 401 || resp.code == 403) {
                    error("DeepSeek Key 无效或额度不足")
                }
                error("DeepSeek 请求失败（${resp.code}）")
            }
            val parsed = json.decodeFromString<ChatResponse>(raw)
            return parsed.choices.firstOrNull()?.message?.content?.trim().orEmpty()
                .ifBlank { error("DeepSeek 返回空内容") }
        }
    }

    private fun looksLikeWholeBook(question: String): Boolean {
        val keys = listOf("全书", "整本书", "总结这本书", "这本书讲了什么", "完整结论")
        return keys.any { question.contains(it) }
    }

    @Serializable
    private data class ChatRequest(
        val model: String,
        val messages: List<Msg>,
        val stream: Boolean,
        val response_format: ResponseFormat? = null,
    )

    @Serializable
    private data class ResponseFormat(val type: String)

    @Serializable
    private data class Msg(val role: String, val content: String)

    @Serializable
    private data class ChatResponse(val choices: List<Choice> = emptyList())

    @Serializable
    private data class Choice(val message: ChoiceMessage? = null)

    @Serializable
    private data class ChoiceMessage(val content: String? = null)

    companion object {
        const val ENDPOINT = "https://api.deepseek.com/chat/completions"
        const val MODEL = "deepseek-v4-flash"
        private val JSON = "application/json; charset=utf-8".toMediaType()
    }
}

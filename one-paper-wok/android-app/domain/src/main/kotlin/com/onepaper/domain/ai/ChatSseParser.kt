package com.onepaper.domain.ai

import kotlinx.serialization.json.Json
import kotlinx.serialization.json.contentOrNull
import kotlinx.serialization.json.jsonArray
import kotlinx.serialization.json.jsonObject
import kotlinx.serialization.json.jsonPrimitive

/** 解析 OpenAI / DeepSeek chat.completions SSE 的 content delta。 */
object ChatSseParser {
    private val json = Json { ignoreUnknownKeys = true }

    fun contentFromData(data: String): String? {
        val payload = data.trim()
        if (payload.isEmpty() || payload == "[DONE]") return null
        return runCatching {
            val root = json.parseToJsonElement(payload).jsonObject
            val choice = root["choices"]?.jsonArray?.firstOrNull()?.jsonObject ?: return@runCatching null
            val delta = choice["delta"]?.jsonObject
            delta?.get("content")?.jsonPrimitive?.contentOrNull
                ?: choice["message"]?.jsonObject?.get("content")?.jsonPrimitive?.contentOrNull
        }.getOrNull()?.takeIf { it.isNotEmpty() }
    }

    fun dataFromLine(line: String): String? {
        val trimmed = line.trim()
        if (!trimmed.startsWith("data:")) return null
        return trimmed.removePrefix("data:").trim()
    }
}

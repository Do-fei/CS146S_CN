package com.onepaper.domain.ai

import org.junit.Assert.assertEquals
import org.junit.Assert.assertNull
import org.junit.Test

class ChatSseParserTest {
    @Test
    fun readsDeltaContent() {
        val data = """{"choices":[{"delta":{"content":"慢"}}]}"""
        assertEquals("慢", ChatSseParser.contentFromData(data))
    }

    @Test
    fun doneIsNull() {
        assertNull(ChatSseParser.contentFromData("[DONE]"))
    }

    @Test
    fun stripsDataPrefix() {
        assertEquals("{\"a\":1}", ChatSseParser.dataFromLine("data: {\"a\":1}"))
        assertNull(ChatSseParser.dataFromLine("event: message"))
    }
}

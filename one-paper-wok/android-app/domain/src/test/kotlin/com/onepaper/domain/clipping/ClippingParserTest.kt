package com.onepaper.domain.clipping

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class ClippingParserTest {
    @Test
    fun readsKindleMyClippings() {
        val raw = """
            Slow Cook (Ada)
            - Your Highlight on page 3 | location 12-14 | Added on Monday, January 1, 2024 12:00:00 AM

            把书读薄

            ==========
            Slow Cook (Ada)
            - Your Note on page 3 | location 15 | Added on Monday, January 1, 2024 12:01:00 AM

            我只记下这一句。

            ==========
        """.trimIndent()
        val items = ClippingParser.parse(raw)
        assertEquals(2, items.size)
        assertEquals("Slow Cook", items[0].bookTitle)
        assertEquals("Ada", items[0].author)
        assertEquals("把书读薄", items[0].quote)
        assertEquals(ClippingSource.KINDLE, items[0].source)
        assertEquals("我只记下这一句。", items[1].note)
    }

    @Test
    fun readsChineseKindleAndWeixinExport() {
        val kindle = """
            慢烹之书（项目组）
            - 您在第 2 页的标注 | 添加于 2026年1月1日

            把思考养厚
            ==========
        """.trimIndent()
        val k = ClippingParser.parse(kindle).single()
        assertEquals("慢烹之书", k.bookTitle)
        assertEquals("把思考养厚", k.quote)

        val weixin = """
            《慢烹之书》
            作者：项目组

            原文：
            成果带走。

            想法：
            这是我的。
        """.trimIndent()
        val w = ClippingParser.parse(weixin).single()
        assertEquals("慢烹之书", w.bookTitle)
        assertEquals("成果带走。", w.quote)
        assertEquals(ClippingSource.WEIXIN_EXPORT, w.source)
    }

    @Test
    fun genericMarkdownQuotes() {
        val raw = """
            # 一纸
            作者：自己

            > 先在这台设备建立书房
        """.trimIndent()
        val item = ClippingParser.parse(raw).single()
        assertEquals("一纸", item.bookTitle)
        assertTrue(item.quote.contains("建立书房"))
        assertEquals(ClippingSource.GENERIC, item.source)
    }
}

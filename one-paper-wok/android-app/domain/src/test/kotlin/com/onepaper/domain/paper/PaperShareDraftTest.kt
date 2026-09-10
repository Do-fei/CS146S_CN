package com.onepaper.domain.paper

import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class PaperShareDraftTest {
    private val input = PaperDraftInput(
        title = "慢烹之书",
        sourceQuotes = listOf("把书读薄"),
        aiSections = listOf("精华" to "这是整理，不是全书。"),
        userSections = listOf("我的理解" to "我只记下这一句。"),
        explore = "还想问范围外的部分。",
    )

    @Test
    fun markdownMarksLayersAndLooksLikePaper() {
        val md = PaperShareDraft.markdown(input)
        assertTrue(md.contains("# 慢烹之书"))
        assertTrue(md.contains("出煲"))
        assertTrue(md.contains("原书"))
        assertTrue(md.contains("把书读薄"))
        assertTrue(md.contains("层：AI"))
        assertTrue(md.contains("层：我的"))
        assertFalse(md.contains("\"items\""))
        assertTrue(md.contains("公开稿未附私人批注"))
    }

    @Test
    fun plainUsesLayerBrackets() {
        val text = PaperShareDraft.plain(input)
        assertTrue(text.contains("【原书】"))
        assertTrue(text.contains("【AI】精华"))
        assertTrue(text.contains("【我的】我的理解"))
        assertTrue(text.contains("【待探索】"))
        assertFalse(text.contains("{"))
    }

    @Test
    fun privateNotesOnlyWhenAsked() {
        val withNotes = PaperShareDraft.markdown(input.copy(privateNotes = listOf("只给自己看")))
        assertTrue(withNotes.contains("只给自己看"))
        val publicDraft = PaperShareDraft.markdown(input)
        assertFalse(publicDraft.contains("只给自己看"))
    }
}

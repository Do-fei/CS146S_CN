package com.onepaper.domain.ai

import com.onepaper.domain.recook.ProjectSection
import com.onepaper.domain.recook.ProjectSnapshot
import com.onepaper.domain.recook.ProposalOp
import com.onepaper.domain.recook.SectionKind
import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class RecookJsonParserTest {
    private val base = ProjectSnapshot(
        revisionId = "rev-1",
        revision = 1,
        sections = listOf(
            ProjectSection("s-me", SectionKind.UNDERSTANDING, "我的理解", "旧稿", 1),
        ),
    )

    @Test
    fun acceptsReplaceForKnownSection() {
        val proposal = RecookJsonParser.parse(
            """{"items":[{"sectionId":"s-me","op":"replace","proposedBody":"新稿"}]}""",
            base,
        )
        assertEquals(ProposalOp.REPLACE, proposal.items.single().op)
        assertEquals("新稿", proposal.items.single().proposedBody)
    }

    @Test
    fun dropsUnknownReplaceAndFencedJsonStillWorks() {
        val raw = """
            ```json
            {"items":[
              {"sectionId":"nope","op":"replace","proposedBody":"坏"},
              {"sectionId":"s-me","op":"replace","proposedBody":"好"}
            ]}
            ```
        """.trimIndent()
        val proposal = RecookJsonParser.parse(raw, base)
        assertEquals(listOf("s-me"), proposal.items.map { it.sectionId })
    }

    @Test(expected = IllegalArgumentException::class)
    fun rejectsEmptyAfterValidation() {
        RecookJsonParser.parse("""{"items":[{"sectionId":"ghost","op":"replace","proposedBody":"x"}]}""", base)
    }

    @Test
    fun rejectsWholeDocumentRewriteShape() {
        val raw = """{"summary":"整本重写","items":[]}"""
        try {
            RecookJsonParser.parse(raw, base)
            assertTrue(false)
        } catch (_: Exception) {
            assertTrue(true)
        }
    }
}

package com.onepaper.domain.recook

import org.junit.Assert.assertEquals
import org.junit.Assert.assertFalse
import org.junit.Assert.assertTrue
import org.junit.Test

class RecookMergerTest {
    private val merger = RecookMerger()

    private val base = ProjectSnapshot(
        revisionId = "rev-1",
        revision = 1,
        sections = listOf(
            ProjectSection("s-essence", SectionKind.ESSENCE, "精华", "原书要点甲。", 1),
            ProjectSection("s-me", SectionKind.UNDERSTANDING, "我的理解", "我认为重点是甲。", 1),
        ),
    )

    @Test
    fun acceptReplaceWhenUserDidNotEdit() {
        val proposal = ChangeProposal(
            proposalId = "p1",
            baseRevisionId = "rev-1",
            items = listOf(
                ChangeProposalItem(
                    itemId = "i1",
                    sectionId = "s-me",
                    op = ProposalOp.REPLACE,
                    proposedBody = "我认为重点是甲，并补充乙。",
                    basedOnSectionRevision = 1,
                ),
            ),
        )
        val result = merger.merge(
            base = base,
            current = base,
            proposal = proposal,
            decisions = mapOf("i1" to ItemDecision(ProposalDecision.ACCEPT)),
            nextRevisionId = "rev-2",
        )
        assertFalse(result.hasConflicts)
        assertEquals("我认为重点是甲，并补充乙。", result.snapshot.section("s-me")!!.body)
        assertEquals("原书要点甲。", result.snapshot.section("s-essence")!!.body)
    }

    @Test
    fun rejectKeepsUserText() {
        val proposal = ChangeProposal(
            proposalId = "p1",
            baseRevisionId = "rev-1",
            items = listOf(
                ChangeProposalItem(
                    itemId = "i1",
                    sectionId = "s-me",
                    op = ProposalOp.REPLACE,
                    proposedBody = "模型想整段换成别的。",
                    basedOnSectionRevision = 1,
                ),
            ),
        )
        val result = merger.merge(
            base, base, proposal,
            mapOf("i1" to ItemDecision(ProposalDecision.REJECT)),
            "rev-2",
        )
        assertEquals("我认为重点是甲。", result.snapshot.section("s-me")!!.body)
        assertTrue(result.outcomes.single() is ItemOutcome.Rejected)
    }

    @Test
    fun userEditDuringComputeBecomesConflict() {
        val current = base.copy(
            revision = 2,
            revisionId = "rev-1b",
            sections = listOf(
                base.sections[0],
                base.sections[1].copy(body = "我已经改成自己的新理解。", revision = 2),
            ),
        )
        val proposal = ChangeProposal(
            proposalId = "p1",
            baseRevisionId = "rev-1",
            items = listOf(
                ChangeProposalItem(
                    itemId = "i1",
                    sectionId = "s-me",
                    op = ProposalOp.REPLACE,
                    proposedBody = "过期建议。",
                    basedOnSectionRevision = 1,
                ),
            ),
        )
        val result = merger.merge(
            base, current, proposal,
            mapOf("i1" to ItemDecision(ProposalDecision.ACCEPT)),
            "rev-3",
        )
        assertTrue(result.hasConflicts)
        assertEquals("我已经改成自己的新理解。", result.snapshot.section("s-me")!!.body)
        assertEquals("过期建议。", result.conflicts.single().proposedBody)
    }

    @Test
    fun acceptEditedWritesUserSuppliedBody() {
        val proposal = ChangeProposal(
            proposalId = "p1",
            baseRevisionId = "rev-1",
            items = listOf(
                ChangeProposalItem(
                    itemId = "i1",
                    sectionId = "s-me",
                    op = ProposalOp.REPLACE,
                    proposedBody = "模型稿。",
                    basedOnSectionRevision = 1,
                ),
            ),
        )
        val result = merger.merge(
            base, base, proposal,
            mapOf(
                "i1" to ItemDecision(
                    ProposalDecision.ACCEPT_EDITED,
                    editedBody = "我改后接受的稿。",
                ),
            ),
            "rev-2",
        )
        assertEquals("我改后接受的稿。", result.snapshot.section("s-me")!!.body)
    }

    @Test
    fun insertDoesNotRewriteExistingSections() {
        val proposal = ChangeProposal(
            proposalId = "p1",
            baseRevisionId = "rev-1",
            items = listOf(
                ChangeProposalItem(
                    itemId = "i2",
                    sectionId = "s-new",
                    op = ProposalOp.INSERT,
                    proposedTitle = "待探索",
                    proposedBody = "还想查这个典故。",
                    insertAfterSectionId = "s-me",
                    basedOnSectionRevision = 1,
                ),
            ),
        )
        val result = merger.merge(
            base, base, proposal,
            mapOf("i2" to ItemDecision(ProposalDecision.ACCEPT)),
            "rev-2",
        )
        assertEquals(listOf("s-essence", "s-me", "s-new"), result.snapshot.sections.map { it.sectionId })
        assertEquals("我认为重点是甲。", result.snapshot.section("s-me")!!.body)
    }

    @Test
    fun userLockedSectionNeverOverwritten() {
        val locked = base.copy(
            sections = listOf(
                base.sections[0],
                base.sections[1].copy(userLocked = true),
            ),
        )
        val proposal = ChangeProposal(
            proposalId = "p1",
            baseRevisionId = "rev-1",
            items = listOf(
                ChangeProposalItem(
                    itemId = "i1",
                    sectionId = "s-me",
                    op = ProposalOp.REPLACE,
                    proposedBody = "不该写进去",
                    basedOnSectionRevision = 1,
                ),
            ),
        )
        val result = merger.merge(
            base, locked, proposal,
            mapOf("i1" to ItemDecision(ProposalDecision.ACCEPT)),
            "rev-2",
        )
        assertTrue(result.hasConflicts)
        assertEquals("我认为重点是甲。", result.snapshot.section("s-me")!!.body)
    }
}

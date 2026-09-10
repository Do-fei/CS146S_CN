package com.onepaper.domain.recook

/**
 * 三路合并：baseRevision + proposedItems + currentRevision。
 * 禁止整份重写。用户在计算期间的编辑优先，冲突回到审阅。
 */
class RecookMerger {

    fun merge(
        base: ProjectSnapshot,
        current: ProjectSnapshot,
        proposal: ChangeProposal,
        decisions: Map<String, ItemDecision>,
        nextRevisionId: String,
    ): MergeResult {
        require(proposal.baseRevisionId == base.revisionId) {
            "proposal must attach to baseRevision"
        }
        val sections = current.sections.associateBy { it.sectionId }.toMutableMap()
        val order = current.sections.map { it.sectionId }.toMutableList()
        val outcomes = mutableListOf<ItemOutcome>()

        for (item in proposal.items) {
            val decision = decisions[item.itemId] ?: ItemDecision(ProposalDecision.REJECT)
            when (decision.decision) {
                ProposalDecision.REJECT -> {
                    outcomes += ItemOutcome.Rejected(item.sectionId)
                }
                ProposalDecision.ACCEPT, ProposalDecision.ACCEPT_EDITED -> {
                    outcomes += applyItem(base, current, item, decision, sections, order)
                }
            }
        }

        val nextRev = current.revision + 1
        val next = ProjectSnapshot(
            revisionId = nextRevisionId,
            revision = nextRev,
            sections = order.mapNotNull { id ->
                sections[id]?.copy(revision = if (touched(outcomes, id)) nextRev else sections[id]!!.revision)
            },
        )
        return MergeResult(next, outcomes)
    }

    private fun touched(outcomes: List<ItemOutcome>, sectionId: String): Boolean =
        outcomes.any { it is ItemOutcome.Applied && it.sectionId == sectionId }

    private fun applyItem(
        base: ProjectSnapshot,
        current: ProjectSnapshot,
        item: ChangeProposalItem,
        decision: ItemDecision,
        sections: MutableMap<String, ProjectSection>,
        order: MutableList<String>,
    ): ItemOutcome {
        if (item.op == ProposalOp.NOOP) {
            return ItemOutcome.Applied(item.sectionId)
        }
        val body = when (decision.decision) {
            ProposalDecision.ACCEPT_EDITED -> decision.editedBody
                ?: return ItemOutcome.Invalid(item.sectionId, "edited body required")
            else -> item.proposedBody
        }
        val title = when (decision.decision) {
            ProposalDecision.ACCEPT_EDITED -> decision.editedTitle ?: item.proposedTitle
            else -> item.proposedTitle
        }

        return when (item.op) {
            ProposalOp.REPLACE -> replace(base, current, item, body, title, sections)
            ProposalOp.INSERT -> insert(item, body, title, sections, order)
            ProposalOp.NOOP -> ItemOutcome.Applied(item.sectionId)
        }
    }

    private fun replace(
        base: ProjectSnapshot,
        current: ProjectSnapshot,
        item: ChangeProposalItem,
        body: String?,
        title: String?,
        sections: MutableMap<String, ProjectSection>,
    ): ItemOutcome {
        val currentSection = current.section(item.sectionId)
            ?: return ItemOutcome.Invalid(item.sectionId, "section missing in current")
        if (currentSection.userLocked) {
            return ItemOutcome.Conflict(
                sectionId = item.sectionId,
                reason = "userLocked",
                currentBody = currentSection.body,
                proposedBody = body,
            )
        }
        val baseSection = base.section(item.sectionId)
        val userEditedSinceBase = baseSection != null && currentSection.body != baseSection.body
        val revisionMoved = currentSection.revision != item.basedOnSectionRevision
        if (userEditedSinceBase || revisionMoved) {
            return ItemOutcome.Conflict(
                sectionId = item.sectionId,
                reason = "user edited since base; will not overwrite",
                currentBody = currentSection.body,
                proposedBody = body,
            )
        }
        if (body == null) {
            return ItemOutcome.Invalid(item.sectionId, "replace requires body")
        }
        sections[item.sectionId] = currentSection.copy(
            body = body,
            title = title ?: currentSection.title,
        )
        return ItemOutcome.Applied(item.sectionId)
    }

    private fun insert(
        item: ChangeProposalItem,
        body: String?,
        title: String?,
        sections: MutableMap<String, ProjectSection>,
        order: MutableList<String>,
    ): ItemOutcome {
        if (sections.containsKey(item.sectionId)) {
            return ItemOutcome.Invalid(item.sectionId, "insert id already exists")
        }
        if (body == null) {
            return ItemOutcome.Invalid(item.sectionId, "insert requires body")
        }
        val created = ProjectSection(
            sectionId = item.sectionId,
            kind = SectionKind.EXPLORE,
            title = title ?: "",
            body = body,
            revision = item.basedOnSectionRevision + 1,
            userLocked = false,
        )
        sections[item.sectionId] = created
        val after = item.insertAfterSectionId
        val idx = if (after == null) order.size else order.indexOf(after).let { if (it < 0) order.size else it + 1 }
        order.add(idx, item.sectionId)
        return ItemOutcome.Applied(item.sectionId)
    }
}

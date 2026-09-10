package com.onepaper.domain.recook

enum class SectionKind {
    ESSENCE,
    CHAPTER,
    EXCERPT,
    UNDERSTANDING,
    EXPLORE,
    CHANGELOG,
}

enum class ProposalOp {
    INSERT,
    REPLACE,
    NOOP,
}

enum class ProposalDecision {
    ACCEPT,
    REJECT,
    ACCEPT_EDITED,
}

data class ProjectSection(
    val sectionId: String,
    val kind: SectionKind,
    val title: String,
    val body: String,
    val revision: Long,
    val userLocked: Boolean = false,
)

data class ProjectSnapshot(
    val revisionId: String,
    val revision: Long,
    val sections: List<ProjectSection>,
) {
    fun section(id: String): ProjectSection? = sections.firstOrNull { it.sectionId == id }
}

data class ChangeProposalItem(
    val itemId: String,
    val sectionId: String,
    val op: ProposalOp,
    val proposedTitle: String? = null,
    val proposedBody: String? = null,
    val insertAfterSectionId: String? = null,
    val basedOnSectionRevision: Long,
)

data class ChangeProposal(
    val proposalId: String,
    val baseRevisionId: String,
    val items: List<ChangeProposalItem>,
)

data class ItemDecision(
    val decision: ProposalDecision,
    val editedBody: String? = null,
    val editedTitle: String? = null,
)

sealed class ItemOutcome {
    data class Applied(val sectionId: String) : ItemOutcome()
    data class Rejected(val sectionId: String) : ItemOutcome()
    data class Conflict(
        val sectionId: String,
        val reason: String,
        val currentBody: String,
        val proposedBody: String?,
    ) : ItemOutcome()

    data class Invalid(val sectionId: String, val reason: String) : ItemOutcome()
}

data class MergeResult(
    val snapshot: ProjectSnapshot,
    val outcomes: List<ItemOutcome>,
) {
    val conflicts: List<ItemOutcome.Conflict> = outcomes.filterIsInstance<ItemOutcome.Conflict>()
    val hasConflicts: Boolean get() = conflicts.isNotEmpty()
}

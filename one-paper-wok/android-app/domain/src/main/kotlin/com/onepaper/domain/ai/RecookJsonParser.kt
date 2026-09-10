package com.onepaper.domain.ai

import com.onepaper.domain.recook.ChangeProposal
import com.onepaper.domain.recook.ChangeProposalItem
import com.onepaper.domain.recook.ProjectSnapshot
import com.onepaper.domain.recook.ProposalOp
import kotlinx.serialization.Serializable
import kotlinx.serialization.json.Json

@Serializable
data class RecookLlmPayload(
    val items: List<RecookLlmItem> = emptyList(),
)

@Serializable
data class RecookLlmItem(
    val sectionId: String,
    val op: String,
    val proposedTitle: String? = null,
    val proposedBody: String? = null,
    val insertAfterSectionId: String? = null,
)

object RecookJsonParser {
    private val json = Json { ignoreUnknownKeys = true }

    fun parse(raw: String, base: ProjectSnapshot): ChangeProposal {
        val cleaned = raw.trim()
            .removePrefix("```json")
            .removePrefix("```")
            .removeSuffix("```")
            .trim()
        val payload = json.decodeFromString<RecookLlmPayload>(cleaned)
        val known = base.sections.map { it.sectionId }.toSet()
        val items = payload.items.mapNotNull { item ->
            val op = runCatching { ProposalOp.valueOf(item.op.uppercase()) }.getOrNull()
                ?: return@mapNotNull null
            if (op == ProposalOp.REPLACE && item.sectionId !in known) return@mapNotNull null
            if (op == ProposalOp.REPLACE && item.proposedBody.isNullOrBlank()) return@mapNotNull null
            if (op == ProposalOp.INSERT && item.proposedBody.isNullOrBlank()) return@mapNotNull null
            val baseRev = base.section(item.sectionId)?.revision ?: base.revision
            ChangeProposalItem(
                itemId = "item-${item.sectionId}-${op.name.lowercase()}",
                sectionId = item.sectionId,
                op = op,
                proposedTitle = item.proposedTitle,
                proposedBody = item.proposedBody,
                insertAfterSectionId = item.insertAfterSectionId,
                basedOnSectionRevision = baseRev,
            )
        }
        require(items.isNotEmpty()) { "no valid recook items" }
        return ChangeProposal(
            proposalId = "proposal-${base.revisionId}",
            baseRevisionId = base.revisionId,
            items = items,
        )
    }
}

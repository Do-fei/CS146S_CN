package com.onepaper.domain.ai

import com.onepaper.domain.citation.Citation
import com.onepaper.domain.recook.ChangeProposal
import com.onepaper.domain.recook.ChangeProposalItem
import com.onepaper.domain.recook.ProjectSnapshot
import com.onepaper.domain.recook.ProposalOp
import com.onepaper.domain.recook.SectionKind

data class ScopeBar(
    val importedChapterCount: Int,
    val importedPageCount: Int,
    val claimsWholeBook: Boolean,
) {
    init {
        require(!claimsWholeBook || importedChapterCount > 0)
    }
}

data class CompanionRequest(
    val bookId: String,
    val question: String,
    val scope: ScopeBar,
    val evidence: List<Citation>,
)

data class CompanionAnswer(
    val text: String,
    val citations: List<Citation>,
    val insufficientEvidence: Boolean,
    val refusedWholeBookConclusion: Boolean,
)

interface AiProvider {
    suspend fun answer(request: CompanionRequest): CompanionAnswer
    suspend fun proposeRecook(base: ProjectSnapshot, userNotes: List<String>): ChangeProposal
}

class FakeAiProvider : AiProvider {
    override suspend fun answer(request: CompanionRequest): CompanionAnswer {
        if (request.scope.importedChapterCount <= 0 && request.scope.importedPageCount <= 0) {
            return CompanionAnswer(
                text = "还没有导入可读范围，不能假装读过这本书。",
                citations = emptyList(),
                insufficientEvidence = true,
                refusedWholeBookConclusion = true,
            )
        }
        if (looksLikeWholeBook(request.question) && !request.scope.claimsWholeBook) {
            return CompanionAnswer(
                text = "目前只导入了部分章节/页，不能给出全书结论。请把问题限制在已导入范围内，或继续导入。",
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
        val quote = request.evidence.first().quote
        return CompanionAnswer(
            text = "就已导入范围来看：「$quote」——这是依据引用的解释，不是全书结论。",
            citations = request.evidence,
            insufficientEvidence = false,
            refusedWholeBookConclusion = false,
        )
    }

    override suspend fun proposeRecook(base: ProjectSnapshot, userNotes: List<String>): ChangeProposal {
        val understand = base.sections.firstOrNull { it.kind == SectionKind.UNDERSTANDING }
            ?: base.sections.first()
        val noteBlob = userNotes.joinToString("；").ifBlank { "用户补充了一则思考" }
        val item = ChangeProposalItem(
            itemId = "item-${understand.sectionId}",
            sectionId = understand.sectionId,
            op = ProposalOp.REPLACE,
            proposedTitle = understand.title,
            proposedBody = understand.body + "\n\n（建议增补，待审阅）$noteBlob",
            basedOnSectionRevision = understand.revision,
        )
        return ChangeProposal(
            proposalId = "proposal-${base.revisionId}",
            baseRevisionId = base.revisionId,
            items = listOf(item),
        )
    }

    private fun looksLikeWholeBook(question: String): Boolean {
        val keys = listOf("全书", "整本书", "总结这本书", "这本书讲了什么", "完整结论")
        return keys.any { question.contains(it) }
    }
}

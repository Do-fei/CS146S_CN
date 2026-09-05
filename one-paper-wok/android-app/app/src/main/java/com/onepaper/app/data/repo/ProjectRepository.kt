package com.onepaper.app.data.repo

import com.onepaper.app.data.local.ProjectDao
import com.onepaper.app.data.local.ProjectEntity
import com.onepaper.app.data.local.ProjectSectionEntity
import com.onepaper.app.data.local.ProposalDao
import com.onepaper.app.data.local.ProposalEntity
import com.onepaper.app.data.local.ProposalItemEntity
import com.onepaper.app.data.local.SectionDao
import com.onepaper.domain.ai.AiProvider
import com.onepaper.domain.recook.ChangeProposal
import com.onepaper.domain.recook.ChangeProposalItem
import com.onepaper.domain.recook.ItemDecision
import com.onepaper.domain.recook.ProjectSection
import com.onepaper.domain.recook.ProjectSnapshot
import com.onepaper.domain.recook.ProposalOp
import com.onepaper.domain.recook.RecookMerger
import com.onepaper.domain.recook.SectionKind
import kotlinx.coroutines.flow.Flow
import java.util.UUID
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class ProjectRepository @Inject constructor(
    private val projects: ProjectDao,
    private val sections: SectionDao,
    private val proposals: ProposalDao,
    private val merger: RecookMerger,
    private val ai: AiProvider,
) {
    fun observeProjects(): Flow<List<ProjectEntity>> = projects.observeAll()
    fun observeSections(projectId: String) = sections.observeForProject(projectId)

    suspend fun project(id: String) = projects.get(id)
    suspend fun sectionsOf(projectId: String) = sections.forProject(projectId)
    suspend fun proposal(id: String) = proposals.get(id)
    suspend fun proposalItems(id: String) = proposals.items(id)
    suspend fun proposalsOf(projectId: String) = proposals.forProject(projectId)

    suspend fun ensureForBook(bookId: String, title: String, seedBody: String): ProjectEntity {
        projects.forBook(bookId)?.let { return it }
        val projectId = UUID.randomUUID().toString()
        val revisionId = "rev-1"
        val entity = ProjectEntity(projectId, bookId, title, revisionId, 1)
        projects.upsert(entity)
        sections.upsertAll(
            listOf(
                ProjectSectionEntity(UUID.randomUUID().toString(), projectId, "s-excerpt", SectionKind.EXCERPT.name, "原书", seedBody.take(280), 1, false, 0),
                ProjectSectionEntity(UUID.randomUUID().toString(), projectId, "s-essence", SectionKind.ESSENCE.name, "精华", "", 1, false, 1),
                ProjectSectionEntity(UUID.randomUUID().toString(), projectId, "s-me", SectionKind.UNDERSTANDING.name, "我的", "", 1, false, 2),
                ProjectSectionEntity(UUID.randomUUID().toString(), projectId, "s-explore", SectionKind.EXPLORE.name, "待探索", "", 1, false, 3),
                ProjectSectionEntity(UUID.randomUUID().toString(), projectId, "s-log", SectionKind.CHANGELOG.name, "更新记录", "", 1, false, 4),
            ),
        )
        return entity
    }

    suspend fun updateSection(projectId: String, sectionId: String, body: String, title: String? = null) {
        val current = sections.forProject(projectId)
        val next = current.map {
            if (it.sectionId != sectionId) it
            else it.copy(body = body, title = title ?: it.title, revision = it.revision + 1, userLocked = true)
        }
        val project = projects.get(projectId) ?: return
        projects.upsert(project.copy(revision = project.revision + 1, revisionId = "rev-${project.revision + 1}"))
        sections.deleteForProject(projectId)
        sections.upsertAll(next)
    }

    suspend fun regenerateSection(projectId: String, sectionId: String) {
        val current = sections.forProject(projectId)
        val target = current.firstOrNull { it.sectionId == sectionId } ?: return
        if (target.userLocked) return
        val next = current.map {
            if (it.sectionId != sectionId) it
            else it.copy(body = it.body, revision = it.revision + 1)
        }
        sections.deleteForProject(projectId)
        sections.upsertAll(next)
    }

    suspend fun createProposalFromNotes(projectId: String, notes: List<String>): String {
        val project = projects.get(projectId) ?: error("missing project")
        val snap = snapshot(projectId)
        val proposal = ai.proposeRecook(snap, notes)
        proposals.upsert(
            ProposalEntity(proposal.proposalId, projectId, project.revisionId, System.currentTimeMillis(), "open"),
        )
        proposal.items.forEach { item ->
            proposals.upsertItem(
                ProposalItemEntity(
                    id = item.itemId,
                    proposalId = proposal.proposalId,
                    sectionId = item.sectionId,
                    op = item.op.name,
                    proposedTitle = item.proposedTitle,
                    proposedBody = item.proposedBody,
                    basedOnSectionRevision = item.basedOnSectionRevision,
                    decision = null,
                    editedBody = null,
                ),
            )
        }
        return proposal.proposalId
    }

    suspend fun decide(proposalId: String, decisions: Map<String, ItemDecision>) {
        val proposalRow = proposals.get(proposalId) ?: return
        val itemRows = proposals.items(proposalId)
        val project = projects.get(proposalRow.projectId) ?: return
        val currentSections = sections.forProject(project.id)
        val base = ProjectSnapshot(
            revisionId = proposalRow.baseRevisionId,
            revision = project.revision,
            sections = currentSections.map { it.toDomain() }.map { section ->
                val item = itemRows.firstOrNull { it.sectionId == section.sectionId }
                if (item != null) section.copy(revision = item.basedOnSectionRevision) else section
            },
        )
        val current = ProjectSnapshot(
            revisionId = project.revisionId,
            revision = project.revision,
            sections = currentSections.map { it.toDomain() },
        )
        val change = ChangeProposal(
            proposalId = proposalId,
            baseRevisionId = proposalRow.baseRevisionId,
            items = itemRows.map {
                ChangeProposalItem(
                    itemId = it.id,
                    sectionId = it.sectionId,
                    op = ProposalOp.valueOf(it.op),
                    proposedTitle = it.proposedTitle,
                    proposedBody = it.proposedBody,
                    basedOnSectionRevision = it.basedOnSectionRevision,
                )
            },
        )
        val merged = merger.merge(base, current, change, decisions, "rev-${project.revision + 1}")
        projects.upsert(project.copy(revisionId = merged.snapshot.revisionId, revision = merged.snapshot.revision))
        sections.deleteForProject(project.id)
        sections.upsertAll(
            merged.snapshot.sections.mapIndexed { idx, section ->
                ProjectSectionEntity(
                    id = UUID.randomUUID().toString(),
                    projectId = project.id,
                    sectionId = section.sectionId,
                    kind = section.kind.name,
                    title = section.title,
                    body = section.body,
                    revision = section.revision,
                    userLocked = section.userLocked,
                    sortIndex = idx,
                )
            },
        )
        itemRows.forEach { row ->
            val d = decisions[row.id]
            proposals.upsertItem(row.copy(decision = d?.decision?.name, editedBody = d?.editedBody))
        }
        proposals.upsert(proposalRow.copy(status = if (merged.hasConflicts) "conflicts" else "applied"))
    }

    suspend fun snapshot(projectId: String): ProjectSnapshot {
        val project = projects.get(projectId) ?: error("missing")
        return ProjectSnapshot(
            revisionId = project.revisionId,
            revision = project.revision,
            sections = sections.forProject(projectId).map { it.toDomain() },
        )
    }

    private fun ProjectSectionEntity.toDomain() = ProjectSection(
        sectionId = sectionId,
        kind = SectionKind.valueOf(kind),
        title = title,
        body = body,
        revision = revision,
        userLocked = userLocked,
    )
}

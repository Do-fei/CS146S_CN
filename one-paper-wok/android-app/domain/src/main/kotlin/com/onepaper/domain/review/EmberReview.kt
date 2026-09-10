package com.onepaper.domain.review

import java.time.Instant
import java.time.ZoneId

/** 文火回看：划了要回看。不是 Anki，没有间隔算法。 */
data class EmberItem(
    val id: String,
    val kind: EmberKind,
    val title: String,
    val body: String,
    val createdAt: Long,
    val bookId: String? = null,
    val editionId: String? = null,
    val locatorJson: String? = null,
)

enum class EmberKind {
    HIGHLIGHT,
    DRAFT,
}

object EmberReview {
    const val DAILY_CAP = 12

    fun dayKey(nowMs: Long, zone: ZoneId = ZoneId.systemDefault()): String {
        return Instant.ofEpochMilli(nowMs).atZone(zone).toLocalDate().toString()
    }

    fun startOfDay(nowMs: Long, zone: ZoneId = ZoneId.systemDefault()): Long {
        return Instant.ofEpochMilli(nowMs)
            .atZone(zone)
            .toLocalDate()
            .atStartOfDay(zone)
            .toInstant()
            .toEpochMilli()
    }

    fun dueToday(
        items: List<EmberItem>,
        nowMs: Long,
        dismissedIds: Set<String>,
        cap: Int = DAILY_CAP,
        zone: ZoneId = ZoneId.systemDefault(),
    ): List<EmberItem> {
        val start = startOfDay(nowMs, zone)
        val highlightBodies = items
            .filter { it.kind == EmberKind.HIGHLIGHT }
            .map { it.body.trim() }
            .filter { it.isNotBlank() }
            .toSet()
        return items
            .filter { it.body.isNotBlank() }
            .filter { it.createdAt < start }
            .filter { it.id !in dismissedIds }
            .filterNot { it.kind == EmberKind.DRAFT && it.body.trim() in highlightBodies }
            .sortedBy { it.createdAt }
            .take(cap)
    }
}

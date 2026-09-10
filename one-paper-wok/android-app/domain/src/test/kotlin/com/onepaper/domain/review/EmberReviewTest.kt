package com.onepaper.domain.review

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test
import java.time.ZoneOffset

class EmberReviewTest {
    private val utc = ZoneOffset.UTC

    @Test
    fun sameDayMarksAreNotDue() {
        val now = 3L * 86_400_000L + 10_000L
        val item = EmberItem("a", EmberKind.HIGHLIGHT, "划", "把书读薄", createdAt = now - 1_000)
        val due = EmberReview.dueToday(listOf(item), now, emptySet(), zone = utc)
        assertTrue(due.isEmpty())
    }

    @Test
    fun yesterdayHighlightIsDueUntilDismissed() {
        val now = 3L * 86_400_000L + 10_000L
        val item = EmberItem("a", EmberKind.HIGHLIGHT, "划", "把书读薄", createdAt = now - 90_000_000L)
        val due = EmberReview.dueToday(listOf(item), now, emptySet(), zone = utc)
        assertEquals(listOf("a"), due.map { it.id })
        val dismissed = EmberReview.dueToday(listOf(item), now, setOf("a"), zone = utc)
        assertTrue(dismissed.isEmpty())
    }

    @Test
    fun capsAndKeepsOldestFirst() {
        val now = 5L * 86_400_000L
        val items = (0 until 20).map { idx ->
            EmberItem(
                id = "n$idx",
                kind = EmberKind.DRAFT,
                title = "稿",
                body = "正文$idx",
                createdAt = 1_000L + idx,
            )
        }
        val due = EmberReview.dueToday(items, now, emptySet(), cap = 3, zone = utc)
        assertEquals(listOf("n0", "n1", "n2"), due.map { it.id })
    }

    @Test
    fun usesLocalDayNotUtc() {
        val shanghai = java.time.ZoneId.of("Asia/Shanghai")
        val dayStart = java.time.LocalDate.of(2026, 9, 5)
            .atStartOfDay(shanghai)
            .toInstant()
            .toEpochMilli()
        val now = dayStart + 30 * 60_000L
        val yesterday = EmberItem("old", EmberKind.HIGHLIGHT, "划", "昨日句", createdAt = dayStart - 60_000L)
        val today = EmberItem("new", EmberKind.HIGHLIGHT, "划", "今日句", createdAt = dayStart + 10_000L)
        val due = EmberReview.dueToday(listOf(yesterday, today), now, emptySet(), zone = shanghai)
        assertEquals(listOf("old"), due.map { it.id })
        assertEquals("2026-09-05", EmberReview.dayKey(now, shanghai))
    }

    @Test
    fun dropsDraftThatOnlyRepeatsAHighlight() {
        val now = 5L * 86_400_000L
        val highlight = EmberItem("h", EmberKind.HIGHLIGHT, "划", "把书读薄", createdAt = 1_000L)
        val copy = EmberItem("n", EmberKind.DRAFT, "稿", "把书读薄", createdAt = 2_000L)
        val mine = EmberItem("m", EmberKind.DRAFT, "稿", "我只记下这一句。", createdAt = 3_000L)
        val due = EmberReview.dueToday(listOf(highlight, copy, mine), now, emptySet(), zone = utc)
        assertEquals(listOf("h", "m"), due.map { it.id })
    }
}

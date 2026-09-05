package com.onepaper.domain.layout

/** 折叠外屏：用最小宽度判断，不冒充真机已测。 */
object CoverLayout {
    const val COVER_SMALLEST_DP = 360
    const val COMPACT_WIDTH_DP = 400
    const val WIDE_WIDTH_DP = 600

    fun isCoverLike(smallestWidthDp: Int): Boolean = smallestWidthDp < COVER_SMALLEST_DP

    fun isCompact(widthDp: Int): Boolean = widthDp < COMPACT_WIDTH_DP

    fun isWide(widthDp: Int): Boolean = widthDp >= WIDE_WIDTH_DP
}

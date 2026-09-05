package com.onepaper.domain.search

/**
 * Android 自带 FTS5 对中文几乎无词。短查询用 n-gram + 精确子串。
 */
object ChineseNgram {
    fun tokens(text: String, n: Int = 3): Set<String> {
        val normalized = text.filter { !it.isWhitespace() }
        if (normalized.isEmpty()) return emptySet()
        if (normalized.length <= n) return setOf(normalized)
        return (0..normalized.length - n).map { i ->
            normalized.substring(i, i + n)
        }.toSet()
    }

    fun matches(haystack: String, query: String): Boolean {
        val q = query.trim()
        if (q.isEmpty()) return true
        if (haystack.contains(q)) return true
        if (q.length < 3) return haystack.contains(q)
        val qTokens = tokens(q)
        val hTokens = tokens(haystack)
        val hit = qTokens.count { it in hTokens }
        return hit * 2 >= qTokens.size
    }

    fun rank(haystack: String, query: String): Int {
        val q = query.trim()
        if (q.isEmpty()) return 0
        if (haystack.contains(q)) return 1_000 + q.length
        val qTokens = tokens(q)
        if (qTokens.isEmpty()) return 0
        val hTokens = tokens(haystack)
        return qTokens.count { it in hTokens }
    }
}

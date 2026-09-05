package com.onepaper.domain.citation

/**
 * 不依赖屏幕页码的回跳。改字号只改变排版，不改变 progression 与 quote。
 */
class LocatorResolver {

    fun resolveEpub(document: EpubDocument, locator: ContentLocator.Epub): ResolveResult {
        val chapter = document.chapterByHref(locator.href)
            ?: return ResolveResult.Missing("chapter ${locator.href} gone")
        if (chapter.contentVersion != document.contentVersion) {
            val shifted = chapter.findQuote(locator.quote)
            return if (shifted != null) {
                ResolveResult.Found(
                    href = chapter.href,
                    progression = shifted.progression,
                    quote = locator.quote.exact,
                    stale = chapter.contentVersion != document.contentVersion,
                )
            } else {
                ResolveResult.Stale("quote not found after content change")
            }
        }
        val byQuote = chapter.findQuote(locator.quote)
        if (byQuote != null) {
            return ResolveResult.Found(
                href = chapter.href,
                progression = byQuote.progression,
                quote = locator.quote.exact,
                stale = false,
            )
        }
        val clamped = locator.progression.coerceIn(0.0, 1.0)
        val approx = chapter.snippetAt(clamped)
        return ResolveResult.Found(
            href = chapter.href,
            progression = clamped,
            quote = approx,
            stale = true,
        )
    }

    fun mapImageQuad(
        quad: ContentLocator.ImageQuad,
        imageWidth: Int,
        imageHeight: Int,
    ): List<PixelPoint> {
        require(imageWidth > 0 && imageHeight > 0)
        return quad.points.map { p ->
            PixelPoint(
                x = (p.x.coerceIn(0.0, 1.0) * imageWidth).toInt(),
                y = (p.y.coerceIn(0.0, 1.0) * imageHeight).toInt(),
            )
        }
    }
}

data class PixelPoint(val x: Int, val y: Int)

sealed class ResolveResult {
    data class Found(
        val href: String,
        val progression: Double,
        val quote: String,
        val stale: Boolean,
    ) : ResolveResult()

    data class Stale(val reason: String) : ResolveResult()
    data class Missing(val reason: String) : ResolveResult()
}

data class EpubDocument(
    val contentVersion: String,
    val chapters: List<EpubChapter>,
) {
    fun chapterByHref(href: String): EpubChapter? = chapters.firstOrNull { it.href == href }
}

data class EpubChapter(
    val href: String,
    val contentVersion: String,
    val plainText: String,
) {
    fun findQuote(quote: TextQuote): QuoteHit? {
        val idx = plainText.indexOf(quote.exact)
        if (idx < 0 || plainText.isEmpty()) return null
        if (quote.prefix.isNotEmpty()) {
            val before = plainText.substring(0, idx)
            if (!before.endsWith(quote.prefix) && !before.contains(quote.prefix)) {
                // prefix is a hint, not a hard fail if exact exists once
                if (plainText.indexOf(quote.exact, idx + 1) >= 0) return null
            }
        }
        val progression = idx.toDouble() / plainText.length.toDouble()
        return QuoteHit(idx, progression)
    }

    fun snippetAt(progression: Double): String {
        if (plainText.isEmpty()) return ""
        val idx = (progression * (plainText.length - 1)).toInt().coerceIn(0, plainText.lastIndex)
        val end = (idx + 24).coerceAtMost(plainText.length)
        return plainText.substring(idx, end)
    }
}

data class QuoteHit(val charIndex: Int, val progression: Double)

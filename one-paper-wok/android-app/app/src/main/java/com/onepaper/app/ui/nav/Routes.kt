package com.onepaper.app.ui.nav

import android.net.Uri

object Routes {
    const val Onboarding = "onboarding"
    const val Home = "home"
    const val Book = "book/{bookId}"
    const val Reader = "reader/{editionId}?quote={quote}&href={href}&page={page}"
    const val Import = "import"
    const val Capture = "capture"
    const val Pages = "pages/{editionId}"
    const val Task = "task/{jobId}"
    const val Project = "project/{projectId}"
    const val Recook = "recook/{proposalId}"
    const val Companion = "companion/{bookId}?quote={quote}&locator={locator}&editionId={editionId}"
    const val Note = "note/{noteId}"
    const val Export = "export/{projectId}"
    const val Backup = "backup"
    const val Settings = "settings"
    const val Handwriting = "handwriting/{noteId}"

    fun book(id: String) = "book/$id"
    fun reader(
        id: String,
        quote: String = "",
        href: String? = null,
        page: Int? = null,
    ): String {
        val builder = Uri.Builder()
            .encodedPath("reader/$id")
            .appendQueryParameter("quote", quote.take(400))
            .appendQueryParameter("href", href.orEmpty())
            .appendQueryParameter("page", page?.toString().orEmpty())
        return builder.build().toString().trimStart('/')
    }
    fun pages(id: String) = "pages/$id"
    fun task(id: String) = "task/$id"
    fun project(id: String) = "project/$id"
    fun recook(id: String) = "recook/$id"
    fun companion(
        id: String,
        quote: String = "",
        locator: String = "",
        editionId: String = "",
    ): String {
        val builder = Uri.Builder()
            .encodedPath("companion/$id")
            .appendQueryParameter("quote", quote.take(400))
            .appendQueryParameter("locator", locator.take(1_200))
            .appendQueryParameter("editionId", editionId)
        return builder.build().toString().trimStart('/')
    }
    fun note(id: String) = "note/$id"
    fun export(id: String) = "export/$id"
    fun handwriting(id: String) = "handwriting/$id"
}

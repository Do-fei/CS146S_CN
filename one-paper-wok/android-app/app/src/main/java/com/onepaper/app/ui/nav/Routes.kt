package com.onepaper.app.ui.nav

object Routes {
    const val Onboarding = "onboarding"
    const val Home = "home"
    const val Book = "book/{bookId}"
    const val Reader = "reader/{editionId}"
    const val Import = "import"
    const val Capture = "capture"
    const val Pages = "pages/{editionId}"
    const val Task = "task/{jobId}"
    const val Project = "project/{projectId}"
    const val Recook = "recook/{proposalId}"
    const val Companion = "companion/{bookId}?quote={quote}"
    const val Note = "note/{noteId}"
    const val Export = "export/{projectId}"
    const val Backup = "backup"
    const val Settings = "settings"
    const val Handwriting = "handwriting/{noteId}"

    fun book(id: String) = "book/$id"
    fun reader(id: String) = "reader/$id"
    fun pages(id: String) = "pages/$id"
    fun task(id: String) = "task/$id"
    fun project(id: String) = "project/$id"
    fun recook(id: String) = "recook/$id"
    fun companion(id: String, quote: String = "") =
        "companion/$id?quote=${android.net.Uri.encode(quote.take(400))}"
    fun note(id: String) = "note/$id"
    fun export(id: String) = "export/$id"
    fun handwriting(id: String) = "handwriting/$id"
}

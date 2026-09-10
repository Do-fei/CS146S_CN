package com.onepaper.domain.paper

/** 出煲稿：像一张能发出去的纸，不是调试 JSON。 */
data class PaperDraftInput(
    val title: String,
    val sourceQuotes: List<String>,
    val aiSections: List<Pair<String, String>>,
    val userSections: List<Pair<String, String>>,
    val explore: String = "",
    val changelog: String = "",
    val privateNotes: List<String> = emptyList(),
)

object PaperShareDraft {
    fun markdown(input: PaperDraftInput): String = buildString {
        appendLine("# ${input.title.ifBlank { "一纸" }}")
        appendLine()
        appendLine("_一纸书煲 · 出煲_")
        appendLine()
        appendLayer(this, "原书", input.sourceQuotes.map { "「${it.trim()}」" })
        appendNamed(this, "AI", input.aiSections)
        appendNamed(this, "我的", input.userSections)
        if (input.explore.isNotBlank()) {
            appendLine("## 待探索")
            appendLine()
            appendLine(input.explore.trim())
            appendLine()
        }
        if (input.changelog.isNotBlank()) {
            appendLine("## 更新记录")
            appendLine()
            appendLine(input.changelog.trim())
            appendLine()
        }
        if (input.privateNotes.isNotEmpty()) {
            appendLine("## 私人笔记（仅这次勾选）")
            appendLine()
            input.privateNotes.forEach { appendLine("- ${it.trim()}") }
            appendLine()
        } else {
            appendLine("_公开稿未附私人批注。_")
            appendLine()
        }
    }.trim() + "\n"

    fun plain(input: PaperDraftInput): String = buildString {
        appendLine(input.title.ifBlank { "一纸" })
        appendLine("一纸书煲 · 出煲")
        appendLine()
        if (input.sourceQuotes.isNotEmpty()) {
            appendLine("【原书】")
            input.sourceQuotes.forEach { appendLine("「${it.trim()}」") }
            appendLine()
        }
        input.aiSections.filter { it.second.isNotBlank() }.forEach { (title, body) ->
            appendLine("【AI】$title")
            appendLine(body.trim())
            appendLine()
        }
        input.userSections.filter { it.second.isNotBlank() }.forEach { (title, body) ->
            appendLine("【我的】$title")
            appendLine(body.trim())
            appendLine()
        }
        if (input.explore.isNotBlank()) {
            appendLine("【待探索】")
            appendLine(input.explore.trim())
            appendLine()
        }
        if (input.changelog.isNotBlank()) {
            appendLine("【更新记录】")
            appendLine(input.changelog.trim())
            appendLine()
        }
        if (input.privateNotes.isNotEmpty()) {
            appendLine("【私人笔记】")
            input.privateNotes.forEach { appendLine(it.trim()) }
            appendLine()
        }
    }.trim() + "\n"

    private fun appendLayer(out: StringBuilder, name: String, lines: List<String>) {
        val usable = lines.filter { it.isNotBlank() && it != "「」" }
        if (usable.isEmpty()) return
        out.appendLine("## $name")
        out.appendLine()
        usable.forEach { out.appendLine("> $it") }
        out.appendLine()
    }

    private fun appendNamed(out: StringBuilder, layer: String, sections: List<Pair<String, String>>) {
        val usable = sections.filter { it.second.isNotBlank() }
        if (usable.isEmpty()) return
        usable.forEach { (title, body) ->
            out.appendLine("## $title")
            out.appendLine()
            out.appendLine("_层：${layer}_")
            out.appendLine()
            out.appendLine(body.trim())
            out.appendLine()
        }
    }
}

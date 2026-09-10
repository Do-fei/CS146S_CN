package com.onepaper.domain.backup

/** WebDAV 路径：无自建账号，只拼用户自己的盘。 */
object WebDavPath {
    const val DEFAULT_REMOTE = "/onepaper/onepaper-backup.zip"
    const val JIANGUO_HINT = "https://dav.jianguoyun.com/dav"

    fun requireHttps(url: String): String {
        val trimmed = url.trim()
        require(trimmed.startsWith("https://", ignoreCase = true)) { "只用 HTTPS，不走明文。" }
        return trimmed.trimEnd('/')
    }

    fun normalizePath(path: String): String {
        val trimmed = path.trim().ifBlank { DEFAULT_REMOTE }
        return if (trimmed.startsWith("/")) trimmed else "/$trimmed"
    }

    fun resolve(baseUrl: String, remotePath: String): String {
        val base = requireHttps(baseUrl)
        return base + normalizePath(remotePath)
    }

    fun parentCollection(fileUrl: String): String? {
        val trimmed = fileUrl.trim().trimEnd('/')
        val slash = trimmed.lastIndexOf('/')
        if (slash < 8) return null
        val parent = trimmed.substring(0, slash)
        return parent.takeIf { it.contains("://") && it.count { it == '/' } >= 3 }
    }
}

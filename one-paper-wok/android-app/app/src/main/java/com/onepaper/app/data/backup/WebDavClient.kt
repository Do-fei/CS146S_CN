package com.onepaper.app.data.backup

import com.onepaper.app.data.secure.SecretStore
import com.onepaper.domain.backup.WebDavPath
import okhttp3.Credentials
import okhttp3.MediaType.Companion.toMediaType
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.RequestBody.Companion.toRequestBody
import java.util.concurrent.TimeUnit
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class WebDavClient @Inject constructor(
    private val secrets: SecretStore,
) {
    private val http = OkHttpClient.Builder()
        .connectTimeout(20, TimeUnit.SECONDS)
        .readTimeout(60, TimeUnit.SECONDS)
        .writeTimeout(60, TimeUnit.SECONDS)
        .build()

    fun upload(bytes: ByteArray) {
        val target = targetUrl()
        ensureParent(target)
        val request = Request.Builder()
            .url(target)
            .header("Authorization", credential())
            .put(bytes.toRequestBody("application/json; charset=utf-8".toMediaType()))
            .build()
        http.newCall(request).execute().use { response ->
            if (!response.isSuccessful) {
                error("上传未成功（${response.code}）。请核对待办密码与路径。")
            }
        }
    }

    fun download(): ByteArray {
        val request = Request.Builder()
            .url(targetUrl())
            .header("Authorization", credential())
            .get()
            .build()
        http.newCall(request).execute().use { response ->
            if (response.code == 404) error("远端还没有备份文件。")
            if (!response.isSuccessful) error("下载未成功（${response.code}）。")
            return response.body?.bytes() ?: error("远端文件是空的。")
        }
    }

    private fun ensureParent(fileUrl: String) {
        val parent = WebDavPath.parentCollection(fileUrl)?.trimEnd('/')?.plus("/") ?: return
        val request = Request.Builder()
            .url(parent)
            .header("Authorization", credential())
            .method("MKCOL", ByteArray(0).toRequestBody(null))
            .build()
        http.newCall(request).execute().use { response ->
            if (response.code !in listOf(201, 405, 409, 301, 200)) {
                // 405/409：目录已在。其它失败不阻断，PUT 时再报。
                if (response.code >= 500) error("无法建立远端目录（${response.code}）。")
            }
        }
    }

    private fun targetUrl(): String {
        val base = secrets.webDavUrl() ?: error("还没有填写 WebDAV 地址。")
        val user = secrets.webDavUser()
        val pass = secrets.webDavPassword()
        if (user.isNullOrBlank() || pass.isNullOrBlank()) error("WebDAV 用户名和密码都要填。密码用应用专用密码，不是登录密码。")
        return WebDavPath.resolve(base, secrets.webDavPath())
    }

    private fun credential(): String {
        return Credentials.basic(secrets.webDavUser().orEmpty(), secrets.webDavPassword().orEmpty())
    }
}

package com.onepaper.app.data.files

import android.content.Context
import dagger.hilt.android.qualifiers.ApplicationContext
import java.io.File
import java.io.InputStream
import java.security.MessageDigest
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class PrivateStore @Inject constructor(
    @ApplicationContext private val context: Context,
) {
    private val root: File = File(context.filesDir, "library").apply { mkdirs() }
    private val exports: File = File(context.cacheDir, "exports").apply { mkdirs() }
    private val captures: File = File(context.cacheDir, "captures").apply { mkdirs() }

    fun editionDir(editionId: String): File = File(root, editionId).apply { mkdirs() }

    fun copyIncoming(editionId: String, name: String, input: InputStream): File {
        val dest = File(editionDir(editionId), name)
        input.use { src -> dest.outputStream().use { src.copyTo(it) } }
        return dest
    }

    fun writeText(editionId: String, name: String, text: String): File {
        val dest = File(editionDir(editionId), name)
        dest.writeText(text)
        return dest
    }

    fun filesDir(): File = context.filesDir

    fun file(relativePath: String): File = File(context.filesDir, relativePath)

    fun relative(file: File): String = file.relativeTo(context.filesDir).path

    fun exportFile(name: String): File = File(exports, name)

    fun captureFile(name: String): File = File(captures, name)

    fun sha256(file: File): String {
        val digest = MessageDigest.getInstance("SHA-256")
        file.inputStream().use { stream ->
            val buf = ByteArray(DEFAULT_BUFFER_SIZE)
            while (true) {
                val n = stream.read(buf)
                if (n <= 0) break
                digest.update(buf, 0, n)
            }
        }
        return digest.digest().joinToString("") { "%02x".format(it) }
    }

    fun usageBytes(): Long = root.walkTopDown().filter { it.isFile }.sumOf { it.length() }
}

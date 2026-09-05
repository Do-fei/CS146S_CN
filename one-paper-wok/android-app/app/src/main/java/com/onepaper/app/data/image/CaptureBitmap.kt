package com.onepaper.app.data.image

import android.content.Context
import android.graphics.Bitmap
import android.graphics.BitmapFactory
import android.graphics.Matrix
import android.net.Uri
import androidx.core.content.FileProvider
import com.onepaper.app.data.files.PrivateStore
import com.onepaper.domain.image.CropBox
import com.onepaper.domain.image.NormCrop
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class CaptureBitmap @Inject constructor(
    private val store: PrivateStore,
) {
    fun decode(context: Context, uri: Uri, maxEdge: Int = 2_048): Bitmap? {
        val bytes = context.contentResolver.openInputStream(uri)?.use { it.readBytes() } ?: return null
        val bounds = BitmapFactory.Options().apply { inJustDecodeBounds = true }
        BitmapFactory.decodeByteArray(bytes, 0, bytes.size, bounds)
        val longest = maxOf(bounds.outWidth, bounds.outHeight).coerceAtLeast(1)
        val sample = generateSequence(1) { it * 2 }.first { longest / it <= maxEdge }
        val opts = BitmapFactory.Options().apply { inSampleSize = sample }
        return BitmapFactory.decodeByteArray(bytes, 0, bytes.size, opts)
    }

    fun apply(source: Bitmap, box: CropBox, rotationDegrees: Int): Bitmap {
        val rotated = rotate(source, rotationDegrees)
        val px = NormCrop.toPixels(box, rotated.width, rotated.height)
        return Bitmap.createBitmap(rotated, px[0], px[1], px[2], px[3])
    }

    fun writeJpeg(context: Context, bitmap: Bitmap, name: String = "crop-${System.currentTimeMillis()}.jpg"): Uri {
        val file = store.captureFile(name)
        file.outputStream().use { out ->
            bitmap.compress(Bitmap.CompressFormat.JPEG, 88, out)
        }
        return FileProvider.getUriForFile(context, "${context.packageName}.files", file)
    }

    fun newCaptureUri(context: Context): Uri {
        val file = store.captureFile("cap-${System.currentTimeMillis()}.jpg")
        file.outputStream().use { /* placeholder so FileProvider can grant */ }
        return FileProvider.getUriForFile(context, "${context.packageName}.files", file)
    }

    private fun rotate(source: Bitmap, degrees: Int): Bitmap {
        val normalized = ((degrees % 360) + 360) % 360
        if (normalized == 0) return source
        val matrix = Matrix().apply { postRotate(normalized.toFloat()) }
        return Bitmap.createBitmap(source, 0, 0, source.width, source.height, matrix, true)
    }
}

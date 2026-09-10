package com.onepaper.app.data.ocr

import android.graphics.BitmapFactory
import com.google.mlkit.vision.common.InputImage
import com.google.mlkit.vision.text.TextRecognition
import com.google.mlkit.vision.text.chinese.ChineseTextRecognizerOptions
import com.onepaper.domain.citation.NormPoint
import com.onepaper.domain.ocr.OcrBox
import com.onepaper.domain.ocr.OcrEngine
import com.onepaper.domain.ocr.OcrKind
import com.onepaper.domain.ocr.OcrResult

class MlKitOcrEngine : OcrEngine {
    override val engineId: String = "mlkit-chinese-bundled"

    override suspend fun recognize(imagePng: ByteArray, kind: OcrKind): OcrResult {
        val bitmap = BitmapFactory.decodeByteArray(imagePng, 0, imagePng.size)
            ?: return OcrResult(kind, "", emptyList(), engineId, isAuthoritativeOriginal = false)
        val recognizer = TextRecognition.getClient(ChineseTextRecognizerOptions.Builder().build())
        return try {
            val text = recognizer.process(InputImage.fromBitmap(bitmap, 0)).await()
            val boxes = text.textBlocks.map { block ->
                val box = block.boundingBox
                val points = if (box != null) {
                    listOf(
                        NormPoint(box.left.toDouble() / bitmap.width, box.top.toDouble() / bitmap.height),
                        NormPoint(box.right.toDouble() / bitmap.width, box.top.toDouble() / bitmap.height),
                        NormPoint(box.right.toDouble() / bitmap.width, box.bottom.toDouble() / bitmap.height),
                        NormPoint(box.left.toDouble() / bitmap.width, box.bottom.toDouble() / bitmap.height),
                    )
                } else {
                    emptyList()
                }
                OcrBox(points = points, text = block.text, confidence = 0.8f)
            }
            OcrResult(
                kind = kind,
                fullText = text.text,
                boxes = boxes,
                engineId = engineId,
                isAuthoritativeOriginal = false,
            )
        } finally {
            recognizer.close()
        }
    }
}

package com.onepaper.domain.ocr

import com.onepaper.domain.citation.NormPoint

enum class OcrKind {
    PRINT,
    HANDWRITING,
}

data class OcrBox(
    val points: List<NormPoint>,
    val text: String,
    val confidence: Float,
)

data class OcrResult(
    val kind: OcrKind,
    val fullText: String,
    val boxes: List<OcrBox>,
    val engineId: String,
    val isAuthoritativeOriginal: Boolean = false,
)

interface OcrEngine {
    val engineId: String
    suspend fun recognize(imagePng: ByteArray, kind: OcrKind): OcrResult
}

/** 印刷体结果不得承诺手写。手写稿必须与原图并存，供用户校对。 */
class FakeOcrEngine(
    private val scripted: Map<String, OcrResult> = emptyMap(),
) : OcrEngine {
    override val engineId: String = "fake-ocr"

    override suspend fun recognize(imagePng: ByteArray, kind: OcrKind): OcrResult {
        val key = imagePng.decodeToString()
        scripted[key]?.let { return it.copy(kind = kind, isAuthoritativeOriginal = false) }
        val sample = if (kind == OcrKind.HANDWRITING) "（手写识别稿，待校对）" else "（印刷体识别稿）"
        return OcrResult(
            kind = kind,
            fullText = sample,
            boxes = listOf(
                OcrBox(
                    points = listOf(
                        NormPoint(0.1, 0.1),
                        NormPoint(0.9, 0.1),
                        NormPoint(0.9, 0.2),
                        NormPoint(0.1, 0.2),
                    ),
                    text = sample,
                    confidence = 0.4f,
                ),
            ),
            engineId = engineId,
            isAuthoritativeOriginal = false,
        )
    }
}

object OcrGeometry {
    fun boxToPixels(box: OcrBox, width: Int, height: Int): List<Pair<Int, Int>> {
        require(width > 0 && height > 0)
        return box.points.map { p ->
            (p.x.coerceIn(0.0, 1.0) * width).toInt() to
                (p.y.coerceIn(0.0, 1.0) * height).toInt()
        }
    }
}

package com.onepaper.domain.image

/** 归一化裁切框，0..1，与位图尺寸无关。 */
data class CropBox(
    val left: Double,
    val top: Double,
    val right: Double,
    val bottom: Double,
) {
    init {
        require(left in 0.0..1.0 && top in 0.0..1.0 && right in 0.0..1.0 && bottom in 0.0..1.0)
        require(right > left && bottom > top)
    }
}

object NormCrop {
    fun clamp(left: Double, top: Double, right: Double, bottom: Double): CropBox {
        val l = left.coerceIn(0.0, 0.95)
        val t = top.coerceIn(0.0, 0.95)
        val r = right.coerceIn(l + 0.05, 1.0)
        val b = bottom.coerceIn(t + 0.05, 1.0)
        return CropBox(l, t, r, b)
    }

    fun toPixels(box: CropBox, width: Int, height: Int): IntArray {
        val x = (box.left * width).toInt().coerceIn(0, width - 1)
        val y = (box.top * height).toInt().coerceIn(0, height - 1)
        val w = ((box.right - box.left) * width).toInt().coerceAtLeast(1).coerceAtMost(width - x)
        val h = ((box.bottom - box.top) * height).toInt().coerceAtLeast(1).coerceAtMost(height - y)
        return intArrayOf(x, y, w, h)
    }

    fun rotateClockwise(degrees: Int): Int {
        val normalized = ((degrees % 360) + 360) % 360
        return (normalized + 90) % 360
    }
}

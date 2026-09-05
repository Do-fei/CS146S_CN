package com.onepaper.domain.image

import org.junit.Assert.assertArrayEquals
import org.junit.Assert.assertEquals
import org.junit.Test

class NormCropTest {
    @Test
    fun clampKeepsMinimumBox() {
        val box = NormCrop.clamp(0.8, 0.8, 0.81, 0.81)
        assertEquals(0.8, box.left, 0.0001)
        assertEquals(0.85, box.right, 0.0001)
        assertEquals(0.8, box.top, 0.0001)
        assertEquals(0.85, box.bottom, 0.0001)
    }

    @Test
    fun pixelsMatchNormalizedBox() {
        val box = NormCrop.clamp(0.25, 0.0, 0.75, 0.5)
        val px = NormCrop.toPixels(box, 200, 100)
        assertArrayEquals(intArrayOf(50, 0, 100, 50), px)
    }

    @Test
    fun rotateClockwiseWraps() {
        assertEquals(90, NormCrop.rotateClockwise(0))
        assertEquals(0, NormCrop.rotateClockwise(270))
    }
}

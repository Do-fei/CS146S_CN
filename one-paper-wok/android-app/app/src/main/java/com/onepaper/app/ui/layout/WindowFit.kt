package com.onepaper.app.ui.layout

import androidx.compose.runtime.Composable
import androidx.compose.runtime.compositionLocalOf
import androidx.compose.runtime.remember
import androidx.compose.ui.platform.LocalConfiguration
import androidx.compose.ui.unit.Dp
import androidx.compose.ui.unit.dp
import com.onepaper.domain.layout.CoverLayout

data class WindowFit(
    val widthDp: Int,
    val heightDp: Int,
    val smallestWidthDp: Int,
) {
    val coverLike: Boolean get() = CoverLayout.isCoverLike(smallestWidthDp)
    val compact: Boolean get() = CoverLayout.isCompact(widthDp) || coverLike
    val wide: Boolean get() = CoverLayout.isWide(widthDp)
    val pagePad: Dp get() = if (coverLike) 10.dp else 16.dp
    val coverW: Dp get() = if (coverLike) 40.dp else 56.dp
    val coverH: Dp get() = if (coverLike) 60.dp else 84.dp
}

val LocalWindowFit = compositionLocalOf { WindowFit(411, 891, 411) }

@Composable
fun rememberWindowFit(): WindowFit {
    val configuration = LocalConfiguration.current
    return remember(configuration.screenWidthDp, configuration.screenHeightDp, configuration.smallestScreenWidthDp) {
        WindowFit(
            widthDp = configuration.screenWidthDp,
            heightDp = configuration.screenHeightDp,
            smallestWidthDp = configuration.smallestScreenWidthDp,
        )
    }
}

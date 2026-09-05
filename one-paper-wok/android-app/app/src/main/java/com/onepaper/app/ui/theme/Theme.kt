package com.onepaper.app.ui.theme

import android.app.Activity
import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Typography
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.runtime.SideEffect
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.graphics.toArgb
import androidx.compose.ui.platform.LocalView
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.ui.unit.dp
import androidx.compose.ui.unit.sp
import androidx.compose.foundation.shape.RoundedCornerShape
import androidx.compose.material3.Shapes
import androidx.core.view.WindowCompat

/** 和纸。主底，不是纯白。 */
val Paper = Color(0xFFF7F3EA)
val PaperDeep = Color(0xFFF1EBE0)

/** 墨。正文与主操作线。 */
val Ink = Color(0xFF2C2925)
val InkSoft = Color(0xFF6E6860)

/** 雾与细线。分割，不是阴影。 */
val Mist = Color(0xFFE6DFD2)
val Line = Color(0xFFB8AFA3)

/** 朱印。只作点、层标、选中，不作大色块按钮。 */
val Seal = Color(0xFFC45C4A)

val SourceGreen = Color(0xFF5B6B4E)
val AiPurple = Color(0xFF6A5B8A)

val Night = Color(0xFF161411)
val NightPaper = Color(0xFFEDE6DA)
val NightMist = Color(0xFF2A2621)
val NightLine = Color(0xFF5C564C)

private val Serif = FontFamily.Serif
private val Sans = FontFamily.SansSerif

val OnePaperTypography = Typography(
    displaySmall = TextStyle(
        fontFamily = Serif,
        fontWeight = FontWeight.Normal,
        fontSize = 32.sp,
        lineHeight = 40.sp,
        letterSpacing = 0.4.sp,
    ),
    headlineSmall = TextStyle(
        fontFamily = Serif,
        fontWeight = FontWeight.Normal,
        fontSize = 26.sp,
        lineHeight = 34.sp,
        letterSpacing = 0.4.sp,
    ),
    titleLarge = TextStyle(
        fontFamily = Serif,
        fontWeight = FontWeight.Medium,
        fontSize = 20.sp,
        lineHeight = 28.sp,
        letterSpacing = 0.25.sp,
    ),
    titleMedium = TextStyle(
        fontFamily = Serif,
        fontWeight = FontWeight.Medium,
        fontSize = 17.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.2.sp,
    ),
    titleSmall = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.3.sp,
    ),
    bodyLarge = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Normal,
        fontSize = 16.sp,
        lineHeight = 26.sp,
        letterSpacing = 0.05.sp,
    ),
    bodyMedium = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Normal,
        fontSize = 15.sp,
        lineHeight = 24.sp,
        letterSpacing = 0.05.sp,
    ),
    bodySmall = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Normal,
        fontSize = 13.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.1.sp,
    ),
    labelLarge = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Medium,
        fontSize = 14.sp,
        lineHeight = 20.sp,
        letterSpacing = 0.5.sp,
    ),
    labelMedium = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Medium,
        fontSize = 12.sp,
        lineHeight = 16.sp,
        letterSpacing = 0.7.sp,
    ),
    labelSmall = TextStyle(
        fontFamily = Sans,
        fontWeight = FontWeight.Medium,
        fontSize = 11.sp,
        lineHeight = 14.sp,
        letterSpacing = 1.4.sp,
    ),
)

val OnePaperShapes = Shapes(
    extraSmall = RoundedCornerShape(2.dp),
    small = RoundedCornerShape(2.dp),
    medium = RoundedCornerShape(2.dp),
    large = RoundedCornerShape(2.dp),
    extraLarge = RoundedCornerShape(4.dp),
)

private val LightColors = lightColorScheme(
    primary = Ink,
    onPrimary = Paper,
    secondary = InkSoft,
    onSecondary = Paper,
    tertiary = Seal,
    onTertiary = Paper,
    background = Paper,
    onBackground = Ink,
    surface = Paper,
    onSurface = Ink,
    surfaceVariant = PaperDeep,
    onSurfaceVariant = InkSoft,
    outline = Line,
    outlineVariant = Mist,
    error = Seal,
    onError = Paper,
    primaryContainer = Mist,
    onPrimaryContainer = Ink,
    secondaryContainer = PaperDeep,
    onSecondaryContainer = Ink,
)

private val DarkColors = darkColorScheme(
    primary = NightPaper,
    onPrimary = Night,
    secondary = Color(0xFFB7AFA4),
    onSecondary = Night,
    tertiary = Color(0xFFD47860),
    onTertiary = Night,
    background = Night,
    onBackground = NightPaper,
    surface = Night,
    onSurface = NightPaper,
    surfaceVariant = NightMist,
    onSurfaceVariant = Color(0xFFB7AFA4),
    outline = NightLine,
    outlineVariant = NightMist,
    error = Color(0xFFD47860),
    onError = Night,
    primaryContainer = NightMist,
    onPrimaryContainer = NightPaper,
)

@Composable
fun OnePaperTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    val scheme = if (darkTheme) DarkColors else LightColors
    val view = LocalView.current
    if (!view.isInEditMode) {
        SideEffect {
            val window = (view.context as Activity).window
            window.statusBarColor = android.graphics.Color.TRANSPARENT
            window.navigationBarColor = scheme.background.toArgb()
            WindowCompat.getInsetsController(window, view).apply {
                isAppearanceLightStatusBars = !darkTheme
                isAppearanceLightNavigationBars = !darkTheme
            }
        }
    }
    MaterialTheme(
        colorScheme = scheme,
        typography = OnePaperTypography,
        shapes = OnePaperShapes,
        content = content,
    )
}

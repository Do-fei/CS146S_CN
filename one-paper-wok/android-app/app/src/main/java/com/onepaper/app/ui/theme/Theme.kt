package com.onepaper.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color

val Paper = Color(0xFFFAF7F1)
val Clay = Color(0xFFBD593B)
val Ink = Color(0xFF302D29)
val Mist = Color(0xFFE8E2D6)
val SourceGreen = Color(0xFF5B6B4E)
val AiPurple = Color(0xFF6A5B8A)

private val LightColors = lightColorScheme(
    primary = Clay,
    onPrimary = Color.White,
    secondary = SourceGreen,
    onSecondary = Color.White,
    tertiary = AiPurple,
    background = Paper,
    onBackground = Ink,
    surface = Paper,
    onSurface = Ink,
    surfaceVariant = Mist,
    onSurfaceVariant = Ink,
    outline = Color(0xFFB7AFA4),
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFFE08A6A),
    onPrimary = Ink,
    secondary = Color(0xFFB7C7A8),
    background = Color(0xFF1C1A17),
    onBackground = Paper,
    surface = Color(0xFF1C1A17),
    onSurface = Paper,
)

@Composable
fun OnePaperTheme(
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit,
) {
    MaterialTheme(
        colorScheme = if (darkTheme) DarkColors else LightColors,
        content = content,
    )
}

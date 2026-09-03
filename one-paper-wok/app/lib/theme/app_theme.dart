import 'package:flutter/material.dart';

class WokColors {
  static const orange = Color(0xFFE8734A);
  static const orangeSoft = Color(0xFFF4A261);
  static const cream = Color(0xFFFFF8F0);
  static const card = Color(0xFFFFFFFF);
  static const ink = Color(0xFF2D2D2D);
  static const muted = Color(0xFF888888);
  static const blue = Color(0xFF4A90D9);
  static const purple = Color(0xFF8B6FD4);
  static const green = Color(0xFF2D9D5C);
}

ThemeData buildWokTheme() {
  final scheme = ColorScheme.fromSeed(
    seedColor: WokColors.orange,
    brightness: Brightness.light,
  ).copyWith(
    primary: WokColors.orange,
    surface: WokColors.cream,
  );
  return ThemeData(
    useMaterial3: true,
    colorScheme: scheme,
    scaffoldBackgroundColor: WokColors.cream,
    appBarTheme: const AppBarTheme(
      backgroundColor: WokColors.cream,
      foregroundColor: WokColors.ink,
      elevation: 0,
      centerTitle: false,
    ),
    floatingActionButtonTheme: const FloatingActionButtonThemeData(
      backgroundColor: WokColors.orange,
      foregroundColor: Colors.white,
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: WokColors.orange,
        foregroundColor: Colors.white,
        padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 14),
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: Colors.white,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(14)),
    ),
    cardTheme: CardThemeData(
      color: Colors.white,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(18),
        side: const BorderSide(color: Color(0xFFF0EBE4)),
      ),
    ),
  );
}

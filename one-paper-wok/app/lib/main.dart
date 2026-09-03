import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'app.dart';
import 'core/config.dart';

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();
  final prefs = await SharedPreferences.getInstance();
  final saved = prefs.getString(AppConfig.urlPrefsKey);
  runApp(
    ProviderScope(
      overrides: [
        if (saved != null && saved.isNotEmpty)
          serverUrlProvider.overrideWith(() {
            return _PreloadedUrl(saved);
          }),
      ],
      child: const OnePaperWokApp(),
    ),
  );
}

class _PreloadedUrl extends ServerUrlNotifier {
  _PreloadedUrl(this._initial);
  final String _initial;
  @override
  String build() => _initial;
}

class AppConfig {
  /// Override with `--dart-define=API_BASE_URL=http://192.168.x.x:8000` on a physical device.
  static const apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://127.0.0.1:8000',
  );
}

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AppConfig {
  static const defaultApiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://192.168.1.1:8000',
  );
  static const urlPrefsKey = 'api_base_url';
}

bool _isPrivateOrLocalHost(String host) {
  if (host == 'localhost' || host == '::1' || host.endsWith('.local')) {
    return true;
  }
  if (host.startsWith('127.') || host.startsWith('10.') || host.startsWith('192.168.')) {
    return true;
  }
  final match = RegExp(r'^172\.(1[6-9]|2\d|3[0-1])\.').firstMatch(host);
  return match != null;
}

String normalizeApiBaseUrl(String raw) {
  var url = raw.trim();
  if (url.endsWith('/')) {
    url = url.substring(0, url.length - 1);
  }
  if (!url.startsWith('http://') && !url.startsWith('https://')) {
    final host = url.split('/').first.split(':').first;
    url = '${_isPrivateOrLocalHost(host) ? 'http' : 'https'}://$url';
  }
  return url;
}

class ServerUrlNotifier extends Notifier<String> {
  @override
  String build() => AppConfig.defaultApiBaseUrl;

  Future<void> load() async {
    final prefs = await SharedPreferences.getInstance();
    state = prefs.getString(AppConfig.urlPrefsKey) ?? AppConfig.defaultApiBaseUrl;
  }

  Future<void> setUrl(String raw) async {
    var url = normalizeApiBaseUrl(raw);
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(AppConfig.urlPrefsKey, url);
    state = url;
  }
}

final serverUrlProvider = NotifierProvider<ServerUrlNotifier, String>(ServerUrlNotifier.new);

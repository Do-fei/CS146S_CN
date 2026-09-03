import 'package:flutter_secure_storage/flutter_secure_storage.dart';
import 'package:shared_preferences/shared_preferences.dart';

class AuthStore {
  AuthStore();

  static const _kAccess = 'access_token';
  static const _kRefresh = 'refresh_token';
  static const _kDevice = 'device_id';

  final FlutterSecureStorage _secure = const FlutterSecureStorage();
  SharedPreferences? _prefs;
  bool _secureOk = true;

  Future<void> _ensurePrefs() async {
    _prefs ??= await SharedPreferences.getInstance();
  }

  Future<String?> _read(String key) async {
    if (_secureOk) {
      try {
        return await _secure.read(key: key);
      } catch (_) {
        _secureOk = false;
      }
    }
    await _ensurePrefs();
    return _prefs!.getString(key);
  }

  Future<void> _write(String key, String? value) async {
    if (_secureOk) {
      try {
        if (value == null) {
          await _secure.delete(key: key);
        } else {
          await _secure.write(key: key, value: value);
        }
        return;
      } catch (_) {
        _secureOk = false;
      }
    }
    await _ensurePrefs();
    if (value == null) {
      await _prefs!.remove(key);
    } else {
      await _prefs!.setString(key, value);
    }
  }

  Future<String?> get accessToken => _read(_kAccess);
  Future<String?> get refreshToken => _read(_kRefresh);

  Future<String> deviceId() async {
    final existing = await _read(_kDevice);
    if (existing != null && existing.isNotEmpty) return existing;
    final id = DateTime.now().microsecondsSinceEpoch.toRadixString(36);
    await _write(_kDevice, id);
    return id;
  }

  Future<void> saveTokens({required String access, required String refresh}) async {
    await _write(_kAccess, access);
    await _write(_kRefresh, refresh);
  }

  Future<void> clear() async {
    await _write(_kAccess, null);
    await _write(_kRefresh, null);
  }
}

import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';

import 'api_client.dart';
import 'models.dart';

final libraryControllerProvider = AsyncNotifierProvider<LibraryController, List<BookItem>>(
  LibraryController.new,
);

class LibraryController extends AsyncNotifier<List<BookItem>> {
  static const _sinceKey = 'last_sync_at';

  @override
  Future<List<BookItem>> build() => refresh();

  ApiClient get _api => ref.read(apiClientProvider);

  Future<List<BookItem>> refresh({bool incremental = true}) async {
    final prefs = await SharedPreferences.getInstance();
    DateTime? since;
    if (incremental) {
      final raw = prefs.getString(_sinceKey);
      if (raw != null) since = DateTime.tryParse(raw);
    }
    final payload = await _api.sync(since: since);
    await prefs.setString(_sinceKey, payload['server_time'] as String);
    if (since == null) {
      final books = (payload['books'] as List)
          .map((e) => BookItem.fromJson(Map<String, dynamic>.from(e)))
          .where((b) => b.deletedAt == null)
          .toList();
      state = AsyncData(books);
      return books;
    }
    final current = [...(state.valueOrNull ?? await _api.listBooks())];
    for (final raw in payload['books'] as List) {
      final item = BookItem.fromJson(Map<String, dynamic>.from(raw));
      current.removeWhere((b) => b.id == item.id);
      if (item.deletedAt == null) current.insert(0, item);
    }
    state = AsyncData(current);
    return current;
  }

  Future<void> resetSyncCursor() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_sinceKey);
  }
}

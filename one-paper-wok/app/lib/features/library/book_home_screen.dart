import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/api_client.dart';
import '../../core/models.dart';
import '../../core/sync_engine.dart';
import '../../theme/app_theme.dart';

class BookHomeScreen extends ConsumerStatefulWidget {
  const BookHomeScreen({super.key, required this.bookId});
  final String bookId;

  @override
  ConsumerState<BookHomeScreen> createState() => _BookHomeScreenState();
}

class _BookHomeScreenState extends ConsumerState<BookHomeScreen> {
  BookItem? _book;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final book = await ref.read(apiClientProvider).getBook(widget.bookId);
      if (mounted) setState(() => _book = book);
    } catch (e) {
      if (mounted) setState(() => _error = ref.read(apiClientProvider).prettyError(e));
    }
  }

  @override
  Widget build(BuildContext context) {
    final book = _book;
    return Scaffold(
      appBar: AppBar(
        title: Text(book?.title ?? '书'),
        actions: [
          IconButton(
            icon: const Icon(Icons.delete_outline),
            onPressed: book == null
                ? null
                : () async {
                    await ref.read(apiClientProvider).deleteBook(book.id);
                    await ref.read(libraryControllerProvider.notifier).refresh();
                    if (context.mounted) context.go('/library');
                  },
          ),
        ],
      ),
      body: book == null
          ? Center(child: _error == null ? const CircularProgressIndicator() : Text(_error!))
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                Text('${book.author ?? ''} · ${book.pageCount} 页 · ${book.status}',
                    style: const TextStyle(color: WokColors.muted)),
                const SizedBox(height: 16),
                _tile(context, Icons.menu_book, '阅读电子书', () => context.push('/book/${book.id}/read')),
                _tile(context, Icons.auto_awesome, '一纸项目', () => context.push('/book/${book.id}/project')),
                _tile(context, Icons.edit_note, '一纸笔记本', () => context.push('/book/${book.id}/notebook')),
                _tile(
                  context,
                  Icons.document_scanner,
                  '回锅加料（扫描批注）',
                  () => context.push('/scan?bookId=${book.id}&annotation=1'),
                ),
              ],
            ),
    );
  }

  Widget _tile(BuildContext context, IconData icon, String title, VoidCallback onTap) {
    return Card(
      child: ListTile(
        leading: Icon(icon, color: WokColors.orange),
        title: Text(title, style: const TextStyle(fontWeight: FontWeight.w600)),
        trailing: const Icon(Icons.chevron_right),
        onTap: onTap,
      ),
    );
  }
}

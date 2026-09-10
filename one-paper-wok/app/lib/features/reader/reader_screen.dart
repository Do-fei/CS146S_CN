import 'package:dio/dio.dart';
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:share_plus/share_plus.dart';

import '../../core/api_client.dart';
import '../../core/models.dart';
import '../../theme/app_theme.dart';

class ReaderScreen extends ConsumerStatefulWidget {
  const ReaderScreen({super.key, required this.bookId});
  final String bookId;

  @override
  ConsumerState<ReaderScreen> createState() => _ReaderScreenState();
}

class _ReaderScreenState extends ConsumerState<ReaderScreen> {
  BookItem? _book;
  int _page = 0;
  String _text = '';
  bool _busy = true;
  bool _showTrans = false;
  String _lang = 'en';
  List<TranslatedSegment> _trans = [];
  List<SearchHit> _hits = [];
  final _search = TextEditingController();
  String? _error;

  @override
  void initState() {
    super.initState();
    _boot();
  }

  @override
  void dispose() {
    _search.dispose();
    super.dispose();
  }

  Future<void> _boot() async {
    try {
      final api = ref.read(apiClientProvider);
      final book = await api.getBook(widget.bookId);
      setState(() => _book = book);
      await _loadPage(0);
    } catch (e) {
      setState(() => _error = ref.read(apiClientProvider).prettyError(e));
    }
  }

  Future<void> _loadPage(int index) async {
    final book = _book;
    if (book == null || book.pageCount == 0) {
      setState(() => _busy = false);
      return;
    }
    setState(() {
      _busy = true;
      _page = index.clamp(0, book.pageCount - 1);
    });
    final api = ref.read(apiClientProvider);
    try {
      final text = await api.pageText(widget.bookId, _page);
      List<TranslatedSegment> trans = [];
      if (_showTrans) {
        trans = await api.translate(widget.bookId, _page, _lang);
      }
      setState(() {
        _text = text;
        _trans = trans;
        _busy = false;
      });
    } catch (e) {
      setState(() {
        _error = api.prettyError(e);
        _busy = false;
      });
    }
  }

  Future<void> _doSearch() async {
    final q = _search.text.trim();
    if (q.isEmpty) return;
    final hits = await ref.read(apiClientProvider).search(widget.bookId, q);
    setState(() => _hits = hits);
  }

  Future<void> _export(bool epub) async {
    final api = ref.read(apiClientProvider);
    try {
      if (epub) {
        final job = await api.exportEpub(widget.bookId);
        while (true) {
          final latest = await api.getJob(job.id);
          if (latest.isTerminal) {
            if (latest.stage == 'failed') throw Exception(latest.error ?? 'EPUB 失败');
            break;
          }
          await Future<void>.delayed(const Duration(seconds: 1));
        }
      }
      final file = await api.downloadEbook(widget.bookId, epub: epub);
      await Share.shareXFiles([XFile(file.path)], text: _book?.title ?? '电子书');
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(api.prettyError(e))));
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    final book = _book;
    return Scaffold(
      appBar: AppBar(
        title: Text(book?.title ?? '阅读'),
        actions: [
          IconButton(tooltip: '导出 PDF', onPressed: () => _export(false), icon: const Icon(Icons.picture_as_pdf)),
          IconButton(tooltip: '导出 EPUB', onPressed: () => _export(true), icon: const Icon(Icons.menu_book)),
        ],
      ),
      body: book == null
          ? Center(child: _error == null ? const CircularProgressIndicator() : Text(_error!))
          : Column(
              children: [
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16),
                  child: Row(
                    children: [
                      Expanded(
                        child: TextField(
                          controller: _search,
                          decoration: const InputDecoration(hintText: '全文搜索', isDense: true),
                          onSubmitted: (_) => _doSearch(),
                        ),
                      ),
                      IconButton(onPressed: _doSearch, icon: const Icon(Icons.search)),
                      Switch(
                        value: _showTrans,
                        onChanged: (v) async {
                          setState(() => _showTrans = v);
                          await _loadPage(_page);
                        },
                      ),
                      DropdownButton<String>(
                        value: _lang,
                        items: const [
                          DropdownMenuItem(value: 'en', child: Text('EN')),
                          DropdownMenuItem(value: 'ja', child: Text('JA')),
                          DropdownMenuItem(value: 'zh', child: Text('ZH')),
                        ],
                        onChanged: (v) async {
                          if (v == null) return;
                          setState(() => _lang = v);
                          if (_showTrans) await _loadPage(_page);
                        },
                      ),
                    ],
                  ),
                ),
                if (_hits.isNotEmpty)
                  SizedBox(
                    height: 72,
                    child: ListView(
                      scrollDirection: Axis.horizontal,
                      children: [
                        for (final h in _hits)
                          ActionChip(
                            label: Text('P.${h.pageIndex} ${h.snippet}', overflow: TextOverflow.ellipsis),
                            onPressed: () => _loadPage(h.pageIndex),
                          ),
                      ],
                    ),
                  ),
                Expanded(
                  child: _busy
                      ? const Center(child: CircularProgressIndicator())
                      : ListView(
                          padding: const EdgeInsets.all(16),
                          children: [
                            FutureBuilder<Map<String, String>>(
                              future: ref.read(apiClientProvider).authHeader(),
                              builder: (context, snap) {
                                if (!snap.hasData) return const SizedBox.shrink();
                                return ClipRRect(
                                  borderRadius: BorderRadius.circular(12),
                                  child: Image.network(
                                    ref.read(apiClientProvider).pageImageUrl(widget.bookId, _page),
                                    headers: snap.data,
                                    errorBuilder: (_, error, stack) {
                                      if (error is DioException) return const SizedBox.shrink();
                                      return const SizedBox.shrink();
                                    },
                                  ),
                                );
                              },
                            ),
                            const SizedBox(height: 16),
                            if (_showTrans)
                              ..._trans.map(
                                (s) => Padding(
                                  padding: const EdgeInsets.only(bottom: 12),
                                  child: Column(
                                    crossAxisAlignment: CrossAxisAlignment.start,
                                    children: [
                                      Text(s.source, style: const TextStyle(color: WokColors.muted)),
                                      Text(s.text, style: const TextStyle(fontSize: 16, height: 1.6)),
                                    ],
                                  ),
                                ),
                              )
                            else
                              Text(_text, style: const TextStyle(fontSize: 16, height: 1.7)),
                          ],
                        ),
                ),
                Padding(
                  padding: const EdgeInsets.all(12),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      IconButton(
                        onPressed: _page > 0 ? () => _loadPage(_page - 1) : null,
                        icon: const Icon(Icons.chevron_left),
                      ),
                      Text('第 $_page / ${book.pageCount - 1} 页'),
                      IconButton(
                        onPressed: _page < book.pageCount - 1 ? () => _loadPage(_page + 1) : null,
                        icon: const Icon(Icons.chevron_right),
                      ),
                    ],
                  ),
                ),
              ],
            ),
    );
  }
}

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/api_client.dart';
import '../../core/models.dart';
import '../../theme/app_theme.dart';

class NotebookScreen extends ConsumerStatefulWidget {
  const NotebookScreen({super.key, required this.bookId});
  final String bookId;

  @override
  ConsumerState<NotebookScreen> createState() => _NotebookScreenState();
}

class _NotebookScreenState extends ConsumerState<NotebookScreen> {
  List<AnnotationItem> _items = [];
  final _typed = TextEditingController();
  bool _busy = true;
  String? _error;

  @override
  void initState() {
    super.initState();
    _load();
  }

  @override
  void dispose() {
    _typed.dispose();
    super.dispose();
  }

  Future<void> _load() async {
    try {
      final items = await ref.read(apiClientProvider).listAnnotations(widget.bookId);
      if (mounted) {
        setState(() {
          _items = items;
          _busy = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _error = ref.read(apiClientProvider).prettyError(e);
          _busy = false;
        });
      }
    }
  }

  Future<void> _addTyped() async {
    final text = _typed.text.trim();
    if (text.isEmpty) return;
    await ref.read(apiClientProvider).createTypedAnnotation(widget.bookId, text: text);
    _typed.clear();
    await _load();
  }

  Future<void> _recook() async {
    setState(() => _busy = true);
    try {
      final job = await ref.read(apiClientProvider).recook(widget.bookId);
      if (mounted) context.go('/cooking/${job.id}');
    } catch (e) {
      setState(() {
        _error = ref.read(apiClientProvider).prettyError(e);
        _busy = false;
      });
    }
  }

  Future<void> _edit(AnnotationItem item) async {
    final controller = TextEditingController(text: item.handwrittenText ?? '');
    final ok = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('修正识别结果'),
        content: TextField(controller: controller, maxLines: 4),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('取消')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('保存')),
        ],
      ),
    );
    if (ok == true) {
      await ref.read(apiClientProvider).updateAnnotation(
            widget.bookId,
            item.id,
            handwrittenText: controller.text,
          );
      await _load();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('一纸笔记本'),
        actions: [
          TextButton(onPressed: _items.isEmpty ? null : _recook, child: const Text('回锅加料')),
        ],
      ),
      body: _busy
          ? const Center(child: CircularProgressIndicator())
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
                TextField(
                  controller: _typed,
                  decoration: InputDecoration(
                    labelText: '打字记录一条批注',
                    suffixIcon: IconButton(onPressed: _addTyped, icon: const Icon(Icons.send)),
                  ),
                  onSubmitted: (_) => _addTyped(),
                ),
                const SizedBox(height: 12),
                OutlinedButton.icon(
                  onPressed: () => context.push('/scan?bookId=${widget.bookId}&annotation=1'),
                  icon: const Icon(Icons.document_scanner),
                  label: const Text('扫描手写批注'),
                ),
                const SizedBox(height: 16),
                if (_items.isEmpty)
                  const Text('还没有批注。扫描书页上的手写，或在这里打字。', style: TextStyle(color: WokColors.muted)),
                for (final a in _items)
                  Card(
                    child: ListTile(
                      title: Text(a.handwrittenText ?? '（待识别）'),
                      subtitle: Text(
                        [
                          if (a.pageIndex != null) 'P.${a.pageIndex}',
                          a.source,
                          a.status,
                          if (a.refinedText != null) a.refinedText!,
                        ].join(' · '),
                      ),
                      onTap: () => _edit(a),
                    ),
                  ),
              ],
            ),
    );
  }
}

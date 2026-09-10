import 'dart:io';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:image_picker/image_picker.dart';
import 'package:uuid/uuid.dart';

import '../../core/api_client.dart';
import '../../core/sync_engine.dart';
import '../../theme/app_theme.dart';

class ScanScreen extends ConsumerStatefulWidget {
  const ScanScreen({super.key, this.bookId, this.annotationMode = false});
  final String? bookId;
  final bool annotationMode;

  @override
  ConsumerState<ScanScreen> createState() => _ScanScreenState();
}

class _ScanScreenState extends ConsumerState<ScanScreen> {
  final _title = TextEditingController();
  final _author = TextEditingController();
  final _pages = <XFile>[];
  String _mode = 'full';
  bool _busy = false;
  String? _error;
  int? _pageIndex;

  @override
  void dispose() {
    _title.dispose();
    _author.dispose();
    super.dispose();
  }

  Future<void> _pick(ImageSource source) async {
    final picker = ImagePicker();
    if (source == ImageSource.gallery) {
      final files = await picker.pickMultiImage(imageQuality: 85);
      setState(() => _pages.addAll(files));
    } else {
      final file = await picker.pickImage(source: ImageSource.camera, imageQuality: 85);
      if (file != null) setState(() => _pages.add(file));
    }
  }

  Future<void> _submit() async {
    if (_pages.isEmpty) {
      setState(() => _error = '请先拍摄或导入至少一页');
      return;
    }
    setState(() {
      _busy = true;
      _error = null;
    });
    final api = ref.read(apiClientProvider);
    try {
      if (widget.annotationMode && widget.bookId != null) {
        await api.uploadAnnotationScans(
          widget.bookId!,
          _pages.map((e) => File(e.path)).toList(),
          pageIndex: _pageIndex,
          opId: const Uuid().v4(),
        );
        if (mounted) context.go('/book/${widget.bookId}/notebook');
        return;
      }
      final book = widget.bookId == null
          ? await api.createBook(
              title: _title.text.trim().isEmpty ? '未命名书稿' : _title.text.trim(),
              author: _author.text.trim().isEmpty ? null : _author.text.trim(),
              mode: _mode,
            )
          : await api.getBook(widget.bookId!);
      await api.uploadPages(book.id, _pages.map((e) => File(e.path)).toList());
      final job = await api.cook(book.id);
      await ref.read(libraryControllerProvider.notifier).refresh();
      if (mounted) context.go('/cooking/${job.id}');
    } catch (e) {
      setState(() => _error = api.prettyError(e));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final annotating = widget.annotationMode;
    return Scaffold(
      appBar: AppBar(title: Text(annotating ? '批注扫描 · 回锅加料' : '自炊台')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          if (!annotating) ...[
            TextField(controller: _title, decoration: const InputDecoration(labelText: '书名')),
            const SizedBox(height: 12),
            TextField(controller: _author, decoration: const InputDecoration(labelText: '作者（可选）')),
            const SizedBox(height: 16),
            SegmentedButton<String>(
              segments: const [
                ButtonSegment(value: 'full', label: Text('全书自炊')),
                ButtonSegment(value: 'excerpt', label: Text('轻摘录')),
              ],
              selected: {_mode},
              onSelectionChanged: (s) => setState(() => _mode = s.first),
            ),
          ] else ...[
            TextField(
              keyboardType: TextInputType.number,
              decoration: const InputDecoration(labelText: '对应页码（从 0 起，可空）'),
              onChanged: (v) => _pageIndex = int.tryParse(v),
            ),
          ],
          const SizedBox(height: 16),
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              for (var i = 0; i < _pages.length; i++)
                Stack(
                  children: [
                    ClipRRect(
                      borderRadius: BorderRadius.circular(8),
                      child: Image.file(File(_pages[i].path), width: 72, height: 96, fit: BoxFit.cover),
                    ),
                    Positioned(
                      right: 0,
                      child: IconButton(
                        icon: const Icon(Icons.close, size: 16, color: Colors.white),
                        onPressed: () => setState(() => _pages.removeAt(i)),
                      ),
                    ),
                  ],
                ),
              OutlinedButton.icon(
                onPressed: () => _pick(ImageSource.camera),
                icon: const Icon(Icons.photo_camera),
                label: const Text('拍摄'),
              ),
              OutlinedButton.icon(
                onPressed: () => _pick(ImageSource.gallery),
                icon: const Icon(Icons.photo_library),
                label: const Text('相册'),
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text('已选 ${_pages.length} 页', style: const TextStyle(color: WokColors.muted)),
          if (_error != null) Text(_error!, style: const TextStyle(color: Colors.red)),
          const SizedBox(height: 24),
          FilledButton(
            onPressed: _busy ? null : _submit,
            child: Text(annotating ? '上传批注并去笔记本' : '🔥 开始慢炖（${_pages.length} 页）'),
          ),
        ],
      ),
    );
  }
}

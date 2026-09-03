import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/api_client.dart';
import '../../core/models.dart';
import '../../core/sync_engine.dart';
import '../../theme/app_theme.dart';

class LibraryScreen extends ConsumerStatefulWidget {
  const LibraryScreen({super.key});

  @override
  ConsumerState<LibraryScreen> createState() => _LibraryScreenState();
}

class _LibraryScreenState extends ConsumerState<LibraryScreen> {
  String _tab = 'all';
  List<JobItem> _jobs = [];

  @override
  void initState() {
    super.initState();
    _loadJobs();
  }

  Future<void> _loadJobs() async {
    try {
      final jobs = await ref.read(apiClientProvider).activeJobs();
      if (mounted) setState(() => _jobs = jobs);
    } catch (_) {}
  }

  @override
  Widget build(BuildContext context) {
    final books = ref.watch(libraryControllerProvider);
    return Scaffold(
      appBar: AppBar(
        title: const Text('我的锅', style: TextStyle(fontWeight: FontWeight.w800, fontSize: 26)),
        actions: [
          IconButton(
            tooltip: '同步',
            onPressed: () => ref.read(libraryControllerProvider.notifier).refresh(),
            icon: const Icon(Icons.sync),
          ),
          IconButton(
            tooltip: '退出',
            onPressed: () async {
              await ref.read(apiClientProvider).logout();
              await ref.read(libraryControllerProvider.notifier).resetSyncCursor();
              if (context.mounted) context.go('/login');
            },
            icon: const Icon(Icons.logout),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/scan'),
        child: const Icon(Icons.photo_camera),
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          await ref.read(libraryControllerProvider.notifier).refresh();
          await _loadJobs();
        },
        child: ListView(
          padding: const EdgeInsets.fromLTRB(16, 8, 16, 96),
          children: [
            for (final job in _jobs)
              _CookingBanner(
                job: job,
                onTap: () => context.push('/cooking/${job.id}'),
              ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: [
                _chip('全部', 'all'),
                _chip('电子书', 'ebook'),
                _chip('一纸项目', 'project'),
              ],
            ),
            const SizedBox(height: 16),
            books.when(
              loading: () => const Padding(
                padding: EdgeInsets.only(top: 48),
                child: Center(child: CircularProgressIndicator()),
              ),
              error: (e, _) => Text('加载失败：${ref.read(apiClientProvider).prettyError(e)}'),
              data: (items) {
                final filtered = items.where((b) {
                  if (_tab == 'ebook') return b.ebook.hasPdf;
                  if (_tab == 'project') return b.hasProject;
                  return true;
                }).toList();
                if (filtered.isEmpty) {
                  return const Padding(
                    padding: EdgeInsets.only(top: 48),
                    child: Center(child: Text('锅还是空的。点右下角开始自炊。', style: TextStyle(color: WokColors.muted))),
                  );
                }
                return Column(children: [for (final b in filtered) _BookCard(book: b)]);
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _chip(String label, String id) {
    final on = _tab == id;
    return ChoiceChip(
      label: Text(label),
      selected: on,
      onSelected: (_) => setState(() => _tab = id),
      selectedColor: const Color(0xFFFFF0EA),
      labelStyle: TextStyle(color: on ? WokColors.orange : WokColors.muted, fontWeight: FontWeight.w600),
    );
  }
}

class _CookingBanner extends StatelessWidget {
  const _CookingBanner({required this.job, required this.onTap});
  final JobItem job;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Container(
        margin: const EdgeInsets.only(bottom: 12),
        padding: const EdgeInsets.all(18),
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          gradient: const LinearGradient(colors: [WokColors.orange, WokColors.orangeSoft]),
        ),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(job.kind == 'recook' ? '🍳 回锅中' : '🍳 慢炖中',
                style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 18)),
            const SizedBox(height: 4),
            Text(job.message ?? job.stage, style: const TextStyle(color: Colors.white70)),
            const SizedBox(height: 12),
            LinearProgressIndicator(
              value: job.progress / 100,
              backgroundColor: Colors.white24,
              color: Colors.white,
            ),
          ],
        ),
      ),
    );
  }
}

class _BookCard extends StatelessWidget {
  const _BookCard({required this.book});
  final BookItem book;

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        contentPadding: const EdgeInsets.all(12),
        leading: Container(
          width: 48,
          height: 64,
          decoration: BoxDecoration(
            borderRadius: BorderRadius.circular(8),
            gradient: const LinearGradient(colors: [WokColors.blue, Color(0xFF2A6CB0)]),
          ),
          child: const Center(child: Text('📘', style: TextStyle(fontSize: 22))),
        ),
        title: Text(book.title, style: const TextStyle(fontWeight: FontWeight.w700)),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('${book.author ?? '未知作者'} · ${book.pageCount} 页 · ${book.status}'),
            const SizedBox(height: 6),
            Wrap(
              spacing: 6,
              children: [
                if (book.hasProject) const _Tag('一纸项目', WokColors.orange),
                if (book.ebook.hasPdf) const _Tag('电子书', WokColors.blue),
                if (book.ebook.hasEpub) const _Tag('EPUB', WokColors.green),
              ],
            ),
          ],
        ),
        onTap: () => context.push('/book/${book.id}'),
      ),
    );
  }
}

class _Tag extends StatelessWidget {
  const _Tag(this.label, this.color);
  final String label;
  final Color color;
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 3),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.12),
        borderRadius: BorderRadius.circular(20),
      ),
      child: Text(label, style: TextStyle(color: color, fontSize: 11, fontWeight: FontWeight.w700)),
    );
  }
}

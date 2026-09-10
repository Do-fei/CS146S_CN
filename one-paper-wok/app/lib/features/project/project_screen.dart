import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/api_client.dart';
import '../../core/models.dart';
import '../../theme/app_theme.dart';

class ProjectScreen extends ConsumerStatefulWidget {
  const ProjectScreen({super.key, required this.bookId});
  final String bookId;

  @override
  ConsumerState<ProjectScreen> createState() => _ProjectScreenState();
}

class _ProjectScreenState extends ConsumerState<ProjectScreen> {
  ProjectItem? _project;
  String? _error;
  int _chapter = 0;

  @override
  void initState() {
    super.initState();
    _load();
  }

  Future<void> _load() async {
    try {
      final project = await ref.read(apiClientProvider).getProject(widget.bookId);
      if (mounted) setState(() => _project = project);
    } catch (e) {
      if (mounted) setState(() => _error = ref.read(apiClientProvider).prettyError(e));
    }
  }

  @override
  Widget build(BuildContext context) {
    final p = _project;
    return Scaffold(
      appBar: AppBar(title: const Text('一纸项目')),
      body: p == null
          ? Center(child: _error == null ? const CircularProgressIndicator() : Text(_error!))
          : ListView(
              padding: const EdgeInsets.all(16),
              children: [
                if (p.chapterOutline.isNotEmpty)
                  SizedBox(
                    height: 40,
                    child: ListView(
                      scrollDirection: Axis.horizontal,
                      children: [
                        for (var i = 0; i < p.chapterOutline.length; i++)
                          Padding(
                            padding: const EdgeInsets.only(right: 8),
                            child: ChoiceChip(
                              label: Text(p.chapterOutline[i].title),
                              selected: _chapter == i,
                              onSelected: (_) => setState(() => _chapter = i),
                            ),
                          ),
                      ],
                    ),
                  ),
                const SizedBox(height: 12),
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Container(
                          padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                          decoration: BoxDecoration(
                            color: WokColors.orange,
                            borderRadius: BorderRadius.circular(20),
                          ),
                          child: Text('一纸精华 · v${p.version}',
                              style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w700, fontSize: 12)),
                        ),
                        const SizedBox(height: 12),
                        Text(
                          _chapter == 0 || p.chapterOutline.isEmpty
                              ? p.summary
                              : p.chapterOutline[_chapter.clamp(0, p.chapterOutline.length - 1)].summary,
                          style: const TextStyle(height: 1.7, fontSize: 15),
                        ),
                        const SizedBox(height: 16),
                        for (var i = 0; i < p.keyInsights.length; i++)
                          ListTile(
                            dense: true,
                            leading: CircleAvatar(
                              backgroundColor: const Color(0xFFFFF0EA),
                              foregroundColor: WokColors.orange,
                              radius: 14,
                              child: Text('${i + 1}', style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w800)),
                            ),
                            title: Text(p.keyInsights[i]),
                          ),
                        for (final insight in p.personalInsights)
                          Container(
                            width: double.infinity,
                            margin: const EdgeInsets.only(top: 8),
                            padding: const EdgeInsets.all(12),
                            decoration: const BoxDecoration(
                              color: Color(0xFFF3EEFF),
                              border: Border(left: BorderSide(color: WokColors.purple, width: 3)),
                            ),
                            child: Text(
                              '我的批注${insight.pageIndex == null ? '' : ' · P.${insight.pageIndex}'}\n${insight.text}',
                              style: const TextStyle(color: Color(0xFF5A3FA0)),
                            ),
                          ),
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: OutlinedButton(
                        onPressed: () => context.push('/scan?bookId=${widget.bookId}&annotation=1'),
                        child: const Text('回锅加料'),
                      ),
                    ),
                    const SizedBox(width: 8),
                    Expanded(
                      child: FilledButton(
                        onPressed: null,
                        child: const Text('分享到食堂（即将开放）'),
                      ),
                    ),
                  ],
                ),
              ],
            ),
    );
  }
}

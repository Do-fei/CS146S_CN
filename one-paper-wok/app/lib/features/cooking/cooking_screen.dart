import 'dart:async';

import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/api_client.dart';
import '../../core/models.dart';
import '../../core/sync_engine.dart';
import '../../theme/app_theme.dart';

class CookingScreen extends ConsumerStatefulWidget {
  const CookingScreen({super.key, required this.jobId});
  final String jobId;

  @override
  ConsumerState<CookingScreen> createState() => _CookingScreenState();
}

class _CookingScreenState extends ConsumerState<CookingScreen> {
  JobItem? _job;
  String? _error;
  Timer? _timer;

  @override
  void initState() {
    super.initState();
    _poll();
    _timer = Timer.periodic(const Duration(seconds: 2), (_) => _poll());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> _poll() async {
    try {
      final job = await ref.read(apiClientProvider).getJob(widget.jobId);
      if (!mounted) return;
      setState(() => _job = job);
      if (job.isTerminal) {
        _timer?.cancel();
        await ref.read(libraryControllerProvider.notifier).refresh();
      }
    } catch (e) {
      if (mounted) setState(() => _error = ref.read(apiClientProvider).prettyError(e));
    }
  }

  @override
  Widget build(BuildContext context) {
    final job = _job;
    return Scaffold(
      appBar: AppBar(title: Text(job?.kind == 'recook' ? '回锅加料' : '慢炖中')),
      body: Padding(
        padding: const EdgeInsets.all(24),
        child: job == null
            ? Center(child: _error == null ? const CircularProgressIndicator() : Text(_error!))
            : Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(job.message ?? job.stage, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
                  const SizedBox(height: 16),
                  LinearProgressIndicator(value: job.progress / 100, color: WokColors.orange),
                  const SizedBox(height: 8),
                  Text('${job.progress}% · ${job.stage}', style: const TextStyle(color: WokColors.muted)),
                  if (job.error != null) Text(job.error!, style: const TextStyle(color: Colors.red)),
                  const Spacer(),
                  if (job.stage == 'done')
                    FilledButton(
                      onPressed: () => context.go('/book/${job.bookId}'),
                      child: const Text('查看出锅结果'),
                    )
                  else
                    OutlinedButton(
                      onPressed: () => context.go('/library'),
                      child: const Text('回我的锅，后台继续'),
                    ),
                ],
              ),
      ),
    );
  }
}

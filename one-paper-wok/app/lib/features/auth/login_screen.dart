import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import '../../core/api_client.dart';
import '../../core/config.dart';
import '../../theme/app_theme.dart';

class LoginScreen extends ConsumerStatefulWidget {
  const LoginScreen({super.key});

  @override
  ConsumerState<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends ConsumerState<LoginScreen> {
  final _email = TextEditingController();
  final _code = TextEditingController();
  late final TextEditingController _server;
  bool _sent = false;
  bool _busy = false;
  String? _hint;
  String? _error;
  String? _health;

  @override
  void initState() {
    super.initState();
    _server = TextEditingController(text: ref.read(serverUrlProvider));
  }

  @override
  void dispose() {
    _email.dispose();
    _code.dispose();
    _server.dispose();
    super.dispose();
  }

  Future<void> _saveServer() async {
    await ref.read(serverUrlProvider.notifier).setUrl(_server.text);
    _server.text = ref.read(serverUrlProvider);
  }

  Future<void> _ping() async {
    setState(() {
      _busy = true;
      _error = null;
      _health = null;
    });
    try {
      await _saveServer();
      final data = await ref.read(apiClientProvider).health();
      setState(() => _health = '已连通 · OCR ${data['providers']?['ocr']} · 邮件 ${data['providers']?['email']}');
    } catch (e) {
      setState(() => _error = '连不上服务器：${ref.read(apiClientProvider).prettyError(e)}\n局域网请确认电脑已启动后端且与手机同一 Wi-Fi；云端请填 https 地址。');
    } finally {
      setState(() => _busy = false);
    }
  }

  Future<void> _send() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await _saveServer();
      final data = await ref.read(apiClientProvider).sendCode(_email.text.trim());
      setState(() {
        _sent = true;
        _hint = data['debug_code'] != null ? '开发模式验证码：${data['debug_code']}' : '验证码已发送到邮箱';
      });
    } catch (e) {
      setState(() => _error = ref.read(apiClientProvider).prettyError(e));
    } finally {
      setState(() => _busy = false);
    }
  }

  Future<void> _verify() async {
    setState(() {
      _busy = true;
      _error = null;
    });
    try {
      await _saveServer();
      await ref.read(apiClientProvider).verify(_email.text.trim(), _code.text.trim());
      if (mounted) context.go('/library');
    } catch (e) {
      setState(() => _error = ref.read(apiClientProvider).prettyError(e));
    } finally {
      if (mounted) setState(() => _busy = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SafeArea(
        child: ListView(
          padding: const EdgeInsets.all(24),
          children: [
            const SizedBox(height: 12),
            const Text('🍲', style: TextStyle(fontSize: 48)),
            const SizedBox(height: 12),
            const Text('一纸读书煲', style: TextStyle(fontSize: 32, fontWeight: FontWeight.w800)),
            const Text('一个有趣的精神庇护所', style: TextStyle(color: WokColors.muted)),
            const SizedBox(height: 28),
            TextField(
              controller: _server,
              keyboardType: TextInputType.url,
              decoration: const InputDecoration(
                labelText: '服务器地址',
                hintText: 'https://xxx.up.railway.app',
                helperText: 'Railway 填 https 公网地址；本地调试填电脑局域网 IP，不要填 127.0.0.1',
              ),
            ),
            const SizedBox(height: 8),
            Align(
              alignment: Alignment.centerLeft,
              child: TextButton(onPressed: _busy ? null : _ping, child: const Text('测试连接')),
            ),
            if (_health != null) Text(_health!, style: const TextStyle(color: WokColors.green)),
            const SizedBox(height: 8),
            TextField(
              controller: _email,
              keyboardType: TextInputType.emailAddress,
              decoration: const InputDecoration(
                labelText: '邮箱',
                hintText: '任意邮箱即可',
                helperText: '未配置 SMTP 时，验证码会直接显示在本页',
              ),
            ),
            if (_sent) ...[
              const SizedBox(height: 16),
              TextField(
                controller: _code,
                keyboardType: TextInputType.number,
                maxLength: 6,
                decoration: const InputDecoration(labelText: '6 位验证码'),
              ),
            ],
            if (_hint != null) ...[
              const SizedBox(height: 8),
              Text(_hint!, style: const TextStyle(color: WokColors.blue, fontWeight: FontWeight.w700)),
            ],
            if (_error != null) ...[
              const SizedBox(height: 8),
              Text(_error!, style: const TextStyle(color: Colors.red)),
            ],
            const SizedBox(height: 32),
            FilledButton(
              onPressed: _busy ? null : (_sent ? _verify : _send),
              child: _busy
                  ? const SizedBox(
                      height: 18,
                      width: 18,
                      child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white),
                    )
                  : Text(_sent ? '登录' : '获取验证码'),
            ),
          ],
        ),
      ),
    );
  }
}

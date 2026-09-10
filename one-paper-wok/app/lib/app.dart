import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';

import 'core/api_client.dart';
import 'features/auth/login_screen.dart';
import 'features/cooking/cooking_screen.dart';
import 'features/library/book_home_screen.dart';
import 'features/library/library_screen.dart';
import 'features/notebook/notebook_screen.dart';
import 'features/project/project_screen.dart';
import 'features/reader/reader_screen.dart';
import 'features/scan/scan_screen.dart';
import 'theme/app_theme.dart';

final _routerProvider = Provider<GoRouter>((ref) {
  final auth = ref.watch(authStoreProvider);
  return GoRouter(
    initialLocation: '/library',
    redirect: (context, state) async {
      final token = await auth.accessToken;
      final loggingIn = state.matchedLocation == '/login';
      if (token == null || token.isEmpty) {
        return loggingIn ? null : '/login';
      }
      if (loggingIn) return '/library';
      return null;
    },
    routes: [
      GoRoute(path: '/login', builder: (c, s) => const LoginScreen()),
      GoRoute(path: '/library', builder: (c, s) => const LibraryScreen()),
      GoRoute(
        path: '/scan',
        builder: (c, s) => ScanScreen(
          bookId: s.uri.queryParameters['bookId'],
          annotationMode: s.uri.queryParameters['annotation'] == '1',
        ),
      ),
      GoRoute(
        path: '/cooking/:jobId',
        builder: (c, s) => CookingScreen(jobId: s.pathParameters['jobId']!),
      ),
      GoRoute(
        path: '/book/:id',
        builder: (c, s) => BookHomeScreen(bookId: s.pathParameters['id']!),
      ),
      GoRoute(
        path: '/book/:id/read',
        builder: (c, s) => ReaderScreen(bookId: s.pathParameters['id']!),
      ),
      GoRoute(
        path: '/book/:id/project',
        builder: (c, s) => ProjectScreen(bookId: s.pathParameters['id']!),
      ),
      GoRoute(
        path: '/book/:id/notebook',
        builder: (c, s) => NotebookScreen(bookId: s.pathParameters['id']!),
      ),
    ],
  );
});

class OnePaperWokApp extends ConsumerWidget {
  const OnePaperWokApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final router = ref.watch(_routerProvider);
    return MaterialApp.router(
      title: '一纸读书煲',
      debugShowCheckedModeBanner: false,
      theme: buildWokTheme(),
      routerConfig: router,
    );
  }
}

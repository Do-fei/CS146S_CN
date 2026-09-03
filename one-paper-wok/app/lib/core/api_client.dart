import 'dart:convert';
import 'dart:io';

import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:path_provider/path_provider.dart';

import 'auth_store.dart';
import 'config.dart';
import 'models.dart';

final authStoreProvider = Provider<AuthStore>((ref) => AuthStore());

final apiClientProvider = Provider<ApiClient>((ref) {
  return ApiClient(ref.watch(authStoreProvider));
});

class ApiClient {
  ApiClient(this._auth) {
    _dio = Dio(
      BaseOptions(
        baseUrl: AppConfig.apiBaseUrl,
        connectTimeout: const Duration(seconds: 20),
        receiveTimeout: const Duration(seconds: 120),
      ),
    );
    _dio.interceptors.add(
      InterceptorsWrapper(
        onRequest: (options, handler) async {
          final token = await _auth.accessToken;
          if (token != null) {
            options.headers['Authorization'] = 'Bearer $token';
          }
          handler.next(options);
        },
        onError: (error, handler) async {
          if (error.response?.statusCode == 401 &&
              !(error.requestOptions.extra['retried'] == true) &&
              !error.requestOptions.path.contains('/auth/')) {
            final refreshed = await _refresh();
            if (refreshed) {
              final req = error.requestOptions;
              req.extra['retried'] = true;
              final token = await _auth.accessToken;
              req.headers['Authorization'] = 'Bearer $token';
              try {
                handler.resolve(await _dio.fetch(req));
                return;
              } catch (e) {
                handler.next(error);
                return;
              }
            }
          }
          handler.next(error);
        },
      ),
    );
  }

  final AuthStore _auth;
  late final Dio _dio;
  bool _refreshing = false;

  Future<bool> _refresh() async {
    if (_refreshing) return false;
    _refreshing = true;
    try {
      final refresh = await _auth.refreshToken;
      if (refresh == null) return false;
      final resp = await Dio(BaseOptions(baseUrl: AppConfig.apiBaseUrl)).post(
        '/auth/refresh',
        data: {'refresh_token': refresh},
      );
      await _auth.saveTokens(
        access: resp.data['access_token'] as String,
        refresh: resp.data['refresh_token'] as String,
      );
      return true;
    } catch (_) {
      await _auth.clear();
      return false;
    } finally {
      _refreshing = false;
    }
  }

  Future<Map<String, dynamic>> sendCode(String email) async {
    final resp = await _dio.post('/auth/send-code', data: {'email': email});
    return Map<String, dynamic>.from(resp.data as Map);
  }

  Future<void> verify(String email, String code) async {
    final resp = await _dio.post(
      '/auth/verify',
      data: {
        'email': email,
        'code': code,
        'device_id': await _auth.deviceId(),
      },
    );
    await _auth.saveTokens(
      access: resp.data['access_token'] as String,
      refresh: resp.data['refresh_token'] as String,
    );
  }

  Future<UserMe> me() async {
    final resp = await _dio.get('/auth/me');
    return UserMe.fromJson(Map<String, dynamic>.from(resp.data as Map));
  }

  Future<void> logout() async {
    final refresh = await _auth.refreshToken;
    if (refresh != null) {
      try {
        await _dio.post('/auth/logout', data: {'refresh_token': refresh});
      } catch (_) {}
    }
    await _auth.clear();
  }

  Future<List<BookItem>> listBooks() async {
    final resp = await _dio.get('/books');
    return (resp.data as List).map((e) => BookItem.fromJson(Map<String, dynamic>.from(e))).toList();
  }

  Future<BookItem> createBook({required String title, String? author, String mode = 'full'}) async {
    final resp = await _dio.post('/books', data: {'title': title, 'author': author, 'mode': mode});
    return BookItem.fromJson(Map<String, dynamic>.from(resp.data as Map));
  }

  Future<BookItem> getBook(String id) async {
    final resp = await _dio.get('/books/$id');
    return BookItem.fromJson(Map<String, dynamic>.from(resp.data as Map));
  }

  Future<void> deleteBook(String id) async {
    await _dio.delete('/books/$id');
  }

  Future<T> _withRetry<T>(Future<T> Function() fn, {int times = 3}) async {
    Object? last;
    for (var i = 0; i < times; i++) {
      try {
        return await fn();
      } catch (e) {
        last = e;
        if (i == times - 1) break;
        await Future<void>.delayed(Duration(milliseconds: 400 * (i + 1)));
      }
    }
    throw last!;
  }

  Future<void> uploadPages(String bookId, List<File> files) async {
    final form = FormData.fromMap({
      'files': [
        for (final f in files)
          await MultipartFile.fromFile(f.path, filename: f.uri.pathSegments.last),
      ],
    });
    await _withRetry(() => _dio.post('/books/$bookId/pages', data: form));
  }

  Future<JobItem> cook(String bookId) async {
    final resp = await _dio.post('/books/$bookId/cook');
    return JobItem.fromJson(Map<String, dynamic>.from(resp.data as Map));
  }

  Future<JobItem> getJob(String jobId) async {
    final resp = await _dio.get('/jobs/$jobId');
    return JobItem.fromJson(Map<String, dynamic>.from(resp.data as Map));
  }

  Future<List<JobItem>> activeJobs() async {
    final resp = await _dio.get('/jobs');
    return (resp.data as List).map((e) => JobItem.fromJson(Map<String, dynamic>.from(e))).toList();
  }

  Future<ProjectItem> getProject(String bookId) async {
    final resp = await _dio.get('/books/$bookId/project');
    return ProjectItem.fromJson(Map<String, dynamic>.from(resp.data as Map));
  }

  Future<String> pageText(String bookId, int pageIndex) async {
    final resp = await _dio.get('/books/$bookId/pages/$pageIndex/text');
    return resp.data['text'] as String? ?? '';
  }

  String pageImageUrl(String bookId, int pageIndex) =>
      '${AppConfig.apiBaseUrl}/books/$bookId/pages/$pageIndex/image';

  String annotationImageUrl(String bookId, String annotationId) =>
      '${AppConfig.apiBaseUrl}/books/$bookId/annotations/$annotationId/image';

  Future<Map<String, String>> authHeader() async {
    final token = await _auth.accessToken;
    return {if (token != null) 'Authorization': 'Bearer $token'};
  }

  Future<List<SearchHit>> search(String bookId, String q) async {
    final resp = await _dio.get('/books/$bookId/search', queryParameters: {'q': q});
    return (resp.data['hits'] as List)
        .map((e) => SearchHit.fromJson(Map<String, dynamic>.from(e)))
        .toList();
  }

  Future<List<TranslatedSegment>> translate(String bookId, int pageIndex, String lang) async {
    final resp = await _dio.post(
      '/books/$bookId/translate',
      data: {'page_index': pageIndex, 'target_lang': lang},
    );
    return (resp.data['segments'] as List)
        .map((e) => TranslatedSegment.fromJson(Map<String, dynamic>.from(e)))
        .toList();
  }

  Future<JobItem> exportEpub(String bookId) async {
    final resp = await _dio.post('/books/$bookId/export/epub');
    return JobItem.fromJson(Map<String, dynamic>.from(resp.data as Map));
  }

  Future<File> downloadEbook(String bookId, {required bool epub}) async {
    final suffix = epub ? 'epub' : 'pdf';
    final dir = await getTemporaryDirectory();
    final file = File('${dir.path}/$bookId.$suffix');
    await _dio.download('/books/$bookId/ebook.$suffix', file.path);
    return file;
  }

  Future<List<AnnotationItem>> listAnnotations(String bookId) async {
    final resp = await _dio.get('/books/$bookId/annotations');
    return (resp.data as List)
        .map((e) => AnnotationItem.fromJson(Map<String, dynamic>.from(e)))
        .toList();
  }

  Future<void> uploadAnnotationScans(String bookId, List<File> files, {int? pageIndex, String? opId}) async {
    final form = FormData.fromMap({
      'page_index': ?pageIndex,
      'client_op_id': ?opId,
      'files': [
        for (final f in files)
          await MultipartFile.fromFile(f.path, filename: f.uri.pathSegments.last),
      ],
    });
    await _dio.post('/books/$bookId/annotations', data: form);
  }

  Future<AnnotationItem> createTypedAnnotation(
    String bookId, {
    required String text,
    int? pageIndex,
    String? opId,
  }) async {
    final resp = await _dio.post(
      '/books/$bookId/annotations/typed',
      data: {'text': text, 'page_index': pageIndex, 'client_op_id': opId},
    );
    return AnnotationItem.fromJson(Map<String, dynamic>.from(resp.data as Map));
  }

  Future<void> updateAnnotation(String bookId, String id, {String? handwrittenText, int? pageIndex}) async {
    await _dio.patch(
      '/books/$bookId/annotations/$id',
      data: {
        'handwritten_text': ?handwrittenText,
        'page_index': ?pageIndex,
      },
    );
  }

  Future<JobItem> recook(String bookId) async {
    final resp = await _dio.post('/books/$bookId/recook');
    return JobItem.fromJson(Map<String, dynamic>.from(resp.data as Map));
  }

  Future<Map<String, dynamic>> sync({DateTime? since}) async {
    final resp = await _dio.get(
      '/sync',
      queryParameters: {if (since != null) 'since': since.toUtc().toIso8601String()},
    );
    return Map<String, dynamic>.from(resp.data as Map);
  }

  String prettyError(Object error) {
    if (error is DioException) {
      final data = error.response?.data;
      if (data is Map && data['detail'] != null) {
        return '${data['detail']}';
      }
      return error.message ?? error.toString();
    }
    return error.toString();
  }

  Future<void> enqueueOffline(String kind, Map<String, dynamic> payload) async {
    final prefsDir = await getApplicationSupportDirectory();
    final file = File('${prefsDir.path}/offline_queue.json');
    List list = [];
    if (await file.exists()) {
      list = jsonDecode(await file.readAsString()) as List;
    }
    list.add({'kind': kind, 'payload': payload, 'at': DateTime.now().toIso8601String()});
    await file.writeAsString(jsonEncode(list));
  }
}

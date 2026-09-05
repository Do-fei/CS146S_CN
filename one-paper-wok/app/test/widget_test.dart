import 'package:flutter_test/flutter_test.dart';

import 'package:one_paper_wok/core/config.dart';
import 'package:one_paper_wok/core/models.dart';
import 'package:one_paper_wok/theme/app_theme.dart';

void main() {
  test('BookItem parses sync payload', () {
    final book = BookItem.fromJson({
      'id': 'abc',
      'title': '思考，快与慢',
      'author': '卡尼曼',
      'status': 'done',
      'mode': 'full',
      'page_count': 12,
      'has_project': true,
      'project_version': 2,
      'ebook': {'has_pdf': true, 'has_epub': false},
      'deleted_at': null,
    });
    expect(book.isDone, isTrue);
    expect(book.hasProject, isTrue);
    expect(book.ebook.hasPdf, isTrue);
  });

  test('theme uses wok orange', () {
    final theme = buildWokTheme();
    expect(theme.colorScheme.primary, WokColors.orange);
  });

  test('JobItem terminal stages', () {
    expect(JobItem.fromJson({
      'id': '1',
      'book_id': 'b',
      'kind': 'cook',
      'stage': 'done',
      'progress': 100,
    }).isTerminal, isTrue);
    expect(JobItem.fromJson({
      'id': '1',
      'book_id': 'b',
      'kind': 'cook',
      'stage': 'ocr',
      'progress': 40,
    }).isTerminal, isFalse);
  });

  test('normalizeApiBaseUrl adds scheme and strips trailing slash', () {
    expect(normalizeApiBaseUrl('192.168.1.8:8000'), 'http://192.168.1.8:8000');
    expect(normalizeApiBaseUrl('http://10.0.0.2:8000/'), 'http://10.0.0.2:8000');
    expect(
      normalizeApiBaseUrl('one-paper-wok-production.up.railway.app/'),
      'https://one-paper-wok-production.up.railway.app',
    );
    expect(
      normalizeApiBaseUrl('https://one-paper-wok-production.up.railway.app'),
      'https://one-paper-wok-production.up.railway.app',
    );
  });
}

class UserMe {
  UserMe({required this.id, required this.email});
  final String id;
  final String email;
  factory UserMe.fromJson(Map<String, dynamic> json) =>
      UserMe(id: json['id'] as String, email: json['email'] as String);
}

class EbookInfo {
  EbookInfo({required this.hasPdf, required this.hasEpub});
  final bool hasPdf;
  final bool hasEpub;
  factory EbookInfo.fromJson(Map<String, dynamic>? json) => EbookInfo(
        hasPdf: json?['has_pdf'] == true,
        hasEpub: json?['has_epub'] == true,
      );
}

class BookItem {
  BookItem({
    required this.id,
    required this.title,
    this.author,
    required this.status,
    required this.mode,
    required this.pageCount,
    required this.hasProject,
    this.projectVersion,
    required this.ebook,
    this.deletedAt,
  });

  final String id;
  final String title;
  final String? author;
  final String status;
  final String mode;
  final int pageCount;
  final bool hasProject;
  final int? projectVersion;
  final EbookInfo ebook;
  final String? deletedAt;

  bool get isCooking => status == 'cooking';
  bool get isDone => status == 'done';

  factory BookItem.fromJson(Map<String, dynamic> json) => BookItem(
        id: json['id'] as String,
        title: json['title'] as String,
        author: json['author'] as String?,
        status: json['status'] as String? ?? 'preparing',
        mode: json['mode'] as String? ?? 'full',
        pageCount: json['page_count'] as int? ?? 0,
        hasProject: json['has_project'] == true,
        projectVersion: json['project_version'] as int?,
        ebook: EbookInfo.fromJson(json['ebook'] as Map<String, dynamic>?),
        deletedAt: json['deleted_at']?.toString(),
      );
}

class JobItem {
  JobItem({
    required this.id,
    required this.bookId,
    required this.kind,
    required this.stage,
    required this.progress,
    this.message,
    this.error,
  });
  final String id;
  final String bookId;
  final String kind;
  final String stage;
  final int progress;
  final String? message;
  final String? error;
  bool get isTerminal => stage == 'done' || stage == 'failed';
  factory JobItem.fromJson(Map<String, dynamic> json) => JobItem(
        id: json['id'] as String,
        bookId: json['book_id'] as String,
        kind: json['kind'] as String,
        stage: json['stage'] as String,
        progress: json['progress'] as int? ?? 0,
        message: json['message'] as String?,
        error: json['error'] as String?,
      );
}

class ChapterOutline {
  ChapterOutline({required this.title, required this.summary, this.startPage});
  final String title;
  final String summary;
  final int? startPage;
  factory ChapterOutline.fromJson(Map<String, dynamic> json) => ChapterOutline(
        title: json['title'] as String? ?? '',
        summary: json['summary'] as String? ?? '',
        startPage: json['start_page'] as int?,
      );
}

class PersonalInsight {
  PersonalInsight({this.annotationId, this.pageIndex, required this.text});
  final String? annotationId;
  final int? pageIndex;
  final String text;
  factory PersonalInsight.fromJson(Map<String, dynamic> json) => PersonalInsight(
        annotationId: json['annotation_id'] as String?,
        pageIndex: json['page_index'] as int?,
        text: json['text'] as String? ?? '',
      );
}

class ProjectItem {
  ProjectItem({
    required this.id,
    required this.bookId,
    required this.version,
    required this.summary,
    required this.keyInsights,
    required this.chapterOutline,
    required this.personalInsights,
  });
  final String id;
  final String bookId;
  final int version;
  final String summary;
  final List<String> keyInsights;
  final List<ChapterOutline> chapterOutline;
  final List<PersonalInsight> personalInsights;
  factory ProjectItem.fromJson(Map<String, dynamic> json) => ProjectItem(
        id: json['id'] as String,
        bookId: json['book_id'] as String,
        version: json['version'] as int? ?? 1,
        summary: json['summary'] as String? ?? '',
        keyInsights: (json['key_insights'] as List? ?? []).map((e) => '$e').toList(),
        chapterOutline: (json['chapter_outline'] as List? ?? [])
            .whereType<Map<String, dynamic>>()
            .map(ChapterOutline.fromJson)
            .toList(),
        personalInsights: (json['personal_insights'] as List? ?? [])
            .whereType<Map<String, dynamic>>()
            .map(PersonalInsight.fromJson)
            .toList(),
      );
}

class AnnotationItem {
  AnnotationItem({
    required this.id,
    required this.bookId,
    this.pageIndex,
    required this.source,
    required this.status,
    this.handwrittenText,
    this.refinedText,
    required this.hasImage,
    this.deletedAt,
  });
  final String id;
  final String bookId;
  final int? pageIndex;
  final String source;
  final String status;
  final String? handwrittenText;
  final String? refinedText;
  final bool hasImage;
  final String? deletedAt;
  factory AnnotationItem.fromJson(Map<String, dynamic> json) => AnnotationItem(
        id: json['id'] as String,
        bookId: json['book_id'] as String,
        pageIndex: json['page_index'] as int?,
        source: json['source'] as String? ?? 'scan',
        status: json['status'] as String? ?? 'pending',
        handwrittenText: json['handwritten_text'] as String?,
        refinedText: json['refined_text'] as String?,
        hasImage: json['has_image'] == true,
        deletedAt: json['deleted_at']?.toString(),
      );
}

class TranslatedSegment {
  TranslatedSegment({required this.segmentIndex, required this.source, required this.text});
  final int segmentIndex;
  final String source;
  final String text;
  factory TranslatedSegment.fromJson(Map<String, dynamic> json) => TranslatedSegment(
        segmentIndex: json['segment_index'] as int? ?? 0,
        source: json['source'] as String? ?? '',
        text: json['text'] as String? ?? '',
      );
}

class SearchHit {
  SearchHit({required this.pageIndex, required this.snippet});
  final int pageIndex;
  final String snippet;
  factory SearchHit.fromJson(Map<String, dynamic> json) => SearchHit(
        pageIndex: json['page_index'] as int? ?? 0,
        snippet: json['snippet'] as String? ?? '',
      );
}

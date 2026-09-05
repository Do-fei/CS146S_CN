package com.onepaper.app.data.local

import androidx.room.Database
import androidx.room.RoomDatabase

@Database(
    entities = [
        BookEntity::class,
        EditionEntity::class,
        ChapterEntity::class,
        PageEntity::class,
        NoteEntity::class,
        AnnotationEntity::class,
        ReadingPositionEntity::class,
        ProjectEntity::class,
        ProjectSectionEntity::class,
        ProposalEntity::class,
        ProposalItemEntity::class,
        ConversationEntity::class,
        MessageEntity::class,
        JobEntity::class,
    ],
    version = 1,
    exportSchema = false,
)
abstract class AppDatabase : RoomDatabase() {
    abstract fun bookDao(): BookDao
    abstract fun editionDao(): EditionDao
    abstract fun chapterDao(): ChapterDao
    abstract fun pageDao(): PageDao
    abstract fun noteDao(): NoteDao
    abstract fun annotationDao(): AnnotationDao
    abstract fun positionDao(): PositionDao
    abstract fun projectDao(): ProjectDao
    abstract fun sectionDao(): SectionDao
    abstract fun proposalDao(): ProposalDao
    abstract fun conversationDao(): ConversationDao
    abstract fun jobDao(): JobDao
    abstract fun backupDao(): BackupDao
}

package com.onepaper.app.data.local

import androidx.room.Database
import androidx.room.RoomDatabase
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase

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
    version = 3,
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

    companion object {
        val MIGRATION_1_2 = object : Migration(1, 2) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("ALTER TABLE messages ADD COLUMN quote TEXT")
                db.execSQL("ALTER TABLE messages ADD COLUMN locatorJson TEXT")
                db.execSQL("ALTER TABLE messages ADD COLUMN editionId TEXT")
            }
        }

        val MIGRATION_2_3 = object : Migration(2, 3) {
            override fun migrate(db: SupportSQLiteDatabase) {
                db.execSQL("ALTER TABLE books ADD COLUMN coverRelPath TEXT")
                db.execSQL("ALTER TABLE pages ADD COLUMN embeddedText TEXT")
                db.execSQL("ALTER TABLE pages ADD COLUMN hasTextLayer INTEGER NOT NULL DEFAULT 0")
                db.execSQL("ALTER TABLE pages ADD COLUMN ocrBoxesJson TEXT")
            }
        }
    }
}

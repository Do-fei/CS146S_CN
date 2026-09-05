package com.onepaper.app.di

import android.content.Context
import androidx.room.Room
import com.onepaper.app.data.local.AnnotationDao
import com.onepaper.app.data.local.AppDatabase
import com.onepaper.app.data.local.BackupDao
import com.onepaper.app.data.local.BookDao
import com.onepaper.app.data.local.ChapterDao
import com.onepaper.app.data.local.ConversationDao
import com.onepaper.app.data.local.EditionDao
import com.onepaper.app.data.local.JobDao
import com.onepaper.app.data.local.NoteDao
import com.onepaper.app.data.local.PageDao
import com.onepaper.app.data.local.PositionDao
import com.onepaper.app.data.local.ProjectDao
import com.onepaper.app.data.local.ProposalDao
import com.onepaper.app.data.local.SectionDao
import com.onepaper.app.data.ai.RoutingAiProvider
import com.onepaper.app.data.ocr.MlKitOcrEngine
import com.onepaper.domain.ai.AiProvider
import com.onepaper.domain.ai.FakeAiProvider
import com.onepaper.domain.ocr.FakeOcrEngine
import com.onepaper.domain.ocr.OcrEngine
import com.onepaper.domain.recook.RecookMerger
import dagger.Module
import dagger.Provides
import dagger.hilt.InstallIn
import dagger.hilt.android.qualifiers.ApplicationContext
import dagger.hilt.components.SingletonComponent
import javax.inject.Singleton

@Module
@InstallIn(SingletonComponent::class)
object AppModule {

    @Provides
    @Singleton
    fun database(@ApplicationContext context: Context): AppDatabase =
        Room.databaseBuilder(context, AppDatabase::class.java, "onepaper.db")
            .addMigrations(AppDatabase.MIGRATION_1_2)
            .fallbackToDestructiveMigration()
            .build()

    @Provides fun bookDao(db: AppDatabase): BookDao = db.bookDao()
    @Provides fun editionDao(db: AppDatabase): EditionDao = db.editionDao()
    @Provides fun chapterDao(db: AppDatabase): ChapterDao = db.chapterDao()
    @Provides fun pageDao(db: AppDatabase): PageDao = db.pageDao()
    @Provides fun noteDao(db: AppDatabase): NoteDao = db.noteDao()
    @Provides fun annotationDao(db: AppDatabase): AnnotationDao = db.annotationDao()
    @Provides fun positionDao(db: AppDatabase): PositionDao = db.positionDao()
    @Provides fun projectDao(db: AppDatabase): ProjectDao = db.projectDao()
    @Provides fun sectionDao(db: AppDatabase): SectionDao = db.sectionDao()
    @Provides fun proposalDao(db: AppDatabase): ProposalDao = db.proposalDao()
    @Provides fun conversationDao(db: AppDatabase): ConversationDao = db.conversationDao()
    @Provides fun jobDao(db: AppDatabase): JobDao = db.jobDao()
    @Provides fun backupDao(db: AppDatabase): BackupDao = db.backupDao()

    @Provides
    @Singleton
    fun fakeAiProvider(): FakeAiProvider = FakeAiProvider()

    @Provides
    @Singleton
    fun aiProvider(router: RoutingAiProvider): AiProvider = router

    @Provides
    @Singleton
    fun ocrEngine(): OcrEngine = try {
        MlKitOcrEngine()
    } catch (_: Throwable) {
        FakeOcrEngine()
    }

    @Provides
    @Singleton
    fun recookMerger(): RecookMerger = RecookMerger()
}

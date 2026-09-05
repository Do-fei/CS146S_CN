package com.onepaper.app.data.local

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query
import androidx.room.Update
import kotlinx.coroutines.flow.Flow

@Dao
interface BookDao {
    @Query("SELECT * FROM books WHERE deletedAt IS NULL ORDER BY createdAt DESC")
    fun observeActive(): Flow<List<BookEntity>>

    @Query("SELECT * FROM books WHERE id = :id")
    suspend fun get(id: String): BookEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(book: BookEntity)

    @Query("UPDATE books SET deletedAt = :now WHERE id = :id")
    suspend fun softDelete(id: String, now: Long)

    @Query("SELECT COUNT(*) FROM books WHERE deletedAt IS NULL")
    suspend fun activeCount(): Int

    @Query("SELECT * FROM books WHERE deletedAt IS NULL")
    suspend fun active(): List<BookEntity>
}

@Dao
interface EditionDao {
    @Query("SELECT * FROM editions WHERE bookId = :bookId")
    suspend fun forBook(bookId: String): List<EditionEntity>

    @Query("SELECT * FROM editions WHERE id = :id")
    suspend fun get(id: String): EditionEntity?

    @Query("SELECT * FROM editions")
    fun observeAll(): Flow<List<EditionEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(edition: EditionEntity)
}

@Dao
interface ChapterDao {
    @Query("SELECT * FROM chapters WHERE editionId = :editionId ORDER BY sortIndex")
    suspend fun forEdition(editionId: String): List<ChapterEntity>

    @Query("SELECT * FROM chapters WHERE editionId = :editionId ORDER BY sortIndex")
    fun observeForEdition(editionId: String): Flow<List<ChapterEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(items: List<ChapterEntity>)

    @Query("SELECT * FROM chapters")
    suspend fun all(): List<ChapterEntity>
}

@Dao
interface PageDao {
    @Query("SELECT * FROM pages WHERE editionId = :editionId ORDER BY `index`")
    suspend fun forEdition(editionId: String): List<PageEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(items: List<PageEntity>)

    @Update
    suspend fun update(page: PageEntity)
}

@Dao
interface NoteDao {
    @Query("SELECT * FROM notes ORDER BY updatedAt DESC")
    fun observeAll(): Flow<List<NoteEntity>>

    @Query("SELECT * FROM notes WHERE id = :id")
    suspend fun get(id: String): NoteEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(note: NoteEntity)

    @Query("DELETE FROM notes WHERE id = :id")
    suspend fun delete(id: String)

    @Query("SELECT COUNT(*) FROM notes")
    suspend fun count(): Int

    @Query("SELECT * FROM notes")
    suspend fun all(): List<NoteEntity>
}

@Dao
interface AnnotationDao {
    @Query("SELECT * FROM annotations WHERE bookId = :bookId")
    suspend fun forBook(bookId: String): List<AnnotationEntity>

    @Query("SELECT * FROM annotations ORDER BY createdAt DESC")
    fun observeAll(): Flow<List<AnnotationEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(item: AnnotationEntity)
}

@Dao
interface PositionDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(item: ReadingPositionEntity)

    @Query("SELECT * FROM reading_positions WHERE editionId = :editionId")
    suspend fun get(editionId: String): ReadingPositionEntity?

    @Query("SELECT * FROM reading_positions")
    fun observeAll(): Flow<List<ReadingPositionEntity>>
}

@Dao
interface ProjectDao {
    @Query("SELECT * FROM projects")
    fun observeAll(): Flow<List<ProjectEntity>>

    @Query("SELECT * FROM projects WHERE id = :id")
    suspend fun get(id: String): ProjectEntity?

    @Query("SELECT * FROM projects WHERE bookId = :bookId LIMIT 1")
    suspend fun forBook(bookId: String): ProjectEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(project: ProjectEntity)

    @Query("SELECT COUNT(*) FROM projects")
    suspend fun count(): Int
}

@Dao
interface SectionDao {
    @Query("SELECT * FROM project_sections WHERE projectId = :projectId ORDER BY sortIndex")
    suspend fun forProject(projectId: String): List<ProjectSectionEntity>

    @Query("SELECT * FROM project_sections WHERE projectId = :projectId ORDER BY sortIndex")
    fun observeForProject(projectId: String): Flow<List<ProjectSectionEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertAll(items: List<ProjectSectionEntity>)

    @Query("DELETE FROM project_sections WHERE projectId = :projectId")
    suspend fun deleteForProject(projectId: String)
}

@Dao
interface ProposalDao {
    @Query("SELECT * FROM proposals WHERE projectId = :projectId ORDER BY createdAt DESC")
    suspend fun forProject(projectId: String): List<ProposalEntity>

    @Query("SELECT * FROM proposals WHERE id = :id")
    suspend fun get(id: String): ProposalEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(item: ProposalEntity)

    @Query("SELECT * FROM proposal_items WHERE proposalId = :proposalId")
    suspend fun items(proposalId: String): List<ProposalItemEntity>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertItem(item: ProposalItemEntity)
}

@Dao
interface ConversationDao {
    @Query("SELECT * FROM conversations WHERE bookId = :bookId")
    suspend fun forBook(bookId: String): ConversationEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(item: ConversationEntity)

    @Query("SELECT * FROM messages WHERE conversationId = :id ORDER BY createdAt")
    fun observeMessages(id: String): Flow<List<MessageEntity>>

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsertMessage(item: MessageEntity)
}

@Dao
interface JobDao {
    @Query("SELECT * FROM jobs ORDER BY updatedAt DESC")
    fun observeAll(): Flow<List<JobEntity>>

    @Query("SELECT * FROM jobs WHERE clientJobId = :id")
    suspend fun get(id: String): JobEntity?

    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun upsert(job: JobEntity)
}

@Dao
interface BackupDao {
    @Query("SELECT * FROM books")
    suspend fun allBooks(): List<BookEntity>

    @Query("SELECT * FROM editions")
    suspend fun allEditions(): List<EditionEntity>

    @Query("SELECT * FROM notes")
    suspend fun allNotes(): List<NoteEntity>

    @Query("SELECT * FROM projects")
    suspend fun allProjects(): List<ProjectEntity>

    @Query("SELECT * FROM project_sections")
    suspend fun allSections(): List<ProjectSectionEntity>
}

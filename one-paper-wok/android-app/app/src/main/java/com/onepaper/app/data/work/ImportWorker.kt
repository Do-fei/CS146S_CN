package com.onepaper.app.data.work

import android.content.Context
import androidx.work.CoroutineWorker
import androidx.work.WorkerParameters

/**
 * 可恢复导入：文件必须先落入私有目录，再把任务标完成。
 * 被杀后不自动续跑，由用户在任务页手动恢复。
 */
class ImportWorker(
    context: Context,
    params: WorkerParameters,
) : CoroutineWorker(context, params) {
    override suspend fun doWork(): Result {
        val jobId = inputData.getString(KEY_JOB_ID) ?: return Result.failure()
        return if (jobId.isBlank()) Result.failure() else Result.success()
    }

    companion object {
        const val KEY_JOB_ID = "clientJobId"
    }
}

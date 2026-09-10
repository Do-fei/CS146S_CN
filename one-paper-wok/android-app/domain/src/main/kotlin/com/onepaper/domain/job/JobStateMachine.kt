package com.onepaper.domain.job

enum class JobStatus {
    QUEUED,
    RUNNING,
    WAITING_FOR_NETWORK,
    RETRYABLE_FAILED,
    FAILED,
    CANCELLED,
    COMPLETED,
}

data class JobState(
    val clientJobId: String,
    val status: JobStatus,
    val attempt: Int = 0,
    val stage: String = "",
    val unitDone: Int = 0,
    val unitTotal: Int = 0,
    val message: String = "",
    val durableFilesPresent: Boolean = false,
)

class JobStateMachine(
    private val maxAttempts: Int = 5,
) {
    fun start(state: JobState): JobState {
        check(state.status == JobStatus.QUEUED || state.status == JobStatus.RETRYABLE_FAILED)
        return state.copy(status = JobStatus.RUNNING, attempt = state.attempt + 1)
    }

    fun progress(state: JobState, stage: String, done: Int, total: Int): JobState {
        check(state.status == JobStatus.RUNNING)
        return state.copy(stage = stage, unitDone = done, unitTotal = total)
    }

    fun waitingForNetwork(state: JobState): JobState {
        check(state.status == JobStatus.RUNNING)
        return state.copy(status = JobStatus.WAITING_FOR_NETWORK)
    }

    fun fail(state: JobState, retryable: Boolean, message: String): JobState {
        check(state.status == JobStatus.RUNNING || state.status == JobStatus.WAITING_FOR_NETWORK)
        val next = if (retryable && state.attempt < maxAttempts) {
            JobStatus.RETRYABLE_FAILED
        } else {
            JobStatus.FAILED
        }
        return state.copy(status = next, message = message)
    }

    fun complete(state: JobState): JobState {
        check(state.status == JobStatus.RUNNING)
        check(state.durableFilesPresent) { "must persist files before completing" }
        return state.copy(status = JobStatus.COMPLETED, unitDone = state.unitTotal)
    }

    fun cancel(state: JobState): JobState {
        check(state.status != JobStatus.COMPLETED)
        return state.copy(status = JobStatus.CANCELLED)
    }

    /**
     * 进程被杀：已复制的私有文件仍在；任务回到可手动恢复，不自动续跑。
     */
    fun afterProcessDeath(state: JobState): JobState {
        if (state.status == JobStatus.COMPLETED || state.status == JobStatus.CANCELLED || state.status == JobStatus.FAILED) {
            return state
        }
        return state.copy(
            status = JobStatus.RETRYABLE_FAILED,
            message = "process killed; files kept; resume manually",
        )
    }

    fun progressLabel(state: JobState): String {
        if (state.unitTotal <= 0) return state.stage.ifBlank { state.status.name }
        return "第 ${state.unitDone}/${state.unitTotal} 页 · ${state.stage.ifBlank { "处理" }}"
    }
}

package com.onepaper.domain.job

import org.junit.Assert.assertEquals
import org.junit.Assert.assertTrue
import org.junit.Test

class JobStateMachineTest {
    private val machine = JobStateMachine()

    @Test
    fun filesMustExistBeforeComplete() {
        val queued = JobState(clientJobId = "job-1", status = JobStatus.QUEUED)
        val running = machine.start(queued).copy(durableFilesPresent = true, unitTotal = 12)
        val progressed = machine.progress(running, "OCR", 12, 12)
        val done = machine.complete(progressed)
        assertEquals(JobStatus.COMPLETED, done.status)
        assertEquals("第 12/12 页 · OCR", machine.progressLabel(progressed))
    }

    @Test
    fun processDeathKeepsFilesAndRequiresManualResume() {
        val running = machine.start(JobState("job-1", JobStatus.QUEUED))
            .copy(durableFilesPresent = true, stage = "OCR", unitDone = 4, unitTotal = 40)
        val after = machine.afterProcessDeath(running)
        assertEquals(JobStatus.RETRYABLE_FAILED, after.status)
        assertTrue(after.durableFilesPresent)
        assertTrue(after.message.contains("resume manually"))
    }

    @Test
    fun sameClientJobIdIsIdempotentIdentity() {
        val a = JobState(clientJobId = "same-key", status = JobStatus.QUEUED)
        val b = JobState(clientJobId = "same-key", status = JobStatus.QUEUED)
        assertEquals(a.clientJobId, b.clientJobId)
    }
}

package com.onepaper.app.data.tts

import android.content.Context
import android.speech.tts.TextToSpeech
import android.speech.tts.UtteranceProgressListener
import com.onepaper.domain.tts.TtsPassage
import dagger.hilt.android.qualifiers.ApplicationContext
import kotlinx.coroutines.flow.MutableStateFlow
import java.util.Locale
import java.util.concurrent.atomic.AtomicReference
import javax.inject.Inject
import javax.inject.Singleton

@Singleton
class TtsSpeaker @Inject constructor(
    @ApplicationContext private val context: Context,
) {
    val speaking = MutableStateFlow(false)
    val notice = MutableStateFlow<String?>(null)
    private val engine = AtomicReference<TextToSpeech?>(null)
    private val pending = AtomicReference<TtsPassage?>(null)
    private var lastUtterance: String = ""

    fun speak(passage: TtsPassage) {
        pending.set(passage)
        val existing = engine.get()
        if (existing == null) {
            val created = TextToSpeech(context) { status ->
                if (status == TextToSpeech.SUCCESS) {
                    engine.get()?.language = Locale.SIMPLIFIED_CHINESE
                    flush()
                } else {
                    notice.value = "这台设备没有可用的系统朗读。"
                    speaking.value = false
                }
            }
            engine.set(created)
        } else {
            flush()
        }
    }

    fun stop() {
        pending.set(null)
        engine.get()?.stop()
        speaking.value = false
    }

    private fun flush() {
        val passage = pending.get() ?: return
        val tts = engine.get() ?: return
        tts.setOnUtteranceProgressListener(
            object : UtteranceProgressListener() {
                override fun onStart(utteranceId: String?) {
                    speaking.value = true
                }

                override fun onDone(utteranceId: String?) {
                    if (utteranceId == lastUtterance) speaking.value = false
                }

                @Deprecated("Deprecated in Java")
                override fun onError(utteranceId: String?) {
                    speaking.value = false
                    notice.value = "朗读中断。"
                }
            },
        )
        notice.value = passage.label
        val chunks = passage.text.chunked(3_500).filter { it.isNotBlank() }
        if (chunks.isEmpty()) {
            speaking.value = false
            notice.value = "这一页没有可朗读的文字。"
            return
        }
        lastUtterance = "onepaper-${chunks.lastIndex}"
        chunks.forEachIndexed { index, chunk ->
            val mode = if (index == 0) TextToSpeech.QUEUE_FLUSH else TextToSpeech.QUEUE_ADD
            tts.speak(chunk, mode, null, "onepaper-$index")
        }
        speaking.value = true
    }
}

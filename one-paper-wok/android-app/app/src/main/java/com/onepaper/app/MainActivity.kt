package com.onepaper.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import com.onepaper.app.data.prefs.UserPrefs
import com.onepaper.app.ui.nav.OnePaperRoot
import com.onepaper.app.ui.theme.OnePaperTheme
import dagger.hilt.android.AndroidEntryPoint
import javax.inject.Inject

@AndroidEntryPoint
class MainActivity : ComponentActivity() {
    @Inject lateinit var prefs: UserPrefs

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        setContent {
            val dark by prefs.darkTheme.collectAsStateWithLifecycle(initialValue = false)
            OnePaperTheme(darkTheme = dark) {
                OnePaperRoot(modifier = Modifier.fillMaxSize())
            }
        }
    }
}

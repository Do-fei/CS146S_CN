package com.onepaper.app.ui.nav

import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.CircularProgressIndicator
import androidx.compose.runtime.Composable
import androidx.compose.runtime.getValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.hilt.navigation.compose.hiltViewModel
import androidx.lifecycle.compose.collectAsStateWithLifecycle
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.rememberNavController
import com.onepaper.app.ui.screens.BackupScreen
import com.onepaper.app.ui.screens.BookScreen
import com.onepaper.app.ui.screens.CaptureScreen
import com.onepaper.app.ui.screens.CompanionScreen
import com.onepaper.app.ui.screens.ExportScreen
import com.onepaper.app.ui.screens.HandwritingScreen
import com.onepaper.app.ui.screens.HomePager
import com.onepaper.app.ui.screens.ImportScreen
import com.onepaper.app.ui.screens.NoteScreen
import com.onepaper.app.ui.screens.OnboardingScreen
import com.onepaper.app.ui.screens.PagesScreen
import com.onepaper.app.ui.screens.ProjectScreen
import com.onepaper.app.ui.screens.ReaderScreen
import com.onepaper.app.ui.screens.RecookScreen
import com.onepaper.app.ui.screens.SettingsScreen
import com.onepaper.app.ui.screens.TaskScreen
import com.onepaper.app.ui.vm.ShelfViewModel

@Composable
fun OnePaperRoot(modifier: Modifier = Modifier) {
    val nav = rememberNavController()
    val shelf: ShelfViewModel = hiltViewModel()
    val onboarded by shelf.onboardingDone.collectAsStateWithLifecycle()
    if (onboarded == null) {
        Box(modifier.fillMaxSize(), contentAlignment = Alignment.Center) {
            CircularProgressIndicator()
        }
        return
    }
    val start = if (onboarded == true) Routes.Home else Routes.Onboarding

    NavHost(navController = nav, startDestination = start, modifier = modifier) {
        composable(Routes.Onboarding) {
            OnboardingScreen(
                onImport = { nav.navigate(Routes.Import) },
                onCapture = { nav.navigate(Routes.Capture) },
                onLater = {
                    nav.navigate(Routes.Home) {
                        popUpTo(Routes.Onboarding) { inclusive = true }
                    }
                },
            )
        }
        composable(Routes.Home) {
            HomePager(
                onOpenBook = { nav.navigate(Routes.book(it)) },
                onImport = { nav.navigate(Routes.Import) },
                onCapture = { nav.navigate(Routes.Capture) },
                onOpenProject = { nav.navigate(Routes.project(it)) },
                onOpenNote = { nav.navigate(Routes.note(it)) },
                onSettings = { nav.navigate(Routes.Settings) },
                onBackup = { nav.navigate(Routes.Backup) },
                onTask = { nav.navigate(Routes.task(it)) },
            )
        }
        composable(Routes.Book) {
            BookScreen(
                onOpenReader = { nav.navigate(Routes.reader(it)) },
                onOpenCompanion = { nav.navigate(Routes.companion(it)) },
                onOpenProject = { nav.navigate(Routes.project(it)) },
                onOpenPages = { nav.navigate(Routes.pages(it)) },
                onBack = { nav.popBackStack() },
            )
        }
        composable(Routes.Reader) {
            ReaderScreen(
                onCompanion = { bookId, _ -> nav.navigate(Routes.companion(bookId)) },
                onBack = { nav.popBackStack() },
            )
        }
        composable(Routes.Import) { ImportScreen(onDone = { nav.popBackStack() }) }
        composable(Routes.Capture) {
            CaptureScreen(onDone = { nav.popBackStack() }, onImport = { nav.navigate(Routes.Import) })
        }
        composable(Routes.Pages) { PagesScreen(onBack = { nav.popBackStack() }) }
        composable(Routes.Task) { TaskScreen(onBack = { nav.popBackStack() }) }
        composable(Routes.Project) {
            ProjectScreen(
                onRecook = { nav.navigate(Routes.recook(it)) },
                onExport = { nav.navigate(Routes.export(it)) },
                onBack = { nav.popBackStack() },
            )
        }
        composable(Routes.Recook) { RecookScreen(onBack = { nav.popBackStack() }) }
        composable(Routes.Companion) { CompanionScreen(onBack = { nav.popBackStack() }) }
        composable(Routes.Note) {
            NoteScreen(
                onBack = { nav.popBackStack() },
                onHandwriting = { nav.navigate(Routes.handwriting(it)) },
            )
        }
        composable(Routes.Export) { ExportScreen(onBack = { nav.popBackStack() }) }
        composable(Routes.Backup) { BackupScreen(onBack = { nav.popBackStack() }) }
        composable(Routes.Settings) { SettingsScreen(onBack = { nav.popBackStack() }) }
        composable(Routes.Handwriting) { HandwritingScreen(onBack = { nav.popBackStack() }) }
    }
}

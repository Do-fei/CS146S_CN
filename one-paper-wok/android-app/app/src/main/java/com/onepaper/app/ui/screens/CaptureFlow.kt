package com.onepaper.app.ui.screens

import android.Manifest
import android.content.pm.PackageManager
import android.graphics.Bitmap
import android.net.Uri
import android.view.ViewGroup
import androidx.activity.compose.rememberLauncherForActivityResult
import androidx.activity.result.contract.ActivityResultContracts
import androidx.camera.core.CameraSelector
import androidx.camera.core.ImageCapture
import androidx.camera.core.ImageCaptureException
import androidx.camera.core.Preview
import androidx.camera.lifecycle.ProcessCameraProvider
import androidx.camera.view.PreviewView
import androidx.compose.foundation.Image
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Box
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.aspectRatio
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
import androidx.compose.foundation.layout.height
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Slider
import androidx.compose.material3.SliderDefaults
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.DisposableEffect
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableFloatStateOf
import androidx.compose.runtime.mutableIntStateOf
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.graphics.asImageBitmap
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.compose.ui.viewinterop.AndroidView
import androidx.core.content.ContextCompat
import androidx.core.content.FileProvider
import androidx.lifecycle.compose.LocalLifecycleOwner
import com.onepaper.app.data.image.CaptureBitmap
import com.onepaper.app.ui.components.Banner
import com.onepaper.app.ui.components.QuietButton
import com.onepaper.app.ui.components.QuietTone
import com.onepaper.app.ui.graphics.ZenGlyph
import com.onepaper.domain.image.NormCrop
import java.io.File

private enum class CaptureStage { Ready, Camera, Crop }

@Composable
fun CaptureStudio(
    bitmaps: CaptureBitmap,
    onImported: (List<Uri>) -> Unit,
) {
    val context = LocalContext.current
    var hasCamera by remember {
        mutableStateOf(
            ContextCompat.checkSelfPermission(context, Manifest.permission.CAMERA) ==
                PackageManager.PERMISSION_GRANTED,
        )
    }
    var stage by remember { mutableStateOf(CaptureStage.Ready) }
    var pending by remember { mutableStateOf<Uri?>(null) }
    var cameraError by remember { mutableStateOf<String?>(null) }
    val permission = rememberLauncherForActivityResult(ActivityResultContracts.RequestPermission()) { granted ->
        hasCamera = granted
        if (granted) stage = CaptureStage.Camera
    }
    val picker = rememberLauncherForActivityResult(ActivityResultContracts.GetMultipleContents()) { uris ->
        when {
            uris.size == 1 -> {
                pending = uris.first()
                stage = CaptureStage.Crop
            }
            uris.size > 1 -> onImported(uris)
        }
    }

    when (stage) {
        CaptureStage.Ready -> Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
            QuietButton(
                "拍照",
                {
                    if (hasCamera) {
                        stage = CaptureStage.Camera
                    } else {
                        permission.launch(Manifest.permission.CAMERA)
                    }
                },
                Modifier.fillMaxWidth(),
                glyph = ZenGlyph.Camera,
                tone = QuietTone.Ink,
            )
            QuietButton("从相册选页", { picker.launch("image/*") }, Modifier.fillMaxWidth(), glyph = ZenGlyph.Scan)
            cameraError?.let { Banner(it) }
            if (!hasCamera) {
                Banner("也可以从相册选。")
            }
        }
        CaptureStage.Camera -> CameraPane(
            onCaptured = { uri ->
                pending = uri
                stage = CaptureStage.Crop
            },
            onCancel = { stage = CaptureStage.Ready },
            onError = {
                cameraError = it
                stage = CaptureStage.Ready
            },
        )
        CaptureStage.Crop -> {
            val uri = pending
            if (uri == null) {
                Banner("没有待裁切的图像。")
                QuietButton("返回", { stage = CaptureStage.Ready }, Modifier.fillMaxWidth())
            } else {
                CropRotatePane(
                    uri = uri,
                    bitmaps = bitmaps,
                    onConfirm = { cropped ->
                        onImported(listOf(cropped))
                        pending = null
                        stage = CaptureStage.Ready
                    },
                    onCancel = {
                        pending = null
                        stage = CaptureStage.Ready
                    },
                )
            }
        }
    }
}

@Composable
private fun CropRotatePane(
    uri: Uri,
    bitmaps: CaptureBitmap,
    onConfirm: (Uri) -> Unit,
    onCancel: () -> Unit,
) {
    val context = LocalContext.current
    val source = remember(uri) { bitmaps.decode(context, uri) }
    var rotation by remember { mutableIntStateOf(0) }
    var left by remember { mutableFloatStateOf(0.05f) }
    var top by remember { mutableFloatStateOf(0.05f) }
    var right by remember { mutableFloatStateOf(0.05f) }
    var bottom by remember { mutableFloatStateOf(0.05f) }
    var preview by remember { mutableStateOf<Bitmap?>(null) }
    var error by remember { mutableStateOf<String?>(null) }
    val box = NormCrop.clamp(
        left.toDouble(),
        top.toDouble(),
        (1f - right).toDouble(),
        (1f - bottom).toDouble(),
    )
    LaunchedEffect(source, rotation, left, top, right, bottom) {
        preview = source?.let { bitmaps.apply(it, box, rotation) }
    }
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Text("裁切与旋转", style = MaterialTheme.typography.titleMedium)
        Text("转到正向，再裁切。", style = MaterialTheme.typography.bodySmall)
        val shown = preview ?: source
        if (shown != null) {
            Image(
                shown.asImageBitmap(),
                contentDescription = "裁切预览",
                modifier = Modifier.fillMaxWidth().height(320.dp),
            )
        } else {
            Banner("打不开这张图。")
        }
        QuietButton(
            "顺时针旋转 90°",
            { rotation = NormCrop.rotateClockwise(rotation) },
            Modifier.fillMaxWidth(),
            glyph = ZenGlyph.Scan,
        )
        CropSlider("左边", left) { left = it }
        CropSlider("上边", top) { top = it }
        CropSlider("右边", right) { right = it }
        CropSlider("下边", bottom) { bottom = it }
        error?.let { Banner(it) }
        QuietButton(
            "确认",
            {
                val cropped = preview ?: source
                if (cropped == null) {
                    error = "没有可保存的图像。"
                    return@QuietButton
                }
                onConfirm(bitmaps.writeJpeg(context, cropped))
            },
            Modifier.fillMaxWidth(),
            tone = QuietTone.Ink,
            glyph = ZenGlyph.Camera,
        )
        QuietButton("取消", onCancel, Modifier.fillMaxWidth(), tone = QuietTone.Ghost)
    }
}

@Composable
private fun CropSlider(label: String, value: Float, onChange: (Float) -> Unit) {
    val scheme = MaterialTheme.colorScheme
    Column {
        Text("$label ${"%.0f".format(value * 100)}%", style = MaterialTheme.typography.bodySmall)
        Slider(
            value = value,
            onValueChange = onChange,
            valueRange = 0f..0.4f,
            colors = SliderDefaults.colors(
                thumbColor = scheme.onSurface,
                activeTrackColor = scheme.onSurface,
                inactiveTrackColor = scheme.outlineVariant,
            ),
        )
    }
}

@Composable
private fun CameraPane(
    onCaptured: (Uri) -> Unit,
    onCancel: () -> Unit,
    onError: (String) -> Unit,
) {
    val context = LocalContext.current
    val lifecycleOwner = LocalLifecycleOwner.current
    val previewView = remember {
        PreviewView(context).apply {
            layoutParams = ViewGroup.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT,
                ViewGroup.LayoutParams.MATCH_PARENT,
            )
            scaleType = PreviewView.ScaleType.FILL_CENTER
        }
    }
    val capture = remember { ImageCapture.Builder().build() }
    DisposableEffect(lifecycleOwner) {
        val future = ProcessCameraProvider.getInstance(context)
        val main = ContextCompat.getMainExecutor(context)
        future.addListener(
            {
                runCatching {
                    val provider = future.get()
                    val preview = Preview.Builder().build().also { built ->
                        built.setSurfaceProvider(previewView.surfaceProvider)
                    }
                    provider.unbindAll()
                    provider.bindToLifecycle(
                        lifecycleOwner,
                        CameraSelector.DEFAULT_BACK_CAMERA,
                        preview,
                        capture,
                    )
                }.onFailure { onError(it.message ?: "相机无法启动") }
            },
            main,
        )
        onDispose {
            runCatching { future.get().unbindAll() }
        }
    }
    Column(verticalArrangement = Arrangement.spacedBy(12.dp)) {
        Box(Modifier.fillMaxWidth().aspectRatio(3f / 4f)) {
            AndroidView(factory = { previewView }, modifier = Modifier.fillMaxSize())
        }
        QuietButton(
            "快门",
            {
                val file = File(File(context.cacheDir, "captures").apply { mkdirs() }, "cap-${System.currentTimeMillis()}.jpg")
                val options = ImageCapture.OutputFileOptions.Builder(file).build()
                capture.takePicture(
                    options,
                    ContextCompat.getMainExecutor(context),
                    object : ImageCapture.OnImageSavedCallback {
                        override fun onImageSaved(outputFileResults: ImageCapture.OutputFileResults) {
                            val uri = FileProvider.getUriForFile(context, "${context.packageName}.files", file)
                            onCaptured(uri)
                        }

                        override fun onError(exception: ImageCaptureException) {
                            onError(exception.message ?: "拍照失败")
                        }
                    },
                )
            },
            Modifier.fillMaxWidth(),
            tone = QuietTone.Ink,
            glyph = ZenGlyph.Camera,
        )
        QuietButton("取消拍照", onCancel, Modifier.fillMaxWidth(), tone = QuietTone.Ghost)
    }
}

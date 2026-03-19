---
title: "Uploading Large Videos in Flutter: Surviving Background Kills on iOS and Android"
date: "2026-03-19T00:00:00.000Z"
template: "post"
draft: false
slug: "/posts/background-video-uploads-in-flutter"
category: "Software Engineering"
tags:
  - "Software Engineering"
  - "Flutter"
  - "Mobile Development"
description: "How we solved large video uploads that kept dying when users switched apps."
socialImage: "./image.jpg"
---

If you've ever tried uploading large video files from a Flutter app, you've probably hit this: the user switches to another app, and the upload silently dies. On iOS especially, this happens fast. The system kills your app, and the upload is gone — no warning, no callback, nothing.

We ran into this problem. Our app lets users upload videos that can be several hundred megabytes. On a typical mobile connection, that takes minutes. The moment the user checks a message or locks the screen, the upload fails.

The root cause is simple. A regular HTTP upload runs inside your app's process. When the system suspends or kills that process, the upload goes with it. We needed the upload to keep going even if the app is no longer running.

Here's how we solved it.

## The Package

We used the [`background_downloader`](https://pub.dev/packages/background_downloader) package. Despite the name, it handles uploads too.

What it does is hand off the upload to the operating system itself:

- On **iOS**, it uses a background URL session — the system manages the transfer even if the app is killed.
- On **Android**, it runs the upload as a foreground service — a persistent task that the system won't easily stop.

Here's everything we changed across Flutter, iOS, and Android.

## Flutter: The Upload Code

This is the main upload class. A few things worth noting:

- `init()` sets up task tracking and the Android foreground service once.
- Task tracking lets us recover uploads that finished while the app was closed.
- On Android, `Config.runInForeground` prevents the system from stopping the upload.

```dart
import 'dart:async';
import 'dart:io';

import 'package:background_downloader/background_downloader.dart';
import 'package:flutter/foundation.dart';
import 'package:logging/logging.dart';
import 'package:mime/mime.dart';
import 'package:path/path.dart' as path;

final _log = Logger('VideoUploader');

class VideoUploader {
  bool _initialized = false;

  Future<void> init() async {
    if (_initialized) return;
    _initialized = true;

    if (kDebugMode) {
      Logger.root.level = Level.ALL;
      Logger.root.onRecord.listen((record) {
        debugPrint(
          '[${record.loggerName}] ${record.level.name}: ${record.message}',
        );
      });
    }

    // Track tasks so we can recover uploads after app restart
    FileDownloader().trackTasks();

    if (Platform.isAndroid) {
      await FileDownloader().configure(
        globalConfig: [(Config.runInForeground, Config.always)],
      );
    }

    _log.info('VideoUploader initialized with task tracking enabled');
  }

  Future<bool> uploadVideo({
    required File file,
    required String uploadURL,
    required String title,
    required Function(int current, int total) onUploadProgress,
  }) async {
    await init();

    String? mimeType = lookupMimeType(file.path) ?? 'application/octet-stream';
    final fileSize = await file.length();

    _log.info('Starting upload: path=${file.path}, size=$fileSize, '
        'mimeType=$mimeType, platform=${Platform.operatingSystem}');

    final task = UploadTask(
      url: uploadURL,
      baseDirectory: BaseDirectory.root,
      directory: file.path.replaceFirst(file.uri.pathSegments.last, ''),
      filename: file.uri.pathSegments.last,
      httpRequestMethod: 'PUT',
      fileField: 'file',
      post: 'binary',
      updates: Updates.statusAndProgress,
      headers: {
        'Content-Type': mimeType,
        'Content-Length': fileSize.toString(),
      },
    );

    if (Platform.isAndroid) {
      FileDownloader().configureNotification(
        running: TaskNotification('Uploading', '$title {progress}'),
        complete: TaskNotification('Upload complete', title),
        error: TaskNotification('Upload failed', title),
        progressBar: true,
      );
    }

    final result = await FileDownloader().upload(
      task,
      onProgress: (progress) {
        final clampedProgress = progress.clamp(0.0, 1.0);
        final currentBytes = (clampedProgress * fileSize).toInt();
        onUploadProgress(currentBytes, fileSize);
        if (kDebugMode) {
          _log.fine(
              'Upload progress: ${(clampedProgress * 100).toStringAsFixed(1)}% '
              '($currentBytes/$fileSize bytes)');
        }
      },
      onStatus: (status) {
        _log.info('Upload status changed: $status');
      },
    );

    if (result.status == TaskStatus.complete) {
      _log.info('Upload completed successfully');
      return true;
    } else {
      _log.warning('Upload failed: status=${result.status}');
      return false;
    }
  }
}
```

One important detail: `trackTasks()` is what lets you reconnect to uploads that finished while the app was closed. Without it, you have no way of knowing whether an upload succeeded or failed after the app was killed.

## App Initialization: Recovering Interrupted Uploads

In your app startup, before `runApp()`, add this:

```dart
await FileDownloader().start(doRescheduleKilledTasks: true);
```

This tells the downloader to automatically retry any uploads that were interrupted when the system killed the app. Without it, those interrupted uploads are just lost.

## iOS Configuration

iOS is where most of the work is. Two changes are needed.

### Info.plist — Background Modes

Add `processing` to your background modes:

```xml
<key>UIBackgroundModes</key>
<array>
    <string>fetch</string>
    <string>processing</string>
    <string>remote-notification</string>
</array>
```

This tells iOS that your app does work that should continue in the background.

### AppDelegate.swift — The Part Most People Miss

This was our most time-consuming issue to debug. When iOS finishes a background upload after your app was killed, it relaunches the app and sends an event. You need to forward that event to the Flutter plugin. If you don't, the plugin never finds out the upload finished, and your app can't update accordingly.

```swift
import UIKit
import Flutter

@main
@objc class AppDelegate: FlutterAppDelegate {
  override func application(
    _ application: UIApplication,
    didFinishLaunchingWithOptions launchOptions: [UIApplication.LaunchOptionsKey: Any]?
  ) -> Bool {
    GeneratedPluginRegistrant.register(with: self)
    return super.application(application, didFinishLaunchingWithOptions: launchOptions)
  }

  // Forward background URL session events to the plugin.
  // Without this, uploads that complete while the app is killed
  // will not be reported back to your Flutter code.
  override func application(
    _ application: UIApplication,
    handleEventsForBackgroundURLSession identifier: String,
    completionHandler: @escaping () -> Void
  ) {
    super.application(application,
                      handleEventsForBackgroundURLSession: identifier,
                      completionHandler: completionHandler)
  }
}
```

Without this override, uploads work perfectly in the foreground but silently disappear when the app is in the background. That's a frustrating one to track down.

## Android Configuration

Android is more straightforward. You need permissions and a foreground service declaration in your `AndroidManifest.xml`:

```xml
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.FOREGROUND_SERVICE"/>
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC"/>

    <application
        android:label="@string/app_name"
        android:name="${applicationName}"
        android:icon="@mipmap/ic_launcher">

        <!-- your existing activity and meta-data -->

        <service
            android:name="androidx.work.impl.foreground.SystemForegroundService"
            android:foregroundServiceType="dataSync"
            android:exported="false" />
    </application>
</manifest>
```

The two permissions allow the app to run a foreground service. The service declaration registers it as a data sync type, which shows a notification during the upload. On Android, foreground services require a visible notification — it's not optional.

## Dependencies

Add these to your `pubspec.yaml`:

```yaml
dependencies:
  background_downloader: ^9.2.3
  logging: ^1.3.0
  mime: ^2.0.0
```

## Things Worth Knowing

A few things we learned along the way:

- **iOS doesn't guarantee when background uploads finish.** The system decides based on battery, network, and other factors. Don't promise users an exact time.
- **Task tracking must be set up before uploads start.** Call `trackTasks()` during initialization, not after.
- **Test on a real device.** The iOS Simulator doesn't accurately reproduce what happens when the system kills your app. Use a real phone, start an upload, switch apps, and force-kill from the app switcher.

## Wrapping Up

Background uploads in Flutter need setup across three layers: Dart, iOS, and Android. The `background_downloader` package handles the heavy lifting, but each platform needs the right configuration to support it.

The most important piece — and the easiest to miss — is the iOS AppDelegate forwarding. Without it, everything works fine in the foreground and silently fails in the background. That one cost us hours. Hopefully this saves you the same trouble. ✌️

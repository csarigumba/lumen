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
socialImage: "./image1.jpg"
---

![Uploading Large Videos in Flutter](./image1.jpg)

If you've ever tried uploading large video files from a Flutter app, you've probably hit this: the user switches to another app, and the upload silently dies. On iOS especially, this happens fast. The system kills your app, and the upload is gone. No warning, no callback, nothing.

We ran into this problem. Our app lets users upload videos that can be several hundred megabytes. On a typical mobile connection, that takes minutes. The moment the user checks a message or locks the screen, the upload fails.

The reason is simple. A regular HTTP upload runs inside your app's process. When the system suspends or kills that process, the upload goes with it. We needed the upload to keep going even if the app is no longer running.

Here's how we solved it.

## The Package

We used the [`background_downloader`](https://pub.dev/packages/background_downloader) package. Despite the name, it handles uploads too.

It hands off the upload to the operating system itself:

- On **iOS**, it uses a background URL session. The system manages the transfer even if the app is killed.
- On **Android**, it runs the upload as a foreground service, a persistent task that the system won't easily stop.

Here's everything we changed across Flutter, iOS, and Android.

## Flutter: The Upload Code

This is the main upload class. A few things worth noting:

- `init()` sets up task tracking and the Android foreground service once.
- Task tracking lets us recover uploads that finished while the app was closed.
- On Android, `Config.runInForeground` prevents the system from stopping the upload.

```dart
import 'dart:io';

import 'package:background_downloader/background_downloader.dart';

class VideoUploader {
  bool _initialized = false;

  Future<void> init() async {
    if (_initialized) return;
    _initialized = true;

    // Track tasks so we can recover uploads after app restart
    FileDownloader().trackTasks();

    if (Platform.isAndroid) {
      await FileDownloader().configure(
        globalConfig: [(Config.runInForeground, Config.always)],
      );
    }
  }

  Future<bool> uploadVideo({
    required File file,
    required String uploadURL,
    required String title,
    required Function(int current, int total) onUploadProgress,
  }) async {
    await init();

    final fileSize = await file.length();

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
        'Content-Length': fileSize.toString(),
      },
    );

    // Required on Android: foreground services need a visible notification
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
      },
    );

    return result.status == TaskStatus.complete;
  }
}
```

The key part here is `trackTasks()`. It lets you reconnect to uploads that finished while the app was closed. Without it, you have no way of knowing whether an upload succeeded or failed after the app was killed.

## App Initialization: Recovering Interrupted Uploads

In your app startup, before `runApp()`, add this:

```dart
await FileDownloader().start(doRescheduleKilledTasks: true);
```

This tells the downloader to automatically retry any uploads that were interrupted when the system killed the app. Without it, those interrupted uploads are just lost.

## iOS Configuration

iOS is where most of the work is. You need two changes.

### Info.plist: Background Modes

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

### AppDelegate.swift

When iOS finishes a background upload after your app was killed, it relaunches the app and sends an event. You need to forward that event to the Flutter plugin. If you don't, the plugin never finds out the upload finished, and your app can't update accordingly.

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

Without this override, uploads work perfectly in the foreground but silently disappear when the app is in the background.

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

The two permissions allow the app to run a foreground service. The service declaration registers it as a data sync type. On Android, foreground services require a visible notification. That's not optional, it's a system requirement.

## Dependencies

Add these to your `pubspec.yaml`:

```yaml
dependencies:
  background_downloader: ^9.2.3
```

## Things Worth Knowing

A few things we learned along the way:

- **iOS doesn't guarantee when background uploads finish.** The system decides based on battery, network, and other factors. Don't promise users an exact time.
- **Task tracking must be set up before uploads start.** Call `trackTasks()` during initialization, not after.
- **Test on a real device.** The iOS Simulator doesn't accurately reproduce what happens when the system kills your app. Use a real phone, start an upload, switch apps, and force-kill from the app switcher.

## Wrapping Up

Background uploads in Flutter need setup across three layers: Flutter, iOS, and Android. The `background_downloader` package handles the heavy lifting, but each platform needs the right configuration to support it. Hopefully this saves you some trouble. ✌️

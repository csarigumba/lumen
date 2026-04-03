---
title: "How to Run a GPU Job on GCP Cloud Batch from Code"
date: "2026-03-26T00:00:00.000Z"
template: "post"
draft: false
slug: "/posts/how-to-spawn-a-gpu-cloud-batch-job-programmatically"
category: "Software Engineering"
tags:
  - "Software Engineering"
  - "GCP"
  - "Cloud Batch"
  - "GPU"
description: "How to submit a Cloud Batch GPU job programmatically, with GCS volume mounts and environment variables."
---

I needed to run some processing that requires a GPU. Serverless functions have a hard timeout limit, and this process can easily run longer than that. Running it on a dedicated GCE instance is not an option either since the workload is on-demand, not something that needs a machine running 24/7. The cleaner pattern is to submit a Cloud Batch job from a serverless function and return immediately. The batch job spins up a GPU machine, does the heavy processing, writes results to GCS, and shuts down with no idle cost and no timeout pressure on the caller.

This post covers how to do that programmatically using the `@google-cloud/batch` Node.js SDK.

## Hardware Configuration

Define your GPU machine spec in a config object:

```js
const BATCH_JOB_CONFIG = {
  region: 'us-central1',
  allowedZones: ['zones/us-central1-a'],
  gpuType: 'nvidia-l4',
  gpuCount: 1,
  installGpuDrivers: true,
  machineType: 'g2-standard-8',  // 8 vCPUs, 32 GB RAM
  cpuMilli: 8000,
  memoryMib: 32768,
  maxRetryCount: 3,
  maxRunDurationSeconds: 10800,  // 3-hour timeout
};
```

Setting `installGpuDrivers: true` on the `AllocationPolicy.Accelerator` handles driver installation automatically, so you don't need to bake drivers into your container image.

## Mounting GCS Buckets as Local Paths

For small inputs, you can bundle everything directly into your Docker image. But if your inputs are large, a better approach is to store them in a GCS bucket and mount it inside the container using [GCS FUSE](https://docs.cloud.google.com/storage/docs/cloud-storage-fuse/overview). This way the container reads and writes files as if they are local paths, without any GCS SDK code inside your workload:

```js
const inputVolume = new batch.Volume({
  gcs: new batch.GCS({ remotePath: cfg.videoAnalysisInputBucket }),
  mountPath: '/mnt/shared/input',
});
```

Your container code can then just `open('/mnt/shared/input/file.mp4', 'rb')` with no GCS SDK needed inside the container. This keeps your workload logic clean and separate from infrastructure concerns.

## Passing Context via Environment Variables

Inject all job-specific context as environment variables at submission time:

```js
environment: new batch.Environment({
  variables: {
    FIRST_NAME: firstName,
    LAST_NAME: lastName,
    GCP_PROJECT_ID: projectId,
  },
}),
```


## Putting It Together

Here's the full job submission:

```js
const { BatchServiceClient, protos } = require('@google-cloud/batch');
const batch = protos.google.cloud.batch.v1;

async function launchCloudBatchJob(firstName, lastName) {
  const client = new BatchServiceClient();
  const projectId = await client.auth.getProjectId();
  const cfg = getConfig();

  const jobId = `gpu-job-${Date.now()}`.toLowerCase().replace(/[^a-z0-9-]/g, '-');

  const inputVolume = new batch.Volume({
    gcs: new batch.GCS({ remotePath: cfg.inputBucket }),
    mountPath: '/mnt/shared/input',
  });

  const task = new batch.TaskSpec({
    runnables: [
      new batch.Runnable({
        container: new batch.Runnable.Container({
          imageUri: cfg.containerImage,
          commands: [],
        }),
        environment: new batch.Environment({
          variables: {
            FIRST_NAME: firstName,
            LAST_NAME: lastName,
            GCP_PROJECT_ID: projectId,
          },
        }),
      }),
    ],
    volumes: [inputVolume],
    computeResource: new batch.ComputeResource({
      cpuMilli: BATCH_JOB_CONFIG.cpuMilli,
      memoryMib: BATCH_JOB_CONFIG.memoryMib,
    }),
    maxRetryCount: BATCH_JOB_CONFIG.maxRetryCount,
    maxRunDuration: { seconds: BATCH_JOB_CONFIG.maxRunDurationSeconds },
  });

  const job = new batch.Job({
    taskGroups: [
      new batch.TaskGroup({
        taskSpec: task,
        taskCount: 1,
      }),
    ],
    allocationPolicy: new batch.AllocationPolicy({
      instances: [
        new batch.AllocationPolicy.InstancePolicyOrTemplate({
          policy: new batch.AllocationPolicy.InstancePolicy({
            machineType: BATCH_JOB_CONFIG.machineType,
            accelerators: [
              new batch.AllocationPolicy.Accelerator({
                type: BATCH_JOB_CONFIG.gpuType,
                count: BATCH_JOB_CONFIG.gpuCount,
                installGpuDrivers: BATCH_JOB_CONFIG.installGpuDrivers,
              }),
            ],
          }),
        }),
      ],
      location: new batch.AllocationPolicy.LocationPolicy({
        allowedLocations: BATCH_JOB_CONFIG.allowedZones,
      }),
    }),
    logsPolicy: new batch.LogsPolicy({
      destination: batch.LogsPolicy.Destination.CLOUD_LOGGING,
    }),
  });

  const [response] = await client.createJob({
    parent: `projects/${projectId}/locations/${BATCH_JOB_CONFIG.region}`,
    jobId,
    job,
  });

  return response.name;
}
```

Call this from your serverless function, store the returned job name, and return immediately. The batch job runs on its own from there.

## Wrapping Up

That's it. A simple way to run GPU workloads on demand without keeping machines running. ✌️

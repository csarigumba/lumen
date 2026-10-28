---
title: "The Last 30% Is Still Our Job"
date: "2026-10-26T00:00:00.000Z"
template: "post"
draft: false
slug: "/posts/the-last-30-percent-is-still-our-job"
category: "Software Engineering"
tags:
  - "Software Engineering"
  - "AI"
  - "Testing"
  - "Career"
description: "AI can get a feature most of the way there quickly. Here's what sits in the last part on my projects, and how my team tries to finish it on purpose instead of finding it in production."
---

I've been reading Addy Osmani's [Beyond Vibe Coding](https://www.oreilly.com/library/view/beyond-vibe-coding/9798341634749/), and one chapter put a name on something I see every week. He calls it the 70% problem.

The idea is that AI coding tools can get you to roughly 70% of a solution very quickly. The last 30% is where they struggle: edge cases, error handling, security, and performance. The code can look solid and still hide problems that only show up in production.

## Is it really 70%?

I think the direction is right, but the number is mostly catchy. It depends on the project.

The book gives a useful hint about why. The 70% the AI handles well is usually the straightforward, patterned part of the work, the kind of code that follows well-known paths or common frameworks. So the real split depends on how much of a task is patterned.

A form with validation, a standard REST endpoint, or a component in a popular framework is mostly patterned. The AI has seen thousands of similar examples, so its first version can get very close.

Work that is specific to your system is different. Business rules that only exist for one client, infrastructure changes, integrations with external services, and data migrations have fewer well-known paths. The AI still writes plausible code, but whether it's correct depends on details of your system that the AI may not know. On that kind of work, the gap can be much bigger than 30%.

So for me, 70% is a reminder that the AI's first version is rarely the finished one.

## What sits in the last 30% for me

While working on many projects, I keep seeing the same pattern. The AI code looks fine. But when we look closer, the edge cases weren't tested properly, and the error handling wasn't covered well. There were also concerns around performance and security that nobody had checked yet.

To make that more concrete, these are the kinds of gaps that fall into the last 30%:

- **Edge cases.** Empty or missing input, very long lists, duplicate submissions when a user double-clicks, time zones, or two people updating the same record at once.
- **Error handling.** A third-party API that times out or returns something unexpected, a retry that creates duplicate records, or an error caught and ignored, so nothing is logged and the user sees a generic message.
- **Performance.** A query inside a loop (the N+1 problem), loading a whole table instead of paginating, or a missing index. It's fast with 20 test rows and slow with real data.
- **Security.** An endpoint that checks if a user is logged in, but not whether they're allowed to see that specific record. Input that goes straight into a query, secrets in config files, or dependencies that are out of date.

These are hard to catch because the happy path works, so nothing looks wrong at first. That's why I think this part needs its own dedicated review, separate from checking whether the feature works at all.

I also think it's the most challenging part, because it's the final stage. It's where you make sure the product is really doing well before real users depend on it.

## How we finish it on purpose

You find the last 30% by doing the work yourself, instead of letting the AI handle it too. Here's what that looks like on my team.

**We match the effort to the topic.** A minor bug fix or a very simple change doesn't need the full process. But for sensitive or big topics, like infrastructure, designs, initial drafts, enhancements, or specific requests from a client, we go slowly and use a proper checklist with checkpoints. Running the full process on every one-line fix would cost a lot of time for very little benefit.

**We test manually against the integration test matrix.** We don't read every line of code anymore. But we do confirm manually that what's written in the integration test matrix actually works.

The matrix is a list of scenarios and the result we expect for each one. A simplified example for an "update my profile" feature could look like this:

| Scenario | Expected result |
| --- | --- |
| Valid update | Changes saved, confirmation shown |
| Required field left empty | Validation error, nothing saved |
| Session expired mid-edit | User sent to login, no partial save |
| Request uses another user's ID | Request rejected, nothing changed |
| Profile service times out | Clear error message, user can retry |

Only the first row is the happy path. The other rows test the failure cases, which is where most of the last 30% shows up.

**We check that the tests cover what matters.** The AI writes tests too, so we make sure those tests cover all the important points. In practice, that means checking that the failure scenarios in the matrix have tests, and that the tests check real behavior instead of only confirming that the code runs. We also run end-to-end integration tests, so the full user journey is tested and we can see there's no regression.

**We still do peer reviews.** I think peer review is still very important right now. Another person validates that the requirement itself is correct, and that what the AI built matches what we expected. The AI checks its work against what we asked for, so it won't notice if the requirement itself is wrong.

Before we call something done, we confirm that the requirements were met, that the AI implemented the plan we agreed on, that manual testing passed, and that the integration tests, unit tests, and CI checks are all correct.

## Who owns the last 30%

The way I see it, the AI now handles most of the implementation and the low-level work.

But the responsibility for saying "this is working, and it's high quality" is still ours.

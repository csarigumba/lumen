---
title: "Why I Chose Hermes as My Personal Agent"
date: "2026-09-08T00:00:00.000Z"
template: "post"
draft: true
slug: "/posts/why-i-chose-hermes"
category: "Developer Tools"
tags:
  - "AI"
  - "Developer Tools"
  - "Personal Knowledge Management"
  - "Obsidian"
  - "Hermes"
description: "I was not looking for another chat window. I wanted a personal agent that could retain useful context, work across the tools I already use, and improve with time."
---

I was not looking for another chat window.

ChatGPT and Claude Code are both useful to me. One is good for thinking through ideas. The other is excellent when I need to work inside a codebase. But most of my life does not begin and end with a prompt or a repository. It is a stream of notes, small decisions, recurring tasks, things I want to learn, and thoughts I do not want to lose before I have time to make sense of them.

That is why I chose [Hermes](https://hermes-agent.nousresearch.com/).

I wanted an agent I could treat more like a personal assistant than a fresh conversation. One that could retain useful context over time, work with the tools I already use, and do small pieces of real work instead of only telling me how I might do them.

## Context should not reset every morning

The part I value most is persistent memory.

A normal chat session starts with a blank page. I explain the background, restate preferences, and try to reconstruct where we left off. That is manageable for one question. It becomes tiring when the work is personal and continuous.

Hermes can keep useful context across sessions: preferences, ongoing projects, and decisions that should not need to be rediscovered every time. I can say a thought when it occurs to me, ask it to remember it, and come back to it later. Months later, I can ask about a previous conversation or decision without having to search through old messages myself.

That changes the relationship. It feels less like opening a tool and more like continuing a conversation.

Memory needs judgment, of course. Not every passing thought deserves to become permanent context. But the ability to keep the things that matter is useful. It lets the system become more familiar with how I work instead of requiring a full reintroduction every day.

## My Obsidian vault is part of the system

I use Obsidian for notes, reflections, ideas, and things I am trying to learn. Before Hermes, the vault was mostly a place where I put information so that I could retrieve it later.

Now I am experimenting with it as a second brain that has an agent layer on top.

Hermes can help me capture a thought, find related notes, and turn scattered material into something useful. I use it in reflection work and philosophical study, where the value is not only storing a quote or an idea. The value is returning to it at the right time, connecting it to a current problem, and testing whether it changes how I act.

The important distinction is that the notes remain mine. Hermes is there to help me work with them, not to replace the habit of thinking.

## It can do work, not just talk about work

I also wanted an assistant that could take bounded action.

For example, I use Hermes to manage and check parts of my personal website. Instead of manually checking whether a service is healthy, I can ask Hermes to inspect it and report what it finds. The agent can read files, run commands, and work through a defined task with me still deciding what should happen next.

This is where an agent is meaningfully different from a chatbot. A chatbot can explain how to check a service. An agent, with the right access and guardrails, can check it.

That does not mean I give it unlimited permission and walk away. Access should be deliberate. Destructive actions need review. Credentials need protection. But there is a useful middle ground between doing every small task manually and automating everything blindly.

## Small automations compound

The other reason I chose Hermes is its support for scheduled work.

I have set up cron jobs to monitor people and topics I follow on X. Hermes collects recent posts, summarizes what matters, and helps me decide whether there is an action worth taking. I use a similar approach for a daily briefing: a short view of what I should know, instead of opening several sites and hoping I remember what to check.

The point is not to consume more information. It is to reduce the manual scanning that produces little value.

A useful briefing should be narrow, sourced, and quiet when nothing matters. The same is true for any personal automation. If it creates more notifications than clarity, it has failed.

## Why Hermes over a single-purpose tool

Hermes brings a few pieces together that I wanted in one place:

- persistent memory and searchable past sessions
- access to my own notes and files
- messaging through Telegram, where I already communicate
- scheduled jobs for recurring research and checks
- tools for real tasks, not only text generation
- the option to improve its skills and workflows as I use it

None of those features is revolutionary in isolation. The value is in the combination. I do not have to move between a notes app, a chat app, a scheduler, and a pile of scripts just to keep a small personal system running.

## Still a work in progress

I do not think of this as a finished setup. It is an evolving system.

I started with Hermes on a remote VPS. That made it accessible, but it also introduced some latency, especially when I was using SSH port forwarding to reach a local dashboard. I am now considering moving more of it to a Mac mini or Raspberry Pi on my local network. Most of my use is already local, and reducing the distance between my notes, services, and agent should make the system simpler and faster.

The bigger lesson so far is straightforward: the best personal agent is not the one with the most impressive demo. It is the one that fits into your real life, remembers enough to be useful, respects the boundaries you set, and saves you from work you should not have to repeat.

That is what I am building with Hermes.

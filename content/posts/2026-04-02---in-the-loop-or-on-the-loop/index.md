---
title: "In the Loop or On the Loop? How I Think About Using AI to Code"
date: "2026-04-02T00:00:00.000Z"
template: "post"
draft: false
slug: "/posts/in-the-loop-or-on-the-loop"
category: "Software Engineering"
tags:
  - "Software Engineering"
  - "AI"
  - "Developer Productivity"
  - "Claude Code"
description: "The short answer: don't abandon the keyboard, but don't refuse the copilot either. The sweet spot is knowing when to drive and when to delegate."
socialImage: "./image.jpg"
---

I've been using AI coding agents for almost a year now. I've tried GitHub Copilot, Cursor, and Claude Code, and I've settled on Claude Code as my primary tool. The productivity gains are real. I ship faster, I prototype in hours instead of days, and I've built things I probably wouldn't have attempted before. But after months of pushing AI further into my workflow, letting it handle entire features end to end, something started to feel off.

I tried letting AI drive my full workflow. From reading PRDs to breaking down tasks to writing every line of code, I handed over the wheel and just monitored. The output was fast. But fast isn't the same as good. The short answer I've landed on: don't abandon the keyboard, but don't refuse the copilot either. The sweet spot is knowing when to drive and when to delegate, and that judgment itself is the skill worth sharpening.

I think about this in two modes: **human in the loop**, where you review every step or write the code yourself with AI assisting, and **human on the loop**, where you set the direction, AI executes, and you monitor. Both have their place. The question is when to use which.

![You hold the wheel. AI rides shotgun.](./image1.jpg)
_You hold the wheel. AI rides shotgun._

## The Problem With Letting AI Drive

AI-generated code can look clean on the surface while hiding real problems underneath. Here are a few things I've run into firsthand.

I vibe-coded a simple web application. The UI looked polished, everything worked in development. But once I deployed it, the navigation was noticeably slow. When I dug into the code, I found it was eagerly importing every module upfront instead of using lazy loading. That's not an obscure optimization, it's a fundamental pattern that any experienced developer would apply without thinking.

On another project, a week scheduler, I found that every keystroke was firing a request to the backend to save the task. The result was a flood of unnecessary API calls that slowed down the entire system. The fix was straightforward: add a debounce. Again, a basic pattern, but one the AI didn't think to apply on its own.

Then there's the UI homogeneity problem. Since AI models are trained on public repositories, the interfaces they generate tend to look remarkably similar, same color palettes, same button styles, same layouts. This one is partly on us for not giving more specific design instructions, but it illustrates a broader point: AI optimizes for getting you to a working output fast, not for production-quality judgment.

These aren't edge cases. They're the kinds of things a careful code review would catch. But if you're on the loop and just merging what AI produces, you miss them. And the cost of fixing these issues post-deploy is always higher than catching them during development. The more you delegate without reviewing closely, the more these small issues compound across a codebase until you're staring at a wall of technical debt you didn't see coming.

This isn't about AI being bad at what it does. It's about AI not having the full context of your production environment, your users, and your scale. It doesn't push back on its own output. It won't tell you "this works, but it'll be slow at scale."

## Skills Are Muscles

Here's what concerns me most about going fully on the loop: coding skills atrophy when you stop using them.

I believe our technical ability works like a muscle. The more you exercise it, the stronger it gets. The less you use it, the weaker it becomes. When AI handles everything from implementation to deployment, you stop practicing the thing that makes you a developer: solving problems at the code level.

Without realizing it, you shift from developer to architect or manager. Those are valid roles, but they focus on high-level direction, not the low-level problem solving that keeps your skills sharp. If you're not writing code, debugging issues, and making implementation decisions on a daily basis, you start to lose familiarity with things you used to do without thinking. Even syntax starts to feel foreign.

The irony is that you need sharp coding skills to review AI output effectively. If your problem-solving muscles have atrophied, your code reviews become rubber stamps. You skim the PR, it looks reasonable, you merge it. That's how technical debt piles up silently, dead code accumulates, unnecessary dependencies creep in, and gradually you stop understanding your own codebase.

This doesn't happen overnight. It's a slow erosion. You don't notice it until you need to debug something complex and realize you're not as confident as you used to be. And once that confidence fades, your usage of AI becomes less effective too, because you can't guide it well or evaluate what it gives you.

Staying in the loop is a form of professional maintenance. It keeps your edge.

## When to Drive, When to Delegate

I'm not saying vibe coding is bad. I'm saying it's about matching your level of involvement to the stakes of the project.

**Human in the loop** is for critical work. Production systems, features that affect real users, anything where bugs have real consequences. In this mode, you're either writing the code yourself with AI assisting, or you're reviewing AI output line by line. You understand every change before it ships. My workflow here typically looks like: review the PRD, break down tasks with AI, review the breakdown, create detailed implementation steps, then build iteratively, checking each piece as it comes together.

**Human on the loop** is for lower-risk work. Prototyping a new idea, generating base templates, writing throwaway scripts, or learning a new framework. In these cases, the cost of imperfect code is low. If AI produces something that's 80% right, that's fine, you're exploring, not shipping. Vibe coding shines here because speed matters more than polish.

It's not one or the other all the time. Some tasks in a critical project can still be handed off to AI. Some prototype code might need a closer look if it's heading toward production. The point is to make that call deliberately. And honestly, getting better at knowing when to step in and when to let go is the real skill worth building.

## Finding Your Balance

The developers who will thrive are the ones who learn to work _with_ AI, not the ones who hand everything over, and not the ones who refuse to use it at all.

My challenge to you: try both approaches in your own workflow. Spend a week fully in the loop, writing code with AI as your assistant. Then spend a week on the loop, letting AI drive while you monitor. Observe what happens. Reflect honestly on what you gained and what you lost. When AI drives your full workflow, does the output truly hold up in production? Are you still sharp enough to catch what it misses?

As AI improves, the balance point will shift. But the principle won't change: staying engaged with your craft matters. Don't let convenience erode the skills that make you effective in the first place.

Find your balance. ✌️

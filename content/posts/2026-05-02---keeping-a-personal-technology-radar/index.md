---
title: "Keeping a Personal Technology Radar"
date: "2026-05-02T00:00:00.000Z"
template: "post"
draft: false
slug: "/posts/keeping-a-personal-technology-radar"
category: "Software Engineering"
tags:
  - "Software Engineering"
  - "Career"
  - "AI"
  - "Learning"
description: "A simple backlog for the technologies I want to learn next."
---

## Picking Up the Thread

In two earlier posts, [Why Technical Breadth Matters More Than Ever](/posts/why-technical-breadth-matters-more-than-ever) and [Twenty Minutes a Day for Technical Breadth](/posts/twenty-minutes-a-day-for-technical-breadth), I argued that breadth is the new leverage in the AI era, and that 20 minutes a day is the small habit that compounds it. What I didn’t talk about is where the topics come from.

For a while, they came from wherever. A tab I left open. A thread I scrolled past. A thing someone mentioned in a meeting. The list was long and messy, and I kept losing track of what I had already decided was worth my time.

The thing that fixed it for me is a personal technology radar.

The idea is not mine. ThoughtWorks has been publishing [a public technology radar](https://www.thoughtworks.com/radar) twice a year since 2010. I came across it in _Fundamentals of Software Architecture_ by Mark Richards and Neal Ford, the same book behind my last two posts. The format is simple. You sort technologies into four rings: Adopt, Trial, Assess, and Hold, depending on how confident you are in each one.

## My Personal Version

Mine is a backlog, not a roadmap. There are no dates, no targets, no “by Q3 I’ll have learned X.” It’s a place to hold things I want to learn, with enough structure that the list does not rot the way a flat note does after a few months.

It rides on top of an inbox. I still dump things into a bookmark folder and a plain note in 5 seconds when I see something interesting. The radar is the next step up. It holds the stuff I have decided is worth tracking, not just stashing. If something is a one-off curiosity, it stays in the inbox. If I am willing to commit to learning it later, it goes on the radar.

That gives it two jobs at once. It is a backlog I pull from for my daily 20 minutes. It is also a forcing function that makes me stay mindful of what is moving in the field. Most weeks, the second job is the one that matters more. The act of deciding whether something is an Assess or a Trial is what keeps me reading and listening with intent, instead of skimming.

The shape is the same as ThoughtWorks’s. Four rings, four quadrants. What changes is the intent. The rings do not mean “what my team should adopt.” They mean “what I am doing with this thing in my own learning.”

The four quadrants are how I split things up: Techniques, Tools, Platforms, and Languages & Frameworks. Same as the original. They keep the table scannable when it gets long.

Here is what the four rings actually mean for me.

- **Adopt**: already in my hands, I lean on it.
- **Trial**: next on the list to actually try.
- **Assess**: curious, want to understand the shape, not committing time yet.
- **Hold**: aware of it, deliberately not reaching for it.

The table itself is simple. A name, a ring, a quadrant, and a one-line description. On top of that, I added two columns the original does not have. `isNew` flags blips I just dropped in, so they do not get lost in a long table. `status` tracks motion: `move_in`, `move_out`, `no_change`. The status column is what makes the radar feel alive between reviews. A blip moving from Trial to Adopt is a small thing, but seeing the move in the table is satisfying.

I have been keeping it for two months. That is long enough to have something usable, short enough that I am still adjusting how I use it. The plan is to revisit the structure once a quarter.

If you want a starting template, mine is public: [my technology radar in Notion](https://www.notion.so/cedricsarigumba/1eb3c70d4fe64e6ab8d50082317e22e4?v=d14fce8abb974cad8330e7182bab4e4f&source=copy_link).

## What’s On Mine Right Now

A small slice, just to show the shape.

- **Adopt**: Claude Code is my daily driver. MCP is how I plug it into the rest of my world.
- **Trial**: Eval-driven development. Treating LLM evals like unit tests, and writing them before the feature.
- **Assess**: OpenTofu, the open-source Terraform fork. I am watching to see if licensing pressure makes a migration worth it.
- **Hold**: Vibe coding without specs. Fine for a prototype, dangerous in a production codebase.

Most of the radar lives in Trial and Assess. That is intentional. Adopt should be the smallest, highest-confidence ring, not the biggest. Hold is not a graveyard either. It is a deliberate “do not reach for this on instinct” list.

## How It Stays Alive

There is no schedule for moving things between rings. A move always has a trigger. I tried it on a small thing. I read enough to form an opinion. I decided the trade-offs are not worth my time. Most moves happen right after a 20-minute session ends, when I have a clearer sense of where the topic actually sits for me. A blip might go from Assess to Trial because I used it once. Another might drop into Hold because I have seen enough to step away.

The signals come from everywhere. Reddit threads, blog posts, conference talks, podcasts, conversations with other engineers. None of it is structured. The radar is what catches it before it disappears.

The loop with the 20-minute habit is simple. Open the radar. Pick the blip that is most worth closing today. Spend 20 minutes on it. If I came out the other side with a clearer view, I update the status. If I did not, I leave it alone and pick a different one tomorrow.

That is the whole system.

## Closing

Two months in, the reason this works for me is not the table or the columns or even the rings. It is that curiosity needs a system. Without one, the new things I encounter every week slip past me. With one, I can see what I am committing to learn, and what I am choosing not to.

If the pace of new tech in the AI era feels like a lot, and you are not sure how to keep up without burning out, try a radar. It does not have to be big or pretty. It just has to be a place where the things you want to learn stop disappearing.

✌️

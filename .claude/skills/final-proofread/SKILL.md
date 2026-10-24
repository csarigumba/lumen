---
name: final-proofread
description: Final pass on a blog post before Sid reads or publishes it. Removes AI slop while keeping his voice. Use after drafting or editing any post in content/posts/, or when Sid says a post "sounds AI generated", "proofread", "final pass", "de-slop", or "is this slop?".
---

# Final proofread (no AI slop)

The last pass on a post in `content/posts/`. The main job is to remove AI slop without flattening Sid's voice. Run it after every draft or rewrite, before telling Sid the post is ready.

Based on [petergyang/no-ai-slop](https://github.com/petergyang/no-ai-slop) (MIT, see `LICENSE`), adapted for this blog.

## Two jobs

**Edit (default).** Fix the post in place, then show a short **What changed** list.

**Detect.** When Sid asks "is this slop?" or asks to scan without rewriting, quote each line that matches a pattern below, name the pattern, and give the fix in a few words. Don't rewrite, score, or guess whether AI wrote it. Offer to edit after.

## Step 1: Find the voice source

Sid's voice beats any rule here. In order of priority:

1. **His own raw words for this post.** If the post was drafted from his answers or dictation, those answers are the best voice sample. Reuse his phrases where they are clear ("it will make my mood bad", "proper tuning of the mind"). Fix grammar slips and dictation mis-hears, and keep the wording.
2. **His older posts in the same category.** Read one or two before editing.

## Step 2: Run the scanner

```bash
python3 .claude/skills/final-proofread/scripts/scan.py content/posts/<post>/index.md
```

It flags mechanical tells: em dashes, banned words, binary contrasts, throat-clearing, short fragments, and colon reveals. The scanner only finds candidates. You still read every line yourself, because most slop is rhythm and invention, which a regex can't catch.

## Step 3: Edit

### Blog rules (stricter than the original skill)

- **No invented content.** Every anecdote, sensory detail, example, feeling, and claim about Sid's life must come from Sid. If a line describes something he never said (how the street looked, what he regrets, how often he fails), cut it or ask him. This is the most common slop in his drafts, because the model fills gaps with plausible details.
- **No em dashes at all.** Use commas, periods, or parentheses.
- **Short paragraphs**, 1 to 3 sentences. Plain, simple words. Active voice.
- **Headers stay** for sections longer than a few paragraphs. Use sentence case for any new headers. Don't retitle existing headers just for case.
- **Keep the frontmatter, quote block, and image.** Don't touch the George Long quotes.
- Keep personal details abstract: no employer or colleague names.

### Patterns to cut

**Binary contrasts.** "It's not X. It's Y." / "The goal isn't X, it's Y." / "One X doesn't do much. A Y does." Say Y directly.

**Fake-profound kickers.** A short quotable line closing a paragraph or section ("And the rain was never the problem."). Delete it and end on the clearest concrete sentence already there. Don't rewrite it into a better aphorism.

**Dramatic fragments.** "It spreads." "Then I choose." "That's it." Fold them into a real sentence or cut them.

**Interpretive metadiscourse.** Lines that tell the reader what to notice: "That's the dangerous part", "This matters more than it sounds", "The key point is". Cut them, or replace them with the fact itself.

**Throat-clearing and faux insight.** "Here's the thing", "The truth is", "What nobody tells you". Cut them.

**Colon reveals.** "The best part: it learns." Write a plain sentence.

**Importance puffery.** "The most powerful habit I have", "a testament to", "pivotal". Use Sid's actual strength of claim ("very powerful" if he said that).

**Superficial -ing endings.** "..., highlighting/reflecting/showing ...". Cut them or state the real consequence.

**Synonym cycling.** Pick one word (impression, reading) and repeat it.

**Robotic rhythm.** Paragraphs that all have the same shape: setup, contrast, kicker. Vary them only where it helps.

**Rule of three.** Lists of three invented examples. Keep only the examples Sid gave.

**Summary-recap endings.** The last paragraph restates the post. End on the practice or the note to his sons instead.

**Reassurance kickers.** "And that's okay." Cut.

### Words to cut

Banned: delve, foster, leverage, utilize, facilitate, empower, streamline, robust, tapestry, realm, beacon, multifaceted, meticulous, intricate, paramount, transformative, elevate, embark, harness, testament, pivotal, journey (figurative), landscape (figurative).

Often empty, so cut them unless they carry meaning: just, literally, honestly, simply, actually, truly, fundamentally, importantly, crucially, ultimately, it's worth noting, at its core, the reality is, the truth is, in order to.

## Step 4: Check against eval.md

Answer every check in `eval.md`. If any check fails, fix the draft and check again.

## Step 5: Report

Output a short **What changed** list (one line per change type), plus anything you cut that Sid might want back, like an invented detail he could replace with a real one. Don't paste the whole post back if you edited the file. Point to the file instead.

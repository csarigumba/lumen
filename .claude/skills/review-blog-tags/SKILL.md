---
name: review-blog-tags
description: Audit and refine the `tags` frontmatter across every blog post in `content/posts/`. Use whenever the user asks to review, audit, refresh, normalize, or rebalance blog tags, or says things like "check if my tags are enough", "fix tag inconsistencies", "update the tags across posts", "see if any tags should be added/removed". Walks the full corpus, proposes per-post add/remove/update edits with reasoning, then applies them.
---

# Review Blog Tags

This skill audits the `tags` field in the frontmatter of every blog post and brings the corpus into a consistent, useful state. The goal is **discoverability**: a reader clicking a tag should land on a coherent group of posts.

## When to use this

Trigger this skill on prompts like:
- "Review all blog post tags"
- "Are the tags on my posts enough?"
- "Audit the tag taxonomy"
- "Add/remove/update tags across the blog"
- "Rebalance tags so similar posts share them"

## What "good tags" look like for this blog

Inferred from the existing corpus — preserve these conventions unless the user says otherwise:

1. **Format**: Title Case, double-quoted, one per line under `tags:` in YAML frontmatter.
2. **First tag = category**: The `category` field's value is always the first tag (e.g., `category: "Software Engineering"` → `"Software Engineering"` is tag 1).
3. **Count**: Typically 3–6 tags per post. Fewer than 3 usually means the post is under-tagged; more than 6 means it's diluted.
4. **Mix of breadth + specificity**: Most posts combine a broad theme tag (e.g., `"Mindset"`, `"AI"`, `"Career"`) with one or two specific tags (e.g., `"Marcus Aurelius"`, `"Ghostty"`, `"GCP"`).
5. **Reuse over invention**: Prefer an existing tag from the corpus over creating a near-duplicate (e.g., reuse `"Life Tips"` instead of inventing `"Daily Living"`).

## Process

Work through these steps in order. Use a TodoWrite list so progress is visible.

### Step 1 — Build the current tag map

Run the following to extract every post's current tags. This is the source of truth for the audit:

```bash
for f in /Users/apple/dev/priv/lumen/content/posts/*/index.md; do
  echo "=== $(basename $(dirname "$f")) ==="
  awk '/^---$/{c++} c==1 && /^(category|tags):/{p=1} c==1 && p && /^[a-z]/ && !/^(category|tags|  -)/{p=0} c==1 && p{print} c==2{exit}' "$f"
done
```

Then build a frequency table of tag usage across the whole corpus. Tags that appear **only once** are candidates for either elimination (if niche and the post has another good tag) or promotion (if other posts secretly belong under that tag too). Tags that appear in **most posts of a category** are healthy.

### Step 2 — Read each post's body, not just the frontmatter

Tags should reflect what the post is actually about, not what the title hints at. For each post, Read the full `index.md`, then ask:

- **Coverage**: Does every major topic in the post have a tag? If a post heavily discusses, say, Claude Code but doesn't tag it, that's a gap.
- **Accuracy**: Is every current tag actually a meaningful theme of the post, or is it decorative? Tags like a person's name should appear only if the post substantively engages with that person's ideas.
- **Consistency**: If two posts cover the same topic, do they share the same tag spelling? (`"Stoicism"` vs `"Stoic Philosophy"` would be a bug.)
- **Reader value**: If a reader clicks this tag, will they find a coherent cluster, or a one-off?

### Step 3 — Propose changes per post, then confirm

Before editing anything, present a per-post diff in this format:

```
2026-04-02---in-the-loop-or-on-the-loop
  keep:   "Software Engineering", "AI", "Claude Code"
  remove: "Developer Productivity"   # only used here, "AI" + "Career" cover it
  add:    "Career"                   # post is really about how engineers work
```

Group the proposed changes and share the full plan with the user. **Wait for confirmation before applying edits** — tag changes affect site navigation and should not be silent.

If the user says "go ahead" or similar, proceed. If they push back on a specific post, adjust and re-confirm only that one.

### Step 4 — Apply edits

Use the Edit tool to modify each post's frontmatter. Only touch the `tags:` block — never the `category`, `title`, `date`, `slug`, or body.

Preserve:
- Indentation (two spaces before the dash).
- Quoting style (double quotes around each tag value).
- Order: category-tag first, then specific → broad, roughly matching the existing pattern.

### Step 5 — Verify

After edits, re-run the extraction command from Step 1 and spot-check that:
- Every post still has the category as its first tag.
- No post is left with zero tags.
- Tag spellings are consistent across the corpus (run a quick frequency table again).

Report back with a short summary: how many posts changed, which tags were introduced, which were retired.

## What NOT to do

- **Don't rewrite categories.** The `category` field is a separate concern; this skill is scoped to tags.
- **Don't invent a brand-new taxonomy.** Refine what exists. If you think a sweeping rename is warranted, raise it with the user as a separate decision before doing it.
- **Don't batch-apply silently.** Always show the proposed diff first.
- **Don't add tags for SEO padding.** Each tag must point to a real cluster of posts (current or expected).

## Tone for the proposal

The user prefers concise, recommendation-led output (no em-dashes; use periods, commas, colons, or parentheses). Lead with the recommended changes per post, not a menu of options.

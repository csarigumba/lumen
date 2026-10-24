# lumen

Personal blog (Gatsby, bun). Posts live in `content/posts/YYYY-MM-DD---slug/index.md`, with images beside them as `image1.png`.

## Rules for posts

- After creating or editing any post in `content/posts/`, run the `final-proofread` skill (`.claude/skills/final-proofread/`) before you finish. It removes AI slop while keeping the author's voice. Don't skip it, even for small edits.
- New posts start as `draft: true`. Only set `draft: false` when the author says to publish.
- Never invent anecdotes, details, or practices. Use only what the author gave you.
- No em dashes.
- Pushing to `develop` deploys the site.

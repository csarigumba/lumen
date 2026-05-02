---
name: check-blog-links
description: >
  Review all blog posts in content/posts and verify that internal links and
  asset paths resolve. Skips external http(s) URLs by design.
  Use when the user says "check blog links", "verify links", "find broken links",
  or asks to audit links across blog posts.
allowed-tools: [Read, Glob, Grep, Bash, Edit]
---

# Check Blog Links

Verify every internal link and asset reference across all posts in `content/posts/**/index.md`. External `http://` and `https://` URLs are intentionally **not** checked — only links the repo itself can prove or disprove.

## Procedure

1. **Collect links.** Extract every URL from `content/posts/**/index.md`:
   - Markdown links: `[text](url)`
   - Reference-style links: `[text]: url`
   - Image sources: `![alt](url)` and `<img src="url">`

   Use the helper script:
   ```bash
   bash .claude/skills/check-blog-links/scripts/extract-links.sh
   ```

2. **Classify each link.**
   - `internal` — site-relative path (`/posts/...`, `/about`, etc.)
   - `anchor` — same-page `#fragment`
   - `asset` — relative file (e.g. `./image.png`) or root-relative (`/image.png`)
   - `external` — `http://` or `https://` → **skip, do not check**

3. **Check each class.**
   - **Internal**: confirm the slug exists. For `/posts/<slug>`, look for `content/posts/*---<slug>` (post folders are `YYYY-MM-DD---slug` but URLs use just the slug). For `/<page>`, look for `content/pages/<page>`.
   - **Anchor**: confirm the heading exists in the same file (slugify with lowercase + hyphens).
   - **Asset**: confirm the file exists. Relative paths (`./image.png`) resolve inside the post folder. Root-relative paths (`/image.png`) resolve inside `static/` — almost always a bug for post images, since post images live next to `index.md`.

4. **Report.** For each broken link, output:
   - File path and line number
   - Original URL
   - Failure reason (missing slug, missing file, missing anchor)
   - Suggested fix when obvious (e.g. `/image.png` → `./image.png`, renamed slug, typo)

5. **Do not auto-fix.** Surface the list and let the user confirm fixes. If the user approves, apply edits with the `Edit` tool, preserving link text.

## Notes

- Skip `mailto:`, `tel:`, and `javascript:` schemes.
- Skip every `http://` and `https://` URL — external link health is out of scope for this skill.
- Localhost or private hosts in posts are always a bug — flag them even though they are http(s).

---
title: "How to Migrate a Git Repository Without Admin Access"
date: "2026-04-07T00:00:00.000Z"
template: "post"
draft: false
slug: "/posts/how-to-migrate-a-git-repository-without-admin-access"
category: "Software Engineering"
tags:
  - "Software Engineering"
  - "Git"
  - "GitHub"
description: "No admin rights on the original repo? Here's how to migrate it manually using clone and mirror, plus validation steps."
---

I recently needed to move a repository from one GitHub organization to another. The catch: we didn't have admin or owner rights on the original repository. That rules out GitHub's built-in transfer feature, which requires admin access on both ends. So instead, we went with a manual approach: clone it, push it to a new remote, and end up with a clean, independent copy with no link back to the original.

Depending on your situation, you either need just the main branch or the entire repository with all branches and tags. Here's how to do both.

## Main Branch Only

If you only care about the main branch, a regular clone and push is enough.

Clone the repo, remove the old remote, and push to the new one:

```bash
git clone https://github.com/original-owner/repo.git
cd repo
git remote remove origin
git remote add origin https://github.com/new-owner/new-repo.git
git push -u origin main
```

Make sure the new repository on GitHub is created empty. No README, no `.gitignore`. Otherwise the push will fail because of conflicting histories.

This gives you a completely independent copy. No fork relationship, no connection to the original.

## All Branches and Tags

If you need everything (all branches, all tags, the full history), use `--mirror`.

```bash
git clone --mirror git@github.com:original-owner/repo.git
cd repo.git
git remote set-url origin git@github.com:new-owner/new-repo.git
git push --mirror
```

A mirror clone creates a bare repository (no working directory, just the Git data). It copies every ref: branches, tags, and anything else the original had. Pushing with `--mirror` sends all of it to the new remote in one shot.

## How to Validate the Migration

After pushing, verify that nothing was lost. Here are four quick checks.

### 1. Compare branch counts

```bash
git ls-remote --heads git@github.com:original-owner/repo.git | wc -l
git ls-remote --heads git@github.com:new-owner/new-repo.git | wc -l
```

The numbers should match.

### 2. Compare commits on key branches

```bash
git ls-remote --heads git@github.com:original-owner/repo.git main develop staging
git ls-remote --heads git@github.com:new-owner/new-repo.git main develop staging
```

The commit hashes should be identical for each branch.

### 3. Compare tag counts

```bash
git ls-remote --tags git@github.com:original-owner/repo.git | wc -l
git ls-remote --tags git@github.com:new-owner/new-repo.git | wc -l
```

If the original had tags, the new repo should have the same count.

### 4. Clone test

```bash
git clone git@github.com:new-owner/new-repo.git test-clone
cd test-clone
git branch -r
git log --oneline -5
```

Make sure the branches are all there and the recent commit history looks correct.

## What Doesn't Come With You

This is important to understand: `git clone --mirror` copies **Git data**, not **GitHub data**. Anything that lives on GitHub's platform rather than inside the Git repository itself is left behind.

That includes:

- **Pull requests** including all PRs, reviews, comments, and draft PRs
- **Issues** including comments, labels, and milestones
- **GitHub Actions** run history, secrets, and environment variables (workflow files transfer since they're committed code)
- **Releases** including release notes and uploaded binaries (tags do transfer)
- **Branch protection rules** which need to be reconfigured manually
- **Wikis** which are separate Git repos (`repo.wiki.git`) and need their own mirror
- **Webhooks and integrations** including connected services, deploy keys, and GitHub App configurations
- **Discussions, Projects, security alerts**
- **Stars, watchers, forks** which all start from zero

In short, you get the full code history (commits, branches, tags) but everything else needs to be set up again on the new repo. If preserving PRs and issues is critical, you'd need the GitHub API or a migration tool like [GitHub's repository transfer](https://docs.github.com/en/repositories/creating-and-managing-repositories/transferring-a-repository), which requires admin access on both ends.

## Which Method Should You Use

It comes down to what you need to bring over.

**Main branch only** works when you're starting fresh and don't care about feature branches or history on other branches. It's the simpler option.

**Mirror clone** is what you want when the new repo needs to be an exact copy with the same branches, tags, and history across everything. This is the safer default if you're migrating a team's active repository.

## Wrapping Up

That's it. Two approaches depending on scope, and four checks to make sure nothing was dropped. ✌️

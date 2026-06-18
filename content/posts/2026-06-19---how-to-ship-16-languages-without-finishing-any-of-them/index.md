---
title: "How to Ship 16 Languages Without Finishing Any of Them"
date: "2026-06-19T00:00:00.000Z"
template: "post"
draft: false
slug: "/posts/how-to-ship-16-languages-without-finishing-any-of-them"
category: "Software Engineering"
tags:
  - "Software Engineering"
  - "Internationalization"
  - "i18next"
  - "React"
  - "Localization"
description: "I needed to localize an app into a lot of languages without it turning into a months-long slog. The trick wasn't finishing each language, it was leaning on i18next's per-key fallback so a barely-translated language ships the same day and fills in over time."
---

I needed to add localization to one of the apps I was building. Not as a token gesture either. The app had to support many languages, and I wanted a way to do it without turning it into a months-long slog.

That's the part that worried me. Translation is usually treated as all-or-nothing. You can't ship Korean until Korean is finished, and "finished" means every one of the thousand-plus strings in the app. So languages pile up as a someday task, the app stays English-only, and everyone waits for a quiet week that never comes. I've watched that backlog grow on other projects, and I didn't want sixteen of those tasks staring back at me.

What I wanted was simple to describe and surprisingly hard to do: ship a language the moment someone translated even a handful of strings, while keeping the app fully usable the entire time. This is the solution I landed on, and it ended up being less about translation and more about how `i18next` is meant to be used.

## The setup is almost boring

The whole i18n bootstrap is about ten lines:

```ts
import i18next from "i18next";
import detector from "i18next-browser-languagedetector";
import { initReactI18next } from "react-i18next";

i18next
  .use(initReactI18next)
  .use(detector)
  .init({
    resources,
    fallbackLng: "en",
    interpolation: { escapeValue: false }, // React already escapes for us
  });
```

Three libraries do the work: `i18next` (the engine), `react-i18next` (the React bindings and the `useTranslation()` hook), and `i18next-browser-languagedetector`.

Notice what isn't there: any detection configuration. Because the detector runs with its defaults, it figures out the right language on its own. A new visitor sees the app in their browser's language, and a returning visitor sees whatever language they picked last time, because the detector remembers the choice. I didn't write any code to make either of those happen.

The `escapeValue: false` line is there on purpose. React already cleans up text before showing it, so I tell i18next not to do the same cleanup again, otherwise the text gets mangled.

## The thing that actually solved it: per-key fallback

Here's the part that made supporting 16 languages affordable. These are six of the sixteen translation files:

| Locale          | Lines |
| --------------- | ----- |
| English         | 1104  |
| Japanese        | 1112  |
| Portuguese (BR) | 1058  |
| German          | 200   |
| French          | 199   |
| Korean          | 49    |

The Korean file translates roughly forty keys. The English file has more than a thousand. So what does a Korean user see for the other 960 strings?

English. And they never notice the seam.

That's `fallbackLng: "en"` doing its job. i18next falls back per key, not per file. If `button.delete` exists in Korean, users see the Korean translation. If `admin.usageAnalytics.tooltip` doesn't, they silently get the English version.

Every locale is effectively English plus an overlay of whatever has been translated so far, and the app remains fully usable regardless of translation completeness.

That's exactly what I wanted.

Localization stopped being a blocking task and became an incremental one. Someone can translate the twenty most visible strings for a new language and ship it the same day, and the language fills in over time with no risk of a half-translated screen looking broken.

This is the one feature the whole approach rests on. Everything else i18next gives me, the browser detection, the React hook, the interpolation, I could have cobbled together myself. Per-key fallback is the part I couldn't, and it's the reason the app can offer sixteen languages when most of them are only partly done. Everything else is convenience.

## How do you switch languages?

The language picker is populated from an exported `LANGUAGES` array of `{ value, label }` pairs. Each label uses the language's own name, `日本語`, `한국어`, `Tiếng Việt`, so users can always find their language even when the UI is currently displayed in one they don't understand.

It's a small detail, but it's the difference between a language switcher that works and one that traps people.

Selecting a language calls:

```ts
i18next.changeLanguage(language);
```

That's it. `react-i18next` re-renders every translated component in place, without a page reload, and the detector cache remembers the choice for next time.

## What I took away

I expected a long translation grind. The real decisions turned out to be about setup, not language:

- Use per-key fallback so partial translations ship right away.
- Keep a tiny TypeScript check to see what's still untranslated.

The win wasn't translating faster. It was making the work small enough that anyone with twenty spare minutes could move it forward. ✌️

---
title: "Why keyset pagination beats OFFSET"
date: "2026-07-10T01:00:00.000Z"
template: "post"
draft: false
slug: "/posts/why-keyset-pagination-beats-offset-with-real-benchmarks"
category: "Software Engineering"
tags:
  - "Software Engineering"
  - "SQL"
  - "PostgreSQL"
  - "Databases"
  - "Performance"
  - "API Design"
description: "OFFSET pagination slows down as you page deeper. I benchmarked OFFSET and keyset pagination on 5 million rows in PostgreSQL: why OFFSET degrades, why keyset stays fast, the tiebreaker mistake that silently skips rows, and when OFFSET is still fine."
---

`LIMIT ... OFFSET` gets slower the deeper you page, because the database must scan and discard every row before the offset. Keyset pagination (also called cursor pagination) takes the same time no matter how deep you go. Most articles state this without numbers, so I benchmarked both.

## The setup

The test table is an append-only event log: logins, order changes, payments. Tables like this grow to tens of millions of rows, and they are where deep pagination actually happens — someone investigating an incident pages back months.

Five million rows in Postgres 16 (Docker, default config):

```sql
CREATE TABLE events (
  id          bigserial PRIMARY KEY,
  occurred_at timestamptz NOT NULL,
  event_type  text        NOT NULL,
  actor_id    int         NOT NULL,
  payload     jsonb       NOT NULL
);

INSERT INTO events (occurred_at, event_type, actor_id, payload)
SELECT
  timestamptz '2024-01-01' + (n * interval '30 seconds'),
  (array['user.login','order.created','order.updated',
         'payment.captured','email.sent'])[1 + n % 5],
  1 + n % 10000,
  jsonb_build_object('seq', n)
FROM generate_series(1, 5_000_000) AS n;

CREATE INDEX idx_events_occurred_at_id ON events (occurred_at, id);
VACUUM ANALYZE events;
```

The index covers both `occurred_at` and `id`, and both techniques use it. OFFSET is slow even with the right index in place.

## The numbers

Page size 20, data already in memory, timings from `psql`'s `\timing`:

| Depth (rows skipped) | OFFSET | Keyset  |
| -------------------- | ------ | ------- |
| 0 (first page)       | 0.4 ms | 0.15 ms |
| 10,000               | 1.0 ms | 0.15 ms |
| 100,000              | 8.5 ms | 0.23 ms |
| 1,000,000            | 105 ms | 0.14 ms |
| 4,900,000            | 452 ms | 0.16 ms |

OFFSET grows linearly with depth. Keyset stays flat. At the deepest page the difference is roughly **2800x**. These numbers are also the best case for OFFSET: the data was in memory and the query only touched the index. When data has to come from disk, OFFSET gets worse and keyset stays about the same.

## Why OFFSET gets slow

`OFFSET 1000000` does not jump to row 1,000,000. An index can find a value quickly, but not a position — nothing in it records which entry is the millionth. So Postgres walks the index from the start, counts off a million entries, discards them, and returns the next 20. The `EXPLAIN ANALYZE` plan shows it (its timings carry measurement overhead, so they differ a little from the table):

```
Limit  (actual time=93.697..93.699 rows=20)
  ->  Index Only Scan using idx_events_occurred_at_id on events
        (actual time=0.013..70.228 rows=1000020)
```

`rows=1000020`: it scanned a million rows to return twenty. Every request pays for every row before the offset.

## The keyset query

Keyset replaces "skip N rows" with "start after the last row I saw". The client sends back the values of the last row from the previous page:

```sql
SELECT id, occurred_at, event_type, actor_id, payload
FROM events
WHERE (occurred_at, id) > ('2024-12-13 05:20:00+00', 1000000)
ORDER BY occurred_at, id
LIMIT 20;
```

The first page is the same query without the `WHERE` clause. For a newest-first feed, flip both: `(occurred_at, id) < (...)` with `ORDER BY occurred_at DESC, id DESC`.

The index now seeks directly to a value:

```
Limit  (actual time=0.028..0.031 rows=20)
  ->  Index Only Scan using idx_events_occurred_at_id on events
        (actual time=0.028..0.029 rows=20)
        Index Cond: (ROW(occurred_at, id) > ROW('2024-12-13 05:20:00+00', 1000000))
```

`rows=20`: it read exactly what it returned. The cost of a keyset page depends on page size, not depth, which is why the keyset column stays flat.

![OFFSET vs keyset pagination on the same 5 million row events table with the same index. On the left, OFFSET 1,000,000 walks the index from the top, scanning and discarding a million rows before returning 20, taking 105 ms. On the right, keyset jumps straight to the cursor position and reads exactly the 20 rows it returns, taking 0.14 ms.](./image1.png)

## The tiebreaker is not optional

The simpler version is wrong:

```sql
WHERE occurred_at > '2024-12-13 05:20:00+00'   -- don't do this
```

Timestamps collide. Busy systems record events with identical timestamps, and batch inserts create hundreds of them at once. If the cursor is only `occurred_at`, the `>` comparison silently skips the remaining rows that share the boundary timestamp — no error, just missing data. Postgres also makes no ordering guarantee among rows with equal sort values, so pages are not even stable between runs.

The fix: add `id` to the sort so every row sorts uniquely, and compare both values as a row:

```sql
-- compare the pair: correct and uses the index cleanly
WHERE (occurred_at, id) > ($1, $2)

-- hand-written equivalent: easy to get wrong
WHERE occurred_at > $1
   OR (occurred_at = $1 AND id > $2)
```

Both mean the same thing, but the row comparison is a single condition Postgres maps directly onto the index, and it is harder to get wrong.

## What the API returns

Clients should never build a cursor, only echo one back. Each response carries an opaque token for the next page:

```json
{
  "data": [ ... 20 events ... ],
  "next_cursor": "eyJvIjoiMjAyNC0xMi0xM1QwNToyMDowMFoiLCJpZCI6MTAwMDAwMH0"
}
```

The token is the last row's `(occurred_at, id)`, base64-encoded. If the API accepted a raw timestamp and id, clients would couple to your sort columns. An opaque token lets you change the sort, add fields, or change the format without breaking callers. A `null` `next_cursor` means last page. A cursor that fails to decode is a 400, not a guess.

## When OFFSET is still the right call

Keyset gives up things you might need:

- **Jumping to page N.** A cursor only knows "after this row". If the UI needs "go to page 47", keyset cannot do it.
- **"Page 3 of 812".** Page numbers and totals do not exist with cursors.
- **Arbitrary sorts.** Keyset needs an index matching the sort order. If users can sort by any column, every sort needs its own index, and computed sorts (relevance score, distance) have no index to seek into.
- **Small tables.** At depth 10,000, OFFSET costs one millisecond. An admin screen paging a few thousand rows will never notice, and OFFSET is less code.

Rule of thumb: infinite scroll, feeds, exports, and any API where clients walk large result sets get keyset. Numbered-page UIs over modest data keep OFFSET.

## The takeaway

OFFSET does work proportional to depth. Keyset does work proportional to page size. On five million rows, that is 452 ms versus 0.16 ms for the same twenty rows. Migration has real costs — cursor handling in the API, a tiebreaker column, no page numbers — so decide per endpoint rather than as a blanket rule. But for anything shaped like a feed or an event log, use keyset. The gap only grows with the table.

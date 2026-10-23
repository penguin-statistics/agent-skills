# REST API quick reference

Base URL: `https://penguin-stats.io/PenguinStats/api/v2/`. Read endpoints are `GET`, need no key, and allow
cross-origin requests (`Access-Control-Allow-Origin: *`, no credentials).

- Contract: https://penguin-stats.io/swagger/doc.json (Swagger 2.0). Its `info.license` (MIT) is the license of the
  **code**; the **data** is CC BY-NC 4.0.
- Human docs: https://developer.penguin-stats.io/public-api/ (Markdown index: `/public-api/llms.txt`).

| Endpoint | Use | Size (gzip) |
|---|---|---|
| `GET /result/matrix?server=CN&itemFilter=30012` | Drop data of one item, every open stage | ~4 KB |
| `GET /result/matrix?server=CN&stageFilter=main_01-07` | Drop data of one stage | <1 KB |
| `GET /result/matrix?server=CN` | Whole matrix of a server (1 MB raw): fetch once, cache | ~100 KB |
| `GET /stages/{stageId}?server=CN` | One stage: `code`, `code_i18n`, `apCost`, `zoneId`, `dropInfos` | ~1 KB |
| `GET /stages?server=CN` | Every stage of a server (1.3 MB raw): cache for a day | ~60 KB |
| `GET /items` / `GET /items/{itemId}` | Items with `name_i18n`, `alias`, `pron`, `itemType`, `rarity` | ~13 KB / <1 KB |
| `GET /zones` / `GET /zones/{zoneId}` | Zones (chapters, events) with open/close times per server | ~20 KB |
| `GET /period?server=CN` | Event periods (drop bonuses) | ~9 KB |
| `GET /result/trends?server=CN` | Daily counts per stage and item, whole server only: fetch once, cache | ~160 KB |
| `GET /result/pattern?server=CN` | Joint drop patterns (single-run reports only), whole server only | ~230 KB |

Matrix query parameters: `server` (`CN` default, `US`, `JP`, `KR`), `stageFilter` and `itemFilter` (comma-separated
IDs), `show_closed_zones` (`false` default: only zones open now; `true` adds past events, for history).

Matrix element:

```json
{"stageId": "main_01-07", "itemId": "30012", "times": 2168906780, "quantity": 2700304289,
 "stdDev": 2.1941, "start": 1556676000000, "end": null}
```

## IDs

- Items: numeric strings for materials (`30012` Orirock Cube / 固源岩), other strings for the rest. Look them up in
  `/items` by `name_i18n` (zh, en, ja, ko) or `alias` (zh, ja nicknames); several items can share an alias.
- Stages: `main_01-07` (code `1-7`), `tough_10-06` (the tough version), `sub_02-12` (`S2-12`), `act19side_05_perm`
  (an event stage left open for good), `..._rep` (a rerun), `wk_*` supply stages. Never build a stage ID from a code:
  `main_10-06` is 10-7. The same code can belong to several stages (normal and tough, event and rerun): look the code
  up in `/stages` (`code`, `code_i18n`) and match on `stageId`.

## Limits and errors

- Filtered `/result/*` requests: 300 per 5 minutes per IP (see `X-RateLimit-*` headers). Unfiltered requests are not
  limited by the application, but are large: cache them.
- Only `/result/matrix` takes `itemFilter` and `stageFilter`. `/result/trends` and `/result/pattern` ignore them and
  return the whole server, and a filter only makes the request count against the limit above.
- `POST /result/advanced` has its own tight limit and is expensive. Do not use it.
- `429` comes with `Retry-After` (seconds). Back off and retry later; do not retry in a loop.
- Unknown IDs return `{"code": "NOT_FOUND", ...}`.
- Data-as-of: the body has no such field. The unfiltered matrix (and `/stages`, `/items`) send `Last-Modified`, the
  time the data was last calculated; filtered matrix responses do not, so record the time you fetched them (`Date`)
  and show that.

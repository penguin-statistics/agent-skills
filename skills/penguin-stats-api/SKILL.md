---
name: penguin-stats-api
description: Query Arknights (明日方舟) item drop rates from Penguin Statistics (企鹅物流数据统计, penguin-stats.io), the crowdsourced drop statistics of the CN, US, JP and KR game servers. Use when the user asks where to farm (刷图) an item, which stage drops a material best, the drop rate (掉率) or sanity (理智) cost per item of a stage, what a stage drops or which events are open, or when writing code that calls the Penguin Statistics API or its MCP server. Covers which endpoint or MCP tool to use, how to compute drop rates (quantity / times), time windows, servers, rate limits and etiquette, and how to credit the data (CC BY-NC 4.0).
license: MIT
compatibility: Needs network access to https://penguin-stats.io (REST API) or to the Penguin Statistics MCP server (https://mcp.penguin-stats.io/mcp).
metadata:
  author: penguin-statistics
  version: "1.0.0"
---

# Penguin Statistics drop data

Penguin Statistics (企鹅物流数据统计) adds up the drops that players report for each run of an Arknights stage,
per game server, into drop rates by stage and item. It is the primary source of Arknights drop rates; wikis and
other tools copy it.

## Pick the access path

1. **MCP tools are connected** (a server named `penguin-stats`, tools such as `search_items`,
   `get_item_drop_rates`): answer the user with them, following the recipes below. They return small, precomputed
   results with the data-as-of time and the attribution. Prefer `get_dataset_info` over this skill: the server
   serves it live, so where its definitions, caveats or license differ from the text here, follow it. Call it when
   unsure how to read or cite a number.
2. **Writing code, or no MCP**: use the REST API at `https://penguin-stats.io/PenguinStats/api/v2/`. See
   [references/rest-api.md](references/rest-api.md).
3. **Answering from memory or a wiki**: don't. Drop tables change with events; fetch current data.

To connect the MCP server: [references/mcp.md](references/mcp.md).

## Rules

- **Always choose the server** (`CN`, `US`, `JP`, `KR`; US is the global/English server) and say which one the numbers
  are for. The API defaults to CN when `server` is left out; pass it anyway.
- **Drop rate = `quantity / times`**: the expected number of the item per run. It can exceed 1 (100%). `times` is the
  number of runs, not of reports. Sanity per item = `apCost / (quantity / times)`.
- **Say when the data is from**: the data-as-of time (MCP `dataAsOf`; REST `Last-Modified` when sent, else the time
  you fetched it) and the window start (`start`). `end: null` means the window is still running: the stage drops the item now.
- **Flag noisy rates**: fewer than 100 runs (`times < 100`) is a low sample. Prefer stages with large samples when
  recommending where to farm.
- **Credit the data** wherever you show or store it:
  `Data: Penguin Statistics (penguin-stats.io), CC BY-NC 4.0` with a link to
  https://creativecommons.org/licenses/by-nc/4.0/ . Put it in program output, in a comment of generated code, or under
  the answer. MCP results carry it as `source.attribution`: show that one.
- **Never call `POST /result/advanced`** (advanced query): it is expensive and separately rate limited. Filtered
  `GET /result/matrix` (`itemFilter`, `stageFilter`) covers the usual questions. `/result/trends` takes only `server`
  and ignores filters, so fetch it once (~160 KB gzip) and cache it.
- **Never submit reports** (`POST /report*`) and never write code that fabricates drop reports. Reports must come from
  real game results; fake ones corrupt everyone's statistics.
- **Be gentle**: send an identifying `User-Agent` with a contact URL or e-mail, send `Accept-Encoding: gzip`, cache
  responses for at least 5 minutes (the server caches for 300 s), and fetch the large lists (`/stages`, `/items`,
  `/zones`, the unfiltered matrix) once and keep them, instead of once per question. On `429`, wait `Retry-After`
  seconds.
- **Use `penguin-stats.io`**. `penguin-stats.cn` is the mainland China mirror and its API may be unreachable from
  elsewhere.

## Recipes with MCP

Pass `server` on every call that takes it, and `lang` (`zh`, `en`, `ja`, `ko`) for names in the user's language.
Arguments are in [references/mcp.md](references/mcp.md).

- **"Where do I farm X?" (X 去哪刷)**
  1. `search_items(query="X")`. If `ambiguous` is true (石头 matches every tier of Orirock), list the candidates and
     ask which one; don't pick for the user.
  2. `get_item_drop_rates(item_id=..., server=..., top_n=3)`. The default order is sanity per item; pass
     `sort_by="drop_rate"` when the user asks for the highest drop rate.
  3. Answer with each stage's code, sanity per item, drop rate and runs (`times`), and flag rows with `lowSample`.
     Then give the server, `dataAsOf` and `source.attribution`.
- **"What does 1-7 drop?"**
  1. `search_stages(query="1-7", server=...)`. One code can name several stages: the normal and the tough version
     (`difficulty`), or an event stage and its rerun or permanent copy (`variant`). Take the one the user means, or ask.
  2. `get_stage_drops(stage_id=..., server=...)`.
- **"Which events are open now?"** `list_events(server=...)`, then `get_stage_drops` for the stages the user asks
  about.
- **"How fresh is the data?" or "How do I cite it?"** `get_dataset_info()`: `dataAsOf` and `latestEventOpenTime` per
  server, the definitions and caveats, the license and the attribution.

## Recipe: best stages for an item, with the REST API

For "the top 3 stages for Orirock Cube on CN":

1. Find the item ID: `GET /items` (cache it) and match `name_i18n` (zh, en, ja, ko) or `alias`; aliases are not
   unique (石头 is every tier of Orirock), so ask when several items match. Orirock Cube (固源岩) is `30012`.
2. `GET /result/matrix?server=CN&itemFilter=30012`: one element per open stage that dropped the item
   (`stageId`, `times`, `quantity`, `start`, `end`). Keep `end == null`.
3. Rank by `quantity / times` (drop rate) or by `apCost / rate` (sanity per item, the usual "most efficient" meaning).
   Ask which one the user means if unclear. Leave out or flag `times < 100`.
4. Get stage codes and sanity costs from `GET /stages/{stageId}?server=CN`, or from the cached `GET /stages?server=CN`.
5. Print server, fetch time, window start, runs, and the attribution.

[scripts/top_stages.py](scripts/top_stages.py) does all of this with the Python standard library:
`python3 scripts/top_stages.py 30012 --server CN --top 3 [--sort sanity]`. The path is relative to this skill's
directory, which is `${CLAUDE_SKILL_DIR}` in Claude Code.

## Checklist for code

A script or app that uses the data, written by you or by the user, should do all of these without being asked:

1. Send `server` on every request (`server=CN` for 国服) and print which server the numbers are for.
2. Print when the data is from: `Last-Modified` or the fetch time, and the window start (`start`) of each row.
3. Compute the drop rate as `quantity / times`, and sanity per item as `apCost / (quantity / times)`.
4. Read only with `GET` (`/result/matrix` filtered by item or stage, `/stages`, `/items`, `/zones`): no
   `POST /result/advanced`, no `POST /report*`.
5. Print the attribution `Data: Penguin Statistics (penguin-stats.io), CC BY-NC 4.0`, and put it in a comment.

## Pitfalls

- A (stage, item) pair missing from the global matrix means it was never dropped in the window. It may still be in
  the stage's drop table; the matrix leaves out `quantity = 0`.
- Windows are per (stage, item): items of the same stage can have different `start` and `times`, because a window
  restarts when the drop table of that item changes.
- `start` is the nominal window start, not the first sample. Times are UTC epoch milliseconds with second precision;
  the window is `[start, end)`.
- Gacha and recruitment rows count items drawn and recruitments, not runs, and have no sanity cost.
- New events on US/JP/KR may be added late; the catalog can lag the game by a few days.
- `stdDev` in the matrix is only approximate; the pattern matrix (`/result/pattern`) counts single-run reports only, so
  it does not match the drop matrix.

Details: [references/semantics.md](references/semantics.md).

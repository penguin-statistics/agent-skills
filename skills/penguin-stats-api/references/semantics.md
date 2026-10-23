# What the numbers mean

Checked against the backend code and production data on 2026-10-22.

## times, quantity, drop rate

- `times`: runs of the stage in the window (one report can cover up to 10 runs). Never 0 in the API.
- `quantity`: total number of the item dropped in those runs.
- Drop rate `quantity / times`: expected items per run. Can exceed 1 (Orirock Cube on S2-12 is about 2.29 per run);
  the website shows it as a percentage, possibly above 100%.
- Sanity per item: `apCost / (quantity / times)`. `apCost` comes from `/stages`.
- Gacha boxes: `times` is the number of items drawn, so the rate is per draw. Recruitment: one report per
  recruitment. Neither has a sanity cost.

## Windows

- `start`, `end`: UTC epoch milliseconds, half-open `[start, end)`, second precision.
- `end: null`: the window is still running (the stage drops the item now). Not a database value.
- Each (stage, item) has its own window. A window restarts when the drop table of that item on that stage changes
  (for example after an event added a bonus drop), so items of one stage can have different `start` and `times`.
- `start` is the nominal start of the window. Early windows can begin before the first stored report.
- Daily buckets (`/result/trends`) cut at the server's local midnight: CN UTC+8, US UTC-7, JP and KR UTC+9.
- First data: CN from May 2019; US, JP, KR from May 2020.

## What is left out

- The global matrix omits pairs with `quantity = 0`: a missing pair may still be in the drop table.
- Only reports judged reliable count. Reports with impossible drops are filtered out.
- The pattern matrix counts single-run reports only, so its sample differs from the drop matrix.
- `stdDev` is computed per report, not per run: treat it as approximate.

## Servers

`CN` (mainland China), `US` (global, English), `JP`, `KR`. Stages and events differ between servers: always pass and
state the server. Penguin Statistics may add new US/JP/KR events a few days late.

## License

Data: CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/). Credit it as
`Data: Penguin Statistics (penguin-stats.io), CC BY-NC 4.0`. The source code of Penguin Statistics is MIT.

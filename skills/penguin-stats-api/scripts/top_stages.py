#!/usr/bin/env python3
"""List the stages with the best drop rate (or sanity per item) of an Arknights item on Penguin Statistics.

Standard library only. Usage:
  python3 top_stages.py 30012 --server CN --top 3
  python3 top_stages.py "Orirock Cube" --server US --sort sanity

Data: Penguin Statistics (penguin-stats.io), CC BY-NC 4.0.
"""
import argparse
import datetime as dt
import gzip
import json
import sys
import urllib.parse
import urllib.request

API = "https://penguin-stats.io/PenguinStats/api/v2"
# Identify your program and how to reach you; replace with your own project URL or e-mail.
USER_AGENT = "penguin-stats-skill-example/1.0 (+https://github.com/penguin-statistics/agent-skills)"
ATTRIBUTION = "Data: Penguin Statistics (penguin-stats.io), CC BY-NC 4.0 (https://creativecommons.org/licenses/by-nc/4.0/)"
LOW_SAMPLE = 100  # runs; below this a rate is noisy


def get(path, **params):
    url = f"{API}/{path}" + (("?" + urllib.parse.urlencode(params)) if params else "")
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept-Encoding": "gzip"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        body = resp.read()
        if resp.headers.get("Content-Encoding") == "gzip":
            body = gzip.decompress(body)
        return json.loads(body)


def resolve_item(query):
    q = query.strip().lower()
    matches = []
    for it in get("items"):
        names = [it["itemId"], it["name"], *it.get("name_i18n", {}).values()]
        for aliases in (it.get("alias") or {}).values():
            names.extend(aliases)
        if q in (n.lower() for n in names if n):
            matches.append(it)
    if len(matches) == 1:
        return matches[0]
    if not matches:
        sys.exit(f"no item matches {query!r}; use its itemId (for example 30012)")
    # Aliases are not unique: 石头 is every tier of Orirock. Ask instead of guessing.
    listed = ", ".join(f"{m['itemId']} {m.get('name_i18n', {}).get('en') or m['name']}" for m in matches)
    sys.exit(f"{query!r} matches several items ({listed}); pass the itemId")


def utc(ms):
    return dt.datetime.fromtimestamp(ms / 1000, dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("item", help="itemId (30012) or a name/alias in zh/en/ja/ko")
    ap.add_argument("--server", default="CN", choices=["CN", "US", "JP", "KR"])
    ap.add_argument("--top", type=int, default=3)
    ap.add_argument("--min-runs", type=int, default=LOW_SAMPLE,
                    help="leave out stages with fewer runs than this (noisy rates); 0 keeps all")
    ap.add_argument("--sort", default="rate", choices=["rate", "sanity"],
                    help="rate: items per run; sanity: sanity cost per item (lower is better)")
    args = ap.parse_args()

    item = resolve_item(args.item)
    fetched_at = dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    # Default show_closed_zones=false: only the zones open on the server now.
    matrix = get("result/matrix", server=args.server, itemFilter=item["itemId"])["matrix"]
    # end == null: the window is still running, so the stage drops the item now.
    rows = [m for m in matrix if m["end"] is None and m["times"] > 0]
    noisy = [m for m in rows if m["times"] < args.min_runs]
    rows = [m for m in rows if m["times"] >= args.min_runs]
    stages = {s["stageId"]: s for s in get("stages", server=args.server)}  # ~60 KB gzipped; cache it in real code
    out = []
    for m in rows:
        st = stages.get(m["stageId"], {})
        rate = m["quantity"] / m["times"]  # expected items per run; can exceed 1
        ap_cost = st.get("apCost")
        out.append({**m, "code": st.get("code", m["stageId"]), "apCost": ap_cost, "rate": rate,
                    "sanity": (ap_cost / rate) if ap_cost and rate > 0 else None})
    if args.sort == "rate":
        out.sort(key=lambda r: -r["rate"])
    else:
        out = sorted((r for r in out if r["sanity"] is not None), key=lambda r: r["sanity"])

    name = item.get("name_i18n", {}).get("en") or item["name"]
    print(f"{name} ({item['itemId']}) on the {args.server} server, open stages, by {args.sort}; fetched {fetched_at}")
    for r in out[: args.top]:
        flag = "  (low sample)" if r["times"] < LOW_SAMPLE else ""
        sanity = f"{r['sanity']:.2f} sanity/item" if r["sanity"] is not None else "no sanity cost"
        print(f"  {r['code']:<10} {r['stageId']:<22} {r['rate'] * 100:7.2f}% per run  {sanity:<20} "
              f"runs={r['times']} quantity={r['quantity']} window since {utc(r['start'])}{flag}")
    if noisy:
        print(f"  ({len(noisy)} stage(s) with fewer than {args.min_runs} runs left out; --min-runs 0 keeps them)")
    print(ATTRIBUTION)


if __name__ == "__main__":
    main()

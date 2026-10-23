#!/usr/bin/env python3
"""Check that the live MCP server has the tools the skill documents, at the URL the plugin connects to.

The skill names the tools and their arguments (references/mcp.md) and the plugin points every client at one URL;
both are only right while the server agrees, and the server is released from another repository (backend-next). A
GET of the endpoint is a 405 by design, so a link checker can't tell; this sends what a client sends. Standard library
only.
"""
import json
import pathlib
import re
import sys
import urllib.request

ROOT = pathlib.Path(__file__).resolve().parents[2]
REFERENCE = ROOT / "skills/penguin-stats-api/references/mcp.md"


def call(url, method, params=None):
    body = json.dumps({"jsonrpc": "2.0", "id": 1, "method": method, "params": params or {}}).encode()
    req = urllib.request.Request(url, data=body, method="POST", headers={
        "Content-Type": "application/json",
        "Accept": "application/json, text/event-stream",
        "MCP-Protocol-Version": "2025-06-18",
        "User-Agent": "penguin-statistics/agent-skills CI (+https://github.com/penguin-statistics/agent-skills)",
    })
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)["result"]


def main():
    url = json.loads((ROOT / ".mcp.json").read_text(encoding="utf-8"))["mcpServers"]["penguin-stats"]["url"]
    tools = {t["name"]: t for t in call(url, "tools/list")["tools"]}
    # The table rows of the reference start with the call: | `get_stage_drops(stage_id, server?, lang?)` | ...
    # an argument without "?" is required
    documented, required = {}, {}
    for name, args in re.findall(r"^\| `(\w+)\(([^)]*)\)` \|", REFERENCE.read_text(encoding="utf-8"), re.M):
        args = [a.strip() for a in args.split(",") if a.strip()]
        documented[name] = {a.rstrip("?") for a in args}
        required[name] = {a for a in args if not a.endswith("?")}

    problems = []
    if set(documented) != set(tools):
        problems.append(f"tools: the server has {sorted(tools)}, {REFERENCE.name} documents {sorted(documented)}")
    for name in sorted(set(documented) & set(tools)):
        live = set(tools[name]["inputSchema"].get("properties", {}))
        if documented[name] != live:
            problems.append(f"{name}: the server takes {sorted(live)}, {REFERENCE.name} documents {sorted(documented[name])}")
        live_required = set(tools[name]["inputSchema"].get("required", []))
        if required[name] != live_required:
            problems.append(f"{name}: the server requires {sorted(live_required)}, {REFERENCE.name} marks "
                            f"{sorted(required[name])} required (no ?)")
        if not tools[name].get("annotations", {}).get("readOnlyHint"):
            problems.append(f"{name}: not marked read-only, while the reference says the server is read-only")
    for p in problems:
        print(f"FAIL {p}")
    if problems:
        sys.exit(f"{len(problems)} problem(s)")
    print(f"ok   {url}: {len(tools)} tools, the same as {REFERENCE.relative_to(ROOT)} with the same required "
          "arguments, all read-only")


if __name__ == "__main__":
    main()

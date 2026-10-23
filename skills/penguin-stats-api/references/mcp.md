# Penguin Statistics MCP server

Read-only, no authentication, Streamable HTTP: `https://mcp.penguin-stats.io/mcp`

Setup steps for each client (Claude, ChatGPT, Cursor, VS Code, Cherry Studio, Codex, Gemini CLI and others) are at
https://mcp.penguin-stats.io/ .

- Claude Code: `claude mcp add --transport http --scope user penguin-stats https://mcp.penguin-stats.io/mcp`
- Claude (web, desktop): Customize → Connectors → Add custom connector, with the URL above; under Authentication
  choose "No sign in".
- Other clients: add a remote MCP server with the URL above and the Streamable HTTP transport. Some clients default
  to the old SSE transport, which fails.

| Tool | Use |
|---|---|
| `search_items(query, lang?, limit?)` | Item IDs from a name, alias, pinyin or ID in any language. Check `ambiguous`. |
| `search_stages(query, server?, lang?, limit?)` | Stage IDs from a code (`1-7`), stage ID or zone name. Check `ambiguous`. |
| `get_item_drop_rates(item_id, server, top_n?, include_closed?, sort_by?, lang?)` | Where to farm an item: rate, sanity per item, runs, window. `sort_by`: `sanity_per_item` (default) or `drop_rate`. |
| `get_stage_drops(stage_id, server, lang?)` | What a stage drops. |
| `list_events(server, open_only?, lang?, limit?)` | Events open or upcoming now, with their stages. |
| `get_dataset_info()` | Definitions, caveats, data-as-of per server, license and attribution. |

`server` is required by the drop and event tools: take it from the conversation or ask the user (`search_stages` only
ranks and marks stages by it, CN when left out). `item_id` also takes the item's name in any language. Drop results carry `dataAsOf` (`list_events`: `now`), and every result a
`source` with the attribution to show. Results are small (top-N lists), so there is no need to page through the whole
matrix.

The server allows 1200 requests per minute per IP address. Past that it answers HTTP 429 with `Retry-After` and the
error "rate limited, retry after N s": wait that long, then retry once.

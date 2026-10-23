# Penguin Statistics agent skills

Skills that teach AI assistants and coding agents to use [Penguin Statistics](https://penguin-stats.io)
(企鹅物流数据统计), the crowdsourced Arknights drop statistics, the right way: say which game server the numbers are
for, compute drop rates correctly, give the time of the data, prefer large samples, and credit the data. They follow
the [Agent Skills](https://agentskills.io) format, so they work in Claude, Claude Code, Codex, Cursor, GitHub Copilot,
Gemini CLI and other agents.

| Skill | What it does |
|---|---|
| [`penguin-stats-api`](skills/penguin-stats-api/SKILL.md) | Answers "where do I farm X" and "what does 1-7 drop" with the Penguin Statistics MCP server or REST API, and writes correct code against the API |

The skill works best with the Penguin Statistics MCP server, `https://mcp.penguin-stats.io/mcp`: free, read-only, no
account and no API key. How to add it to Claude, ChatGPT, Cursor, VS Code, Cherry Studio and other apps:
**https://mcp.penguin-stats.io/**

## Install

- **Any agent** (Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, OpenCode and others), with Node.js:

  ```sh
  npx skills add penguin-statistics/agent-skills
  ```

- **Claude** (claude.ai, desktop app): zip the `skills/penguin-stats-api` folder (the folder itself, not its files)
  and upload the zip under **Customize → Skills**.

## Try it

Ask your assistant, in any language:

- "Where should I farm Orirock Cube on the CN server?"
- "What does 1-7 drop on the US server?"
- "写一个脚本，查询国服固源岩掉率最高的前 3 个关卡并打印"

Or run the example script, which needs only Python 3:

```sh
python3 skills/penguin-stats-api/scripts/top_stages.py 30012 --server CN --top 3
```

## What it sends

The skill is text and an example script; it sends nothing by itself. An agent that follows it calls the public
Penguin Statistics API (`penguin-stats.io`) or the MCP server (`mcp.penguin-stats.io`) with item names or IDs, stage
codes and the game server, never your conversation. What the MCP server logs, and for how long:
https://mcp.penguin-stats.io/#privacy

## License

Skill text and scripts: [MIT](LICENSE). Penguin Statistics data:
[CC BY-NC 4.0](https://creativecommons.org/licenses/by-nc/4.0/), free for non-commercial use with credit. Credit it as
`Data: Penguin Statistics (penguin-stats.io), CC BY-NC 4.0`.

## Contributing

Rules for changes are in [AGENTS.md](AGENTS.md). Report a problem:
https://github.com/penguin-statistics/agent-skills/issues

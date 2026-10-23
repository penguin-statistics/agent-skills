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

### The plugin: MCP server and skill together

- **Claude Code** (2.1.292 or later):

  ```
  /plugin install penguin-stats --marketplace penguin-statistics/agent-skills
  ```

  On older versions: `/plugin marketplace add penguin-statistics/agent-skills`, then
  `/plugin install penguin-stats@penguin-statistics`.

- **Claude** (claude.ai, desktop app): **Customize → Plugins → Add → Add marketplace**, enter
  `penguin-statistics/agent-skills` and add **Penguin Statistics**. Then connect the server on the plugin's
  **Connectors** tab (no sign-in needed).

- **Codex**:

  ```sh
  codex plugin marketplace add penguin-statistics/agent-skills
  codex plugin add penguin-stats@penguin-statistics
  ```

- **Gemini CLI**:

  ```sh
  gemini extensions install https://github.com/penguin-statistics/agent-skills
  ```

- **VS Code** (GitHub Copilot): with the `chat.plugins.enabled` setting on, run **Chat: Install Plugin From Source**
  from the Command Palette and enter `https://github.com/penguin-statistics/agent-skills`.

If you added the server by hand before, you can remove that entry: Claude Code and claude.ai treat the two as one
server, but other apps may load the tools twice.

### The skill only

- **Any agent** (Claude Code, Codex, Cursor, GitHub Copilot, Gemini CLI, OpenCode and others), with Node.js:

  ```sh
  npx skills add penguin-statistics/agent-skills
  ```

- **Claude** (claude.ai, desktop app): zip the `skills/penguin-stats-api` folder (the folder itself, not its files)
  and upload the zip under **Customize → Skills**.

### The MCP server only

Steps for Claude, ChatGPT, Cursor, VS Code, Cherry Studio, Codex, Gemini CLI and others, with one-click links where
the app has them: **https://mcp.penguin-stats.io/**

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

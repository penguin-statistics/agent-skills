# AGENTS.md

This repository publishes Agent Skills (https://agentskills.io/specification) for Penguin Statistics data. It is
public, and agents outside the project install it as it is.

- One directory per skill under `skills/<name>/`. `name` in `SKILL.md` must equal the directory name; `description`
  stays within 1024 characters and starts with what the skill does and when to use it.
- Keep `SKILL.md` under 500 lines; put details in `references/` (one level deep) and runnable examples in `scripts/`
  (Python standard library only). Refer to files by their path relative to the skill directory.
- Facts about the data must match backend-next (`internal/controller/mcp`, the `get_dataset_info` definitions and
  caveats) and the live API. Check every number and endpoint you write against the live API before committing, and
  update the skill when backend-next changes the public API, its semantics or the MCP tools.
- Never document `POST /result/advanced` or any `POST /report*` endpoint.
- No secrets, internal host names or IP addresses, in files or in commit messages.
- `CLAUDE.md` is a symlink to this file.

## The plugin

The repository root is also one plugin, `penguin-stats`: the MCP server plus everything under `skills/`. Each client
reads its own manifest:

| File | Read by |
|---|---|
| `.claude-plugin/plugin.json`, `.mcp.json` | Claude Code, claude.ai and the Claude desktop app |
| `.claude-plugin/marketplace.json` | the same, to install from this repository (Codex reads it too) |
| `plugin.json`, `mcp.json` | Agent Plugins 1.0.0 clients: Codex, VS Code, Cursor |
| `gemini-extension.json` | Gemini CLI |

- Keep `name` and `version` the same in `.claude-plugin/plugin.json`, `plugin.json`, `gemini-extension.json` and the
  `metadata.version` of each `SKILL.md`. Bump `version` with every change users should get: Claude Code and Codex
  keep an installed plugin on its version until the version changes.
- The server URL is `https://mcp.penguin-stats.io/mcp`. `.mcp.json` uses it exactly, so that Claude Code and claude.ai
  take the plugin's server and a connector added by hand for one server (they compare the whole URL, query included).
  `mcp.json` and `gemini-extension.json` add `?via=plugin`, which marks plugin installs; the server answers the same
  without it.
- Gemini CLI wants `httpUrl` for Streamable HTTP (its `url` means the old SSE transport). Don't add `contextFileName`
  or a `GEMINI.md`: Gemini would load it into every conversation, while skills load only when needed.
- `assets/logo.png` is the 512×512 icon of penguin-stats.io, for plugin listings.

## Checks

```sh
# the Agent Skills reference validator (agentskills/agentskills, pinned)
uvx --from 'git+https://github.com/agentskills/agentskills@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref' \
  skills-ref validate skills/penguin-stats-api
# the Claude marketplace, plugin manifest and skills
claude plugin validate . --strict
# the Gemini CLI extension
npx -y @google/gemini-cli@0.63.0 extensions validate .
# each script once against the live API
python3 skills/penguin-stats-api/scripts/top_stages.py 30012 --server CN --top 3
```

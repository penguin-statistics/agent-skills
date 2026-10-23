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

## Checks

```sh
# the Agent Skills reference validator (agentskills/agentskills, pinned)
uvx --from 'git+https://github.com/agentskills/agentskills@69ef37e9424c0a7ea9dd2293b559e43ec8176379#subdirectory=skills-ref' \
  skills-ref validate skills/penguin-stats-api
# each script once against the live API
python3 skills/penguin-stats-api/scripts/top_stages.py 30012 --server CN --top 3
```

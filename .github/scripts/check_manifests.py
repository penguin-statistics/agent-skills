#!/usr/bin/env python3
"""Check the plugin manifests against their current schemas and against each other.

Each client reads its own manifest (see AGENTS.md), and a client that finds an error in one skips the plugin or its
server without a word, so this checks every one of them: against the schema its client publishes, fetched now so a
change of the schema shows up here, and against the other manifests, which must name the same plugin, version and
server. Needs jsonschema: uv run --no-project --with jsonschema python .github/scripts/check_manifests.py
"""
import json
import pathlib
import re
import sys
import urllib.request

import jsonschema

ROOT = pathlib.Path(__file__).resolve().parents[2]
NAME = "penguin-stats"
SERVER = "penguin-stats"
MCP_URL = "https://mcp.penguin-stats.io/mcp"
# The Claude manifests must use the exact connector URL: Claude Code and claude.ai take two servers with the same URL
# for one, and a query string makes them two. The others mark plugin installs.
MCP_URL_PLUGIN = MCP_URL + "?via=plugin"
# Gemini CLI publishes no schema for gemini-extension.json, only for settings.json, whose MCP server entries are the
# ones an extension declares. These are the keys its extension reference documents.
GEMINI_SETTINGS_SCHEMA = "https://raw.githubusercontent.com/google-gemini/gemini-cli/main/schemas/settings.schema.json"
GEMINI_KEYS = {"name", "version", "description", "mcpServers", "contextFileName", "excludeTools", "migratedTo", "plan",
               "settings", "themes"}

errors = []


def fail(msg):
    errors.append(msg)
    print(f"FAIL {msg}")


def load(path):
    return json.loads((ROOT / path).read_text(encoding="utf-8"))


def fetch(url):
    req = urllib.request.Request(url, headers={"User-Agent": "penguin-statistics/agent-skills CI"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.load(resp)


def check_schema(path, doc, schema_url, schema=None):
    schema = schema or fetch(schema_url)
    cls = jsonschema.validators.validator_for(schema)
    cls.check_schema(schema)
    problems = sorted(cls(schema).iter_errors(doc), key=lambda e: list(e.absolute_path))
    for e in problems:
        fail(f"{path}: {'/'.join(map(str, e.absolute_path)) or '(root)'}: {e.message} (schema {schema_url})")
    if not problems:
        print(f"ok   {path} against {schema_url}")


def frontmatter(skill_md):
    # The frontmatter of a SKILL.md is flat YAML: name, description and compatibility on one line each, and a
    # metadata map of quoted strings. skills-ref parses it properly; this only reads the fields compared here.
    text = skill_md.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    if not m:
        fail(f"{skill_md.relative_to(ROOT)}: no frontmatter")
        return {}
    fields, section = {}, None
    for line in m.group(1).splitlines():
        if line.startswith("  ") and section:
            k, _, v = line.strip().partition(":")
            fields[f"{section}.{k}"] = v.strip().strip('"')
        else:
            k, _, v = line.partition(":")
            section = k if not v.strip() else None
            fields[k] = v.strip()
    return fields


def main():
    claude = load(".claude-plugin/plugin.json")
    market = load(".claude-plugin/marketplace.json")
    claude_mcp = load(".mcp.json")
    portable = load("plugin.json")
    portable_mcp = load("mcp.json")
    gemini = load("gemini-extension.json")

    # Each file against the schema it names, as its clients do.
    check_schema(".claude-plugin/plugin.json", claude, claude["$schema"])
    check_schema(".claude-plugin/marketplace.json", market, market["$schema"])
    check_schema("plugin.json", portable, portable["$schema"])
    check_schema("mcp.json", portable_mcp, portable_mcp["$schema"])
    settings = fetch(GEMINI_SETTINGS_SCHEMA)
    server_schema = {"$schema": settings.get("$schema"), "$defs": settings["$defs"], "$ref": "#/$defs/MCPServerConfig"}
    for name, server in gemini.get("mcpServers", {}).items():
        check_schema(f"gemini-extension.json mcpServers.{name}", server, GEMINI_SETTINGS_SCHEMA + "#/$defs/MCPServerConfig",
                     server_schema)
    if unknown := set(gemini) - GEMINI_KEYS:
        fail(f"gemini-extension.json: keys its reference does not document: {sorted(unknown)}")
    # A context file would load into every Gemini conversation; the skill loads only when needed.
    if "contextFileName" in gemini or (ROOT / "GEMINI.md").exists():
        fail("gemini-extension.json: no contextFileName or GEMINI.md (see AGENTS.md)")

    # One plugin: the same name and version wherever a client reads them.
    entries = [p for p in market["plugins"] if p["name"] == NAME]
    if len(entries) != 1 or entries[0].get("source") not in ("./", "."):
        fail(f".claude-plugin/marketplace.json: want one entry {NAME!r} with source './', got {market['plugins']}")
    names = {".claude-plugin/plugin.json": claude["name"], "plugin.json": portable["name"],
             "gemini-extension.json": gemini["name"]}
    versions = {".claude-plugin/plugin.json": claude.get("version"), "plugin.json": portable.get("version"),
                "gemini-extension.json": gemini.get("version")}
    for skill_md in sorted(ROOT.glob("skills/*/SKILL.md")):
        fm = frontmatter(skill_md)
        rel = str(skill_md.relative_to(ROOT))
        versions[rel + " metadata.version"] = fm.get("metadata.version")
        if fm.get("name") != skill_md.parent.name:
            fail(f"{rel}: name {fm.get('name')!r} differs from its directory {skill_md.parent.name!r}")
        if not 0 < len(fm.get("description", "")) <= 1024:
            fail(f"{rel}: description has {len(fm.get('description', ''))} characters, want 1 to 1024")
        if len(fm.get("compatibility", "")) > 500:
            fail(f"{rel}: compatibility has more than 500 characters")
    if set(names.values()) != {NAME}:
        fail(f"plugin names differ: {names}")
    if len(set(versions.values())) != 1 or None in versions.values():
        fail(f"versions differ: {versions}")
    else:
        print(f"ok   name {NAME!r} and version {claude['version']!r} everywhere")

    # One server, at the public URL.
    before = len(errors)
    urls = {
        ".mcp.json": (claude_mcp["mcpServers"].get(SERVER, {}).get("url"), {MCP_URL}),
        "mcp.json": (portable_mcp["mcpServers"].get(SERVER, {}).get("url"), {MCP_URL, MCP_URL_PLUGIN}),
        "gemini-extension.json": (gemini.get("mcpServers", {}).get(SERVER, {}).get("httpUrl"), {MCP_URL, MCP_URL_PLUGIN}),
    }
    for path, (url, allowed) in urls.items():
        if url not in allowed:
            fail(f"{path}: server {SERVER!r} has URL {url!r}, want one of {sorted(allowed)}")
    if claude_mcp["mcpServers"].get(SERVER, {}).get("type") != "http":
        fail(".mcp.json: Claude needs type 'http' for Streamable HTTP")
    for path, servers in ((".mcp.json", claude_mcp["mcpServers"]), ("mcp.json", portable_mcp["mcpServers"]),
                          ("gemini-extension.json", gemini.get("mcpServers", {}))):
        if set(servers) != {SERVER}:
            fail(f"{path}: want exactly the server {SERVER!r}, got {sorted(servers)}")
    if len(errors) == before:
        print(f"ok   server {SERVER!r} at {MCP_URL} in every manifest")

    # The listing icon must be there.
    icon = ROOT / claude.get("icon", "")
    if not icon.is_file() or icon.read_bytes()[:8] != b"\x89PNG\r\n\x1a\n":
        fail(f".claude-plugin/plugin.json: icon {claude.get('icon')!r} is not a PNG file")

    if errors:
        sys.exit(f"{len(errors)} problem(s)")


if __name__ == "__main__":
    main()

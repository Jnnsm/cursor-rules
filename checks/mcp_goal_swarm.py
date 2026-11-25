"""Verify project MCP config can launch ForgeSwarm for goal-swarm."""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MCP_PATH = ROOT / ".cursor" / "mcp.json"


def check() -> list[str]:
    if not MCP_PATH.is_file():
        return [f"{MCP_PATH.relative_to(ROOT)}: missing (need goal-swarm MCP config)"]

    try:
        data = json.loads(MCP_PATH.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f".cursor/mcp.json: {exc}"]

    servers = data.get("mcpServers")
    if not isinstance(servers, dict):
        return [".cursor/mcp.json: missing mcpServers object"]

    server = servers.get("goal-swarm")
    if not isinstance(server, dict):
        return [".cursor/mcp.json: missing mcpServers.goal-swarm"]

    issues: list[str] = []
    if server.get("type") != "stdio":
        issues.append('.cursor/mcp.json: goal-swarm.type must be "stdio"')

    command = server.get("command")
    if not isinstance(command, str) or not command.strip():
        issues.append(".cursor/mcp.json: goal-swarm.command required")

    args = server.get("args")
    if not isinstance(args, list) or "forgeswarm" not in args:
        issues.append(".cursor/mcp.json: goal-swarm.args must include forgeswarm")

    directory = _directory_arg(args if isinstance(args, list) else [])
    if directory is None:
        issues.append(".cursor/mcp.json: goal-swarm.args need --directory <forgeswarm>")
    else:
        fs_dir = Path(_expand(directory))
        if not (fs_dir / "pyproject.toml").is_file():
            issues.append(
                f".cursor/mcp.json: ForgeSwarm missing at {fs_dir} "
                "(clone to ~/src/forgeswarm or fix --directory)"
            )

    env = server.get("env")
    db = env.get("FORGESWARM_DB") if isinstance(env, dict) else None
    if not isinstance(db, str) or not db.strip():
        issues.append(".cursor/mcp.json: env.FORGESWARM_DB required")
    else:
        db_path = Path(_expand(db))
        if not db_path.parent.is_dir():
            issues.append(
                f".cursor/mcp.json: FORGESWARM_DB parent missing: {db_path.parent}"
            )

    return issues


def _directory_arg(args: list[object]) -> str | None:
    for i, item in enumerate(args):
        nxt = args[i + 1] if i + 1 < len(args) else None
        if item == "--directory" and isinstance(nxt, str):
            return nxt
    return None


def _expand(value: str) -> str:
    return (
        value.replace("${userHome}", str(Path.home()))
        .replace("${workspaceFolder}", str(ROOT))
        .replace("${pathSeparator}", "/")
        .replace("${/}", "/")
    )

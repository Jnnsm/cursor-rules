"""Prove two ForgeSwarm MCP clients share one instruction/task board.

Two sequential stdio sessions against the same FORGESWARM_DB:
  Agent A (session 1) creates project + plan + task
  Agent B (session 2) sees that task and get_briefing

Run (uses the ForgeSwarm clone's venv / mcp client):

  uv run --directory ~/src/forgeswarm python \\
    /home/jnnsm/Documents/cursor-rules/scripts/swarm_share_smoke.py

Exit 0 = shared control works. Exit 1 = sharing broken.
"""

from __future__ import annotations

import asyncio
import json
import logging
import os
import sys
import tempfile
from collections.abc import Awaitable, Callable
from pathlib import Path
from typing import Any

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

FORGESWARM_DIR = Path(
    os.environ.get("FORGESWARM_DIR", Path.home() / "src" / "forgeswarm")
)
GOAL = "smoke: shared-control proof under one instruction"

logger = logging.getLogger("swarm_share_smoke")


async def call(session: ClientSession, tool: str, **kwargs: Any) -> Any:
    result = await session.call_tool(tool, kwargs)
    if getattr(result, "isError", None) or getattr(result, "is_error", False):
        text = result.content[0].text if result.content else "unknown"
        raise RuntimeError(f"{tool} failed: {text}")
    sc = result.structuredContent
    if sc is not None:
        return sc["result"] if set(sc.keys()) == {"result"} else sc
    return json.loads(result.content[0].text)


async def with_session(
    db: Path, body: Callable[[ClientSession], Awaitable[Any]]
) -> Any:
    server = StdioServerParameters(
        command="uv",
        args=["run", "--directory", str(FORGESWARM_DIR), "forgeswarm"],
        env={**os.environ, "FORGESWARM_DB": str(db)},
    )
    async with stdio_client(server) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await body(session)


async def agent_a(session: ClientSession) -> dict[str, Any]:
    await call(session, "register_agent", agent_id="agent-a", role="planner")
    project = await call(
        session,
        "create_project",
        goal=GOAL,
        constraints="shared DB smoke; Path A ForgeSwarm",
    )
    plan = await call(
        session,
        "submit_plan",
        project_id=project["id"],
        tasks=[
            {
                "title": "Shared instruction task",
                "role": "implementer",
                "priority": 1,
            }
        ],
    )
    task_id = plan["created_tasks"][0]["id"]
    return {"project_id": project["id"], "task_id": task_id}


async def agent_b(
    session: ClientSession, project_id: str, task_id: str
) -> dict[str, Any]:
    await call(session, "register_agent", agent_id="agent-b", role="implementer")
    ready = await call(session, "list_tasks", project_id=project_id, ready_only=True)
    ids = {t["id"] for t in ready}
    if task_id not in ids:
        raise RuntimeError(
            f"agent-b missing task {task_id} in ready list: {sorted(ids)}"
        )
    claimed = await call(session, "claim_task", task_id=task_id, agent_id="agent-b")
    briefing = await call(session, "get_briefing", task_id=task_id)
    project = (
        briefing.get("project") if isinstance(briefing.get("project"), dict) else {}
    )
    goal = project.get("goal") or briefing.get("goal")
    if goal != GOAL:
        raise RuntimeError(
            f"agent-b briefing goal mismatch: {goal!r} / keys={list(briefing)}"
        )
    return {"claimed": claimed, "briefing_goal": goal, "ready_count": len(ready)}


async def main() -> int:
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(message)s")
    if not (FORGESWARM_DIR / "pyproject.toml").is_file():
        logger.error("FAIL: ForgeSwarm missing at %s", FORGESWARM_DIR)
        return 1

    db = Path(tempfile.mkdtemp(prefix="swarm-share-")) / "share.db"
    logger.info("DB: %s", db)
    logger.info("ForgeSwarm: %s", FORGESWARM_DIR)

    try:
        created = await with_session(db, agent_a)
        logger.info(
            "agent-a created project=%s task=%s",
            created["project_id"],
            created["task_id"],
        )
        seen = await with_session(
            db,
            lambda s: agent_b(s, created["project_id"], created["task_id"]),
        )
    except (RuntimeError, OSError, json.JSONDecodeError, KeyError, TypeError) as exc:
        logger.error("FAIL: %s", exc)
        return 1

    logger.info(
        "PASS: agent-b saw shared task, claimed it, briefing goal=%s",
        seen["briefing_goal"],
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))

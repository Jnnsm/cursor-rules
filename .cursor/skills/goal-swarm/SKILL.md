---
name: goal-swarm
description: >-
  Four-role architecture swarm (Coder, UI/UX, Tester, PM) coordinated via
  ForgeSwarm MCP (shared board, atomic claims, plan→implement→review,
  discussions→decisions) with a hard verification gate before marking a goal
  complete. Use when delivering non-trivial features, multi-file work, UI
  changes, or any "get this done" goal; when agents might claim done without
  proof; or when the user mentions swarm, role agreement, or working-program
  guarantee.
---

# Goal swarm

Guarantee a working program by having four roles agree on one ForgeSwarm board,
then proving it with evidence.

**Coordination bus:** MCP server `goal-swarm` (ForgeSwarm, stdio + shared
SQLite at `.swarm/forgeswarm.db`). Requires `~/src/forgeswarm` installed from
source with `mcp>=1.10.0,<2`. Config via project `.cursor/mcp.json` **and/or**
global `~/.cursor/mcp.json` (merge; never wipe other servers; backup first).
Must include `"type": "stdio"` (see `.cursor/mcp.json.example` /
`.cursor/mcp.json.absolute.example`). Global installs often appear as namespace
`user-goal-swarm`. Shared-board smoke: `scripts/swarm_share_smoke.py`. Install
verifier: `checks/mcp_goal_swarm.py` (via `uv run prove`).

### Enable MCP in Cursor (required once / after config changes)

1. Confirm clone: `~/src/forgeswarm` exists (`pyproject.toml` present).
2. Confirm config: project `.cursor/mcp.json` and/or global `~/.cursor/mcp.json`
   has `mcpServers.goal-swarm` with `"type": "stdio"` and a working
   `uv … forgeswarm` launch (absolute paths safest).
3. In Cursor: **Customize** (sidebar) → MCP / Servers → find **goal-swarm** →
   enable/toggle on if disabled.
4. **Reload MCP / Restart Cursor**: Command Palette → “Developer: Reload Window”
   (or fully quit and reopen). Project MCP is not picked up mid-session; global
   may hot-load.
5. Verify: `GetDynamicTools` for `goal-swarm` or `user-goal-swarm` lists
   ForgeSwarm tools. If still missing, check Output → **MCP Logs**, then run
   `uv run --directory ~/src/forgeswarm python /path/to/cursor-rules/scripts/swarm_share_smoke.py`
   to prove the server itself works outside Cursor.

## Roles

| Role | Owns | ForgeSwarm mapping | Must not |
|------|------|--------------------|----------|
| **PM** | Goal clarity, scope, acceptance, final sign-off | `planner` — `create_project`, `submit_plan`, `record_decision`, `resolve_discussion` | Implement or mark done without Tester evidence / approved reviews |
| **Coder** | Minimal correct implementation (ponytail), `AGENT_CHANGES.md` | `implementer` — `claim_task`, `get_briefing`, `save_context`, `submit_for_review` | Declare done; skip checks Tester requires; self-review |
| **UI/UX** | User-facing clarity, layout/flow, a11y of surfaces touched | Extra `implementer` (or UI-tagged tasks); **N/A** when no UI | Invent UI when there is none; block on taste alone |
| **Tester** | Runnable verification + peer review | `reviewer` — `get_review_queue`, `run_checks`, `post_review` | Accept "it should work"; rubber-stamp without running checks |

Keep Cursor Task/subagents as the four workers. They share state through the
MCP board (same `FORGESWARM_DB`), not through chat alone.

## MCP spawn protocol

Namespace: `goal-swarm` or `user-goal-swarm` (ForgeSwarm tools). One **project_id** per goal. Stable
`agent_id`s (e.g. `pm-1`, `coder-1`, `uiux-1`, `tester-1`) — self-review is
rejected by agent id.

1. **PM registers + boards the goal**
   - `register_agent(agent_id, role="planner")`
   - `create_project(goal, constraints)` — constraints = stack, ponytail, prove gate, out-of-scope cuts
   - Optional: `get_workflow_template` (`ship-feature` / `refactor-module` / `debug-issue`) then adapt
   - `submit_plan(project_id, tasks)` — 3–8 tasks with `role` (`planner`/`implementer`/`reviewer`/`any`), `priority`, `depends_on` (0-based indexes into this plan)
   - `record_decision` for architectural choices the plan assumes
2. **Spawn workers** — Cursor Task agents for Coder / UI-UX (if UI) / Tester. Each:
   - `register_agent` once with their stable id + role
   - `list_tasks(project_id, ready_only=true)` → `claim_task` (atomic lease) → **`get_briefing(task_id)`** and treat goal, constraints, decisions, dependency summaries, and prior review feedback as binding
3. **Disagree → discuss** — contested choice: `open_discussion` → each side `post_to_discussion` (≥2 distinct agents required) → PM `resolve_discussion` (auto-records a binding decision into every future briefing). Do not settle conflicts only in chat.
4. **Coder / UI-UX implement** — only claimed work; `update_task` / `save_context` as needed; no drive-by extras. Substantive work: `submit_for_review(content, self_assessment)`. Trivial mechanical only: `complete_task`.
5. **Tester verifies**
   - `get_review_queue(project_id)`
   - `run_checks(task_id, command="uv run prove", cwd=<workspace root>)` (allowlist includes `uv`; no prove wrapper)
   - Also run project tests / file read-back when acceptance needs them
   - `post_review(submission_id, verdict="approve"|"request_changes", comments=…)` — never review your own submission; `request_changes` returns the task to the author with briefing feedback
6. **PM signs off** — only when `get_task_graph` / board is green, reviews approved, and Tester evidence is exit 0. Optionally `get_retrospective` for bounce/check stats.

**Solo mode:** one agent, multiple role registrations and the same tool order — gates stay real (no self-review: use distinct agent_ids per role).

### Fallback if MCP unavailable

If `goal-swarm` tools are missing (server not loaded, clone missing, Cursor not
reloaded): **say so**, simulate the four roles in order, and still enforce the
evidence gate below. Do **not** pretend MCP state exists. Prefer fixing MCP
(`~/src/forgeswarm` + reload) over long-term fallback.

## Agreement record (required before "done")

Fill from **MCP facts** (project id, task ids, discussion/decision ids, check
exit codes). Leave blanks as fail:

```markdown
## Goal agreement
- Goal: …
- MCP project_id: … | FALLBACK (no MCP)
- Acceptance: …
- Plan (chosen): … (cite submit_plan / decision ids)
- Dissent resolved: … (discussion_id → resolution) | none
- Coder: AGREE | BLOCK — …
- UI/UX: AGREE | N/A | BLOCK — …
- Tester: AGREE | BLOCK — evidence: `run_checks` / `uv run prove` (exit 0) — check_id/output …
- PM: SIGN-OFF | HOLD — …
- Proof this session: `uv run prove` / other command output pasted
```

Any **BLOCK**, missing proof, or unapproved review queue → not complete.

## Verification evidence (Tester)

Prefer, in order:

1. ForgeSwarm `run_checks` with `uv run prove` → `passed=true` / exit 0; paste or cite recorded output.
2. Project tests / the command that proves acceptance criteria (via `run_checks` when allowlisted).
3. File evidence: read delivered paths and confirm required content exists.

Never: "tests would pass", "looks good", or unrun commands.

## Skip swarm (still keep the gate)

Trivia and explicit "skip swarm" still need **evidence before complete** when
code or config changed: run prove/tests or show file proof. Q&A with no repo
change needs no prove.

# cursor-rules

Rails-style Python project template. Copy this repo; put your product in `app/` (or rename the package). This template does not ship a predefined layer layout — you own the package structure. The repository is the constraint: agent rules, import boundaries you add, and `uv run prove`. Cursor rules for reuse live in `.cursor/rules/`.

## Prove

```bash
uv sync
uv run pre-commit install
uv run prove
```

A zero exit from `uv run prove` is the proof: import boundaries, discovered checks, format, lint, types, tests. The commit hook runs the same command.

## Add a lesson

One step:

- the tool already knows it: one entry in `pyproject.toml` (`[tool.ruff.lint]` or `[tool.importlinter]`)
- otherwise: `checks/<lesson>.py` with `def check() -> list[str]` (copy `checks/comments.py`)

Record the lesson there. Leave `AGENTS.md` unchanged.

## Layout

- `app/` — empty product package (`__init__.py` only); add your modules and packages as you build
- `checks/` — auto-discovered lessons; `_run.py` is the prove runner

When architecture boundaries matter, add an import-linter contract in `pyproject.toml` (for example a layers contract once those packages exist), or a `checks/` lesson.

## Rules

| File | Scope | Summary |
|------|-------|---------|
| `ponytail.mdc` | Always apply | Lazy senior dev mode — YAGNI, minimal diffs, reuse before writing |
| `coding-agent.mdc` | Always apply | Agent workflow — change tracking, logging, Python tooling, task completion |
| `trust-pyramid.mdc` | Always apply | Copy the repo, add a check, run `uv run prove` |

```bash
ln -s /path/to/cursor-rules/.cursor/rules/*.mdc ~/.cursor/rules/
```

Cursor loads `.mdc` files from `.cursor/rules/` and from `~/.cursor/rules/`.

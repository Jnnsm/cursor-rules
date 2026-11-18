# Agent

Copy `checks/` (lesson checks + prove runner) and put product code in your own package (this template ships an empty `app/` package name only — no predefined layers). You own the layout.

A mistake that should never recur becomes a check, not a paragraph:

1. One entry in `pyproject.toml` under `[tool.ruff.lint]` or `[tool.importlinter]`, when that tool already has the rule (add import-linter contracts when your packages exist).
2. Otherwise `checks/<lesson>.py` with `def check() -> list[str]` (empty list passes). Copy `checks/comments.py`. It is auto-discovered.

Leave this file and `.cursor/rules/` unchanged when you add a lesson.

Done means `uv run prove` exited 0 in this session. Paste the output.

Human review is last. It only covers what that command cannot see:

- the change was needed
- behavior the tests do not cover
- trust boundaries and secrets
- a `ponytail:` ceiling is still acceptable

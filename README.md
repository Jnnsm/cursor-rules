# cursor-rules

Personal collection of [Cursor](https://cursor.com) rules (`.mdc` files) for reuse across projects.

## Usage

Copy or symlink rules into one of:

- **Global (all projects):** `~/.cursor/rules/`
- **Per-project:** `<project>/.cursor/rules/`

```bash
# Symlink globally (edit path to this repo)
ln -s /path/to/cursor-rules/*.mdc ~/.cursor/rules/

# Or copy into a project
cp ponytail.mdc coding-agent.mdc /path/to/project/.cursor/rules/
```

Cursor loads `.mdc` files automatically from those directories.

## Included rules

| File | Scope | Summary |
|------|-------|---------|
| `ponytail.mdc` | Always apply | Lazy senior dev mode — YAGNI, minimal diffs, reuse before writing |
| `coding-agent.mdc` | Always apply | Agent workflow — change tracking, logging, Python tooling, task completion |

import os
import re
import tokenize
from pathlib import Path

# ponytail: skips dot directories, so a file under .hidden is not scanned; scan those too if a check must see them
_SKIP = {"__pycache__", "build", "dist"}
_ALLOWED = re.compile(
    r"#[ \t]*(?:"
    r"noqa:[ \t]*[A-Z]+[0-9]+(?:[ \t]*,[ \t]*[A-Z]+[0-9]+)*"
    r"|type:[ \t]*ignore\[[^\]\s]+(?:[ \t]*,[ \t]*[^\]\s]+)*\]"
    r"|ponytail:[ \t]*\S(?:.*\S)?"
    r")[ \t]*"
)


def check() -> list[str]:
    return scan(Path(__file__).resolve().parents[1])


def scan(root: Path) -> list[str]:
    violations: list[str] = []
    for path in sorted(_python_files(root)):
        violations.extend(_file(root, path))
    return violations


def _python_files(root: Path) -> list[Path]:
    files: list[Path] = []
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [
            name
            for name in dirnames
            if not name.startswith(".")
            and name not in _SKIP
            and not name.endswith(".egg-info")
        ]
        files.extend(Path(dirpath) / name for name in filenames if name.endswith(".py"))
    return files


def _file(root: Path, path: Path) -> list[str]:
    try:
        with path.open("rb") as handle:
            tokens = list(tokenize.tokenize(handle.readline))
    except (tokenize.TokenError, SyntaxError, UnicodeError, OSError) as exc:
        return [f"{path.relative_to(root)}: {exc}"]
    found: list[str] = []
    for token in tokens:
        if token.type != tokenize.COMMENT or _ALLOWED.fullmatch(token.string):
            continue
        found.append(
            f"{path.relative_to(root)}:{token.start[0]}: {token.string} "
            "(allowed: noqa:<CODE>, type: ignore[<code>], ponytail: <ceiling, upgrade>)"
        )
    return found

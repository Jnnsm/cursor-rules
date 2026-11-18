import importlib
import logging
import os
import pkgutil
import subprocess
import sys
from collections.abc import Callable
from pathlib import Path

# ponytail: stops at the first red layer; collect every layer if one run must report them all
ROOT = Path(__file__).resolve().parents[1]

logger = logging.getLogger("prove")


def main() -> None:
    os.chdir(ROOT)
    logging.basicConfig(level=logging.INFO, stream=sys.stdout, format="%(message)s")
    _step("imports", ["lint-imports"])
    _checks()
    _step("format", ["ruff", "format", "--check", "."])
    _step("lint", ["ruff", "check", "."])
    _step("types", ["mypy"])
    _step("tests", ["pytest"])


def discover() -> list[tuple[str, Callable[[], list[str]]]]:
    import checks

    found: list[tuple[str, Callable[[], list[str]]]] = []
    modules = sorted(pkgutil.iter_modules(checks.__path__), key=lambda item: item.name)
    for info in modules:
        if info.name.startswith("_"):
            continue
        module = importlib.import_module(f"checks.{info.name}")
        check = getattr(module, "check", None)
        if not callable(check):
            raise SystemExit(f"checks/{info.name}.py has no check()")
        found.append((info.name, check))
    return found


def _checks() -> None:
    logger.info("== checks ==")
    for name, check in discover():
        result = check()
        if not isinstance(result, list) or not all(
            isinstance(item, str) for item in result
        ):
            logger.info("checks/%s.py check() must return list[str]", name)
            raise SystemExit(1)
        if result:
            logger.info("\n".join(result))
            raise SystemExit(1)
        logger.info("checks/%s.py ok", name)


def _step(label: str, argv: list[str]) -> None:
    command = [str(Path(sys.executable).parent / argv[0]), *argv[1:]]
    logger.info("== %s ==", label)
    logger.info("+ %s", " ".join(command))
    completed = subprocess.run(command, cwd=ROOT, check=False)
    if completed.returncode != 0:
        raise SystemExit(completed.returncode)

from pathlib import Path

import pytest

from checks._run import discover
from checks.comments import scan

_ALLOWED = [
    "x = 1\n",
    '"""note"""\nx = 1\n',
    'x = "hash # inside"\n',
    "x = 1  # noqa: F401\n",
    "x = 1  # noqa: E722, BLE001\n",
    "x = 1  # type: ignore[assignment]\n",
    "x = 1  # type: ignore[arg-type, assignment]\n",
    "# ponytail: O(n^2) scan, index past 10k rows\n",
]

_REJECTED = [
    "x = 1  # increment x\n",
    "x = 1  # noqa\n",
    "x = 1  # noqa:\n",
    "x = 1  # type: ignore\n",
    "x = 1  # type: ignore[]\n",
    "x = 1  # noqa: F401 explained in words\n",
    "x = 1  # type: ignore[assignment] because reasons\n",
    "# ponytail:\n",
    "# TODO: later\n",
]


@pytest.mark.parametrize("source", _ALLOWED)
def test_allowed_comments(tmp_path: Path, source: str) -> None:
    (tmp_path / "mod.py").write_text(source)
    assert scan(tmp_path) == []


@pytest.mark.parametrize("source", _REJECTED)
def test_narration_and_bare_directives_fail(tmp_path: Path, source: str) -> None:
    (tmp_path / "mod.py").write_text(source)
    assert scan(tmp_path)


def test_nested_file_is_scanned(tmp_path: Path) -> None:
    nested = tmp_path / "pkg"
    nested.mkdir()
    (nested / "mod.py").write_text("x = 1  # narrate\n")
    assert scan(tmp_path)


def test_unparseable_file_is_a_violation(tmp_path: Path) -> None:
    (tmp_path / "mod.py").write_text("x = 'oops\n")
    assert scan(tmp_path)


def test_comment_check_is_discovered() -> None:
    assert "comments" in {name for name, _ in discover()}

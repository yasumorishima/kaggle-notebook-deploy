"""__version__ and pyproject.toml must not drift apart."""

import re
from pathlib import Path

from kaggle_notebook_deploy import __version__

PYPROJECT = Path(__file__).resolve().parent.parent / "pyproject.toml"


def _declared_version() -> str:
    for line in PYPROJECT.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^version = "([^"]+)"', line)
        if m:
            return m.group(1)
    raise AssertionError(f"no version line in {PYPROJECT}")


def test_version_matches_pyproject():
    """The version lives in two files; nothing compared them until now.

    They had drifted -- pyproject said 0.1.4 while __version__ (what
    `kaggle-notebook-deploy --version` prints, and what the published
    0.1.4 wheel therefore reported) still said 0.1.3. test_version passed
    only because it asserted the same stale literal.

    Compared against the file rather than importlib.metadata on purpose:
    metadata is fixed at install time, so a stale editable install would
    fail this for a reason that has nothing to do with the repo.
    """
    assert __version__ == _declared_version()

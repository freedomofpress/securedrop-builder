"""
Shared functions between various scripts
"""
import re
from pathlib import Path

RE_NAME = re.compile(r'name="(.*?)"')


def project_name(path: Path) -> str:
    """Extract the project name from setup.py"""
    setup_py = path / "setup.py"
    if not setup_py.exists():
        raise RuntimeError(f"No setup.py in {path}."
                           "If this isn't a Python project, use --project?")
    search = RE_NAME.search(setup_py.read_text())
    if not search:
        raise RuntimeError(f"Unable to parse name out of {setup_py}. "
                           "If this isn't a Python project, use --project?")
    return search.group(1)

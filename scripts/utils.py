"""
Shared functions between various scripts
"""
import re
try:
    import tomllib
except ImportError:
    # pre-Python 3.11 compatibility
    import toml as tomllib
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


def parse_poetry_lock(path: Path) -> list[(str, str)]:
    data = tomllib.load(path.open("rb"))
    ret = []
    for package in data['package']:
        # TODO: this will need to be fixed for Poetry 1.5
        if package['category'] != "main":
            continue
        ret.append((package['name'], package['version']))

    return ret


def parse_requirements_txt(path: Path) -> list[(str, str)]:
    ret = []
    for line in path.read_text().splitlines():
        if line.startswith('#'):
            continue
        if "==" not in line:
            continue
        name, constraint = line.split("==", 1)
        version = constraint.rstrip("\\").strip()
        ret.append((name, version))
    return ret

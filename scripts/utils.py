"""
Shared functions between various scripts
"""

import re

try:
    import tomllib
except ModuleNotFoundError:
    # pre-Python 3.11 compatibility
    try:
        import toml as tomllib
    except ModuleNotFoundError:
        print("WARNING: Could not find tomllib or toml, Poetry support unavailable.")

from pathlib import Path

RE_NAME = re.compile(r'name="(.*?)"')


def get_project_name(path: Path) -> str:
    """Extract the project name from setup.py"""
    setup_py = path / "setup.py"
    if not setup_py.exists():
        raise RuntimeError(
            f"No setup.py in {path}." "If this isn't a Python project, use --project?"
        )
    search = RE_NAME.search(setup_py.read_text())
    if not search:
        raise RuntimeError(
            f"Unable to parse name out of {setup_py}. "
            "If this isn't a Python project, use --project?"
        )
    return search.group(1)


def get_requirements_names_and_versions(path: Path) -> list[(str, str)]:
    """
    Return a list of package names and versions for all dependencies declared in a
    requirements.txt file.
    """
    ret = []
    for line in path.read_text().splitlines():
        if line.startswith("#"):
            continue
        if "==" not in line:
            continue
        name, constraint = line.split("==", 1)
        version = constraint.rstrip("\\").strip()
        ret.append((name, version))
    return ret


def get_poetry_names_and_versions(
    path_to_poetry_lock: Path, path_to_pyproject_toml
) -> list[(str, str)]:
    """
    Return a list of package names and versions for all main (non-development) dependencies,
    including transitive ones, defined via Poetry configuration files.
    """
    data = tomllib.loads(path_to_poetry_lock.read_text())
    relevant_dependencies = get_relevant_poetry_dependencies(
        path_to_pyproject_toml, path_to_poetry_lock
    )
    ret = []
    for package in data["package"]:
        if normalize(package["name"]) not in relevant_dependencies:
            continue
        ret.append((package["name"], package["version"]))

    return ret


def get_relevant_poetry_dependencies(
    path_to_pyproject_toml: Path, path_to_poetry_lock: Path
) -> list[str]:
    """
    Identify main (non-development) requirements. poetry.lock does not preserve
    the distinction between different dependency groups, so we have to parse
    both files.
    """
    pyproject_dict = tomllib.loads(path_to_pyproject_toml.read_text())

    # Create a set to keep track of main and transitive dependencies (set ensures
    # no duplicates)
    relevant_dependencies = set(
        normalize(name) for name in pyproject_dict["tool"]["poetry"]["dependencies"]
    )

    # Remove 'python' as it's not a package dependency
    if "python" in relevant_dependencies:
        relevant_dependencies.remove("python")

    parsed_toml = tomllib.loads(path_to_poetry_lock.read_text())

    # Identify transitive dependencies (may be enumerated in lockfile
    # before the dependency which declares them)
    for package in parsed_toml.get("package", []):
        package_name = normalize(package["name"])
        if package_name in relevant_dependencies:
            for sub_dependency in package.get("dependencies", {}):
                relevant_dependencies.add(normalize(sub_dependency))

    return list(relevant_dependencies)


def get_poetry_hashes(
    path_to_poetry_lock: Path, path_to_pyproject_toml: Path
) -> dict[str, list[str]]:
    """
    Get a dictionary for all main (non-development) dependencies and their
    valid hashes as defined in a set of requirements as defined in
    pyproject.toml/poetry.lock. This includes transitive dependencies of
    main dependencies.
    """
    dependencies = {}
    relevant_dependencies = get_relevant_poetry_dependencies(
        path_to_pyproject_toml, path_to_poetry_lock
    )
    parsed_toml = tomllib.loads(path_to_poetry_lock.read_text())

    for package in parsed_toml.get("package", []):
        package_name = normalize(package["name"])
        if package_name in relevant_dependencies:
            package_name_and_version = f"{package_name}=={package['version']}"
            dependencies[package_name_and_version] = [
                file_dict["hash"].replace("sha256:", "") for file_dict in package["files"]
            ]

    return dependencies


def get_requirements_hashes(path_to_requirements_file: Path) -> dict[str, list[str]]:
    """
    Return a dictionary of valid hashes for each dependency declared in a requirements
    file.
    """
    lines = path_to_requirements_file.read_text().splitlines()

    result_dict = {}
    current_package = None

    for line in lines:
        if line.startswith("#") or not line.strip():
            continue

        package_match = re.match(r"(\S+==\S+)", line)
        hash_match = re.search(r"--hash=sha256:([\da-f]+)", line)

        if package_match:
            current_package = package_match.group(1)
            result_dict[current_package] = []
        elif hash_match and current_package:
            result_dict[current_package].append(hash_match.group(1))

    for package, hashes in result_dict.items():
        if not hashes:
            raise ValueError(f"The package {package} does not have any hashes.")

    return result_dict


def get_requirements_from_poetry(path_to_poetry_lock: Path, path_to_pyproject_toml: Path) -> str:
    """
    Returns a multiline string in requirements.txt format for a set of Poetry main dependencies.
    """
    # Get the hashes along with the package names and versions
    hashes_dict = get_poetry_hashes(path_to_poetry_lock, path_to_pyproject_toml)

    # Form the requirements.txt string
    requirements = []
    for package_name_and_version, hashes in hashes_dict.items():
        hash_strings = [f"--hash=sha256:{h}" for h in hashes]
        requirement_line = f"{package_name_and_version} {' '.join(hash_strings)}"
        requirements.append(requirement_line)

    return "\n".join(requirements)


def normalize(dependency_name: str) -> str:
    """
    For consistent comparisons between pyproject.toml and lockfile,
    normalize names consistent with PEP503.  This implementation is drawn directly from
    <https://peps.python.org/pep-0503/#normalized-names>.
    """
    return re.sub(r"[-_.]+", "-", dependency_name).lower()

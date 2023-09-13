"""
Shared functions between various scripts
"""
import re
import sys

try:
    import tomllib
except ImportError:
    # pre-Python 3.11 compatibility
    import toml as tomllib
from pathlib import Path

RE_NAME = re.compile(r'name="(.*?)"')


def get_project_name(path: Path) -> str:
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

def get_requirements_names_and_versions(path: Path) -> list[(str, str)]:
    """
    Return a list of package names and versions for all dependencies declared in a
    requirements.txt file.
    """
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

def get_poetry_names_and_versions(path_to_poetry_lock: Path, path_to_pyproject_toml) -> list[(str, str)]:
    """
    Return a list of package names and versions for all main (non-development) dependencies,
    including transitive ones, defined via Poetry configuration files.
    """
    data = tomllib.loads(path_to_poetry_lock.read_text())
    relevant_dependencies = get_relevant_poetry_dependencies(path_to_pyproject_toml, path_to_poetry_lock)
    ret = []
    for package in data['package']:
        if package['name'] not in relevant_dependencies:
            continue
        ret.append((package['name'], package['version']))

    return ret

def get_relevant_poetry_dependencies(path_to_pyproject_toml: Path, path_to_poetry_lock: Path) -> list[str]:
    """
    Identify main (non-development) requirements. poetry.lock does not preserve
    the distinction between different dependency groups, so we have to parse
    both files.
    """
    pyproject_dict = tomllib.loads(path_to_pyproject_toml.read_text())

    # Extract main dependencies
    main_dependencies = list(pyproject_dict["tool"]["poetry"]["dependencies"].keys())

    # Remove 'python' as it's not a package dependency
    if "python" in main_dependencies:
        main_dependencies.remove("python")

    parsed_toml = tomllib.loads(path_to_poetry_lock.read_text())

    # Create a set to keep track of main and transitive dependencies (set ensures
    # no duplicates)
    relevant_dependencies = set(main_dependencies)

    # Identify transitive dependencies (may be enumerated in lockfile
    # before the dependency which declares them)
    for package in parsed_toml.get("package", []):
        package_name = package["name"]
        if package_name in main_dependencies:
            for sub_dependency in package.get("dependencies", {}).keys():
                relevant_dependencies.add(sub_dependency)

    return list(relevant_dependencies)

def get_poetry_hashes(path_to_poetry_lock: Path, path_to_pyproject_toml: Path) -> dict[str, list[str]]:
    """
    Get a dictionary for all main (non-development) dependencies and their
    valid hashes as defined in a set of requirements as defined in
    pyproject.toml/poetry.lock. This includes transitive dependencies of
    main depenencies.
    """
    dependencies = {}
    relevant_dependencies = get_relevant_poetry_dependencies(path_to_pyproject_toml, path_to_poetry_lock)
    parsed_toml = tomllib.loads(path_to_poetry_lock.read_text())

    for package in parsed_toml.get("package", []):
        package_name = package["name"]
        if package_name in relevant_dependencies:
            package_name_and_version = f"{package_name}=={package['version']}"
            dependencies[package_name_and_version] = [
                file_dict["hash"].replace("sha256:", "")
                for file_dict in package["files"]
            ]

    return dependencies

def get_requirements_hashes(path_to_requirements_file: Path) -> dict[str, list[str]]:
    """
    Return a dictionary of valid hashes for each dependency declared in a requirements
    file.
    """
    lines = path_to_requirements_file.read_text().splitlines()
    uncommented_lines = [line for line in lines if not line.lstrip().startswith("#")]

    # requirements.txt uses a multiline format, where \ is used as a newline marker.
    # Unwrap each dependency into a single line, then turn the result into a list
    # again.
    dependencies_with_hashes = (
        "".join(uncommented_lines).replace("\\\n", "").splitlines()
    )

    # Create a dictionary in the format
    # {'foo==2.4.0': ['sha256sum', 'sha256sum']}
    dependencies = {}
    for dependency_line in dependencies_with_hashes:
        if not dependency_line:
            continue
        try:
            assert len(dependency_line.split()) >= 2
        except AssertionError:
            print(
                "requirements.txt is not in expected format. Does it include hashes for all requirements?"
            )
            sys.exit(1)

        package_name_and_version, *hashes = dependency_line.split()
        hashes = [hash.replace("--hash=sha256:", "") for hash in hashes]
        dependencies[package_name_and_version] = hashes
    return dependencies


import os
import pytest
import sys
from pathlib import Path

# Adjusting the path to import utils module
path_to_script = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "../scripts/utils.py"
)
sys.path.append(os.path.dirname(path_to_script))

from utils import (
    get_requirements_names_and_versions,
    get_poetry_names_and_versions,
    get_relevant_poetry_dependencies,
    get_poetry_hashes,
    get_requirements_hashes,
    get_requirements_from_poetry,
)

# These tests generally verify that our utility functions correctly parse the
# fixtures below. The Poetry fixture includes a development-only requirement
# (pytest) which should not be returned.
PYPROJECT_TOML_PATH = Path(__file__).parent / "fixtures/pyproject.toml"
POETRY_LOCK_PATH = Path(__file__).parent / "fixtures/poetry.lock"
REQUIREMENTS_TXT_PATH = Path(__file__).parent / "fixtures/requirements.txt"
EXPECTED_DEPENDENCIES = [
    ("beautifulsoup4", "4.12.2"),
    ("colorama", "0.4.6"),
    ("cowsay", "6.0"),
    ("soupsieve", "2.5"),
]
EXPECTED_KEYS = [f"{name}=={version}" for name, version in EXPECTED_DEPENDENCIES]


def test_get_requirements_names_and_versions():
    assert (
        get_requirements_names_and_versions(REQUIREMENTS_TXT_PATH)
        == EXPECTED_DEPENDENCIES
    )


def test_get_poetry_names_and_versions():
    output = get_poetry_names_and_versions(POETRY_LOCK_PATH, PYPROJECT_TOML_PATH)
    assert output == EXPECTED_DEPENDENCIES


def test_get_relevant_poetry_dependencies():
    expected_output = ["colorama", "cowsay", "beautifulsoup4", "soupsieve"]
    output = get_relevant_poetry_dependencies(PYPROJECT_TOML_PATH, POETRY_LOCK_PATH)
    # Ensure we correctly ignore development-only dependencies
    assert "pytest" not in output
    assert sorted(output) == sorted(expected_output)


def test_get_poetry_hashes():
    output = get_poetry_hashes(POETRY_LOCK_PATH, PYPROJECT_TOML_PATH)
    assert list(output.keys()) == EXPECTED_KEYS
    assert all(len(output[dep]) > 0 for dep in output.keys())
    assert all(all(len(hash) == 64 for hash in output[dep]) for dep in output.keys())


def test_get_requirements_hashes():
    output = get_requirements_hashes(REQUIREMENTS_TXT_PATH)
    assert list(output.keys()) == EXPECTED_KEYS
    assert all(len(output[dep]) > 0 for dep in output.keys())
    assert all(all(len(hash) == 64 for hash in output[dep]) for dep in output.keys())


def test_get_requirements_from_poetry():
    output = get_requirements_from_poetry(POETRY_LOCK_PATH, PYPROJECT_TOML_PATH)
    output_lines = output.strip().split("\n")
    assert len(output_lines) == len(EXPECTED_KEYS)
    for line in output_lines:
        package_name_and_version, *hashes = line.split()
        assert package_name_and_version in EXPECTED_KEYS
        assert all(hash_str.startswith("--hash=sha256:") for hash_str in hashes)


if __name__ == "__main__":
    pytest.main([__file__])

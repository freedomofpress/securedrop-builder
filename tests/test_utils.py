import os
import sys
from pathlib import Path

import pytest

# Adjusting the path to import utils module
path_to_script = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../scripts/utils.py")
sys.path.append(os.path.dirname(path_to_script))

from utils import (
    get_poetry_hashes,
    get_poetry_names_and_versions,
    get_relevant_poetry_dependencies,
    get_requirements_from_poetry,
    get_requirements_hashes,
    get_requirements_names_and_versions,
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
    ("fortune-python", "1.0.3"),
    ("soupsieve", "2.5"),
]
EXPECTED_DEPENDENCY_NAMES = [name for name, _ in EXPECTED_DEPENDENCIES]
EXPECTED_KEYS = [f"{name}=={version}" for name, version in EXPECTED_DEPENDENCIES]
# Hex-encoded SHA-256 hashes are 64 characters long
SHA256_HASH_LENGTH = 64


def test_get_requirements_names_and_versions():
    assert sorted(get_requirements_names_and_versions(REQUIREMENTS_TXT_PATH)) == sorted(
        EXPECTED_DEPENDENCIES
    )


def test_get_poetry_names_and_versions():
    output = get_poetry_names_and_versions(POETRY_LOCK_PATH, PYPROJECT_TOML_PATH)
    assert sorted(output) == sorted(EXPECTED_DEPENDENCIES)


def test_get_relevant_poetry_dependencies():
    output = get_relevant_poetry_dependencies(PYPROJECT_TOML_PATH, POETRY_LOCK_PATH)
    # Ensure we correctly ignore development-only dependencies
    assert "pytest" not in output
    assert sorted(output) == sorted(EXPECTED_DEPENDENCY_NAMES)


def _check_hashes(output):
    assert sorted(list(output)) == sorted(EXPECTED_KEYS)
    for _, hashes in output.items():
        # We should have at least one hash per dependency
        assert len(hashes) > 0
        for hash in hashes:
            assert len(hash) == SHA256_HASH_LENGTH


def test_get_poetry_hashes():
    output = get_poetry_hashes(POETRY_LOCK_PATH, PYPROJECT_TOML_PATH)
    _check_hashes(output)


def test_get_requirements_hashes():
    output = get_requirements_hashes(REQUIREMENTS_TXT_PATH)
    _check_hashes(output)


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

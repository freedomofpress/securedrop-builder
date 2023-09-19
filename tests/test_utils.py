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
)

PYPROJECT_TOML_PATH = Path(__file__).parent / "fixtures/pyproject.toml"
POETRY_LOCK_PATH = Path(__file__).parent / "fixtures/poetry.lock"
REQUIREMENTS_TXT_PATH = Path(__file__).parent / "fixtures/requirements.txt"


def test_get_requirements_names_and_versions():
    expected_output = [
        ("beautifulsoup4", "4.12.2"),
        ("colorama", "0.4.6"),
        ("cowsay", "6.0"),
        ("soupsieve", "2.5"),
    ]
    assert get_requirements_names_and_versions(REQUIREMENTS_TXT_PATH) == expected_output


def test_get_poetry_names_and_versions():
    expected_output = [
        ("beautifulsoup4", "4.12.2"),
        ("colorama", "0.4.6"),
        ("cowsay", "6.0"),
        ("soupsieve", "2.5"),
    ]
    output = get_poetry_names_and_versions(POETRY_LOCK_PATH, PYPROJECT_TOML_PATH)
    assert output == expected_output


def test_get_relevant_poetry_dependencies():
    expected_output = ["colorama", "cowsay", "beautifulsoup4", "soupsieve"]
    output = get_relevant_poetry_dependencies(PYPROJECT_TOML_PATH, POETRY_LOCK_PATH)
    assert sorted(output) == sorted(expected_output)


def test_get_poetry_hashes():
    output = get_poetry_hashes(POETRY_LOCK_PATH, PYPROJECT_TOML_PATH)
    expected_keys = [
        "beautifulsoup4==4.12.2",
        "colorama==0.4.6",
        "cowsay==6.0",
        "soupsieve==2.5",
    ]

    assert list(output.keys()) == expected_keys
    assert all(len(output[dep]) > 0 for dep in output.keys())
    assert all(all(len(hash) == 64 for hash in output[dep]) for dep in output.keys())


def test_get_requirements_hashes():
    output = get_requirements_hashes(REQUIREMENTS_TXT_PATH)
    expected_keys = [
        "beautifulsoup4==4.12.2",
        "colorama==0.4.6",
        "cowsay==6.0",
        "soupsieve==2.5",
    ]

    assert list(output.keys()) == expected_keys
    assert all(len(output[dep]) > 0 for dep in output.keys())
    assert all(all(len(hash) == 64 for hash in output[dep]) for dep in output.keys())


if __name__ == "__main__":
    pytest.main([__file__])

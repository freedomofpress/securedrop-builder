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
)

PYPROJECT_TOML_PATH = Path(__file__).parent / "fixtures/pyproject.toml"
POETRY_LOCK_PATH = Path(__file__).parent / "fixtures/poetry.lock"
REQUIREMENTS_TXT_PATH = Path(__file__).parent / "fixtures/requirements.txt"


def test_get_requirements_names_and_versions():
    expected_output = [("colorama", "0.4.6"), ("cowsay", "6.0")]
    print(get_requirements_names_and_versions(REQUIREMENTS_TXT_PATH))
    assert get_requirements_names_and_versions(REQUIREMENTS_TXT_PATH) == expected_output


def test_get_poetry_names_and_versions():
    expected_output = [("colorama", "0.4.6"), ("cowsay", "6.0")]
    output = get_poetry_names_and_versions(POETRY_LOCK_PATH, PYPROJECT_TOML_PATH)
    assert output == expected_output

def test_get_relevant_poetry_dependencies():
    # TODO: Ensure we have a transitive dependency
    expected_output = [
        "colorama",
        "cowsay",
    ]
    output = get_relevant_poetry_dependencies(PYPROJECT_TOML_PATH, POETRY_LOCK_PATH)
    assert sorted(output) == sorted(expected_output)


if __name__ == "__main__":
    pytest.main([__file__])

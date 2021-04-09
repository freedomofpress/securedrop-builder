import pytest
import subprocess
import os


PACKAGE_BUILD_TARGETS = {
    "securedrop-client": "main",
    "securedrop-log": "main",
    "securedrop-proxy": "main",
    "securedrop-export": "main",
}

# These are the package names we want to test reproducibility for
PACKAGE_NAMES = PACKAGE_BUILD_TARGETS.keys()


def get_repo_root():
    cmd = "git rev-parse --show-toplevel".split()
    top_level = subprocess.check_output(cmd).decode("utf-8").rstrip()
    return top_level

repo_root = get_repo_root()


@pytest.mark.parametrize("pkg_name", PACKAGE_NAMES)
def test_deb_builds_are_reproducible(pkg_name):
    """
    Uses 'reprotest' to confirm that the Debian package build process
    is deterministic, i.e. all .deb files are created with the same checksum
    across multiple builds.

    We're not testing many variations, only exec_path, as a simple test
    for deterministic builds with most aspects controlled.
    """

    cmd_env = os.environ.copy()
    cmd_env["PKG_GITREF"] = os.environ.get("PKG_GITREF", PACKAGE_BUILD_TARGETS[pkg_name])
    cmd_env["TERM"] = "xterm-256color"
    cmd = [
        "reprotest",
        "-c",
        f"make {pkg_name}",
        "--variations",
        "-all, -kernel, +exec_path, +build_path",
        ".",
        f"build/debbuild/packaging/{pkg_name}*.deb",
    ]
    subprocess.check_call(cmd, env=cmd_env, cwd=repo_root)

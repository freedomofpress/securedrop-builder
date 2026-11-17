import os
import shutil
import subprocess

import pytest

# These are the SDW repositories that we build wheels for.
REPOS_WITH_WHEELS = [
    "export",
    "log",
]


@pytest.mark.parametrize("name", REPOS_WITH_WHEELS)
def test_wheel_builds_match_version_control(name):
    subprocess.check_call(
        [
            "/usr/bin/git",
            "clone",
            "https://github.com/freedomofpress/securedrop-client",
            f"/tmp/monorepo-{name}",
        ]
    )
    build_cmd = (
        f"./scripts/build-sync-wheels --pkg-dir /tmp/monorepo-{name}/{name} "
        f"--project securedrop-{name} --clobber"
    ).split()
    subprocess.check_call(build_cmd)
    # Check for modified files (won't catch new, untracked files)
    subprocess.check_call("git diff --exit-code".split())
    # Check for new, untracked files. Test will fail if working copy is dirty
    # in any way, so mostly useful in CI.
    assert subprocess.check_output("git status --porcelain".split()) == b""


def test_workstation_bootstrap_wheels():
    subprocess.check_call(
        [
            "./scripts/build-sync-wheels",
            "--pkg-dir",
            "./workstation-bootstrap",
            "--project",
            "workstation-bootstrap",
        ]
    )
    # Check for modified files (won't catch new, untracked files)
    subprocess.check_call(["/usr/bin/git", "diff", "--exit-code"])
    # Check for new, untracked files.
    assert subprocess.check_output(["/usr/bin/git", "status", "--porcelain"]) == b""


# The securedrop-app-code wheels are built in the securedrop repository's
# Noble builder image, so these tests need docker or podman.
@pytest.fixture(scope="module")
def securedrop_checkout():
    path = "/tmp/securedrop"
    subprocess.check_call(
        ["/usr/bin/git", "clone", "https://github.com/freedomofpress/securedrop", path]
    )
    oci_bin = os.environ.get("OCI_BIN") or ("podman" if shutil.which("podman") else "docker")
    env = {**os.environ, "OCI_BIN": oci_bin, "OCI_RUN_ARGUMENTS": "", "OS_VERSION": "noble"}
    subprocess.check_call(["/usr/bin/bash", "./builder/image_prep.sh"], cwd=path, env=env)
    return path


@pytest.mark.parametrize("target", ["build-server-bootstrap-wheels", "build-server-wheels"])
def test_server_wheels(securedrop_checkout, target):
    subprocess.check_call(
        ["/usr/bin/make", target, f"SECUREDROP_DIR={securedrop_checkout}", "BUILD_ARGS=--clobber"]
    )
    # Check for modified files (won't catch new, untracked files)
    subprocess.check_call(["/usr/bin/git", "diff", "--exit-code"])
    # Check for new, untracked files.
    assert subprocess.check_output(["/usr/bin/git", "status", "--porcelain"]) == b""

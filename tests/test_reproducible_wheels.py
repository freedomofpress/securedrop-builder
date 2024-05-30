import subprocess

import pytest

# These are the SDW repositories that we build wheels for.
REPOS_WITH_WHEELS = [
    "client",
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

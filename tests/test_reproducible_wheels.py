import pytest
import subprocess


# These are the SDW repositories that we build wheels for.
REPOS_WITH_WHEELS = [
    "client",
    "export",
    "log",
    "proxy",
]


@pytest.mark.parametrize("name", REPOS_WITH_WHEELS)
def test_wheel_builds_match_version_control(name):
    subprocess.check_call(["git", "clone", "https://github.com/freedomofpress/securedrop-client", f"/tmp/monorepo-{name}"])
    build_cmd = f"./scripts/build-sync-wheels --pkg-dir /tmp/monorepo-{name}/{name} --project securedrop-{name}" \
                " --clobber".split()
    subprocess.check_call(build_cmd)
    # Check for modified files (won't catch new, untracked files)
    subprocess.check_call("git diff --exit-code".split())
    # Check for new, untracked files. Test will fail if working copy is dirty
    # in any way, so mostly useful in CI.
    assert subprocess.check_output("git status --porcelain".split()) == b""

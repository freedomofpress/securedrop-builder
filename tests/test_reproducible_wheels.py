import pytest
import subprocess
import os


# These are the SDW repositories that we build wheels for.
REPOS_WITH_WHEELS = [
    "securedrop-client",
    "securedrop-export",
    "securedrop-log",
    "securedrop-proxy",
]


def get_repo_root():
    cmd = "git rev-parse --show-toplevel".split()
    top_level = subprocess.check_output(cmd).decode("utf-8").rstrip()
    return top_level


@pytest.mark.skip(reason="Comparing to version control is sufficient")
@pytest.mark.parametrize("repo_name", REPOS_WITH_WHEELS)
def test_wheel_builds_are_reproducible(repo_name):
    """
    Uses 'reprotest' to confirm that the wheel build process, per repo,
    is deterministic, i.e. all .whl files are created with the same checksum
    across multiple builds.

    Explanations of the excluded reproducibility checks:

      * user_group: As tar command will fail for random user/groups
      * time: breaks HTTPS, so pip calls fail
      * locales: some locales fail, would be nice to fix, but low priority
      * kernel: x86_64 is the supported architecture, we don't ship others
    """
    repo_url = f"https://github.com/freedomofpress/{repo_name}"
    cmd_env = os.environ.copy()
    cmd_env["TERM"] = "xterm-256color"
    cmd = [
        "reprotest",
        "-c",
        f"./scripts/build-sync-wheels -p {repo_url} --clobber",
        "--variations",
        "-user_group, -time, -locales, -kernel",
        ".",
        "localwheels/*.whl",
    ]
    repo_root = get_repo_root()
    subprocess.check_call(cmd, env=cmd_env, cwd=repo_root)


@pytest.mark.parametrize("repo_name", REPOS_WITH_WHEELS)
def test_wheel_builds_match_version_control(repo_name):
    repo_url = f"https://github.com/freedomofpress/{repo_name}"
    build_cmd = f"./scripts/build-sync-wheels -p {repo_url} --clobber".split()
    subprocess.check_call(build_cmd)
    # Check for modified files (won't catch new, untracked files)
    subprocess.check_call("git diff --exit-code".split())
    # Check for new, untracked files. Test will fail if working copy is dirty
    # in any way, so mostly useful in CI.
    assert subprocess.check_output("git status --porcelain".split()) == b""

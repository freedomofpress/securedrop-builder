import pytest
import subprocess
import os


# These are the SDW repositories that we build wheels for.
REPOS_WITH_WHEELS = [
    "securedrop-client",
    "securedrop-log",
    "securedrop-proxy",
]


def get_repo_root():
    cmd = "git rev-parse --show-toplevel".split()
    top_level = subprocess.check_output(cmd).decode("utf-8").rstrip()
    return top_level


@pytest.mark.parametrize("repo_name", REPOS_WITH_WHEELS)
def test_wheel_builds_are_reproducible(repo_name):
    """
    Uses 'reprotest' to confirm that the wheel build process, per repo,
    is deterministic, i.e. all .whl files are created with the same checksum
    across multiple builds.

    Explanations of the excluded reproducibility checks:

      * time: breaks HTTPS, so pip calls fail
      * locales: some locales fail, would be nice to fix, but low priority
      * kernel: x86_64 is the supported architecure, we don't ship others
    """
    repo_url = f"https://github.com/freedomofpress/{repo_name}"
    cmd_env = os.environ.copy()
    cmd_env["TERM"] = "xterm-256color"
    cmd = [
        "reprotest",
        "-c",
        f"./scripts/build-sync-wheels -p {repo_url} --clobber",
        "--vary",
        "+all, -time, -locales, -kernel",
        ".",
        "localwheels/*.whl",
    ]
    repo_root = get_repo_root()
    subprocess.check_call(cmd, env=cmd_env, cwd=repo_root)

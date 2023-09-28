import pytest
import subprocess


# These are the repositories that we build wheels for.
REPOS_WITH_WHEELS = {
    "securedrop-client": {"os": "debian"},
    "securedrop-export": {"os": "debian"},
    "securedrop-log": {"os": "debian"},
    "securedrop-proxy": {"os": "debian"},
    "securedrop": {
        "os": "ubuntu",
        "extra_args": [
            "--requirements", "securedrop/requirements/python3",
            "--project", "securedrop-app-code",
        ]
    },
}


def is_platform(wanted: str) -> bool:
    """Is this the platform we wanted?"""
    with open("/etc/os-release") as f:
        text = f.read()
    for line in text.splitlines():
        if line.startswith("ID="):
            return line.split("=", 1)[1] == wanted
    raise RuntimeError("Unable to parse ID= out of /etc/os-release")


@pytest.mark.parametrize("repo_info", REPOS_WITH_WHEELS.items())
def test_wheel_builds_match_version_control(repo_info):
    repo_name, args = repo_info
    if not is_platform(args["os"]):
        pytest.skip(f"Skipping {repo_name} because we're not on {args['os']}")
    repo_url = f"https://github.com/freedomofpress/{repo_name}"
    build_cmd = f"./scripts/build-sync-wheels --pkg-dir {repo_url} --project {repo_name} --clobber".split()
    subprocess.check_call(build_cmd + args.get("extra_args", []))
    # Check for modified files (won't catch new, untracked files)
    subprocess.check_call("git diff --exit-code".split())
    # Check for new, untracked files. Test will fail if working copy is dirty
    # in any way, so mostly useful in CI.
    assert subprocess.check_output("git status --porcelain".split()) == b""

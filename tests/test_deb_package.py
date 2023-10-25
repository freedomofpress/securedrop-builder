import subprocess
import tempfile
from pathlib import Path

import pytest

SECUREDROP_ROOT = Path(
    subprocess.check_output(["git", "rev-parse", "--show-toplevel"]).decode().strip()
)
DEB_PATHS = list((SECUREDROP_ROOT / "build/debbuild/packaging").glob("*.deb"))

@pytest.mark.parametrize("deb", DEB_PATHS)
def test_securedrop_keyring_removes_conffiles(deb: Path):
    """
    Ensures additional conffiles are not shipped in the `securedrop-keyring`
    package. Files in `/etc/` are automatically marked as conffiles during
    packaging, so our build logic overwrites the additional files that would
    be left behind in the `/etc/apt/trusted.gpg.d/` diretory.

    When `securedrop-keyring.gpg` is shipped in `/usr/share/keyrings`, this
    test can be removed.
    """
    if not deb.name.startswith(("securedrop-keyring")):
        return

    with tempfile.TemporaryDirectory() as tmpdir:
        subprocess.check_call(["dpkg-deb", "--control", deb, tmpdir])
        conffiles_path = Path(tmpdir) / "conffiles"
        assert conffiles_path.exists()
        # No files are currently allow-listed to be conffiles
        assert conffiles_path.read_text().rstrip() == ""


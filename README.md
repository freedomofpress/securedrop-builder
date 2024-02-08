> By contributing to this project, you agree to abide by our [Code of Conduct](https://github.com/freedomofpress/.github/blob/main/CODE_OF_CONDUCT.md).

[![CircleCI](https://circleci.com/gh/freedomofpress/securedrop-builder/tree/main.svg?style=svg)](https://circleci.com/gh/freedomofpress/securedrop-builder/tree/main)

# securedrop-builder

`securedrop-builder` is the tool we use to build reproducible Python wheels for [SecureDrop Workstation components](https://github.com/freedomofpress/securedrop-client).

## Updating our bootstrapped build tools

We use the [build](https://pypa-build.readthedocs.io/en/latest/) toolchain to build our reproducible wheels.
If we have to update the tools, use the following steps

```shell
# Ensure you are running in a cleanly boostrapped virtual environment
rm -rf .venv
make install-deps
source .venv/bin/activate
# Perform the required dependency operations using Poetry.
# Use "poetry update <foo>" to update an individual dependency per pyproject.toml
# Use "poetry lock --no-update" to pick up pyproject.toml additions/removals
# Use -C to run commands in the workstation-bootstrap directory, e.g.:
poetry -C workstation-bootstrap/ lock --no-update
# Now we are ready to build updated wheels:
./scripts/build-sync-wheels --project workstation-bootstrap --pkg-dir ./workstation-bootstrap
# Once the new wheels are ready, we recreate our sha256sums:
./scripts/sync-sha256sums ./workstation-bootstrap
# Sign the list of sha256sums
gpg --armor --output workstation-bootstrap/sha256sums.txt.asc --detach-sig  workstation-bootstrap/sha256sums.txt
# We can even verify if we want
./scripts/verify-sha256sum-signature ./workstation-bootstrap/
# Update the build-requirements.txt file
./scripts/update-requirements --pkg-dir ./workstation-bootstrap/ --project workstation-bootstrap
```

Make sure that your GPG public key is stored in `pubkeys/`, so CI can verify the signatures.

## Updating Python wheels

When adding a new production dependency to a component, new wheels will need to be built
plus updates to `build-requirements.txt`. This should be done after you have updated the
dependencies in the component's `pyproject.toml` and `poetry.lock` files.

### 0. Enable the virtualenv

Create a fresh virtualenv and install the build tools from our bootstrapped wheels.

```shell
rm -rf .venv
make install-deps
```

The following steps needs to be done from the same virtual environment.

### 1. Try to update build-requirements.txt for the project

From the `securedrop-builder` directory, run the following, where `<component>`
is what you're trying to update dependencies for, e.g. "client", "proxy", etc.

```shell
PKG_DIR=/home/user/code/securedrop-client/<component> make requirements
```

This will create/update the `build-requirements.txt` file in the project directory along with the binary wheel
hashes from our own Python package index server.

If we are missing any wheels from our cache/build/server, it will let you know with a following message.

```shell
The following dependent wheel(s) are missing:
pytest==3.10.1

Please build the wheel by using the following command.
	PKG_DIR=/home/user/code/securedrop-client make build-wheels
Then add the newly built wheels and sources to the `wheels` subdirectory for the package.
After these steps, please rerun the command again.
```

The next step is to build the wheels. To do this step, you will need a maintainer
to build the wheels and sign the updated sha256sums file with your individual key.

### 2. Build wheels

This must be done in an environment for building production artifacts:

```shell
PKG_DIR=/home/user/code/securedrop-client make build-wheels
```

This above command will let you know about any new wheels + sources. It will
build/download sources from PyPI (by verifying it against the sha256sums from
the `poetry.lock` of the project).

If your package contains compiled code (e.g. C or Rust extensions), it must be
built for all Debian versions we support.

### 3. Commit changes to the wheels directory (if only any update of wheels)

Now add these built artifacts to version control, from the relevant package
directory:

```shell
git add wheels/
git commit
```

Submit a PR containing the new wheels and updated files.

### 4. Update build-requirements.txt

After building and committing the new wheels, re-run the command from step 1:

```shell
PKG_DIR=/home/user/code/securedrop-client/<component> make requirements
```

This will update the build-requirements.txt file, commit and open a PR with these
changes. Note that CI will likely fail until the PR from step 3 is merged.

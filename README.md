> By contributing to this project, you agree to abide by our [Code of Conduct](https://github.com/freedomofpress/.github/blob/main/CODE_OF_CONDUCT.md).

[![CircleCI](https://circleci.com/gh/freedomofpress/securedrop-builder/tree/main.svg?style=svg)](https://circleci.com/gh/freedomofpress/securedrop-builder/tree/main)

# securedrop-builder

`securedrop-builder` is the tool we use to package Python projects into Debian packages for the [SecureDrop Workstation](https://github.com/freedomofpress/securedrop-workstation).

* For instructions on how to build [SecureDrop](https://github.com/freedomofpress/securedrop) Debian packages, see https://developers.securedrop.org/en/latest/release_management.html.

* For building SecureDrop Workstation RPMs, see our [qubes-template-securedrop-workstation](https://github.com/freedomofpress/qubes-template-securedrop-workstation#build-instructions) and [securedrop-workstation-dom0-config](https://github.com/freedomofpress/securedrop-workstation/wiki/Building-securedrop-workstation-dom0-config-RPM-package) docs.

## Getting Started

1. Clone `securedrop-builder` and install its dependencies:

    ```shell
    git clone git@github.com:freedomofpress/securedrop-builder.git
    cd securedrop-builder
    make install-deps  # This also confifgures the git-lfs repo used to store SecureDrop Workstation dependencies (https://github.com/freedomofpress/securedrop-builder/tree/HEAD/workstation-bootstrap/wheels)
    ```

2. Build a package in one of the following ways:
    ```shell
    # From a release tag x.y.z signed by the SecureDrop Release Signing key
    PKG_VERSION=x.y.z ./scripts/update-changelog securedrop-client
    SD_PKG_GITREF=x.y.z make securedrop-client
    ```
    
    ```shell
    # From a non-release tag or branch
    PKG_VERSION=<version> ./scripts/update-changelog securedrop-client
    SD_PKG_GITREF=<ref> make securedrop-client
    ```
    
    ```shell
    # From a source tarball
    # First give the Debian package you want to build a version number by setting it in the changelog
    PKG_VERSION=<version> ./scripts/update-changelog securedrop-client
    PKG_PATH=local/path/to/securedrop-client/dist/securedrop-client-x.y.z.tar.gz make securedrop-client
    ```
    
    ```shell
    # From a local source checkout
    # First give the Debian package you want to build a version number by setting it in the changelog
    PKG_VERSION=<version> ./scripts/update-changelog securedrop-client
    PKG_PATH=local/path/to/securedrop-client make securedrop-client
    ```
    
## Which packages can `securedrop-builder` build?

* [securedrop-client](https://github.com/freedomofpress/securedrop-client)
* [securedrop-export](https://github.com/freedomofpress/securedrop-export)
* [securedrop-keyring](https://github.com/freedomofpress/securedrop-keyring)
* [securedrop-log](https://github.com/freedomofpress/securedrop-log)
* [securedrop-proxy](https://github.com/freedomofpress/securedrop-proxy)
* [securedrop-workstation-config](https://github.com/freedomofpress/securedrop-builder/tree/main/securedrop-workstation-config)
* [secruedrop-workstation-viewer](https://github.com/freedomofpress/securedrop-builder/tree/main/securedrop-workstation-viewer)


## Build and deploy a package

Refer to https://developers.securedrop.org/en/latest/workstation_release_management.html.

_If you don't need to deploy a package and just want to test locally, you can start by building it from a source checkout (see :ref:`Getting Started`) and then install it in its corresponding AppVM._

## Updating our bootstrapped build tools

We use [build](https://pypa-build.readthedocs.io/en/latest/) toolchain to build our reproducible wheels.
If we have to update the tool, use the following steps

```shell
# First create a new fresh virtualenv
rm -rf .venv && python3 -m venv .venv
source .venv/bin/activate
# Then install pip-tools, from pinned dependencies
python3 -m pip install -r workstation-bootstrap/requirements.txt
# Then update the requirements.in file as required
pip-compile --allow-unsafe --generate-hashes \
    --output-file=workstation-bootstrap/requirements.txt workstation-bootstrap/requirements.in
# Now we are ready for bootstrapping
./scripts/build-sync-wheels --project workstation-bootstrap --pkg-dir ./workstation-bootstrap --requirements .
# Here we have the new wheels ready
# Now let us recreate our new sha256sums for bootstrapping
./scripts/sync-sha256sums ./workstation-bootstrap
# now let us sign the list of sha256sums
gpg --armor --output workstation-bootstrap/sha256sums.txt.asc --detach-sig  workstation-bootstrap/sha256sums.txt
# We can even verify if we want
./scripts/verify-sha256sum-signature ./workstation-bootstrap/
# Update the build-requirements.txt file
./scripts/update-requirements --pkg-dir ./workstation-bootstrap/ --project workstation-bootstrap --requirements .
```

Make sure that your GPG public key is stored in `pubkeys/`, so CI can verify the signatures.

## Updating Python wheels

Maintainers of `securedrop-client` and `securedrop-proxy` must ensure that
the requirements files which are used for build of these packages (`build-requirements.txt`)
using `make requirements` are kept up to date in latest `main` of those repositories.

If new dependencies were added in the `build-requirements.txt` of that
repo that are not in the FPF PyPI mirror (`./localwheels/` in this repository), then the maintainer needs
to do the following (we are taking `securedrop-client` project as example):

### 0. Enable the virtualenv

You can create a fresh virtualenv and install the build tools from our bootstrapped wheels.

```shell
rm -rf .venv
make install-deps
```

Remember that the following steps needs to be done from the same virtual environment.

### 1. Create updated build-requirements.txt for the project

From the `securedrop-builder` directory,

```shell
PKG_DIR=/home/user/code/securedrop-client make requirements
```

This will create the proper `build-requirements.txt` file in the project directory along with the binary wheel
hashes from our own Python package index server.

If we are missing any wheels from our cache/build/server, it will let you know with a following message.

```shell
The following dependent wheel(s) are missing:
pytest==3.10.1

Please build the wheel by using the following command.
	PKG_DIR=/home/user/code/securedrop-client make build-wheels
Then add the newly built wheels and sources to ./localwheels/.
Also update the index HTML files accordingly commit your changes.
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
the `requirements.txt` of the project).

### 3. Commit changes to the localwheels directory (if only any update of wheels)

Now add these built artifacts to version control:

```shell
git add localwheels/
git commit
```

Finally, submit a PR containing the new wheels and updated files.
If you wish to test the new wheels in a local build before submitting a PR,
or as part of PR review, you can do so by:

Then run e.g. `SD_PKG_GITREF=0.4.1 make securedrop-client` to verify that the new wheels are working.

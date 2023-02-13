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
    # From a release tag signed by the SecureDrop Release Signing key
    PKG_VERSION=x.y.z make securedrop-client
    ```
    
    ```shell
    # From an rc tag signed by a maintainer (the rc tag must be the most recent entry in the changelog) 
    PKG_VERSION=x.y.z-rcN make securedrop-client
    ```
    
    ```shell
    # From a source tarball
    # First give the Debian package you want to build a version number by setting it in the changelog
    PKG_VERSION=x.y.z ./scripts/update-changelog securedrop-client
    PKG_PATH=local/path/to/securedrop-client/dist/securedrop-client-x.y.z.tar.gz make securedrop-client
    ```
    
    ```shell
    # From a local source checkout
    # First give the Debian package you want to build a version number by setting it in the changelog
    PKG_VERSION=x.y.z-rcN ./scripts/update-changelog securedrop-client
    PKG_DIR=local/path/to/securedrop-client make securedrop-client
    ```
    
## Which packages can `securedrop-builder` build?

* [securedrop-client](https://github.com/freedomofpress/securedrop-client)
* [securedrop-export](https://github.com/freedomofpress/securedrop-export)
* [securedrop-keyring](https://github.com/freedomofpress/securedrop-keyring)
* [securedrop-log](https://github.com/freedomofpress/securedrop-log)
* [securedrop-proxy](https://github.com/freedomofpress/securedrop-proxy)
* [securedrop-workstation-config](https://github.com/freedomofpress/securedrop-builder/tree/main/securedrop-workstation-config)
* [secruedrop-workstation-viewer](https://github.com/freedomofpress/securedrop-builder/tree/main/securedrop-workstation-viewer)


## Build and deploy a package to `apt-test`

1. Open a Terminal in `sd-dev-dvm` (see https://developers.securedrop.org/en/latest/workstation_release_management.html#how-to-create-the-dispvm-for-building-packages).
2. Clone `securedrop-builder` and install its dependencies:
    ```shell
    git clone git@github.com:freedomofpress/securedrop-builder.git
    cd securedrop-builder
    make install-deps  # This also confifgures the git-lfs repo used to store SecureDrop Workstation dependencies (https://github.com/freedomofpress/securedrop-builder/tree/HEAD/workstation-bootstrap/wheels)
    ```
3. Create a changelog entry for the new version of the package you are about to build.
    ```shell
    PKG_VERSION=x.y.z-rcN ./scripts/update-changelog securedrop-foobar
    ```
4. Build the package.
    ```shell
    PKG_VERSION=x.y.z-rcN make securedrop-foobar
    ```
5. Ouput the package hash so you can copy it into the build logs in a following step.
    ```
    sha256sum bulid/debbuild/packaging/securedrop-foobar_x.y.z-rcN.deb
    ```
6. Save and publish your terminal history to the [build-logs repository](https://github.com/freedomofpress/build-logs/).

7. Open a PR to https://github.com/freedomofpress/securedrop-dev-packages-lfs with your package. Once merged, your package will be deployed to https://apt-test.freedom.press.

## Build and deploy a package to `apt-qa`

1. Open a Terminal in `sd-dev-dvm` (see [How to create the DispVM for building packages](#how-to-create-the-dispvm-for-building-packages)).
2. Clone `securedrop-builder` and install its dependencies:
    ```shell
    git clone git@github.com:freedomofpress/securedrop-builder.git
    cd securedrop-builder
    make install-deps  # This also confifgures the git-lfs repo used to store SecureDrop Workstation dependencies (https://github.com/freedomofpress/securedrop-builder/tree/HEAD/workstation-bootstrap/wheels)
    ```
3. Build the package.
    ```shell
    # The x.y.z release tag must by signed by the SecureDrop Release Signing key
    PKG_VERSION=x.y.z make securedrop-foobar
    ```
4. Ouput the package hash so you can copy it into the build logs in a following step.
    ```shell
    sha256sum bulid/debbuild/packaging/securedrop-foobar_x.y.z.deb
    ```
5. Confirm the hash matches the x.yr.z-rcN package that was approved for release.
6. Save and publish your terminal history to the [build-logs repository](https://github.com/freedomofpress/build-logs/).
7. Add your package to a new branch called `release` in https://github.com/freedomofpress/securedrop-debian-packages-lfs. 
8. Update the apt repo distribution files by running `./tools/publish` and push those changes to the `release` branch as well. This will deploy your pakcage to https://apt-qa.freedom.press.
9. Open a PR in https://github.com/freedomofpress/securedrop-debian-packages-lfs to merge `release` into `main` and link to the new `build-logs` commit.

## Build and deploy a package to `apt-prod`

Once the `release` branch containing your package is merged into `main` in https://github.com/freedomofpress/securedrop-debian-packages-lfs, it will be deloyed to https://apt.freedom.press.

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

Then run e.g. `PKG_VERSION=0.4.1 make securedrop-client` to verify that the new wheels are working.

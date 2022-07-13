> By contributing to this project, you agree to abide by our [Code of Conduct](https://github.com/freedomofpress/.github/blob/main/CODE_OF_CONDUCT.md).

# SecureDrop Debian Packaging

[![CircleCI](https://circleci.com/gh/freedomofpress/securedrop-debian-packaging/tree/main.svg?style=svg)](https://circleci.com/gh/freedomofpress/securedrop-debian-packaging/tree/main)

This repository contains the packaging files and tooling for building Debian packages for projects for the [SecureDrop Workstation](https://github.com/freedomofpress/securedrop-workstation) based on Qubes OS. Development/staging packages are placed on `apt-test.freedom.press` for installation in Debian-based TemplateVMs, and production packages are placed on `apt.freedom.press`. Please note that the SecureDrop Workstation is currently in a limited beta phase and not yet recommended for general use.

## Packaging a Python-based SecureDrop project

The following process is used for Python-based projects for the Qubes SecureDrop Workstation, namely, `securedrop-proxy` and `securedrop-client`:

![gif explaining what is committed where](images/securedrop-pip-mirror.gif)

The following diagram shows the makefile targets/scripts in this repository, the produced artifacts and the locations where these artifacts are stored:

![Packaging Workflow](images/diagram.png)

### Packaging Dependencies

In a Debian AppVM in Qubes:

```
make install-deps
```

**Note:** either run `make install-deps` each time you start your debian packaging AppVM, or make
sure that you install them into the template for your debian packaging AppVM.

The install target will configure [git-lfs](https://git-lfs.github.com/), used for storing
binary wheel files.

## Updating our bootstrapped build tools

We use [build](https://pypa-build.readthedocs.io/en/latest/) toolchain to build our reproducible wheels.
If we have to update the tool, use the following steps

```
# First create a new fresh virtualenv
rm -rf .venv && python3 -m venv .venv
source .venv/bin/activate
# Then install pip-tools, from pinned dependencies
python3 -m pip install -r requirements.txt
# Then update the requirements.in file as required
pip-compile --allow-unsafe --generate-hashes --output-file=requirements.txt requirements.in
# Now we are ready for bootstrapping
./scripts/build-sync-wheels --cache ./bootstrap -p $PWD
# Here we have the new wheels ready
# Now let us recreate our new sha256sums for bootstrapping
BOOTSTRAP=true ./scripts/sync-sha256sums
# now let us sign the list of sha256sums
gpg --armor --output bootstrap-sha256sums.txt.asc --detach-sig  bootstrap-sha256sums.txt
# We can even verify if we want
BOOTSTRAP=true ./scripts/verify-sha256sum-signature
# Update the build-requirements.txt file
PKG_DIR=$PWD BOOTSTRAP=true ./scripts/update-requirements
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

```
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --require-hashes --no-index --no-deps --no-cache-dir -r build-requirements.txt --find-links ./bootstrap/
```

Remember that the following steps needs to be done from the same virtual environment.

### 1. Create updated build-requirements.txt for the project

From the `securedrop-debian-packaging` directory,

```
PKG_DIR=/home/user/code/securedrop-client make requirements
```

This will create the proper `build-requirements.txt` file in the project directory along with the binary wheel
hashes from our own Python package index server.

If we are missing any wheels from our cache/build/server, it will let you know with a following message.

```
The following dependent wheel(s) are missing:
pytest==3.10.1

Please build the wheel by using the following command.
	PKG_DIR=/home/user/code/securedrop-client make build-wheels
Then add the newly built wheels and sources to ./localwheels/.
Also update the index HTML files accordingly commit your changes.
After these steps, please rerun the command again.
```

The next step is to build the wheels. To do this step, you will need an owner
of the SecureDrop release key to build the wheel and sign the updated sha256sums file
with the release key. If you're not sure who to ask, ping @redshiftzero for a pointer.

### 2. Build wheels

This must be done in an environment for building production artifacts:

```shell
PKG_DIR=/home/user/code/securedrop-client make build-wheels
```

This above command will let you know about any new wheels + sources. It will
build/download sources from PyPI (by verifying it against the sha256sums from
the `requirements.txt` of the project).

Then navigate back to the project's code directory and run the following command.

```bash
python3 setup.py sdist
```

### 3. Commit changes to the localwheels directory (if only any update of wheels)

Now add these built artifacts to version control:

```
git add localwheels/
git commit
```

Finally, submit a PR containing the new wheels and updated files.
If you wish to test the new wheels in a local build before submitting a PR,
or as part of PR review, you can do so by:

Then run e.g. `PKG_VERSION=0.4.1 make securedrop-client` to verify that the new wheels are working.

## Make a release

Summarizing release manager steps, at a high level, for changes into this repository. Further detail is available in the [SecureDrop Workstation Release Management documentation](https://github.com/freedomofpress/securedrop-workstation#release-a-subproject)

1. Update versions as necessary in the project's repository, and open a pull request
2. Do a test build following steps in "Build a package" section below
3. Create a PR to this repository with updated build logic (if necessary) and updated debian changelog (using `./scripts/update-changelog`). Note around the time this PR is merged, there should be a corresponding tag in the associated package code's repository. Otherwise, nightly builds will fail
4. Push the release tag for use in building to the project's repository
5. Merge the project's repository code
6. Re-run CI in this repository, it will use the latest tag and build logic to test the build
7. Build tarballs, and create a detached signature with the release key
8. Copy your build logs into your project's corresponding directory in the `build-logs` repository, and push your changes to the `main` branch, see https://github.com/freedomofpress/build-logs/commit/fc0eb9551678c8f58ea0017f1eb291375ea5bd9e for example.
9. Commit these tarballs in the `tarballs/` directory
10. Open a PR to the `securedrop-debian-packaging` repository with a test plan to verify the checksum in the build logs and tarball signature. The reviewer can perform verification by running:

```
sha256sum <package>.tar.gz
gpg --verify <package>.tar.gz.asc <package>.tar.gz
```

11. Once the PR above is merged, create a new tag from the merge commit which will later be used to verify the integrity of the tarballs prior to building the debian packages
12. Observe nightlies the next day to ensure *all* packages are built properly

## Build a package

Next, checkout the project you intend to package and enter that directory:

```
git clone git@github.com:freedomofpress/securedrop-foobar.git
cd securedrop-foobar
```

Verify the release tag for the project:

```
git tag -v x.y.z
```

Checkout the release tag:

```
git checkout x.y.z
```

If it hasn't been added already, generate a tarball to be used in the build process:

```
python3 setup.py sdist
```

Clone this repository for access to the packaging tooling.

```
cd ..
git clone git@github.com:freedomofpress/securedrop-debian-packaging.git
cd securedrop-debian-packaging
```

If you are releasing a new version (rather than rebuilding a package from a previous version),
you must update the changelog.

Run the following script to create a new entry that you will update with the same bullets from the package's own changelog.

```
PKG_VERSION=x.y.z ./scripts/update-changelog securedrop-foobar
```

Build the package:

```
PKG_VERSION=x.y.z make securedrop-foobar
```

Output package hash so you can copy it into the build logs in the next step:

```
sha256sum /path/to/built/package.deb
```

Save and publish your build logs to the `build-logs` repository, e.g. https://github.com/freedomofpress/build-logs/commit/786eb46672b07b5c635d87a075770b53a0ce3df9

Commit the deb to a new `securedrop-debian-packages-lfs` branch (this will be added as a `git-lfs` object).

Commit all new and modified `reprepro` files created via the publish script (`sudo apt install reprepro` if not already installed):
```
./tools/publish

```

Now open a PR and link to the new `build-logs` commit. A release key holder will add a detached signature to the package in your PR. Make sure the detached signature matches new Release file by running:
```
gpg --verify repo/public/dists/buster/Release.gpg repo/public/dists/buster/Release
```

Once the PR is merged, the new packages will be picked up by a script and deployed to https://apt.freedom.press within 30 minutes.

## Build a package for development or test (skip signature verfication)

Checkout the project you intend to package and enter that directory:

```
git clone git@github.com:freedomofpress/securedrop-foobar.git
cd securedrop-foobar
```

If there is a dev or rc tag you are testing, then checkout that tag, e.g.

```
git checkout x.y.zrc1
```

Update `setup.py` with the rc or dev version number, e.g. `0.5.0dev1` or `0.5.0rc1`. In order for the debian packaging tool to work, you cannot use a `-` or `.` or `_` between the vesion number and the `dev` or `rc` portion of the string. Now you can generate a tarball to be used in the build process:

```
python3 setup.py sdist
```

Clone this repository for access to the packaging tooling.

```
cd ..
git clone git@github.com:freedomofpress/securedrop-debian-packaging.git
cd securedrop-debian-packaging
```

If you are releasing a new version (rather than rebuilding a package from a previous version),
you must update the changelog.

Run the following script to create a new entry that you will update with the same bullets from the package's own changelog.

```
./scripts/update-changelog securedrop-foobar
```

Build the package, e.g. `for x.y.zrc1`:

```
PKG_VERSION=x.y.zrc1 PKG_PATH=path/to/securedrop-foobar/dist/securedrop-foobar-x.y.z.rc1.tar.gz make securedrop-foobar
```

## Packaging non-Python based SecureDrop projects

TODO

## Intro to packaging

For an introduction to packaging Python projects into Debian packages, one can see the [SecureDrop Debian Packaging Guide](https://securedrop-debian-packaging-guide.readthedocs.io/en/latest/). Note that these guidelines on Read the Docs are for educational purposes only. The README you are currently reading is the canonical reference for SecureDrop Workstation packagers.

# SecureDrop Debian Packaging

[![CircleCI](https://circleci.com/gh/freedomofpress/securedrop-debian-packaging/tree/master.svg?style=svg)](https://circleci.com/gh/freedomofpress/securedrop-debian-packaging/tree/master)

This repository contains the packaging files and tooling for building Debian packages for projects for the alpha [SecureDrop Workstation](https://github.com/freedomofpress/securedrop-workstation) based on Qubes OS. Packages are placed on `apt-test-qubes.freedom.press` for installation in Debian-based TemplateVMs. These packages are not yet ready for use in a production environment.

## Packaging a Python-based SecureDrop project

The following process is used for Python-based projects for the Qubes SecureDrop Workstation, namely, `securedrop-proxy` and `securedrop-client`:

![gif explaining what is committed where](images/securedrop-pip-mirror.gif)

The following diagram shows the makefile targets/scripts in this repository, the produced artifacts and the locations where these artifacts are stored:

![Packaging Workflow](images/diagram.png)

### Packaging Dependencies

In a Debian AppVM in Qubes:

```
make install-deps
make fetch-wheels
```

## Updating Python wheels

Maintainers of `securedrop-client` and `securedrop-proxy` must ensure that
the requirements files which are used for build of these packages (`build-requirements.txt`)
using `make requirements` are kept up to date in latest `master` of those repositories.

If new dependencies were added in the `requirements.txt` of that
repo that are not in the FPF PyPI mirror, then the maintainer needs
to:

1. Build those wheels using `make build-wheels`
2. Push the tarball and wheel package of the new
dependency to the FPF PyPI mirror using the steps described [here](https://github.com/freedomofpress/securedrop-debian-packaging-guide/issues/6).
3. Make a PR updating the shasums and signature in this repository.
4. Once this is done, `make requirements` can be used to update `build-requirements.txt`
in the repository to be packaged.

## Make a release

Summarizing release manager steps:

1. Update versions as necessary
2. Do a test build following steps below
3. Make any changes as necessary and create a PR into the repository to be packaged with the modifications from steps 1-3
4. Push the release tag for use in building
5. For a release candidate or alpha (pre-production) release, push the tag as described in the section below to trigger the build pipeline. For a production release, you should ask the person with production access to build the package and push.

## Automated Builds

The build and deployment of packages for release candidates, alpha releases, and nightlies is done via Circle CI. 

### Nightly

Nighly builds occur at 5 UTC (10 PM Pacific time) for:

* `securedrop-proxy`
* `securedrop-client`

These packages will appear on `apt-test-qubes.freedom.press`

### Release Candidates and Alpha Releases

#### Workstation

TK

These packages will appear on `apt-test-qubes.freedom.press`.

#### Core

To trigger a build of packages corresponding to a release tag (rc or otherwise) which will be automatically deployed to `apt-test.freedom.press`, push a tag to _this_ repository containing `securedrop-core/BUILD_TAG` where `BUILD_TAG` is the tag you want the packages to be built on in the target repository.

Note that only packages with the same versions but modified checksums will not be committed.

## Build a package

Next, checkout the project you intend to package and enter that directory:

```
git clone git@github.com:freedomofpress/securedrop-foobar.git
cd securedrop-foobar
```

Checkout the release tag for the project:

```
git checkout 0.x.y
```

Generate a tarball to be used in the build process:

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
you must update the changelog:

```
./scripts/update-changelog securedrop-foobar
```

Finally, build the package by pointing to the tarball and package version:

```
PKG_PATH=/path/to/tarball PKG_VERSION=0.x.y make securedrop-foobar
```

## Packaging non-Python based SecureDrop projects

TODO

## Intro to packaging

For an introduction to packaging Python projects into Debian packages, one can see the [SecureDrop Debian Packaging Guide](https://securedrop-debian-packaging-guide.readthedocs.io/en/latest/). Note that these guidelines on Read the Docs are for educational purposes only. The README you are currently reading is the canonical reference for SecureDrop Workstation packagers. 


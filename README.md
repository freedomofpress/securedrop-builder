# SecureDrop Debian Packaging

This repository contains the packaging files and tooling for building Debian packages for projects for the alpha [SecureDrop Workstation](https://github.com/freedomofpress/securedrop-workstation) based on Qubes OS. Packages are placed on `apt-test-qubes.freedom.press` for installation in Debian-based TemplateVMs. These packages are not yet ready for use in a production environment.

## Packaging a Python-based SecureDrop project

This includes `securedrop-proxy` and `securedrop-client`.

### Packaging Dependencies

In a Debian AppVM in Qubes:

```
make install-deps
make syncwheels
```

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


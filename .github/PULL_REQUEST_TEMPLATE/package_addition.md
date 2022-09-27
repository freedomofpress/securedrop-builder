---
name: Package addition
about: Add or upgrade a dependency for one of our Debian packages.

---

## Description

_Which packages are you adding, and why?_

## Test plan

- Automated tests ([Circle CI][ci]):
  - [ ] All Bullseye jobs are passing
  - [ ] Bookworm failures are not ignored:
    - This PR does not introduce any new Bookworm failures
    - An issue is open for all new Bookworm failures
- Security:
  - [ ] A [diff review][review-docs] was performed for all build dependencies

  [ci]: https://app.circleci.com/pipelines/github/freedomofpress/securedrop-debian-packaging
  [review-docs]: https://github.com/freedomofpress/securedrop/wiki/Dependency-specification-and-update-policies

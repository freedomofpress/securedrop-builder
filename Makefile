DEFAULT_GOAL: help
SHELL := /bin/bash

.PHONY: securedrop-proxy
securedrop-proxy: ## Builds Debian package for securedrop-proxy code
	PKG_NAME="securedrop-proxy" ./scripts/build-debianpackage

.PHONY: securedrop-client
securedrop-client: ## Builds Debian package for securedrop-client code
	PKG_NAME="securedrop-client" ./scripts/build-debianpackage

.PHONY: securedrop-workstation-config
securedrop-workstation-config: ## Builds Debian metapackage for Qubes Workstation base dependencies
	PKG_NAME="securedrop-workstation-config" ./scripts/build-debianpackage

.PHONY: securedrop-workstation-svs-disp
securedrop-workstation-svs-disp: ## Builds Debian metapackage for Disposable VM dependencies and tooling (DEPRECATED)
	PKG_NAME="securedrop-workstation-svs-disp" ./scripts/build-debianpackage

.PHONY: securedrop-workstation-viewer
securedrop-workstation-viewer: ## Builds Debian metapackage for Disposable VM dependencies and tooling
	PKG_NAME="securedrop-workstation-viewer" ./scripts/build-debianpackage

.PHONY: securedrop-export
securedrop-export: ## Builds Debian package for Qubes Workstation export scripts
	PKG_NAME="securedrop-export" ./scripts/build-debianpackage

.PHONY: securedrop-log
securedrop-log: ## Builds Debian package for Qubes Workstation securedrop-log scripts
	PKG_NAME="securedrop-log" ./scripts/build-debianpackage

.PHONY: securedrop-keyring
securedrop-keyring: ## Builds Debian package containing the release key
	PKG_NAME="securedrop-keyring" ./scripts/build-debianpackage

.PHONY: install-deps
install-deps: ## Install initial Debian packaging dependencies
	./scripts/install-deps

.PHONY: lint-desktop-files
lint-desktop-files: ## Install initial Debian packaging dependencies
	./scripts/lint-desktop-files

.PHONY: requirements
requirements: ## Creates requirements files for the Python projects
	./scripts/update-requirements

.PHONY: build-wheels
build-wheels: ## Builds the wheels and adds them to the localwheels directory
	./scripts/verify-sha256sum-signature $$(basename ${PKG_DIR})
	./scripts/build-sync-wheels
	./scripts/sync-sha256sums $$(basename ${PKG_DIR})
	@echo Done!

.PHONY: test
test: ## Run simple test suite (skips reproducibility checks)
	pytest -v tests/test_update_requirements.py tests/test_deb_package.py tests/test_utils.py

.PHONY: reprotest
reprotest: ## Runs only reproducibility tests, for .deb and .whl files
	pytest -vvs tests/test_reproducible_*.py

.PHONY: help
help: ## Prints this message and exits
	@printf "Makefile for building SecureDrop Workstation packages\n"
	@printf "Subcommands:\n\n"
	@perl -F':.*##\s+' -lanE '$$F[1] and say "\033[36m$$F[0]\033[0m : $$F[1]"' $(MAKEFILE_LIST) \
		| sort \
		| column -s ':' -t

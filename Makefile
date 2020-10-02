DEFAULT_GOAL: help

.PHONY: securedrop-proxy
securedrop-proxy: ## Builds Debian package for securedrop-proxy code
	PKG_NAME="securedrop-proxy" ./scripts/build-debianpackage

.PHONY: securedrop-client
securedrop-client: ## Builds Debian package for securedrop-client code
	PKG_NAME="securedrop-client" ./scripts/build-debianpackage

.PHONY: securedrop-workstation-config
securedrop-workstation-config: ## Builds Debian metapackage for Qubes Workstation base dependencies
	PKG_NAME="securedrop-workstation-config" ./scripts/build-debianpackage

.PHONY: securedrop-workstation-grsec
securedrop-workstation-grsec: ## Builds Debian metapackage for Qubes Workstation hardened kernel
	PKG_NAME="securedrop-workstation-grsec" ./scripts/build-debianpackage

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

.PHONY: requirements
requirements: ## Creates requirements files for the Python projects
	./scripts/update-requirements

.PHONY: build-wheels
build-wheels: ## Builds the wheels and adds them to the localwheels directory
	./scripts/verify-sha256sum-signature
	./scripts/build-sync-wheels -p ${PKG_DIR}
	./scripts/sync-sha256sums
	@printf "Done! Now please follow the instructions in\n"
	@printf "https://github.com/freedomofpress/securedrop-debian-packaging-guide/"
	@printf "to push these changes to the FPF PyPI index\n"

.PHONY: test
test: ## Run test suite
	pytest -v tests/

.PHONY: clean
clean: ## Removes all non-version controlled packaging artifacts
	rm -rf localwheels/*

.PHONY: help
help: ## Prints this message and exits
	@printf "Makefile for building SecureDrop Workstation packages\n"
	@printf "Subcommands:\n\n"
	@perl -F':.*##\s+' -lanE '$$F[1] and say "\033[36m$$F[0]\033[0m : $$F[1]"' $(MAKEFILE_LIST) \
		| sort \
		| column -s ':' -t

DEFAULT_GOAL: help

.PHONY: wheel-urls
wheel-urls: ## Creates download URLs from s3 bucket from sha256sums.txt file
	./scripts/createdownloadurls.py > wheelsurls.txt

.PHONY: syncwheels
syncwheels: ## Downloads wheels and sources from the remote server
	./scripts/syncwheels

.PHONY: securedrop-proxy
securedrop-proxy: ## Builds Debian package for securedrop-proxy code
	PKG_NAME="securedrop-proxy" ./scripts/build-debianpackage

.PHONY: securedrop-client
securedrop-client: ## Builds Debian package for securedrop-client code
	PKG_NAME="securedrop-client" ./scripts/build-debianpackage

.PHONY: securedrop-workstation-config
securedrop-workstation-config: ## Builds Debian metapackage for Qubes Workstation base dependencies

.PHONY: securedrop-workstation-grsec
securedrop-workstation-grsec: ## Builds Debian metapackage for Qubes Workstation hardened kernel

.PHONY: install-deps
install-deps: ## Install initial Debian packaging dependencies
	./scripts/install-deps

.PHONY: requirements
requirements: ## Creates requirements files for the Python projects
	./scripts/create-requirements
	./scripts/update-requirements

.PHONY: build-wheels
build-wheels: syncwheels ## Builds the wheels and syncs to the localwheels directory
	./scripts/build-sync-wheels -p ${PKG_DIR}
	./scripts/sync-sha256sums
	./scripts/createdownloadurls.py > wheelsurls.txt

.PHONY: sync-sha256sums
sync-sha256sums: ## Updates the sha256sums of the localwheels
	./scripts/sync-sha256sums
	./scripts/createdownloadurls.py > wheelsurls.txt

.PHONY: clean
clean: ## Removes all non-version controlled packaging artifacts

.PHONY: help
help: ## Prints this message and exits
	@printf "Makefile for building SecureDrop Workstation packages\n"
	@printf "Subcommands:\n\n"
	@perl -F':.*##\s+' -lanE '$$F[1] and say "\033[36m$$F[0]\033[0m : $$F[1]"' $(MAKEFILE_LIST) \
		| sort \
		| column -s ':' -t

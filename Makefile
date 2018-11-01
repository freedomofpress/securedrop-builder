DEFAULT_GOAL: help

.PHONY: securedrop-proxy
securedrop-proxy: ## Builds Debian package for securedrop-proxy code

.PHONY: securedrop-client
securedrop-client: ## Builds Debian package for securedrop-client code

.PHONY: securedrop-workstation-config
securedrop-workstation-config: ## Builds Debian metapackage for Qubes Workstation base dependencies

.PHONY: securedrop-workstation-grsec
securedrop-workstation-grsec: ## Builds Debian metapackage for Qubes Workstation hardened kernel

.PHONY: clean
clean: ## Removes all non-version controlled packaging artifacts

.PHONY: help
help: ## Prints this message and exits
	@printf "Makefile for building SecureDrop Workstation packages\n"
	@printf "Subcommands:\n\n"
	@perl -F':.*##\s+' -lanE '$$F[1] and say "\033[36m$$F[0]\033[0m : $$F[1]"' $(MAKEFILE_LIST) \
		| sort \
		| column -s ':' -t

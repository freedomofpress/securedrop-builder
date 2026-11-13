DEFAULT_GOAL: help
SHELL := /bin/bash

.PHONY: lint
lint:
	@poetry run ruff check .
	@poetry run ruff format --check .
	@poetry run zizmor .

.PHONY: fix
fix:
	@poetry run ruff check . --fix
	@poetry run ruff format .

.PHONY: install-deps
install-deps: ## Install initial wheel building dependencies
	./scripts/install-deps

.PHONY: requirements
requirements: ## Creates requirements files for the Python projects
	./scripts/update-requirements

.PHONY: build-wheels
build-wheels: ## Builds the wheels and adds them to the wheels subdirectory
	./scripts/verify-sha256sum-signature securedrop-$$(basename ${PKG_DIR})
	./scripts/build-sync-wheels
	./scripts/sync-sha256sums securedrop-$$(basename ${PKG_DIR})
	@echo Done!

.PHONY: build-server-wheels
build-server-wheels: ## Builds the securedrop-app-code wheels in the Noble builder image
	./scripts/verify-sha256sum-signature securedrop-app-code
	./scripts/run-in-server-builder ./scripts/build-sync-wheels --pkg-dir /securedrop/securedrop $(BUILD_ARGS)
	./scripts/sync-sha256sums securedrop-app-code
	@echo Done!

.PHONY: build-server-bootstrap-wheels
build-server-bootstrap-wheels: ## Builds the server-bootstrap wheels in the Noble builder image
	./scripts/run-in-server-builder ./scripts/build-sync-wheels --project server-bootstrap --pkg-dir ./server-bootstrap $(BUILD_ARGS)
	./scripts/sync-sha256sums server-bootstrap
	@echo Done!

.PHONY: test
test: ## Run simple test suite (skips reproducibility checks)
	poetry run pytest -v tests/test_update_requirements.py tests/test_utils.py

.PHONY: reprotest
reprotest: ## Runs only reproducibility tests for .whl files
	poetry run pytest -vvs tests/test_reproducible_wheels.py

.PHONY: help
help: ## Prints this message and exits
	@printf "Makefile for building SecureDrop Workstation wheels\n"
	@printf "Subcommands:\n\n"
	@perl -F':.*##\s+' -lanE '$$F[1] and say "\033[36m$$F[0]\033[0m : $$F[1]"' $(MAKEFILE_LIST) \
		| sort \
		| column -s ':' -t

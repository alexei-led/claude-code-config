.DEFAULT_GOAL := help

# --- Lint ---

.PHONY: lint lint-python lint-shell lint-markdown
lint: lint-python lint-shell lint-markdown ## Run all linters

lint-python: ## Lint Python files with ruff
	uv run ruff check .
	uv run ruff format --check .

lint-shell: ## Lint shell scripts with shellcheck + shfmt
	@command -v shellcheck >/dev/null 2>&1 || { echo "shellcheck not installed"; exit 1; }
	@command -v shfmt >/dev/null 2>&1 || { echo "shfmt not installed"; exit 1; }
	find plugins scripts -name '*.sh' -exec shellcheck {} +
	find plugins scripts -name '*.sh' -exec shfmt -i 0 -d {} +
	@# Check non-.sh shell scripts (pre-commit, release-tag)
	shfmt -i 0 -d scripts/pre-commit scripts/release-tag

lint-markdown: ## Lint Markdown files
	@command -v markdownlint-cli2 >/dev/null 2>&1 || { echo "markdownlint-cli2 not installed — skipping"; exit 0; }
	markdownlint-cli2 '**/*.md'

# --- Test ---

.PHONY: test
test: ## Run pytest
	uv run --extra test python -m pytest tests/ -v

# --- Validate ---

.PHONY: validate validate-config validate-flat validate-overlays validate-executables lint-instructions
validate: validate-config validate-flat validate-overlays validate-executables ## Run all validation checks

validate-config: ## Validate plugin configs and frontmatter
	uv run python scripts/validate-config.py

validate-flat: ## Check flat/ symlinks are in sync
	bash scripts/generate-flat.sh --check

validate-overlays: ## Check skills-codex/ overlays are in sync
	uv run python scripts/generate-overlays.py --check

lint-instructions: ## Lint agent/skill instructions (advisory)
	@uv run python scripts/lint-instructions.py

validate-executables: ## Check shell scripts have executable bit
	@fail=0; \
	for f in $$(find plugins scripts -name '*.sh') scripts/pre-commit scripts/release-tag; do \
		[ -x "$$f" ] || { echo "ERROR: $$f is not executable"; fail=1; }; \
	done; \
	[ $$fail -eq 0 ] || exit 1

# --- Format ---

.PHONY: fmt
fmt: ## Auto-format Python and shell files
	uv run ruff check --fix .
	uv run ruff format .
	find plugins scripts -name '*.sh' -exec shfmt -i 0 -w {} +
	shfmt -i 0 -w scripts/pre-commit scripts/release-tag

# --- Flat ---

.PHONY: flat
flat: ## Sync flat/ symlinks with plugin contents
	bash scripts/generate-flat.sh

# --- Overlays ---

.PHONY: overlays
overlays: ## Build platform-specific skill overlays (skills-codex/)
	uv run python scripts/generate-overlays.py

# --- CI (runs everything) ---

.PHONY: ci
ci: lint overlays validate test ## Run full CI pipeline locally

# --- Setup ---

.PHONY: setup
setup: ## Install pre-commit hook and dev dependencies
	cp scripts/pre-commit .git/hooks/pre-commit
	chmod +x .git/hooks/pre-commit
	uv sync --extra test
	@echo "Setup complete — pre-commit hook installed"

# --- Release ---

.PHONY: release
release: ## Create release tag (usage: make release V=1.2.0)
ifndef V
	$(error Usage: make release V=1.2.0)
endif
	scripts/release-tag v$(V)
	@echo "Push with: git push origin master v$(V)"

# --- Help ---

.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "  \033[36m%-18s\033[0m %s\n", $$1, $$2}'

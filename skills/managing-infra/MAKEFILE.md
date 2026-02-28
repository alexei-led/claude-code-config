# Makefile Patterns

## Self-Documenting Help

```makefile
.PHONY: help
help: ## Show this help
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | \
		awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

.DEFAULT_GOAL := help
```

## Go Project

```makefile
.PHONY: build test lint fmt clean

VERSION ?= $(shell git describe --tags --always --dirty)
LDFLAGS := -ldflags "-X main.version=$(VERSION)"

build: ## Build binary
	go build $(LDFLAGS) -o bin/app ./cmd/app

test: ## Run tests
	go test -v -race ./...

lint: ## Run linter
	golangci-lint run

fmt: ## Format code
	go fmt ./...
	goimports -w .

clean: ## Clean build artifacts
	rm -rf bin/ dist/
```

## Python Project

```makefile
.PHONY: install test lint fmt clean

install: ## Install dependencies
	uv sync

test: ## Run tests
	uv run pytest -v

lint: ## Run linter
	uv run ruff check .

fmt: ## Format code
	uv run ruff format .

clean: ## Clean cache files
	rm -rf .pytest_cache .ruff_cache __pycache__ .mypy_cache
```

## Docker Targets

```makefile
.PHONY: docker-build docker-push

IMAGE := ghcr.io/user/app
TAG := $(VERSION)

docker-build: ## Build Docker image
	docker build -t $(IMAGE):$(TAG) -t $(IMAGE):latest .

docker-push: ## Push Docker image
	docker push $(IMAGE):$(TAG)
	docker push $(IMAGE):latest
```

## Multi-Platform Build

```makefile
.PHONY: docker-buildx

docker-buildx: ## Build and push multi-arch image
	docker buildx build \
		--platform linux/amd64,linux/arm64 \
		--tag $(IMAGE):$(TAG) \
		--tag $(IMAGE):latest \
		--push .
```

## Phony Declarations

Always declare `.PHONY` for non-file targets to avoid conflicts with files of the same name.

```makefile
.PHONY: all build test lint fmt clean install help
```

## Variables

```makefile
# Conditional defaults
GO ?= go
GOFLAGS ?=

# Shell commands
SHELL := /bin/bash
.SHELLFLAGS := -eu -o pipefail -c
```

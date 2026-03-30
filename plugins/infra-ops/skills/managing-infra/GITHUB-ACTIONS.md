# GitHub Actions Patterns

## Workflow Structure

Separate workflows for different purposes:

```
.github/workflows/
├── ci.yml           # PRs: lint, test, compile
├── release.yml      # Tags: multi-arch Docker build
└── security.yml     # Scheduled: dependency scanning
```

## CI Workflow (PRs)

```yaml
name: CI
on:
  pull_request:
  push:
    branches: [main]

permissions:
  contents: read

jobs:
  lint:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true
      - run: golangci-lint run

  test:
    strategy:
      matrix:
        os: [ubuntu-24.04, ubuntu-24.04-arm]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true
      - run: go test -race -coverprofile=coverage.out ./...
      - uses: actions/upload-artifact@v4
        with:
          name: coverage-${{ matrix.os }}
          path: coverage.out
```

## Release Workflow (Tags)

Multi-arch Docker with native ARM runners (no QEMU):

```yaml
name: Release
on:
  push:
    tags: ["v*"]

permissions:
  contents: read
  packages: write

env:
  REGISTRY: ghcr.io
  IMAGE_NAME: ${{ github.repository }}

jobs:
  build-binaries:
    strategy:
      matrix:
        include:
          - os: ubuntu-24.04
            goos: linux
            goarch: amd64
          - os: ubuntu-24.04-arm
            goos: linux
            goarch: arm64
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-go@v5
        with:
          go-version-file: go.mod
          cache: true
      - run: |
          CGO_ENABLED=0 go build -ldflags="-s -w" -o bin/app-${{ matrix.goos }}-${{ matrix.goarch }} .
      - uses: actions/upload-artifact@v4
        with:
          name: binary-${{ matrix.goos }}-${{ matrix.goarch }}
          path: bin/

  docker:
    needs: build-binaries
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@v4

      - uses: actions/download-artifact@v4
        with:
          pattern: binary-*
          path: bin/
          merge-multiple: true

      - uses: docker/setup-buildx-action@v3

      - uses: docker/login-action@v3
        with:
          registry: ${{ env.REGISTRY }}
          username: ${{ github.actor }}
          password: ${{ secrets.GITHUB_TOKEN }}

      - uses: docker/metadata-action@v5
        id: meta
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}

      - uses: docker/build-push-action@v6
        with:
          context: .
          platforms: linux/amd64,linux/arm64
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

## Python CI

```yaml
jobs:
  test-python:
    strategy:
      matrix:
        os: [ubuntu-24.04, ubuntu-24.04-arm]
        python-version: ["3.13", "3.14"]
    runs-on: ${{ matrix.os }}
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4
      - uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5
        with:
          python-version: ${{ matrix.python-version }}
          cache: pip
      - run: |
          pip install -e ".[dev]"
          pytest --cov
```

## Caching Strategies

### Go

```yaml
- uses: actions/setup-go@d35c59abb061a4a6fb18e82ac0862c26744d6ab5 # v5
  with:
    go-version-file: go.mod
    cache: true # Built-in GOMODCACHE caching
```

### Python

```yaml
- uses: actions/setup-python@a26af69be951a213d495a4c3e4e4022e16d87065 # v5
  with:
    python-version: "3.14"
    cache: pip
    cache-dependency-path: pyproject.toml
```

### Docker

```yaml
- uses: docker/build-push-action@14487ce63c7a62a4a324b0bfb37086795e31c6c1 # v6
  with:
    cache-from: type=gha
    cache-to: type=gha,mode=max
```

## Security Best Practices

### Permissions

```yaml
permissions:
  contents: read # Default for most jobs
  packages: write # Only for release jobs
  id-token: write # Only for OIDC auth
```

### Pin Actions by SHA

```yaml
# Good - pinned
- uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4

# Bad - floating tag
- uses: actions/checkout@v4
```

### Environment Protection

```yaml
jobs:
  deploy:
    environment: production # Requires approval
    runs-on: ubuntu-24.04
```

### Concurrency Control

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

## Multi-Arch Build (No QEMU)

Use native ARM runners for compilation, combine in final image:

```yaml
jobs:
  build:
    strategy:
      matrix:
        include:
          - runner: ubuntu-24.04
            platform: linux/amd64
          - runner: ubuntu-24.04-arm
            platform: linux/arm64
    runs-on: ${{ matrix.runner }}
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4
      - run: docker build -t app:${{ matrix.platform }} .
      - run: docker save app:${{ matrix.platform }} > image.tar
      - uses: actions/upload-artifact@ea165f8d65b6e75b540449e92b4886f43607fa02 # v4
        with:
          name: image-${{ matrix.platform }}
          path: image.tar

  manifest:
    needs: build
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/download-artifact@d3f86a106a0bac45b974a628896c90dbdf5c8093 # v4
      # Create and push multi-arch manifest
```

## Reusable Workflows

```yaml
# .github/workflows/reusable-go-ci.yml
on:
  workflow_call:
    inputs:
      go-version:
        type: string
        default: "1.25"

jobs:
  ci:
    runs-on: ubuntu-24.04
    steps:
      - uses: actions/checkout@11bd71901bbe5b1630ceea73d27597364c9af683 # v4
      - uses: actions/setup-go@d35c59abb061a4a6fb18e82ac0862c26744d6ab5 # v5
        with:
          go-version: ${{ inputs.go-version }}
      - run: go test ./...
```

Usage:

```yaml
jobs:
  go:
    uses: ./.github/workflows/reusable-go-ci.yml
    with:
      go-version: "1.25"
```

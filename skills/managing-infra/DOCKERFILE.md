# Dockerfile Patterns

## Go Multi-Stage Build

```dockerfile
FROM golang:1.23-alpine AS builder

WORKDIR /app
COPY go.mod go.sum ./
RUN go mod download

COPY . .
RUN CGO_ENABLED=0 GOOS=linux go build -ldflags="-s -w" -o /app/bin/server ./cmd/server

FROM gcr.io/distroless/static-debian12:nonroot

COPY --from=builder /app/bin/server /server
USER nonroot:nonroot
ENTRYPOINT ["/server"]
```

## Python Multi-Stage Build

```dockerfile
FROM python:3.14-slim AS builder

WORKDIR /app
RUN pip install uv
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

FROM python:3.14-slim

WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY src/ ./src/

ENV PATH="/app/.venv/bin:$PATH"
USER nobody:nobody
ENTRYPOINT ["python", "-m", "src.main"]
```

## Base Image Selection

| Use Case         | Image                                       |
| ---------------- | ------------------------------------------- |
| Go static binary | `gcr.io/distroless/static-debian12:nonroot` |
| Go with cgo      | `gcr.io/distroless/base-debian12:nonroot`   |
| Minimal scratch  | `scratch`                                   |
| Python           | `python:3.14-slim`                          |
| Debug needed     | `alpine` or `debian:bookworm-slim`          |

## Security Best Practices

```dockerfile
# Non-root user
USER nonroot:nonroot
# or
USER nobody:nobody
# or specific UID
USER 65532:65532

# Read-only root filesystem (set in K8s or compose)
# No HEALTHCHECK with secrets
# No ADD for remote URLs (use COPY)
```

## Multi-Platform Build

```dockerfile
# Platform-aware build
FROM --platform=$BUILDPLATFORM golang:1.23-alpine AS builder
ARG TARGETOS TARGETARCH

RUN CGO_ENABLED=0 GOOS=$TARGETOS GOARCH=$TARGETARCH go build -o /app/server
```

Build with:

```bash
docker buildx build --platform linux/amd64,linux/arm64 --push -t image:tag .
```

## Caching Layers

Order from least to most frequently changed:

1. Base image
2. System dependencies
3. Language dependencies (go.mod, pyproject.toml)
4. Application code

```dockerfile
COPY go.mod go.sum ./
RUN go mod download        # Cached unless deps change

COPY . .                   # Invalidates on any code change
RUN go build
```

## .dockerignore

```
.git
.github
*.md
!README.md
Makefile
.env*
```

# Go Review Slice

Language-specific review material for Go 1.25+. The host skill supplies scope, workflow, and the findings/output contract — this file supplies only the Go tooling, version-specific traps, and focus-area checks.

## Run tooling first

Execute these before manual review to catch issues programmatically:

```bash
# Build and vet (catches logic issues)
go build ./... 2>&1 && go vet ./... 2>&1

# Security, correctness & performance linters (2 min timeout)
golangci-lint run --timeout=2m --enable=gosec,bodyclose,nilerr,nilnil,nilnesserr,errcheck,staticcheck,contextcheck,rowserrcheck,sqlclosecheck,nosprintfhostport,prealloc,perfsprint,ineffassign,wastedassign ./... 2>&1

# Race detector on tests (5 min timeout)
go test -race -short -timeout=5m ./... 2>&1
```

Include tool output in findings. If tools report issues, those are the primary findings. Focus manual review on files flagged by tools plus their direct callers. Do not scan the whole codebase manually.

If `golangci-lint` fails to run, debug it before falling back to manual review:

```bash
golangci-lint --help          # Main help
golangci-lint run --help      # Run command options
golangci-lint linters         # List available linters
golangci-lint linters --json  # Machine-readable linter list
```

## LSP navigation (trace security-sensitive data flow)

- `goToDefinition` — trace function calls to understand data flow
- `findReferences` — find all callers of security-sensitive functions
- `incomingCalls` — trace who calls a function (input-validation checks)
- `goToImplementation` — find concrete implementations of interfaces

## Go 1.25 specific traps

- WaitGroup misuse: `go vet` now catches `Add()` after goroutine spawn
- Host:port formatting: `go vet` catches unsafe `fmt.Sprintf("%s:%d", host, port)`
- Loop variable capture: fixed in Go 1.22+, but still flag for clarity in closures

## Logic correctness

- Nil pointer dereference: unchecked nil on pointers, maps, channels, interfaces
- Off-by-one errors: slice bounds, loop boundaries
- Integer overflow: calculations that could exceed int bounds
- Missing return: functions with multiple return paths missing values
- Context ignored: not checking `ctx.Err()` or `ctx.Done()` in long operations

## Security (OWASP)

- SQL injection: string concatenation in queries → use parameterized queries
- Command injection: `os/exec` with unsanitized user input
- Hardcoded secrets: credentials, API keys in source code
- Weak random: `math/rand` for security → use `crypto/rand`
- Path traversal: unsanitized file paths from user input
- Error exposure: returning internal error details to users
- Timing attacks: non-constant-time comparisons for secrets → `subtle.ConstantTimeCompare()`

## Performance

- Unbounded goroutines: missing worker pools → `wg.Go()` with semaphore
- `defer` in loops: defers stack up until function returns
- Slice growth: missing pre-allocation → `make([]T, 0, cap)`
- String concat in loops: use `strings.Builder`
- Connection leaks: missing `Close()` on connections, files, `resp.Body`
- Context without timeout: external calls without `context.WithTimeout`

## Failure handling

- Build or vet fails: report as blocking; do not proceed with manual review.
- Race detector finds a data race: blocking; report with goroutine trace if available.
- `golangci-lint` fails to run: use the debug commands above; continue manual review and note the tool was unavailable.
- LSP unavailable: skip data-flow tracing, note that cross-file call-chain checks were skipped.
- Security finding needs context not visible in code: prefix `[NEEDS REVIEW]` rather than asserting a vulnerability.

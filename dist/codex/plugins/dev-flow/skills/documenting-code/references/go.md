# Go Documentation Slice

Language-specific documentation conventions for Go 1.25+. The host skill supplies workflow and verification — this file supplies only the Go doc-comment conventions and examples.

## run tooling first

```bash
golangci-lint run --timeout=2m --enable=godot,godoclint,godox,revive ./... 2>&1
```

Use LSP to verify coverage:

- `documentSymbol` — list all exported symbols in a file
- `hover` — check existing documentation on symbols
- `findReferences` — verify documented APIs are used correctly

If golangci-lint fails:

```bash
golangci-lint --help
golangci-lint run --help
golangci-lint linters
```

## godoc comment conventions

Every exported symbol must have a comment starting with the symbol name.

### package comment

```go
// Package userservice provides user management functionality.
//
// Basic usage:
//
//	service := userservice.New(repo, logger)
//	user, err := service.CreateUser(ctx, CreateUserRequest{
//	    Email: "user@example.com",
//	})
package userservice
```

Place the package comment in `doc.go` or the main file.

### function comment

```go
// CreateUser creates a new user with the provided information.
// Returns the created user with generated ID or validation/conflict errors.
//
// Example:
//
//	user, err := service.CreateUser(ctx, CreateUserRequest{
//	    Email: "john@example.com",
//	})
func (s *Service) CreateUser(ctx context.Context, req CreateUserRequest) (*User, error)
```

Format: `// FunctionName does ...` not `// This function does ...`

### type comment

```go
// User represents a system user with authentication and profile information.
type User struct {
	// ID is the unique identifier, generated automatically
	ID string `json:"id"`

	// Email must be unique across the system
	Email string `json:"email" validate:"required,email"`
}
```

### deprecated marker

```go
// Deprecated: use NewClientV2 instead.
func NewClient(url string) *Client
```

## comment quality

Comments are only valuable when they explain why, not what.

Delete:

```go
i++              // increment i
user.Save()      // save the user
if err != nil {  // check for error
    return err   // return the error
}
```

Keep:

```go
// retryCount is 3 because the external API has ~30% timeout rate
const retryCount = 3

// Use RWMutex instead of Mutex because reads are 100x more frequent than writes
var cacheMu sync.RWMutex

// maxBatchSize must be ≤1000 per BigQuery streaming insert limits
const maxBatchSize = 1000
```

Decision rule: would a competent Go developer understand without this comment? Delete it. Does it explain business logic, constraints, or non-obvious decisions? Keep it.

## test files: no comments

Tests self-document through descriptive names and table-driven cases.

Delete:

```go
func TestCreate(t *testing.T) {
	// Create a new user
	user := &User{Name: "test"}
	// Call the service
	err := svc.Create(user)
	// Check no error
	require.NoError(t, err)
}
```

Keep:

```go
func TestUserService_Create_ValidUser(t *testing.T) {
	user := &User{Name: "test"}
	err := svc.Create(user)
	require.NoError(t, err)
}
```

Only keep a comment in a test file when explaining non-obvious external system behavior or why a specific edge case matters.

## readme accuracy

- `go get` / `go install` commands must work.
- Usage examples must compile and run with the current API.
- API documentation must match current exported symbols.

## failure handling

- Missing godoc on an exported symbol is a blocking issue — always report it.
- If golangci-lint is unavailable, inspect exported symbols manually via LSP `documentSymbol` and file reading.
- If LSP is unavailable, read files directly; note the limitation.

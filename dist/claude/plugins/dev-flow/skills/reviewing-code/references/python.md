# Python Review Slice

Language-specific review material for Python 3.12+. The host skill supplies scope, workflow, and the findings/output contract — this file supplies only the Python tooling, version-specific traps, and focus-area checks.

## Run tooling first

Execute these before manual review to catch issues programmatically:

```bash
# Static analysis and linting
ruff check .

# Security vulnerability scanning
bandit -r . -f json

# Type checking for logic errors
pyright src/
```

Include tool output in findings. Tool-reported issues take priority over manual findings. Focus manual review on files flagged by tools plus direct callers found via LSP. Do not scan the entire codebase manually.

If a tool is not installed or fails, note the failure in findings and continue with manual review of remaining focus areas. Do not attempt to install missing tools.

## LSP navigation (trace security-sensitive data flow)

- `goToDefinition` — trace function calls to understand data flow
- `findReferences` — find all callers of security-sensitive functions
- `incomingCalls` — trace who calls a function (input validation checks)
- `goToImplementation` — find concrete implementations of Protocols

## Python 3.14 specific traps

- Deferred annotations: no need for `from __future__ import annotations`
- `concurrent.interpreters`: true multi-core parallelism without GIL — review for race conditions in code migrating from multiprocessing
- Free-threaded build: thread safety assumptions changed — shared mutable state that was previously safe under the GIL may now race
- Incremental GC: large memory apps benefit; review object lifecycle patterns for unexpected retention

### Performance opportunities

- `concurrent.interpreters`: for CPU-bound work, consider subinterpreters over multiprocessing
- Free-threaded Python: threading now viable for CPU-bound code

## Logic correctness

- None handling: missing None checks, incorrect `is None` vs `== None`
- Mutable defaults: `def func(x=[]):` creates shared state bug
- Off-by-one errors: range boundaries, slice indices
- Type mismatches: passing wrong types despite type hints
- Exception handling: catching too broad, missing exception chaining (`raise ... from e`)

## Security (OWASP)

- SQL injection: string concatenation in queries — use parameterized queries
- Command injection: `subprocess` with `shell=True` and unsanitized input
- Deserialization: `pickle.loads()` on untrusted data
- Eval/Exec: `eval()` or `exec()` with user input
- Path traversal: unsanitized file paths from user input
- Weak crypto: MD5/SHA1 for passwords, `random` instead of `secrets`

## Performance

- N+1 queries: database queries in loops — batch fetch instead
- Missing indexes: repeated list lookups — use dict/set
- Memory leaks: unbounded caches, circular references, unclosed file handles
- Inefficient algorithms: O(n²) when O(n) exists
- Blocking I/O in async: synchronous calls in async functions

## Thread safety (Python 3.14 free-threading)

- Shared mutable state: global variables accessed from multiple threads
- Race conditions: non-atomic operations on shared data
- Missing locks: concurrent access without synchronization

## Failure handling

- Tool not installed or fails: note the gap in findings; continue with manual review of remaining areas.
- Security issue is ambiguous: err on the side of flagging it — mark as "potential" and explain the attack vector.
- LSP unavailable: fall back to reading files directly; note that cross-file call-chain checks were skipped.

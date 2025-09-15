---
allowed-tools: Task, Bash, Read, LS, Grep, mcp__perplexity-ask__perplexity_ask
description: Go testing guidelines - comprehensive rules for writing valuable tests
---

# Go Testing Guidelines

## Test Design

- Avoid pointless, naive, duplicate tests
- Learn from existing tests: style, design, flow, mock usage
- Prefer existing test files and adding cases to existing tests
- Make tests valuable, well-written, follow Go best practices

## Mocking

- Use mockery generated mocks with EXPECT for type safety
- Define interfaces close to consumers (prefer private)
- Generate private interface mocks in package with mockery annotations

## Test Execution & Debugging

- Write tests for ALL new/updated code promptly
- Ensure all tests pass (existing + new)
- When tests fail: suspect code changes, understand flow/expectations
- Never remove/comment tests or change code to fake results

## Process

- Ultrathink about good tests
- Consult Perplexity for help/questions
- Code must be correct, tests validate correctness

Apply these guidelines when writing or reviewing tests.

---
allowed-tools: Bash(gemini --prompt:*)
description: Ask Gemini for additional insights on complex problems, architectural decisions, or when you need additional context.
---

# Ask Gemini for Additional Insights

Query Gemini AI to get a second perspective on complex problems, architectural decisions, or when you need additional context.

## Usage

This command will invoke the Gemini CLI to analyze your question and provide insights.

```bash
gemini --model gemini-2.5-pro --prompt "$ARGUMENTS"
```

## When to Use

- **Architecture decisions**: Get alternative approaches to system design
- **Complex algorithms**: Verify optimization strategies
- **Security concerns**: Double-check security implementations
- **Best practices**: Confirm industry standards
- **Code review**: Get a second opinion on implementation choices

## Examples

- `/ask_gemini What are the security implications of using JWT tokens in this architecture?`
- `/ask_gemini Review this database schema design for scalability issues`
- `/ask_gemini What's the most efficient way to implement rate limiting in Go?`

## Note

Gemini provides an independent perspective. Always evaluate its suggestions against your project's specific requirements and constraints.

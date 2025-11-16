# Morphllm

Pattern-based code editing for bulk transformations across multiple files.

Use when: Multi-file edits, style enforcement, framework updates, text replacements
Avoid: Single file changes, semantic operations (symbol renames, dependency tracking)

Works best with: Sequential (plans strategy), native tools (individual edits)

Examples:

- "update all components to hooks" → Morphllm
- "enforce linting rules everywhere" → Morphllm
- "replace all logger calls" → Morphllm
- "explain this code" → native Claude

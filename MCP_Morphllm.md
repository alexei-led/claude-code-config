# Morphllm

Three tools for code search and bulk editing.

## Search Tools (always available)

**codebase_search** - Semantic search using AI embeddings. Finds code by meaning, not keywords.
Use when: "Where is X implemented?", understanding unfamiliar codebases, finding related code

**warp_grep** - AI-powered contextual search. Explores codebase automatically to find relevant snippets.
Use when: Finding specific implementations, tracing functionality across files

## Editing Tool (asks permission)

**edit_file** - Fast bulk edits across multiple files using `// ... existing code ...` placeholders.
Use when: Same change across 5+ files, style enforcement, framework migrations

Prefer built-in Edit for: Single files, careful refactors, complex logic changes

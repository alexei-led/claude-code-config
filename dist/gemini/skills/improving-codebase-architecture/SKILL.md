---
description: Find deepening opportunities in a codebase, informed by the domain language
  in CONTEXT.md and the decisions in docs/adr/. Use when the user wants to improve
  architecture, find refactoring opportunities, consolidate tightly-coupled modules,
  or make a codebase more testable and AI-navigable. NOT for line-level cleanup (use
  reviewing-code) or batch edits (use refactoring-code).
name: improving-codebase-architecture
---

# Improve Codebase Architecture

Surface architectural friction and propose deepening opportunities — refactors that turn shallow modules into deep ones. The aim is testability and AI-navigability.

## Role-gated action

This skill produces a candidate list and an agreed design, not edits. Both roles run it the same way; the difference is what happens after DESIGN AGREED:

- Write-capable role (engineer): hand the agreed design to `refactoring-code` to apply.
- Read-only role (reviewer): stop at DESIGN AGREED — it is the deliverable. Apply nothing.

## Language detection and references

Detect the language from the file extensions in scope and load the matching reference for language-specific deepening patterns:

- Go → [references/go.md](references/go.md)
- Python → [references/python.md](references/python.md)
- TypeScript → [references/typescript.md](references/typescript.md)
- Web → [references/web.md](references/web.md)

Mixed languages: load each matching reference. Unknown language: use the language-agnostic vocabulary and process below only.

## Critical Boundary Rules

- Do not use this skill for line-level cleanup: renames, formatting, comment cleanup, or one-file cosmetic edits.
- For line-level cleanup, say once: "This is not an architecture-deepening task." Route to `reviewing-code`, `refactoring-code`, or normal editing, and keep scope limited to the requested cleanup if proceeding.
- For line-level cleanup, do not mention modules, interfaces, seams, depth, leverage, locality, or other design terms. Ask once: "Do you want deeper architecture analysis, or should I keep this to the requested cleanup?"
- Seam discipline: do not add interfaces/ports for hypothetical variation. State that real variation is required before adding an interface/port: one adapter means hypothetical; two real adapters or confirmed variation means real.
- For valid architecture workflow descriptions, explicitly contrast deepening work with cosmetic or line-level cleanup.

## Glossary

Use the module-depth vocabulary exactly in every suggestion — module, interface, implementation, depth, seam, adapter, leverage, locality — plus the deletion test, the interface-is-the-test-surface principle, and the one-adapter-vs-two seam rule. Full definitions and the complete principle list are in [LANGUAGE.md](references/LANGUAGE.md); read it before naming candidates. Don't drift into "component," "service," "API," or "boundary."

This skill is informed by the project's domain model. The domain language gives names to good seams; ADRs record decisions the skill should not re-litigate.

## Process

### 1. Explore

Read the project's domain glossary (`CONTEXT.md` / `CONTEXT-MAP.md`) and any ADRs in `docs/adr/` for the area you're touching first. If the project uses `brainstorming-ideas`-style domain docs, that's where vocabulary and decisions live.

Then use the Agent tool with `subagent_type=Explore` to walk the codebase. Don't follow rigid heuristics — explore organically and note where you experience friction:

- Where does understanding one concept require bouncing between many small modules?
- Where are modules **shallow** — interface nearly as complex as the implementation?
- Where have pure functions been extracted just for testability, but the real bugs hide in how they're called (no **locality**)?
- Where do tightly-coupled modules leak across their seams?
- Which parts of the codebase are untested, or hard to test through their current interface?

Apply the **deletion test** to anything you suspect is shallow: would deleting it concentrate complexity, or just move it? A "yes, concentrates" is the signal you want.

### 2. Present candidates

Present a numbered list of deepening opportunities. For each candidate:

- **Files** — which files/modules are involved
- **Problem** — why the current architecture is causing friction
- **Solution** — plain English description of what would change
- **Benefits** — explained in terms of locality and leverage, and also in how tests would improve

Use CONTEXT.md vocabulary for the domain, and [LANGUAGE.md](references/LANGUAGE.md) vocabulary for the architecture. If `CONTEXT.md` defines "Order," talk about "the Order intake module" — not "the FooBarHandler," and not "the Order service."

### ADR conflicts

If a candidate contradicts an existing ADR, only surface it when the friction is real enough to warrant revisiting the ADR. Mark it clearly (e.g. "contradicts ADR-0007 — but worth reopening because…"). Don't list every theoretical refactor an ADR forbids.

Do NOT propose interfaces yet. Ask the user: "Which of these would you like to explore?"

### 3. Grilling loop

Once the user picks a candidate, drop into a grilling conversation (see the `brainstorming-ideas` skill's `references/grill-protocol.md` for the interview discipline). Walk the design tree with them — constraints, dependencies, the shape of the deepened module, what sits behind the seam, what tests survive.

Side effects happen inline as decisions crystallize:

- **Naming a deepened module after a concept not in `CONTEXT.md`?** Add the term to `CONTEXT.md` with a tight one-sentence definition, same discipline as `brainstorming-ideas`. Create the file lazily if it doesn't exist.
- **Sharpening a fuzzy term during the conversation?** Update `CONTEXT.md` right there.
- **User rejects the candidate with a load-bearing reason?** Offer an ADR in `docs/adr/`, framed as: "Want me to record this as an ADR so future architecture reviews don't re-suggest it?" Only offer when the reason would actually be needed by a future explorer to avoid re-suggesting the same thing — skip ephemeral reasons ("not worth it right now") and self-evident ones.
- **Want to explore alternative interfaces for the deepened module?** See [INTERFACE-DESIGN.md](references/INTERFACE-DESIGN.md).

## Failure handling

- No `CONTEXT.md` or ADRs found → proceed with exploration; note the absence; do not invent domain vocabulary.
- User asks for line-level cleanup (rename, formatting) → say once: "This is not an architecture-deepening task." Route to `reviewing-code` or `refactoring-code` and stop using architecture terminology.
- Candidate list rejected entirely → ask: "Is the friction you're experiencing in a specific area I haven't surfaced?" Narrow the explore scope before re-running.

## Output format

```text
ARCHITECTURE CANDIDATES
=======================
1. Files: <list>
   Problem: <friction description>
   Solution: <plain-English change>
   Benefits: locality — <how>; leverage — <how>; tests — <how>

2. ...

Which of these would you like to explore?
```

After the grilling loop resolves a candidate, output a brief summary:

```text
DESIGN AGREED
=============
Candidate: <name>
Seam: <where>
Depth gained: <what moves behind the interface>
CONTEXT.md updated: yes | no
ADR offered: yes | no | n/a
Next step: use refactoring-code to apply
```

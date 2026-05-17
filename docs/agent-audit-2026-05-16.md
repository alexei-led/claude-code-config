# Agent Audit — 2026-05-16

Diagnostic review of all 39 agents in `src/agents/`. No code changed. Scope: duplication, simplification, instruction quality, token efficiency, routing. Evidence base: per-agent reads, concrete `diff` overlap measurements per role family, `lint-instructions.py` format output, Perplexity best-practice cross-check.

## Scoring rubric

Seven dimensions, 1–5 (5 = best), max 35. Derived from the Perplexity subagent-design rubric, adapted to this repo's conventions.

- **F1 Focus** — one narrow job vs sprawl / multi-role
- **F2 Routing** — frontmatter `description` encodes language+operation+scope and is unambiguous vs siblings (this is the orchestrator's only routing signal)
- **F3 ToolScope** — `allowed-tools` minimal for the task; body tool refs match frontmatter (least privilege)
- **F4 Redundancy** — low duplication of global rules / model-default behavior / other agents
- **F5 DoneVerifiable** — explicit success / exit criteria
- **F6 TokenEff** — information density; no boilerplate or inline-tutorial bloat
- **F7 Distinctiveness** — uniqueness vs siblings after mentally stripping language-specific words

## Full scores (39 agents)

| Agent | F1 | F2 | F3 | F4 | F5 | F6 | F7 | Lines | Total/35 |
|---|---|---|---|---|---|---|---|---|---|
| infra-engineer | 4 | 5 | 4 | 4 | 4 | 4 | 5 | 184 | **30** |
| web-tests | 5 | 4 | 4 | 4 | 3 | 5 | 4 | 105 | **29** |
| playwright-tester | 5 | 5 | 3 | 3 | 3 | 4 | 5 | 61 | **28** |
| go-idioms | 4 | 5 | 4 | 3 | 4 | 3 | 4 | 220 | **27** |
| py-idioms | 4 | 4 | 3 | 4 | 3 | 5 | 4 | 110 | **27** |
| pdf-parser | 5 | 4 | 4 | 3 | 3 | 3 | 5 | 128 | **27** |
| scout | 4 | 4 | 4 | 3 | 4 | 4 | 4 | 66 | **27** |
| ts-idioms | 3 | 5 | 5 | 3 | 4 | 2 | 4 | 274 | **26** |
| go-qa | 5 | 3 | 4 | 3 | 4 | 4 | 3 | 114 | **26** |
| web-qa | 4 | 4 | 3 | 3 | 4 | 5 | 3 | 77 | **26** |
| web-idioms | 4 | 3 | 3 | 4 | 3 | 5 | 3 | 108 | **25** |
| advisor | 4 | 3 | 5 | 3 | 3 | 4 | 3 | 39 | **25** |
| go-simplify | 4 | 4 | 4 | 3 | 3 | 3 | 4 | 193 | **25** |
| web-impl | 4 | 3 | 4 | 4 | 3 | 4 | 3 | 100 | **25** |
| web-engineer | 4 | 4 | 3 | 3 | 2 | 4 | 4 | 164 | **24** |
| reviewer | 4 | 3 | 4 | 3 | 3 | 4 | 3 | 48 | **24** |
| ts-docs | 4 | 3 | 4 | 3 | 4 | 3 | 3 | 143 | **24** |
| web-docs | 3 | 2 | 3 | 4 | 3 | 5 | 4 | 107 | **24** |
| py-impl | 4 | 3 | 4 | 3 | 3 | 4 | 3 | 117 | **24** |
| py-simplify | 4 | 3 | 3 | 3 | 4 | 4 | 3 | 146 | **24** |
| perplexity-researcher | 4 | 3 | 4 | 3 | 3 | 3 | 3 | 96 | **23** |
| planner | 4 | 2 | 5 | 3 | 3 | 4 | 2 | 51 | **23** |
| py-docs | 4 | 3 | 2 | 3 | 4 | 4 | 3 | 117 | **23** |
| ts-impl | 4 | 3 | 4 | 2 | 4 | 2 | 4 | 188 | **23** |
| go-tests | 3 | 4 | 3 | 3 | 4 | 2 | 4 | 272 | **23** |
| py-tests | 4 | 3 | 3 | 3 | 3 | 4 | 3 | 187 | **23** |
| ts-tests | 3 | 4 | 2 | 3 | 4 | 3 | 4 | 212 | **23** |
| go-docs | 4 | 3 | 3 | 3 | 3 | 3 | 3 | 145 | **22** |
| go-impl | 4 | 3 | 4 | 2 | 4 | 2 | 3 | 226 | **22** |
| docs-keeper | 4 | 4 | 4 | 2 | 2 | 2 | 4 | 287 | **22** |
| typescript-engineer | 3 | 3 | 4 | 2 | 5 | 2 | 3 | 347 | **22** |
| python-engineer | 3 | 3 | 4 | 2 | 4 | 3 | 3 | 285 | **22** |
| ts-simplify | 4 | 3 | 3 | 3 | 4 | 2 | 3 | 235 | **22** |
| py-qa | 3 | 3 | 2 | 3 | 3 | 4 | 3 | 104 | **21** |
| ts-qa | 4 | 3 | 2 | 2 | 4 | 2 | 4 | 253 | **21** |
| spec-planner | 4 | 2 | 5 | 2 | 3 | 3 | 2 | 91 | **21** |
| web-simplify | 3 | 2 | 3 | 3 | 3 | 2 | 4 | 208 | **20** |
| go-engineer | 2 | 2 | 4 | 2 | 4 | 2 | 2 | 347 | **18** |
| worker | 2 | 1 | 1 | 2 | 2 | 3 | 1 | 29 | **12** |

Mean 23.7/35. The distribution is tight (most agents 21–27) because they share a templated skeleton — the scores cluster by construction, which is itself a finding. Two outliers at the bottom: `go-engineer` (18) and `worker` (12).

## Cross-cutting findings

### 1. The dominant problem is routing ambiguity, not token bloat

Every language family ships near-identical frontmatter descriptions: `go-qa`, `go-tests`, `go-simplify`, `go-impl` all reduce to "Go code review" as a routing key. The orchestrator sees only `name` + `description`; it cannot disambiguate four agents that all say "review Go code." This degrades dispatch accuracy across ~24 agents. Highest-severity issue found. F2 is the lowest-scoring dimension repo-wide.

### 2. A templated skeleton exists and has already drifted

Concrete `diff` measurements per family (shared / language-specific):

| Family | Shared skeleton | Verdict |
|---|---|---|
| docs | 35–47% | template |
| idioms | 14–42% | template |
| impl | 33–45% | template |
| qa | 28–31% | template |
| simplify | ~20% (+identical Core Philosophy block) | template |
| tests | 6–10% | keep separate |
| engineers (lang) | ~43% (go/ts 347L twins are coincidental, not clean) | template |

Drift is observable, not hypothetical: the same "competent dev would understand" rule appears in three phrasings across `*-docs`; `*-qa`/`*-impl`/`*-simplify`/`*-tests` Python files carry a "Python 3.14" section while frontmatter says 3.12+; `typescript-engineer` has a `Failure Handling` section its Go/Python twins lack; `python-engineer` has an `Agentic Approach` preamble no sibling has. Manual cross-language sync has already failed.

### 3. Inline tutorials inflate the heavy files

`go-engineer`/`typescript-engineer` (347L), `docs-keeper` (287L, ~60% boilerplate templates), `ts-idioms` (274L), `go-tests` (272L), `ts-qa` (253L), `ts-simplify` (235L) carry 30–100 lines of language tutorial / code examples (thin-wrapper patterns, OWASP snippets, tsconfig blocks, React Testing Library). These restate content that belongs in the `writing-go` / `writing-typescript` skills. This is the real runtime token waste — distinct from the duplication problem.

Headline pathology: **`go-engineer` is the largest file in the repo (347L, tied with `typescript-engineer`) yet scores 18/35 — second-worst overall, only above `worker`.** Size is inversely correlated with quality here: an HTMX section bolted onto a Go agent, no "NOT for" exclusion, heavy idiom/test overlap with `go-idioms`/`go-tests`/`go-impl`. The biggest agents are the worst agents.

### 4. Tool over-permissioning is systemic

Frontmatter grants bash tools the body never invokes: `py-docs` (mypy, pyright, pytest, uv), `web-*` (playwright), `py-simplify` (mypy, pyright, pytest), `ts-qa`/`ts-tests` (eslint, prettier, tsc on agents that forbid style work), `py-qa` runs `bandit` that is *not* granted (will fail sandboxed). Least-privilege violations on roughly half the families.

### 5. Format non-compliance is universal and template-fixable

`lint-instructions.py`: F-BOLD-SPARSE on 27 agents (bold on 27–51% of prose lines vs the repo's ≤15% rule), F-NO-ITALIC on 8, F-NO-DIAGRAM on `docs-keeper` (ships a mermaid example the repo's own rules forbid). U-FAILURE (no failure handling) on advisor/docs-keeper/planner/reviewer/scout/worker. U-GROUND (no verification step) on pdf-parser/planner/playwright-tester/reviewer/scout/spec-planner/infra-engineer. Because the cause is one shared skeleton, one fix propagates.

### 6. Redundant / poorly-bounded agent pairs

- **`planner` vs `spec-planner`** — descriptions are functionally identical ("creates implementation plans"); they serve different pipelines (scout→planner→worker vs `.spec/` workflow) but nothing in the routing key says so.
- **`*-engineer` vs `*-impl`** — both propose code changes in the same language/domain; the real split (greenfield vs review-existing) is stated in neither description. Orchestrator cannot route between them.
- **`reviewer` / `advisor` vs `*-qa`** — all produce read-only risk lists; differentiators (cross-language, PR-scope, strategic-vs-line-level) are body-only, invisible to routing.
- **`worker`** — lowest score (12/35). "General-purpose worker with full capabilities, no tools declared" is a routing black hole and an explicit anti-pattern (linter U-SCOPE + S-ANTI-EAGER). Any unmatched dispatch lands here.

### 7. Naming inconsistency breaks prefix routing

`python-engineer` / `typescript-engineer` / `web-engineer` use full language names; every peer uses short prefixes (`py-impl`, `ts-idioms`, `go-qa`). Any prefix-based routing or tooling that globs `py-*` / `ts-*` silently misses the engineers. Standardize to `py-engineer` / `ts-engineer`.

## Recommendation on the plugin-boundary question (you asked me to advise)

You ship per-language plugins (`go-dev`, `python-dev`, `typescript-dev`, `web-dev`), each bundling its own agents. The options were: keep per-language, shared build-time template, or one parametric cross-language agent.

**Recommendation: shared build-time template — option (b). Do not collapse to a parametric agent.**

Reasoning:

- **Parametric (c) is wrong here.** It destroys the per-language routing signal (already the weakest dimension) and breaks plugin packaging — `python-dev` cannot ship a "covers all languages" agent. A single parametric agent also bloats to 500–600 lines enumerating every language's tooling, eating the token savings it promised.
- **Keep-as-is (a) is failing.** Drift is measured and active; 30–45% of every file is hand-maintained duplication.
- **Template (b) keeps the plugin boundary intact** — `make build` still emits one self-contained per-language agent into each plugin's `dist/`. Runtime token cost per agent is unchanged. The win is maintenance and drift elimination: skeleton (Role / Run-Tooling-First / LSP nav / Output Format / Failure Handling / format compliance) lives once in a partial; `{{language}}`, `{{version}}`, `{{tooling_commands}}`, `{{focus_areas}}` are slots. This is the same pattern `make build` already uses for the four targets.
- **Exception: `*-tests`.** Only 6–10% shared skeleton; content is language-intrinsic (table-driven vs parametrize vs test.each). Templating saves ~9 lines and adds indirection. Keep these four hand-written; just normalize the drifted "pointless tests" definition and fix the routing description.

Net: template the docs/idioms/impl/qa/simplify families and the 4 language engineers; leave `*-tests` and the standalone agents per-file.

## Ranked recommendations (diagnostic — no changes made)

1. **Fix routing descriptions first (highest impact, lowest effort).** Rewrite every frontmatter `description` to `[language] — [operation] — [scope]` with disjoint trigger phrases so `go-qa`/`go-tests`/`go-simplify`/`go-impl` are distinguishable. Add pipeline prefixes to `planner`/`spec-planner`. Add "new feature" vs "review existing" to `*-engineer` vs `*-impl`. No behavior change, large dispatch-accuracy gain.
2. **Resolve `worker`.** Either give it a narrow job + explicit scope guards, or delete it and let the orchestrator fall back to a named agent. A catch-all with no tools and no scope is a liability.
3. **Introduce the build-time skeleton template** for docs/idioms/impl/qa/simplify + 4 language engineers. Eliminates ~30–45% maintained duplication and all drift; fixes F-BOLD-SPARSE / U-FAILURE / U-GROUND in one place.
4. **Move inline tutorials out of the heavy files** into the `writing-*` skills: `go-engineer`/`ts-engineer` (−~150L), `go-tests` (−~60L), `ts-idioms` (−tsconfig/satisfies blocks), `ts-qa` (−OWASP snippets), `docs-keeper` (−boilerplate templates). Direct runtime token reduction.
5. **Tighten tool scopes** to least privilege; delete unused bash grants; add `bandit` to `py-qa` (currently broken under sandbox).
6. **Decide `*-engineer` vs `*-impl` coexistence.** Either encode the boundary in both descriptions or merge `impl` into `engineer` as a review submode. Today they are unroutable duplicates.
7. **Rename** `python-engineer`/`typescript-engineer`/`web-engineer` → `py-engineer`/`ts-engineer`/`web-engineer` for prefix consistency.
8. **Standardize the empty-result output contract** (`"No issues found."` vs `"No issues in {area}."` vs a `### SIMPLIFICATIONS` block) — fold into the template.

## Notes

## Consolidation design — Option A (chosen direction)

Decided: collapse the language-family agents into the **existing** role skills extended with per-language `references/`, using `context: fork` for isolation. Packaging scoped per plugin. This section is the design; no code changed.

### Why this works mechanically (verified, not assumed)

- The 5 cross-language review skills (`reviewing-code`, `improving-tests`, `documenting-code`, `refactoring-code`, `fixing-code`) all belong to **one** plugin, `dev-workflow`. The 24 `*-{docs,idioms,impl,qa,simplify,tests}` agents also belong to `dev-workflow`. So this is a within-plugin consolidation — routing topology does not change across plugins.
- `writing-{go,python,typescript,web}` already `context: fork` and already ship per-language `references/` (PATTERNS.md, TESTING.md, CLI.md). The pattern is proven by 12 existing skills; `make build` copies a skill's whole `references/` dir to every dist target automatically (`SUPPORT_DIRS` in `scripts/build/overlay.py`). **No build changes required.**
- The genericity validator (`scripts/validate/validate_genericity.py`) scans only `SKILL.md`/`AGENT.md` base + non-Claude overlays. It does **not** scan `references/`. Putting Go/Python/TS/Web content in `reviewing-code/references/go.md` is safe.
- Per-plugin scoping is automatic: `dev-workflow` is cross-language so its review skills correctly carry all 4 references; each `*-dev` plugin owns only its own `writing-<lang>` skill, so it ships only that language's references. Nothing to engineer.

### Agent-family → skill mapping

| Deleted agents (×4 langs) | Absorbed into | Reference target |
|---|---|---|
| `*-qa` | `reviewing-code` (security/quality) | `reviewing-code/references/<lang>.md` |
| `*-simplify` | `improve-codebase-architecture` (already purpose-built: over-abstraction, refactoring opportunities, testability) | `improve-codebase-architecture/references/<lang>.md` |
| `*-impl` | `reviewing-code` (requirements/DI review) or `fixing-code` (bug-style) — see open decision | `reviewing-code/references/<lang>.md`, "implementation review" section |

Rationale for splitting rather than dumping all three into `reviewing-code`: the audit's worst finding was routing ambiguity. Collapsing qa+simplify+impl onto one already-broadest-in-repo skill would move the ambiguity up a layer, not dissolve it. `improve-codebase-architecture` already exists with a description tuned for the simplify concern; distributing across purpose-built skills keeps each routing key discriminative.
| `*-idioms` | `writing-<lang>` (idiom review = inverse of idiom authoring; same knowledge) | extend existing `writing-<lang>/references/PATTERNS.md` |
| `*-docs` | `documenting-code` | `documenting-code/references/<lang>.md` |
| `*-tests` | `improving-tests` | `improving-tests/references/<lang>.md` |

Net: 24 review-family agents → 0. Three `dev-workflow` skills gain one `references/<lang>.md` each (×4 = 12 small files); `writing-<lang>` PATTERNS.md absorb the idiom content. Each new reference holds only the genuinely language-specific content the audit measured (53–94% of each old agent) — the 30–45% shared skeleton is dropped, not copied, because the host skill already supplies it.

### The engineer coupling (must handle, do not skip)

`writing-go` declares `agent: go-engineer`, `writing-python` → `python-engineer`, etc. Deleting the engineers without repointing breaks the fork target. The 4 engineer AGENT.md files are ~43% shared skeleton (measured) with the rest being generic philosophy/workflow/verification that duplicates the `writing-<lang>` skill body. Resolution:

- Collapse the 4 `*-engineer` agents into **one** generic `engineer` agent: language-agnostic persona (propose-only mode, proposal format, workflow, verification checklist — the shared 43%). All language specifics come from the `writing-<lang>` skill body + references that the fork already loads.
- Repoint `writing-<lang>` frontmatter: `agent: engineer`.
- Also fixes the naming inconsistency (no more `python-engineer` vs `py-impl` prefix mismatch — the per-language engineer disappears entirely).

39 → ~12 agents (initial design estimate — superseded; see **Executed resolution** below for the actual 39 → 3 outcome): 1 generic `engineer`, kept standalone (`advisor`, `scout`, `pdf-parser`, `perplexity-researcher`, `playwright-tester`, `infra-engineer`, `spec-planner`), plus the resolutions below.

### Standalone dispositions

- **`docs-keeper`** (dev-workflow, 287L, ~60% boilerplate): redundant with the `documenting-code` skill. Delete; `documenting-code` (already `context: fork`) replaces it.
- **`reviewer`** (pi-only): redundant with `reviewing-code`. Delete on plugin platforms; keep only if pi flat-layout needs a named entrypoint — then make it a 10-line shim that defers to the skill.
- **`worker`** (pi-only, score 12/35): catch-all anti-pattern. Either give it a narrow scope + tool grants, or delete and let routing fall back to a named agent.
- **`planner` vs `spec-planner`**: different homes (pi flat vs `spec` plugin), genuinely different pipelines. Keep both; fix descriptions to encode the pipeline (the audit's rec #1) — not a consolidation target.
- **`advisor`** (pi-only): distinct enough (strategic, propose-only, escalation). Keep; tighten description vs `reviewing-code`.

### Migration order (low-risk first)

1. Fix all frontmatter `description` fields (audit rec #1) — independent, immediate dispatch-accuracy win, no structural change.
2. Build `engineer` generic agent; **add it to all four** `src/plugins/{go,python,typescript,web}-dev/plugin.yaml` (each `writing-<lang>` lives in its own language plugin and forks into the engineer, so the shared agent must be present in all four); repoint the 4 `writing-<lang>` skills to `agent: engineer`; delete the 4 `*-engineer` agents. Verify `writing-go` still forks.
3. Add `references/<lang>.md` to `reviewing-code`, `improving-tests`, `documenting-code`, `improve-codebase-architecture`. For idioms: `writing-go/python/typescript` already have `references/PATTERNS.md` to extend; **`writing-web` has no `references/` dir — create it** (`writing-web/references/PATTERNS.md`). Port only the language-specific slices from the agents being deleted.
4. Add the language-detection + reference-load instruction to each host skill body (pattern: detect from file extensions → read matching `references/<lang>.md`; fall back to general guidance).
5. Delete the 24 review-family agents + `docs-keeper`; remove them from `src/plugins/dev-workflow/plugin.yaml`.
6. Resolve `worker`/`reviewer`; `make check` + `make build`; spot-test a Go review and a Python test-improvement through the skills.

### Risks

- **Language detection in-skill** replaces orchestrator language routing. Mitigation: deterministic from file extensions; explicit fallback. Lower risk than today's ambiguous descriptions (the audit's worst dimension).
- **Behavior compression**: a reference is read fully on demand, so per-language depth is preserved — but cross-cutting cases (mixed TS+HTML) need the skill body to say "load multiple references when languages mix."
- **Loss of parallel per-language subagents**: today rarely exploited (the families aren't dispatched in parallel); `context: fork` still gives isolation. Acceptable.
- **pi platform** uses flat layout and owns several pi-only agents (`advisor`/`scout`/`planner`/`worker`/`reviewer`). This consolidation is plugin-centric; pi dispositions are a separate, lower-priority pass.

### Open decisions (need your call before implementation)

1. Engineer collapse: **(i)** one generic `engineer` agent as fork target (recommended — preserves a named persona, minimal change to `writing-<lang>`), or **(ii)** drop `agent:` entirely so `writing-<lang>` forks with the default Task agent and the skill body carries everything (fewer agents still, but loses the propose-only persona separation). Recommendation: (i).
2. `*-impl` home: `reviewing-code` (requirements/DI compliance review of existing code) vs `fixing-code` (when the impl review is bug-driven). These are different user intents; the old `*-impl` agents blurred them. Recommendation: route the compliance/review slice to `reviewing-code`, leave bug-diagnosis to `fixing-code` — but confirm this matches how you actually use the impl agents today.

## Notes

This report uses markdown tables deliberately — it is a human-facing diagnostic, not an LLM instruction file, so the repo's "no tables in instructions" rule (AGENTS.md) does not apply. Scores were produced by eight role-clustered audit subagents using the shared rubric above and concrete `diff`/`wc` overlap measurements; four subagent-reported totals were arithmetic errors and have been corrected by re-summing F1..F7. The per-cluster raw evidence is not persisted beyond this session — regenerate via the same role-clustered audit if deeper line-level detail is needed.

## Executed resolution

This diagnostic was acted on. The consolidation plan `docs/plans/completed/20260516-agent-role-skill-consolidation.md` executed the chosen direction (Option A, refined): instead of a build-time template, the two conflated axes — role and domain/language — were fully separated. Role became an agent (an enforced tool-grant envelope, not prose); domain became a role-agnostic skill that owns its output contract; language became `references/<lang>.md` inside each skill.

Outcome: 39 → 3 agents (`engineer`, `reviewer`, `advisor`) with disjoint enforced envelopes — `reviewer` is provably non-mutating (Read/Grep/Glob/LS only), `engineer` is the sole mutator (Edit/Write/Bash). The dominant defect this audit identified (finding #1, routing ambiguity across ~24 indistinct keys) is structurally eliminated: language is no longer a routing key. Per-language tutorials moved out of agent bodies into skill references (findings #3, #4, #6). See the plan file for the per-task record and the scenario-parity verification.

### Known deferred follow-up

`src/skills/spec-work/SKILL.md` was repointed name-swap-only per the Task 7/8 fence (plan line 270): the flow text was intentionally left untouched to keep the consolidation surgical. As a result its Solo-engineer prompt still says "Return proposals only — do not apply edits" (lines 168–169) and the Implementation-pair block assigns the `reviewer` role as a "test specialist" that "writes tests" (line 178). Both contradict the new role envelopes: `engineer` applies directly (does not return proposals), and `reviewer` is Read/Grep/Glob/LS only (cannot write tests). The skill still functions for planning and decomposition, but its implementation-mode prose needs a follow-up rewrite to match the role contracts (engineer applies and verifies; pair = reviewer-proposes-tests then engineer-applies). Tracked here so it is not lost; deliberately out of scope for the consolidation pass.

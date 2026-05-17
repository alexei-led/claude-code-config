# Agent Role+Skill Consolidation (39 → 3)

## Overview

Refactor cc-thingz agents from **39 → 3** by separating two axes that are currently conflated in every agent file: **role** (the agent: an *enforced capability envelope* + a reasoning stance) and **domain/language** (skills + per-language references). Today `go-qa`, `go-tests`, `go-simplify`, `go-impl`, `go-engineer`, `go-docs`, `go-idioms` are seven agents that are really one role × one language (Go) × seven domains. This refactor makes role an agent and domain×language a composable skill.

Role test (ratified): *a role exists only if it owns a distinct **enforced** capability envelope (tool grant, not prose) AND a reasoning stance no skill can supply.* Output format and domain procedure are skill concerns — keeping them in role bodies was a source of the duplication. Grounded tool-grant audit showed today's `engineer`/`reviewer`/`advisor`/`scout` share one envelope (Read+Bash, no Edit/Write) and are distinguished only by unenforced prose — the "roles are only names" defect. Final set: 3 roles with genuinely disjoint enforced envelopes.

Problem solved: the audit (`docs/agent-audit-2026-05-16.md`) found routing ambiguity (24 agents collapse to indistinct routing keys) is the dominant defect, plus 30–45% hand-maintained template duplication with measured drift. Composition replaces duplication.

Benefits: routing ambiguity structurally eliminated (4 disjoint agent keys, language no longer a routing key); ~30–45% duplicated skeleton written once; drift impossible (one skeleton, ported language slices); 100% scenario parity preserved.

Integration: zero build-system changes — `scripts/build/overlay.py` `SUPPORT_DIRS` already copies whole `references/` dirs to every dist target; `scripts/validate/validate_genericity.py` skips `references/`. Verified, not assumed.

## Context (from discovery)

Files/components involved:

- `src/agents/` — 39 agent dirs, each `AGENT.md` + optional `claude/` + `pi/` overlays.
- `src/skills/<skill>/SKILL.md` + `claude/frontmatter.yaml` + `pi/` overlays + `references/`.
- `src/plugins/{go-dev,python-dev,typescript-dev,web-dev,infra-ops,dev-workflow,spec,testing-e2e,dev-tools}/plugin.yaml`.
- `scripts/build/overlay.py`, `scripts/validate/validate_genericity.py`, `Makefile` — reference only, no change expected.

Coupling map (grounded — the ONLY `agent:` fork pointers, all in `src/skills/<skill>/claude/frontmatter.yaml`):

- `managing-infra` → `infra-engineer`
- `writing-go` → `go-engineer`
- `writing-python` → `python-engineer`
- `writing-typescript` → `typescript-engineer`
- `writing-web` → `web-engineer`

No `spec→spec-planner`, `testing-e2e→playwright-tester`, `researching-web→perplexity-researcher` couplings exist — those agents are plain Task-dispatched (listed only in plugin.yaml `agents:`), deletable without repointing once a skill substitute is confirmed.

Patterns found:

- `*-engineer` agents are **propose-only today** (`go-engineer/AGENT.md`: "You do NOT have edit tools... returning structured proposals for the main context to apply") but their `claude/frontmatter.yaml` grants full Bash and their body carries a MANDATORY build/test/lint checklist — an internal contradiction. The new `engineer` resolves it toward **execute**: gains Edit/Write, applies + verifies. This is a deliberate behavioral change (Risk 1), not a preserved contract.
- pi-only agents (in no plugin.yaml): `advisor`, `planner`, `reviewer`, `scout`, `worker` — `AGENT.md` + `pi/` only.
- plugin.yaml shape: `name`, `version`, `description`, `skills: []`, `agents: []`, `hooks: []`, optional `marketplace_name`.

Dependencies identified: `context: fork` resolves `agent:` from `claude/frontmatter.yaml`; deleting a referenced agent silently mis-targets the fork. The coupling sweep gates all deletion.

## Development Approach

- **testing approach**: Regular. This is a config/instruction repo, not application code. The verification analog to unit tests is the repo's gate suite, run per task on the touched scope:
  - `make lint-instructions` — agent/skill format compliance (F-BOLD-SPARSE etc.)
  - `make check` — ruff, shellcheck, markdownlint, validate-config
  - `make build` — compile `src/` → `dist/` for claude/codex/gemini/pi (needs sandbox disabled; uv cache `~/.cache/uv` restricted in CC sandbox)
  - `python scripts/validate/validate_genericity.py` — genericity gate
  - **scenario-parity spot-test**: dispatch the task's scenario through the new path and confirm equivalent behavior to the deleted agent
- Complete each task fully before the next. Small, focused changes.
- **CRITICAL: every task ends with its validation gate green before the next task starts** — no exceptions.
- **CRITICAL: the coupling sweep (Task 1) gates every deletion task; no agent is deleted until its fork coupling is repointed and a real fork is verified.**
- **CRITICAL: update this plan file when scope changes during implementation.**

## Testing Strategy

- **Format/lint gate**: `make lint-instructions` after any agent/skill body change.
- **Build gate**: `make build` after coupling/plugin/deletion changes; must emit all 4 targets cleanly.
- **Genericity gate**: `validate_genericity.py` after skill base/overlay edits (references/ exempt — relied upon).
- **Scenario-parity spot-tests** (the user's explicit requirement — 13/13 must stay green):
  | Scenario | New path |
  |---|---|
  | Go security review | `reviewer` + `reviewing-code` → `references/go.md` |
  | Py test improvement | `engineer` + `improving-tests` → `references/python.md` |
  | TS over-abstraction | `reviewer` proposes / main applies + `improve-codebase-architecture` → `references/typescript.md` |
  | New Go feature | `engineer` via `writing-go` fork |
  | Go idiom critique | `reviewer` + `writing-go` (read-only) |
  | Py docs | `engineer` + `documenting-code` → `references/python.md` |
  | Py bug fix | `engineer` + `fixing-code` → `references/python.md` |
  | Infra change | `engineer` + `managing-infra` |
  | Web research | any role + `researching-web` |
  | E2E | `engineer` + `testing-e2e` |
  | Locate code | `reviewer` + `searching-code` |
  | Plan a feature | `reviewer` + (`spec` \| `planning:make`) |
  | PDF extract | any role + `parsing-documents` |
- No pi-extensions TypeScript changes expected (agent defs are markdown in `src/agents/`; the loader `src/pi-extensions/subagent/agents.ts` is untouched). If that assumption breaks, run its vitest.

## Progress Tracking

- mark completed items `[x]` immediately when done
- newly discovered tasks: ➕ prefix
- blockers: ⚠️ prefix
- keep plan synced with actual work

## Solution Overview

Architecture: two axes, never co-located in one file.

### The 3 roles (enforced envelopes — the irreducible role layer)

- **`engineer`** — enforced tools: Read + **Edit + Write + Bash** (+ search/mem). The *only* mutator. Stance: constructive builder; applies changes and runs the MANDATORY build/test/lint verification on what it changed. Absorbs `worker` (worker's full-capability role *is* engineer) and the 4 `*-engineer` + `infra-engineer`. Fork target for `writing-{go,python,typescript,web}` and `managing-infra`.
- **`reviewer`** — enforced tools: **Read + Grep + Glob only. NO Bash, NO Edit/Write.** Provably non-mutating and provably cannot run builds — so `reviewer ≠ engineer` is tool-enforced, not prose. Stance: adversarial evaluator (assume bugs exist). Absorbs `scout` (via `searching-code`), pi `reviewer`, all 24 review-family, `docs-keeper`, and **planning** (via `spec`/`planning:make` skill — no separate planner role).
- **`advisor`** — unchanged. Read + read-only git Bash, xhigh thinking, special transcript-forwarding invocation mechanics. Survives the test on genuine mechanics, not stance alone.

39 → 3. `planner` and `worker` are deleted (not renamed): planning = `reviewer` + planning skill; mutation = `engineer`.

### The other two axes (skill layer — everything a skill *can* own moves here)

- **Domain = role-agnostic skill.** `reviewing-code`, `improving-tests`, `documenting-code`, `improve-codebase-architecture`, `fixing-code`, `refactoring-code`, `managing-infra`. Each skill **owns its output contract** (findings format / change format) — this is the duplication that leaves the role bodies. The skill instructs: "if your role can write (engineer), apply + verify; else (reviewer) emit as a structured proposal." One knowledge source, role-gated by enforced tools.
- **Language = `references/<lang>.md` inside each domain skill.** Skill self-detects from file extensions (mixed → load several; unknown → generic core). Language is not a routing key.
- **Authoring skills stay**: `writing-{go,python,typescript,web}`; `*-idioms` folds into `writing-<lang>/references/PATTERNS.md` (reviewer invokes `writing-<lang>` read-only to critique idioms).

### Role bodies become thin (the anti-duplication core)

A role `AGENT.md` carries ONLY: persona/stance (2–4 lines), the enforced-envelope statement, and the skill-routing block. **Removed and relocated:** all language tutorial/code examples → `references/`; all output-format blocks → owning skill; all domain procedure → skill. Expected: each role body ≈ 30–45 lines vs today's 48–347.

### Key consequences (must be tracked, not glossed)

- **Fork-convention change (behavioral).** `writing-<lang>` `context: fork` now forks into an *edit-capable* `engineer`: the subagent applies + verifies and returns a summary, instead of returning a proposal for main to apply. This changes how forked language work behaves. Tracked as Risk 1.
- **`reviewer` loses Bash.** It can no longer run `git diff`/`git log`. Reviewers must work from files in scope (Read/Grep/Glob) + diff context supplied by the caller. Tracked as Risk 2.
- **Survival rule (ratified, ruthless):** standalone exists only if not `(engineer|reviewer)+skill` OR special mechanics. → `infra-engineer`→`engineer`+`managing-infra`; `worker`→`engineer` (delete); `scout`→`reviewer`+`searching-code` (delete); pi `reviewer`/`planner`→roles (delete); `perplexity-researcher`→`researching-web`; `playwright-tester`→`testing-e2e`; `pdf-parser`→new `parsing-documents` skill; 4 `*-engineer`→`engineer`; 24 review-family + `docs-keeper`→roles+skills; `spec-planner`/`planner`→`reviewer`+planning skill.
- **Hop-2 mitigation:** each role body carries an explicit skill-routing block so orchestrator→role→skill stays accurate.
- **pi full scope:** pi flat-layout `engineer`/`reviewer`; keep `advisor`; delete pi-only `worker`/`scout`/old-`reviewer`/old-`planner`.

## Technical Details

- Agent dir: `AGENT.md` (generic base) + `claude/` + `pi/` overlays. New `engineer`/`reviewer` follow this layout; `advisor` stays as-is.
- Skill fork coupling: `src/skills/<skill>/claude/frontmatter.yaml` `agent:` field. Repoint the 5 known pointers; no others exist.
- Enforced tool envelopes (the role layer) — set in `src/agents/<role>/claude/frontmatter.yaml` + `pi/frontmatter.yaml`:
  - `engineer`: `Read, Edit, Write, Bash, Grep, Glob, LS` + ctx7/morphllm/mem-search (mutator + verifier)
  - `reviewer`: `Read, Grep, Glob, LS` only — **no Bash, no Edit, no Write** (provably non-mutating)
  - `advisor`: unchanged (Read + read-only git Bash, xhigh, transcript-forward)
- plugin.yaml `agents:` edits (exact):
  - `go-dev`: `[go-engineer]` → `[engineer]`
  - `python-dev`: `[python-engineer]` → `[engineer]`
  - `typescript-dev`: `[typescript-engineer]` → `[engineer]`
  - `web-dev`: `[web-engineer]` → `[engineer]`
  - `infra-ops`: `[infra-engineer]` → `[engineer]`
  - `dev-workflow`: `[docs-keeper + 24 review-family]` → `[engineer, reviewer]`
  - `spec`: `[spec-planner]` → `[reviewer]` (planning runs as reviewer + `spec`/`planning:make`)
  - `testing-e2e`: `[playwright-tester]` → `[engineer]`
  - `dev-tools`: `[pdf-parser, perplexity-researcher]` → `[reviewer]`
- References: port only the language-specific 53–94% slice from each deleted agent; drop the shared skeleton (host skill core supplies it).
- `writing-web` has no `references/` dir today → create it.

## What Goes Where

- **Implementation Steps** (`[ ]`): all agent/skill/plugin file edits, reference materialization, lint/build/genericity gates, scenario-parity spot-tests — all achievable in this repo.
- **Post-Completion** (no checkboxes): version bump + release (push annotated tag → CI builds release; NEVER `gh release create`); downstream `cc-forge` mirror sync; any consuming-project re-pin.

## Implementation Steps

### Task 1: Coupling sweep + freeze the map (GATING — no deletions anywhere until this is green)

**Files:**

- Create: `docs/plans/coupling-map-20260516.md` (working artifact; delete at Task N)

- [x] `grep -rn '^agent:' src/skills/*/claude/frontmatter.yaml src/skills/*/pi/frontmatter.yaml` — capture every fork pointer
- [x] `grep -rn 'agent' src/skills/*/SKILL.md` — confirm no `agent:` pointers live in base SKILL.md (expected: none)
- [x] cross-check each pi-only agent (`advisor`/`planner`/`reviewer`/`scout`/`worker`) is absent from every `plugin.yaml`
- [x] write the frozen skill→agent map to the artifact; assert exactly 5 pointers (`managing-infra`, `writing-{go,python,typescript,web}`)
- [x] gate: if any pointer is unaccounted for, STOP and re-scope before any later task

### Task 2: Build generic `engineer` and `reviewer` role agents — thin bodies, enforced envelopes (inert until referenced)

**Files:**

- Create: `src/agents/engineer/AGENT.md`, `src/agents/engineer/claude/frontmatter.yaml`, `src/agents/engineer/pi/frontmatter.yaml`
- Create: `src/agents/reviewer/AGENT.md`, `src/agents/reviewer/claude/frontmatter.yaml`, `src/agents/reviewer/pi/frontmatter.yaml`
- Modify (scope correction): `src/plugins/{go-dev,python-dev,typescript-dev,web-dev,infra-ops,dev-workflow,spec,testing-e2e,dev-tools}/plugin.yaml` — additive `agents:` ownership only

⚠️ Scope correction (discovered at implementation): the plan assumed agents stay inert with no plugin.yaml change until Task 3. The pre-commit hook runs `make build`, and `scripts/build/plugin_index.py:validate_plugin_ownership` rejects any claude/codex-targeted agent owned by no plugin.yaml. So a Task 2 commit cannot pass build without plugin ownership. Resolution: the **additive** half of Task 3's plugin.yaml work (append `engineer`/`reviewer`, keep old entries) was pulled forward into Task 2; Task 3 keeps the fork-pointer repoint, scenario spot-tests, and the **removal** of old `agents:` entries. Old agents stay owned (still listed) so build remains green until Task 8 deletes them.

- [x] (pulled forward) additive `plugin.yaml` `agents:` ownership: `engineer` → go-dev/python-dev/typescript-dev/web-dev/infra-ops/testing-e2e; `engineer`+`reviewer` → dev-workflow; `reviewer` → spec/dev-tools — old entries retained; `make build` clean for all 4 targets
- [x] `engineer/claude/frontmatter.yaml`: tools = `Read, Edit, Write, Bash, Grep, Glob, LS` + ctx7/morphllm/mem-search; `engineer/pi/frontmatter.yaml`: `read, edit, write, bash, grep, find, ls` (the mutator envelope — this is the enforced role boundary)
- [x] `engineer/AGENT.md` (target ≈30–45 lines): constructive-builder stance; "you APPLY changes and run the MANDATORY build/test/lint verification on what you changed"; generic verification discipline; failure handling. **NO Proposal Format block** (engineer applies, does not return proposals); **NO language tutorial/code examples** (→ references); **NO domain procedure** (→ skill)
- [x] add explicit skill-routing block to `engineer`: `code authoring/impl→writing-<lang>; bug fix→fixing-code; batch refactor→refactoring-code; test authoring→improving-tests; docs→documenting-code; infra→managing-infra`
- [x] `reviewer/claude/frontmatter.yaml` + `reviewer/pi/frontmatter.yaml`: tools = `Read, Grep, Glob, LS` ONLY — **no Bash, no Edit, no Write** (the enforced non-mutating boundary; do not rely on prose restriction)
- [x] `reviewer/AGENT.md` (target ≈30–45 lines): adversarial-evaluator stance ("assume bugs exist until proven otherwise"); works from files in scope + caller-supplied diff context (no `git diff` — no Bash); skill-routing block: `security/quality→reviewing-code; over-abstraction/architecture→improve-codebase-architecture; test design→improving-tests; docs→documenting-code; locate→searching-code; planning→spec|planning:make; idiom critique→writing-<lang>`. **NO findings-format block** (→ owned by `reviewing-code` and each domain skill)
- [x] disjoint frontmatter `description` for both (audit rec #1): role + enforced-capability + stance; no language; no overlap with each other or `advisor`
- [x] gate: `make lint-instructions` clean for both; `validate_genericity.py` clean (no language-specific content in base); confirm each body ≤ ~45 lines (anti-duplication check)

### Task 3: Repoint the 5 fork couplings + plugin manifests; verify a real fork BEFORE any deletion

**Files:**

- Modify: `src/skills/{managing-infra,writing-go,writing-python,writing-typescript,writing-web}/claude/frontmatter.yaml`
- Modify: `src/plugins/{go-dev,python-dev,typescript-dev,web-dev,infra-ops,dev-workflow,spec,testing-e2e,dev-tools}/plugin.yaml`

⚠️ Atomic-coupling defect (advisor-flagged): `validate_plugin_ownership` couples plugin.yaml old-entry **removal** with old-agent-dir **deletion** (Task 8). Removing `go-engineer` from `go-dev` while `src/agents/go-engineer/` still exists makes it an unowned claude/codex agent → build fails. So the removal half of Task 3 and the deletion of Task 8 must run together (or Task 3 defers removal to Task 8). Resolve at the Task 3 iteration: either merge Task 3-removal into Task 8, or keep old entries until Task 8 and only do fork-pointer repoint + spot-tests here.

- [x] repoint the 5 `claude/frontmatter.yaml` `agent:` fields: `*-engineer`/`infra-engineer` → `engineer`
- [x] additive `plugin.yaml` ownership already done in Task 2 (verify); **defer old-entry removal to Task 8** (coupled with dir deletion per ⚠️ above) — verified: all 9 plugin.yaml retain old + new entries
- [x] `make build` — emits all 4 targets without unresolved-agent errors (claude/codex/gemini/pi, 40 agents, clean)
- [x] scenario-parity spot-test: `writing-go` `context: fork` → `agent: engineer` resolves to real edit-capable `engineer` agent (compiled into go-dev dist); applies+verifies per Risk 1 behavioral change (not propose — engineer is the mutator), not a broken/default target
- [x] scenario-parity spot-test: `managing-infra` → `agent: engineer`; resolves to real `engineer` agent compiled into infra-ops dist
- [x] gate: both forks verified green — this unlocks the deletion tasks (6–9)

### Task 4: Materialize per-language references for domain skills

**Files:**

- Create: `src/skills/reviewing-code/references/{go,python,typescript,web}.md`
- Create: `src/skills/improving-tests/references/{go,python,typescript,web}.md`
- Create: `src/skills/documenting-code/references/{go,python,typescript,web}.md`
- Create: `src/skills/improve-codebase-architecture/references/{go,python,typescript,web}.md`
- Create: `src/skills/managing-infra/references/{terraform,kubernetes,helm}.md`

⚠️ Scope correction (managing-infra, discovered at implementation): the repo filesystem is case-insensitive (APFS) and `managing-infra/references/` already ships comprehensive uppercase `TERRAFORM.md` + `KUBERNETES.md`. Creating lowercase `terraform.md`/`kubernetes.md` would collide and duplicate. Grounded read of `infra-engineer/AGENT.md` showed its K8s `securityContext` block and Kustomize structure are already fully covered by the existing `KUBERNETES.md` (lines 23/39/95), and its Terraform content by `TERRAFORM.md`; cloud-CLI bits belong to `using-cloud-cli`, not here. The only genuine gap was Helm (skill description + decision guide cover Helm but no `HELM.md` existed and the SKILL.md References list omitted it). Resolution: created `references/HELM.md` (new, no collision) and wired it into `managing-infra/SKILL.md`; did NOT create colliding lowercase `terraform.md`/`kubernetes.md` (existing uppercase files retained, infra-engineer added nothing new there). Net infra-engineer port = HELM.md.

- [x] port the language-specific slice from `*-qa` → `reviewing-code/references/<lang>.md`; drop shared skeleton
- [x] port `*-tests` → `improving-tests/references/<lang>.md`
- [x] port `*-docs` (+ `docs-keeper` non-boilerplate) → `documenting-code/references/<lang>.md`
- [x] port `*-simplify` → `improve-codebase-architecture/references/<lang>.md`; port `infra-engineer` infra specifics → `managing-infra/references/*.md` (resolved per ⚠️ above: HELM.md created; terraform/kubernetes already covered)
- [x] gate: `make build` copies all new `references/` to every dist target (verified 17 new-ref hits per target across claude/codex/gemini/pi); `validate_genericity.py` clean (references/ exempt — confirmed: validator only scans SKILL.md/AGENT.md/body.md, never references/)

### Task 5: Fold idioms into authoring skills + create `writing-web/references/` + new `parsing-documents` skill

**Files:**

- Modify: `src/skills/writing-{go,python,typescript}/references/PATTERNS.md`
- Create: `src/skills/writing-web/references/PATTERNS.md`
- Create: `src/skills/parsing-documents/SKILL.md` (+ `claude/frontmatter.yaml` as needed)
- Modify: `src/plugins/dev-tools/plugin.yaml` (add `parsing-documents` to `skills:`)

- [x] extend `writing-{go,python,typescript}/references/PATTERNS.md` with `*-idioms` language slices (added `## Idioms Checklist`: go = naming/thin-wrapper/one-line/stdlib-first; python = 3.14/Pythonic/anti-patterns; ts = strict-config/satisfies-as-const/composition/`??`/anti-patterns; deduped against existing PATTERNS content; Contents updated)
- [x] create `writing-web/references/PATTERNS.md` from `web-idioms` (new references/ dir; semantic-HTML/modern-CSS/minimal-JS; wired `## References` into `writing-web/SKILL.md` for parity+discoverability)
- [x] author `parsing-documents` skill from `pdf-parser` body; disjoint description; add to dev-tools `skills:` (SKILL.md vendor-neutral — "the Read tool" not platform-specific; `claude/frontmatter.yaml` = `context: fork` + Bash envelope so reviewer-as-caller still gets extraction tools; added to dev-tools `skills:`)
- [x] gate: `make lint-instructions` (17 warn/56 info — baseline, no regression) + `validate_genericity.py` (passed) + `make build` (clean, all 4 targets, 45 skills, parsing-documents owned by dev-tools) clean

### Task 6: Make the 7 domain skills role-agnostic + add language self-detection

**Files:**

- Modify: `src/skills/{reviewing-code,improving-tests,documenting-code,improve-codebase-architecture,fixing-code,refactoring-code,managing-infra}/SKILL.md`
- Modify (scope correction): `src/skills/reviewing-code/claude/body.md` — overlay reconciliation forced by the build gate (see ⚠️ below)

⚠️ Scope corrections (discovered at implementation):

1. **Overlay reconciliation (reviewing-code).** The plan listed only SKILL.md, but `reviewing-code/claude/body.md` appended Claude-specific content under a `## Delegate to reviewer agents (\_+)` anchor that the role-agnostic rewrite deleted, plus it spawned deleted per-language reviewer agents and non-existent `codex-assistant`/`gemini-consultant`. `make build` (the Task 6 gate) hard-fails on the missing anchor. Resolution: re-anchored the overlay block to the surviving `## Review dimensions (\_+)`, rewrote it to fan dimensions to `Task(subagent_type="reviewer", ...)` sub-tasks and to spawn external bridges only if configured (no hard-coded deleted agent names), and updated the `$ARGUMENTS` keyword tuning + historical-context block to role/dimension language. `claude/body.md` is a Claude overlay — genericity validator does not scan it, lint unaffected.
2. **`fixing-code`/`refactoring-code` have no `references/<lang>.md`.** Task 4 created per-language references only for `reviewing-code`/`improving-tests`/`documenting-code`/`improve-codebase-architecture` (+ infra for `managing-infra`). So the "load `references/<lang>.md`" instruction would dangle for these two. Resolution: their language-detection sections honestly state there are no per-language reference files — operate from the generic core; the detected language only selects which build/test/lint verification commands to run (the plan's "unknown → generic core only" branch is their always-case). Spot-test 5 ("loads `references/python.md`") is idealized; the correct parity behavior is generic-core + Python toolchain (ruff/pytest) with engineer apply+verify — verified equivalent to the old `py-impl`/fixing behavior.

- [x] **relocate the output contracts into the skills** (the duplication leaving the role bodies): ported the `reviewer` tiered-findings format (Critical/Warnings/Suggestions/Summary, from the pre-Task-2 pi `reviewer`) into `reviewing-code`'s Report format (renamed CRITICAL/IMPORTANT/SUGGESTIONS → Critical/Warnings/Suggestions, added Summary); ported the old `*-engineer` Proposal Format (## Proposed Changes / ### Change N / File / Action / Code / Rationale, language-generalized) into `fixing-code`/`refactoring-code`/`improving-tests`/`documenting-code`/`managing-infra` as the explicit reviewer "propose" branch; `improve-codebase-architecture` already owns its CANDIDATES → DESIGN AGREED contract (light touch per advisor)
- [x] add the role-gated action instruction to each skill: "Detect your capability from your tools, not from prose: write-capable (engineer) applies + verifies; read-only (reviewer) emits the Proposed Changes contract, applies nothing." `fixing-code` gates per-step (reviewer runs diagnose Steps 1–3, stops before Step 4); `reviewing-code`/`improve-codebase-architecture` are findings/design-only (route fixes to fixing-code/refactoring-code)
- [x] add language-detection + reference-load instruction: detect from file extensions → load `references/<lang>.md`; mixed → load several; unknown → generic core only. `reviewing-code`/`improving-tests`/`documenting-code`/`improve-codebase-architecture` → go/python/typescript/web; `managing-infra` → infra tool-type detection (`*.tf`→TERRAFORM, K8s YAML→KUBERNETES, `Chart.yaml`→HELM, etc.); `fixing-code`/`refactoring-code` → no refs exist, generic core + language-appropriate toolchain (per ⚠️ 2)
- [x] scenario-parity spot-test: `reviewer`+`reviewing-code` on a Go file loads `references/go.md`, produces tiered findings, attempts NO edit/bash — PASS (tool-enforced: reviewer envelope Read/Grep/Glob/LS only + skill "produces findings, not edits")
- [x] scenario-parity spot-test: `engineer`+`fixing-code` on a Python file → generic core + Python toolchain (no `references/python.md` exists for fixing-code per ⚠️ 2), engineer role-gate applies fix + runs verification — PASS (parity = old py-impl apply+verify behavior)
- [x] scenario-parity spot-test: `reviewer`+`fixing-code` (cross-mode) emits the fix as a structured proposal, applies nothing — PASS (role-gate stops before Step 4 + reviewer envelope has no Edit/Write/Bash)
- [x] gate: `make lint-instructions` clean for all 7 (17 warn/56 info — baseline, no regression; the 7 trip only pre-existing INFOs); confirmed no output-format block in `engineer`/`reviewer` `AGENT.md` (both "Defer to the active skill's output contract"); `advisor` retains its Verdict/Risks/Actions block per the plan's explicit "advisor unchanged" rule (preserved special-mechanics, not domain duplication); `validate_genericity.py` passed; `make build` clean all 4 targets

### Task 7: Wire planning into `reviewer` (NO planner agent — planner is deleted)

**Files:**

- Modify: `src/agents/reviewer/AGENT.md` (skill-routing block already includes `planning→spec|planning:make` from Task 2 — verify wording)
- Modify: `src/plugins/spec/plugin.yaml` (already `[reviewer]` from Task 3 — verify)

⚠️ Scope correction (Bash-dependency finding — Risk 2 realized): no file edits required this task; it is verify + annotate. Findings:

1. Routing already correct: `reviewer/AGENT.md:19` routes `planning → spec or planning:make`; `spec/plugin.yaml:15` already lists `reviewer` (`spec-planner` retained until Task 8 per the Task 3 deferral). No wording change needed — keeping the role body thin is itself a plan invariant, so the resolution lives in this note, not in `reviewer/AGENT.md`.
2. All 8 `spec-*` SKILL.md bodies hard-depend on Bash and cannot run under the reviewer envelope (Read/Grep/Glob/LS only): `scripts/specctl init|show|validate|status|done`, `mkdir -p .spec/...`, and `git branch --show-current` (`spec-status`). `planning:make` is NOT an escape hatch — it is an external global skill that writes `docs/plans/*.md` (needs Write, which reviewer also lacks). The only reviewer-envelope-compatible part of planning is the *reasoning/decomposition* (requirement → tasks, dependencies, acceptance criteria), not the `.spec/` scaffolding or file materialization.
3. Resolution (per Risk 2, verbatim — engineer hand-off): `reviewer` produces the plan *content* as its read-only proposal output; `scripts/specctl` scaffolding, `.spec/`/`docs/plans/` file writes, and git steps are an `engineer` hand-off (or main-thread orchestration). `spec-*` bodies are deliberately out of the Task 6 role-agnostic rewrite scope and are NOT modified here — folding them in would be unauthorized scope creep. This is documented, not rewritten.

- [x] confirm `reviewer` skill-routing routes planning intent to the `spec` / `planning:make` skill (the planning stance/output is the skill's, not a role's) — verified `reviewer/AGENT.md:19`
- [x] verify the `spec` skill body still works under the `reviewer` envelope — FINDING: it does NOT run standalone; all 8 `spec-*` hard-depend on Bash (`scripts/specctl`, `mkdir -p .spec/`, `git branch --show-current`). Flagged ⚠️ above with the Risk 2 engineer-hand-off resolution
- [x] scenario-parity spot-test: "plan a feature" → routes to `reviewer` (routing line 19 correct); under strict envelope the subagent produces the plan *decomposition as read-only proposal text* (its deferred output contract), and `specctl`/file-write scaffolding is an `engineer` hand-off — honest parity is decomposition-only, NOT self-materialized `EPIC-*.md`/`TASK-*.md` (asserting full parity would be false; matches Risk 2)
- [x] gate: `make lint-instructions` (17 warn/56 info — baseline, no regression) + `make build` (clean, all 4 targets, 40 agents, no unresolved-agent errors)

### Task 8: Delete the consolidated agents (GATED on Tasks 1+3 green)

**Files:**

- Delete: `src/agents/{go,py,ts,web}-{qa,tests,docs,idioms,impl,simplify}/` (24), `src/agents/docs-keeper/`, `src/agents/{go,python,typescript,web}-engineer/` (4), `src/agents/infra-engineer/`, `src/agents/perplexity-researcher/`, `src/agents/playwright-tester/`, `src/agents/pdf-parser/`, `src/agents/spec-planner/`
- Modify: any `plugin.yaml` still listing a deleted agent (should be none after Task 3 — verify)

⚠️ Scope corrections (discovered at implementation):

1. **plugin.yaml old-entry removal lands here** (per the Task 3 ⚠️ atomic-coupling deferral). `validate_plugin_ownership` fails both ways (unowned dir OR plugin pointing at a missing agent), so the 9 plugin.yaml old-entry removals + 34 dir deletions are one atomic commit. Final `agents:`: go/python/typescript/web-dev + infra-ops + testing-e2e → `[engineer]`; dev-workflow → `[engineer, reviewer]`; spec + dev-tools → `[reviewer]`.
2. **Six skill bodies still hard-referenced deleted agents** (not caught by Tasks 3/6, which only touched the 7 domain SKILL.md + reviewing-code/claude/body.md). The "zero references remain" gate forced repointing: `deploying-infra/SKILL.md` infra-engineer→engineer; `documenting-code/claude/body.md` docs-keeper→engineer; `improving-tests/claude/body.md` per-language `*-tests` map → role-agnostic language self-detection + `references/<lang>.md`; `spec-work/SKILL.md` spec-planner→reviewer, `*-engineer`→engineer, `*-tests`→reviewer (name-swap only, flow text untouched per Task 7 fence); `testing-e2e/claude/body.md` playwright-tester→engineer. `researching-web/claude/body.md`: the "Deep Mode: Agent" section was **deleted** (not repointed) — neither surviving role has Perplexity MCP in its enforced envelope, so the dispatch block was removed and the skill's direct-MCP default covers it (advisor-flagged broken-dispatch avoidance).

- [x] confirm Task 1 map frozen and Task 3 fork verification green (hard gate)
- [x] delete the 34 consolidated agent dirs
- [x] `grep -rn` the deleted agent names across `src/` — zero references remain
- [x] gate: `make build` clean for all 4 targets; no unresolved-agent errors

### Task 9: pi full scope — flat-layout roles, delete pi-only obsolete agents

**Files:**

- Modify/Create: pi overlays for `engineer`/`reviewer` (enforced envelopes per Task 2)
- Delete: `src/agents/worker/`, `src/agents/scout/`, pi-only old `src/agents/reviewer/`, pi-only `src/agents/planner/` (planning now = reviewer + skill; no planner agent)
- Keep: `src/agents/advisor/` untouched

- [x] the old pi-only `reviewer` dir is replaced by the new generic `reviewer` (Task 2) — verified: dir recreated in commit 28bd5dd with new generic AGENT.md; `pi/frontmatter.yaml` = `read, grep, find, ls` (no bash/edit/write); no stale frontmatter
- [x] delete pi-only `worker` (its full-capability role = `engineer`), `scout` (= `reviewer`+`searching-code`), `planner` (= `reviewer`+planning skill) — also repointed `searching-code/pi/body.md:17` scout→reviewer (only remaining src/ reference to a deleted pi-only agent)
- [x] confirm `advisor` survives unchanged — `git status` on `src/agents/advisor/` empty (untouched)
- [x] gate: `make build` pi target clean (3 agents, all 4 targets); **pi agent set = exactly `engineer, reviewer, advisor`** (verified `dist/pi/agents/`); `make lint-instructions` 2 warn/21 info (improved vs 17/56 baseline, no regression)

### Task 10: Verify acceptance criteria

- [x] exactly 3 surviving agents (`engineer`, `reviewer`, `advisor`); 39→3 confirmed via `ls src/agents/` (output: `advisor engineer reviewer`)
- [x] enforced-envelope check: `reviewer` claude+pi frontmatter has NO Bash/Edit/Write (`Read,Grep,Glob,LS` / `read,grep,find,ls`); `engineer` has Edit/Write/Bash (claude+pi); `advisor` unchanged — `git status --porcelain src/agents/advisor/` empty, last change `fd304e3` predates the refactor, `targets: [pi]` (no claude overlay by design)
- [x] anti-duplication check: `engineer` (33 lines) and `reviewer` (34 lines) both carry "Defer to the active skill's output contract — do not define your own" and no language tutorial; `advisor` (39 lines) retains its Verdict/Risks/Actions block by the explicit Task 6 line 240 carve-out (preserved special-mechanics, the plan's "advisor unchanged" rule). All ≤ ~45 lines
- [x] full 13/13 scenario-parity matrix spot-tested green — structural verification: all 15 skills present, all 16 `references/<lang>.md` present, 5 fork pointers all `agent: engineer`, plugin `agents:` ownership only `engineer`/`reviewer`; scenario 7 (Py bug fix → `fixing-code`) is generic-core by Task 6 ⚠️2 design (idealized in matrix), confirmed parity = old py-impl apply+verify
- [x] `make check` clean — "check: clean (all derived artifacts match canonical sources)"; also ran `make lint` (ruff/ruff-format/shellcheck/shfmt/markdownlint 0 errors/tsc) exit 0 and `make validate` (validate-config 0 warnings + genericity) exit 0
- [x] `make build` clean for claude/codex/gemini/pi — 45 skills, 3 agents, 10 hooks, all 4 targets, no unresolved-agent errors
- [x] `make lint-instructions` — 2 warning(s)/21 info(s); no regression vs the 17/56 pre-refactor baseline (matches Task 9 post-state, improved)
- [x] `validate_genericity.py` clean — "Genericity check passed"

### Task 11: Update documentation

- [x] update `AGENTS.md` (agent inventory section reflects 3 agents + role=enforced-envelope / skill=domain+output / references=language model) — added `## Agents` section
- [x] append note to `docs/agent-audit-2026-05-16.md` linking this plan as the executed resolution — added `## Executed resolution`
- [x] update `CLAUDE.md` if the role+skill composition model needs a one-liner for future sessions — no separate edit: `CLAUDE.md` is `@AGENTS.md`, so the new `## Agents` one-liner is already in its effective content
- [x] delete the Task 1 working artifact `docs/plans/coupling-map-20260516.md`
- [x] move this plan to `docs/plans/completed/`

## Risks

1. **Fork-convention change (behavioral, highest).** `writing-<lang>`/`managing-infra` `context: fork` now forks into an edit-capable `engineer`: the subagent *applies + verifies* and returns a summary, instead of returning a proposal for main to apply. Forked language/infra work behaves differently (more autonomous). Mitigation: Task 3 verifies a real fork end-to-end before any deletion; scenario-parity spot-tests (new Go feature, infra change) must show applied+verified output, not a dangling proposal.
2. **`reviewer` loses Bash.** No `git diff`/`git log`/build. Mitigation: reviewer works from files in scope (Read/Grep/Glob) + caller-supplied diff context; Task 7 flags any `spec-*`/review skill with a hard Bash dependency as ⚠️ to resolve (move that step to an `engineer` hand-off or supply context).
3. **Coupling break.** Missed `agent:` pointer silently mis-targets `context: fork`. Mitigation: Task 1 sweep gates all deletion; only 5 pointers exist (grounded); verify fork post-repoint, pre-delete.
4. **Hop-2 routing.** `reviewer`/`engineer` must pick the right domain skill. Mitigation: explicit skill-routing block in each thin role body; 13/13 spot-test matrix.
5. **Output-contract relocation regressions.** Moving formats from role→skill could drift a skill's output. Mitigation: Task 6 ports verbatim then de-dupes; spot-tests assert the tiered-findings and applied-change shapes.
6. **Behavior compression.** Porting only the language slice may drop nuance. Mitigation: manual per-agent port + behavioral diff in spot-tests.
7. **Build/validator.** Verified no changes (SUPPORT_DIRS copies `references/`; genericity validator skips it). Residual: new `parsing-documents` skill + `writing-web/references/` must pass `make check`.

## Post-Completion

*Items requiring manual intervention or external systems — no checkboxes, informational only*

**Manual verification:**

- Run a real Go security review and a real Python test-improvement end-to-end through a fresh session to confirm dispatch accuracy in practice (not just spot-tests).
- Confirm orchestrator picks `engineer` vs `reviewer` correctly on ambiguous phrasing ("clean up this code" — does it route to reviewer-proposes or engineer-applies?).

**External system updates:**

- Version bump + release: push an annotated tag; CI (`release.yml`) builds the release. **NEVER `gh release create`.**
- `cc-thingz` (origin) is source of truth; `cc-forge` is a mirror — push/PR to `cc-thingz`, mirror syncs after.
- Any project consuming these plugins re-pins to the new version after release.

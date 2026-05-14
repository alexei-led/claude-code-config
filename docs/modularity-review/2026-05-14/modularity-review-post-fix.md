# Modularity Review — Post-Fix

**Scope**: Pi hooks design after the three-commit refactor (`refactor(pi): split hook-runner...`, `feat(build): generate Pi hooks.json from meta.yaml`, `docs: add modularity review`). Comparison against [the original review](modularity-review.md) of the same surface.
**Date**: 2026-05-14

## Executive Summary

The refactor moved Pi hooks from a 1,540-line monolithic adapter to a seven-module package (`hook-runner/`) with a single Claude Code wire-format [anti-corruption layer](https://coupling.dev/posts/core-concepts/balance/) and a build-pipeline-derived Pi manifest. Six of the seven flagged issues are resolved; the seventh (Pi runtime API facade) was deliberately deferred under the [seam-discipline rule](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) that one consumer doesn't justify an adapter. Aggregate score across six modularity dimensions rose from **82/210 (39%)** to **181/210 (86%)** — a **+47-point absolute / +120% relative** improvement. No new critical issues introduced; three minor follow-ups noted for future passes.

## Scoring Method

Each integration is rated on six dimensions, 1 (worst) to 5 (best). Higher is better.

| Dimension          | What it measures                                                                                 |
| ------------------ | ------------------------------------------------------------------------------------------------ |
| **Encapsulation**  | Is the shared knowledge concentrated in one seam, or scattered?                                  |
| **Locality**       | Does adding a new field/feature require one edit or many?                                        |
| **Cohesion**       | Are related responsibilities grouped, unrelated ones separated?                                  |
| **Cognitive load** | Can a contributor reason about the integration without holding the whole codebase in their head? |
| **Testability**    | Can the integration be exercised without mocking the world?                                      |
| **Change safety**  | Does the type system / structure flag divergence at compile time?                                |

Per-integration totals are out of 30. The aggregate is out of 210 (7 integrations × 30).

## Per-Integration Scoring

### Issue 1 — Claude Code wire protocol [anti-corruption layer](https://coupling.dev/posts/core-concepts/balance/)

| Dimension      | Before |  After |       Δ | Evidence                                                                                                                                                                   |
| -------------- | -----: | -----: | ------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------- |
| Encapsulation  |      1 |      5 |      +4 | `hookSpecificOutput` / `permissionDecision` / legacy `approve                                                                                                              | block`mapping appear in **only**`cc-protocol.ts`(14 references).`dispatch.ts`and`index.ts` no longer mention CC field names. |
| Locality       |      1 |      5 |      +4 | New CC field → one-file edit in `cc-protocol.ts`.                                                                                                                          |
| Cohesion       |      2 |      5 |      +3 | Four parser functions grouped with their shared helpers (`parseJsonObject`, `hookSpecificOutput`, `stringField`) and the `blockingError` / `plainTextContext` conventions. |
| Cognitive load |      2 |      4 |      +2 | 184-line file is a complete CC-spec reference.                                                                                                                             |
| Testability    |      2 |      5 |      +3 | Pure functions: `decodePreToolUse(stdout) → PreToolUseDecision`. No Pi context required.                                                                                   |
| Change safety  |      1 |      4 |      +3 | Closed discriminated unions (`PreToolPermission`, `PermissionRequestDecision`, etc.) — invalid values rejected at parse time.                                              |
| **Total**      |  **9** | **28** | **+19** | (+63 percentage points)                                                                                                                                                    |

**Severity transition**: Critical → resolved.

### Issue 2 — Pi defaults derived from `meta.yaml`

| Dimension      | Before |  After |       Δ | Evidence                                                                                                                                                                         |
| -------------- | -----: | -----: | ------: | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Encapsulation  |      2 |      5 |      +3 | Single source of truth: `src/hooks/<name>/meta.yaml`. Third-party commands live in their own boundary file (`hooks-external.json`).                                              |
| Locality       |      1 |      5 |      +4 | New bundled hook → drop `src/hooks/<name>/{hook.*,meta.yaml}`; Pi entry generated automatically by `compile_hook._build_pi`.                                                     |
| Cohesion       |      2 |      5 |      +3 | Per-target shapes are derivations of one intent (`EVENT_MAP[event][target]`).                                                                                                    |
| Cognitive load |      3 |      4 |      +1 | `pi:` block is opt-in; default is "Pi gets the same wiring as Claude unless told otherwise."                                                                                     |
| Testability    |      3 |      5 |      +2 | Four new pytest cases: `test_pi_manifest_from_meta_yaml`, `test_pi_manifest_merges_external`, `test_pi_manifest_honors_pi_async`, `test_pi_manifest_honors_pi_timeout_override`. |
| Change safety  |      1 |      4 |      +3 | `load_hook` validates `pi.async: bool` / `pi.timeout: positive int`; mismatched events fail at build time.                                                                       |
| **Total**      | **12** | **28** | **+16** | (+53 percentage points)                                                                                                                                                          |

**Severity transition**: Significant → resolved.

### Issue 3 — Outer-wait / per-entry timeout invariant

| Dimension      | Before |  After |       Δ | Evidence                                                                                                                                                                                                                                    |
| -------------- | -----: | -----: | ------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Encapsulation  |      1 |      4 |      +3 | Pi-specific timeout declared in `meta.yaml` (`pi: { timeout: 1740 }`), with a multi-line comment explaining the 60-second margin. Default outer-wait formula in `hook-bridge.ts` (`timeoutSec*1000 + SYNTHETIC_HOOK_OUTER_WAIT_MARGIN_MS`). |
| Locality       |      1 |      4 |      +3 | Changing the policy → edit one `meta.yaml` block.                                                                                                                                                                                           |
| Cohesion       |      2 |      4 |      +2 | Timeout policy lives next to the event definition.                                                                                                                                                                                          |
| Cognitive load |      1 |      4 |      +3 | The "why 1740s" rationale is in the file that owns the value.                                                                                                                                                                               |
| Testability    |      2 |      4 |      +2 | `test_pi_manifest_honors_pi_timeout_override` + retained outer-wait test in `plan-mode/index.test.ts`.                                                                                                                                      |
| Change safety  |      1 |      3 |      +2 | Default formula prevents the silent-fail-open case; explicit caller-supplied `timeoutMs` is still honored verbatim (intentional, for short interactive deadlines like permission-gate's 2s).                                                |
| **Total**      |  **8** | **23** | **+15** | (+63 percentage points)                                                                                                                                                                                                                     |

**Severity transition**: Significant → resolved (with one residual: explicit `timeoutMs < timeoutSec*1000` is still a valid configuration — relied upon by permission-gate, but a hostile bundled-hook author could exploit it).

### Issue 4 — `hook-runner.ts` god module

| Dimension      | Before |  After |       Δ | Evidence                                                                                                                                                     |
| -------------- | -----: | -----: | ------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| Encapsulation  |      2 |      5 |      +3 | Seven sub-modules, each owning one concern: `types`, `config`, `cc-protocol`, `dispatch`, `instructions`, `ui`, `index`.                                     |
| Locality       |      2 |      4 |      +2 | New synthetic event → `index.ts` (dispatcher branch) + `dispatch.ts` (new aggregator if event uses a novel rank rule). Down from five locations in one file. |
| Cohesion       |      1 |      5 |      +4 | Instruction-file discovery lives in its own 54-line file, not adjacent to permission-decision parsers.                                                       |
| Cognitive load |      1 |      5 |      +4 | Largest module is `index.ts` at 533 lines (Pi event handlers); `cc-protocol` 184, `dispatch` 327, `config` 362, others under 160.                            |
| Testability    |      3 |      4 |      +1 | Modules importable in isolation; full test split not yet done (existing `hook-runner.test.ts` still loads the whole extension).                              |
| Change safety  |      2 |      4 |      +2 | TypeScript imports make dependencies explicit; module-level `_config` cache is the only shared mutable state and lives in `config.ts`.                       |
| **Total**      | **11** | **27** | **+16** | (+53 percentage points)                                                                                                                                      |

**Severity transition**: Significant → resolved.

### Issue 5 — Pi runtime API surface (deferred)

| Dimension      | Before |  After |      Δ | Evidence                                                                                                                    |
| -------------- | -----: | -----: | -----: | --------------------------------------------------------------------------------------------------------------------------- |
| Encapsulation  |      2 |      3 |     +1 | `sendHookMessageToAgent` (the steer/followUp/notify ladder) is one named function in `index.ts` instead of inline-repeated. |
| Locality       |      2 |      3 |     +1 | Channel name centralized (`HOOK_RUNNER_INVOKE_CHANNEL`); ladder is one function.                                            |
| Cohesion       |      3 |      3 |      0 | No deliberate change.                                                                                                       |
| Cognitive load |      2 |      3 |     +1 | Smaller surrounding file makes the ladder easier to spot.                                                                   |
| Testability    |      3 |      3 |      0 | No deliberate change.                                                                                                       |
| Change safety  |      1 |      2 |     +1 | `try/catch` ladder still hides Pi-side rename of `deliverAs: "steer"` — but at one site.                                    |
| **Total**      | **11** | **17** | **+6** | (+20 percentage points)                                                                                                     |

**Severity transition**: Significant → significant (deliberately deferred). Per the architecture-review skill's [seam discipline](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) ("one adapter = hypothetical seam"), a `pi-runtime.ts` facade for one consumer is indirection without [locality](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) benefit. **Promote to "do it" when a second consumer of the ladder appears or Pi pre-1.0 → 1.0 lands.**

### Issue 6 — `HookEntry` wire-vs-runtime split

| Dimension      | Before |  After |       Δ | Evidence                                                                                                                                      |
| -------------- | -----: | -----: | ------: | --------------------------------------------------------------------------------------------------------------------------------------------- |
| Encapsulation  |      2 |      5 |      +3 | `HookEntryConfig` (parsed JSON shape) vs `HookEntryRuntime` (`{ config, source, disabled }`) declared in `types.ts`.                          |
| Locality       |      3 |      5 |      +2 | Wire-format addition → `HookEntryConfig`; runtime tag addition → `HookEntryRuntime`. Compiler enforces the right lifecycle.                   |
| Cohesion       |      2 |      5 |      +3 | Each type has one purpose.                                                                                                                    |
| Cognitive load |      3 |      5 |      +2 | Reader can't confuse "comes from JSON" with "computed during load".                                                                           |
| Testability    |      3 |      4 |      +1 | Test fixtures construct `HookEntryRuntime` explicitly — no implicit-default tags.                                                             |
| Change safety  |      2 |      5 |      +3 | Type system catches attempts to serialize a `HookEntryRuntime` as wire content (the original `_source` underscore-prefix convention is gone). |
| **Total**      | **15** | **29** | **+14** | (+47 percentage points)                                                                                                                       |

**Severity transition**: Minor → resolved.

### Issue 7 — `TOOL_NAME_MAP` consolidation

| Dimension      | Before |  After |       Δ | Evidence                                                                                                                                                            |
| -------------- | -----: | -----: | ------: | ------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| Encapsulation  |      2 |      5 |      +3 | Map + `toCcToolName` live in `hook-bridge.ts` alongside the [contract](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) that uses CC names. |
| Locality       |      2 |      5 |      +3 | New Pi tool → one entry in `TOOL_NAME_MAP`.                                                                                                                         |
| Cohesion       |      3 |      5 |      +2 | Mapping next to its consumers — the synthetic-event channel + every extension that emits CC-named tool events.                                                      |
| Cognitive load |      3 |      5 |      +2 | One call site: `toCcToolName("bash")`.                                                                                                                              |
| Testability    |      4 |      5 |      +1 | Existing table-driven test in `hook-runner.test.ts` covers every registered name.                                                                                   |
| Change safety  |      2 |      4 |      +2 | Underscored names without explicit registration return as-is (no silent `Read_url` inference) — failure is loud, not invisible.                                     |
| **Total**      | **16** | **29** | **+13** | (+45 percentage points)                                                                                                                                             |

**Severity transition**: Minor → resolved.

## Aggregate Score

| Integration                                                                                    |       Before |         After |          Δ |
| ---------------------------------------------------------------------------------------------- | -----------: | ------------: | ---------: |
| 1. CC wire protocol [anti-corruption layer](https://coupling.dev/posts/core-concepts/balance/) |            9 |            28 |        +19 |
| 2. Pi defaults from `meta.yaml`                                                                |           12 |            28 |        +16 |
| 3. Outer-wait timeout invariant                                                                |            8 |            23 |        +15 |
| 4. `hook-runner.ts` god module                                                                 |           11 |            27 |        +16 |
| 5. Pi runtime API (deferred)                                                                   |           11 |            17 |         +6 |
| 6. `HookEntry` wire/runtime split                                                              |           15 |            29 |        +14 |
| 7. `TOOL_NAME_MAP` consolidation                                                               |           16 |            29 |        +13 |
| **Total**                                                                                      | **82 / 210** | **181 / 210** |    **+99** |
| **Percentage**                                                                                 |      **39%** |       **86%** | **+47 pp** |

The largest absolute gain is **Issue 1 (+19)** — the [model-coupled](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) imitation of an unowned external spec was the most expensive to leave alone. Issues 2 and 4 (+16 each) close a close second, both delivering a tractable [locality](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) gain by replacing hand-maintained derivative state with a single source of truth.

## Balance Rule Re-Check

For each integration, apply [`BALANCE = (STRENGTH XOR DISTANCE) OR NOT VOLATILITY`](https://coupling.dev/posts/core-concepts/balance/) to the post-refactor state.

| Integration                                                                            | Strength                                                                                                                                                                                                         | Distance                   | Volatility | Balanced?                                                                                 |
| -------------------------------------------------------------------------------------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | -------------------------- | ---------- | ----------------------------------------------------------------------------------------- |
| `dispatch` → `cc-protocol` (decoded decision API)                                      | [Contract](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/)                                                                                                                              | Same module                | Medium     | Yes                                                                                       |
| `cc-protocol` → CC wire spec (encapsulated imitation)                                  | [Model](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/)                                                                                                                                 | External vendor            | High       | Yes — strength is now confined to one file, so high-distance/high-volatility is tolerable |
| `compile_hook` → `meta.yaml`                                                           | [Contract](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) (validated schema)                                                                                                           | Same repo, same build step | Medium     | Yes                                                                                       |
| `hook-runner/index.ts` → Pi runtime API                                                | [Model](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) / [Intrusive](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) where it depends on `deliverAs` fallback | External npm package       | High       | **No** — deferred, see Issue 5                                                            |
| `permission-gate` / `plan-mode` → `hook-bridge.ts` (toCcToolName, invokeSyntheticHook) | [Contract](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/)                                                                                                                              | Same package               | Medium     | Yes                                                                                       |
| `hook-runner/config.ts` → file system (hooks.json paths)                               | [Functional](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) (knows Pi's settings layout)                                                                                               | Same module                | Medium     | Yes                                                                                       |
| `invokeSyntheticHook` outer wait ↔ per-entry timeout                                   | [Contract](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) (default formula in code)                                                                                                    | Same module                | Medium     | Yes                                                                                       |

Six of seven post-refactor integrations satisfy the balance rule. The remaining imbalance (Pi runtime API) is intentional, documented, and triggered only by external vendor churn that has not yet happened.

## New / Residual Issues

Three minor findings emerged from the post-fix walk. None blocks merge; all should be tracked.

### Residual A — `permission-gate` can starve the outer wait

**Severity**: Minor.
`invokeSyntheticHook` now derives the outer-wait floor from `timeoutSec`, but `permission-gate` explicitly passes `timeoutMs: 2000` to keep the interactive prompt responsive. That value is honored verbatim — which is correct for permission-gate but means a hostile bundled-hook author could ship a `timeoutSec: 60` PermissionRequest hook and watch the outer wait fire at 2s, returning a fail-closed deny regardless of what the hook would have decided.

The current behavior is what permission-gate wants. The latent risk: if a _different_ extension copies permission-gate's pattern without thinking about the trade-off, it'll fail closed prematurely. Documentable in `hook-bridge.ts`; not worth a code change today.

### Residual B — `hooks-external.json` is a build input that looks like a runtime config

**Severity**: Minor.
The new `src/pi-extensions/hooks-external.json` is consumed only by `compile_hook._build_pi` and excluded from `dist/` by `compile_pi_extension._BUILD_INPUT_FILES`. A reader who skims `src/pi-extensions/` will assume it's a runtime-loaded config (sibling to TypeScript modules) and be wrong. Consider relocating to `src/hooks/external.json` (next to the per-hook directories it conceptually extends) or `scripts/build/pi-hooks-external.json` (next to the script that reads it). Not urgent.

### Residual C — `hook-runner.test.ts` depends on `make build` having run

**Severity**: Minor.
The test now reads `dist/pi/extensions/hooks.json` for its bundled-config fixture. Pre-push hooks and CI always rebuild before testing, but a developer running `bun test src/pi-extensions/` after `git pull` without `make build` will get a stale or missing fixture. The pre-commit hook already runs build; this is a documentation gap, not a test-correctness gap. A guard in the test that prints "run `make build` first" if the file is missing would close the loop.

## What's Next

In rough order of leverage:

1. **Promote Issue 5** when a second consumer of the Pi message-delivery ladder appears, or Pi 1.0 lands.
2. **Split `hook-runner.test.ts`** to mirror the new module layout — one test file per sub-module — so each module's `Testability` score reaches 5/5.
3. **Address Residual B** — relocate `hooks-external.json` to make its build-time role obvious.
4. **Lock the timeout contract** — promote the `timeoutMs >= timeoutSec*1000 + margin` invariant from a default to a runtime assertion (Residual A) once external bundled-hook authors are a realistic threat model.

---

_This analysis was performed using the [Balanced Coupling](https://coupling.dev) model by [Vlad Khononov](https://vladikk.com)._

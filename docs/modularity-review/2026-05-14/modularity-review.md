# Modularity Review

**Scope**: Pi hooks design — `src/pi-extensions/hook-runner.ts`, `hook-bridge.ts`, `hooks.json`, consuming extensions (`permission-gate`, `plan-mode`), the cross-target build pipeline (`scripts/build/compile_hook.py`), and the user-space hook scripts under `src/hooks/*`.
**Date**: 2026-05-14

## Executive Summary

cc-thingz packages a Pi extension (`hook-runner`) that bridges Pi's native runtime events to Claude Code-compatible hook scripts so the same `src/hooks/*` artefacts run unchanged on Pi, Claude Code, Codex, and Gemini. The current design has a clean inter-extension contract (`hook-bridge.ts`) and a sensible "data, not code" wiring (`hooks.json`), but three layers absorb too much: `hook-runner` is a 1,540-line module holding ten responsibilities; Pi defaults are hand-maintained in `hooks.json` while every other target derives them from `src/hooks/<name>/meta.yaml`; and the Claude Code wire protocol — owned by Anthropic and still evolving — is duplicated by imitation inside the parser with legacy fallbacks already accreted. The system is healthy enough to ship today, but the modularity is unbalanced where it matters most: the parts that change most often (CC protocol shape, Pi runtime API surface, bundled wiring) are precisely the parts most tightly bound to a single file. Most important finding: the [model coupling](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) to the unowned Claude Code hook protocol is the largest source of future churn, and it currently has no anti-corruption layer.

## Coupling Overview

| Integration                                                                                               | [Strength](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/)                                                                                                                                         | [Distance](https://coupling.dev/posts/dimensions-of-coupling/distance/) | [Volatility](https://coupling.dev/posts/dimensions-of-coupling/volatility/) | [Balanced?](https://coupling.dev/posts/core-concepts/balance/) |
| --------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- | ----------------------------------------------------------------------- | --------------------------------------------------------------------------- | -------------------------------------------------------------- |
| `hook-runner` → Claude Code hook protocol (external spec, imitated)                                       | [Model](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/)                                                                                                                                            | High (foreign vendor, no contract)                                      | High                                                                        | No — critical                                                  |
| `hook-runner` → Pi runtime API (`pi.on`, `ExtensionContext`, `deliverAs`)                                 | [Model](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) / [Intrusive](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) where it depends on undocumented fallback semantics | High (npm dep, external team)                                           | High (Pi is pre-1.0)                                                        | No — significant                                               |
| `hooks.json` (Pi defaults) ↔ `src/hooks/<name>/meta.yaml` + `compile_hook.EVENT_MAP`                      | [Functional](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) (duplicated wiring inventory)                                                                                                         | Different files / formats / build paths                                 | Medium (every new bundled hook touches both)                                | No — significant                                               |
| `plan-mode` outer wait ↔ `hooks.json` `ExitPlanMode` `timeout` entry                                      | [Intrusive](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) (implicit cross-file ordering invariant)                                                                                               | Different files, same release                                           | High (already caused a fix in this branch)                                  | No — significant                                               |
| `hook-runner` internals (config IO, `/hooks` TUI, output parsers, event handlers, instructions discovery) | Low [strength](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/), same file → [low cohesion](https://coupling.dev/posts/core-concepts/balance/)                                                      | Zero (one file)                                                         | Medium                                                                      | No — minor (cognitive cost)                                    |
| `HookEntry` shape: wire format + view model + runtime state (`_source`, `_disabled`)                      | [Intrusive](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/)                                                                                                                                        | Zero (one module)                                                       | Low                                                                         | No — minor                                                     |
| `hook-bridge.ts` (synthetic event contract) ↔ `permission-gate`, `plan-mode`                              | [Contract](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) (discriminated unions, named channel)                                                                                                   | Same extension package, co-deployed                                     | Medium                                                                      | Yes — exemplar                                                 |
| `revdiff-plan-review.py` → revdiff-planning (third-party Claude plugin)                                   | [Model](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) (imitates Claude env: `CLAUDE_PLUGIN_ROOT`, etc.), guarded by fail-open                                                                    | High (separate package, separate maintainer)                            | Low–medium                                                                  | Yes — tolerable via fail-open                                  |
| Hook scripts (`src/hooks/<name>/hook.*`) ↔ `hook-runner` (JSON stdin / exit code / stdout)                | [Contract](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/)                                                                                                                                         | Process boundary, same repo                                             | Low                                                                         | Yes                                                            |

## Issue: Claude Code wire protocol is duplicated by imitation, with no anti-corruption layer

**Integration**: `hook-runner` → Claude Code hook spec (external, unowned)
**Severity**: Critical

### Knowledge Leakage

`hook-runner.ts` carries a full second copy of Claude Code's hook output protocol: `hookSpecificOutput.hookEventName`, `permissionDecision` (`allow|ask|deny|defer`), legacy `decision` (`approve|block`) with rewrite rules at lines 451–453, `permissionDecisionReason` with two-level fallback (`reason` → `parsed.reason`), `additionalContext`, `updatedInput`, plus per-event variants for `PermissionRequest`, `PermissionDenied`, and the generic decision shape. The exit code semantics (`2` = block, stderr carries the reason, stdout=JSON OR free text depending on whether `parseJsonObject` returns), the decision rank order (`allow < ask < defer < deny` at lines 775–780), and the "approve→allow / block→deny" legacy migration are all hard-coded in this file. None of this is owned by cc-thingz — it is reverse-engineered from Anthropic's hook documentation. There is no single module that says "this is the CC v1 wire format"; the same field names are read at half a dozen unrelated parse sites.

### Complexity Impact

Each new Claude Code hook feature — new event, new decision shape, new `hookSpecificOutput` field, new failure mode — forces edits across `parsePreToolUseOutput`, `parsePermissionRequestOutput`, `parsePermissionDeniedOutput`, `parseDecisionOutput`, plus the per-event branches inside `cc-hooks:invoke` (lines 1146–1175). A reader who has not internalised CC's hook spec cannot predict what stdout will be accepted. The legacy-name rewriting (already two layers deep) is a leading indicator of [unpredictable change outcomes](https://coupling.dev/posts/core-concepts/complexity/): an incoming "approve" string is silently rewritten to "allow", but only inside `parsePreToolUseOutput` — not inside `parseDecisionOutput`. That asymmetry is invisible from the call site.

### Cascading Changes

Three concrete scenarios:

1. Claude Code adds a fifth `permissionDecision` value (e.g. `redirect`). At minimum every `parse*` function plus the rank table plus the `cc-hooks:invoke` branches needs to be edited, and the synthetic-bridge type union in `hook-bridge.ts` must learn the new value. There is no compile-time signal pointing at the call sites that need updating.
2. CC tightens semantics so that `decision: "block"` only counts on `PostToolUse`. Today's code accepts it everywhere via `parseDecisionOutput`, which would now leak a CC-side detail into Pi behaviour.
3. A user writes a hook script that emits `{"hookSpecificOutput": {"hookEventName": "PostToolUse", ...}}` for a `PreToolUse` invocation. The guard at lines 437–441 silently discards the payload — the script author has no feedback loop, and the failure is invisible.

### Recommended Improvement

Introduce a single CC-protocol [anti-corruption layer](https://coupling.dev/posts/core-concepts/balance/) — e.g. `src/pi-extensions/cc-protocol/` — that exposes one entry point per hook event:

```ts
// cc-protocol/index.ts
export function decode(eventName: HookEventName, stdout: string, stderr: string, exitCode: number): HookDecision { … }
```

`HookDecision` is a closed discriminated union owned by cc-thingz, not Anthropic. `hook-runner` then talks only to `HookDecision` — no `permissionDecision` string, no `hookSpecificOutput` reaching the dispatcher. The legacy-name rewriting, the rank table, the "stderr-as-reason" rule, and the JSON-or-plain-text stdout fallback all live behind that seam. Adding a new CC field becomes a one-file change; the parser becomes independently testable; the [contract coupling](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) with the rest of `hook-runner` replaces the model coupling with Anthropic's spec.

Trade-off: one extra file and one extra type. The cost is genuinely low because the imitation already exists — this only relocates it. The win is that every future CC spec movement becomes a [contract-coupling](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) change at a single seam instead of a fan-out across the file.

## Issue: Pi default wiring is duplicated between `meta.yaml` and `hooks.json`

**Integration**: `src/hooks/<name>/meta.yaml` + `compile_hook.EVENT_MAP` ↔ `src/pi-extensions/hooks.json`
**Severity**: Significant

### Knowledge Leakage

For Claude, Codex, and Gemini, the build pipeline derives manifests automatically from `meta.yaml` via `EVENT_MAP` in `compile_hook.py:54–105`. For Pi, the same wiring is maintained by hand in `src/pi-extensions/hooks.json`: `session-start.py`, `skill-enforcer.sh`, `file-protector.py`, `git-guardrails.sh`, `revdiff-plan-review.py`, `smart-lint.sh`, `test-runner.sh`, `notify.sh` are all listed twice — once in `src/hooks/<name>/meta.yaml`, once in `hooks.json`. Worse, the `${PI_HOOKS_DIR}` placeholder, per-entry timeouts, and `async` flags are an entirely Pi-specific shape that is _only_ spelled out in `hooks.json` even though the same information could be `meta.yaml.timeout` plus a `pi.async` flag.

### Complexity Impact

A reasonable developer adding a new bundled hook for Pi must (a) drop a `src/hooks/foo/hook.sh` with `meta.yaml`, (b) wait for `compile_hook` to emit `dist/{claude,codex,gemini}/...` manifests, and (c) remember to _also_ hand-edit `src/pi-extensions/hooks.json`. Step (c) is invisible from step (a). Forgetting it produces a hook that fires on three targets and silently no-ops on Pi.

### Cascading Changes

1. Renaming a hook script: must edit `src/hooks/<old>/meta.yaml` → `<new>/`, and grep-replace inside `hooks.json` (no compile-time check).
2. Adding a new event kind (e.g. `Setup`): requires updating `EVENT_MAP` for the other three targets and inventing a new entry in `hooks.json` from scratch. The Pi side is the only target whose wiring is not derived from a single source of truth.
3. Changing a default timeout: same diff applied in two places.

### Recommended Improvement

Extend `compile_hook.EVENT_MAP` with a `pi` column (today it has `claude`, `codex`, `gemini`). Have `compile_hook` emit `dist/pi/extensions/hooks.json` the same way it emits Claude/Codex/Gemini manifests, from `meta.yaml` + the source-event mapping. `meta.yaml` gains optional `pi.async: true` and `pi.matcher: "..."` fields where the Pi mapping needs them (only `notify` and `ccgram` today). Delete the hand-maintained `src/pi-extensions/hooks.json`; keep its successor as a generated artefact under `dist/`. The bundled-config loader in `hook-runner.ts:314–323` keeps reading the same path.

Trade-off: a small amount of build-pipeline code (~30 lines, mirroring `_build_claude`). In exchange the Pi default wiring stops being a [functionally-coupled](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) hand-edit and joins the other three targets' derive-from-`meta.yaml` discipline.

## Issue: Outer-wait and per-entry timeout are an implicit cross-file invariant

**Integration**: `plan-mode/index.ts:168` (30-minute outer wait) ↔ `hooks.json` `ExitPlanMode.timeout: 1740` (s)
**Severity**: Significant

### Knowledge Leakage

`invokeExitPlanHook` waits 30 minutes for `hook-runner` to call back; the `revdiff-plan-review` entry inside `hooks.json` has a 1740-second (29-minute) per-hook timeout. The invariant — _per-entry timeout must fire first, otherwise the outer wait treats a stuck hook as approval_ — is not encoded anywhere. It lives only in the comment at `plan-mode/index.ts:160–164`. The same invariant was reportedly broken once already (the misalignment between `revdiff-plan-review.py`'s `subprocess.timeout=1740` and the hook-runner outer wait was the subject of recent fixes in this branch).

### Complexity Impact

Whoever edits `hooks.json` to raise the `ExitPlanMode` timeout (a perfectly reasonable user customisation, since the whole point is to give the human time to annotate the plan) silently breaks the fail-closed property: hook-runner returns to the outer wait, which fires at 30 minutes regardless, and the plan goes through. The author of the change has no signal that they crossed an invariant boundary.

### Cascading Changes

1. Any user with a slow plan-review workflow who bumps the hook timeout above 29 minutes opens a silent fail-open hole.
2. Adding a second long-running synthetic hook (e.g. an interactive code-review hook) requires re-deriving the same constraint from scratch.
3. Reducing the outer wait (perfectly sensible if the hook is short-lived) breaks revdiff plan review with no compile-time signal.

### Recommended Improvement

Push the invariant into `hook-bridge.ts`. The synthetic-call API already accepts `timeoutSec` (per-subprocess) and `timeoutMs` (outer wait); have `invokeSyntheticHook` enforce `timeoutMs >= timeoutSec * 1000 + margin` and have hook-runner expose the effective per-entry timeout it will use so the caller can compute the outer wait dynamically (e.g. `outerMs = perEntryTimeoutSec * 1000 + 30_000`). Alternatively, eliminate the outer wait entirely for events where hook-runner has its own per-entry timeout — the caller waits unconditionally, hook-runner is the single timeout authority. Either way the invariant becomes structural, not lore.

Trade-off: a few lines of API contract change. The current shape works as long as nobody touches the timeouts; the proposed shape works as long as `hook-bridge.ts` is the only place anyone needs to read.

## Issue: `hook-runner.ts` is a god module

**Integration**: Internal — `hook-runner.ts` (1,540 lines)
**Severity**: Significant (cognitive cost; will become Critical as the module accrues more synthetic events)

### Knowledge Leakage

A single file owns: (1) config discovery, validation, and merge across four file paths, (2) the `/hooks` interactive TUI with toggle/edit subcommands, (3) the synthetic-bridge event-bus listener, (4) ten Pi runtime event handlers, (5) four hook-output parsers for distinct CC payload shapes, (6) common stdin builders, (7) tool-name normalisation, (8) the disable-list and `_source` tagging machinery, (9) instruction-file discovery (AGENTS.md / CLAUDE.md / `.claude/rules/*.md`), and (10) subprocess execution with timeout/async handling. These responsibilities are connected only by happening to live in the same Pi extension entry point. Several of them — instruction discovery, the `/hooks` TUI, the disable-list — have low [integration strength](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) with the rest and would be more legible elsewhere.

### Complexity Impact

The file routinely exceeds the [4±1 cognitive budget](https://coupling.dev/posts/core-concepts/complexity/): a contributor adding a new synthetic event must understand the parser layer, the dispatcher rank rules, the `loadConfig` cache invalidation rule, and the `cc-hooks:invoke` routing — none of which are visibly related to the new event. Test files are already 561 lines for hook-runner and 213 for plan-mode, and they continue to grow.

### Cascading Changes

Adding a new event kind today touches: the `CORE_HOOK_EVENT_NAMES` array, the `HooksConfig` interface, the parser (a new `parse*Output` function), the synthetic-bridge dispatch switch, and probably a new event handler. Five locations in the same file, none of which the type system links together. A new contributor cannot identify "the parser layer" by looking at the directory.

### Recommended Improvement

Split along the existing seams. Suggested layout:

- `hook-runner/config.ts` — `loadConfig`, `extractHooksConfig`, `applyDisabled`, `tagEntries`, `hooksSummary`. Owns the four config-file paths and the disable-list.
- `hook-runner/cc-protocol.ts` — the parsers (per the first issue).
- `hook-runner/dispatch.ts` — `runPreToolUseGroups`, `runPermissionRequestGroups`, `runPermissionDeniedGroups`, `runDecisionHooks`, `runHook`, `runHookAsync`.
- `hook-runner/instructions.ts` — `discoverInstructionFiles` (it has no business being near the CC-protocol parsers).
- `hook-runner/ui.ts` — the `/hooks` TUI command and its sub-handlers.
- `hook-runner/index.ts` — the Pi-runtime event handlers; each is now <30 lines because the heavy lifting is behind the modules above.

Trade-off: file count grows. In return each sub-module becomes a real unit with its own tests, and the strength of [coupling](https://coupling.dev/posts/core-concepts/coupling/) within each is high while the strength between them drops to function-level [contract coupling](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/). This is the simplest mechanical refactor in the review and unlocks the others.

## Issue: Pi runtime API coupling is intrusive in places

**Integration**: `hook-runner.ts` + `plan-mode/index.ts` → `@earendil-works/pi-coding-agent`
**Severity**: Significant

### Knowledge Leakage

The code depends on undocumented or semi-documented Pi behaviour: `pi.sendUserMessage(payload, { deliverAs: "steer" })` falls back to `{ deliverAs: "followUp" }` and finally to `ctx.ui.notify` (`sendHookMessageToAgent` at lines 574–590). `ctx.isIdle()` gates the choice. `pi.events.emit/on` are used as a private bus with a string channel name (`cc-hooks:invoke`). The `tool_call` return shape `{ block, reason }` and the `before_agent_start` return shape `{ message: { customType, content, display } }` are both Pi-internal vocabulary. Plan-mode reaches into `ctx.sessionManager.getEntries()` and pattern-matches on `customType` markers it itself wrote ("plan-mode-execute", "plan-mode-context"). None of these are wrapped behind a single facade. Pi is a young, actively-developed project — these surfaces will move.

### Complexity Impact

Any breaking change in Pi's API requires hunting through three files (`hook-runner.ts`, `plan-mode/index.ts`, `permission-gate.ts`) plus the test mocks. Today's tests mock the Pi SDK shape directly, which means a Pi-side rename forces N test rewrites in addition to the production-code edits.

### Cascading Changes

1. Pi renames `deliverAs: "steer"` → `deliverAs: "interrupt"`. Caller in `hook-runner.ts:582` must change; nothing in the type system flags it because we caught the error and fell back to `followUp`, masking the rename.
2. Pi removes `ctx.isIdle()`. Every caller of `sendHookMessageToAgent` must pick a new heuristic.
3. Pi adds a new `agent_start` payload shape. The dispatcher at line 1226 still works because the typed `_event` is ignored — but `event.toolResults` shape changes at `turn_end` propagate immediately.

### Recommended Improvement

Introduce a thin Pi-runtime facade (`pi-runtime.ts` or similar) that owns: (a) message delivery (`deliverAgent(payload)` collapses the steer/followUp/notify ladder), (b) idle/UI capability detection, (c) the event-bus channel name and emit/on wrappers. Hook-runner and the other extensions consume the facade. The unowned API surface — Pi's actual types — appears in exactly one file; the rest of cc-thingz sees a stable [contract](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/).

Trade-off: a thin extra layer. The cost is real because the facade must stay current with Pi. The win is that the volatility of the external dependency is absorbed in one place rather than fanning out.

## Issue: `HookEntry` smuggles view-model and runtime state through its wire shape

**Integration**: Internal — `hook-runner.ts:83–91`
**Severity**: Minor

### Knowledge Leakage

`HookEntry` is the JSON shape parsed from `hooks.json` (`type`, `command`, `timeout`, `async`) plus two intrusive runtime-only fields prefixed with `_`: `_source` (`"bundled" | "global" | "project"`) and `_disabled` (boolean). The comment at line 90 says "Never persisted" — but the discipline is by convention only. Every reader of `HookEntry` (dispatcher, summary builder, `/hooks` UI, filter pipeline) must know which fields belong to which lifecycle.

### Complexity Impact

A consumer that JSON-serialises a `HookEntry` (for debugging, telemetry, or copy-paste into a user config) will accidentally publish the `_source` and `_disabled` tags. The discipline is unenforced.

### Recommended Improvement

Split the type into `HookEntryConfig` (wire format) and `HookEntryRuntime` (`{ config: HookEntryConfig; source: HookSource; disabled: boolean }`). `loadConfig` produces `HookEntryRuntime`; everything downstream consumes it. The wire/state separation becomes a [contract](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/), not a naming convention.

Trade-off: one extra type alias and a small touch-up to the summary/UI code. The win is small but the change is mechanical, and it composes with the file split.

## Issue: `TOOL_NAME_MAP` is duplicated knowledge with a fragile fallback

**Integration**: `hook-runner.ts:166–181` (mapping) ↔ `permission-gate.ts:29,35` (hard-coded `"Bash"`) ↔ `plan-mode/index.ts:151` (hard-coded `"ExitPlanMode"`)
**Severity**: Minor

### Knowledge Leakage

Three call sites need to know the canonical CC tool name for the same Pi tool: `hook-runner` has a nine-entry mapping plus a capitalise-first-letter fallback, `permission-gate` hard-codes `"Bash"`, `plan-mode` hard-codes `"ExitPlanMode"`. The fallback is also fragile: a future Pi tool with a snake_case name (e.g. `read_url`) would map to `Read_url`, not `ReadUrl` — but no test exercises that branch.

### Recommended Improvement

Move `TOOL_NAME_MAP` and `toCcToolName` into `hook-bridge.ts` (it is already the contract surface between `hook-runner` and consumers). Replace the literal `"Bash"` and `"ExitPlanMode"` in the consumer extensions with `toCcToolName("bash")` / `toCcToolName("exit_plan_mode")`. Drop the snake_case-to-PascalCase auto-conversion in favour of an explicit warning when a Pi tool has no registered CC name — silent inference is the failure mode.

Trade-off: minor. The change tightens [contract coupling](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) and gives users a real error when a tool mapping is missing.

## What is already balanced

Not every integration in this design is a problem. Three are exemplary and should be preserved as the refactor progresses:

- **`hook-bridge.ts` synthetic event contract.** Discriminated unions, named channel, explicit timeouts, fail-closed defaults for permission events. Strength is [contract-level](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/), distance is zero (same package, co-deployed), volatility is medium. The balance rule is satisfied.
- **Hook scripts ↔ hook-runner.** JSON-on-stdin / exit-code-2-blocks is a stable published protocol. Same repo, contract coupling, low domain volatility (Claude Code defined the shape years ago). Good.
- **`revdiff-plan-review.py` ↔ revdiff-planning.** External plugin, no formal contract, but fail-open absorbs missing-plugin volatility and the wrapper only re-exports stdin/stdout. The Claude env-var imitation (`CLAUDE_PLUGIN_ROOT`, `CLAUDE_PROJECT_DIR`, `CLAUDE_PLUGIN_DATA`) is mild [model coupling](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) but the third-party plugin owns the constants — cc-thingz is the one imitating, and the wrapper isolates that knowledge to one ~120-line file.

## Suggested sequencing

1. Split `hook-runner.ts` into the five sub-modules listed (mechanical, unblocks the rest).
2. Land the CC-protocol [anti-corruption layer](https://coupling.dev/posts/core-concepts/balance/) (`cc-protocol.ts`). Move all parsers behind it; remove the legacy-name rewriting from the dispatcher.
3. Move `TOOL_NAME_MAP` into `hook-bridge.ts`; replace hard-coded CC tool names in `permission-gate` and `plan-mode`.
4. Generate `dist/pi/extensions/hooks.json` from `meta.yaml` via `compile_hook`. Delete `src/pi-extensions/hooks.json`.
5. Push the per-entry vs outer-wait invariant into `invokeSyntheticHook`.
6. Introduce the Pi-runtime facade; migrate callers incrementally.

Steps 1 and 2 are the high-leverage ones — together they eliminate roughly two-thirds of the [model coupling](https://coupling.dev/posts/dimensions-of-coupling/integration-strength/) flagged in this review.

---

_This analysis was performed using the [Balanced Coupling](https://coupling.dev) model by [Vlad Khononov](https://vladikk.com)._

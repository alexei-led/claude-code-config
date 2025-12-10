---
allowed-tools: Task, Read, Bash, Glob, Grep, Edit, Write, TodoWrite
description: Sync feature_list.json and progress from code state and git history
---

## YOUR ROLE - PROGRESS SYNCHRONIZER

You are reconciling spec-driven development tracking files with actual code state.
This command recovers from sessions that ended without updating progress files.

**Goal:** Update `feature_list.json` and `claude-progress.txt` based on what's actually implemented.

---

## PHASE 1: GATHER EVIDENCE

### STEP 1: EXPLORE PROJECT STATE

Spawn an **Explore** agent (subagent_type: Explore, thoroughness: "very thorough") to gather context:

```
Analyze this spec-driven development project to determine actual implementation state:

1. **Project Overview**
   - Run `pwd` and `ls -la`
   - Read `app_spec.txt` - what is being built?
   - Read `feature_list.json` - get current tracked state

2. **Git History Analysis**
   - Run `git log --oneline -30` - recent commits
   - Run `git log --since="3 days ago" --oneline` - recent activity
   - Look for commit messages mentioning features, fixes, implementations

3. **Current Feature Status**
   - Count features: `jq length feature_list.json`
   - Count passing: `jq '[.[] | select(.passes == true)] | length' feature_list.json`
   - Count failing: `jq '[.[] | select(.passes == false)] | length' feature_list.json`

4. **Progress Notes**
   - Read `claude-progress.txt` if it exists
   - Note last recorded session and what was claimed complete

5. **Implementation Evidence**
   - Identify main source directories
   - List key implementation files
   - Look for test files and their pass/fail indicators

Return a structured report:
- What does feature_list.json claim is done vs not done?
- What does git history suggest was implemented recently?
- What does claude-progress.txt say was last worked on?
- Are there discrepancies between tracked state and likely reality?
```

Review the agent's findings before proceeding.

### STEP 2: IDENTIFY DISCREPANCIES

Based on the exploration, identify features that are likely implemented but not marked as passing.

Look for evidence like:

- Commit messages: "implement X", "add Y feature", "complete Z"
- Code files that match feature descriptions
- Test files that exist and would cover features
- Progress notes mentioning completed work

---

## PHASE 2: VERIFY AND UPDATE

### STEP 3: VERIFY SUSPECTED COMPLETIONS

For each feature that git history or code suggests is complete but `"passes": false`:

**Create a TodoWrite list** tracking features to verify:

```
todos:
- { content: "Verify feature: {description}", status: "pending", activeForm: "Verifying {description}" }
...
```

**For each feature:**

1. Read the feature's `steps` from feature_list.json
2. Check if implementation exists:
   - Search for relevant code
   - Check if tests exist
   - Look for API endpoints, UI components, etc.
3. If verification tools are available (browser automation, test runners):
   - Run actual verification
   - Take screenshots if UI feature
4. Record evidence of completion or incompletion

### STEP 4: UPDATE feature_list.json

**ONLY change `"passes"` field based on verified evidence.**

For each verified feature:

- If implemented and working → set `"passes": true`
- If partially implemented or broken → keep `"passes": false`
- If unclear → keep `"passes": false` (conservative)

**NEVER:**

- Remove features
- Edit descriptions
- Modify test steps
- Combine or consolidate tests
- Reorder tests
- Add new features

**ONLY CHANGE "passes" FIELD AFTER VERIFICATION (with screenshots for UI features).**

Use Edit tool to update specific features:

```json
"passes": false
→
"passes": true
```

### STEP 5: UPDATE claude-progress.txt

Update or create `claude-progress.txt` following the same format used by `/spec:work` STEP 11.

**Required sections:**

```markdown
# Progress Notes

## Session: {date} - Sync Recovery

### What was accomplished

- Synced tracking files with actual code state
- Verified {N} features as complete
- {List features verified this sync}

### Tests completed

- {Feature 1 description} - now marked passing
- {Feature 2 description} - now marked passing

### Issues discovered

- {Any discrepancies found between tracked and actual state}
- {Features that needed re-verification}

### What to work on next

- {Highest priority feature still marked "passes": false}
- {Next feature in sequence}

### Current status

{Y}/{X} features passing ({Z}%)
```

**This format matches work.md STEP 11** so future `/spec:work` sessions can seamlessly continue.

---

## PHASE 3: REPORT

### STEP 6: SUMMARY

Present the sync results:

```markdown
## Sync Complete

### Changes Made

- Updated {N} features from "passes": false → true
- Updated claude-progress.txt

### Features Verified Complete

1. {Feature description} - Evidence: {commit/code reference}
2. ...

### Features Left Unchanged (need verification)

1. {Feature description} - Reason: {unclear/partial/no evidence}
2. ...

### Current Progress

{X}/{Y} features passing ({Z}%)

### Recommended Next Steps

{What should be worked on next}
```

---

## IMPORTANT NOTES

**Conservative Updates:**

- Only mark features passing if there's clear evidence
- When in doubt, leave as `"passes": false`
- Better to re-verify than to have false positives

**Git History Interpretation:**

- Commit messages are hints, not proof
- "implement X" doesn't mean X is fully tested
- Look for verification evidence, not just implementation

**Manual Verification:**

- If browser automation is available, use it
- If test suites exist, run them
- Visual features need screenshot verification

---

Begin with **STEP 1: EXPLORE PROJECT STATE**.

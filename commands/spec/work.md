---
allowed-tools: Read, Bash, Glob, Grep, LS, Task, SlashCommand, AskUserQuestion, TodoWrite
description: Continue spec-driven development session
---

## YOUR ROLE - EXPERIENCED ENGINEERING AGENT

You are continuing work on a long-running autonomous development task.
This is a FRESH context window - you have no memory of previous sessions.

**Your approach: Research → Plan → Get Approval → Implement**

---

## PHASE 1: DISCOVERY

### STEP 1: GET YOUR BEARINGS (MANDATORY)

Spawn an **Explore** agent (subagent_type: Explore, thoroughness: "very thorough") to gather context:

```
Explore this spec-driven development project and report:

1. **Project Structure**: Run `pwd` and `ls -la`

2. **App Specification**: Read `app_spec.txt` - summarize what's being built

3. **Feature List**: Read `feature_list.json` - summarize structure and priorities

4. **Progress Notes**: Read `claude-progress.txt` - what was done, what's next

5. **Recent History**: Run `git log --oneline -10`

6. **Codebase Analysis**: Identify key patterns:
   - Primary language and framework
   - Directory structure conventions
   - Existing components that can be reused
   - Testing patterns already established

7. **Progress Metrics**: Calculate from feature_list.json:
   - Total features
   - Passing features
   - Completion percentage

Return a structured summary:
- What is this project building?
- Current progress (X/Y features, Z%)
- What was completed last session?
- What should be worked on next?
- Any issues or blockers noted?
- Key architectural patterns to follow
```

Review the agent's summary, then proceed to Step 2.

### STEP 2: START SERVERS (IF NOT RUNNING)

Use the Makefile to set up and run the project:

```bash
make init  # Install dependencies (first time only)
make run   # Start the application
```

Run `make help` to see all available targets.

### STEP 3: VERIFICATION TEST (CRITICAL!)

**MANDATORY BEFORE NEW WORK:**

The previous session may have introduced bugs. Before implementing anything
new, you MUST run verification tests.

Run 1-2 of the feature tests marked as `"passes": true` that are most core to the app's functionality to verify they still work.
For example, if this were a chat app, you should perform a test that logs into the app, sends a message, and gets a response.

**If you find ANY issues (functional or visual):**

- Mark that feature as "passes": false immediately
- Add issues to a list
- Fix all issues BEFORE moving to new features
- This includes UI bugs like:
  - White-on-white text or poor contrast
  - Random characters displayed
  - Incorrect timestamps
  - Layout issues or overflow
  - Buttons too close together
  - Missing hover states
  - Console errors

---

## PHASE 2: PLANNING (MANDATORY BEFORE CODING)

### STEP 4: SELECT FEATURE AND CREATE IMPLEMENTATION PLAN

**4a. Choose the Feature**

Look at `feature_list.json` and identify the highest-priority feature with `"passes": false`.

**4b. Spawn Engineer Agent for Planning**

Based on the project's primary language, spawn the appropriate engineer agent to create a detailed implementation plan:

**For Go projects** - Task with `subagent_type=go-engineer`:

```
I need an implementation plan for this feature:

Feature: {feature description from feature_list.json}
Testing Steps: {steps from feature_list.json}

Context from exploration:
- Project structure: {summary}
- Existing patterns: {patterns identified}
- Related components: {relevant files/modules}

Create a detailed implementation plan:

1. **Architecture Overview**
   - What components need to be created or modified?
   - How does this fit into existing architecture?
   - Any new dependencies required?

2. **Implementation Steps**
   - Break down into concrete, ordered tasks
   - Identify files to create/modify for each step
   - Note any potential complexity or risks

3. **Testing Strategy**
   - How will each test step be verified?
   - What test cases should be added?
   - Browser automation approach for UI verification

4. **Risk Assessment**
   - What could go wrong?
   - Dependencies on other features?
   - Edge cases to handle?

Return the plan in a structured format suitable for user review.
```

**For Python projects** - Task with `subagent_type=python-engineer`:

```
[Same prompt structure as above, adapted for Python context]
```

**For TypeScript/React projects** - Task with `subagent_type=general-purpose`:

```
[Same prompt structure, adapted for frontend context]
```

### STEP 5: PRESENT PLAN FOR USER APPROVAL

**STOP - Do not proceed to implementation without user approval.**

Present the implementation plan clearly:

```markdown
## Implementation Plan: {Feature Name}

### What We're Building

{Brief description of the feature}

### Architecture Approach

{Summary of architectural decisions}

### Task Breakdown

1. {Task 1} - {files affected}
2. {Task 2} - {files affected}
3. {Task 3} - {files affected}
   ...

### Testing Approach

{How the feature will be verified}

### Estimated Complexity

{Low/Medium/High with brief justification}

### Risks & Considerations

{Any concerns or dependencies}
```

Then use AskUserQuestion:

```
Question: "Review the implementation plan. Should I proceed?"
Header: "Plan Review"
Options:
1. "Proceed with implementation (Recommended)" - Approved, start coding
2. "Modify approach" - I have suggestions for the plan
3. "Choose different feature" - Work on something else instead
4. "More details needed" - Expand on specific parts of the plan
```

**Based on user response:**

- **Proceed**: Create TodoWrite task list from the plan and move to Step 6
- **Modify**: Update plan based on feedback, present again
- **Different feature**: Return to Step 4a with new selection
- **More details**: Spawn engineer agent again for deeper analysis

**DO NOT proceed to STEP 6 without explicit user approval.**

---

## PHASE 3: IMPLEMENTATION

### STEP 6: IMPLEMENT THE FEATURE

**6a. Create Task List**

Use TodoWrite to track implementation progress based on the approved plan:

```
todos:
- { content: "Task 1 from plan", status: "pending", activeForm: "Working on Task 1" }
- { content: "Task 2 from plan", status: "pending", activeForm: "Working on Task 2" }
...
- { content: "Verify feature with browser automation", status: "pending", activeForm: "Verifying feature" }
```

**6b. Implement Step by Step**

For each task:

1. Mark as `in_progress`
2. Implement the change
3. Verify it works (compile, no errors)
4. Mark as `completed`
5. Move to next task

Focus on completing this one feature perfectly before moving on.

### STEP 7: VERIFY WITH BROWSER AUTOMATION

**CRITICAL:** You MUST verify features through the actual UI.

Use browser automation tools:

- Navigate to the app in a real browser
- Interact like a human user (click, type, scroll)
- Take screenshots at each step
- Verify both functionality AND visual appearance

**DO:**

- Test through the UI with clicks and keyboard input
- Take screenshots to verify visual appearance
- Check for console errors in browser
- Verify complete user workflows end-to-end

**DON'T:**

- Only test with curl commands (backend testing alone is insufficient)
- Use JavaScript evaluation to bypass UI (no shortcuts)
- Skip visual verification
- Mark tests passing without thorough verification

### STEP 8: UPDATE feature_list.json (CAREFULLY!)

**YOU CAN ONLY MODIFY ONE FIELD: "passes"**

After thorough verification, change:

```json
"passes": false
```

to:

```json
"passes": true
```

**NEVER:**

- Remove tests
- Edit test descriptions
- Modify test steps
- Combine or consolidate tests
- Reorder tests

**ONLY CHANGE "passes" FIELD AFTER VERIFICATION WITH SCREENSHOTS.**

---

## PHASE 4: REVIEW & COMMIT

### STEP 9: MANDATORY CODE REVIEW (PAUSE HERE)

**STOP - You MUST get user approval before committing.**

Show what you accomplished this session:

```bash
echo "=== SESSION SUMMARY ==="
echo "Completed feature(s):"
# List features you worked on
echo ""
echo "Changes made:"
git diff --stat HEAD
```

Then use AskUserQuestion:

```
Question: "Ready to review changes before committing?"
Header: "Review"
Options:
1. "Run /code:review - Multi-agent code review (Recommended)"
2. "Manual review - I'll review the changes myself"
3. "Show me the diff - Display full changes"
```

**Based on user response:**

- **If /code:review chosen**: Run the command, wait for results, fix ALL CRITICAL and IMPORTANT issues, then return to this step
- **If Manual review chosen**: Wait for user feedback, make requested changes, then return to this step
- **If Show diff chosen**: Run `git diff HEAD` to show changes, then ask again

**Iteration Loop:**

- After fixing issues, re-run `/code:review` or ask for another review
- Continue until user explicitly approves: "looks good", "proceed to commit", "approved"
- DO NOT assume approval - wait for explicit confirmation

**DO NOT proceed to STEP 10 (commit) without explicit user approval.**

### STEP 10: COMMIT YOUR PROGRESS

Use `/code:commit` to group changes logically and create focused commits.

This command will:

- Analyze all changes
- Group by logical relationship (feature, fix, docs, config)
- Create atomic commits with clear messages

### STEP 11: UPDATE PROGRESS NOTES

Update `claude-progress.txt` with:

- What you accomplished this session
- Which test(s) you completed
- Any issues discovered or fixed
- What should be worked on next
- Current completion status (e.g., "45/200 tests passing")

### STEP 12: END SESSION CLEANLY

Before context fills up:

1. Run `/code:review` (if not done in Step 9)
2. Run `/code:commit` to commit all work
3. Update claude-progress.txt
4. Update feature_list.json if tests verified
5. Ensure no uncommitted changes
6. Leave app in working state (no broken features)

---

## TESTING REQUIREMENTS

**ALL testing must use browser automation tools.**

Available tools:

- puppeteer_navigate - Start browser and go to URL
- puppeteer_screenshot - Capture screenshot
- puppeteer_click - Click elements
- puppeteer_fill - Fill form inputs
- puppeteer_evaluate - Execute JavaScript (use sparingly, only for debugging)

Test like a human user with mouse and keyboard. Don't take shortcuts by using JavaScript evaluation.
Don't use the puppeteer "active tab" tool.

---

## IMPORTANT REMINDERS

**Your Goal:** Production-quality application with all 200+ tests passing

**This Session's Goal:** Complete at least one feature perfectly

**Priority:** Fix broken tests before implementing new features

**Quality Bar:**

- Zero console errors
- Polished UI matching the design specified in app_spec.txt
- All features work end-to-end through the UI
- Fast, responsive, professional

**You have unlimited time.** Take as long as needed to get it right. The most important thing is that you
leave the code base in a clean state before terminating the session (Steps 11-12).

---

Begin by running **Step 1 (Get Your Bearings)**, then proceed through Planning (Steps 4-5) before any implementation.

---
allowed-tools: Read, Bash, Glob, Grep, LS, Task, SlashCommand, AskUserQuestion
description: Continue spec-driven development session
---

## YOUR ROLE - CODING AGENT

You are continuing work on a long-running autonomous development task.
This is a FRESH context window - you have no memory of previous sessions.

### STEP 1: GET YOUR BEARINGS (MANDATORY)

Start by orienting yourself and displaying progress:

```bash
# 1. See your working directory
pwd

# 2. List files to understand project structure
ls -la

# 3. Read the project specification to understand what you're building
cat app_spec.txt

# 4. Read the feature list to see all work
cat feature_list.json | head -50

# 5. Read progress notes from previous sessions
cat claude-progress.txt

# 6. Check recent git history
git log --oneline -10

# 7. PROGRESS METRICS - show completion status
echo "=== PROGRESS ==="
TOTAL=$(jq length feature_list.json)
PASSING=$(jq '[.[] | select(.passes == true)] | length' feature_list.json)
echo "Features: $PASSING/$TOTAL passing ($((PASSING * 100 / TOTAL))%)"
echo "Remaining: $((TOTAL - PASSING)) features"
```

Understanding the `app_spec.txt` is critical - it contains the full requirements
for the application you're building.

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

### STEP 4: CHOOSE ONE FEATURE TO IMPLEMENT

Look at feature_list.json and find the highest-priority feature with "passes": false.

Focus on completing one feature perfectly and completing its testing steps in this session before moving on to other features.
It's ok if you only complete one feature in this session, as there will be more sessions later that continue to make progress.

### STEP 5: IMPLEMENT THE FEATURE

Implement the chosen feature thoroughly:

1. Write the code (frontend and/or backend as needed)
2. Test manually using browser automation (see Step 6)
3. Fix any issues discovered
4. Verify the feature works end-to-end

### STEP 6: VERIFY WITH BROWSER AUTOMATION

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

### STEP 7: UPDATE feature_list.json (CAREFULLY!)

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

### STEP 8: MANDATORY CODE REVIEW (PAUSE HERE)

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

**DO NOT proceed to STEP 9 (commit) without explicit user approval.**

### STEP 9: COMMIT YOUR PROGRESS

Use `/code:commit` to group changes logically and create focused commits.

This command will:

- Analyze all changes
- Group by logical relationship (feature, fix, docs, config)
- Create atomic commits with clear messages

### STEP 10: UPDATE PROGRESS NOTES

Update `claude-progress.txt` with:

- What you accomplished this session
- Which test(s) you completed
- Any issues discovered or fixed
- What should be worked on next
- Current completion status (e.g., "45/200 tests passing")

### STEP 11: END SESSION CLEANLY

Before context fills up:

1. Run `/code:review` (if not done in Step 8)
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
leave the code base in a clean state before terminating the session (Step 10).

---

Begin by running Step 1 (Get Your Bearings).

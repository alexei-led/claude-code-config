#!/bin/bash
# UserPromptSubmit hook that enforces skill activation
#
# This hook requires Claude to activate relevant skills before implementation.

cat <<'EOF'
INSTRUCTION: MANDATORY SKILL ACTIVATION

Check <available_skills> for relevance before proceeding.

IF any skills are relevant:
  1. State which skills and why (only mention relevant ones)
  2. Immediately activate each with Skill(skill-name) tool
  3. Then proceed with implementation

IF no skills are relevant:
  - Proceed directly (no statement needed)

Example when skills are relevant:
  relevant skills: mongo (querying database), local-docs (using go-pkgz)
  [immediately activates: Skill(mongo), Skill(local-docs)]
  [then proceeds with implementation]

CRITICAL: Activate relevant skills via Skill() tool before implementation.
Mentioning a skill without activating it is worthless.
EOF

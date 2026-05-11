#!/usr/bin/env bats

HOOK="$BATS_TEST_DIRNAME/../../src/hooks/git-guardrails/HOOK.sh"
FIXTURES="$BATS_TEST_DIRNAME/fixtures"

@test "git-guardrails: safe git command is allowed (exits 0)" {
	run bash "$HOOK" <"$FIXTURES/git_guardrails_safe.json"
	[ "$status" -eq 0 ]
}

@test "git-guardrails: git reset --hard is blocked (exits 2)" {
	run bash "$HOOK" <"$FIXTURES/git_guardrails_dangerous.json" 2>&1
	[ "$status" -eq 2 ]
}

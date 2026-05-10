#!/usr/bin/env bats

HOOK="$BATS_TEST_DIRNAME/../../plugins/dev-workflow/hooks/skill-enforcer.sh"
FIXTURES="$BATS_TEST_DIRNAME/fixtures"

@test "skill-enforcer: unrelated prompt is silent and exits 0" {
	run bash "$HOOK" < "$FIXTURES/skill_enforcer_no_match.json"
	[ "$status" -eq 0 ]
	[ -z "$output" ]
}

@test "skill-enforcer: prompt matching known skills outputs suggestion and exits 0" {
	run bash "$HOOK" < "$FIXTURES/skill_enforcer_match.json"
	[ "$status" -eq 0 ]
	[[ "$output" == *"Consider skills"* ]]
}

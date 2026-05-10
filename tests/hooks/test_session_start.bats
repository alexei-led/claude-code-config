#!/usr/bin/env bats

HOOK="$BATS_TEST_DIRNAME/../../plugins/dev-workflow/hooks/session-start.sh"
FIXTURES="$BATS_TEST_DIRNAME/fixtures"

@test "session-start: valid cwd exits 0" {
	run bash "$HOOK" <"$FIXTURES/session_start_valid.json"
	[ "$status" -eq 0 ]
}

@test "session-start: empty JSON payload falls back gracefully and exits 0" {
	run bash "$HOOK" <"$FIXTURES/session_start_empty.json"
	[ "$status" -eq 0 ]
}

#!/usr/bin/env bats

HOOK="$BATS_TEST_DIRNAME/../../plugins/dev-workflow/hooks/file-protector.sh"
FIXTURES="$BATS_TEST_DIRNAME/fixtures"

@test "file-protector: safe file path is allowed (exits 0)" {
	run bash "$HOOK" <"$FIXTURES/file_protector_safe.json"
	[ "$status" -eq 0 ]
}

@test "file-protector: .env file path is blocked (exits 2)" {
	run bash "$HOOK" <"$FIXTURES/file_protector_sensitive.json" 2>&1
	[ "$status" -eq 2 ]
}

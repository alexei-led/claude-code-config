#!/usr/bin/env bats

HOOK="$BATS_TEST_DIRNAME/../../src/hooks/file-protector/HOOK.sh"
FIXTURES="$BATS_TEST_DIRNAME/fixtures"

@test "file-protector: safe file path is allowed (exits 0)" {
	run bash "$HOOK" <"$FIXTURES/file_protector_safe.json"
	[ "$status" -eq 0 ]
}

@test "file-protector: .env file path is blocked (exits 2)" {
	run bash "$HOOK" <"$FIXTURES/file_protector_sensitive.json" 2>&1
	[ "$status" -eq 2 ]
}

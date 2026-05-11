#!/usr/bin/env bats

HOOK="$BATS_TEST_DIRNAME/../../src/hooks/smart-lint/HOOK.sh"

setup() {
	WORK_DIR="${BATS_TEST_TMPDIR:-$(mktemp -d)}"
	mkdir -p "$WORK_DIR"
}

teardown() {
	rm -rf "$WORK_DIR"
}

@test "smart-lint: SKIP_LINT=1 skips all linting and exits 0" {
	run env SKIP_LINT=1 bash "$HOOK"
	[ "$status" -eq 0 ]
}

@test "smart-lint: .nolint file in project root skips linting and exits 0" {
	touch "$WORK_DIR/.nolint"
	run bash -c "cd '$WORK_DIR' && bash '$HOOK'"
	[ "$status" -eq 0 ]
}

#!/usr/bin/env bash
# JavaScript/TypeScript linting: prettier, eslint, knip, dependency-cruiser (arch tier).

lint_typescript() {
	log_debug "js/ts checks"

	local files=()
	mapfile -t files < <(get_changed_files ".js" ".ts" ".jsx" ".tsx")
	if [[ "${#files[@]}" -eq 0 ]]; then
		log_debug "No uncommitted JS/TS files, skipping JavaScript checks"
		return 0
	fi

	local pm="npm"
	[[ -f "yarn.lock" ]] && pm="yarn"
	[[ -f "pnpm-lock.yaml" ]] && pm="pnpm"

	# Use prettier if available, otherwise try via package manager
	if command_exists prettier; then
		run_formatter_on_files "JS Formatter (prettier)" "prettier --write" "prettier --check" "${files[@]}"
	elif command_exists bunx; then
		run_formatter_on_files "JS Formatter (prettier)" "bunx prettier --write" "bunx prettier --check" "${files[@]}"
	elif command_exists npx; then
		run_formatter_on_files "JS Formatter (prettier)" "npx prettier --write" "npx prettier --check" "${files[@]}"
	elif [[ "$pm" != "npm" ]]; then
		run_formatter_on_files "JS Formatter (prettier)" "$pm exec prettier --write" "$pm exec prettier --check" "${files[@]}"
	fi
	if grep -q '"lint":' package.json 2>/dev/null; then
		# Note: npm run lint typically runs on whole project, might need package.json config for file-specific linting
		run_linter "JS Linter (eslint)" "$pm" run lint
	fi

	# Architecture tier — opt-in by config-file presence. Skipped via SKIP_ARCH=1
	# or .nolint-arch. Project-wide tools, so they don't take the file list.
	[[ "${SKIP_ARCH:-0}" == "1" ]] && return 0

	# knip — unused exports, files, deps. Triggers on its own config file.
	# --max-issues 0 ensures non-zero exit on any finding (knip's default tolerates one).
	if [[ -f knip.json || -f knip.jsonc || -f knip.ts || -f knip.js ]]; then
		if command_exists knip; then
			run_linter "Knip" knip --reporter compact --no-progress --max-issues 0
		elif command_exists bunx; then
			run_linter "Knip" bunx knip --reporter compact --no-progress --max-issues 0
		elif command_exists npx; then
			run_linter "Knip" npx knip --reporter compact --no-progress --max-issues 0
		else
			echo -e "${CYAN}ℹ knip config present but no runner found. Install:${NC} bun add -g knip"
		fi
	fi

	# dependency-cruiser — boundary rules and import cycles. CLI is `depcruise`.
	# `-T err` reporter exits non-zero on violations (default reporter does not).
	if [[ -f .dependency-cruiser.cjs || -f .dependency-cruiser.js || -f .dependency-cruiser.json || -f .dependency-cruiser.mjs ]]; then
		local dc_target="."
		[[ -d src ]] && dc_target="src"
		if command_exists depcruise; then
			run_linter "Dependency-Cruiser" depcruise -T err "$dc_target"
		elif command_exists bunx; then
			run_linter "Dependency-Cruiser" bunx depcruise -T err "$dc_target"
		elif command_exists npx; then
			run_linter "Dependency-Cruiser" npx depcruise -T err "$dc_target"
		else
			echo -e "${CYAN}ℹ dependency-cruiser config present but no runner found. Install:${NC} bun add -g dependency-cruiser"
		fi
	fi
}

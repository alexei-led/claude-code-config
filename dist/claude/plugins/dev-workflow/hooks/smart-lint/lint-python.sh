#!/usr/bin/env bash
# Python linting: ruff (format + lint), black + flake8 fallback, pyright type checks.

lint_python() {
	log_debug "python checks"

	local files=()
	mapfile -t files < <(get_changed_files ".py")
	if [[ "${#files[@]}" -eq 0 ]]; then
		log_debug "No uncommitted Python files, skipping Python checks"
		return 0
	fi

	if command_exists ruff; then
		# ruff format replaces black — single tool for formatting
		run_formatter_on_files "Python Formatter (ruff)" "ruff format" "ruff format --check" "${files[@]}"
		# --unfixable=F401: report unused imports but don't auto-remove them
		# AI agents add imports in one edit and use them in the next
		run_linter "Python Linter (ruff)" ruff check --fix --unfixable=F401 "${files[@]}"
	else
		if command_exists black; then
			run_formatter_on_files "Python Formatter (black)" "black" "black --check" "${files[@]}"
		fi
		if command_exists flake8; then
			run_linter "Python Linter (flake8)" flake8 "${files[@]}"
		fi
	fi
	if command_exists pyright; then
		# Filter out reportMissingImports — missing stubs, not real errors
		local pyright_output
		if pyright_output=$(pyright "${files[@]}" 2>&1); then
			log_debug "pyright passed"
		else
			local filtered
			filtered=$(echo "$pyright_output" | grep -v 'reportMissingImports')
			if echo "$filtered" | grep -qE ' error: '; then
				add_error "Python Type Checker (pyright)" "$filtered"
			else
				log_debug "pyright: only missing stubs warnings (filtered)"
			fi
		fi
	fi
}

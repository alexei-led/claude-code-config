#!/usr/bin/env bash
# test-runner.sh - Automated test execution after code changes
#
# DESCRIPTION
#   Auto-detects project type and runs appropriate tests.
#   Falls back gracefully when preferred tools are absent.
#
#   Makefile targets are the universal escape hatch: if Makefile has a
#   recognised test target it wins regardless of language, letting projects
#   wire any tool or configuration without modifying this script.
#
# EXIT CODES
#   0 - All tests passed (or no framework found)
#   1 - Test failures or errors

set +e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m'

echo "" >&2
echo "🧪 Running tests..." >&2
echo "──────────────────" >&2

# --- UNIVERSAL MAKEFILE ESCAPE HATCH ---
# If the project has wired a Makefile test target, use it unconditionally.
# This lets any tool or configuration be used without touching this script.
#
# Opt out per-project with a .nomake file in the repo root (add to .gitignore
# for a local-only override, or commit it to disable for the whole team).
# Opt out transiently with SKIP_MAKE=1 in the environment.
if [[ "${SKIP_MAKE:-}" != "1" ]] && [[ ! -f ".nomake" ]] && [[ -f "Makefile" ]]; then
	for target in test tests check verify; do
		if grep -qE "^${target}[[:space:]]*:" Makefile 2>/dev/null; then
			echo -e "${BLUE}[INFO]${NC} Running: make $target" >&2
			make "$target"
			EXIT_CODE=$?
			echo "" >&2
			if [[ $EXIT_CODE -eq 0 ]]; then
				echo -e "${GREEN}✅ Tests passed${NC}" >&2
			else
				echo -e "${RED}❌ Tests failed!${NC}" >&2
			fi
			exit $EXIT_CODE
		fi
	done
fi

# --- LANGUAGE DETECTION ---
detect_project_type() {
	# Ordered by specificity — first match wins.
	if [[ -f "go.mod" ]]; then
		echo "go"
	elif [[ -f "Cargo.toml" ]]; then
		echo "rust"
	elif [[ -f "mix.exs" ]]; then
		echo "elixir"
	elif [[ -f "pom.xml" ]]; then
		echo "java"
	elif [[ -f "build.gradle" ]] || [[ -f "build.gradle.kts" ]]; then
		echo "gradle"
	elif find . -maxdepth 2 \( -name "*.csproj" -o -name "*.sln" \) -print -quit 2>/dev/null | grep -q .; then
		echo "dotnet"
	elif [[ -f "Package.swift" ]]; then
		echo "swift"
	elif [[ -f "Gemfile" ]]; then
		echo "ruby"
	elif [[ -f "composer.json" ]]; then
		echo "php"
	elif [[ -f "pyproject.toml" ]] || [[ -f "setup.py" ]] || [[ -f "requirements.txt" ]]; then
		echo "python"
	elif [[ -f "package.json" ]]; then
		echo "javascript"
	elif find . -maxdepth 3 -name "*.bats" -print -quit 2>/dev/null | grep -q .; then
		echo "shell"
	else
		echo "unknown"
	fi
}

# --- LANGUAGE-SPECIFIC RUNNERS ---

run_python_tests() {
	# uv run respects the project lockfile and interpreter — avoids stale PATH wrappers.
	# .venv/bin/pytest is a direct-path fallback when uv is absent.
	# python3 -m pytest is safer than bare pytest (no shebang interpreter mismatch).
	if command -v uv &>/dev/null && [[ -f "pyproject.toml" ]]; then
		echo -e "${BLUE}[INFO]${NC} Running: uv run pytest" >&2
		uv run pytest -v
	elif [[ -x ".venv/bin/pytest" ]]; then
		echo -e "${BLUE}[INFO]${NC} Running: .venv/bin/pytest" >&2
		.venv/bin/pytest -v
	elif python3 -c "import pytest" 2>/dev/null; then
		echo -e "${BLUE}[INFO]${NC} Running: python3 -m pytest" >&2
		python3 -m pytest -v
	else
		echo -e "${YELLOW}[WARN]${NC} pytest not found — install: uv add --dev pytest" >&2
		return 0
	fi
}

run_javascript_tests() {
	# Detect package manager from lockfile — matches smart-lint.sh convention.
	local pm="npm"
	[[ -f "yarn.lock" ]] && pm="yarn"
	[[ -f "pnpm-lock.yaml" ]] && pm="pnpm"
	{ [[ -f "bun.lockb" ]] || [[ -f "bun.lock" ]]; } && pm="bun"

	local exec_cmd="npx"
	[[ "$pm" == "bun" ]] && exec_cmd="bunx"
	[[ "$pm" == "yarn" ]] && exec_cmd="yarn dlx"
	[[ "$pm" == "pnpm" ]] && exec_cmd="pnpm exec"

	# package.json "test" script is the project's explicit configuration — always honour it.
	if grep -q '"test"' package.json 2>/dev/null; then
		echo -e "${BLUE}[INFO]${NC} Running: $pm test" >&2
		$pm test
		return $?
	fi

	# No test script — infer framework from config files present in the repo.
	if find . -maxdepth 2 -name "vitest.config.*" -print -quit 2>/dev/null | grep -q .; then
		echo -e "${BLUE}[INFO]${NC} Running: $exec_cmd vitest run" >&2
		$exec_cmd vitest run
		return $?
	fi
	if find . -maxdepth 2 -name "jest.config.*" -print -quit 2>/dev/null | grep -q .; then
		echo -e "${BLUE}[INFO]${NC} Running: $exec_cmd jest" >&2
		$exec_cmd jest
		return $?
	fi
	if find . -maxdepth 2 -name ".mocharc*" -print -quit 2>/dev/null | grep -q .; then
		echo -e "${BLUE}[INFO]${NC} Running: $exec_cmd mocha" >&2
		$exec_cmd mocha
		return $?
	fi

	# bun can discover *.test.{ts,js} files natively without any config or script.
	if [[ "$pm" == "bun" ]] && command -v bun &>/dev/null; then
		echo -e "${BLUE}[INFO]${NC} Running: bun test" >&2
		bun test
		return $?
	fi

	echo -e "${YELLOW}[WARN]${NC} No test script or framework config found — add a 'test' script to package.json" >&2
	return 0
}

run_ruby_tests() {
	if command -v bundle &>/dev/null; then
		if [[ -d "spec" ]]; then
			echo -e "${BLUE}[INFO]${NC} Running: bundle exec rspec" >&2
			bundle exec rspec
		elif [[ -d "test" ]]; then
			echo -e "${BLUE}[INFO]${NC} Running: bundle exec rake test" >&2
			bundle exec rake test
		else
			echo -e "${YELLOW}[WARN]${NC} No spec/ or test/ directory found" >&2
			return 0
		fi
	elif command -v rspec &>/dev/null; then
		echo -e "${BLUE}[INFO]${NC} Running: rspec" >&2
		rspec
	else
		echo -e "${YELLOW}[WARN]${NC} bundler not found — install: gem install bundler" >&2
		return 0
	fi
}

run_php_tests() {
	# Pest is the modern PHP test runner; PHPUnit is the classic fallback.
	# Config files (phpunit.xml, phpunit.xml.dist, Pest.php) are read automatically
	# by the runner — no need to detect them here.
	if [[ -x "vendor/bin/pest" ]]; then
		echo -e "${BLUE}[INFO]${NC} Running: vendor/bin/pest" >&2
		vendor/bin/pest
	elif [[ -x "vendor/bin/phpunit" ]]; then
		echo -e "${BLUE}[INFO]${NC} Running: vendor/bin/phpunit" >&2
		vendor/bin/phpunit
	else
		echo -e "${YELLOW}[WARN]${NC} No test runner found — install: composer require --dev pestphp/pest" >&2
		return 0
	fi
}

# --- DISPATCH ---

PROJECT_TYPE=$(detect_project_type)
EXIT_CODE=0

case "$PROJECT_TYPE" in
"go")
	if command -v gotestsum &>/dev/null; then
		# gotestsum gives cleaner output and better failure summaries than go test
		echo -e "${BLUE}[INFO]${NC} Running: gotestsum ./..." >&2
		gotestsum ./...
	else
		echo -e "${BLUE}[INFO]${NC} Running: go test ./..." >&2
		go test ./... -v
	fi
	EXIT_CODE=$?
	;;

"javascript")
	run_javascript_tests
	EXIT_CODE=$?
	;;

"python")
	run_python_tests
	EXIT_CODE=$?
	;;

"rust")
	echo -e "${BLUE}[INFO]${NC} Running: cargo test" >&2
	cargo test
	EXIT_CODE=$?
	;;

"ruby")
	run_ruby_tests
	EXIT_CODE=$?
	;;

"java")
	echo -e "${BLUE}[INFO]${NC} Running: mvn test" >&2
	mvn test -q
	EXIT_CODE=$?
	;;

"gradle")
	if [[ -x "./gradlew" ]]; then
		echo -e "${BLUE}[INFO]${NC} Running: ./gradlew test" >&2
		./gradlew test
	else
		echo -e "${BLUE}[INFO]${NC} Running: gradle test" >&2
		gradle test
	fi
	EXIT_CODE=$?
	;;

"dotnet")
	echo -e "${BLUE}[INFO]${NC} Running: dotnet test" >&2
	dotnet test
	EXIT_CODE=$?
	;;

"elixir")
	echo -e "${BLUE}[INFO]${NC} Running: mix test" >&2
	mix test
	EXIT_CODE=$?
	;;

"swift")
	echo -e "${BLUE}[INFO]${NC} Running: swift test" >&2
	swift test
	EXIT_CODE=$?
	;;

"php")
	run_php_tests
	EXIT_CODE=$?
	;;

"shell")
	if command -v bats &>/dev/null; then
		echo -e "${BLUE}[INFO]${NC} Running: bats ." >&2
		bats .
	else
		echo -e "${YELLOW}[WARN]${NC} bats not found — install: brew install bats-core" >&2
	fi
	EXIT_CODE=$?
	;;

*)
	echo -e "${YELLOW}[WARN]${NC} Unknown project type, cannot run tests" >&2
	EXIT_CODE=0
	;;
esac

echo "" >&2
if [[ $EXIT_CODE -eq 0 ]]; then
	echo -e "${GREEN}✅ Tests passed (or no test framework found)${NC}" >&2
else
	echo -e "${RED}❌ Tests failed!${NC}" >&2
fi

exit $EXIT_CODE

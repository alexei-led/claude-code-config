# Reset Working State

Clean up the working directory and reset to a known good state.

## Actions

1. **Run all formatters and linters** - Ensure code is clean
2. **Clear temporary files** - Remove .cache, __pycache__, etc.
3. **Verify git status** - Check for uncommitted changes
4. **Regenerate TODO.md** - Update task list from current state

## Optional Arguments

- `--hard`: Reset git to last clean commit (destructive!)
- `--cache`: Only clear cache files
- `--format`: Only run formatters

## Usage Examples

- `/reset` - Standard cleanup
- `/reset --hard` - Full reset including git
- `/reset --cache` - Just clear caches

$ARGUMENTS
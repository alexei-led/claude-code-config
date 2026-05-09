# Custom Rules for Pi Planning Skills

Custom rules inject project-specific or personal conventions into the planning workflow.

## File Locations

Checked in this order. First non-empty file wins.

1. Project-level: `.pi/planning-rules.md`
2. Project-level fallback for Claude compatibility: `.claude/planning-rules.md`
3. User-level: `~/.pi/agent/planning-rules.md`

Project-level rules override user-level rules. Files are never merged.

## Resolution

Use `../planning-common/scripts/resolve-rules.sh planning-rules.md` from a planning skill directory. The script prints the first matching file or nothing.

## Rule Management

Valid operations:
- show rules
- add/update project rules in `.pi/planning-rules.md`
- add/update user rules in `~/.pi/agent/planning-rules.md`
- clear project rules
- clear user rules

## Example

```markdown
## Testing
- Prefer table-driven tests
- Cover success and error paths

## Scope
- Split migrations from feature work
- One endpoint or one component per task
```

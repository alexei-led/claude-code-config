# Python CLI Patterns

## Framework: Click (Preferred)

Mature, explicit, full control over complex nested CLIs.

### Basic Command Group

```python
import click

@click.group()
@click.option("--debug/--no-debug", default=False, envvar="APP_DEBUG")
@click.option("--log-level", default="INFO", envvar="LOG_LEVEL",
              type=click.Choice(["DEBUG", "INFO", "WARNING", "ERROR"]))
@click.pass_context
def cli(ctx: click.Context, debug: bool, log_level: str) -> None:
    """My application CLI."""
    ctx.ensure_object(dict)
    ctx.obj["debug"] = debug
    ctx.obj["log_level"] = log_level

@cli.command()
@click.argument("input_file", type=click.Path(exists=True))
@click.option("-o", "--output", type=click.Path(), default="output.json")
@click.option("-v", "--verbose", is_flag=True)
@click.option("--dry-run", is_flag=True)
def process(input_file: str, output: str, verbose: bool, dry_run: bool) -> None:
    """Process input files."""
    if dry_run:
        click.echo(f"Would process {input_file} -> {output}")
        return
    result = do_process(input_file)
    Path(output).write_text(json.dumps(result))
```

### Environment Variable Support

Always wire options to envvars for 12-factor compatibility:

```python
@click.option("--token", envvar="API_TOKEN", required=True,
              help="API token ($API_TOKEN)")
@click.option("--port", envvar="APP_PORT", type=int, default=8080,
              help="Port ($APP_PORT, default: 8080)")
```

**Precedence:** CLI flag > env var > .env file > default value.

### Custom Validators

```python
def _validate_positive_float(ctx, param, value):
    if value is not None and value <= 0:
        raise click.BadParameter("must be positive")
    return value

@click.option("--timeout", type=float, callback=_validate_positive_float)
```

### Async Commands

```python
import asyncio
import functools

def async_command(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        return asyncio.run(f(*args, **kwargs))
    return wrapper

@cli.command()
@click.argument("url")
@async_command
async def fetch(url: str) -> None:
    """Fetch data from URL."""
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
    click.echo(response.text)
```

### Default Subcommand

```python
class _DefaultToRun(click.Group):
    """Default to 'run' subcommand when none specified."""
    def parse_args(self, ctx, args):
        if not args or args[0] not in self.commands:
            args = ["run"] + list(args)
        return super().parse_args(ctx, args)

@click.group(cls=_DefaultToRun)
def cli(): ...
```

### Structuring Large CLIs

Split into modules, attach subgroups lazily:

```
src/myapp/
├── cli/
│   ├── __init__.py    # root group
│   ├── users.py       # @users_group commands
│   └── db.py          # @db_group commands
```

```python
# cli/__init__.py
from myapp.cli.users import users
from myapp.cli.db import db

@click.group()
def cli(): pass

cli.add_command(users)
cli.add_command(db)
```

## Alternative: typer

Type-hint based CLI (built on Click). Less boilerplate, but less control:

```python
import typer
app = typer.Typer()

@app.command()
def process(input_file: Path, verbose: bool = False):
    """Process input files."""
    ...
```

## Alternative: argparse (stdlib)

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="Process files")
    parser.add_argument("input", type=Path)
    parser.add_argument("-v", "--verbose", action="store_true")
    args = parser.parse_args()
    process(args.input)
```

## Output Formats

```python
def print_items(items: list[dict], format: str = "table") -> None:
    match format:
        case "json":
            print(json.dumps(items, indent=2))
        case "csv":
            if not items:
                return
            writer = csv.DictWriter(sys.stdout, fieldnames=items[0].keys())
            writer.writeheader()
            writer.writerows(items)
        case _:
            if not items:
                return
            headers = list(items[0].keys())
            widths = [max(len(h), max(len(str(item.get(h, "")))
                     for item in items)) for h in headers]
            print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
            print("  ".join("-" * w for w in widths))
            for item in items:
                print("  ".join(str(item.get(h, "")).ljust(w)
                      for h, w in zip(headers, widths)))
```

## Progress Display

```python
from rich.progress import Progress, SpinnerColumn, TextColumn

def process_with_progress(items: list[Item]) -> None:
    with Progress(SpinnerColumn(), TextColumn("{task.description}")) as progress:
        task = progress.add_task("Processing...", total=len(items))
        for item in items:
            progress.update(task, description=f"Processing {item.name}")
            process_item(item)
            progress.advance(task)
```

## Exit Codes

```python
EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2

def main() -> int:
    try:
        run()
        return EXIT_OK
    except click.UsageError as e:
        click.echo(f"Usage error: {e}", err=True)
        return EXIT_USAGE
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        return EXIT_ERROR
```

## Entry Point

```toml
# pyproject.toml
[project.scripts]
mytool = "mypackage.cli:cli"
```

```python
# src/mypackage/__main__.py
from mypackage.cli import cli

def main():
    cli()

if __name__ == "__main__":
    main()
```

## Testing Click Apps

```python
from click.testing import CliRunner

@pytest.fixture
def runner():
    return CliRunner()

def test_run_default(runner):
    result = runner.invoke(cli, ["run", "--port", "9090"])
    assert result.exit_code == 0

def test_env_override(runner):
    result = runner.invoke(cli, [], env={"APP_PORT": "9090"})
    assert result.exit_code == 0

def test_isolated_filesystem(runner):
    with runner.isolated_filesystem():
        Path("config.json").write_text('{"key": "value"}')
        result = runner.invoke(cli, ["load", "config.json"])
        assert result.exit_code == 0
```

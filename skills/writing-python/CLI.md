# Python CLI Patterns

## Framework: typer (Recommended)

Built on Click, with type hints for argument parsing.

```python
import typer

app = typer.Typer()

@app.command()
def process(
    input_file: Path,
    output: Path = Path("output.json"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
    dry_run: bool = typer.Option(False, "--dry-run"),
):
    """Process input files."""
    if dry_run:
        typer.echo(f"Would process {input_file} -> {output}")
        return

    result = do_process(input_file)
    output.write_text(json.dumps(result))

@app.command()
def list_items(
    format: str = typer.Option("table", help="Output format: table, json, csv"),
):
    """List all items."""
    items = fetch_items()
    print_items(items, format)

if __name__ == "__main__":
    app()
```

## Alternative: argparse (stdlib)

```python
import argparse

def main():
    parser = argparse.ArgumentParser(description="Process files")
    parser.add_argument("input", type=Path, help="Input file")
    parser.add_argument("-o", "--output", type=Path, default=Path("output.json"))
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument("--dry-run", action="store_true")

    args = parser.parse_args()

    if args.dry_run:
        print(f"Would process {args.input} -> {args.output}")
        return

    process(args.input, args.output)

if __name__ == "__main__":
    main()
```

## Output Formats

```python
import csv
import json
import sys
from io import StringIO

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
            widths = [max(len(h), max(len(str(item.get(h, ""))) for item in items)) for h in headers]
            print("  ".join(h.ljust(w) for h, w in zip(headers, widths)))
            print("  ".join("-" * w for w in widths))
            for item in items:
                print("  ".join(str(item.get(h, "")).ljust(w) for h, w in zip(headers, widths)))
```

## Progress Display

```python
from rich.progress import Progress, SpinnerColumn, TextColumn

def process_with_progress(items: list[Item]) -> None:
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
    ) as progress:
        task = progress.add_task("Processing...", total=len(items))
        for item in items:
            progress.update(task, description=f"Processing {item.name}")
            process_item(item)
            progress.advance(task)
```

## Confirmation Prompts

```python
import typer

def delete_item(name: str, force: bool = False) -> None:
    if not force:
        confirm = typer.confirm(f"Delete {name}?")
        if not confirm:
            raise typer.Abort()
    do_delete(name)
```

## Environment Configuration

```python
import os
from dataclasses import dataclass

@dataclass
class Config:
    api_url: str
    api_key: str
    timeout: int = 30

    @classmethod
    def from_env(cls) -> "Config":
        return cls(
            api_url=os.environ.get("API_URL", "https://api.example.com"),
            api_key=os.environ["API_KEY"],
            timeout=int(os.environ.get("TIMEOUT", 30)),
        )
```

## Exit Codes

```python
import sys

EXIT_OK = 0
EXIT_ERROR = 1
EXIT_USAGE = 2

def main() -> int:
    try:
        run()
        return EXIT_OK
    except UsageError as e:
        print(f"Usage error: {e}", file=sys.stderr)
        return EXIT_USAGE
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_ERROR

if __name__ == "__main__":
    sys.exit(main())
```

## Entry Point

In `pyproject.toml`:

```toml
[project.scripts]
mytool = "mypackage.__main__:main"
```

In `src/mypackage/__main__.py`:

```python
from mypackage.cli import app

def main():
    app()

if __name__ == "__main__":
    main()
```

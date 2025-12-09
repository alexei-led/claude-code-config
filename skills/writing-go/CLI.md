# Go CLI Patterns

## Framework Choice: Cobra vs urfave/cli

Both are production-ready. Choose based on project needs.

| Aspect      | Cobra                        | urfave/cli               |
| ----------- | ---------------------------- | ------------------------ |
| Community   | Larger (kubectl, hugo, gh)   | Solid (many cloud tools) |
| Code gen    | `cobra-cli` scaffolding      | Manual                   |
| Completions | Built-in shell completions   | Add-on                   |
| Docs gen    | Auto man pages, markdown     | Manual                   |
| Structure   | File-per-command scales well | Single file works        |
| Learning    | More boilerplate initially   | Simpler start            |
| Env vars    | Viper integration            | Built-in `EnvVars` field |

**Cobra fits well:**

- Complex CLIs with many subcommands
- Need shell completions and doc generation
- kubectl/gh style patterns

**urfave/cli fits well:**

- Simpler CLIs, fewer commands
- Built-in env var support needed
- Less boilerplate preferred

## Cobra Patterns

### Project Structure

```
cmd/
├── root.go
├── process.go
├── list.go
└── version.go
main.go
```

### Root Command

```go
// cmd/root.go
var (
    cfgFile string
    verbose bool
)

var rootCmd = &cobra.Command{
    Use:   "mytool",
    Short: "A helpful CLI tool",
}

func Execute() error {
    return rootCmd.Execute()
}

func init() {
    rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file")
    rootCmd.PersistentFlags().BoolVarP(&verbose, "verbose", "v", false, "verbose output")
}
```

### Subcommand

```go
// cmd/process.go
var processCmd = &cobra.Command{
    Use:   "process [file]",
    Short: "Process input files",
    Args:  cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        input := args[0]
        output, _ := cmd.Flags().GetString("output")
        dryRun, _ := cmd.Flags().GetBool("dry-run")

        if dryRun {
            fmt.Printf("Would process %s -> %s\n", input, output)
            return nil
        }
        return process(input, output)
    },
}

func init() {
    processCmd.Flags().StringP("output", "o", "output.json", "output file")
    processCmd.Flags().Bool("dry-run", false, "preview without applying")
    rootCmd.AddCommand(processCmd)
}
```

### Shell Completions

```go
var completionCmd = &cobra.Command{
    Use:   "completion [bash|zsh|fish]",
    Short: "Generate shell completions",
    Args:  cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        switch args[0] {
        case "bash":
            return rootCmd.GenBashCompletion(os.Stdout)
        case "zsh":
            return rootCmd.GenZshCompletion(os.Stdout)
        case "fish":
            return rootCmd.GenFishCompletion(os.Stdout, true)
        }
        return fmt.Errorf("unknown shell: %s", args[0])
    },
}
```

## urfave/cli Patterns

### Single File CLI

```go
func main() {
    app := &cli.App{
        Name:  "mytool",
        Usage: "A helpful CLI tool",
        Flags: []cli.Flag{
            &cli.StringFlag{
                Name:    "config",
                Aliases: []string{"c"},
                EnvVars: []string{"MYTOOL_CONFIG"},
            },
            &cli.BoolFlag{Name: "verbose"},
        },
        Commands: []*cli.Command{
            {
                Name:  "process",
                Usage: "Process input files",
                Flags: []cli.Flag{
                    &cli.StringFlag{Name: "input", Aliases: []string{"i"}, Required: true},
                    &cli.StringFlag{Name: "output", Aliases: []string{"o"}, Value: "output.json"},
                    &cli.BoolFlag{Name: "dry-run"},
                },
                Action: runProcess,
            },
        },
    }

    if err := app.Run(os.Args); err != nil {
        fmt.Fprintf(os.Stderr, "error: %v\n", err)
        os.Exit(1)
    }
}

func runProcess(c *cli.Context) error {
    if c.Bool("dry-run") {
        fmt.Printf("Would process %s -> %s\n", c.String("input"), c.String("output"))
        return nil
    }
    return process(c.String("input"), c.String("output"))
}
```

## Output Formats (Both Frameworks)

```go
type OutputFormat string

const (
    FormatTable OutputFormat = "table"
    FormatJSON  OutputFormat = "json"
    FormatCSV   OutputFormat = "csv"
)

func printItems(items []Item, format OutputFormat) error {
    switch format {
    case FormatJSON:
        return json.NewEncoder(os.Stdout).Encode(items)
    case FormatCSV:
        w := csv.NewWriter(os.Stdout)
        defer w.Flush()
        w.Write([]string{"ID", "Name", "Status"})
        for _, item := range items {
            w.Write([]string{item.ID, item.Name, item.Status})
        }
        return nil
    default:
        tw := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
        fmt.Fprintln(tw, "ID\tNAME\tSTATUS")
        for _, item := range items {
            fmt.Fprintf(tw, "%s\t%s\t%s\n", item.ID, item.Name, item.Status)
        }
        return tw.Flush()
    }
}
```

## Embedded Data

```go
//go:embed templates/*
var templates embed.FS

//go:embed data/defaults.json
var defaultsJSON []byte
```

## Build Information

```go
var (
    version   = "dev"
    commit    = "none"
    buildDate = "unknown"
)

// Build with:
// go build -ldflags "-X main.version=1.0.0 -X main.commit=$(git rev-parse HEAD)"
```

## Exit Codes

```go
const (
    ExitOK          = 0
    ExitError       = 1
    ExitUsageError  = 2
)

func main() {
    if err := run(); err != nil {
        fmt.Fprintf(os.Stderr, "error: %v\n", err)
        os.Exit(ExitError)
    }
}
```

## Logging

```go
func setupLogger(verbose bool) *slog.Logger {
    level := slog.LevelInfo
    if verbose {
        level = slog.LevelDebug
    }

    if isTerminal() {
        return slog.New(slog.NewTextHandler(os.Stderr, &slog.HandlerOptions{Level: level}))
    }
    return slog.New(slog.NewJSONHandler(os.Stderr, &slog.HandlerOptions{Level: level}))
}

func isTerminal() bool {
    fi, _ := os.Stdout.Stat()
    return (fi.Mode() & os.ModeCharDevice) != 0
}
```

---
name: cli-development
description: CLI application development covering argument parsing (Commander.js, Click, Cobra), interactive prompts, progress bars, colored output, configuration files, shell completions, man pages, cross-platform compatibility, and distribution patterns for Node.js, Python, Go, and Rust CLIs.
---

# CLI Development

This skill should be used when building command-line tools and CLI applications. It covers argument parsing, user interaction, and distribution across languages.

## When to Use This Skill

Use this skill when you need to:

- Build command-line tools and utilities
- Parse arguments and subcommands
- Create interactive CLI prompts
- Add colored output and progress indicators
- Distribute CLI tools via npm/pip/brew

## Node.js CLI with Commander

```typescript
#!/usr/bin/env node
// src/cli.ts
import { Command } from "commander";
import chalk from "chalk";
import ora from "ora";
import { version } from "../package.json";

const program = new Command()
  .name("myctl")
  .description("My awesome CLI tool")
  .version(version);

// Subcommand with options
program
  .command("deploy")
  .description("Deploy the application")
  .argument("<environment>", "target environment (dev/staging/prod)")
  .option("-t, --tag <tag>", "Docker image tag", "latest")
  .option("-d, --dry-run", "Preview changes without applying")
  .option("--no-cache", "Build without cache")
  .action(async (environment, options) => {
    const spinner = ora(`Deploying to ${environment}...`).start();
    try {
      if (options.dryRun) {
        spinner.info(chalk.yellow("Dry run — no changes applied"));
        return;
      }
      await deployApp(environment, options.tag);
      spinner.succeed(chalk.green(`Deployed to ${environment}`));
    } catch (error) {
      spinner.fail(chalk.red(`Deploy failed: ${(error as Error).message}`));
      process.exit(1);
    }
  });

// Subcommand with interactive prompt
program
  .command("init")
  .description("Initialize a new project")
  .action(async () => {
    const inquirer = (await import("inquirer")).default;
    const answers = await inquirer.prompt([
      { type: "input", name: "name", message: "Project name:" },
      { type: "list", name: "template", message: "Template:", choices: ["minimal", "full", "api"] },
      { type: "confirm", name: "git", message: "Initialize git?", default: true },
    ]);
    console.log(chalk.blue("\nCreating project:"), answers.name);
    // scaffold project...
  });

program.parse();
```

```json
// package.json
{
  "name": "myctl",
  "version": "1.0.0",
  "bin": { "myctl": "./dist/cli.js" },
  "files": ["dist"],
  "scripts": {
    "build": "tsc",
    "dev": "tsx src/cli.ts"
  }
}
```

## Python CLI with Click

```python
# cli.py
import click
from rich.console import Console
from rich.progress import track

console = Console()

@click.group()
@click.version_option()
def cli():
    """My awesome CLI tool."""
    pass

@cli.command()
@click.argument("environment", type=click.Choice(["dev", "staging", "prod"]))
@click.option("--tag", "-t", default="latest", help="Docker image tag")
@click.option("--dry-run", "-d", is_flag=True, help="Preview without applying")
def deploy(environment: str, tag: str, dry_run: bool):
    """Deploy the application to an environment."""
    if dry_run:
        console.print(f"[yellow]Dry run: would deploy {tag} to {environment}[/]")
        return

    with console.status(f"Deploying to {environment}..."):
        # deploy logic
        pass

    console.print(f"[green]Successfully deployed {tag} to {environment}[/]")

@cli.command()
@click.argument("files", nargs=-1, type=click.Path(exists=True))
@click.option("--output", "-o", type=click.Path(), default="output.json")
def process(files: tuple[str, ...], output: str):
    """Process input files."""
    results = []
    for f in track(files, description="Processing..."):
        results.append(process_file(f))

    with open(output, "w") as fp:
        json.dump(results, fp, indent=2)
    console.print(f"[green]Wrote {len(results)} results to {output}[/]")

if __name__ == "__main__":
    cli()
```

```toml
# pyproject.toml
[project.scripts]
myctl = "mypackage.cli:cli"
```

## Go CLI with Cobra

```go
// cmd/root.go
package cmd

import (
    "fmt"
    "os"
    "github.com/spf13/cobra"
    "github.com/spf13/viper"
)

var rootCmd = &cobra.Command{
    Use:   "myctl",
    Short: "My awesome CLI tool",
}

var deployCmd = &cobra.Command{
    Use:   "deploy [environment]",
    Short: "Deploy the application",
    Args:  cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        env := args[0]
        tag, _ := cmd.Flags().GetString("tag")
        dryRun, _ := cmd.Flags().GetBool("dry-run")

        if dryRun {
            fmt.Printf("Dry run: would deploy %s to %s\n", tag, env)
            return nil
        }
        return deployApp(env, tag)
    },
}

func init() {
    deployCmd.Flags().StringP("tag", "t", "latest", "Docker image tag")
    deployCmd.Flags().BoolP("dry-run", "d", false, "Preview without applying")
    rootCmd.AddCommand(deployCmd)
}

func Execute() {
    if err := rootCmd.Execute(); err != nil {
        os.Exit(1)
    }
}
```

## Output Formatting

```typescript
import chalk from "chalk";

// Status messages
console.log(chalk.green("✓"), "Operation successful");
console.log(chalk.yellow("⚠"), "Warning: disk space low");
console.log(chalk.red("✗"), "Operation failed");
console.log(chalk.blue("ℹ"), "Info: 42 files processed");

// Tables
import { table } from "table";
const data = [
  ["Name", "Status", "Version"],
  ["api", chalk.green("running"), "2.1.0"],
  ["web", chalk.green("running"), "1.5.3"],
  ["worker", chalk.red("stopped"), "1.2.0"],
];
console.log(table(data));

// Progress bar (Node.js)
import cliProgress from "cli-progress";
const bar = new cliProgress.SingleBar({}, cliProgress.Presets.shades_classic);
bar.start(100, 0);
for (let i = 0; i <= 100; i++) {
  bar.update(i);
  await new Promise(r => setTimeout(r, 50));
}
bar.stop();
```

## Configuration File Pattern

```typescript
import { cosmiconfig } from "cosmiconfig";

// Searches for config in:
// - package.json "myctl" key
// - .myctlrc (JSON/YAML)
// - .myctlrc.json / .myctlrc.yml
// - myctl.config.js / myctl.config.ts
const explorer = cosmiconfig("myctl");
const result = await explorer.search();

if (result) {
  console.log(`Config loaded from ${result.filepath}`);
  const config = result.config;
}
```

## Distribution

```bash
# npm (Node.js)
npm publish  # publishes to npmjs.com
# Users install: npm install -g myctl

# pip (Python)
python -m build && twine upload dist/*
# Users install: pip install myctl

# Go
go install github.com/user/myctl@latest

# Homebrew (any language)
# Create formula in homebrew-tap repo
brew tap user/tap && brew install myctl
```

## Additional Resources

- Commander.js: https://github.com/tj/commander.js
- Click (Python): https://click.palletsprojects.com/
- Cobra (Go): https://cobra.dev/
- Ink (React for CLIs): https://github.com/vadimdemedes/ink
- Rich (Python): https://rich.readthedocs.io/

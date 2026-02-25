---
name: go-cobra-cli
description: Go Cobra CLI patterns covering command hierarchies, flags, arguments, configuration with Viper, interactive prompts, output formatting, and shell completions.
---

# Go Cobra CLI

This skill should be used when building command-line tools with Go Cobra. It covers command hierarchies, flags, arguments, configuration, interactive prompts, and output formatting.

## When to Use This Skill

Use this skill when you need to:

- Build CLI tools with subcommands in Go
- Parse flags, arguments, and environment variables
- Integrate configuration with Viper
- Add shell completion support
- Format CLI output as tables, JSON, or YAML

## Setup

```bash
go get github.com/spf13/cobra
go get github.com/spf13/viper
go install github.com/spf13/cobra-cli@latest
```

## Project Structure

```
myctl/
├── cmd/
│   ├── root.go
│   ├── serve.go
│   ├── user.go
│   └── user_create.go
├── internal/
│   └── config/
│       └── config.go
├── main.go
└── go.mod
```

## Root Command

```go
// cmd/root.go
package cmd

import (
    "fmt"
    "os"

    "github.com/spf13/cobra"
    "github.com/spf13/viper"
)

var cfgFile string

var rootCmd = &cobra.Command{
    Use:   "myctl",
    Short: "A CLI tool for managing resources",
    Long:  "myctl is a command-line interface for managing users, services, and deployments.",
}

func init() {
    cobra.OnInitialize(initConfig)
    rootCmd.PersistentFlags().StringVar(&cfgFile, "config", "", "config file (default $HOME/.myctl.yaml)")
    rootCmd.PersistentFlags().String("output", "table", "output format: table, json, yaml")
    viper.BindPFlag("output", rootCmd.PersistentFlags().Lookup("output"))
}

func initConfig() {
    if cfgFile != "" {
        viper.SetConfigFile(cfgFile)
    } else {
        home, _ := os.UserHomeDir()
        viper.AddConfigPath(home)
        viper.SetConfigName(".myctl")
    }
    viper.SetEnvPrefix("MYCTL")
    viper.AutomaticEnv()
    viper.ReadInConfig()
}

func Run() {
    if err := rootCmd.Execute(); err != nil {
        fmt.Fprintln(os.Stderr, err)
        os.Exit(1)
    }
}
```

## Subcommands with Flags

```go
// cmd/serve.go
package cmd

import (
    "fmt"
    "github.com/spf13/cobra"
)

var serveCmd = &cobra.Command{
    Use:   "serve",
    Short: "Start the HTTP server",
    RunE: func(cmd *cobra.Command, args []string) error {
        port, _ := cmd.Flags().GetInt("port")
        host, _ := cmd.Flags().GetString("host")
        fmt.Printf("Starting server on %s:%d\n", host, port)
        return startServer(host, port)
    },
}

func init() {
    rootCmd.AddCommand(serveCmd)
    serveCmd.Flags().IntP("port", "p", 8080, "port to listen on")
    serveCmd.Flags().String("host", "0.0.0.0", "host to bind to")
}
```

## Command Groups

```go
// cmd/user.go
package cmd

import "github.com/spf13/cobra"

var userCmd = &cobra.Command{
    Use:   "user",
    Short: "Manage users",
}

func init() {
    rootCmd.AddCommand(userCmd)
}

// cmd/user_create.go
package cmd

import (
    "fmt"
    "github.com/spf13/cobra"
)

var userCreateCmd = &cobra.Command{
    Use:   "create [name]",
    Short: "Create a new user",
    Args:  cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        name := args[0]
        email, _ := cmd.Flags().GetString("email")
        role, _ := cmd.Flags().GetString("role")

        user, err := createUser(name, email, role)
        if err != nil {
            return fmt.Errorf("failed to create user: %w", err)
        }

        fmt.Printf("Created user: %s (ID: %s)\n", user.Name, user.ID)
        return nil
    },
}

func init() {
    userCmd.AddCommand(userCreateCmd)
    userCreateCmd.Flags().StringP("email", "e", "", "user email (required)")
    userCreateCmd.Flags().StringP("role", "r", "user", "user role")
    userCreateCmd.MarkFlagRequired("email")
}
```

## Argument Validation

```go
var deleteCmd = &cobra.Command{
    Use:   "delete [id]",
    Short: "Delete a resource",
    Args:  cobra.ExactArgs(1),
    ValidArgsFunction: func(cmd *cobra.Command, args []string, toComplete string) ([]string, cobra.ShellCompDirective) {
        resources := listResourceIDs()
        return resources, cobra.ShellCompDirectiveNoFileComp
    },
    RunE: func(cmd *cobra.Command, args []string) error {
        force, _ := cmd.Flags().GetBool("force")
        if !force {
            fmt.Printf("Delete %s? [y/N]: ", args[0])
            var confirm string
            fmt.Scanln(&confirm)
            if confirm != "y" && confirm != "Y" {
                fmt.Println("Cancelled.")
                return nil
            }
        }
        return deleteResource(args[0])
    },
}
```

## Output Formatting

```go
import (
    "encoding/json"
    "fmt"
    "os"
    "text/tabwriter"

    "gopkg.in/yaml.v3"
)

func printOutput(format string, data interface{}, headers []string, rows [][]string) {
    switch format {
    case "json":
        enc := json.NewEncoder(os.Stdout)
        enc.SetIndent("", "  ")
        enc.Encode(data)
    case "yaml":
        enc := yaml.NewEncoder(os.Stdout)
        enc.Encode(data)
    default:
        w := tabwriter.NewWriter(os.Stdout, 0, 0, 2, ' ', 0)
        fmt.Fprintln(w, joinTabs(headers))
        for _, row := range rows {
            fmt.Fprintln(w, joinTabs(row))
        }
        w.Flush()
    }
}
```

## Entry Point

```go
// main.go
package main

import "myctl/cmd"

func main() {
    cmd.Run()
}
```

## Shell Completions

```go
// Add completion command
var completionCmd = &cobra.Command{
    Use:   "completion [bash|zsh|fish|powershell]",
    Short: "Generate shell completion scripts",
    Args:  cobra.ExactArgs(1),
    RunE: func(cmd *cobra.Command, args []string) error {
        switch args[0] {
        case "bash":
            return rootCmd.GenBashCompletion(os.Stdout)
        case "zsh":
            return rootCmd.GenZshCompletion(os.Stdout)
        case "fish":
            return rootCmd.GenFishCompletion(os.Stdout, true)
        case "powershell":
            return rootCmd.GenPowerShellCompletionWithDesc(os.Stdout)
        default:
            return fmt.Errorf("unsupported shell: %s", args[0])
        }
    },
}
```

## Additional Resources

- Cobra: https://cobra.dev/
- GitHub: https://github.com/spf13/cobra
- Viper: https://github.com/spf13/viper

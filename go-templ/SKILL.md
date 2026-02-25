---
name: go-templ
description: Go templ patterns covering type-safe HTML templating, components, props, layouts, conditional rendering, loops, and integration with htmx and Echo/Chi.
---

# Go templ

This skill should be used when building server-rendered HTML with Go templ. It covers components, props, layouts, conditional rendering, and framework integration.

## When to Use This Skill

Use this skill when you need to:

- Build type-safe HTML templates in Go
- Create reusable components with props
- Implement layouts and page composition
- Integrate with htmx for interactivity
- Use templ with Echo, Chi, or Fiber

## Setup

```bash
go install github.com/a-h/templ/cmd/templ@latest
go get github.com/a-h/templ
```

## Basic Component

```templ
// components/hello.templ
package components

templ Hello(name string) {
    <div class="greeting">
        <h1>Hello, { name }!</h1>
    </div>
}
```

## Components with Props

```templ
// components/card.templ
package components

type CardProps struct {
    Title       string
    Description string
    ImageURL    string
    Tags        []string
}

templ Card(props CardProps) {
    <div class="card">
        if props.ImageURL != "" {
            <img src={ props.ImageURL } alt={ props.Title }/>
        }
        <div class="card-body">
            <h3>{ props.Title }</h3>
            <p>{ props.Description }</p>
            if len(props.Tags) > 0 {
                <div class="tags">
                    for _, tag := range props.Tags {
                        <span class="tag">{ tag }</span>
                    }
                </div>
            }
        </div>
    </div>
}
```

## Layouts

```templ
// layouts/base.templ
package layouts

templ Base(title string) {
    <!DOCTYPE html>
    <html lang="en">
        <head>
            <meta charset="UTF-8"/>
            <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
            <title>{ title }</title>
            <link rel="stylesheet" href="/static/style.css"/>
        </head>
        <body>
            @Nav()
            <main class="container">
                { children... }
            </main>
            @Footer()
        </body>
    </html>
}

templ Nav() {
    <nav>
        <a href="/">Home</a>
        <a href="/about">About</a>
    </nav>
}

templ Footer() {
    <footer>
        <p>Built with Go and templ</p>
    </footer>
}
```

## Pages Using Layouts

```templ
// pages/home.templ
package pages

import "myapp/layouts"
import "myapp/components"

templ HomePage(users []User) {
    @layouts.Base("Home") {
        <h1>Users</h1>
        <div class="user-grid">
            for _, user := range users {
                @components.Card(components.CardProps{
                    Title:       user.Name,
                    Description: user.Email,
                    Tags:        user.Roles,
                })
            }
        </div>
    }
}
```

## Conditional Rendering

```templ
templ UserStatus(user User) {
    <div class="status">
        if user.IsActive {
            <span class="badge active">Active</span>
        } else {
            <span class="badge inactive">Inactive</span>
        }

        switch user.Role {
            case "admin":
                <span class="role admin">Administrator</span>
            case "editor":
                <span class="role editor">Editor</span>
            default:
                <span class="role user">User</span>
        }
    </div>
}
```

## Forms

```templ
templ CreateUserForm() {
    <form method="POST" action="/users">
        <div class="field">
            <label for="name">Name</label>
            <input type="text" id="name" name="name" required/>
        </div>
        <div class="field">
            <label for="email">Email</label>
            <input type="email" id="email" name="email" required/>
        </div>
        <button type="submit">Create User</button>
    </form>
}

templ FormErrors(errors map[string]string) {
    if len(errors) > 0 {
        <div class="errors">
            for field, msg := range errors {
                <p class="error">{ field }: { msg }</p>
            }
        </div>
    }
}
```

## Integration with Echo

```go
package main

import (
    "myapp/pages"
    "github.com/a-h/templ"
    "github.com/labstack/echo/v4"
)

func Render(c echo.Context, status int, t templ.Component) error {
    c.Response().Header().Set("Content-Type", "text/html")
    c.Response().WriteHeader(status)
    return t.Render(c.Request().Context(), c.Response().Writer)
}

func main() {
    e := echo.New()

    e.GET("/", func(c echo.Context) error {
        users := fetchUsers()
        return Render(c, 200, pages.HomePage(users))
    })

    e.Logger.Fatal(e.Start(":8080"))
}
```

## Generate Go Code

```bash
templ generate              # generate Go from .templ files
templ generate --watch      # watch mode for development
templ fmt .                 # format templ files
```

## Additional Resources

- templ: https://templ.guide/
- GitHub: https://github.com/a-h/templ
- Examples: https://github.com/a-h/templ/tree/main/examples

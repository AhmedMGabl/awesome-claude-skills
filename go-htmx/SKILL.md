---
name: go-htmx
description: Go htmx integration patterns covering server-side rendering with partial updates, triggers, swapping strategies, form handling, infinite scroll, and live search.
---

# Go + htmx

This skill should be used when building interactive web applications with Go and htmx. It covers partial updates, triggers, swapping strategies, forms, and common UI patterns.

## When to Use This Skill

Use this skill when you need to:

- Add interactivity to Go server-rendered pages without JavaScript
- Implement partial page updates with htmx
- Build live search, infinite scroll, and inline editing
- Handle form submissions with htmx
- Use htmx triggers, swapping, and out-of-band updates

## Setup

Include htmx via CDN in your base template:

```html
<script src="https://unpkg.com/htmx.org@2.0.0"></script>
```

## Basic Pattern: Click to Load

```html
<!-- Button triggers GET request, replaces target -->
<button hx-get="/api/users" hx-target="#user-list" hx-swap="innerHTML">
    Load Users
</button>
<div id="user-list"></div>
```

```go
func handleListUsers(w http.ResponseWriter, r *http.Request) {
    users := fetchUsers()
    tmpl.ExecuteTemplate(w, "user-list", users)
}
```

```html
{{define "user-list"}}
{{range .}}
<div class="user-card">
    <h3>{{.Name}}</h3>
    <p>{{.Email}}</p>
</div>
{{end}}
{{end}}
```

## Live Search

```html
<input type="search" name="q"
    hx-get="/search"
    hx-trigger="input changed delay:300ms"
    hx-target="#results"
    placeholder="Search users..."/>
<div id="results"></div>
```

```go
func handleSearch(w http.ResponseWriter, r *http.Request) {
    query := r.URL.Query().Get("q")
    results := searchUsers(query)
    tmpl.ExecuteTemplate(w, "search-results", results)
}
```

## Inline Editing

```html
{{define "user-display"}}
<div id="user-{{.ID}}" class="user-row">
    <span>{{.Name}}</span>
    <span>{{.Email}}</span>
    <button hx-get="/users/{{.ID}}/edit" hx-target="#user-{{.ID}}" hx-swap="outerHTML">
        Edit
    </button>
</div>
{{end}}

{{define "user-edit-form"}}
<form id="user-{{.ID}}" class="user-row"
    hx-put="/users/{{.ID}}"
    hx-target="#user-{{.ID}}"
    hx-swap="outerHTML">
    <input name="name" value="{{.Name}}"/>
    <input name="email" value="{{.Email}}"/>
    <button type="submit">Save</button>
    <button hx-get="/users/{{.ID}}" hx-target="#user-{{.ID}}" hx-swap="outerHTML">
        Cancel
    </button>
</form>
{{end}}
```

```go
func handleEditUser(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    user := getUser(id)

    switch r.Method {
    case http.MethodGet:
        tmpl.ExecuteTemplate(w, "user-edit-form", user)
    case http.MethodPut:
        r.ParseForm()
        user.Name = r.FormValue("name")
        user.Email = r.FormValue("email")
        saveUser(user)
        tmpl.ExecuteTemplate(w, "user-display", user)
    }
}
```

## Infinite Scroll

```html
{{define "user-page"}}
{{range .Users}}
<div class="user-card">
    <h3>{{.Name}}</h3>
    <p>{{.Email}}</p>
</div>
{{end}}
{{if .HasMore}}
<div hx-get="/users?page={{.NextPage}}"
     hx-trigger="revealed"
     hx-swap="outerHTML">
    Loading more...
</div>
{{end}}
{{end}}
```

```go
func handleUsers(w http.ResponseWriter, r *http.Request) {
    page, _ := strconv.Atoi(r.URL.Query().Get("page"))
    if page < 1 { page = 1 }
    limit := 20

    users := fetchUsersPaginated(page, limit)
    hasMore := len(users) == limit

    data := map[string]interface{}{
        "Users":    users,
        "HasMore":  hasMore,
        "NextPage": page + 1,
    }
    tmpl.ExecuteTemplate(w, "user-page", data)
}
```

## Delete with Confirmation

```html
<button hx-delete="/users/{{.ID}}"
        hx-target="#user-{{.ID}}"
        hx-swap="outerHTML"
        hx-confirm="Delete this user?">
    Delete
</button>
```

```go
func handleDeleteUser(w http.ResponseWriter, r *http.Request) {
    id := chi.URLParam(r, "id")
    deleteUser(id)
    w.WriteHeader(http.StatusOK)
    // Return empty response - element is removed
}
```

## Out-of-Band Updates

```go
// Update multiple page elements in one response
func handleCreateUser(w http.ResponseWriter, r *http.Request) {
    r.ParseForm()
    user := createUser(r.FormValue("name"), r.FormValue("email"))

    // Primary response: new user row
    tmpl.ExecuteTemplate(w, "user-row", user)

    // Out-of-band: update the user count
    fmt.Fprintf(w, `<span id="user-count" hx-swap-oob="true">%d users</span>`, getUserCount())
}
```

## htmx Request Headers

```go
func isHTMXRequest(r *http.Request) bool {
    return r.Header.Get("HX-Request") == "true"
}

func handlePage(w http.ResponseWriter, r *http.Request) {
    users := fetchUsers()
    if isHTMXRequest(r) {
        // Return partial for htmx
        tmpl.ExecuteTemplate(w, "user-list", users)
    } else {
        // Return full page for direct navigation
        tmpl.ExecuteTemplate(w, "full-page", users)
    }
}
```

## Additional Resources

- htmx: https://htmx.org/
- htmx Reference: https://htmx.org/reference/
- Go + htmx examples: https://github.com/a-h/templ/tree/main/examples

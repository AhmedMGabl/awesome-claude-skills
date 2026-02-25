---
name: dotnet-blazor
description: Blazor patterns covering components, data binding, event handling, forms, dependency injection, JavaScript interop, and server/WebAssembly render modes.
---

# Blazor

This skill should be used when building interactive web UIs with Blazor. It covers components, data binding, events, forms, DI, JS interop, and render modes.

## When to Use This Skill

Use this skill when you need to:

- Build interactive web UIs with C#
- Create reusable Blazor components
- Handle forms and validation
- Use JavaScript interop
- Choose between Server and WebAssembly modes

## Component Basics

```razor
@* Components/Counter.razor *@
<h3>Counter: @count</h3>
<button class="btn btn-primary" @onclick="Increment">Click me</button>

@code {
    private int count = 0;

    [Parameter]
    public int InitialCount { get; set; } = 0;

    [Parameter]
    public EventCallback<int> OnCountChanged { get; set; }

    protected override void OnInitialized()
    {
        count = InitialCount;
    }

    private async Task Increment()
    {
        count++;
        await OnCountChanged.InvokeAsync(count);
    }
}
```

## Data Binding

```razor
@* Two-way binding *@
<input @bind="name" />
<input @bind="name" @bind:event="oninput" />
<input @bind="date" @bind:format="yyyy-MM-dd" />

@* Component parameter binding *@
<SearchBox @bind-Query="searchQuery" />

@code {
    private string name = "";
    private DateTime date = DateTime.Today;
    private string searchQuery = "";
}
```

```razor
@* SearchBox.razor *@
<input value="@Query" @oninput="OnInput" placeholder="Search..." />

@code {
    [Parameter] public string Query { get; set; } = "";
    [Parameter] public EventCallback<string> QueryChanged { get; set; }

    private async Task OnInput(ChangeEventArgs e)
    {
        await QueryChanged.InvokeAsync(e.Value?.ToString() ?? "");
    }
}
```

## Forms and Validation

```razor
<EditForm Model="user" OnValidSubmit="HandleSubmit" FormName="user-form">
    <DataAnnotationsValidator />
    <ValidationSummary />

    <div class="mb-3">
        <label>Name</label>
        <InputText @bind-Value="user.Name" class="form-control" />
        <ValidationMessage For="() => user.Name" />
    </div>

    <div class="mb-3">
        <label>Email</label>
        <InputText @bind-Value="user.Email" class="form-control" />
        <ValidationMessage For="() => user.Email" />
    </div>

    <div class="mb-3">
        <label>Role</label>
        <InputSelect @bind-Value="user.Role" class="form-select">
            <option value="">Select role...</option>
            <option value="User">User</option>
            <option value="Admin">Admin</option>
        </InputSelect>
    </div>

    <button type="submit" class="btn btn-primary" disabled="@isSubmitting">
        @(isSubmitting ? "Saving..." : "Save")
    </button>
</EditForm>

@code {
    private UserModel user = new();
    private bool isSubmitting;

    private async Task HandleSubmit()
    {
        isSubmitting = true;
        await UserService.CreateAsync(user);
        isSubmitting = false;
        Navigation.NavigateTo("/users");
    }
}
```

## Dependency Injection

```csharp
// Program.cs
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddHttpClient<ApiClient>(client =>
    client.BaseAddress = new Uri("https://api.example.com"));
```

```razor
@inject IUserService UserService
@inject NavigationManager Navigation
@inject IJSRuntime JS

@code {
    private List<User> users = [];

    protected override async Task OnInitializedAsync()
    {
        users = await UserService.GetAllAsync();
    }
}
```

## Lifecycle Methods

```razor
@implements IAsyncDisposable

@code {
    private Timer? timer;

    protected override void OnInitialized() { /* sync init */ }

    protected override async Task OnInitializedAsync()
    {
        // Async initialization - called once
        await LoadDataAsync();
    }

    protected override void OnParametersSet()
    {
        // Called when parameters change
    }

    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (firstRender)
        {
            // DOM is available, safe to call JS interop
            await JS.InvokeVoidAsync("initChart", chartElement);
        }
    }

    public async ValueTask DisposeAsync()
    {
        timer?.Dispose();
    }
}
```

## JavaScript Interop

```razor
@inject IJSRuntime JS

<div @ref="chartElement"></div>

@code {
    private ElementReference chartElement;

    protected override async Task OnAfterRenderAsync(bool firstRender)
    {
        if (firstRender)
        {
            await JS.InvokeVoidAsync("createChart", chartElement, data);
        }
    }

    private async Task<string> GetClipboard()
    {
        return await JS.InvokeAsync<string>("navigator.clipboard.readText");
    }
}
```

## Render Modes (.NET 8+)

```razor
@* Static SSR (default) *@
@rendermode InteractiveServer    @* Server-side interactivity via SignalR *@
@rendermode InteractiveWebAssembly   @* Client-side via WebAssembly *@
@rendermode InteractiveAuto      @* Server first, then WebAssembly *@

@* Per-component in parent *@
<Counter @rendermode="InteractiveServer" />

@* Global in App.razor *@
<Routes @rendermode="InteractiveServer" />
```

## Additional Resources

- Blazor: https://learn.microsoft.com/en-us/aspnet/core/blazor/
- Components: https://learn.microsoft.com/en-us/aspnet/core/blazor/components/
- Forms: https://learn.microsoft.com/en-us/aspnet/core/blazor/forms/

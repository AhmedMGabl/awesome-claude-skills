---
name: dotnet-aspnetcore
description: ASP.NET Core patterns covering minimal APIs, controllers, middleware, dependency injection, authentication, Entity Framework Core, and deployment configuration.
---

# ASP.NET Core

This skill should be used when building web applications with ASP.NET Core. It covers minimal APIs, controllers, middleware, DI, authentication, EF Core, and deployment.

## When to Use This Skill

Use this skill when you need to:

- Build REST APIs with minimal APIs or controllers
- Configure middleware and dependency injection
- Implement authentication and authorization
- Use Entity Framework Core for data access
- Deploy ASP.NET Core applications

## Minimal API

```csharp
var builder = WebApplication.CreateBuilder(args);

builder.Services.AddDbContext<AppDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("Default")));
builder.Services.AddScoped<IUserService, UserService>();
builder.Services.AddAuthentication().AddJwtBearer();
builder.Services.AddAuthorization();

var app = builder.Build();

app.UseAuthentication();
app.UseAuthorization();

var users = app.MapGroup("/api/users").RequireAuthorization();

users.MapGet("/", async (IUserService service, int page = 1, int size = 20) =>
    Results.Ok(await service.GetAllAsync(page, size)));

users.MapGet("/{id:int}", async (int id, IUserService service) =>
    await service.GetByIdAsync(id) is { } user
        ? Results.Ok(user)
        : Results.NotFound());

users.MapPost("/", async (CreateUserRequest request, IUserService service) =>
{
    var user = await service.CreateAsync(request);
    return Results.Created($"/api/users/{user.Id}", user);
});

users.MapPut("/{id:int}", async (int id, UpdateUserRequest request, IUserService service) =>
{
    await service.UpdateAsync(id, request);
    return Results.NoContent();
});

users.MapDelete("/{id:int}", async (int id, IUserService service) =>
{
    await service.DeleteAsync(id);
    return Results.NoContent();
}).RequireAuthorization("AdminOnly");

app.Run();
```

## Controller-Based API

```csharp
[ApiController]
[Route("api/[controller]")]
public class ProductsController : ControllerBase
{
    private readonly IProductService _productService;

    public ProductsController(IProductService productService)
    {
        _productService = productService;
    }

    [HttpGet]
    public async Task<ActionResult<PagedResult<ProductDto>>> GetAll(
        [FromQuery] int page = 1, [FromQuery] int size = 20)
    {
        return Ok(await _productService.GetAllAsync(page, size));
    }

    [HttpGet("{id:int}")]
    [ProducesResponseType(StatusCodes.Status200OK)]
    [ProducesResponseType(StatusCodes.Status404NotFound)]
    public async Task<ActionResult<ProductDto>> GetById(int id)
    {
        var product = await _productService.GetByIdAsync(id);
        return product is null ? NotFound() : Ok(product);
    }

    [HttpPost]
    [Authorize(Roles = "Admin")]
    public async Task<ActionResult<ProductDto>> Create([FromBody] CreateProductRequest request)
    {
        var product = await _productService.CreateAsync(request);
        return CreatedAtAction(nameof(GetById), new { id = product.Id }, product);
    }
}
```

## Middleware

```csharp
public class ExceptionHandlingMiddleware
{
    private readonly RequestDelegate _next;
    private readonly ILogger<ExceptionHandlingMiddleware> _logger;

    public ExceptionHandlingMiddleware(RequestDelegate next,
        ILogger<ExceptionHandlingMiddleware> logger)
    {
        _next = next;
        _logger = logger;
    }

    public async Task InvokeAsync(HttpContext context)
    {
        try
        {
            await _next(context);
        }
        catch (NotFoundException ex)
        {
            context.Response.StatusCode = 404;
            await context.Response.WriteAsJsonAsync(new { error = ex.Message });
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unhandled exception");
            context.Response.StatusCode = 500;
            await context.Response.WriteAsJsonAsync(new { error = "Internal server error" });
        }
    }
}

// Register
app.UseMiddleware<ExceptionHandlingMiddleware>();
```

## Entity Framework Core

```csharp
public class AppDbContext : DbContext
{
    public DbSet<User> Users => Set<User>();
    public DbSet<Post> Posts => Set<Post>();

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<User>(entity =>
        {
            entity.HasIndex(e => e.Email).IsUnique();
            entity.HasMany(e => e.Posts)
                .WithOne(e => e.Author)
                .HasForeignKey(e => e.AuthorId)
                .OnDelete(DeleteBehavior.Cascade);
        });
    }
}
```

## JWT Authentication

```csharp
builder.Services.AddAuthentication(JwtBearerDefaults.AuthenticationScheme)
    .AddJwtBearer(options =>
    {
        options.TokenValidationParameters = new TokenValidationParameters
        {
            ValidateIssuer = true,
            ValidateAudience = true,
            ValidateLifetime = true,
            ValidIssuer = builder.Configuration["Jwt:Issuer"],
            ValidAudience = builder.Configuration["Jwt:Audience"],
            IssuerSigningKey = new SymmetricSecurityKey(
                Encoding.UTF8.GetBytes(builder.Configuration["Jwt:Key"]!))
        };
    });

builder.Services.AddAuthorization(options =>
{
    options.AddPolicy("AdminOnly", policy => policy.RequireRole("Admin"));
});
```

## Configuration

```json
// appsettings.json
{
  "ConnectionStrings": {
    "Default": "Host=localhost;Database=myapp;Username=postgres;Password=secret"
  },
  "Jwt": {
    "Key": "your-secret-key-at-least-32-chars",
    "Issuer": "myapp",
    "Audience": "myapp"
  }
}
```

## Additional Resources

- ASP.NET Core: https://learn.microsoft.com/en-us/aspnet/core/
- EF Core: https://learn.microsoft.com/en-us/ef/core/
- Minimal APIs: https://learn.microsoft.com/en-us/aspnet/core/fundamentals/minimal-apis

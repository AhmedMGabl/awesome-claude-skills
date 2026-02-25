---
name: dotnet-entityframework
description: Entity Framework Core patterns covering DbContext, entity configuration, migrations, LINQ queries, relationships, change tracking, and performance optimization.
---

# Entity Framework Core

This skill should be used when working with Entity Framework Core for .NET data access. It covers DbContext, entity configuration, migrations, LINQ queries, relationships, and performance.

## When to Use This Skill

Use this skill when you need to:

- Configure DbContext and entity models
- Write LINQ queries for data access
- Manage database migrations
- Optimize query performance
- Handle relationships and navigation properties

## Entity Configuration

```csharp
public class User
{
    public int Id { get; set; }
    public required string Name { get; set; }
    public required string Email { get; set; }
    public DateTime CreatedAt { get; set; } = DateTime.UtcNow;
    public List<Post> Posts { get; set; } = [];
    public UserProfile? Profile { get; set; }
}

public class Post
{
    public int Id { get; set; }
    public required string Title { get; set; }
    public required string Content { get; set; }
    public bool Published { get; set; }
    public int AuthorId { get; set; }
    public User Author { get; set; } = null!;
    public List<Tag> Tags { get; set; } = [];
}

public class UserConfiguration : IEntityTypeConfiguration<User>
{
    public void Configure(EntityTypeBuilder<User> builder)
    {
        builder.HasIndex(u => u.Email).IsUnique();
        builder.Property(u => u.Name).HasMaxLength(100);
        builder.Property(u => u.Email).HasMaxLength(255);
        builder.HasOne(u => u.Profile)
            .WithOne(p => p.User)
            .HasForeignKey<UserProfile>(p => p.UserId);
    }
}
```

## DbContext

```csharp
public class AppDbContext : DbContext
{
    public DbSet<User> Users => Set<User>();
    public DbSet<Post> Posts => Set<Post>();
    public DbSet<Tag> Tags => Set<Tag>();

    public AppDbContext(DbContextOptions<AppDbContext> options) : base(options) { }

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.ApplyConfigurationsFromAssembly(typeof(AppDbContext).Assembly);

        // Global query filter (soft delete)
        modelBuilder.Entity<Post>().HasQueryFilter(p => !p.IsDeleted);
    }

    public override Task<int> SaveChangesAsync(CancellationToken cancellationToken = default)
    {
        foreach (var entry in ChangeTracker.Entries<BaseEntity>())
        {
            if (entry.State == EntityState.Modified)
                entry.Entity.UpdatedAt = DateTime.UtcNow;
        }
        return base.SaveChangesAsync(cancellationToken);
    }
}
```

## Queries

```csharp
public class UserRepository
{
    private readonly AppDbContext _db;

    public UserRepository(AppDbContext db) => _db = db;

    public async Task<User?> GetByIdAsync(int id)
    {
        return await _db.Users
            .Include(u => u.Profile)
            .FirstOrDefaultAsync(u => u.Id == id);
    }

    public async Task<List<User>> GetWithPostsAsync(int page, int size)
    {
        return await _db.Users
            .Include(u => u.Posts.Where(p => p.Published))
            .OrderByDescending(u => u.CreatedAt)
            .Skip((page - 1) * size)
            .Take(size)
            .AsSplitQuery()
            .ToListAsync();
    }

    public async Task<List<UserDto>> SearchAsync(string term)
    {
        return await _db.Users
            .Where(u => EF.Functions.Like(u.Name, $"%{term}%"))
            .Select(u => new UserDto(u.Id, u.Name, u.Email, u.Posts.Count))
            .ToListAsync();
    }

    // Raw SQL when needed
    public async Task<List<User>> GetTopAuthorsAsync()
    {
        return await _db.Users
            .FromSqlRaw("""
                SELECT u.* FROM users u
                JOIN posts p ON p.author_id = u.id
                WHERE p.published = true
                GROUP BY u.id
                ORDER BY COUNT(p.id) DESC
                LIMIT 10
                """)
            .ToListAsync();
    }
}
```

## Migrations

```bash
dotnet ef migrations add InitialCreate
dotnet ef migrations add AddUserProfile
dotnet ef database update
dotnet ef migrations script --idempotent -o migration.sql
```

## Transactions

```csharp
public async Task TransferPostAsync(int postId, int newAuthorId)
{
    await using var transaction = await _db.Database.BeginTransactionAsync();
    try
    {
        var post = await _db.Posts.FindAsync(postId)
            ?? throw new NotFoundException("Post not found");
        post.AuthorId = newAuthorId;

        var log = new AuditLog { Action = "transfer", EntityId = postId };
        _db.AuditLogs.Add(log);

        await _db.SaveChangesAsync();
        await transaction.CommitAsync();
    }
    catch
    {
        await transaction.RollbackAsync();
        throw;
    }
}
```

## Performance

```csharp
// No-tracking for read-only queries
var users = await _db.Users
    .AsNoTracking()
    .ToListAsync();

// Compiled queries for hot paths
private static readonly Func<AppDbContext, int, Task<User?>> GetUserById =
    EF.CompileAsyncQuery((AppDbContext db, int id) =>
        db.Users.FirstOrDefault(u => u.Id == id));

// Bulk operations
await _db.Posts
    .Where(p => p.CreatedAt < cutoff)
    .ExecuteDeleteAsync();

await _db.Posts
    .Where(p => p.AuthorId == oldId)
    .ExecuteUpdateAsync(s => s.SetProperty(p => p.AuthorId, newId));
```

## Additional Resources

- EF Core: https://learn.microsoft.com/en-us/ef/core/
- Querying: https://learn.microsoft.com/en-us/ef/core/querying/
- Performance: https://learn.microsoft.com/en-us/ef/core/performance/

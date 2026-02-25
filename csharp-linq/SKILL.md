---
name: csharp-linq
description: C# LINQ patterns covering query syntax, method syntax, deferred execution, grouping, joins, projections, custom extension methods, and async LINQ with EF Core.
---

# C# LINQ

This skill should be used when writing LINQ queries in C#. It covers query and method syntax, deferred execution, grouping, joins, projections, and async LINQ.

## When to Use This Skill

Use this skill when you need to:

- Query collections with LINQ expressions
- Use grouping, joins, and projections
- Understand deferred vs immediate execution
- Write custom LINQ extension methods
- Use async LINQ with Entity Framework Core

## Method Syntax Basics

```csharp
var products = new List<Product>
{
    new("Laptop", 999.99m, "Electronics"),
    new("Mouse", 29.99m, "Electronics"),
    new("Desk", 249.99m, "Furniture"),
    new("Chair", 399.99m, "Furniture"),
};

// Filter, order, project
var affordable = products
    .Where(p => p.Price < 500)
    .OrderBy(p => p.Price)
    .Select(p => new { p.Name, p.Price })
    .ToList();

// First, Single, Any, All
var cheapest = products.MinBy(p => p.Price);
var hasExpensive = products.Any(p => p.Price > 900);
var allCategorized = products.All(p => !string.IsNullOrEmpty(p.Category));

// Aggregation
var totalValue = products.Sum(p => p.Price);
var avgPrice = products.Average(p => p.Price);
var count = products.Count(p => p.Category == "Electronics");
```

## Grouping

```csharp
// Group by category
var byCategory = products
    .GroupBy(p => p.Category)
    .Select(g => new
    {
        Category = g.Key,
        Count = g.Count(),
        Total = g.Sum(p => p.Price),
        Average = g.Average(p => p.Price),
        Products = g.OrderBy(p => p.Name).ToList()
    })
    .OrderByDescending(g => g.Total);

// Multiple keys
var byYearMonth = orders
    .GroupBy(o => new { o.Date.Year, o.Date.Month })
    .Select(g => new
    {
        g.Key.Year,
        g.Key.Month,
        Revenue = g.Sum(o => o.Total),
        OrderCount = g.Count()
    });
```

## Joins

```csharp
// Inner join
var orderDetails = orders
    .Join(customers,
        order => order.CustomerId,
        customer => customer.Id,
        (order, customer) => new
        {
            OrderId = order.Id,
            CustomerName = customer.Name,
            order.Total
        });

// Left join with GroupJoin
var customersWithOrders = customers
    .GroupJoin(orders,
        c => c.Id,
        o => o.CustomerId,
        (customer, customerOrders) => new
        {
            customer.Name,
            OrderCount = customerOrders.Count(),
            TotalSpent = customerOrders.Sum(o => o.Total)
        });

// Zip
var pairs = names.Zip(scores, (name, score) => new { name, score });
```

## Query Syntax

```csharp
// Equivalent to method syntax, sometimes more readable for joins
var query =
    from o in orders
    join c in customers on o.CustomerId equals c.Id
    join p in products on o.ProductId equals p.Id
    where o.Date >= startDate
    orderby o.Date descending
    select new
    {
        OrderDate = o.Date,
        CustomerName = c.Name,
        ProductName = p.Name,
        o.Quantity,
        LineTotal = o.Quantity * p.Price
    };

// Let clause for intermediate calculations
var discounted =
    from p in products
    let discountedPrice = p.Price * 0.9m
    where discountedPrice < 300
    select new { p.Name, Original = p.Price, Discounted = discountedPrice };
```

## Deferred Execution

```csharp
// Deferred: query is NOT executed yet
var query = products.Where(p => p.Price > 100);

// Executed when enumerated
foreach (var p in query) { /* executes here */ }

// Immediate execution operators
var list = query.ToList();        // materializes
var array = query.ToArray();      // materializes
var dict = query.ToDictionary(p => p.Id);
var first = query.First();        // executes
var count = query.Count();        // executes
var any = query.Any();            // executes
```

## Set Operations

```csharp
var setA = new[] { 1, 2, 3, 4, 5 };
var setB = new[] { 3, 4, 5, 6, 7 };

var union = setA.Union(setB);           // 1,2,3,4,5,6,7
var intersect = setA.Intersect(setB);   // 3,4,5
var except = setA.Except(setB);         // 1,2
var distinct = setA.Concat(setB).Distinct();

// Custom equality
var uniqueUsers = users.DistinctBy(u => u.Email);
```

## Custom Extension Methods

```csharp
public static class LinqExtensions
{
    public static IEnumerable<IEnumerable<T>> Batch<T>(
        this IEnumerable<T> source, int size)
    {
        var batch = new List<T>(size);
        foreach (var item in source)
        {
            batch.Add(item);
            if (batch.Count == size)
            {
                yield return batch;
                batch = new List<T>(size);
            }
        }
        if (batch.Count > 0) yield return batch;
    }

    public static IEnumerable<T> WhereNotNull<T>(this IEnumerable<T?> source) where T : class
    {
        return source.Where(x => x is not null)!;
    }
}

// Usage
foreach (var batch in items.Batch(100))
{
    await ProcessBatchAsync(batch.ToList());
}
```

## Async LINQ with EF Core

```csharp
// Async enumeration
var users = await _db.Users
    .Where(u => u.IsActive)
    .OrderBy(u => u.Name)
    .ToListAsync();

var user = await _db.Users.FirstOrDefaultAsync(u => u.Email == email);
var exists = await _db.Users.AnyAsync(u => u.Email == email);
var count = await _db.Users.CountAsync(u => u.Role == "Admin");

// Async streaming
await foreach (var user in _db.Users.AsAsyncEnumerable())
{
    await ProcessUserAsync(user);
}
```

## Additional Resources

- LINQ: https://learn.microsoft.com/en-us/dotnet/csharp/linq/
- Standard Query Operators: https://learn.microsoft.com/en-us/dotnet/csharp/programming-guide/concepts/linq/standard-query-operators-overview
- EF Core LINQ: https://learn.microsoft.com/en-us/ef/core/querying/

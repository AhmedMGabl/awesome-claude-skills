---
name: rust-testing
description: Rust testing patterns covering unit tests, integration tests, property-based testing, mocking with mockall, async test utilities, test fixtures, and benchmarking.
---

# Rust Testing

This skill should be used when writing tests for Rust applications. It covers unit tests, integration tests, property-based testing, mocking, and benchmarking.

## When to Use This Skill

Use this skill when you need to:

- Write unit and integration tests in Rust
- Use test helpers, fixtures, and setup/teardown
- Mock traits with mockall
- Test async code with tokio::test
- Write property-based tests with proptest

## Unit Tests

```rust
pub fn divide(a: f64, b: f64) -> Result<f64, String> {
    if b == 0.0 {
        return Err("division by zero".into());
    }
    Ok(a / b)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_divide_ok() {
        assert_eq!(divide(10.0, 2.0).unwrap(), 5.0);
    }

    #[test]
    fn test_divide_by_zero() {
        let result = divide(10.0, 0.0);
        assert!(result.is_err());
        assert_eq!(result.unwrap_err(), "division by zero");
    }

    #[test]
    fn test_divide_negative() {
        let result = divide(-10.0, 2.0).unwrap();
        assert!((result - (-5.0)).abs() < f64::EPSILON);
    }

    #[test]
    #[should_panic(expected = "overflow")]
    fn test_overflow() {
        might_overflow(u32::MAX);
    }
}
```

## Mocking with mockall

```toml
# Cargo.toml
[dev-dependencies]
mockall = "0.12"
```

```rust
use mockall::automock;

#[automock]
trait UserRepository {
    fn find_by_id(&self, id: i64) -> Option<User>;
    fn create(&self, name: &str, email: &str) -> Result<User, String>;
}

struct UserService<R: UserRepository> {
    repo: R,
}

impl<R: UserRepository> UserService<R> {
    fn get_user(&self, id: i64) -> Option<User> {
        self.repo.find_by_id(id)
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_get_user_found() {
        let mut mock = MockUserRepository::new();
        mock.expect_find_by_id()
            .with(mockall::predicate::eq(1))
            .times(1)
            .returning(|_| Some(User { id: 1, name: "Alice".into(), email: "alice@example.com".into() }));

        let service = UserService { repo: mock };
        let user = service.get_user(1).unwrap();
        assert_eq!(user.name, "Alice");
    }

    #[test]
    fn test_get_user_not_found() {
        let mut mock = MockUserRepository::new();
        mock.expect_find_by_id()
            .returning(|_| None);

        let service = UserService { repo: mock };
        assert!(service.get_user(999).is_none());
    }
}
```

## Async Tests

```rust
#[cfg(test)]
mod tests {
    use super::*;

    #[tokio::test]
    async fn test_fetch_user() {
        let pool = setup_test_db().await;
        let user = create_test_user(&pool, "Alice").await;

        let result = fetch_user(&pool, user.id).await.unwrap();
        assert_eq!(result.name, "Alice");

        cleanup_test_db(&pool).await;
    }

    #[tokio::test]
    async fn test_concurrent_operations() {
        let (tx, mut rx) = tokio::sync::mpsc::channel(10);

        tokio::spawn(async move {
            tx.send("hello").await.unwrap();
        });

        let msg = rx.recv().await.unwrap();
        assert_eq!(msg, "hello");
    }
}
```

## Integration Tests

```rust
// tests/api_tests.rs
use myapp::create_app;

#[tokio::test]
async fn test_create_user_api() {
    let app = create_app().await;

    let response = app
        .oneshot(
            axum::http::Request::builder()
                .method("POST")
                .uri("/api/users")
                .header("content-type", "application/json")
                .body(r#"{"name":"Bob","email":"bob@example.com"}"#.into())
                .unwrap(),
        )
        .await
        .unwrap();

    assert_eq!(response.status(), 201);
}
```

## Property-Based Testing

```toml
# Cargo.toml
[dev-dependencies]
proptest = "1"
```

```rust
use proptest::prelude::*;

fn reverse_string(s: &str) -> String {
    s.chars().rev().collect()
}

proptest! {
    #[test]
    fn test_reverse_twice_is_identity(s in "\\PC*") {
        let reversed = reverse_string(&reverse_string(&s));
        prop_assert_eq!(reversed, s);
    }

    #[test]
    fn test_reverse_length(s in "\\PC*") {
        prop_assert_eq!(reverse_string(&s).len(), s.len());
    }

    #[test]
    fn test_add_commutative(a in 0i64..1000, b in 0i64..1000) {
        prop_assert_eq!(a + b, b + a);
    }
}
```

## Test Fixtures

```rust
#[cfg(test)]
mod tests {
    struct TestFixture {
        db: PgPool,
        user: User,
    }

    impl TestFixture {
        async fn setup() -> Self {
            let db = create_test_pool().await;
            let user = seed_test_user(&db).await;
            TestFixture { db, user }
        }

        async fn teardown(self) {
            cleanup_test_data(&self.db).await;
        }
    }

    #[tokio::test]
    async fn test_with_fixture() {
        let fixture = TestFixture::setup().await;

        let result = get_user(&fixture.db, fixture.user.id).await;
        assert!(result.is_ok());

        fixture.teardown().await;
    }
}
```

## Running Tests

```bash
cargo test                         # run all tests
cargo test test_name               # run specific test
cargo test -- --nocapture          # show println output
cargo test -- --test-threads=1     # run sequentially
cargo test --lib                   # unit tests only
cargo test --test api_tests        # specific integration test
cargo test --release               # test with optimizations
```

## Additional Resources

- Testing: https://doc.rust-lang.org/book/ch11-00-testing.html
- mockall: https://docs.rs/mockall/
- proptest: https://proptest-rs.github.io/proptest/

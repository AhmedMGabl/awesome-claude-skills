---
name: java-junit5
description: JUnit 5 testing patterns covering assertions, parameterized tests, nested tests, extensions, MockMvc, Testcontainers, and Spring Boot test slices.
---

# Java JUnit 5 Testing

This skill should be used when writing tests for Java applications with JUnit 5. It covers assertions, parameterized tests, extensions, MockMvc, Testcontainers, and Spring Boot testing.

## When to Use This Skill

Use this skill when you need to:

- Write unit and integration tests with JUnit 5
- Use parameterized and nested tests
- Mock dependencies with Mockito
- Test Spring Boot controllers with MockMvc
- Use Testcontainers for database tests

## Basic Tests

```java
import org.junit.jupiter.api.*;
import static org.assertj.core.api.Assertions.*;

class UserServiceTest {

    private UserService userService;

    @BeforeEach
    void setUp() {
        userService = new UserService(new InMemoryUserRepository());
    }

    @Test
    @DisplayName("should create user with valid data")
    void createUser() {
        User user = userService.create("Alice", "alice@example.com");

        assertThat(user.getName()).isEqualTo("Alice");
        assertThat(user.getEmail()).isEqualTo("alice@example.com");
        assertThat(user.getId()).isNotNull();
    }

    @Test
    void shouldThrowOnDuplicateEmail() {
        userService.create("Alice", "alice@example.com");

        assertThatThrownBy(() -> userService.create("Bob", "alice@example.com"))
            .isInstanceOf(DuplicateEmailException.class)
            .hasMessageContaining("alice@example.com");
    }
}
```

## Parameterized Tests

```java
@ParameterizedTest
@ValueSource(strings = {"", " ", "  "})
void shouldRejectBlankName(String name) {
    assertThatThrownBy(() -> userService.create(name, "test@example.com"))
        .isInstanceOf(IllegalArgumentException.class);
}

@ParameterizedTest
@CsvSource({
    "alice@example.com, true",
    "invalid-email, false",
    "@missing.com, false",
    "user@domain.com, true"
})
void shouldValidateEmail(String email, boolean expected) {
    assertThat(EmailValidator.isValid(email)).isEqualTo(expected);
}

@ParameterizedTest
@MethodSource("provideUsers")
void shouldCalculateDiscount(User user, double expectedDiscount) {
    assertThat(pricingService.getDiscount(user)).isEqualTo(expectedDiscount);
}

static Stream<Arguments> provideUsers() {
    return Stream.of(
        Arguments.of(new User("free"), 0.0),
        Arguments.of(new User("pro"), 0.10),
        Arguments.of(new User("enterprise"), 0.25)
    );
}
```

## Nested Tests

```java
@Nested
@DisplayName("when user exists")
class WhenUserExists {

    private User existingUser;

    @BeforeEach
    void setUp() {
        existingUser = userService.create("Alice", "alice@example.com");
    }

    @Test
    void shouldFindById() {
        assertThat(userService.findById(existingUser.getId())).isPresent();
    }

    @Test
    void shouldUpdateName() {
        userService.updateName(existingUser.getId(), "Alicia");
        User updated = userService.findById(existingUser.getId()).orElseThrow();
        assertThat(updated.getName()).isEqualTo("Alicia");
    }

    @Nested
    @DisplayName("when deleting")
    class WhenDeleting {
        @Test
        void shouldRemoveUser() {
            userService.delete(existingUser.getId());
            assertThat(userService.findById(existingUser.getId())).isEmpty();
        }
    }
}
```

## Mockito Integration

```java
@ExtendWith(MockitoExtension.class)
class OrderServiceTest {

    @Mock
    private OrderRepository orderRepository;

    @Mock
    private PaymentGateway paymentGateway;

    @InjectMocks
    private OrderService orderService;

    @Test
    void shouldProcessOrder() {
        Order order = new Order(1L, BigDecimal.valueOf(99.99));
        when(paymentGateway.charge(any())).thenReturn(PaymentResult.success("txn-123"));
        when(orderRepository.save(any())).thenReturn(order);

        OrderResult result = orderService.process(order);

        assertThat(result.isSuccess()).isTrue();
        verify(paymentGateway).charge(argThat(payment ->
            payment.getAmount().equals(BigDecimal.valueOf(99.99))));
        verify(orderRepository).save(argThat(o -> o.getStatus() == OrderStatus.PAID));
    }
}
```

## MockMvc Controller Tests

```java
@WebMvcTest(UserController.class)
class UserControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockBean
    private UserService userService;

    @Test
    void shouldReturnUser() throws Exception {
        when(userService.findById(1L)).thenReturn(Optional.of(new User(1L, "Alice")));

        mockMvc.perform(get("/api/users/1"))
            .andExpect(status().isOk())
            .andExpect(jsonPath("$.name").value("Alice"));
    }

    @Test
    void shouldCreateUser() throws Exception {
        when(userService.create(any(), any())).thenReturn(new User(1L, "Alice"));

        mockMvc.perform(post("/api/users")
                .contentType(MediaType.APPLICATION_JSON)
                .content("""
                    {"name": "Alice", "email": "alice@example.com"}
                    """))
            .andExpect(status().isCreated())
            .andExpect(jsonPath("$.id").value(1));
    }

    @Test
    void shouldReturn404WhenNotFound() throws Exception {
        when(userService.findById(999L)).thenReturn(Optional.empty());

        mockMvc.perform(get("/api/users/999"))
            .andExpect(status().isNotFound());
    }
}
```

## Testcontainers

```java
@SpringBootTest
@Testcontainers
class UserRepositoryIT {

    @Container
    static PostgreSQLContainer<?> postgres = new PostgreSQLContainer<>("postgres:16-alpine");

    @DynamicPropertySource
    static void configureProperties(DynamicPropertyRegistry registry) {
        registry.add("spring.datasource.url", postgres::getJdbcUrl);
        registry.add("spring.datasource.username", postgres::getUsername);
        registry.add("spring.datasource.password", postgres::getPassword);
    }

    @Autowired
    private UserRepository userRepository;

    @Test
    void shouldPersistUser() {
        User user = new User("Alice", "alice@example.com");
        User saved = userRepository.save(user);

        assertThat(saved.getId()).isNotNull();
        assertThat(userRepository.findByEmail("alice@example.com")).isPresent();
    }
}
```

## Additional Resources

- JUnit 5: https://junit.org/junit5/docs/current/user-guide/
- AssertJ: https://assertj.github.io/doc/
- Testcontainers: https://testcontainers.com/guides/
